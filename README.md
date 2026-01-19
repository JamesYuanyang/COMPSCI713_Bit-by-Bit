# Human Ethics Advisor (Bit By Bit)

An AI-powered assistant that helps University of Auckland researchers review and strengthen human ethics applications before submission. The app connects to an IBM Watsonx.ai deployment (RAG-backed) and provides feedback based on key policy sources such as NEAC, HRC, UAHPEC, AHREC, Te Ara Tika, and institutional privacy and IT policies.

## What This App Does
- Chat-based Q&A for ethics guidance and application review
- Document analysis for PDF and DOCX uploads
- Local storage of API configuration for quick reuse

## Requirements
- Python 3.9+ (recommended)
- An active IBM Watsonx.ai deployment (public URL)
- IBM IAM API key

## Install
```bash
pip install streamlit requests pymupdf python-docx
```

## Run
```bash
streamlit run streamlit-chatwithdoc.py
```

## Usage
1. Open the app in your browser.
2. Expand "Configure API Key and Deployment URL" and save your credentials.
3. Ask questions in the chat or upload a PDF/DOCX and click "Analyze This Document".

## Notes on the Deployment
- The UI expects a Watsonx.ai deployment configured for ethics review and retrieval over the relevant guidelines.
- Credentials are stored locally in `api_data.db`. Delete or ignore this file if you do not want to persist secrets.

## Evaluation Targets (Project Plan)
- Model QA metrics: >70% on answer correctness, faithfulness, and contextual accuracy.
- Ethics rubric: >85% average on compliance/risk identification, policy traceability, actionability, and structure/clarity.
- End-to-end validation with three example application cases.

## Team
- Qinxue Feng
- Katie Law
- Jiajun Xiao 
- Yizheng Xing
- Nanyuanyang Zhang
