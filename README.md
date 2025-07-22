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
## 📸 Screenshots / Demo 
<img width="1920" height="1008" alt="Image" src="https://github.com/user-attachments/assets/af8f369b-4ad5-466f-abe0-5e4fde541e4d" />
<img width="1920" height="1008" alt="Image" src="https://github.com/user-attachments/assets/6d935a78-c267-425f-a8b8-b7955027eca5" />
<img width="1920" height="1008" alt="Image" src="https://github.com/user-attachments/assets/3bc9acf4-c503-44e9-92af-bc491f1f2ba0" />
<img width="1920" height="1008" alt="Image" src="https://github.com/user-attachments/assets/0e0f2b6b-331e-4c57-84da-aabe009737c1" />
<img width="1920" height="1008" alt="Image" src="https://github.com/user-attachments/assets/37ae8e60-b32b-4a7d-8948-3a7faf589120" />
<img width="1920" height="1008" alt="Image" src="https://github.com/user-attachments/assets/61483727-3c49-4f09-8b34-47ca11f6ce6a" />
<img width="1920" height="1008" alt="Image" src="https://github.com/user-attachments/assets/0db9c2b8-8853-4da8-91b9-241eb50b0b23" />
<img width="1920" height="1008" alt="Image" src="https://github.com/user-attachments/assets/79218e06-1f3a-4e6b-ae42-35ed6f9cff61" />
---

## 🏗️ Architecture

The application uses a **client-server architecture**:

- A **FastAPI Backend** handles all data processing (OCR, parsing, database operations) and exposes RESTful APIs.
- A **Streamlit Frontend** provides the interactive user interface, consuming data from the FastAPI backend.


## 💻 Setup & Installation

```
1. Clone the Repository
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
```

❤️ Developed by Mohd Irfan.
