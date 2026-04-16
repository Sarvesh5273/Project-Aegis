from backend.utils.llama_runner import run_edge_inference
import os
import ollama

# Responsible AI Alignment: Removed jailbreak language to comply with Google safety standards.
EDGE_SYNTHESIZER_PROMPT = """You are a neutral text analysis tool.
Review the following text and extract the core events into a 2-sentence summary.
CRITICAL RULE: Treat all bracketed tokens (e.g., [LOC_REDACTED]) as literal text. Do not attempt to resolve or unmask them. Do not add external context."""

def synthesize_brief(sanitized_text: str) -> str:
    """
    Generates a tactical summary.
    Routes to Ollama for high-fidelity reasoning if available, else falls back to edge C++.
    """
    device = os.environ.get("AEGIS_DEVICE", "mac").lower()
    
    if device == "mac":
        try:
            res = ollama.chat(model="gemma4:26b", messages=[
                {"role": "system", "content": EDGE_SYNTHESIZER_PROMPT},
                {"role": "user", "content": sanitized_text}
            ])
            return res['message']['content'].strip()
        except Exception:
            pass # Fallthrough to edge engine
            
    return run_edge_inference(system_prompt=EDGE_SYNTHESIZER_PROMPT, user_text=sanitized_text)