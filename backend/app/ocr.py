import fitz  # PyMuPDF
from google.cloud import vision
import io
import os

class OCRService:
    def __init__(self):
        # Initialize Google Cloud Vision client
        # Relies on GOOGLE_APPLICATION_CREDENTIALS env var or default auth
        self.vision_client = vision.ImageAnnotatorClient()

    def extract_text(self, file_path: str, mime_type: str) -> str:
        """
        Hybrid OCR extraction:
        1. If PDF, try valid text extraction with PyMuPDF.
           If text length > 50 chars, return it (Cost Savings).
        2. If PDF (scanned) or Image, use Google Cloud Vision API.
        """
        extracted_text = ""

        try:
            if mime_type == "application/pdf":
                extracted_text = self._extract_text_from_pdf_local(file_path)
                
                # Threshold check: If we have enough text, avoid Cloud Vision
                if len(extracted_text.strip()) > 50:
                    print("OCR: Successfully extracted text locally with PyMuPDF.")
                    return extracted_text
                else:
                    print("OCR: PDF text content too low/empty. Falling back to Cloud Vision (Scanned PDF).")

            # Fallback or Image: Use Cloud Vision
            print(f"OCR: Using Google Cloud Vision for {mime_type}")
            return self._extract_text_cloud_vision(file_path, mime_type)

        except Exception as e:
            print(f"OCR Error: {e}")
            # Return partial text or empty string on failure, don't crash upload
            return extracted_text

    def _extract_text_from_pdf_local(self, file_path: str) -> str:
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"PyMuPDF Error: {e}")
        return text

    def _extract_text_cloud_vision(self, file_path: str, mime_type: str) -> str:
        try:
            with open(file_path, "rb") as image_file:
                content = image_file.read()

            if mime_type == "application/pdf":
                # Vision API for PDF/TIFF is async 'async_batch_annotate_files' usually,
                # but for simplicity/speed on single page docs we might treat as image if converted?
                # Actually, Vision API standard client supports images directly.
                # For PDFs, it's more complex (requires GCS or async op).
                # OPTIMIZATION: Convert first few pages of PDF to image locally with PyMuPDF and send to Vision?
                # This avoids GCS requirement. Let's do that for the "scanned pdf" fallback.
                return self._ocr_pdf_as_images(file_path)
            else:
                # Standard Image (JPG, PNG)
                image = vision.Image(content=content)
                response = self.vision_client.text_detection(image=image)
                texts = response.text_annotations
                
                if texts:
                    return texts[0].description
                return ""

        except Exception as e:
            print(f"Cloud Vision Error: {e}")
            return ""

    def _ocr_pdf_as_images(self, file_path: str) -> str:
        """
        Renders PDF pages to images and sends them to Cloud Vision.
        Avoids the complexity of Cloud Vision PDF GCS-async flow for simple uploads.
        Limits to first 5 pages to save costs/time.
        """
        full_text = ""
        try:
            with fitz.open(file_path) as doc:
                # Limit to first 5 pages for OCR to keep speed high and costs low
                for page_num in range(min(5, len(doc))):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    
                    image = vision.Image(content=img_data)
                    response = self.vision_client.text_detection(image=image)
                    texts = response.text_annotations
                    
                    if texts:
                        full_text += texts[0].description + "\n"
        except Exception as e:
            print(f"PDF-to-Image OCR Error: {e}")
        
        return full_text
