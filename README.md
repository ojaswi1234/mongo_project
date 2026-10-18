# MediTrack: Smart Hospital Management System with MongoDB & AI Vector Search

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0%2B%20%2F%20Atlas-green.svg)](https://www.mongodb.com/)
[![PyMongo](https://img.shields.io/badge/PyMongo-4.6%2B-darkgreen.svg)](https://pymongo.readthedocs.io/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg)](https://palletsprojects.com/p/flask/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS-38bdf8.svg)](https://tailwindcss.com/)

A full-stack, enterprise-grade healthcare management application demonstrating **MongoDB document modeling**, **`$jsonSchema` validation**, **PyMongo CRUD operations**, **complex multi-stage aggregation pipelines**, and **MongoDB Vector Search** for AI-assisted clinical diagnosis.

Designed for final-year Computer Science & Engineering academic submission (**Course Outcomes: CO4, CO5, CO6**).

---

## 🌟 Key Features

1. **Hybrid NoSQL Document Architecture**:
   - **Embedded (1-to-Few)**: Patient vitals history, prescriptions, and billing ledger embedded in a single BSON document for zero-join, high-locality reads.
   - **Referenced (1-to-Many)**: Physicians and departments referenced via ID to avoid data redundancy and update anomalies.
2. **Database-Level Schema Validation (`$jsonSchema`)**:
   - Enforced directly by the MongoDB engine. Validates regex ID patterns (`^PAT-[0-9]{4}$`), age bounds (0–125), enums, and nested structures.
3. **Atomic MongoDB Updates**:
   - `$push` for continuous time-stamped vitals telemetry.
   - `$inc` for atomic mathematical increments on patient billing.
   - Soft deletion (HIPAA compliance) for permanent audit trails.
4. **5 Advanced Aggregation Pipelines**:
   - **Pipeline 1**: Department-wise patient volume, average age, and billing revenue (`$match`, `$group`, `$sort`).
   - **Pipeline 2**: Doctor workload & revenue attribution (`$lookup` cross-collection join).
   - **Pipeline 3**: Clinical critical vitals anomaly detection (`$unwind`, `$match`).
   - **Pipeline 4**: Pharmacy prescription frequency analysis (`$unwind`, `$group`).
   - **Pipeline 5**: Multi-faceted executive dashboard (`$facet` parallel multi-pipeline execution).
5. **MongoDB as a Vector Database & AI Clinical Assistant**:
   - Stores 64-dimensional dense vector embeddings directly in MongoDB documents (`clinical_embedding`).
   - Natural language symptom search using vector cosine similarity.
   - Generates AI diagnostic summaries, department routing, and drug recommendations.
   - Synthesizes the exact MongoDB Atlas `$vectorSearch` aggregation syntax.
6. **Modern Web Interface**:
   - Interactive charts with Chart.js (vitals telemetry curves, revenue breakdown).
   - Responsive UI powered by Tailwind CSS (via CDN).
   - Auto-fallback to In-Memory Mock mode (`mongomock`) so the project is **100% runnable anywhere offline** during presentations.

---

## 📁 Project Structure

```
SmartHospital_MongoDB/
│
├── app.py                     # Flask Web Application entry point (localhost:5000)
├── requirements.txt           # Python dependencies (pymongo, flask, rich, etc.)
├── .env.example               # Environment configuration template
├── output_demonstration.txt   # Complete verified execution log of all operations
│
├── config/
│   ├── __init__.py
│   └── database.py            # Connection manager (Local MongoDB, Atlas, or Mock fallback)
│
├── database/
│   ├── __init__.py
│   ├── schema_validation.py   # Definition of $jsonSchema rules and indexes
│   └── seed_data.py           # Realistic seed dataset generator with pre-computed vectors
│
├── models/
│   ├── __init__.py
│   ├── patient.py             # Patient document structure & helpers
│   └── doctor.py              # Doctor document structure & helpers
│
├── operations/
│   ├── __init__.py
│   ├── crud.py                # CRUD queries (Create, Read with $elemMatch, Update with $push/$inc, Delete)
│   └── aggregations.py        # 5 multi-stage Aggregation Pipelines
│
├── ai/
│   ├── __init__.py
│   └── vector_engine.py       # MongoDB Vector Search engine & AI diagnostic assistant
│
├── scripts/
│   ├── mongo_queries.js       # Standalone raw MongoDB Shell / Compass query script
│   └── run_demo.py            # Automated terminal demonstration and test runner
│
├── templates/                 # Modern web templates (Tailwind CSS + Chart.js)
│   ├── base.html              # Base layout with navbar and system status badge
│   ├── index.html             # Executive hospital dashboard
│   ├── patients.html          # Searchable patient directory
│   ├── patient_detail.html    # Patient chart, vitals trend graph, and modals
│   ├── patient_form.html      # Admission form demonstrating $jsonSchema validation
│   ├── analytics.html         # Aggregation analytics with interactive charts
│   └── ai_search.html         # AI Vector Search & Clinical Assistant
│
└── docs/                      # Course deliverables & presentation materials
    ├── PROJECT_REPORT.md      # Formal academic project report (ready for submission)
    ├── VIVA_PREPARATION.md    # Top 15 Viva Voce Q&A and technical defense
    └── PRESENTATION_SLIDES.md # Slide-by-slide presentation deck script
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Dependencies
Ensure Python 3.10+ is installed. Install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure MongoDB Connection (Optional)
The project works out-of-the-box!
- **Default / Offline Mode**: If no MongoDB server is running, the app automatically activates the built-in **In-Memory Mock Mode** so you can run the entire system offline during exams or presentations.
- **Local MongoDB**: Ensure `mongod` service is running on `mongodb://localhost:27017/`.
- **MongoDB Atlas**: Open `.env` and set your Atlas URI:
  ```env
  MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/
  DATABASE_NAME=SmartHospitalDB
  ENABLE_OFFLINE_MOCK_FALLBACK=True
  ```

### 3. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to:
👉 **`http://localhost:5000`**

---

## 🖥️ Web Portal Navigation

| URL Route | Feature | MongoDB Operations Highlighted |
|---|---|---|
| `/` | **Dashboard** | KPI counts, bed occupancy, recent admissions |
| `/patients` | **Patient Directory** | Filter by department/status, search by keyword |
| `/patient/<id>` | **Patient Profile** | Vitals trend chart, `$push` vitals modal, `$inc` billing update |
| `/patients/new` | **Admit Patient** | Real-time MongoDB `$jsonSchema` validation test |
| `/analytics` | **Aggregation Hub** | Visual charts for Pipelines 1 to 5 (`$group`, `$lookup`, `$unwind`, `$facet`) |
| `/ai-search` | **AI Vector Search** | Natural language symptom search via 64-dim vector similarity |

---

## ⚡ Running Standalone Demonstration & MongoDB Scripts

### 1. Automated Execution Proof
To generate a complete, formatted test report showing all operations:
```bash
python scripts/run_demo.py
```
This executes all CRUD queries, schema rejection tests, and aggregation pipelines, saving output directly to `output_demonstration.txt`.

### 2. Standalone MongoDB Shell (`mongosh`) / Compass
If the evaluator asks to see raw MongoDB queries:
1. Open MongoDB Compass or `mongosh`.
2. Open `scripts/mongo_queries.js`.
3. Copy-paste the commands directly into the MongoDB shell or Compass Aggregation Pipeline tab.

---

## 🎓 Academic Viva Cheat Sheet

- **Why Embed Vitals?** High read locality, bounded size (<100 readings per stay), and atomic single-document modifications via `$push`.
- **Why Reference Doctors?** Unbounded growth (one doctor treats thousands of patients) and avoiding update anomalies.
- **Why MongoDB as a Vector Database?** Eliminates synchronization drift between separate databases (e.g. MongoDB + Pinecone). Operational records and vector embeddings live inside the same document.
- **What is `$elemMatch`?** Ensures multiple filter conditions match against the **same** array element rather than different elements across the array.

For the complete 15-question viva guide, see [`docs/VIVA_PREPARATION.md`](docs/VIVA_PREPARATION.md).
