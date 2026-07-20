# TTB Label Verification System (AI Prototype)

## 📌 Project Overview
This repository contains a proof-of-concept web application designed for the Alcohol and Tobacco Tax and Trade Bureau (TTB) Compliance Division. The application leverages a multimodal Large Language Model (LLM) to automate the optical verification of alcohol beverage labels against expected COLA application data, drastically reducing manual data entry verification while maintaining strict regulatory compliance.

**Live Prototype:** [Click here to access the live web app](https://ttb-label-verification-app-avabknkbcz7n7yps6fre8t.streamlit.app/)

---

## 🏗️ System Architecture & Approach

Traditional Optical Character Recognition (OCR) systems process documents sequentially (Scan -> Extract -> Regex Match), which often results in processing times exceeding 30 seconds. To meet the TTB's strict <5-second latency requirement, this application bypasses traditional OCR. 

Instead, it utilizes a native multimodal LLM (Google Gemini 1.5 Flash) to ingest the raw image pixels and evaluate compliance in a single, parallel pass. The application enforces a **Structured Output Schema (Pydantic)** to guarantee the AI returns a predictable, crash-proof JSON object, allowing for deterministic UI rendering.

### Stakeholder Requirements Addressed:
* **The "Mother" UI Test (Sarah & Dave):** A strict, single-page, dual-column dashboard. Inputs on the left, images on the right, and one primary button. No nested menus.
* **Batch Processing (Janet):** The file uploader accepts multiple label images simultaneously, processing them in a loop to clear heavy queues during peak seasons.
* **Fuzzy vs. Strict Matching (Dave & Jenny):** The AI prompt isolates evaluation logic. Brand names and ABV allow for typographical leniency (e.g., "STONE'S THROW" vs "Stone's Throw"), while the Government Warning enforces a zero-tolerance, exact-character match including ALL CAPS casing.
* **Explainable AI (Auditability):** The results output a side-by-side table comparing the expected COLA data against exactly what the AI extracted from the label, building trust with the agents.

---

## 🛠️ Tools Used & Trade-Offs

* **Frontend:** `Streamlit`
  * *Justification:* Enables rapid prototyping of data-focused web applications in pure Python. 
  * *Trade-off:* Less customizable than a React/Node.js frontend, but perfect for a standalone proof-of-concept prioritizing speed of delivery.
* **AI Engine:** `Google Gemini 1.5 Flash` via `google-generativeai`
  * *Justification:* Optimized for high-speed, multimodal tasks. It handles curved labels, glare, and poor lighting natively without requiring pre-processing image filters.
  * *Trade-off:* Flash is slightly less capable at complex logical reasoning than larger models (like GPT-4o or Claude 3.5 Sonnet), but it was chosen explicitly to comfortably beat the 5-second processing requirement.
* **Data Structuring:** `Pydantic`
  * *Justification:* Prevents application crashes by forcing the LLM to return data matching a strict backend schema.

---

## 🔒 Security & Assumptions

* **Ephemeral State Management:** To comply with federal IT security guidelines regarding PII and document retention (noted by IT Admin Marcus), this application does not connect to a database. Images and text data are processed in system memory and immediately discarded when the session ends. 
* **Cloud Deployment:** The prototype is hosted externally to bypass internal TTB network firewalls that previously blocked outbound ML endpoint traffic.
* **Assumption:** We assume agents have access to digital image files (JPG/PNG) of the labels submitted in the COLA application.

---

## 💻 Local Setup & Run Instructions

If you wish to run this application locally on your machine rather than using the deployed web version, follow these steps:

**1. Clone the repository:**
```bash
git clone [https://github.com/your-username/ttb-label-verification-app.git](https://github.com/your-username/ttb-label-verification-app.git)
cd ttb-label-verification-app

---

## 🚀 Next Steps for Production Deployment

While this application was built as a standalone Minimum Viable Product (MVP) to solve the immediate bottleneck in the labeling division, scaling it for enterprise-wide deployment will involve the following architectural enhancements:

*   **Codebase Modularity:** Refactoring the single-file Streamlit structure into discrete modules (e.g., `ui_components.py`, `ai_processing.py`, and `data_schemas.py`). This will allow multiple engineers to work on the app simultaneously without merge conflicts.
*   **TTB System Integration:** Transitioning the "Expected Application Data" manual input fields into automated API calls that pull directly from the legacy .NET COLA database via secure webhooks.
*   **Audit Logging:** Implementing a secure, internal TTB database to store the AI's JSON outputs and decision logs for historical compliance tracking, without ever storing the proprietary label images.
*   **Role-Based Access Control (RBAC):** Adding federal Single Sign-On (SSO) to track which agents are verifying which batches of labels.
