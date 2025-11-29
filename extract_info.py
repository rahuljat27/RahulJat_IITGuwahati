import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from data_schema import FinalResponse   # Your pydantic schema

load_dotenv()

def extract_ocr_to_json(raw_ocr_text: str) -> tuple[dict, dict]:
    """
    Takes raw OCR text from a hospital bill and returns
    a tuple containing:
    1. Structured JSON (dict) response following FinalResponse schema.
    2. Token usage metadata (dict).
    """

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")

    # Initialize LLM
    # Note: Ensure the model name is correct (e.g., gemini-1.5-flash)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        api_key=GEMINI_API_KEY,
        temperature=0
    )

    # Setup parser
    parser = PydanticOutputParser(pydantic_object=FinalResponse)

    # Prompt
    prompt_template = PromptTemplate(
        template="""
        You are an expert data extraction AI specialized in medical billing OCR.

        Your task is to extract structured data from the provided raw OCR text.

        **CRITICAL INSTRUCTIONS:**
        1. OCR Correction Rules:
           - 'L.00' or 'l.00' -> '1.00'
           - 'S0u.00' -> '1500.00'
           - 'Ii80.00' -> '1180.00'
           - Fix misspellings in medical item names.
        2. Page Separation:
           Use markers like "--- Page 1 ---" to group items by pages.
        3. Math Check:
           Ensure Quantity * Rate ≈ Amount.
        4. Follow JSON schema exactly.

        {format_instructions}

        **RAW OCR TEXT:**
        {raw_text}
        """,
        input_variables=["raw_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    try:
        # --- 1. PREPARE INPUT ---
        # Use invoke() to create a proper PromptValue object (handles messages correctly)
        chain_input = prompt_template.invoke({"raw_text": raw_ocr_text})

        # --- 2. CALL LLM ---
        llm_response = llm.invoke(chain_input)

        # --- 3. EXTRACT METADATA ---
        # LangChain standardizes usage in 'usage_metadata'
        # Google specific data might also be in 'response_metadata'
        token_usage = llm_response.usage_metadata
        
        if not token_usage:
            # Fallback if usage_metadata is None (older versions)
            token_usage = llm_response.response_metadata.get("token_usage", {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
            })

        # --- 4. PARSE OUTPUT ---
        final_pydantic_object = parser.parse(llm_response.content)

        # --- RETURN ---
        return final_pydantic_object.model_dump(), token_usage

    except Exception as e:
        raise RuntimeError(f"Error while extracting OCR text: {e}")