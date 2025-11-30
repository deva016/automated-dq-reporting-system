# 📊 Automated Data Quality & Reporting System

A lightweight, production-ready **Data Quality (DQ) Engine** with a **Streamlit UI**.
Upload any dataset → get profiling, missing-value checks, duplicate detection, schema inference, anomaly flags, scoring, and downloadable reports.

This project is fully deployable **for FREE** on:
✅ Streamlit Community Cloud
or
✅ HuggingFace Spaces (Streamlit)

---

## 🚀 Features

* **Upload CSV / Excel / Parquet**
* **Automatic Dataset Profiling**

  * Missing values
  * Unique counts
  * Type inference
  * Basic statistics
* **Data Quality Checks**

  * Completeness check
  * Duplicate row detection
  * Schema mismatch detection
  * Numeric outlier detection
* **DQ Score (0–100)**
* **Downloadable Violations Report (CSV)**
* **Optional PDF Report Generation**

---

## 🗂️ Project Structure

```bash
automated-dq-reporting-system/
│
├── app/
│   └── app.py
│
├── dq_engine/
│   ├── __init__.py
│   ├── profiler.py
│   ├── checks.py
│   ├── anomaly.py
│   ├── repairs.py
│   ├── schema_infer.py
│   └── scoring.py
│
├── utils/
│   ├── __init__.py
│   ├── io.py
│   └── validators.py
│
├── reports/
│   ├── __init__.py
│   ├── export.py
│   └── pdf_report.py
│
├── samples/
│   └── sample.csv
│
├── tests/
│   └── test_checks.py
│
├── requirements.txt
└── README.md
```

---

## 🛠️ Local Setup Instructions (Windows)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/deva016/automated-dq-reporting-system.git
cd automated-dq-reporting-system
```

### 2️⃣ Create & Activate Virtual Environment

#### **Using PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **Using CMD**

```cmd
.\.venv\Scripts\activate.bat
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run Streamlit App

```bash
streamlit run app/app.py
```

Open in browser:

```
http://localhost:8501
```

---

## 🧪 Run Tests

```bash
pytest -q
```

---

## 🚀 Deploy to Streamlit Cloud (FREE)

1. Push repo to GitHub
2. Visit: [https://share.streamlit.io](https://share.streamlit.io)
3. Click **New App**
4. Select:

   * **Repo:** `deva016/automated-dq-reporting-system`
   * **Branch:** `main`
   * **App Path:** `app/app.py`
5. Click **Deploy**

Streamlit auto-installs packages from `requirements.txt`.

---

## 🚀 Deploy to Hugging Face Spaces (FREE Alternative)

1. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Create **New Space** → Type: `Streamlit`
3. Connect your GitHub repo
4. HuggingFace automatically builds the app from `requirements.txt`

---

## 📦 requirements.txt (Minimum)

```txt
streamlit
pandas
numpy
scikit-learn
rapidfuzz
openpyxl
pyarrow
reportlab
python-dateutil
```

---

## 📌 Notes

* Ensure `__init__.py` exists in all package folders.
* PDF reports require **reportlab**.
* For scanned document processing → install `pytesseract` + Tesseract OCR.

---

## ❤️ Contribution

Pull Requests are welcome!
You can help extend the project with:

* Additional anomaly detection
* Custom schema validation rules
* Automated data repairs
* Data quality dashboards

