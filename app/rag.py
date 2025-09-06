# app/rag.py
from pathlib import Path
from typing import List, Tuple
import re
from rank_bm25 import BM25Okapi

class SimpleRAG:
    """
    Lightweight RAG using BM25 (lexical). No FAISS, no Torch, no HF embeddings.
    Good enough to retrieve your Edge System snippets reliably on Streamlit Cloud.
    """
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.chunks: List[dict] = []
        self._bm25 = None
        self._tokenized_corpus: List[List[str]] = []

    def _chunk(self, text: str, max_chars: int = 1200):
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

    def _tokenize(self, s: str) -> List[str]:
        # simple, fast tokenization
        return re.findall(r"[A-Za-z0-9']+", s.lower())

    def build(self):
        # load and chunk all .txt files
        for p in self.data_dir.glob("*.txt"):
            txt = p.read_text(encoding="utf-8", errors="ignore")
            for c in self._chunk(txt):
                self.chunks.append({"source": p.name, "text": c})
        if not self.chunks:
            self.chunks.append({"source": "EMPTY", "text": "No documents ingested yet."})

        # build BM25 index
        self._tokenized_corpus = [self._tokenize(c["text"]) for c in self.chunks]
        self._bm25 = BM25Okapi(self._tokenized_corpus)

    def search(self, query: str, k: int = 5) -> List[Tuple[float, dict]]:
        if not self._bm25:
            raise RuntimeError("RAG not built. Call build() first.")
        tokens = self._tokenize(query)
        scores = self._bm25.get_scores(tokens)
        # get top-k indices
        topk_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(float(scores[i]), self.chunks[i]) for i in topk_idx]
