# Targeted Transformation Dashboard

A Streamlit-based dashboard for analyzing and tracking the transformation status of a company.
The tool enables users to assess maturity levels, analyze performance gaps, and prioritize improvement measures based on data-driven insights.

---

## 🔧 Features

- Maturity Assessment Visualization – Plot current state for different dimensions
- Gap Analysis – Identify the largest performance gaps at a glance
- Measure Prioritization – Rank improvement actions based on maturity gap and utility
- Upload / Load Assessment Data (Excel template)
- Download Reports

---

## 🚀 How to Run

### Option 1: Run Locally

    git clone https://github.com/simongrafKIT/streamlit-dashboard
    cd streamlit-dashboard
    pip install -r requirements.txt
    streamlit run dashboard/app.py

Requires Python 3.9+

### Option 2: Use Online Version

    https://targeted-transformation.streamlit.app/

---

## 📁 Project Structure

    streamlit-dashboard/
    ├── dashboard/
    │   ├── __init__.py         
    │   ├── alignment.py        # Prioritization of measures (phase 3)
    │   ├── app.py              # Main Streamlit application
    │   ├── constants.py        # Global constants
    │   ├── data_io.py          # Read Excel file
    │   ├── plots.py            # Main plots (phase 1 +2)
    │   ├── tab_questions.py    # Display all assessment questions
    │   ├── ui.py               # Streamlit UI
    │   └── utils.py            # Aux. function
    ├── requirements.txt
    └── README.md

