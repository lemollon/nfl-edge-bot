import os
from huggingface_hub import InferenceClient

class LLMBackend:
    def __init__(self, backend: str = "hf_inference", model_name: str | None = None, api_token: str | None = None):
        # We map any backend to HF Inference to avoid heavy installs on Streamlit Cloud
        self.model_name = model_name or "meta-llama/Meta-Llama-3-8B-Instruct"
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            raise RuntimeError("HUGGINGFACE_API_TOKEN not set. Add it in Streamlit Secrets.")
        self.client = InferenceClient(model=self.model_name, token=self.api_token)

    def chat(self, system: str, user: str) -> str:
        # Try chat endpoint first; fallback to text-generation if not supported
        try:
            out = self.client.chat_completion(
                messages=[{"role":"system","content":system},{"role":"user","content":user}],
                max_tokens=800, temperature=0.3
            )
            return out.choices[0].message["content"]
        except Exception:
            prompt = f"[System]\n{system}\n\n[User]\n{user}\n\n[Assistant]\n"
            txt = self.client.text_generation(prompt, max_new_tokens=800, temperature=0.3)
            return txt.strip()
