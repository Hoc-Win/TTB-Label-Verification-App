import streamlit as st
import google.generativeai as genai
from PIL import Image
from pydantic import BaseModel, Field
import json

# ==========================================
# 1. PAGE CONFIGURATION & UI SETUP
# ==========================================
st.set_page_config(page_title="TTB Label Verification System", layout="wide", page_icon="🔍")

st.title("🔍 TTB Label Verification System")
st.markdown("Upload label images and input the expected application data to verify compliance.")

# ==========================================
# 2. API KEY AUTHENTICATION & SETUP
# ==========================================
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("⚠️ Gemini API Key not found. Please add it to your Streamlit secrets.")
    st.stop()

# ==========================================
# 3. STRUCTURED OUTPUT SCHEMA
# ==========================================
class LabelVerification(BaseModel):
    brand_match: bool = Field(description="True if brand names match (forgiving of minor punctuation/casing).")
    extracted_brand: str = Field(description="The exact brand name text found on the label.")
    
    class_match: bool = Field(description="True if class/type matches.")
    extracted_class: str = Field(description="The exact class/type text found on the label.")
    
    abv_match: bool = Field(description="True if ABV matches.")
    extracted_abv: str = Field(description="The exact ABV text found on the label.")
    
    warning_match: bool = Field(description="True ONLY if the warning text is a word-for-word exact match, and 'GOVERNMENT WARNING:' is in ALL CAPS.")
    extracted_warning: str = Field(description="The exact warning text extracted from the label.")
    
    overall_decision: str = Field(description="Must be 'Approve', 'Reject', or 'Flag for Review'.")
    requires_human_review: bool = Field(description="True if the image is too blurry, angled, or illegible to make a confident decision.")
    discrepancy_notes: str = Field(description="Brief explanation of any rejections, mismatches, or reasons for review.")

# ==========================================
# 4. USER INTERFACE
# ==========================================
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("📝 1. Expected Application Data")
    st.info("Input the data exactly as it appears on the COLA application.")
    
    # UI Refinement #1 & #3: Added asterisks for required fields and removed hardcoded dummy data
    expected_brand = st.text_input("Brand Name *", placeholder="Enter brand name...")
    expected_class = st.text_input("Class/Type *", placeholder="Enter class/type...")
    expected_abv = st.text_input("Alcohol Content (ABV) *", placeholder="Enter ABV...")
    
with col2:
    st.subheader("📸 2. Label Image Upload")
    # UI Refinement #2: The batch uploader is built natively into this single component
    uploaded_files = st.file_uploader("Upload Label Images (Drag & drop multiple files for batch processing)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.divider()

# ==========================================
# 5. CORE AI LOGIC & PROCESSING
# ==========================================
if st.button("🚀 Verify Label Compliance", type="primary", use_container_width=True):
    
    # UI Refinement #3: Strict validation guardrails before API execution
    if not expected_brand or not expected_class or not expected_abv:
        st.error("🚨 *Please fill out all required text fields (marked with *) before verifying.*")
    elif not uploaded_files:
        st.warning("⚠️ *Please upload at least one label image to begin verification.*")
    else:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # UI Refinement #2: Batch processing progress bar setup
        total_files = len(uploaded_files)
        progress_bar = st.progress(0, text="Initializing batch verification...")
        
        for index, uploaded_file in enumerate(uploaded_files):
            # Update progress bar for each file
            current_file_num = index + 1
            progress_bar.progress(current_file_num / total_files, text=f"Processing label {current_file_num} of {total_files}: {uploaded_file.name}")
            
            image = Image.open(uploaded_file)
            
            with st.spinner(f"Analyzing {uploaded_file.name}... (Target: < 5 seconds)"):
                
                prompt = f"""
                You are an expert TTB Compliance Agent. Review the provided alcohol label image against the expected application data.
                
                Expected Data:
                - Brand Name: {expected_brand}
                - Class/Type: {expected_class}
                - ABV: {expected_abv}
                
                Rules for Evaluation:
                1. Fuzzy Matching (Dave's Rule): For Brand, Class, and ABV, forgive minor punctuation or capitalization differences (e.g., "STONE'S THROW" matches "Stone's Throw").
                2. Strict Matching (Jenny's Rule): Locate the health warning. It MUST begin with "GOVERNMENT WARNING:" in exactly ALL CAPS. If it says "Government Warning" or uses different casing, it is an instant failure.
                3. Quality Control: Compensate for bad angles or glare. If the text is completely unreadable, flag for human review.
                """
                
                try:
                    response = model.generate_content(
                        [prompt, image],
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json",
                            response_schema=LabelVerification,
                            temperature=0.1
                        )
                    )
                    
                    result = json.loads(response.text)
                    
                    # ==========================================
                    # 6. RESULTS DISPLAY
                    # ==========================================
                    st.markdown(f"### Results for: `{uploaded_file.name}`")
                    
                    if result["requires_human_review"]:
                        st.warning("🟡 **FLAGGED FOR HUMAN REVIEW:** Image quality is too low or text is illegible.")
                    elif result["overall_decision"] == "Approve":
                        st.success("✅ **APPROVED:** Label matches application data and warning is compliant.")
                    else:
                        st.error("🔴 **REJECTED:** Discrepancies found.")
                    
                    if result["discrepancy_notes"]:
                        st.write(f"**Agent Notes:** {result['discrepancy_notes']}")
                    
                    def status_icon(match):
                        return "✅ Pass" if match else "❌ Fail"

                    st.markdown(f"""
                    | Field | Status | Expected (COLA Form) | Extracted (What AI Saw) |
                    | :--- | :--- | :--- | :--- |
                    | **Brand Name** | {status_icon(result['brand_match'])} | {expected_brand} | {result['extracted_brand']} |
                    | **Class/Type** | {status_icon(result['class_match'])} | {expected_class} | {result['extracted_class']} |
                    | **ABV** | {status_icon(result['abv_match'])} | {expected_abv} | {result['extracted_abv']} |
                    | **Gov. Warning** | {status_icon(result['warning_match'])} | *Strict Format Required* | *See expander below* |
                    """)
                    
                    with st.expander("View Extracted Government Warning Text"):
                        st.write(result["extracted_warning"])
                    
                    st.divider()

                except Exception as e:
                    st.error(f"An error occurred while processing {uploaded_file.name}: {e}")
                    
        # Clear the progress bar when the batch is fully complete
        progress_bar.empty()
