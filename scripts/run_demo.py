"""
Automated Demonstration Script for Smart Hospital MongoDB System.
Executes all project requirements sequentially, logs output, and formats tables
for live presentation, screenshots, and viva demonstration.
"""

import sys
import os
from datetime import datetime
from tabulate import tabulate

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import (
    db,
    is_mock_mode,
    seed_sample_data,
    add_patient,
    record_vital_reading,
    update_billing_charges,
    soft_delete_patient,
    get_department_analytics,
    get_vitals_anomalies,
    get_top_medications,
    get_executive_summary,
    search_similar_patients
)

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class TeeOutput:
    """Duplicates stdout to both terminal and a demonstration log file."""
    def __init__(self, log_filepath):
        self.terminal = sys.stdout
        self.log = open(log_filepath, "w", encoding="utf-8")

    def write(self, message):
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode("ascii", "replace").decode("ascii"))
        self.log.write(message)

    def flush(self):
        try:
            self.terminal.flush()
        except Exception:
            pass
        self.log.flush()

    def close(self):
        self.log.close()


def print_banner(title: str):
    width = 78
    print("\n" + "=" * width)
    print(f" {title.upper()} ".center(width, "="))
    print("=" * width + "\n")


def run_full_demonstration(output_log_path: str = "output_demonstration.txt"):
    tee = TeeOutput(output_log_path)
    original_stdout = sys.stdout
    sys.stdout = tee

    try:
        print_banner("Smart Hospital & Patient Care Management System (MediTrack)")
        print(f"Execution Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Author              : Ojaswi Bhardwaj (Reg: 12319444, Roll: 37, Section: K3P23SD)")
        print("Course / Subject    : CSE494 - MongoDB Coursework Project (CO4, CO5, CO6)")
        print("Live Deployment     : https://mongo-project-nwjl.onrender.com")
        print("GitHub Repository   : https://github.com/ojaswi1234/mongo_project.git\n")

        # ----------------------------------------------------------------------
        # STEP 1: DATABASE CONNECTION
        # ----------------------------------------------------------------------
        print_banner("1. Database Connection & Environment Setup")
        print(f"Connection Status   : {'[MOCK IN-MEMORY MODE]' if is_mock_mode else '[LIVE MONGODB SERVER]'}")
        print(f"Database Selected   : {db.name}")

        # ----------------------------------------------------------------------
        # STEP 2: SCHEMA VALIDATION INTEGRITY TEST
        # ----------------------------------------------------------------------
        print_banner("2. Schema Validation ($jsonSchema) Enforcement")
        print("Attempting to insert an invalid patient document:")
        print("  - patient_id: 'INVALID_ID_FORMAT' (Violates regex: ^PAT-[0-9]{4}$)")
        print("  - age: 155 (Violates maximum: 125)")
        print("  - gender: 'Alien' (Violates enum: [Male, Female, Other])")

        invalid_doc = {
            "patient_id": "INVALID_ID_FORMAT",
            "name": "Validation Test Dummy",
            "age": 155,
            "gender": "Alien",
            "department": "Cardiology",
            "status": "Admitted",
            "billing": {"total_amount": 300, "payment_status": "Paid"}
        }
        res = add_patient(invalid_doc)
        if not res["success"]:
            print(f"\n[OK] Schema Engine Correctly Blocked Document: {res.get('error')}")
        else:
            print("[!] Warning: Document was allowed.")

        # ----------------------------------------------------------------------
        # STEP 3: SEED DATA POPULATION
        # ----------------------------------------------------------------------
        print_banner("3. Populating Realistic Hospital Seed Data")
        seed_sample_data()
        patient_count = db.patients.count_documents({})
        print(f"Total Patients Seeded: {patient_count}")

        # ----------------------------------------------------------------------
        # STEP 4: CRUD OPERATIONS (CREATE, READ, UPDATE, DELETE)
        # ----------------------------------------------------------------------
        print_banner("4. CRUD Operations Demonstration")

        # 4.1 CREATE
        print("[4.1] CREATE Operation: Inserting new valid patient PAT-1009...")
        new_patient = {
            "patient_id": "PAT-1009",
            "name": "Lucas Vance",
            "age": 31,
            "gender": "Male",
            "blood_group": "O+",
            "department": "Cardiology",
            "status": "Admitted",
            "assigned_doctor_name": "Dr. Sarah Jenkins",
            "admission_date": datetime.now(),
            "medical_notes": ["Routine cardiac checkup post-palpitations"],
            "vitals_history": [
                {"timestamp": datetime.now(), "blood_pressure": "120/80", "heart_rate": 72, "oxygen_level": 99, "temperature": 98.6}
            ],
            "prescriptions": [
                {"medicine": "Metoprolol", "dosage": "25mg", "days": 14}
            ],
            "billing": {"room_charges": 500.0, "consultation_fee": 150.0, "medicine_charges": 45.0, "total_amount": 695.0, "payment_status": "Pending"}
        }
        create_res = add_patient(new_patient)
        print(f"Insert Success: {create_res['success']} | Inserted ID: {create_res.get('inserted_id')}")

        # 4.2 READ
        print("\n[4.2] READ Operation: Querying Admitted Cardiology Patients...")
        cardio_patients = list(db.patients.find({"department": "Cardiology", "status": "Admitted"}))
        t_cardio = [
            [p["patient_id"], p["name"], p["age"], p["blood_group"], p["status"], f"${p['billing']['total_amount']}"]
            for p in cardio_patients
        ]
        print(tabulate(t_cardio, headers=["Patient ID", "Name", "Age", "Blood", "Status", "Total Bill"], tablefmt="grid"))

        # 4.3 UPDATE ($push array operator)
        print("\n[4.3] UPDATE Operation: Appending fresh Vital Reading to PAT-1001 using $push...")
        vital_reading = {
            "timestamp": datetime.now(),
            "blood_pressure": "122/80",
            "heart_rate": 70,
            "oxygen_level": 99,
            "temperature": 98.4
        }
        push_ok = record_vital_reading("PAT-1001", vital_reading)
        print(f"Vital Appended via $push: Success = {push_ok}")

        # 4.4 UPDATE ($inc billing operator)
        print("\n[4.4] UPDATE Operation: Adding medicine charge ($50) to PAT-1001 via $inc...")
        inc_ok = update_billing_charges("PAT-1001", add_medicine=50.0, new_status="Paid")
        pat_updated = db.patients.find_one({"patient_id": "PAT-1001"})
        print(f"Billing Updated via $inc: Total is now ${pat_updated['billing']['total_amount']} (Status: {pat_updated['billing']['payment_status']})")

        # 4.5 DELETE (Soft Delete)
        print("\n[4.5] DELETE Operation: Soft Deleting PAT-1004 (Setting status to 'Archived')...")
        soft_delete_patient("PAT-1004")
        pat_archived = db.patients.find_one({"patient_id": "PAT-1004"})
        print(f"Soft Deletion Result: Status = '{pat_archived.get('status')}', is_archived = {pat_archived.get('is_archived')}")

        # ----------------------------------------------------------------------
        # STEP 5: AGGREGATION PIPELINES
        # ----------------------------------------------------------------------
        print_banner("5. Multi-Stage Aggregation Pipelines")

        # Pipeline 1
        print("[PIPELINE 1] Department-wise Patient Demographics & Financial Revenue ($match, $group, $sort)")
        dept_data = get_department_analytics()
        t_dept = [
            [d["department"], d["total_patients"], round(d["average_age"], 1), f"${round(d['total_revenue'], 2)}", f"${round(d['avg_bill_amount'], 2)}"]
            for d in dept_data
        ]
        print(tabulate(t_dept, headers=["Department", "Patients", "Avg Age", "Total Revenue", "Avg Bill"], tablefmt="grid"))

        # Pipeline 2
        print("\n[PIPELINE 2] Clinical Critical Vitals Triage Anomaly Alert ($unwind, $match, $sort)")
        vitals_alerts = get_vitals_anomalies()
        t_vitals = [
            [v["patient_id"], v["patient_name"], v["department"], f"{v['heart_rate']} BPM", f"{v['oxygen_level']}%", v["blood_pressure"]]
            for v in vitals_alerts
        ]
        print(tabulate(t_vitals, headers=["Patient ID", "Name", "Department", "Heart Rate", "SpO2", "BP"], tablefmt="grid"))

        # Pipeline 3
        print("\n[PIPELINE 3] Pharmacy Most Prescribed Medications ($unwind, $group, $sort, $limit)")
        meds_data = get_top_medications(limit=5)
        t_meds = [
            [m["medicine"], m["prescription_count"], f"{m['avg_duration_days']} days"]
            for m in meds_data
        ]
        print(tabulate(t_meds, headers=["Medicine Name", "Total Prescriptions", "Avg Duration"], tablefmt="grid"))

        # Pipeline 4
        print("\n[PIPELINE 4] Multi-Faceted Executive Hospital Dashboard ($facet)")
        facets = get_executive_summary()
        print("\n-- Inpatient Status Distribution:")
        print(tabulate([[s["_id"], s["count"]] for s in facets.get("status_summary", [])], headers=["Status", "Patients"], tablefmt="simple"))
        print("\n-- Billing Realization Summary:")
        print(tabulate([[b["_id"], b["patient_count"], f"${round(b['total_billed'], 2)}"] for b in facets.get("billing_summary", [])], headers=["Payment Status", "Patients", "Total Amount"], tablefmt="simple"))

        # ----------------------------------------------------------------------
        # STEP 6: AI VECTOR SEARCH (10-DIMENSIONAL SYMPTOM VECTORS)
        # ----------------------------------------------------------------------
        print_banner("6. MongoDB as a Vector Database & AI Clinical Search")
        query = "acute chest pain and elevated palpitations"
        print(f"Query: '{query}'")
        matched = search_similar_patients(query, top_k=3)
        t_sim = [
            [m["patient_id"], m["name"], m["department"], f"{m['match_percentage']}%", m["similarity_score"]]
            for m in matched
        ]
        print(tabulate(t_sim, headers=["Patient ID", "Matched Name", "Department", "Match %", "Cosine Score"], tablefmt="grid"))

        print_banner("All Operations Executed Successfully!")
        print(f"[OK] Full log saved to: {output_log_path}")

    finally:
        sys.stdout = original_stdout
        tee.close()


if __name__ == "__main__":
    log_file = os.path.join(os.path.dirname(__file__), "..", "output_demonstration.txt")
    run_full_demonstration(log_file)
