# app/model.py
import os
from typing import List, Optional
from huggingface_hub import InferenceClient
from huggingface_hub.utils._errors import HfHubHTTPError

# FIXED: Reordered models with most reliable first, removed broken TinyLlama
OPEN_MODELS: List[str] = [
    "distilgpt2",  # Most reliable - rarely has 404 errors
    "gpt2-medium", # Backup reliable option
    "Qwen/Qwen2.5-7B-Instruct", 
    "HuggingFaceH4/zephyr-7b-beta",
    "microsoft/Phi-3-mini-4k-instruct",
]

class LLMBackend:
    def __init__(self, backend: str = "hf_inference", model_name: Optional[str] = None, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            raise RuntimeError("HUGGINGFACE_API_TOKEN not set in secrets.")
        pref = [model_name] if model_name else []
        self.models = pref + [m for m in OPEN_MODELS if m not in pref]
        self._clients = {}

    def _client(self, model: str) -> InferenceClient:
        if model not in self._clients:
            self._clients[model] = InferenceClient(model=model, token=self.api_token)
        return self._clients[model]

    def chat(self, system: str, user: str, max_new_tokens: int = 512, temperature: float = 0.4) -> str:
        last_err = None
        for model in self.models:
            try:
                cli = self._client(model)
                # 1) try chat endpoint (fast for chat-tuned models)
                try:
                    out = cli.chat_completion(
                        messages=[{"role":"system","content":system},{"role":"user","content":user}],
                        max_tokens=max_new_tokens,
                        temperature=temperature,
                        top_p=0.9
                    )
                    return out.choices[0].message["content"]
                except Exception:
                    # 2) fallback to text-generation with tight decoding
                    prompt = f"[System]\n{system}\n\n[User]\n{user}\n\n[Assistant]\n"
                    txt = cli.text_generation(
                        prompt,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        top_p=0.9,
                        repetition_penalty=1.1,
                        return_full_text=False,
                    )
                    return txt.strip()
            except HfHubHTTPError as e:
                last_err = e
                continue
            except Exception as e:
                last_err = e
                continue

        msg = (
            "All inference backends failed (model may be gated or rate-limited). "
            "Try switching to DistilGPT2 (very fast) or GPT2 Medium in the model dropdown."
        )
        if last_err:
            msg += f"\nLast error: {type(last_err).__name__}: {last_err}"
        raise RuntimeError(msg)
