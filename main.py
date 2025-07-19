from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
from pdf2image import convert_from_bytes
import google.generativeai as genai
from io import BytesIO
import pandas as pd
import re
import difflib

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("Google API Key not found. Please check your .env file.")
    st.stop()

genai.configure(api_key=api_key)

# Constants
VALID_DEPTS = {"ARE", "ECE", "CCE", "CYS", "MEE", "CSE"}

# Gemini helper
def get_gemini_response(input_text, image_data, user_query):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input_text, image_data[0], user_query])
    return response.text

def input_image_setup(file_bytes, mime_type):
    return [{"mime_type": mime_type, "data": file_bytes}]

def pdf_to_images(file):
    poppler_path = r"C:\Users\deva6\poppler-24.08.0\Library\bin"  # Update if needed
    return convert_from_bytes(file.read(), fmt='jpeg', poppler_path=poppler_path)

def extract_dept_code(reg):
    match = re.search(r"U4([A-Z]{3})", reg)
    return match.group(1) if match else None

def fix_register_number_force(raw, correct_dept="CSE"):
    raw = raw.upper().replace(" ", "").replace("-", "").replace(".", "")
    dept_match = re.search(r"([A-Z]{3})\d{5}$", raw)
    suffix_match = re.search(r"(\d{5})$", raw)
    dept = dept_match.group(1) if dept_match else correct_dept
    suffix = suffix_match.group(1) if suffix_match else "00000"
    if dept not in VALID_DEPTS:
        closest = difflib.get_close_matches(dept, VALID_DEPTS, n=1)
        dept = closest[0] if closest else correct_dept
    return f"CH.EN.U4{dept}{suffix}"

# Prompts
input_prompt = """
You are an expert in analyzing student exam slips.

From the uploaded image, extract:
1. Full Register Number (e.g., CH.EN.U4ECE23003)
2. Course Code (e.g., 23ECE102)
3. Serial Number — a 6-digit number printed at the top right next to "Sl.No.: AC"

Return in this format:
Register Number: <value>
Course Code: <value>
Serial Number: <value>
"""

marks_prompt = """
You are analyzing a student marks slip.

From the uploaded image, extract:
1. Serial Number — a 6-digit number (e.g., 144972)
2. Marks for each question — If available, extract marks for each question as:
   Q1: <value>, Q2: <value>, ..., Qn: <value>
3. Total Marks — Look for the value labeled "Total Marks", "Total", or similar.

Ignore questions that are not mentioned. Return in this format:

Serial Number: <value>
Q1: <value>
Q2: <value>
...
Total Marks: <value>
"""

# Streamlit UI
st.set_page_config(page_title="Slip Extractor")
st.title("Exam Slip + Marks Extractor")

uploaded_exam_file = st.file_uploader("Upload Exam Slip (Image or PDF)", type=["jpg", "jpeg", "png", "pdf"])
uploaded_marks_file = st.file_uploader("Upload Marks Slip (Image or PDF)", type=["jpg", "jpeg", "png", "pdf"])
submit = st.button("Extract and Merge")

if uploaded_exam_file and uploaded_marks_file and submit:
    try:
        # Step 1: Exam Slip Extraction
        exam_type = uploaded_exam_file.type
        exam_images = pdf_to_images(uploaded_exam_file) if exam_type == "application/pdf" else [Image.open(uploaded_exam_file)]

        exam_results = []
        for idx, img in enumerate(exam_images):
            st.image(img, caption=f"Exam Slip Page {idx+1}", use_container_width=True)
            buffer = BytesIO()
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(buffer, format="JPEG")
            image_bytes = buffer.getvalue()
            image_data = input_image_setup(image_bytes, "image/jpeg")
            response = get_gemini_response(input_prompt, image_data, "Extract exam slip info")

            reg_match = re.search(r"Register Number: (.+)", response)
            course_match = re.search(r"Course Code: (.+)", response)
            serial_match = re.search(r"Sl\.?No\.?:?\s*AC\s*(\d{6})", response, re.IGNORECASE)
            fallback_serial_match = re.search(r"Serial Number:\s*(\d{6})", response)

            if serial_match:
                serial = serial_match.group(1).strip()
            elif fallback_serial_match:
                serial = fallback_serial_match.group(1).strip()
            else:
                serial = "Not found"

            reg = reg_match.group(1).strip() if reg_match else "Not found"
            course = course_match.group(1).strip() if course_match else "Not found"

            exam_results.append({
                "Page": idx + 1,
                "Register Number": reg,
                "Course Code": course,
                "Serial Number": serial
            })

            with st.expander(f"Gemini Response (Exam Page {idx+1})"):
                st.code(response, language="markdown")

        df_exam = pd.DataFrame(exam_results)
        df_exam["Serial Number"] = df_exam["Serial Number"].astype(str).str.extract(r"(\d{6})")

        # Fix register numbers
        dept_counts = df_exam["Register Number"].apply(extract_dept_code).value_counts()
        correct_dept = dept_counts.idxmax() if not dept_counts.empty else "CSE"
        df_exam["Register Number"] = df_exam["Register Number"].apply(lambda x: fix_register_number_force(x, correct_dept))

        if not df_exam["Course Code"].isnull().all():
            majority_course = df_exam["Course Code"].value_counts().idxmax()
            df_exam["Course Code"] = majority_course

        st.subheader("Extracted Exam Data")
        st.dataframe(df_exam)

        # Step 2: Marks Slip Extraction
        marks_type = uploaded_marks_file.type
        marks_images = pdf_to_images(uploaded_marks_file) if marks_type == "application/pdf" else [Image.open(uploaded_marks_file)]

        marks_results = []
        for idx, img in enumerate(marks_images):
            st.image(img, caption=f"Marks Slip Page {idx+1}", use_container_width=True)
            buffer = BytesIO()
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(buffer, format="JPEG")
            image_bytes = buffer.getvalue()
            image_data = input_image_setup(image_bytes, "image/jpeg")
            response = get_gemini_response(marks_prompt, image_data, "Extract marks info")

            serial_match = re.search(r"Serial Number: (\d{6})", response)
            total_match = re.search(r"Total Marks: (\d+)", response)

            serial = serial_match.group(1).strip() if serial_match else "Not found"
            total = total_match.group(1).strip() if total_match else "Not found"

            question_marks = dict(re.findall(r"(Q\d+):\s*(\d+)", response))
            question_marks = {q: int(m) for q, m in question_marks.items()}

            entry = {"Serial Number": serial}
            entry.update(question_marks)
            entry["Total Marks"] = int(total) if total.isdigit() else None

            marks_results.append(entry)

            with st.expander(f"Gemini Response (Marks Page {idx+1})"):
                st.code(response, language="markdown")

        df_marks = pd.DataFrame(marks_results)
        df_marks["Serial Number"] = df_marks["Serial Number"].astype(str).str.extract(r"(\d{6})")

        question_cols = sorted([col for col in df_marks.columns if col.startswith("Q")], key=lambda x: int(x[1:]))
        df_marks[question_cols] = df_marks[question_cols].fillna(0).astype(int)
        df_marks = df_marks[["Serial Number"] + question_cols + ["Total Marks"]]

        st.subheader("Extracted Marks Data")
        st.dataframe(df_marks)

        # Step 3: Merge & Preserve Exam Order
        final_df = pd.merge(df_exam, df_marks, on="Serial Number", how="inner")
        final_df = final_df.set_index("Serial Number")
        final_df = final_df.loc[df_exam["Serial Number"]].reset_index()

        question_cols = sorted([col for col in final_df.columns if re.match(r"Q\d+", col)], key=lambda x: int(x[1:]))
        final_df["Question Sum"] = final_df[question_cols].sum(axis=1)
        final_df["Match?"] = final_df["Question Sum"] == final_df["Total Marks"]
        final_df.drop(columns=["Question Sum"], inplace=True)

        final_columns = ["Register Number", "Serial Number", "Course Code"] + question_cols + ["Total Marks", "Match?"]
        filtered_df = final_df[final_columns]

        st.subheader(" Final Merged Data (Exam + Marks)")
        st.dataframe(filtered_df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name="Final Merged")

        st.download_button("⬇ Download Final Excel",
                           data=output.getvalue(),
                           file_name="final_exam_marks_data.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"An error occurred: {e}")
