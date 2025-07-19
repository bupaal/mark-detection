Mark Detection System

A Streamlit-based application to **automatically extract** student data such as **Register Number**, **Course Code**, **Serial Number**, and **Total Marks** from scanned exam and marks slips using the **Gemini Vision-Language model (1.5 Flash)**.

## 🔍 Objective

To automate and standardize data extraction from exam documents using vision-language AI, reducing manual effort and improving accuracy for institutional workflows.

---

## 🧰 Features

- 📌 Extracts:
  - Register Number (e.g., CH.EN.U4CSE23012)
  - Course Code (e.g., 23CSE102)
  - Serial Number (top-right corner)
  - Question-wise marks
  - Total marks

- 📄 Supports JPG, PNG, and PDF
- 🛠️ Auto-corrects malformed Register Numbers
- 🔗 Merges exam and marks slips based on Serial Number
- 📥 Outputs a downloadable Excel sheet

---

## 🏗️ Tech Stack

| Tool        | Purpose                     |
|-------------|-----------------------------|
| Streamlit   | Web interface               |
| Gemini API  | Vision-language extraction  |
| OpenCV/PIL  | Image processing            |
| pdf2image   | PDF conversion              |
| pandas      | Data manipulation           |
| dotenv      | API key management          |

---

## 🖥️ How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/bupaal/mark-detection.git
cd mark-detection
