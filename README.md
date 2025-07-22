# 📈 Receipt & Bill Analyzer

## Smart Expense Tracking & Analytics

This full-stack mini-application helps you effortlessly manage your expenses by uploading receipts and bills, automatically extracting key data, and providing insightful financial analytics.

---

## ✨ Key Features

- **Intelligent Data Extraction**  
  Automatically parses **Vendor/Biller**, **Date**, **Amount**, **Category**, and **Currency** from `.jpg`, `.png`, `.pdf`, and `.txt` files.

- **Interactive Dashboard**  
  A user-friendly **Streamlit interface** for managing and visualizing your expenses.

- **Powerful Search & Filter**  
  Efficiently find transactions using keywords, amount/date ranges, and vendor patterns.

- **Comprehensive Analytics**  
  Visualizes total spend, mean/median, category/vendor distributions, and monthly spending trends.

---

## 🎁 Implemented Bonus Features
-**Manual Field Correction via UI: Users can edit and correct parsed data directly in the interactive table presented in the Streamlit UI.**

- **Data Export**  
  **Export summaries and raw data to CSV and JSON** formats.

- **Currency & Multi-Language OCR Support**  
  Backend designed for currency detection and potential multi-language receipt processing

## 🚀 Technologies Used

### 🔧 Backend:
- **Python**: Core language
- **FastAPI**: High-performance web framework for REST APIs
- **SQLAlchemy**: ORM for SQLite database interaction
- **Pydantic**: Data validation
- **`pytesseract` & `opencv-python`**: For OCR and image processing
- **`pdf2image`**: For PDF processing (requires Poppler)

### 🎨 Frontend:
- **Streamlit**: Python framework for building interactive web applications
- **`requests`**: For API communication with the backend
- **`pandas`**: For data manipulation and display

### 🧰 Tools & External Dependencies:
- **Git & GitHub**: Version control and hosting
- **Tesseract OCR Engine**: External OCR software
- **Poppler**: External PDF rendering library

---
##📸 Screenshots / Demo
---

## 🏗️ Architecture

The application uses a **client-server architecture**:

- A **FastAPI Backend** handles all data processing (OCR, parsing, database operations) and exposes RESTful APIs.
- A **Streamlit Frontend** provides the interactive user interface, consuming data from the FastAPI backend.


----
## 💻 Setup & Installation

1. Clone the Repository

```bash
git clone https://github.com/mohdirfan-code/Receipt-bill-analyzer.git
cd Receipt-bill-analyzer

2. Set Up Virtual Environment & Install Dependencies
cd backend
python -m venv venv
.\venv\Scripts\activate  # PowerShell
# OR
.\venv\Scripts\activate.bat  # CMD

pip install -r requirements.txt


3. Run FastAPI Backend
cd backend
.\venv\Scripts\activate
cd ..
uvicorn backend.main:app --reload 

4. Run Streamlit Frontend
cd backend
.\venv\Scripts\activate
cd ../frontend_streamlit
streamlit run app.py
-

❤️ Contribution & Contact
Developed by Mohd Irfan.
