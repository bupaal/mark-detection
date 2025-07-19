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

 Set Up Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
3. Configure API Key
Create a .env file in the project root:

ini
Copy
Edit
GOOGLE_API_KEY=your_google_api_key_here
4. Run the App
bash
Copy
Edit
streamlit run main.py
📁 Project Structure
bash
Copy
Edit
mark-detection/
├── main.py            # Streamlit app logic
├── .env               # API key (excluded via .gitignore)
├── requirements.txt   # Required packages
├── README.md          # This file
└── .devcontainer/     # Dev environment setup (optional)
✅ Sample Output (Excel)
Register Number	Serial Number	Course Code	Q1	Q2	...	Total Marks	Match?
CH.EN.U4CSE23004	233069	23CSE101	5	6	...	53	✅
CH.EN.U4CSE23016	233216	23CSE101	6	7	...	56	✅

Match? validates if the total equals the sum of question-wise marks.

🧠 Prompt Strategy
Gemini is given separate optimized prompts for:

Exam Slip: Register No, Course Code, Serial No

Marks Slip: Serial No, Q-wise Marks, Total

Post-processing includes:

Regex-based cleanup

Department code correction (e.g., fixing “PRE” to closest valid code like “CSE”)

⚙️ Dependencies
nginx
Copy
Edit
streamlit
pillow
pdf2image
python-dotenv
pandas
xlsxwriter
google-generativeai
📌 Notes
Poppler must be installed for PDF conversion (e.g., C:\poppler\bin)

.env file is excluded via .gitignore

Use on clear scanned documents for best accuracy

👤 Author
Haridoss Bupaal
