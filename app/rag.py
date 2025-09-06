import os
from pathlib import Path
from typing import List, Tuple
import numpy as np
from huggingface_hub import InferenceClient

# Uses HF Inference "feature-extraction" (works on Streamlit Cloud, no torch/faiss)
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

class SimpleRAG:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not token:
            raise RuntimeError("HUGGINGFACE_API_TOKEN not set. Add it in Streamlit Secrets.")
        # We set the model here so we can call feature_extraction without passing it every time
        self.client = InferenceClient(model=EMBED_MODEL, token=token)
        self.chunks: List[dict] = []
        self.embs: np.ndarray | None = None

    def _chunk(self, text: str, max_chars: int = 1200):
        import re
        sents = re.split(r'(?<=[.!?])\s+', text.strip())
        cur, out = "", []
        for s in sents:
            if len(cur) + len(s) < max_chars:
                cur += (" " + s)
            else:
                if cur.strip(): out.append(cur.strip())
                cur = s
        if cur.strip(): out.append(cur.strip())
        return out

    def _embed(self, texts: List[str]) -> np.ndarray:
        """
        Uses HF Inference feature-extraction. For sentence-transformer models,
        it returns one vector per input. For token-level models, we average tokens.
        """
        # HF returns either:
        # - List[List[float]]  -> one embedding per input (sentence-transformers)
        # - List[List[List[float]]] -> token embeddings (we average across tokens)
        out = self.client.feature_extraction(texts)
        # Ensure list-of-embeddings shape
        if isinstance(out, list) and len(out) and isinstance(out[0], list):
            # token-level case: first element is a list of token vectors
            if len(out) and isinstance(out[0][0], list):
                vecs = np.array([np.mean(np.asarray(x, dtype="float32"), axis=0) for x in out], dtype="float32")
            else:
                vecs = np.asarray(out, dtype="float32")
        else:
            vecs = np.asarray(out, dtype="float32")
        # normalize rows for cosine similarity
        norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
        return vecs / norms

    def build(self):
        for p in self.data_dir.glob("*.txt"):
            txt = p.read_text(encoding="utf-8", errors="ignore")
            for c in self._chunk(txt):
                self.chunks.append({"source": p.name, "text": c})
        if not self.chunks:
            self.chunks.append({"source": "EMPTY", "text": "No documents ingested yet."})
        self.embs = self._embed([c["text"] for c in self.chunks])

    def search(self, query: str, k: int = 5) -> List[Tuple[float, dict]]:
        q = self._embed([query])[0]  # (d,)
        sims = (self.embs @ q)       # cosine similarity (embeddings are normalized)
        topk = np.argsort(sims)[::-1][:k]
        return [(float(sims[i]), self.chunks[i]) for i in topk]
