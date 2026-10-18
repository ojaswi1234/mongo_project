"""
Flask Web Application for Smart Hospital MongoDB Management System.
Features:
- MongoDB CRUD web views (Create, Read, Update, Delete)
- Native PyMongo connection management
- MongoDB Schema Validation ($jsonSchema) enforcement
- Interactive MongoDB Aggregation Analytics with Chart.js
- MongoDB Vector Search & AI Clinical Assistant (Vector Database)
"""

import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config.database import get_db_connection
from database.schema_validation import apply_schema_validations
from database.seed_data import populate_seed_data
from operations.crud import (
    create_patient,
    get_patient_by_id,
    search_patients_advanced,
    update_patient_status,
    add_patient_vital_reading,
    update_billing_charges,
    soft_delete_patient
)
from operations.aggregations import (
    get_department_analytics,
    get_doctor_workload_analytics,
    get_critical_vitals_anomalies,
    get_top_prescribed_medications,
    get_hospital_executive_dashboard
)
from ai.vector_engine import (
    perform_mongo_vector_search,
    get_atlas_vector_search_pipeline,
    generate_ai_clinical_summary,
    generate_clinical_embedding
)

app = Flask(__name__)
app.secret_key = "smarthospital-secret-key-cse-finalyear"
CORS(app)

# Initialize Database Connection
client, db, is_mock = get_db_connection()
apply_schema_validations(db, is_mock=is_mock)

# Auto-seed if database is empty
if db.patients.count_documents({}) == 0:
    populate_seed_data(db, drop_existing=False)


@app.context_processor
def inject_global_data():
    """Injects system status and counts to all templates."""
    total_patients = db.patients.count_documents({"status": {"$ne": "Archived"}})
    admitted_patients = db.patients.count_documents({"status": "Admitted"})
    return {
        "is_mock_mode": is_mock,
        "database_name": db.name,
        "total_active_patients": total_patients,
        "total_admitted_patients": admitted_patients,
        "current_year": datetime.now().year
    }


# ==============================================================================
# WEB VIEWS / CONTROLLERS
# ==============================================================================

@app.route("/")
def index():
    """Executive Dashboard View."""
    # Summary Metrics
    total_patients = db.patients.count_documents({"status": {"$ne": "Archived"}})
    admitted = db.patients.count_documents({"status": "Admitted"})
    observation = db.patients.count_documents({"status": "Under Observation"})
    discharged = db.patients.count_documents({"status": "Discharged"})

    # Recent Patients
    recent_patients = list(
        db.patients.find({"status": {"$ne": "Archived"}})
        .sort("admission_date", -1)
        .limit(6)
    )

    # Department Statistics (Aggregation Pipeline 1)
    dept_analytics = get_department_analytics(db)

    # Bed Occupancy from departments
    departments = list(db.departments.find({}))

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
    """Searchable & Filterable Patient Directory."""
    dept_filter = request.args.get("department", "").strip()
    status_filter = request.args.get("status", "").strip()
    search_query = request.args.get("q", "").strip()

    query = {"status": {"$ne": "Archived"}}
    if dept_filter and dept_filter != "All":
        query["department"] = dept_filter
    if status_filter and status_filter != "All":
        query["status"] = status_filter
    if search_query:
        query["$or"] = [
            {"name": {"$regex": search_query, "$options": "i"}},
            {"patient_id": {"$regex": search_query, "$options": "i"}},
            {"medical_notes": {"$regex": search_query, "$options": "i"}}
        ]

    patients = list(db.patients.find(query).sort("admission_date", -1))
    all_departments = ["Cardiology", "Neurology", "Orthopedics", "General Medicine", "Pediatrics"]
    all_statuses = ["Admitted", "Under Observation", "Discharged"]

    return render_template(
        "patients.html",
        patients=patients,
        departments=all_departments,
        statuses=all_statuses,
        current_dept=dept_filter,
        current_status=status_filter,
        search_query=search_query
    )


@app.route("/patient/<patient_id>")
def patient_detail(patient_id):
    """Detailed Patient View with Vitals Timeline & Doctor Details."""
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        flash(f"Patient with ID '{patient_id}' was not found.", "danger")
        return redirect(url_for("patients_list"))

    # Fetch assigned doctor via referencing
    doctor = None
    if patient.get("assigned_doctor_id"):
        doctor = db.doctors.find_one({"doctor_id": patient["assigned_doctor_id"]})

    # Prepare vitals history for Chart.js
    vitals = patient.get("vitals_history", [])
    timestamps = []
    heart_rates = []
    systolic_bp = []
    diastolic_bp = []
    spo2_levels = []

    for v in vitals:
        ts = v.get("timestamp")
        if isinstance(ts, datetime):
            timestamps.append(ts.strftime("%b %d, %H:%M"))
        else:
            timestamps.append(str(ts)[:16])

        heart_rates.append(v.get("heart_rate", 75))
        spo2_levels.append(v.get("oxygen_level", 98))

        # Parse BP e.g. "120/80"
        bp_str = str(v.get("blood_pressure", "120/80"))
        parts = bp_str.split("/")
        systolic_bp.append(int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 120)
        diastolic_bp.append(int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 80)

    chart_data = {
        "labels": timestamps,
        "heart_rates": heart_rates,
        "systolic": systolic_bp,
        "diastolic": diastolic_bp,
        "spo2": spo2_levels
    }

    return render_template(
        "patient_detail.html",
        patient=patient,
        doctor=doctor,
        chart_data=chart_data
    )


@app.route("/patients/new", methods=["GET", "POST"])
def patient_create():
    """Register New Patient with MongoDB $jsonSchema Validation Demo."""
    doctors = list(db.doctors.find({}))
    if request.method == "POST":
        try:
            patient_id = request.form.get("patient_id", "").strip()
            name = request.form.get("name", "").strip()
            age_raw = request.form.get("age", "").strip()
            age = int(age_raw) if age_raw.isdigit() else age_raw
            gender = request.form.get("gender")
            blood_group = request.form.get("blood_group")
            department = request.form.get("department")
            status = request.form.get("status", "Admitted")
            assigned_doctor_id = request.form.get("assigned_doctor_id")
            medical_notes = [n.strip() for n in request.form.get("medical_notes", "").split("\n") if n.strip()]

            # Billing
            room_charges = float(request.form.get("room_charges", 500) or 0)
            consultation_fee = float(request.form.get("consultation_fee", 150) or 0)
            medicine_charges = float(request.form.get("medicine_charges", 50) or 0)
            payment_status = request.form.get("payment_status", "Pending")

            patient_doc = {
                "patient_id": patient_id,
                "name": name,
                "age": age,
                "gender": gender,
                "blood_group": blood_group,
                "department": department,
                "status": status,
                "assigned_doctor_id": assigned_doctor_id,
                "admission_date": datetime.now(),
                "discharge_date": None,
                "contact": {
                    "phone": request.form.get("phone", ""),
                    "email": request.form.get("email", ""),
                    "emergency_contact": request.form.get("emergency_contact", "")
                },
                "vitals_history": [
                    {
                        "timestamp": datetime.now(),
                        "blood_pressure": request.form.get("blood_pressure", "120/80"),
                        "heart_rate": int(request.form.get("heart_rate", 75)),
                        "temperature": float(request.form.get("temperature", 98.6)),
                        "oxygen_level": int(request.form.get("oxygen_level", 98))
                    }
                ],
                "medical_notes": medical_notes,
                "prescriptions": [],
                "billing": {
                    "room_charges": room_charges,
                    "consultation_fee": consultation_fee,
                    "medicine_charges": medicine_charges,
                    "total_amount": room_charges + consultation_fee + medicine_charges,
                    "payment_status": payment_status
                }
            }

            result = create_patient(db, patient_doc)
            if result["success"]:
                flash(f"Patient '{name}' ({patient_id}) successfully admitted into {department}!", "success")
                return redirect(url_for("patient_detail", patient_id=patient_id))
            else:
                flash(result["error"], "danger")
        except Exception as e:
            flash(f"Error during admission: {str(e)}", "danger")

    return render_template("patient_form.html", doctors=doctors)


@app.route("/patient/<patient_id>/add-vitals", methods=["POST"])
def patient_add_vitals(patient_id):
    """Appends vital measurement to embedded array using MongoDB $push operator."""
    try:
        vital_record = {
            "timestamp": datetime.now(),
            "blood_pressure": request.form.get("blood_pressure", "120/80"),
            "heart_rate": int(request.form.get("heart_rate", 75)),
            "temperature": float(request.form.get("temperature", 98.6)),
            "oxygen_level": int(request.form.get("oxygen_level", 98))
        }
        res = add_patient_vital_reading(db, patient_id, vital_record)
        if res["success"]:
            flash("Vitals successfully appended to patient history using MongoDB $push!", "success")
        else:
            flash("Failed to record vitals.", "danger")
    except Exception as e:
        flash(f"Invalid vitals input: {str(e)}", "danger")

    return redirect(url_for("patient_detail", patient_id=patient_id))


@app.route("/patient/<patient_id>/update-billing", methods=["POST"])
def patient_update_billing(patient_id):
    """Updates patient billing charges using MongoDB $inc and $set operators."""
    try:
        med_charge = float(request.form.get("additional_medicine_charge", 0) or 0)
        room_charge = float(request.form.get("additional_room_charge", 0) or 0)
        pay_status = request.form.get("payment_status")

        res = update_billing_charges(
            db,
            patient_id,
            additional_room_charge=room_charge,
            additional_medicine_charge=med_charge,
            new_payment_status=pay_status
        )
        if res["success"]:
            flash("Billing ledger successfully updated using MongoDB $inc operator!", "success")
        else:
            flash("No changes made to billing.", "info")
    except Exception as e:
        flash(f"Billing error: {str(e)}", "danger")

    return redirect(url_for("patient_detail", patient_id=patient_id))


@app.route("/patient/<patient_id>/discharge", methods=["POST"])
def patient_discharge(patient_id):
    """Discharges patient and sets discharge date."""
    res = update_patient_status(db, patient_id, "Discharged")
    if res["success"]:
        flash(f"Patient '{patient_id}' has been discharged.", "warning")
    return redirect(url_for("patient_detail", patient_id=patient_id))


@app.route("/patient/<patient_id>/archive", methods=["POST"])
def patient_archive(patient_id):
    """Soft deletes patient (HIPAA audit compliance)."""
    res = soft_delete_patient(db, patient_id)
    if res["success"]:
        flash(f"Patient '{patient_id}' has been archived (Soft Delete).", "info")
    return redirect(url_for("patients_list"))


@app.route("/analytics")
def analytics():
    """MongoDB Aggregation Pipelines Visualization Dashboard."""
    # Pipeline 1: Department Financials & Patients
    dept_analytics = get_department_analytics(db)

    # Pipeline 2: Doctor Workload ($lookup)
    doc_workload = get_doctor_workload_analytics(db)

    # Pipeline 3: Vitals Anomalies ($unwind + $match)
    vitals_anomalies = get_critical_vitals_anomalies(db, min_heart_rate=100, max_oxygen=95)

    # Pipeline 4: Prescriptions ($unwind + $group)
    top_meds = get_top_prescribed_medications(db, limit=6)

    # Pipeline 5: Executive Dashboard ($facet)
    dashboard_facets = get_hospital_executive_dashboard(db)

    return render_template(
        "analytics.html",
        dept_analytics=dept_analytics,
        doc_workload=doc_workload,
        vitals_anomalies=vitals_anomalies,
        top_meds=top_meds,
        dashboard_facets=dashboard_facets
    )


@app.route("/ai-search", methods=["GET", "POST"])
def ai_search():
    """MongoDB Vector Database & AI Clinical Case Similarity Search."""
    sample_queries = [
        "Patient with acute chest pain, elevated pulse, and suspected cardiac ischemia",
        "Chronic migraine with severe headaches and neurological aura",
        "Post-operative joint surgery knee replacement with limited mobility",
        "Respiratory infection with high fever, cough, and decreased oxygen saturation",
        "Acute dizziness, balance loss, and vertigo episodes"
    ]

    query_text = request.args.get("q", "").strip() or request.form.get("query", "").strip()
    dept_filter = request.args.get("department", "All").strip()
    results = []
    ai_summary = None
    atlas_pipeline = []

    if query_text:
        results = perform_mongo_vector_search(db, query_text, top_k=4, department_filter=dept_filter)
        ai_summary = generate_ai_clinical_summary(query_text, results)
        query_vec = generate_clinical_embedding(query_text)
        atlas_pipeline = get_atlas_vector_search_pipeline(query_vec)

    return render_template(
        "ai_search.html",
        query_text=query_text,
        dept_filter=dept_filter,
        results=results,
        ai_summary=ai_summary,
        atlas_pipeline=atlas_pipeline,
        sample_queries=sample_queries
    )


@app.route("/api/seed", methods=["POST"])
def api_seed_database():
    """Reset & Re-populate Database with Realistic Seed Data."""
    try:
        res = populate_seed_data(db, drop_existing=True)
        flash(f"Database successfully re-seeded with {res['patients_inserted']} patients and {res['doctors_inserted']} doctors!", "success")
    except Exception as e:
        flash(f"Seed error: {str(e)}", "danger")
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    print("\n=======================================================")
    print(" Smart Hospital MongoDB Web Application Starting...")
    print(f" Database: {db.name} (Mode: {'In-Memory Mock' if is_mock else 'Live MongoDB'})")
    print(f" Access Web Portal at: http://0.0.0.0:{port}")
    print("=======================================================\n")
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
