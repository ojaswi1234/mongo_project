# MediTrack: Smart Hospital Management System with MongoDB & AI Vector Search

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0%2B%20%2F%20Atlas-green.svg)](https://www.mongodb.com/)
[![PyMongo](https://img.shields.io/badge/PyMongo-4.6%2B-darkgreen.svg)](https://pymongo.readthedocs.io/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg)](https://palletsprojects.com/p/flask/)
[![Live App](https://img.shields.io/badge/Render-Live%20Demo-success?logo=render)](https://mongo-project-nwjl.onrender.com)

> **Student Name**: Ojaswi Bhardwaj  
> **Registration No.**: 12319444 | **Roll No.**: 37  
> **Subject**: CSE494 | **Section**: K3P23SD  
> **GitHub Repository**: [https://github.com/ojaswi1234/mongo_project.git](https://github.com/ojaswi1234/mongo_project.git)  
> **Live Deployment URL**: [https://mongo-project-nwjl.onrender.com](https://mongo-project-nwjl.onrender.com)  

A clean, presentation-ready full-stack healthcare web application demonstrating **MongoDB document modeling**, **`$jsonSchema` validation**, **PyMongo CRUD operations**, **multi-stage aggregation pipelines**, and **MongoDB Vector Search** for AI-assisted clinical diagnosis.

Designed for final-year Computer Science & Engineering academic submission (**Course Outcomes: CO4, CO5, CO6 — 30 Marks**).

---

## 📁 Simple & Clean Project Structure

```
SmartHospital_MongoDB/
│
├── app.py                     # ⭐ Single consolidated app with 8 clean, numbered sections
├── SmartHospital_Project_Report.pdf  # ⭐ Formal Academic Project Report (PDF)
├── SmartHospital_Presentation.pdf    # ⭐ 10-Slide Landscape Presentation Deck (PDF)
├── requirements.txt           # Python dependencies (pymongo, flask, reportlab, etc.)
├── Procfile                   # Cloud deployment command (web: gunicorn app:app)
├── render.yaml                # Render auto-deployment configuration
├── output_demonstration.txt   # Complete verified execution log of all operations
│
├── scripts/
│   ├── run_demo.py                  # Terminal demo script running all operations
│   ├── generate_report_pdf.py       # Standalone compiler for Project Report PDF
│   ├── generate_presentation_pdf.py # Standalone compiler for Presentation PDF
│   └── mongo_queries.js             # Raw MongoDB Shell / Compass query script
│
├── templates/                 # Clean web templates (Tailwind CSS + Chart.js)
│   ├── base.html              # Base layout with navbar and system status badge
│   ├── index.html             # Executive hospital dashboard
│   ├── patients.html          # Searchable patient directory
│   ├── patient_detail.html    # Patient chart, vitals trend graph, and modals
│   ├── patient_form.html      # Admission form with $jsonSchema validation test
│   ├── analytics.html         # Aggregation analytics with interactive charts
│   └── ai_search.html         # AI Vector Search & Clinical Assistant
│
└── docs/                      # Course deliverables & presentation materials
    ├── SmartHospital_Project_Report.pdf # PDF Project Report
    ├── SmartHospital_Presentation.pdf   # PDF Presentation Slide Deck
    ├── PROJECT_REPORT.md      # Formal academic project report (Markdown source)
    ├── VIVA_PREPARATION.md    # Top 15 Viva Voce Q&A and technical defense
    └── PRESENTATION_SLIDES.md # Slide-by-slide presentation deck script
```

---

## 🎤 How to Present This Project in 3 Minutes (Viva Walkthrough)

When the evaluator asks you to present your project, follow this 4-step sequence:

### Step 1: Open the Code (`app.py`)
Show that the code is divided into clean, numbered sections matching the syllabus:
1. **Section 1 (Line 30)**: Database connection with automatic offline fallback (`mongomock`), guaranteeing zero crashes during viva.
2. **Section 2 (Line 50)**: Engine-level schema validation (`$jsonSchema`) enforcing patient ID regex (`^PAT-[0-9]{4}$`), age bounds (0–125), and enum boundaries.
3. **Section 3 (Line 100)**: 10-dimensional clinical symptom vector model (`SYMPTOM_DIMENSIONS`) and cosine similarity function.
4. **Section 4 (Line 160)**: Realistic starter hospital data seeded with pre-computed vectors.
5. **Section 5 (Line 280)**: CRUD operations (`add_patient`, `$push` for vitals, `$inc` for billing, `$set` for soft deletion).
6. **Section 6 (Line 360)**: 4 multi-stage Aggregation pipelines (`$match`, `$group`, `$unwind`, `$facet`).
7. **Section 7 (Line 450)**: Flask routes rendering the web views.

### Step 2: Run the Terminal Demo
Open your terminal and run:
```bash
python scripts/run_demo.py
```
Explain: *"This script tests every single rubric requirement—schema rejection, CRUD operations, aggregation pipelines, and AI vector similarity—displaying the results in clean ASCII tables."*

### Step 3: Demonstrate the Live Web App
Open `http://localhost:5000` (or the Live URL: `https://mongo-project-nwjl.onrender.com`):
1. **Dashboard (`/`)**: Show executive KPIs and bed occupancy meters.
2. **Patients Directory (`/patients`)**: Filter by Department ("Cardiology") or Status ("Admitted").
3. **Patient Chart (`/patient/PAT-1001`)**:
   - Show the interactive Chart.js vital curves (Heart Rate, Blood Pressure, SpO2).
   - Click **"Record New Vitals"** &rarr; Demonstrates atomic `$push` update.
   - Click **"Update Billing"** &rarr; Demonstrates atomic `$inc` update.
4. **Admission Form (`/patients/new`)**:
   - Click **"Fill Invalid Sample"** and click Submit &rarr; Demonstrates MongoDB `$jsonSchema` blocking malformed entries with a red error badge!
5. **Aggregation Hub (`/analytics`)**:
   - Show the 4 pipelines: Department Revenue (`$group`), Critical Vitals Triage (`$unwind`), Pharmacy Demand (`$group`), and Executive Facets (`$facet`).
   - Click **"View Pipeline Query"** to show the raw MongoDB code on screen.
6. **AI Vector Search (`/ai-search`)**:
   - Click sample query *"acute chest pain and elevated palpitations"*.
   - Show that it returns **Ethan Wright (PAT-1005)** with 100% match and **Robert Miller (PAT-1001)** with 70.7% match, recommending Cardiology drugs based on historical charts.

### Step 4: Show the Generated Deliverable PDFs
Point to the compiled PDFs:
- [`SmartHospital_Project_Report.pdf`](SmartHospital_Project_Report.pdf)
- [`SmartHospital_Presentation.pdf`](SmartHospital_Presentation.pdf)

---

## ⚡ Quick Start Guide

### 1. Prerequisites & Dependencies
Ensure Python 3.10+ is installed. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python app.py
```
Open **`http://localhost:5000`** in your browser.

> **Offline Safe**: If local MongoDB is not running, the app automatically switches to **In-Memory Mock Mode**, so you can present without needing an active internet connection or local database daemon.

---

## 🎓 Academic Viva Cheat Sheet (Top 4 Questions)

1. **Why use an embedded document for vitals instead of a separate table?**
   - *Answer*: High read locality (vitals are always viewed with the patient chart), bounded size (<50 readings per stay, <<16MB BSON limit), and atomic updates using `$push` without multi-table JOINs.
2. **Why reference doctors instead of embedding?**
   - *Answer*: 1-to-many unbounded relationship. One doctor treats thousands of patients over years. Referencing avoids duplicate doctor records and update anomalies.
3. **How does MongoDB act as an AI Vector Database?**
   - *Answer*: We store 10-dimensional clinical symptom vectors directly in the patient document (`clinical_embedding`). We compute cosine similarity ($Q \cdot D$) to find similar cases. In MongoDB Atlas, this maps natively to the `$vectorSearch` aggregation stage with HNSW indexing.
4. **What is `$elemMatch`?**
   - *Answer*: It ensures that multiple conditions match on the **exact same** array element (e.g., heart rate &ge; 100 AND SpO2 &le; 95 on the same reading), preventing false positive cross-element matches.
