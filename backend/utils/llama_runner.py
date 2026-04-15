import subprocess
import logging
import re

# ─── Sonnet's Optimized Patterns ───────────────────────────────────────────
_ANSI_RE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
_METRICS_RE = re.compile(
    r'(?:\[\s*Prompt\s*:\s*[\d.]+\s*t/s|llama_print_timings\s*:|llama_perf_(?:context|sampler)_print\s*:)',
    re.IGNORECASE
)
_TRUNCATED_RE = re.compile(r'\.\.\.\s*\(truncated\)\s*\n?', re.IGNORECASE)
_KILL_RE = re.compile(r'\s*>\s*/exit\b[^\n]*(\nExiting\.{0,3})?\s*$', re.IGNORECASE)

def run_edge_inference(system_prompt: str, user_text: str, model_path: str = "gemma-2-2b-it-Q4_K_M.gguf", max_tokens: str = "150") -> str:
    """
    Executes bare-metal C++ inference via llama-cli.
    """
    # 1. We inject a highly specific, unique END-OF-PROMPT anchor.
    # This completely eliminates Sonnet's dangerous "blank line" assumption.
    full_prompt = f"{system_prompt}\n\nSanitized Text:\n{user_text}\n\n[AEGIS_START_GEN]"

    cli_path = "./llama.cpp/build/bin/llama-cli"
    full_model_path = f"./llama.cpp/{model_path}"

    cmd = [
        cli_path,
        "-m", full_model_path,
        "-p", full_prompt,
        "-n", max_tokens,
        "--temp", "0.1",
        "--log-disable"
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True,
            timeout=180,
            input="/exit\n"  
        )

        # Step 1: Sonnet's ANSI Stripper
        text = _ANSI_RE.sub('', result.stdout)

        # Step 2: Sonnet's Tail Boundary (Metrics)
        m_end = _METRICS_RE.search(text)
        end_pos = m_end.start() if m_end else len(text)
        generation_block = text[:end_pos]

        # Step 3: Aegis Head Boundary (Bulletproof)
        # Check for Sonnet's truncation marker first
        m_trunc = _TRUNCATED_RE.search(generation_block)
        if m_trunc:
            clean_output = generation_block[m_trunc.end():]
        elif "[AEGIS_START_GEN]" in generation_block:
            # If not truncated, split exactly at our custom anchor
            clean_output = generation_block.split("[AEGIS_START_GEN]")[-1]
        else:
            clean_output = generation_block

        # Step 4: Sonnet's Kill Command Scrub
        clean_output = _KILL_RE.sub('', clean_output).strip()

        # Step 5: Aegis JSON Fail-Safe (Missing from Sonnet)
        json_match = re.search(r'\[\s*\{.*?\}\s*\]', clean_output, re.DOTALL)
        if json_match and "original" in json_match.group(0):
            return json_match.group(0)

        # Step 6: Return the clean text if it's a summary
        return clean_output if clean_output else "[SYSTEM ERROR]: Generation block empty."

    except Exception as e:
        logging.error(f"Execution failed: {str(e)}")
        return "[SYSTEM ERROR]: Inference failure."