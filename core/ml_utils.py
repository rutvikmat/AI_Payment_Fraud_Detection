import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageChops, ImageEnhance
import pandas as pd
from sklearn.ensemble import IsolationForest
import os
import re
import uuid

# --- 1. SCREENSHOT FORENSICS MODULE ---

def error_level_analysis(image_path, quality=90):
    """
    Performs ELA to detect if an image has been edited.
    It resaves the image at a specific quality and subtracts it from the original.
    High differences indicate potential manipulation.
    """
    try:
        original = Image.open(image_path).convert('RGB')
        
        # Save a temporary resaved image
        resaved_path = 'temp_ela.jpg'
        original.save(resaved_path, 'JPEG', quality=quality)
        resaved = Image.open(resaved_path)
        
        # Create the ELA image (difference)
        ela_image = ImageChops.difference(original, resaved)
        
        # Enhance brightness to make differences visible
        extrema = ela_image.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
        scale = 255.0 / max_diff
        ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
        
        # Clean up
        if os.path.exists(resaved_path):
            os.remove(resaved_path)
            
        return ela_image
    except Exception as e:
        print(f"ELA Error: {e}")
        return None

def extract_text_from_image(image_path):
    """
    Uses Tesseract OCR to extract text from UPI screenshots.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return ""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Simple preprocessing
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        text = pytesseract.image_to_string(gray)
        return text.lower()
    except Exception as e:
        print(f"Text Extraction Error: {e}")
        return ""

def detect_screenshot_fraud(image_path, claimed_amount):
    """
    Analyzes a screenshot for fraud indicators.
    """
    text = extract_text_from_image(image_path)
    
    results = {
        'is_suspicious': False,
        'reasons': [],
        'extracted_text': text
    }

    # 1. Keyword Check
    if "payment successful" not in text and "paid" not in text:
        results['reasons'].append("Missing 'Payment Successful' confirmation text.")
        results['is_suspicious'] = True

    # 2. Amount Mismatch Check (Simple string search)
    if str(int(claimed_amount)) not in text:
        results['reasons'].append(f"Claimed amount {claimed_amount} not found clearly in screenshot.")
        # We assume suspicion if exact amount string isn't found
        # results['is_suspicious'] = True 

    return results

# --- 2. CCTV / PUMP READER MODULE ---

def extract_numbers_from_image(image_path):
    """
    Specific OCR to find numbers in a Pump/CCTV image.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []
            
        # Preprocessing for digital numbers (often bright on dark background)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Configure Tesseract to look for digits only
        custom_config = r'--oem 3 --psm 6 outputbase digits'
        text = pytesseract.image_to_string(gray, config=custom_config)
        
        # Find all numbers (integers or decimals)
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        return [float(n) for n in numbers]
    except Exception as e:
        print(f"OCR Error: {e}")
        return []

# --- 3. TRANSACTION PATTERN MODULE ---

def train_anomaly_model():
    """
    Trains an Isolation Forest model on the generated dataset.
    """
    dataset_path = 'datasets/transaction_data.csv'
    if not os.path.exists(dataset_path):
        return None
        
    try:
        df = pd.read_csv(dataset_path)
        # Features: FuelLiters, BillAmount
        X = df[['FuelLiters', 'BillAmount']]
        
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(X)
        return model
    except Exception as e:
        print(f"Training Error: {e}")
        return None

# Initialize model globally
anomaly_model = train_anomaly_model()

def check_transaction_anomaly(liters, amount):
    """
    Predicts if a transaction is anomalous using the trained model.
    """
    if anomaly_model is None:
        return False
        
    try:
        # Isolation Forest returns -1 for anomalies, 1 for normal
        prediction = anomaly_model.predict([[liters, amount]])
        return prediction[0] == -1
    except Exception as e:
        print(f"Prediction Error: {e}")
        return False
    

def detect_screenshot_fraud(image_path, claimed_amount):
    # ... keep existing text extraction code ...
    
    # 1. Generate ELA Image
    ela_image = error_level_analysis(image_path)
    ela_filename = f"ela_{uuid.uuid4().hex}.jpg"
    ela_save_path = os.path.join(settings.MEDIA_ROOT, 'ela_evidence', ela_filename)
    
    # Create directory if not exists
    os.makedirs(os.path.dirname(ela_save_path), exist_ok=True)
    
    # Save the forensic image
    if ela_image:
        ela_image.save(ela_save_path)
    
    # ... keep existing logic ...
    
    return {
        'is_suspicious': results['is_suspicious'],
        'reasons': results['reasons'],
        'ela_path': f"ela_evidence/{ela_filename}" # Return this path
    }