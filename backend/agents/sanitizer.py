import re
import spacy
import json
import logging
from backend.utils.llama_runner import run_edge_inference

# ---------------------------------------------------------
# LAYER 1 INIT: Multilingual Deterministic Baseline
# ---------------------------------------------------------
try:
    nlp = spacy.load("xx_ent_wiki_sm")
except OSError:
    import subprocess
    print("Downloading multilingual spaCy model...")
    subprocess.run(["python", "-m", "spacy", "download", "xx_ent_wiki_sm"])
    nlp = spacy.load("xx_ent_wiki_sm")

# ---------------------------------------------------------
# LAYER 2 INIT: Generative JSON Extraction (Edge)
# ---------------------------------------------------------
# We use a rigid prompt to force JSON output from the C++ engine.
# (Note: In a true production edge environment, we would pass a .gbnf 
# grammar file to llama-cli to mathematically guarantee JSON structure).
EDGE_SANITIZER_PROMPT = """You are a data extraction tool.
Extract all Person Names, Organization Names, and Locations from the text.
Output ONLY valid JSON in this exact format:
[
  {"original": "John Doe", "token": "[PER_1]"},
  {"original": "London", "token": "[LOC_1]"}
]
Do not include markdown formatting. Do not include any other text."""

def safe_replace(text: str, original: str, token: str) -> str:
    """Safely replaces whole words, ignoring 1-character false positives."""
    if len(original) <= 1:
        return text
    
    # Escape regex specials in the original string (e.g., if it contains periods)
    escaped_orig = re.escape(original)
    
    # Use word boundaries to prevent partial word replacement (e.g., replacing 'E' inside 'REDACTED')
    # We use a case-insensitive replacement.
    pattern = re.compile(rf'\b{escaped_orig}\b', re.IGNORECASE)
    return pattern.sub(token, text)

def sanitize_pipeline(raw_text: str) -> dict:
    """
    Executes the 3-Layer Aegis Redaction Pipeline via C++ Edge Engine.
    """
    text = raw_text
    redaction_map = {}
    
    # LAYER 3: Regex Fallback (Run FIRST to catch standard PII before NLP messes it up)
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL_REDACTED]', text)
    text = re.sub(r'\b\d{10}\b', '[PHONE_REDACTED]', text)
    text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_REDACTED]', text)
    # Improved coordinates regex
    text = re.sub(r'\d{1,3}(\.\d+)?°?[NS],\s*\d{1,3}(\.\d+)?°?[EW]', '[COORDS_REDACTED]', text)

    # LAYER 1: spaCy NER (Deterministic)
    doc = nlp(text)
    for ent in doc.ents:
        # Ignore 1-character entities to prevent catastrophic document corruption
        if len(ent.text) > 1 and "REDACTED" not in ent.text:
            token = f"[{ent.label_}_REDACTED]"
            redaction_map[ent.text] = token
            text = safe_replace(text, ent.text, token)

    # LAYER 2: Gemma 4 C++ Subprocess Extraction
    raw_json_output = run_edge_inference(
        system_prompt=EDGE_SANITIZER_PROMPT,
        user_text=text,
        max_tokens="400" # Give the JSON room to finish printing
    )

    # Attempt to parse the C++ engine's JSON output
    try:
        # Strip markdown code blocks if the model ignored instructions
        clean_json = raw_json_output.replace('```json', '').replace('```', '').strip()
        
        # Find the start and end of the JSON array
        start_idx = clean_json.find('[')
        end_idx = clean_json.rfind(']') + 1
        
        if start_idx != -1 and end_idx != 0:
            entities = json.loads(clean_json[start_idx:end_idx])
            for entity in entities:
                orig = entity.get("original")
                tok = entity.get("token")
                if orig and tok and len(orig) > 1 and "REDACTED" not in orig:
                    redaction_map[orig] = tok
                    text = safe_replace(text, orig, tok)
    except json.JSONDecodeError as e:
        logging.warning(f"Edge Sanitizer JSON parse failed: {e}. Falling back to Layers 1 and 3.")
        # If the edge model fails to output valid JSON, we rely on the Regex and spaCy layers.

    return {
        "status": "success",
        "redaction_map": redaction_map,
        "sanitized_text": text
    }