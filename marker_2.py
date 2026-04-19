import pytesseract
import re
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

# --- CONFIGURATION ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def convert_multiple_images_inline(pdf_path, output_path):
    model_dict = create_model_dict()
    converter = PdfConverter(artifact_dict=model_dict)
    result = converter(pdf_path)
    full_text, _, _ = text_from_rendered(result)

    if result.images:
        print(f"Detected {len(result.images)} images. Starting OCR...")
        
        # We loop through every image found in the PDF
        for img_name, img_obj in result.images.items():
            try:
                # 1. Run Tesseract on this specific image
                print(f"Processing: {img_name}")
                ocr_text = pytesseract.image_to_string(img_obj, lang='hin+eng').strip()
                
                # 2. Prepare the replacement text
                # We use a separator to make it look clean in the Markdown
                replacement = f"\n\n--- [OCR START: {img_name}] ---\n{ocr_text}\n--- [OCR END] ---\n\n"
                
                # 3. Use Regex to find the image tag in the text
                # This matches ![] (img_name) even if there is text inside the brackets
                pattern = rf"!\[.*?\]\({re.escape(img_name)}\)"
                
                if re.search(pattern, full_text):
                    full_text = re.sub(pattern, replacement, full_text)
                    print(f"Successfully injected OCR for {img_name} at its original position.")
                else:
                    # If the tag isn't found in the text, append it to the end so no data is lost
                    full_text += f"\n\n### Missing Image Tag Reference: {img_name}\n{replacement}"
                    
            except Exception as e:
                print(f"Failed to process {img_name}: {e}")

    # Save final results
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)

convert_multiple_images_inline(r"D:\Python_AI\NLP\Docling\Hindi_English PDF_3.pdf", "final_output.md")