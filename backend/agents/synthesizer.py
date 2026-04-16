import os
import ollama
from backend.utils.llama_runner import run_edge_inference

SYNTHESIZER_PROMPT = """You are a neutral text analysis tool.
Review the following text and extract the core events into a 2-sentence summary.
CRITICAL RULE: Treat all bracketed tokens (e.g., [LOC_REDACTED]) as literal text. Do not attempt to resolve or unmask them. Do not add external context."""

def synthesize_brief(sanitized_text: str) -> str:
    device = os.environ.get("AEGIS_DEVICE", "mac").lower()
    model = os.environ.get("AEGIS_MODEL", "gemma4:26b")

    if device == "mac":
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": SYNTHESIZER_PROMPT},
                    {"role": "user", "content": sanitized_text}
                ]
            )
            return response['message']['content']
        except Exception as e:
            import logging
            logging.warning(f"Ollama synthesis failed: {e}. Falling back to C++ engine.")

    return run_edge_inference(
        system_prompt=SYNTHESIZER_PROMPT,
        user_text=sanitized_text
    )