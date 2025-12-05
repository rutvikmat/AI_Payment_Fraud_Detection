🛡️ FraudGuard AI - Payment Fraud Detection System

Academic Project (2025-26) > Topic: AI-Based Payment Fraud Detection in Petrol Billing

Stack: Django, Python, OpenCV, Scikit-Learn, Tailwind CSS

📌 Project Overview

FraudGuard AI is an automated, real-time system designed to eliminate billing discrepancies, fake UPI screenshots, and employee manipulation at petrol stations. It leverages Machine Learning (Isolation Forest) for pattern detection and Computer Vision (OCR & ELA) for verifying payment screenshots and pump readings.

The system provides a dual-interface: a public-facing Project Synopsis/Landing page and a secured, dark-mode Admin Console for live monitoring.

🚀 Key Features

1. 🧠 AI & ML Modules

Fake Screenshot Detection: Uses Error Level Analysis (ELA) to detect pixel manipulation (Photoshop edits) in UPI payment screenshots.

OCR Verification: Extracts text from screenshots to verify if the "Payment Successful" message and amount match the transaction.

CCTV/Pump Verification: Reads digital numbers from pump images to cross-check fuel dispensed vs. entered amount.

Anomaly Detection: Uses Isolation Forest to flag suspicious transaction patterns (e.g., unusual amounts for specific times).

2. 💻 Interactive Interface

Live Admin Console: A professional, dark-mode dashboard simulating real-time monitoring with Chart.js visualization.

Visual Forensics: Displays forensic evidence (ELA images) directly in the alert feed.

Voice Alerts: Text-to-speech integration announces fraud alerts audibly in the control room.

Reporting: CSV export functionality for audit trails.

🛠️ Tech Stack

Backend: Django 4.x / 5.x (Python)

Frontend: HTML5, Tailwind CSS (CDN), Chart.js

Database: SQLite (Default)

Computer Vision: OpenCV (cv2), Tesseract OCR (pytesseract), Pillow (PIL)

Machine Learning: Scikit-Learn (sklearn)

⚙️ Installation & Setup

1. Prerequisites

Python 3.9+ installed.

Tesseract OCR installed on your machine.

Windows: Download Installer (Add to Path).

Mac: brew install tesseract

Linux: sudo apt install tesseract-ocr

2. Clone & Environment

# Clone the repository (if applicable) or navigate to folder
cd PetrolFraudDetection

# Create Virtual Environment
python -m venv venv

# Activate Environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate


3. Install Dependencies

pip install -r requirements.txt


Note: If requirements.txt is missing, install manually:

pip install django pandas numpy scikit-learn opencv-python pytesseract pillow


4. Database Initialization

# Generate synthetic training data for the ML model
python generate_dataset.py

# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create Admin User (for Django Admin panel)
python manage.py createsuperuser


▶️ How to Run

Start the Server:

python manage.py runserver


Access the Application:

Landing Page: http://127.0.0.1:8000/

Live Admin Console: http://127.0.0.1:8000/live/

New Scan/Analysis: http://127.0.0.1:8000/analyze/

🧪 Demo Scenarios (For Examiners)

Scenario 1: The "Honest" Customer

Input: Fuel: 10L, Bill: 1000.

Result: ✅ Approved. (Logged as valid transaction).

Scenario 2: Billing Mismatch (Logic Check)

Input: Fuel: 50L, Bill: 100. (Math doesn't add up).

Result: 🚨 FRAUD (Amount Mismatch).

Scenario 3: CCTV Mismatch (Visual Check)

Input: Upload Pump Image showing "50.00". Enter Fuel Dispensed as "10.0".

Result: 🚨 FRAUD (Pump Reading Mismatch).

Scenario 4: Fake Screenshot (Forensics)

Input: Upload a generic image or edited receipt.

Result: 🚨 FRAUD (Tampered Screenshot / OCR Fail).

📂 Project Structure

PetrolFraudDetection/
├── manage.py                   # Django Manager
├── generate_dataset.py         # Script to create dummy data
├── db.sqlite3                  # Database
├── media/                      # Stores uploaded evidence
│   ├── screenshots/
│   ├── pump_cctv/
│   └── ela_evidence/           # Generated forensic images
├── core/                       # Main Application App
│   ├── models.py               # Database Schema
│   ├── views.py                # Business Logic
│   ├── ml_utils.py             # AI/OCR/Forensics Logic
│   └── templates/core/
│       ├── dashboard.html      # Landing Page
│       ├── live_dashboard.html # Admin Console
│       └── check_fraud.html    # Analysis Form
└── fraud_detection/            # Project Settings
    ├── settings.py
    └── urls.py


📝 Future Enhancements

Cloud-based centralized fraud database.

Real-time video feed integration (RTSP).

Automated GST bill generation.

