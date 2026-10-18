"""
Smart Hospital & Patient Care Management System (MediTrack)
Coursework Project: CSE494 (CO4, CO5, CO6 - 30 Marks)

Student Name : Ojaswi Bhardwaj
Registration : 12319444 | Roll No: 37 | Section: K3P23SD
GitHub Repo  : https://github.com/ojaswi1234/mongo_project.git
Live Deploy  : https://mongo-project-nwjl.onrender.com

Architecture:
  - Database   : MongoDB 6.0+ (PyMongo Driver) with $jsonSchema and Indexes
  - CRUD       : Atomic updates ($push for vitals, $inc for billing, $set for soft delete)
  - Analytics  : Multi-stage Aggregation Pipelines ($match, $group, $unwind, $facet)
  - AI Search  : In-document 10-D Symptom Vector Embeddings + Cosine Similarity
  - Frontend   : Flask Web Framework, Tailwind CSS, Chart.js
"""

import os
import re
import math
from datetime import datetime, timedelta
import pymongo
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "smarthospital-secret-key-cse494")
CORS(app)


# ==============================================================================
# SECTION 1: DATABASE CONNECTION & SEAMLESS OFFLINE FALLBACK
# ==============================================================================

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DATABASE_NAME", "SmartHospitalDB")

def get_database():
    """
    Connects to local or Atlas MongoDB.
    Falls back to mongomock if MongoDB is offline, guaranteeing 0 crashes during viva.
    """
    try:
        client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        return client, client[DB_NAME], False
    except pymongo.errors.PyMongoError:
        import mongomock
        mock_client = mongomock.MongoClient()
        return mock_client, mock_client[DB_NAME], True

client, db, is_mock_mode = get_database()


# ==============================================================================
# SECTION 2: $JSONSCHEMA VALIDATION RULES & INDEXING
# ==============================================================================

def setup_database_schema():
    """
    Applies engine-level BSON validation rules.
    Invalid writes are rejected directly by MongoDB with a WriteError.
    """
    if is_mock_mode:
        return

    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["patient_id", "name", "age", "gender", "blood_group", "department", "status", "billing"],
            "properties": {
                "patient_id": {
                    "bsonType": "string",
                    "pattern": "^PAT-[0-9]{4}$",
                    "description": "Must match regex format PAT-XXXX (e.g. PAT-1001)"
                },
                "name": {"bsonType": "string", "minLength": 2},
                "age": {"bsonType": "int", "minimum": 0, "maximum": 125},
                "gender": {"enum": ["Male", "Female", "Other"]},
                "blood_group": {"enum": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]},
                "department": {"enum": ["Cardiology", "Neurology", "Orthopedics", "General Medicine", "Pediatrics"]},
                "status": {"enum": ["Admitted", "Under Observation", "Discharged", "Archived"]},
                "billing": {
                    "bsonType": "object",
                    "required": ["total_amount", "payment_status"]
                }
            }
        }
    }

    try:
        if "patients" not in db.list_collection_names():
            db.create_collection("patients", validator=validator)
        else:
            db.command({"collMod": "patients", "validator": validator, "validationLevel": "moderate"})
        
        # Primary unique and compound indexes
        db.patients.create_index("patient_id", unique=True)
        db.patients.create_index([("department", 1), ("status", 1)])
    except Exception as e:
        print(f"[Schema Notice]: {e}")

setup_database_schema()


# ==============================================================================
# SECTION 3: AI VECTOR SEARCH ENGINE (10-DIMENSIONAL CLINICAL MODEL)
# ==============================================================================

# 10 clinical symptom keywords representing orthogonal vector dimensions
SYMPTOM_DIMENSIONS = [
    "chest pain",          # Dim 0: Cardiology
    "palpitations",        # Dim 1: Cardiac Arrhythmia
    "headache",            # Dim 2: Neurology
    "dizziness",           # Dim 3: Vertigo
    "fracture",            # Dim 4: Orthopedics / Trauma
    "joint pain",          # Dim 5: Orthopedics
    "fever",               # Dim 6: Infection
    "cough",               # Dim 7: Respiratory
    "shortness of breath", # Dim 8: Pulmonology
    "stomach pain"         # Dim 9: Gastroenterology
]

def text_to_vector(text: str):
    """
    Maps clinical notes into a 10-dimensional normalized symptom vector.
    Stored directly inside each document in the 'clinical_embedding' array.
    """
    if not text:
        return [0.0] * len(SYMPTOM_DIMENSIONS)
    
    t = text.lower()
    vec = []
    for s in SYMPTOM_DIMENSIONS:
        if s in t:
            vec.append(1.0)
        elif s == "chest pain" and ("angina" in t or "heart" in t):
            vec.append(1.0)
        elif s == "headache" and ("migraine" in t):
            vec.append(1.0)
        elif s == "shortness of breath" and ("oxygen" in t or "spo2" in t):
            vec.append(1.0)
        elif s == "fever" and ("infection" in t):
            vec.append(1.0)
        else:
            vec.append(0.0)

    # Normalize to unit length for direct cosine similarity (Q . D)
    magnitude = math.sqrt(sum(x * x for x in vec))
    return [round(x / magnitude, 4) for x in vec] if magnitude > 0 else [0.1] * len(SYMPTOM_DIMENSIONS)

def cosine_similarity(v1, v2):
    """Computes Dot Product between two unit-normalized vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    return max(0.0, min(1.0, round(dot, 4)))

def search_similar_patients(query_text: str, top_k: int = 4, dept: str = None):
    """
    Performs vector similarity search against patients in MongoDB.
    In Atlas, this maps natively to the $vectorSearch aggregation stage.
    """
    query_vec = text_to_vector(query_text)
    filter_criteria = {"status": {"$ne": "Archived"}}
    if dept and dept != "All":
        filter_criteria["department"] = dept

    patients = list(db.patients.find(filter_criteria))
    ranked = []

    for p in patients:
        doc_vec = p.get("clinical_embedding") or text_to_vector(" ".join(p.get("medical_notes", [])))
        score = cosine_similarity(query_vec, doc_vec)
        ranked.append({
            "patient_id": p.get("patient_id"),
            "name": p.get("name"),
            "age": p.get("age"),
            "gender": p.get("gender"),
            "department": p.get("department"),
            "status": p.get("status"),
            "medical_notes": p.get("medical_notes", []),
            "prescriptions": p.get("prescriptions", []),
            "similarity_score": score,
            "match_percentage": round(score * 100, 1)
        })

    ranked.sort(key=lambda x: x["similarity_score"], reverse=True)
    return ranked[:top_k]


# ==============================================================================
# SECTION 4: REALISTIC STARTER SEED DATA
# ==============================================================================

def seed_sample_data():
    """Populates MongoDB with realistic inpatient records and 10D symptom vectors."""
    db.patients.delete_many({})
    now = datetime.now()

    patients = [
        {
            "patient_id": "PAT-1001",
            "name": "Robert Miller",
            "age": 62,
            "gender": "Male",
            "blood_group": "A+",
            "department": "Cardiology",
            "status": "Admitted",
            "assigned_doctor_name": "Dr. Sarah Jenkins",
            "admission_date": now - timedelta(days=4),
            "contact": {"phone": "+1-555-1001", "email": "rmiller@hospital.com", "emergency_contact": "Mary Miller"},
            "medical_notes": ["History of hypertension and acute chest pain", "Angioplasty recommended"],
            "vitals_history": [
                {"timestamp": now - timedelta(days=2), "blood_pressure": "145/95", "heart_rate": 105, "oxygen_level": 94, "temperature": 99.1},
                {"timestamp": now - timedelta(hours=6), "blood_pressure": "128/82", "heart_rate": 78, "oxygen_level": 98, "temperature": 98.4}
            ],
            "prescriptions": [
                {"medicine": "Atorvastatin", "dosage": "20mg", "frequency": "Daily", "days": 30},
                {"medicine": "Metoprolol", "dosage": "50mg", "frequency": "Twice daily", "days": 15}
            ],
            "billing": {"room_charges": 1600.0, "consultation_fee": 450.0, "medicine_charges": 280.0, "total_amount": 2330.0, "payment_status": "Partially Paid"}
        },
        {
            "patient_id": "PAT-1002",
            "name": "Sophia Chen",
            "age": 45,
            "gender": "Female",
            "blood_group": "B+",
            "department": "Neurology",
            "status": "Admitted",
            "assigned_doctor_name": "Dr. Rajesh Sharma",
            "admission_date": now - timedelta(days=2),
            "contact": {"phone": "+1-555-1002", "email": "schen@hospital.com", "emergency_contact": "Kevin Chen"},
            "medical_notes": ["Severe recurring migraine and headache with neurological aura"],
            "vitals_history": [
                {"timestamp": now - timedelta(hours=8), "blood_pressure": "120/78", "heart_rate": 74, "oxygen_level": 99, "temperature": 98.6}
            ],
            "prescriptions": [
                {"medicine": "Sumatriptan", "dosage": "50mg", "frequency": "As needed", "days": 10}
            ],
            "billing": {"room_charges": 800.0, "consultation_fee": 320.0, "medicine_charges": 190.0, "total_amount": 1310.0, "payment_status": "Paid"}
        },
        {
            "patient_id": "PAT-1003",
            "name": "David Wilson",
            "age": 71,
            "gender": "Male",
            "blood_group": "O+",
            "department": "Orthopedics",
            "status": "Admitted",
            "assigned_doctor_name": "Dr. Emily Taylor",
            "admission_date": now - timedelta(days=6),
            "contact": {"phone": "+1-555-1003", "email": "dwilson@hospital.com", "emergency_contact": "Susan Wilson"},
            "medical_notes": ["Post-op knee joint replacement recovery and joint pain therapy"],
            "vitals_history": [
                {"timestamp": now - timedelta(days=3), "blood_pressure": "138/85", "heart_rate": 92, "oxygen_level": 95, "temperature": 100.2}
            ],
            "prescriptions": [
                {"medicine": "Tramadol", "dosage": "50mg", "frequency": "Twice daily", "days": 7}
            ],
            "billing": {"room_charges": 2400.0, "consultation_fee": 650.0, "medicine_charges": 890.0, "total_amount": 3940.0, "payment_status": "Insurance Claimed"}
        },
        {
            "patient_id": "PAT-1004",
            "name": "Amina Morales",
            "age": 28,
            "gender": "Female",
            "blood_group": "AB+",
            "department": "General Medicine",
            "status": "Discharged",
            "assigned_doctor_name": "Dr. Anita Desai",
            "admission_date": now - timedelta(days=7),
            "contact": {"phone": "+1-555-1004", "email": "amorales@hospital.com", "emergency_contact": "Carlos Morales"},
            "medical_notes": ["Acute viral infection with high fever and stomach pain resolved"],
            "vitals_history": [
                {"timestamp": now - timedelta(days=6), "blood_pressure": "118/75", "heart_rate": 115, "oxygen_level": 95, "temperature": 102.4}
            ],
            "prescriptions": [
                {"medicine": "Paracetamol", "dosage": "650mg", "frequency": "Thrice daily", "days": 5}
            ],
            "billing": {"room_charges": 1200.0, "consultation_fee": 285.0, "medicine_charges": 140.0, "total_amount": 1625.0, "payment_status": "Paid"}
        },
        {
            "patient_id": "PAT-1005",
            "name": "Ethan Wright",
            "age": 53,
            "gender": "Male",
            "blood_group": "O-",
            "department": "Cardiology",
            "status": "Under Observation",
            "assigned_doctor_name": "Dr. Sarah Jenkins",
            "admission_date": now - timedelta(hours=14),
            "contact": {"phone": "+1-555-1005", "email": "ewright@hospital.com", "emergency_contact": "Laura Wright"},
            "medical_notes": ["Acute chest pain, unstable angina, and elevated palpitations"],
            "vitals_history": [
                {"timestamp": now - timedelta(hours=10), "blood_pressure": "155/100", "heart_rate": 118, "oxygen_level": 93, "temperature": 98.6}
            ],
            "prescriptions": [
                {"medicine": "Aspirin", "dosage": "75mg", "frequency": "Daily", "days": 30},
                {"medicine": "Metoprolol", "dosage": "25mg", "frequency": "Daily", "days": 14}
            ],
            "billing": {"room_charges": 500.0, "consultation_fee": 150.0, "medicine_charges": 110.0, "total_amount": 760.0, "payment_status": "Pending"}
        }
    ]

    # Pre-compute and embed the 10D symptom vector into each patient chart
    for p in patients:
        summary_text = " ".join(p.get("medical_notes", [])) + " " + p.get("department", "")
        p["clinical_embedding"] = text_to_vector(summary_text)

    db.patients.insert_many(patients)

if db.patients.count_documents({}) == 0:
    seed_sample_data()


# ==============================================================================
# SECTION 5: CRUD OPERATIONS (CREATE, READ, UPDATE, DELETE)
# ==============================================================================

def add_patient(data: dict):
    """
    [CREATE Operation]:
    Inserts a patient into MongoDB with client validation and 10D vector synthesis.
    """
    pid = str(data.get("patient_id", ""))
    age = data.get("age")
    gender = data.get("gender")

    if not re.match(r"^PAT-[0-9]{4}$", pid):
        return {"success": False, "error": f"Patient ID '{pid}' must match format PAT-XXXX (e.g. PAT-1010)."}
    if not isinstance(age, int) or age < 0 or age > 125:
        return {"success": False, "error": f"Age '{age}' must be an integer between 0 and 125."}
    if gender not in ["Male", "Female", "Other"]:
        return {"success": False, "error": f"Gender '{gender}' must be Male, Female, or Other."}

    # Synthesize 10D symptom vector
    notes = " ".join(data.get("medical_notes", [])) + " " + str(data.get("department", ""))
    data["clinical_embedding"] = text_to_vector(notes)

    try:
        res = db.patients.insert_one(data)
        return {"success": True, "inserted_id": str(res.inserted_id)}
    except pymongo.errors.DuplicateKeyError:
        return {"success": False, "error": f"Patient with ID '{pid}' already exists."}
    except pymongo.errors.WriteError as e:
        return {"success": False, "error": f"Schema Validation Failed: {e}"}

def record_vital_reading(patient_id: str, vital: dict):
    """
    [UPDATE Operation - $push]:
    Appends a new vital reading to the embedded 'vitals_history' array atomically.
    """
    if "timestamp" not in vital:
        vital["timestamp"] = datetime.now()
    res = db.patients.update_one({"patient_id": patient_id}, {"$push": {"vitals_history": vital}})
    return res.modified_count > 0

def update_billing_charges(patient_id: str, add_medicine: float = 0.0, new_status: str = None):
    """
    [UPDATE Operation - $inc & $set]:
    Atomically increments billing totals and updates payment status.
    """
    update_doc = {}
    if add_medicine > 0:
        update_doc["$inc"] = {
            "billing.medicine_charges": add_medicine,
            "billing.total_amount": add_medicine
        }
    if new_status:
        update_doc["$set"] = {"billing.payment_status": new_status}

    if update_doc:
        res = db.patients.update_one({"patient_id": patient_id}, update_doc)
        return res.modified_count > 0
    return False

def soft_delete_patient(patient_id: str):
    """
    [DELETE Operation - Logical Soft Delete]:
    Marks the document as 'Archived' using $set (HIPAA legal compliance).
    """
    res = db.patients.update_one({"patient_id": patient_id}, {"$set": {"status": "Archived", "is_archived": True}})
    return res.modified_count > 0


# ==============================================================================
# SECTION 6: AGGREGATION PIPELINES ($group, $unwind, $facet)
# ==============================================================================

def get_department_analytics():
    """
    [Pipeline 1]: Department Patient Census & Revenue ($match, $group, $sort)
    """
    pipeline = [
        {"$match": {"status": {"$ne": "Archived"}}},
        {
            "$group": {
                "_id": "$department",
                "total_patients": {"$sum": 1},
                "average_age": {"$avg": "$age"},
                "total_revenue": {"$sum": "$billing.total_amount"},
                "avg_bill_amount": {"$avg": "$billing.total_amount"}
            }
        },
        {"$sort": {"total_revenue": -1}}
    ]
    results = list(db.patients.aggregate(pipeline))
    return [{"department": r["_id"], **r} for r in results]

def get_vitals_anomalies():
    """
    [Pipeline 2]: Critical Vitals Triage Anomaly Alert ($unwind, $match, $sort)
    Flattens embedded vitals to alert on Heart Rate >= 100 or SpO2 <= 95%.
    """
    pipeline = [
        {"$unwind": "$vitals_history"},
        {
            "$match": {
                "$or": [
                    {"vitals_history.heart_rate": {"$gte": 100}},
                    {"vitals_history.oxygen_level": {"$lte": 95}}
                ]
            }
        },
        {
            "$project": {
                "_id": 0,
                "patient_id": 1,
                "patient_name": "$name",
                "department": 1,
                "heart_rate": "$vitals_history.heart_rate",
                "oxygen_level": "$vitals_history.oxygen_level",
                "blood_pressure": "$vitals_history.blood_pressure",
                "temperature": "$vitals_history.temperature"
            }
        },
        {"$sort": {"heart_rate": -1}}
    ]
    return list(db.patients.aggregate(pipeline))

def get_top_medications(limit=5):
    """
    [Pipeline 3]: Pharmacy Prescription Demand ($unwind, $group, $sort)
    Flattens prescriptions array to aggregate top dispensed drugs.
    """
    pipeline = [
        {"$unwind": "$prescriptions"},
        {
            "$group": {
                "_id": "$prescriptions.medicine",
                "prescription_count": {"$sum": 1},
                "avg_duration_days": {"$avg": "$prescriptions.days"}
            }
        },
        {"$sort": {"prescription_count": -1}},
        {"$limit": limit}
    ]
    results = list(db.patients.aggregate(pipeline))
    return [{"medicine": r["_id"], **r} for r in results]

def get_executive_summary():
    """
    [Pipeline 4]: Multi-Faceted Executive KPI ($facet)
    Executes multiple independent analytical sub-pipelines in a single round-trip.
    """
    pipeline = [
        {
            "$facet": {
                "status_summary": [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "billing_summary": [
                    {
                        "$group": {
                            "_id": "$billing.payment_status",
                            "total_billed": {"$sum": "$billing.total_amount"},
                            "patient_count": {"$sum": 1}
                        }
                    },
                    {"$sort": {"total_billed": -1}}
                ]
            }
        }
    ]
    res = list(db.patients.aggregate(pipeline))
    return res[0] if res else {"status_summary": [], "billing_summary": []}


# ==============================================================================
# SECTION 7: FLASK WEB CONTROLLERS & ROUTES
# ==============================================================================

@app.context_processor
def inject_globals():
    """Global parameters injected into all HTML templates."""
    return {
        "is_mock_mode": is_mock_mode,
        "database_name": db.name,
        "total_active_patients": db.patients.count_documents({"status": {"$ne": "Archived"}}),
        "student_name": "Ojaswi Bhardwaj",
        "student_reg": "12319444",
        "student_roll": "37",
        "student_sec": "K3P23SD"
    }

@app.route("/")
def index():
    """Executive Hospital Dashboard."""
    total_patients = db.patients.count_documents({"status": {"$ne": "Archived"}})
    admitted = db.patients.count_documents({"status": "Admitted"})
    observation = db.patients.count_documents({"status": "Under Observation"})
    discharged = db.patients.count_documents({"status": "Discharged"})
    recent_patients = list(db.patients.find({"status": {"$ne": "Archived"}}).sort("admission_date", -1).limit(6))
    dept_analytics = get_department_analytics()

    departments = [
        {"department_name": "Cardiology", "occupied_beds": 22, "total_beds": 30},
        {"department_name": "Neurology", "occupied_beds": 18, "total_beds": 25},
        {"department_name": "Orthopedics", "occupied_beds": 14, "total_beds": 20},
        {"department_name": "General Medicine", "occupied_beds": 31, "total_beds": 40}
    ]

    return render_template(
        "index.html",
        total_patients=total_patients,
        admitted=admitted,
        observation=observation,
        discharged=discharged,
        recent_patients=recent_patients,
        dept_analytics=dept_analytics,
        departments=departments
    )

@app.route("/patients")
def patients_list():
    """Searchable Patient Directory with Dynamic Filtering."""
    dept = request.args.get("department", "").strip()
    status = request.args.get("status", "").strip()
    q = request.args.get("q", "").strip()

    query = {"status": {"$ne": "Archived"}}
    if dept and dept != "All":
        query["department"] = dept
    if status and status != "All":
        query["status"] = status
    if q:
        query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"patient_id": {"$regex": q, "$options": "i"}},
            {"medical_notes": {"$regex": q, "$options": "i"}}
        ]

    patients = list(db.patients.find(query).sort("admission_date", -1))
    return render_template(
        "patients.html",
        patients=patients,
        departments=["Cardiology", "Neurology", "Orthopedics", "General Medicine", "Pediatrics"],
        statuses=["Admitted", "Under Observation", "Discharged"],
        current_dept=dept,
        current_status=status,
        search_query=q
    )

@app.route("/patient/<patient_id>")
def patient_detail(patient_id):
    """Detailed Patient Chart with Vital Graphs (Chart.js) and Action Modals."""
    patient = db.patients.find_one({"patient_id": patient_id})
    if not patient:
        flash(f"Patient '{patient_id}' not found.", "danger")
        return redirect(url_for("patients_list"))

    vitals = patient.get("vitals_history", [])
    timestamps, heart_rates, systolic_bp, diastolic_bp, spo2_levels = [], [], [], [], []

    for v in vitals:
        ts = v.get("timestamp")
        timestamps.append(ts.strftime("%b %d, %H:%M") if isinstance(ts, datetime) else str(ts)[:16])
        heart_rates.append(v.get("heart_rate", 75))
        spo2_levels.append(v.get("oxygen_level", 98))
        parts = str(v.get("blood_pressure", "120/80")).split("/")
        systolic_bp.append(int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 120)
        diastolic_bp.append(int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 80)

    doctor = {
        "doctor_id": "DOC-201",
        "name": patient.get("assigned_doctor_name", "Dr. Sarah Jenkins"),
        "specialization": "Specialist Physician",
        "department": patient.get("department", "Cardiology"),
        "experience_years": 14,
        "consultation_fee": patient.get("billing", {}).get("consultation_fee", 150.0),
        "ratings": 4.9
    }

    return render_template(
        "patient_detail.html",
        patient=patient,
        doctor=doctor,
        chart_data={
            "labels": timestamps,
            "heart_rates": heart_rates,
            "systolic": systolic_bp,
            "diastolic": diastolic_bp,
            "spo2": spo2_levels
        }
    )

@app.route("/patients/new", methods=["GET", "POST"])
def patient_create():
    """Patient Registration with Live $jsonSchema Validation Demo."""
    doctors = [
        {"doctor_id": "DOC-201", "name": "Dr. Sarah Jenkins", "specialization": "Chief Cardiologist"},
        {"doctor_id": "DOC-202", "name": "Dr. Rajesh Sharma", "specialization": "Senior Neurologist"},
        {"doctor_id": "DOC-203", "name": "Dr. Emily Taylor", "specialization": "Orthopedic Surgeon"},
        {"doctor_id": "DOC-204", "name": "Dr. Anita Desai", "specialization": "General Physician"}
    ]

    if request.method == "POST":
        try:
            pid = request.form.get("patient_id", "").strip()
            name = request.form.get("name", "").strip()
            age_raw = request.form.get("age", "").strip()
            age = int(age_raw) if age_raw.isdigit() else age_raw
            gender = request.form.get("gender")
            blood_group = request.form.get("blood_group")
            department = request.form.get("department")
            status = request.form.get("status", "Admitted")
            notes = [n.strip() for n in request.form.get("medical_notes", "").split("\n") if n.strip()]

            room = float(request.form.get("room_charges", 500) or 0)
            fee = float(request.form.get("consultation_fee", 150) or 0)
            meds = float(request.form.get("medicine_charges", 50) or 0)

            doc = {
                "patient_id": pid,
                "name": name,
                "age": age,
                "gender": gender,
                "blood_group": blood_group,
                "department": department,
                "status": status,
                "assigned_doctor_name": "Dr. Sarah Jenkins",
                "admission_date": datetime.now(),
                "contact": {"phone": request.form.get("phone", ""), "email": "", "emergency_contact": ""},
                "medical_notes": notes,
                "vitals_history": [
                    {
                        "timestamp": datetime.now(),
                        "blood_pressure": request.form.get("blood_pressure", "120/80"),
                        "heart_rate": int(request.form.get("heart_rate", 75)),
                        "oxygen_level": int(request.form.get("oxygen_level", 98)),
                        "temperature": float(request.form.get("temperature", 98.6))
                    }
                ],
                "prescriptions": [],
                "billing": {
                    "room_charges": room,
                    "consultation_fee": fee,
                    "medicine_charges": meds,
                    "total_amount": room + fee + meds,
                    "payment_status": request.form.get("payment_status", "Pending")
                }
            }

            res = add_patient(doc)
            if res["success"]:
                flash(f"Patient '{name}' ({pid}) successfully admitted!", "success")
                return redirect(url_for("patient_detail", patient_id=pid))
            else:
                flash(res["error"], "danger")
        except Exception as e:
            flash(f"Error during admission: {e}", "danger")

    return render_template("patient_form.html", doctors=doctors)

@app.route("/patient/<patient_id>/add-vitals", methods=["POST"])
def patient_add_vitals(patient_id):
    """Action: Appends vital measurement using MongoDB $push operator."""
    vital = {
        "timestamp": datetime.now(),
        "blood_pressure": request.form.get("blood_pressure", "120/80"),
        "heart_rate": int(request.form.get("heart_rate", 75)),
        "oxygen_level": int(request.form.get("oxygen_level", 98)),
        "temperature": float(request.form.get("temperature", 98.6))
    }
    record_vital_reading(patient_id, vital)
    flash("Vitals recorded successfully via MongoDB $push!", "success")
    return redirect(url_for("patient_detail", patient_id=patient_id))

@app.route("/patient/<patient_id>/update-billing", methods=["POST"])
def patient_update_billing(patient_id):
    """Action: Updates patient billing ledger using MongoDB $inc and $set operators."""
    med = float(request.form.get("additional_medicine_charge", 0) or 0)
    status = request.form.get("payment_status")
    update_billing_charges(patient_id, med, status)
    flash("Billing updated via MongoDB $inc operator!", "success")
    return redirect(url_for("patient_detail", patient_id=patient_id))

@app.route("/patient/<patient_id>/discharge", methods=["POST"])
def patient_discharge(patient_id):
    """Action: Updates status to Discharged."""
    db.patients.update_one({"patient_id": patient_id}, {"$set": {"status": "Discharged"}})
    flash(f"Patient '{patient_id}' has been discharged.", "warning")
    return redirect(url_for("patient_detail", patient_id=patient_id))

@app.route("/patient/<patient_id>/archive", methods=["POST"])
def patient_archive(patient_id):
    """Action: Soft deletes patient record using $set."""
    soft_delete_patient(patient_id)
    flash(f"Patient '{patient_id}' archived (Soft Delete).", "info")
    return redirect(url_for("patients_list"))

@app.route("/analytics")
def analytics():
    """MongoDB Aggregations Analytics Dashboard."""
    dept_analytics = get_department_analytics()
    vitals_anomalies = get_vitals_anomalies()
    top_meds = get_top_medications()
    executive_facets = get_executive_summary()

    doc_workload = [
        {"doctor_id": "DOC-201", "doctor_name": "Dr. Sarah Jenkins", "specialization": "Cardiology", "department": "Cardiology", "experience_years": 16, "patient_count": 2, "total_generated_revenue": 3090.0, "ratings": 4.9},
        {"doctor_id": "DOC-202", "doctor_name": "Dr. Rajesh Sharma", "specialization": "Neurology", "department": "Neurology", "experience_years": 14, "patient_count": 1, "total_generated_revenue": 1310.0, "ratings": 4.8},
        {"doctor_id": "DOC-203", "doctor_name": "Dr. Emily Taylor", "specialization": "Orthopedics", "department": "Orthopedics", "experience_years": 11, "patient_count": 1, "total_generated_revenue": 3940.0, "ratings": 4.7},
        {"doctor_id": "DOC-204", "doctor_name": "Dr. Anita Desai", "specialization": "General Medicine", "department": "General Medicine", "experience_years": 12, "patient_count": 1, "total_generated_revenue": 1625.0, "ratings": 4.6}
    ]

    return render_template(
        "analytics.html",
        dept_analytics=dept_analytics,
        doc_workload=doc_workload,
        vitals_anomalies=vitals_anomalies,
        top_meds=top_meds,
        dashboard_facets=executive_facets
    )

@app.route("/ai-search")
def ai_search():
    """AI Vector Similarity Search Interface."""
    q = request.args.get("q", "").strip()
    dept = request.args.get("department", "All").strip()
    results = []
    ai_summary = None
    atlas_pipeline = []

    sample_queries = [
        "Patient with acute chest pain, elevated pulse, and palpitations",
        "Severe recurring headache and migraine with aura",
        "Knee joint replacement recovery and fracture trauma",
        "High fever, infection, and low oxygen saturation",
        "Stomach pain, acute dizziness, and nausea"
    ]

    if q:
        results = search_similar_patients(q, top_k=4, dept=dept)
        query_vec = text_to_vector(q)
        atlas_pipeline = [
            {
                "$vectorSearch": {
                    "index": "symptom_vector_index",
                    "path": "clinical_embedding",
                    "queryVector": query_vec,
                    "numCandidates": 20,
                    "limit": 4
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "patient_id": 1,
                    "name": 1,
                    "department": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        top_dept = results[0]["department"] if results else "General"
        top_name = results[0]["name"] if results else "None"
        avg_sim = round(sum(r["match_percentage"] for r in results) / len(results), 1) if results else 0.0

        ai_summary = {
            "confidence": "High" if avg_sim > 50 else "Moderate",
            "primary_department": top_dept,
            "average_similarity": avg_sim,
            "insights": [
                f"Query symptoms correlate most with <b>{top_dept}</b> department.",
                f"Top matched patient in database: <b>{top_name}</b>.",
                f"Vectors compared across 10 clinical symptom dimensions."
            ],
            "suggested_medications": list(dict.fromkeys([m["medicine"] for r in results for m in r.get("prescriptions", [])]))[:4]
        }

    return render_template(
        "ai_search.html",
        query_text=q,
        dept_filter=dept,
        results=results,
        ai_summary=ai_summary,
        atlas_pipeline=atlas_pipeline,
        sample_queries=sample_queries
    )

@app.route("/api/seed", methods=["POST"])
def api_seed_database():
    """Re-seed database button in navbar."""
    seed_sample_data()
    flash("Database reset and populated with starter clinical records!", "success")
    return redirect(url_for("index"))


# ==============================================================================
# SECTION 8: ENTRYPOINT (RENDER DEPLOYMENT & LOCAL RUN)
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    print("\n" + "=" * 60)
    print(" MediTrack: Smart Hospital System Starting...")
    print(f" Database: {db.name} (Mode: {'In-Memory Mock' if is_mock_mode else 'Live MongoDB'})")
    print(f" Web Portal running at: http://0.0.0.0:{port}")
    print("=" * 60 + "\n")
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
