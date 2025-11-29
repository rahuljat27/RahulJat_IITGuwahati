import os
import tempfile
import requests
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from extract_text import extract_raw_text
from extract_info import extract_ocr_to_json

app = FastAPI(title="Medical Bill Extraction API")

class ExtractRequest(BaseModel):
    document: str  # URL of the PDF or Image

class TokenUsage(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int
    
class ExtractResponse(BaseModel):
    is_success: bool
    token_usage: TokenUsage
    data: dict


def download_document(url: str) -> str:
    """Downloads the document to a temporary location and returns file path."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download document: {e}")

    # Create temp file
    suffix = ".pdf" if url.lower().endswith(".pdf") else ".png"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(resp.content)
    temp_file.close()

    return temp_file.name

@app.post("/extract-bill-data", response_model=ExtractResponse)
async def extract_bill_data(req: ExtractRequest):
    try:
        # Step 1: Download file
        file_path = download_document(req.document)


        raw_text = extract_raw_text(
                file_path
            )
            
        # else:
        #     raise HTTPException(status_code=400, detail="Only PDF documents are supported currently.")

        # Step 3: LLM → Structured JSON
        extraction_result, token_usage  = extract_ocr_to_json(raw_text)
        
        token_usage_data = TokenUsage(
            total_tokens=token_usage.get("total_tokens", 0),
            input_tokens=token_usage.get("input_tokens", 0),
            output_tokens=token_usage.get("output_tokens", 0)
        )


        # Step 4: Response
        return {
            "is_success": True,
            "token_usage": token_usage_data,
            "data": extraction_result.get("data", {})
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
