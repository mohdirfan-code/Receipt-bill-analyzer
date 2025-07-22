import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import cv2
import numpy as np
import re
import os

def preprocess_image_opencv(file_path):
    """
    Advanced preprocessing using OpenCV to enhance image quality for OCR.
    Steps: grayscale, adaptive threshold, denoising, sharpening.
    """
    img = cv2.imread(file_path)
    if img is None:
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Adaptive thresholding (binarization)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
    )
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 30, 7, 21)
    # Sharpen
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    # Save preprocessed image temporarily
    temp_path = file_path + "_preprocessed.png"
    cv2.imwrite(temp_path, sharpened)
    return temp_path

def ocr_image(file_path, lang="eng"):
    """
    OCR for image files with OpenCV preprocessing fallback.
    """
    try:
        # Try direct OCR first
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang=lang)
        if not text.strip():
            # Try advanced OpenCV preprocessing if OCR result is empty
            preprocessed_path = preprocess_image_opencv(file_path)
            if preprocessed_path:
                image = Image.open(preprocessed_path)
                text = pytesseract.image_to_string(image, lang=lang)
                try:
                    os.remove(preprocessed_path)
                except Exception:
                    pass
        print("OCR Output:", text)  # Debug: print OCR result
        return text
    except Exception as e:
        print(f"OCR failed for image: {e}")
        return ""

def ocr_pdf(file_path, lang="eng"):
    """
    OCR for PDFs; convert each page to image and apply OCR + preprocessing.
    """
    text = ""
    try:
        images = convert_from_path(file_path)
        for idx, img in enumerate(images):
            page_text = pytesseract.image_to_string(img, lang=lang)
            if not page_text.strip():
                # Save PIL Image to OpenCV format for preprocessing
                temp_img_path = f"{file_path}_page{idx}.png"
                img.save(temp_img_path)
                preprocessed_path = preprocess_image_opencv(temp_img_path)
                if preprocessed_path:
                    image = Image.open(preprocessed_path)
                    page_text = pytesseract.image_to_string(image, lang=lang)
                    try:
                        os.remove(preprocessed_path)
                        os.remove(temp_img_path)
                    except Exception:
                        pass
            text += page_text + "\n"
        print("OCR Output:", text)  # Debug: print OCR result
        return text
    except Exception as e:
        print(f"OCR failed for PDF: {e}")
        return ""

def parse_text_file(file_path):
    """Parse text from .txt files directly."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            print("Text file content:", text)  # Debug
            return text
    except Exception as e:
        print(f"Text file parsing failed: {e}")
        return ""

def parse_receipt_text(text):
    """
    Rule-based extraction logic for receipts/bills (regex).
    """
    vendor = None
    date = None
    amount = None
    category = None
    currency = None

    vendor_match = re.search(r'(?:Vendor|Biller|Store|Payee)\s*[:\-]\s*(.+)', text, re.IGNORECASE)
    if vendor_match:
        vendor = vendor_match.group(1).strip()
    else:
        # Fallback: first line as vendor if it's not empty
        lines = text.splitlines()
        for line in lines:
            candidate = line.strip()
            # Look for lines that are likely vendor names (not empty and not numeric)
            if candidate and not re.match(r'^[\d\W]+$', candidate):
                vendor = candidate
                break

    date_match = re.search(r'(\d{4}[/-]\d{2}[/-]\d{2}|\d{2}[/-]\d{2}[/-]\d{4})', text)
    if date_match:
        date = date_match.group(1)

    amount_match = re.search(r'([₹$€£]\s?\d+[.,]?\d*)', text)
    if amount_match:
        try:
            amount = float(re.sub(r'[^\d.]', '', amount_match.group(1)))
        except Exception:
            amount = None
        currency = re.sub(r'[\d.,\s]', '', amount_match.group(1))
    else:
        # Fallback: try to find a line containing 'total' and extract an amount
        for line in lines:
            if 'total' in line.lower():
                amt = re.search(r'(\d+[.,]?\d*)', line)
                if amt:
                    try:
                        amount = float(amt.group(1).replace(',', ''))
                    except Exception:
                        amount = None
                currency = re.search(r'[₹$€£]', line)
                if currency:
                    currency = currency.group(0)
                break

    if vendor:
        if any(word in vendor.lower() for word in ["electricity", "power", "energy"]):
            category = "Utilities"
        elif any(word in vendor.lower() for word in ["grocery", "mart", "food", "whole foods", "walmart"]):
            category = "Groceries"

    return {
        "vendor": vendor,
        "date": date,
        "amount": amount,
        "category": category,
        "currency": currency
    }