import spacy
import json
import logging
import os
import re
import ollama
from backend.utils.llama_runner import run_edge_inference
from backend.utils.nlp_helpers import apply_regex_fallbacks

try:
    nlp = spacy.load("xx_ent_wiki_sm")
except OSError as e:
    raise RuntimeError("Missing offline dependency: xx_ent_wiki_sm. Run setup.sh first.") from e

EDGE_SANITIZER_PROMPT = """You are a data extraction tool.
Extract all Person Names, Organization Names, and Locations from the text.
Output ONLY valid JSON in this exact format:
[{"original": "John Doe", "token": "[PER_1]"}]"""

def safe_replace(text: str, original: str, token: str) -> str:
    if len(original) <= 1: return text
    pattern = re.compile(rf'\b{re.escape(original)}\b', re.IGNORECASE)
    return pattern.sub(token, text)

def sanitize_pipeline(raw_text: str) -> dict:
    redaction_map = {}

    # LAYER 3: Regex fallbacks — runs first, returns map for highlighting
    text, regex_map = apply_regex_fallbacks(raw_text)
    redaction_map.update(regex_map)

    # LAYER 1: spaCy NER
    doc = nlp(text)
    for ent in doc.ents:
        if len(ent.text) > 1 and "REDACTED" not in ent.text:
            token = f"[{ent.label_}_REDACTED]"
            redaction_map[ent.text] = token
            text = safe_replace(text, ent.text, token)

    # LAYER 2: Dual-Path Inference
    device = os.environ.get("AEGIS_DEVICE", "mac").lower()

    if device == "mac":
        extraction_tool = {
            'type': 'function',
            'function': {
                'name': 'extract_sensitive_entities',
                'description': 'Extract Person, Organization, and Location names for redaction.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'entities': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'original': {'type': 'string'},
                                    'token': {'type': 'string'}
                                }
                            }
                        }
                    },
                    'required': ['entities']
                }
            }
        }

        try:
            response = ollama.chat(
                model=os.environ.get("AEGIS_MODEL", "gemma4:26b"),
                messages=[{"role": "user", "content": f"Extract entities from this text: {text}"}],
                tools=[extraction_tool]
            )

            if response.get('message', {}).get('tool_calls'):
                tool_call = response['message']['tool_calls'][0]
                entities = tool_call['function']['arguments'].get('entities', [])

                for entity in entities:
                    orig, tok = entity.get("original"), entity.get("token")
                    if orig and tok and len(orig) > 1 and "REDACTED" not in orig:
                        redaction_map[orig] = tok
                        text = safe_replace(text, orig, tok)

                return {"status": "success", "redaction_map": redaction_map, "sanitized_text": text}
            else:
                raise ValueError("Model failed to invoke the extraction tool.")

        except Exception as e:
            logging.warning(f"Native function call failed: {e}. Falling back to C++ engine.")
            raw_json_output = run_edge_inference(EDGE_SANITIZER_PROMPT, text, max_tokens="400")
    else:
        # Raspberry Pi path
        raw_json_output = run_edge_inference(EDGE_SANITIZER_PROMPT, text, max_tokens="400")

    # C++ Fallback JSON Parsing
    clean_json = raw_json_output.strip()
    if clean_json.startswith('[') and clean_json.endswith(']'):
        try:
            entities = json.loads(clean_json)
            for entity in entities:
                orig, tok = entity.get("original"), entity.get("token")
                if orig and tok and len(orig) > 1 and "REDACTED" not in orig:
                    redaction_map[orig] = tok
                    text = safe_replace(text, orig, tok)
        except json.JSONDecodeError as e:
            logging.warning(f"Edge JSON parse failed: {e}")

    return {"status": "success", "redaction_map": redaction_map, "sanitized_text": text}