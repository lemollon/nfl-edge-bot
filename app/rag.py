import os, faiss, numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMB_DIM = 384

class SimpleRAG:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = faiss.IndexFlatIP(EMB_DIM)
        self.chunks, self.embs = [], None

    def _chunk(self, text: str, max_chars: int = 1200):
        import re
        sents = re.split(r'(?<=[.!?])\s+', text.strip())
        cur, out = "", []
        for s in sents:
            if len(cur) + len(s) < max_chars:
                cur += (" " + s)
            else:
                if cur.strip():
                    out.append(cur.strip())
                cur = s
        if cur.strip():
            out.append(cur.strip())
        return out

    def build(self):
        for p in self.data_dir.glob("*.txt"):
            txt = p.read_text(encoding="utf-8", errors="ignore")
            for c in self._chunk(txt):
                self.chunks.append({"source": p.name, "text": c})
        if not self.chunks:
            self.chunks.append({"source":"EMPTY","text":"No documents ingested yet."})
        X = self.model.encode([c["text"] for c in self.chunks], normalize_embeddings=True)
        self.embs = np.array(X, dtype="float32")
        self.index.add(self.embs)

    def search(self, query: str, k: int = 5):
        q = self.model.encode([query], normalize_embeddings=True).astype("float32")
        D, I = self.index.search(q, k)
        return [(float(D[0][i]), self.chunks[I[0][i]]) for i in range(len(I[0])) if I[0][i] != -1]
