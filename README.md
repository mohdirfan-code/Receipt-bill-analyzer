# 📈 Receipt & Bill Analyzer

## Smart Expense Tracking & Analytics

This full-stack mini-application helps you effortlessly manage your expenses by uploading receipts and bills, automatically extracting key data, and providing insightful financial analytics.

---

## ✨ Key Features

- **Intelligent Data Extraction**  
  Automatically parses **Vendor/Biller**, **Date**, **Amount**, **Category**, and **Currency** from `.jpg`, `.png`, `.pdf`, and `.txt` files.

- **Interactive Dashboard**  
  A user-friendly **Streamlit interface** for managing and visualizing your expenses.

- **Tabular View & Manual Correction**  
  View and **edit parsed data directly** in an interactive table via the UI.

- **Powerful Search & Filter**  
  Efficiently find transactions using keywords, amount/date ranges, and vendor patterns.

- **Comprehensive Analytics**  
  Visualizes total spend, mean/median, category/vendor distributions, and monthly spending trends.

- **Data Export**  
  **Export summaries and raw data to CSV and JSON** formats.

- **Currency & Multi-Language OCR Support**  
  Backend designed for currency detection and potential multi-language receipt processing.

---

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

## 🏗️ Architecture

The application uses a **client-server architecture**:

- A **FastAPI Backend** handles all data processing (OCR, parsing, database operations) and exposes RESTful APIs.
- A **Streamlit Frontend** provides the interactive user interface, consuming data from the FastAPI backend.

```mermaid
graph TD
    User -->|Interacts with| Streamlit[Streamlit Frontend]
    Streamlit -->|HTTP Requests| FastAPI[FastAPI Backend]
    FastAPI -->|Data Storage| SQLite[SQLite Database & Local Uploads]
    FastAPI --o|OCR Processing| TesseractPoppler[Tesseract OCR & Poppler]

💻 Setup & Installation
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/mohdirfan-code/Receipt-bill-analyzer.git
cd Receipt-bill-analyzer
2. Install Prerequisites
Ensure the following are installed and added to your system's PATH:

Python 3.11+

Tesseract OCR Engine (with language data)

Poppler

Node.js & npm (optional, useful if switching frameworks)

3. Set Up Python Virtual Environment & Install Dependencies
bash
Copy
Edit
cd backend
python -m venv venv
.\venv\Scripts\activate  # PowerShell
# OR
.\venv\Scripts\activate.bat  # Command Prompt

# Install Python dependencies
pip install -r requirements.txt
Sample requirements.txt (already present in repo):

nginx
Copy
Edit
fastapi
uvicorn
sqlalchemy
pydantic
python-dotenv
flask-cors
python-multipart
pillow
pytest
pytesseract
pdf2image
opencv-python
numpy
streamlit
pandas
requests
4. Ensure Backend Folders Exist
bash
Copy
Edit
mkdir backend\uploads
mkdir backend\db
5. Run FastAPI Backend
In a new terminal:

bash
Copy
Edit
cd backend
.\venv\Scripts\activate
cd ..
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
6. Run Streamlit Frontend
In another terminal:

bash
Copy
Edit
cd backend
.\venv\Scripts\activate
cd ../frontend_streamlit
streamlit run app.py
Access in browser: http://localhost:8501

⚠️ Limitations & Assumptions
Ephemeral Local Storage: Files and DB entries are stored locally and will be lost on cloud restarts. Use persistent storage like AWS S3 or a hosted PostgreSQL DB in production.

OCR Accuracy: Results depend on receipt quality and OCR capabilities. Complex layouts may produce incorrect parsing.

No Currency Conversion: Only detects symbols; no real-time exchange or conversion logic implemented.

No User Authentication: All uploaded data is accessible globally within a running instance.

📸 Screenshots / Demo
(Insert screenshots or a link to a screen recording/demo video here)

❤️ Contribution & Contact
Developed by Firdous as part of the internship assignment.

GitHub: https://github.com/mohdirfan-code/Receipt-bill-analyzer
Feel free to open issues or pull requests!

vbnet
Copy
Edit
