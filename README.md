# Mark Detection System

This project is a web-based application that extracts and validates student examination data from scanned exam and mark slips vision-language models like GEMINI AI.

## Features

* Upload scanned **exam slips** and **mark slips** (PDF/JPG/PNG)
* Extracts:

  * Register Number, Course Code, Serial Number (from Exam Slip)
  * Serial Number, Question-wise Marks, Total Marks (from Mark Slip)
* Validates total marks against individual question scores
* Handles noisy data using:

  * Regex cleanup
  * Department code correction (e.g., fixes `CSC` to `CSE`)
* Exports results to Excel

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/bupaal/mark-detection.git
cd mark-detection
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Key

Create a `.env` file in the root folder and add your Google API key:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Run the Application

```bash
streamlit run main.py
```

---

## Project Structure

```
mark-detection/
├── main.py            # Streamlit app logic
├── .env               # API key config (excluded via .gitignore)
├── requirements.txt   # Python dependencies
├── README.md          # Project documentation
└── .devcontainer/     # Optional development container setup
```

---

## Sample Excel Output Format

| Register Number  | Serial Number | Course Code | Q1 | Q2 | ... | Total Marks | Match? |
| ---------------- | ------------- | ----------- | -- | -- | --- | ----------- | ------ |
| CH.EN.U4CSE23004 | 233069        | 23CSE101    | 5  | 6  | ... | 53          | ✅      |
| CH.EN.U4CSE23016 | 233216        | 23CSE101    | 6  | 7  | ... | 56          | ✅      |

> The **Match?** column verifies if total marks equal the sum of question-wise marks.

---

## Notes

* Poppler must be installed for PDF-to-image conversion
  (e.g., `C:\poppler\bin` on Windows)
* `.env` file is excluded from the repository for security
* Works best on high-quality scanned documents

---

## Dependencies

* streamlit
* pillow
* pdf2image
* python-dotenv
* pandas
* xlsxwriter
* google-generativeai

---

## Author

Haridoss Bupaal


