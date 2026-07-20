TTB Label Verification System (AI Prototype)
📌 Project Overview
This repository contains a proof-of-concept web application designed for the Alcohol and Tobacco Tax and Trade Bureau (TTB) Compliance Division. The application leverages a multimodal Large Language Model (LLM) to automate the optical verification of alcohol beverage labels against expected COLA application data, drastically reducing manual data entry verification while maintaining strict regulatory compliance.

**Live Prototype:** [Click here to access the live web app](https://ttb-label-verification-app-avabknkbcz7n7yps6fre8t.streamlit.app/)

---
🏗️ System Architecture & Approach
This application utilizes a native multimodal LLM (Google Gemini 3.5 Flash) to ingest the raw image pixels and evaluate compliance in a single, parallel pass. The application enforces a designated pass or fail string for easy extraction in order to visually show whether the label passed or failed. Any fauilures will include an explanation to justify the result.

The app is designed to be simple to use. Just upload an image of a label, then click the "Process Label" button to get the PASSED or FAILED result.

The app's user interface (UI) is developed with the Streamlit layout. It consists of a simple, easy-to-use layout:

Two panels: Left, Right
The left panel consists of an Upload button to upload an image of a label and a "Process Label" button to process.
The left panel also contains the uploaded image, which will be resized with the proper aspect ratio and displayed below the Upload button.
The right panel is dedicated to error messages and the results of the AI analysis. It should provide the following visualizations:
Error message indicating an image needs to be uploaded before processing
Busy graphics indicating processing in progress
Red or green message indicating FAILURE or PASSING of the analysis
Extracted text from the image
The AI analysis
🛠️ Tools Used & Trade-Offs
Frontend: Streamlit

Justification: Enables rapid prototyping of data-focused web applications in pure Python.
AI Engine: Google Gemini 1.5 Flash via google-genai

Justification: Optimized for high-speed, multimodal tasks. It handles curved labels, glare, and poor lighting natively without requiring pre-processing image filters.
🔒 Security & Assumptions
For security purpose, this application utilizes everything from the internet. It does not retain any data.
It requires outbout access to the provided URL (https://ttb-label-verification-app-avabknkbcz7n7yps6fre8t.streamlit.app/)
💠 Future Enhancements
This app serves as a quick proof of concept. It can be enhanced to include additional features, such as:

Support for multiple image uploads and batch processing.
A data table listing all images (and their labels) with processing status. Clicking on an entry will open the image to display the extracted text and verification result.
Ability to save the AI analysis.
Ability to generate and save report for batch processing.
Enhanced post-processing to ensure "PASSED" and "FAILED" labels are justified correctly.
💻 Local Setup & Run Instructions
If you wish to run this application locally on your machine rather than using the deployed web version, follow these steps:

Clone the repository
Install python
Install packages listed in the requirements.txt
From terminal, issue command:streamlit run app.py
