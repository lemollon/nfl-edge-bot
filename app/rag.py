import os
from pathlib import Path
from typing import List, Tuple
import numpy as np
from huggingface_hub import InferenceClient

# Set HUGGINGFACE_API_TOKEN in Streamlit Secrets (TOML):
# HUGGINGFACE_API_TOKEN = "hf_...."
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

class SimpleRAG:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not token:
            raise RuntimeError("HUGGINGFACE_API_TOKEN not set. Add it in Streamlit Secrets.")
        self.client = InferenceClient(token=token)
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
        res = self.client.embeddings(model=EMBED_MODEL, inputs=texts)
        vecs = np.array(res["embeddings"], dtype="float32")
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
        sims = (self.embs @ q)       # cosine because normalized
        topk = np.argsort(sims)[::-1][:k]
        return [(float(sims[i]), self.chunks[i]) for i in topk]
