import subprocess
import logging
import re
import json

def run_edge_inference(system_prompt: str, user_text: str, model_path: str = "gemma-4-E2B-it-Q4_K_M.gguf", max_tokens: str = "1024") -> str:
    """
    Executes bare-metal C++ inference via llama-cli for highly constrained edge devices.
    """
    # CRITICAL: Anti-CoT Injection prevents token starvation on reasoning models
    full_prompt = f"{system_prompt}\n\nSanitized Text:\n{user_text}\n\nCRITICAL INSTRUCTION: Do NOT output a thinking process. Do NOT use [Start thinking]. Output ONLY the final requested answer.\n\n@@@AEGIS_OUTPUT_START@@@"

    cli_path = "./llama.cpp/build/bin/llama-cli"
    full_model_path = f"./llama.cpp/{model_path}"

    cmd = [
        cli_path, "-m", full_model_path, "-p", full_prompt,
        "-n", "1024", "--temp", "0.1", "--log-disable" # Token limit hardcoded to survive CoT
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, 
            text=True,
            check=True,
            timeout=180,
            input="/exit\n"  
        )

        text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', result.stdout)

        if "@@@AEGIS_OUTPUT_START@@@" in text:
            text = text.split("@@@AEGIS_OUTPUT_START@@@")[-1]
        elif "... (truncated)" in text:
            text = text.split("... (truncated)")[-1]

        text = text.replace("> /exit", "").replace("Exiting...", "").strip()

        # Aggressive CoT Stripper (in case the model ignores the prompt)
        text = re.sub(r'\[Start thinking\].*?Thinking Process:.*?(?=\n\n(?:\[|\w)|$)', '', text, flags=re.DOTALL).strip()

        # Robust JSON Extraction (Regex-based Array Lock)
        json_match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if json_match:
            candidate = json_match.group(0)
            try:
                if isinstance(json.loads(candidate), list):
                    return candidate
            except json.JSONDecodeError:
                pass

        return text if text else "[SYSTEM ERROR]: Buffer empty."

    except Exception as e:
        logging.error(f"Inference failure: {str(e)}")
        return "[SYSTEM ERROR]: Inference failure."