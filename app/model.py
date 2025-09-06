import os
from typing import List
from huggingface_hub import InferenceClient
from huggingface_hub.utils._errors import HfHubHTTPError

# Open, ungated defaults. You can add more if you like.
OPEN_MODELS: List[str] = [
    "HuggingFaceH4/zephyr-7b-beta",         # fast, ungated
    "Qwen/Qwen2.5-7B-Instruct",             # ungated
    "microsoft/Phi-3-mini-4k-instruct",     # small, ungated
]

class LLMBackend:
    def __init__(self, backend: str = "hf_inference", model_name: str | None = None, api_token: str | None = None):
        # Always use HF Inference in this Streamlit build (keeps deploy light)
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            raise RuntimeError("HUGGINGFACE_API_TOKEN not set. Add it in Streamlit Secrets.")

        # Build a prioritized model list: [user choice] + OPEN_MODELS (deduped)
        pref = [model_name] if model_name else []
        combined = pref + [m for m in OPEN_MODELS if m not in pref]
        self.models = combined
        # lazily create clients per model
        self._clients = {}

    def _client(self, model: str) -> InferenceClient:
        if model not in self._clients:
            self._clients[model] = InferenceClient(model=model, token=self.api_token)
        return self._clients[model]

    def chat(self, system: str, user: str) -> str:
        last_err = None
        for model in self.models:
            try:
                # Prefer chat endpoint
                cli = self._client(model)
                try:
                    out = cli.chat_completion(
                        messages=[{"role":"system","content":system},
                                  {"role":"user","content":user}],
                        max_tokens=800, temperature=0.4
                    )
                    return out.choices[0].message["content"]
                except Exception:
                    # Fallback to text-generation
                    prompt = f"[System]\n{system}\n\n[User]\n{user}\n\n[Assistant]\n"
                    txt = cli.text_generation(prompt, max_new_tokens=800, temperature=0.4)
                    return txt.strip()
            except HfHubHTTPError as e:
                # Permission/rate-limit/gated → try the next open model
                last_err = e
                continue
            except Exception as e:
                last_err = e
                continue

        # If every model failed, raise a friendly error
        msg = (
            "All inference backends failed (model may be gated or rate-limited). "
            "Try a different model in the sidebar (e.g., HuggingFaceH4/zephyr-7b-beta)."
        )
        if last_err:
            msg += f"\nLast error: {type(last_err).__name__}: {last_err}"
        raise RuntimeError(msg)
