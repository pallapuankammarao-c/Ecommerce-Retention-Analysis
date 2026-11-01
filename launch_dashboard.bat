@echo off
echo Starting Olist E-Commerce Retention & Churn Dashboard...
start "" http://localhost:8501
streamlit run "%~dp0dashboard\app.py" --server.port 8501
pause

