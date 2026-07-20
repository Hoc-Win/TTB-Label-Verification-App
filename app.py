'''
@author: Hoc Nguyen

@desc: ttb-cola.py is a web app developed to process images of labels using Google Gemini engine.
       The app extracts text from the label image and verifies it against TTB-COLA beverage label requirements.
       This app will be deployed on Streamlit Cloud and will be accessible via a web browser.

@Todo: The app can be enhanced to include more features such as:
       - Support for multiple image uploads and batch processing.
       - data table to list all images (labels) with processed status. Click on it will 
         open up the image and show the extracted text and verification result.
       - Add more post-processing to ensure PASSED and FAILED labels processed correctly.


Date    Ver      Changes
------  -------  ----------------------------------------------
260719  1.00.00  Initial Release
260719  1.00.01  Added more comments and wrap extracted text in code block for better readability

'''

import streamlit as st
from PIL import Image
import google.genai as genai


# Setup Gemini API client
try:
    client = genai.Client()

    # **** if model expired, then use following code to look for available models  ****
    # for model in client.models.list():
    #     if "flash" in model.name and "generateContent" in model.supported_actions:
    #         print(f"Available: {model.name}")   
except KeyError:
    st.error("⚠️ Gemini API Key not found. Please add it to your Streamlit secrets.")
    st.stop()


def analyze_label(img):
    # Extract text from the image using Gemini API
    # must use system_instruction and temperature=0.0 to ensure deterministic compliance checking
    try:
        system_instruction = (
            "Using TTB-COLA beverage label requirements, output either '***PASSED***' or '***FAILED***' clearly, "
            "followed by an explanation if it fails. Do not just extract text; you must evaluate it."
        )
        prompt = (
            "Extract text from the image and use TTB-COLA to verify the label. "
            "Provide a summary of the extracted text and any relevant information."
            "Designate '***PASSED***' or '***FAILED***' based on the verification results "
            "for easy identification. If the label is not valid, provide a brief "
            "explanation of why it failed."
        )

        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[img, prompt],
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0  # Crucial for deterministic compliance checking
            )
        )
    except Exception as e:
        st.error(f"❌ Error occurred while processing image: {e}")
        return None

    return response.text

# Resize the image to fit within a container while maintaining aspect ratio
def smart_resize(img):
    img_width, img_height = img.size
    container_width, container_height = 300, 400
    scale = min(container_width / img_width, container_height / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    resized_image = img.resize((new_width, new_height))
    return resized_image


# Setup Streamlit page configuration
st.set_page_config(page_title="TTB Label Verification System", layout="wide")
st.title("🔍 TTB Label Verification System")

# --- Layout for our page ---
left, right = st.columns([2, 3])

# setup the left column for image upload and processing
with left:
    with st.container(height=550):
        uploaded = st.file_uploader("Upload label image", max_upload_size=1, type=["png", "jpg", "jpeg"])
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if uploaded:
                img = Image.open(uploaded)
                
                # resize the image to fit within the container while maintaining aspect ratio
                resized_image = smart_resize(img)

                st.image(resized_image)
        
        with col2:
            process = st.button("Process Label")

# setup the right column for displaying results
with right:
    if process:
        if uploaded:
            # initialize extracted_text to None before processing
            extracted_text = None

            # Use a spinner to indicate that the analysis is in progress
            with st.spinner(f"Analyzing {uploaded.name}..."):
                extracted_text = analyze_label(img)

            #
            if extracted_text is not None:
                if "***PASSED***" in extracted_text:
                    st.success("✅ Label verification PASSED!")
                else:
                    st.error("❌ Label verification FAILED!")

                st.subheader("Extracted Text")
                st.code(extracted_text, wrap_lines=True)
        else:
            st.error("❌ Please upload an image first.")
