from extract_text import extract_raw_text
from extract_info import extract_ocr_to_json

def main():
    # Path to the scanned PDF bill
    pdf_file_path = "train_sample_9.pdf"  # Replace with your PDF file path

    # Step 1: Extract raw OCR text from PDF
    raw_ocr_text = extract_raw_text(pdf_file_path)
    # with open("raw_ocr_output.txt", "w", encoding="utf-8") as f:
    #     f.write(raw_ocr_text)

    # Step 2: Extract structured JSON from raw OCR text
    structured_data , token_usage  = extract_ocr_to_json(raw_ocr_text)

    # Print the structured JSON data
    print(structured_data)
    print("Token Usage:", token_usage)


if __name__ == "__main__":
    main()
