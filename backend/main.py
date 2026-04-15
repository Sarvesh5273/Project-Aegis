from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from backend.agents.synthesizer import synthesize_brief

# Import the 3-Layer Sanitizer and Layer 0 Air-Gap Enforcer
from backend.agents.sanitizer import sanitize_pipeline
from backend.utils.network_guard import assert_air_gapped

# Initialize the FastAPI application
app = FastAPI(
    title="Project Aegis API",
    description="Offline, air-gapped AI document intelligence.",
    version="1.0.0"
)

# Define the precise API Contract request schema
class ProcessRequest(BaseModel):
    raw_text: str
    task: str  # Must be "sanitize", "synthesize", or "both"

# Define the exact API Contract response schema
class ProcessResponse(BaseModel):
    status: str
    redaction_map: Optional[Dict[str, str]] = None
    sanitized_text: Optional[str] = None
    synthesis_result: Optional[str] = None

@app.post("/api/v1/process", response_model=ProcessResponse)
async def process_document(request: ProcessRequest):
    """
    Primary endpoint for processing sensitive field reports.
    Executes the physical network check before routing to local models.
    """
    
    # ---------------------------------------------------------
    # LAYER 0: DEAD-MAN'S SWITCH
    # ---------------------------------------------------------
    # If this fails, the application hard-crashes immediately.
    try:
        assert_air_gapped()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Initialize response payload
    response_data = {
        "status": "success",
        "redaction_map": {},
        "sanitized_text": "",
        "synthesis_result": ""
    }

    # ---------------------------------------------------------
    # TASK ROUTING
    # ---------------------------------------------------------
    if request.task in ["sanitize", "both"]:
        # Execute the 3-Layer pipeline
        sanitizer_result = sanitize_pipeline(request.raw_text)
        
        response_data["redaction_map"] = sanitizer_result["redaction_map"]
        response_data["sanitized_text"] = sanitizer_result["sanitized_text"]

    if request.task in ["synthesize", "both"]:
        # The Synthesizer strictly operates on the safe text
        text_to_synthesize = response_data["sanitized_text"] if request.task == "both" else request.raw_text
        
        # Call the new Gemma 4 synthesis agent
        response_data["synthesis_result"] = synthesize_brief(text_to_synthesize)

    return response_data

@app.get("/health")
async def health_check():
    """Simple health check for deployment readiness."""
    return {"status": "offline_and_secure"}