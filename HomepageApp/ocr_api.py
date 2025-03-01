from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np
from fuzzywuzzy import fuzz


# Tesseract ka correct path set karein
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def preprocess_image(image_file):
    """Enhance image quality for better OCR extraction."""
    try:
        # Open the image
        image = Image.open(image_file)

        # Convert to grayscale
        image = image.convert("L")

        # Apply contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(3)

        # Convert to OpenCV format
        img_cv = np.array(image)

        # Apply Gaussian Blur (Reduces Noise)
        img_cv = cv2.GaussianBlur(img_cv, (5, 5), 0)

        # Apply Adaptive Thresholding
        img_cv = cv2.adaptiveThreshold(img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

        # Resize Image for Better OCR Accuracy
        img_cv = cv2.resize(img_cv, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Convert back to PIL format
        processed_image = Image.fromarray(img_cv)

        # Save processed image for debugging
        processed_image.save("/mnt/data/processed_image.png")
        print("✅ Processed Image Saved for Debugging!")

        return processed_image
    except Exception as e:
        print(f"❌ Error in image preprocessing: {str(e)}")
        return None

def extract_text_from_api(image_file):
    """Extracts text from an image using Tesseract OCR."""
    try:
        # Preprocess the image
        processed_image = preprocess_image(image_file)
        if processed_image is None:
            return "Error: Image preprocessing failed"

        # OCR Extraction with Tesseract
        extracted_text = pytesseract.image_to_string(processed_image, config="--psm 6")

        # Print extracted text for debugging
        print("🔍 Extracted OCR Text:\n", extracted_text)

        # If no text is detected, return an error
        if not extracted_text.strip():
            return "Error: OCR extraction failed - No text detected"

        return extracted_text.strip()
    except Exception as e:
        return f"OCR extraction failed: {str(e)}"

def fuzzy_match(expected, extracted):
    """Check similarity between expected and extracted text using fuzzy matching."""
    return fuzz.ratio(expected.lower(), extracted.lower()) > 70  # 70% match is sufficient

def verify_ocr_data(extracted_text, form_data):
    """Compares extracted OCR text with form input."""
    form_name = form_data.get("name", "").strip()
    form_college = form_data.get("college", "").strip()
    form_uid = form_data.get("id", "").strip()

    extracted_name = "Tisha Grover"  # Dummy extracted data (modify as per regex)
    extracted_college = "Some College"
    extracted_uid = "2310987125"

    # Apply fuzzy matching for name and college
    name_match = fuzzy_match(form_name, extracted_name)
    college_match = fuzzy_match(form_college, extracted_college)
    uid_match = form_uid == extracted_uid  # UID should match exactly

    # Verification result
    if name_match and college_match and uid_match:
        return "✅ Verification Successful!"
    elif not name_match:
        return "❌ Name Mismatch!"
    elif not college_match:
        return "❌ College Name Mismatch!"
    elif not uid_match:
        return "❌ UID Mismatch!"
    else:
        return "❌ Verification Failed!"