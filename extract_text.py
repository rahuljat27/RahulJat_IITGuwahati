import easyocr
import numpy as np # Import numpy for faster in-memory processing
from pdf2image import convert_from_path
from pathlib import Path

def extract_raw_text(
    file_path: str,
    dpi: int = 300, # 300 is usually sufficient and faster than 350
    poppler_path: str = r"C:\Users\HP\Downloads\Release-25.11.0-0\poppler-25.11.0\Library\bin"
) -> str:
    """
    Extracts raw OCR text from Scanned PDF or Images.
    """

    # Initialize OCR Reader (Move this outside the function if calling multiple times to load model only once)
    reader = easyocr.Reader(['en']) 

    path_obj = Path(file_path) # Use a specific variable for the Path object
    ext = path_obj.suffix.lower()

    all_text = ""

    # -------------------------------
    # CASE 1: FILE IS A PDF
    # -------------------------------
    if ext == ".pdf":
        try:
            images = convert_from_path(
                str(path_obj), # Convert Path to string here
                dpi=dpi,
                poppler_path=poppler_path
            )

            for i, img in enumerate(images):
                # OPTIMIZATION: Convert PIL image directly to numpy array
                # This avoids saving "page_i.jpg" to disk (much faster)
                img_np = np.array(img)

                result = reader.readtext(img_np, detail=0)
                page_text = "\n".join(result)

                all_text += f"\n\n--- Page {i+1} ---\n" + page_text
        except Exception as e:
            raise RuntimeError(f"Error processing PDF: {e}")

    # -------------------------------
    # CASE 2: FILE IS AN IMAGE
    # -------------------------------
    elif ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]:
        
        # FIX: Convert path_obj back to string for EasyOCR
        result = reader.readtext(str(path_obj), detail=0) 
        page_text = "\n".join(result)

        all_text = f"--- Image OCR ---\n{page_text}"

    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return all_text