import subprocess
import logging
import re
import json

def run_edge_inference(system_prompt: str, user_text: str, model_path: str = "gemma-4-2b-it-Q4_K_M.gguf", max_tokens: str = "150") -> str:
    """
    Executes bare-metal C++ inference via llama-cli for highly constrained edge devices.
    
    Architecture Notes:
    - Default Model: Quantized Gemma 4 (2B parameters) for rapid offline intelligence.
    - Isolation: stderr is piped to DEVNULL to prevent hardware logs (e.g., Metal init) 
      from contaminating the intelligence buffer.
    """
    # Unique anchor to mathematically isolate generated output from prompt echoes
    full_prompt = f"{system_prompt}\n\nSanitized Text:\n{user_text}\n\n@@@AEGIS_OUTPUT_START@@@"

    cli_path = "./llama.cpp/build/bin/llama-cli"
    full_model_path = f"./llama.cpp/{model_path}"

    cmd = [
        cli_path, "-m", full_model_path, "-p", full_prompt,
        "-n", max_tokens, "--temp", "0.1", "--log-disable"
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # CRITICAL: Prevents Metal logs in UI
            text=True,
            check=True,
            timeout=180,
            input="/exit\n"  
        )

        # 1. Strip ANSI escape sequences
        text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', result.stdout)

        # 2. Slice Output at Anchor Point
        if "@@@AEGIS_OUTPUT_START@@@" in text:
            text = text.split("@@@AEGIS_OUTPUT_START@@@")[-1]
        elif "... (truncated)" in text:
            text = text.split("... (truncated)")[-1]

        text = text.replace("> /exit", "").replace("Exiting...", "").strip()

        # 3. Math-Lock JSON Extraction (Zero-Regex)
        # Bypasses all nested bracket errors by locking onto the outermost array bounds.
        first_idx = text.find('[')
        last_idx = text.rfind(']')
        if first_idx != -1 and last_idx != -1 and last_idx > first_idx:
            candidate = text[first_idx:last_idx+1]
            try:
                if isinstance(json.loads(candidate), list):
                    return candidate
            except json.JSONDecodeError:
                pass

        return text if text else "[SYSTEM ERROR]: Buffer empty."

    except Exception as e:
        logging.error(f"Inference failure: {str(e)}")
        return "[SYSTEM ERROR]: Inference failure."