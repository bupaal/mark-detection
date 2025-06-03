from dotenv import load_dotenv
import streamlit as st
import os
import pandas as pd
import re
from io import BytesIO
from PIL import Image
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Google API Key not found. Please check your .env file.")
    st.stop()

genai.configure(api_key=api_key)

def get_gemini_response(image):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt_text = """
        You are an AI expert in analyzing mark sheets.
        Extract only the Serial Number (6-digit only) from the given image.
        Format your response as:
        Serial No: [extracted value]
    """
    response = model.generate_content([prompt_text, image])
    return response.text

def process_image(image_file):
    if image_file is not None:
        return Image.open(image_file)
    return None

def extract_valid_serial_no(text):
    serial_numbers = re.findall(r'\b\d{6}\b', text)
    return serial_numbers[0] if serial_numbers else ""

def save_to_excel(data):
    df = pd.DataFrame(data)
    df["Serial No"] = df["Serial No"].astype(str).str.strip()
    is_valid = df["Serial No"].str.match(r"^\d{6}$")
    valid_df = df[is_valid]
    dummy_df = df[~is_valid]
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        valid_df.to_excel(writer, sheet_name="Valid", index=False)
        dummy_df.to_excel(writer, sheet_name="Dummy", index=False)
    output.seek(0)
    return output

if "captured_images" not in st.session_state:
    st.session_state.captured_images = []

if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = []

st.set_page_config(page_title="Serial Number Extractor")
st.header("Serial Number Extractor with Camera Support")

st.subheader("Capture All Required Images First")
captured_image = st.camera_input("Take a picture", key=f"camera_{len(st.session_state.captured_images)}")

if captured_image is not None:
    st.session_state.captured_images.append(captured_image)
    st.success(f"Image {len(st.session_state.captured_images)} captured! Capture more if needed.")

if st.session_state.captured_images:
    st.subheader("Captured Images")
    for idx, img in enumerate(st.session_state.captured_images):
        st.image(img, caption=f"Image {idx + 1}", use_container_width=True)

if st.button("Clear Captured Images"):
    st.session_state.captured_images = []
    st.session_state.extracted_data = []
    st.rerun()

if st.button("Process All Captured Images"):
    if not st.session_state.captured_images:
        st.warning("No images captured! Please take some photos first.")
    else:
        st.session_state.extracted_data = []
        for idx, image_file in enumerate(st.session_state.captured_images):
            image = process_image(image_file)
            response = get_gemini_response(image)
            serial_no = extract_valid_serial_no(response)
            st.session_state.extracted_data.append({"Serial No": serial_no})
        st.success("Processing completed!")

if st.session_state.extracted_data:
    st.subheader("Extracted Serial Numbers")
    st.table(st.session_state.extracted_data)
    excel_file = save_to_excel(st.session_state.extracted_data)
    st.download_button(
        label="Download Serial Numbers (Excel)",
        data=excel_file,
        file_name="serial_numbers.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
