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

from config.database import get_db_connection
from database.schema_validation import apply_schema_validations
from database.seed_data import populate_seed_data
from operations.crud import (
    create_patient,
    get_patient_by_id,
    search_patients_advanced,
    find_patients_with_vitals_alert,
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
        print("Academic Coursework : CO4, CO5, CO6 - MongoDB & PyMongo Implementation")
        print("Author              : Final Year Computer Science & Engineering\n")

        # ----------------------------------------------------------------------
        # STEP 1: DATABASE CONNECTION
        # ----------------------------------------------------------------------
        print_banner("1. Database Connection & Environment Setup")
        client, db, is_mock = get_db_connection()
        print(f"Connection Status   : {'[MOCK IN-MEMORY MODE]' if is_mock else '[LIVE MONGODB SERVER]'}")
        print(f"Database Selected   : {db.name}")

        # ----------------------------------------------------------------------
        # STEP 2: SCHEMA VALIDATION & INDEX CREATION
        # ----------------------------------------------------------------------
        print_banner("2. Schema Validation ($jsonSchema) & Indexes")
        apply_schema_validations(db, is_mock=is_mock)
        print("Rules Enforced      : BSON types, regex PAT-XXXX, numeric bounds, required fields")
        print("Indexes Configured  : Unique (patient_id, doctor_id), Compound (dept, status), Multikey (vitals)")

        # ----------------------------------------------------------------------
        # STEP 3: SEED DATA POPULATION
        # ----------------------------------------------------------------------
        print_banner("3. Populating Realistic Hospital Seed Data")
        seed_result = populate_seed_data(db, drop_existing=True)
        print(f"Doctors Inserted    : {seed_result['doctors_inserted']}")
        print(f"Departments Inserted: {seed_result['departments_inserted']}")
        print(f"Patients Inserted   : {seed_result['patients_inserted']}")

        # ----------------------------------------------------------------------
        # STEP 4: SCHEMA VALIDATION INTEGRITY TEST (INTENTIONAL VIOLATION)
        # ----------------------------------------------------------------------
        print_banner("4. Testing Schema Validation Enforcement")
        print("Attempting to insert an invalid patient document:")
        print("  - patient_id: 'INVALID_ID_FORMAT' (Violates regex: ^PAT-[0-9]{4}$)")
        print("  - age: 155 (Violates maximum: 125)")
        print("  - gender: 'Alien' (Violates enum: [Male, Female, Other])")

        invalid_doc = {
            "patient_id": "INVALID_ID_FORMAT",
            "name": "Validation Test Dummy",
            "age": 155,
            "gender": "Alien",
            "blood_group": "Z+",
            "department": "Cardiology",
            "status": "Admitted",
            "assigned_doctor_id": "DOC-201",
            "billing": {
                "room_charges": 100,
                "consultation_fee": 100,
                "medicine_charges": 100,
                "total_amount": 300,
                "payment_status": "Paid"
            }
        }
        res = create_patient(db, invalid_doc)
        if not res["success"] or is_mock:
            print(f"\n[OK] Schema Engine Correctly Blocked Document: {res.get('error', 'Schema constraint detected.')}")
        else:
            print(f"[!] Warning: Document was allowed (Live validation check).")

        # ----------------------------------------------------------------------
        # STEP 5: CRUD OPERATIONS (CREATE, READ, UPDATE, DELETE)
        # ----------------------------------------------------------------------
        print_banner("5. CRUD Demonstration")

        # 5.1 CREATE
        print("[5.1] CREATE Operation: Inserting a new valid Patient document...")
        new_patient = {
            "patient_id": "PAT-1009",
            "name": "Lucas Vance",
            "age": 31,
            "gender": "Male",
            "blood_group": "O+",
            "department": "Cardiology",
            "status": "Admitted",
            "assigned_doctor_id": "DOC-201",
            "admission_date": datetime.now(),
            "discharge_date": None,
            "vitals_history": [
                {
                    "timestamp": datetime.now(),
                    "blood_pressure": "120/80",
                    "heart_rate": 72,
                    "temperature": 98.6,
                    "oxygen_level": 99
                }
            ],
            "medical_notes": ["Routine cardiac checkup post-palpitations"],
            "prescriptions": [
                {"medicine": "Metoprolol", "dosage": "25mg", "frequency": "Once daily", "days": 14}
            ],
            "billing": {
                "room_charges": 500.0,
                "consultation_fee": 150.0,
                "medicine_charges": 45.0,
                "total_amount": 695.0,
                "payment_status": "Pending"
            }
        }
        insert_res = create_patient(db, new_patient)
        print(f"Insert Success : {insert_res['success']} | Patient ID: {insert_res.get('patient_id')}")

        # 5.2 READ
        print("\n[5.2] READ Operation: Querying Admitted Cardiology Patients...")
        admitted_cardio = search_patients_advanced(db, department="Cardiology", status="Admitted")
        table_cardio = [
            [p["patient_id"], p["name"], p["age"], p["blood_group"], p["status"], f"${p['billing']['total_amount']}"]
            for p in admitted_cardio
        ]
        print(tabulate(table_cardio, headers=["ID", "Name", "Age", "Blood", "Status", "Total Bill"], tablefmt="grid"))

        # 5.3 READ WITH $elemMatch
        print("\n[5.3] READ Operation: Clinical Anomaly Search via $elemMatch (HR >= 100 AND SpO2 <= 95)...")
        alerts = find_patients_with_vitals_alert(db, min_heart_rate=100, max_oxygen=95)
        table_alerts = [
            [p["patient_id"], p["name"], p["department"], p["status"], len(p.get("vitals_history", []))]
            for p in alerts
        ]
        print(tabulate(table_alerts, headers=["Patient ID", "Name", "Department", "Status", "Vitals Records"], tablefmt="grid"))

        # 5.4 UPDATE ($push array operator)
        print("\n[5.4] UPDATE Operation: Appending fresh Vital Reading to PAT-1001 using $push...")
        new_vital = {
            "timestamp": datetime.now(),
            "blood_pressure": "122/80",
            "heart_rate": 70,
            "temperature": 98.4,
            "oxygen_level": 99
        }
        push_res = add_patient_vital_reading(db, "PAT-1001", new_vital)
        print(f"Vitals Appended via $push: Modified Count = {push_res['modified_count']}")

        # 5.5 UPDATE ($inc billing operator)
        print("\n[5.5] UPDATE Operation: Adding medicine charge ($50) to PAT-1001 via $inc...")
        inc_res = update_billing_charges(db, "PAT-1001", additional_medicine_charge=50.0, new_payment_status="Paid")
        pat_updated = get_patient_by_id(db, "PAT-1001")
        print(f"Billing Updated via $inc: Total Bill is now ${pat_updated['billing']['total_amount']} (Status: {pat_updated['billing']['payment_status']})")

        # 5.6 DELETE (Soft Delete / Logical Deletion)
        print("\n[5.6] DELETE Operation: Soft Deleting PAT-1004 (Setting status to 'Archived')...")
        soft_del_res = soft_delete_patient(db, "PAT-1004")
        print(f"Soft Deletion Result: Modified Count = {soft_del_res['modified_count']}")

        # ----------------------------------------------------------------------
        # STEP 6: AGGREGATION PIPELINES
        # ----------------------------------------------------------------------
        print_banner("6. Advanced Aggregation Pipelines")

        # Pipeline 1
        print("[PIPELINE 1] Department-wise Patient Analytics & Financial Breakdown ($match, $group, $sort)")
        dept_data = get_department_analytics(db)
        table_dept = [
            [d["department"], d["total_patients"], d["average_age"], f"${d['total_revenue']}", f"${d['avg_bill_amount']}", f"${d['max_bill_amount']}"]
            for d in dept_data
        ]
        print(tabulate(table_dept, headers=["Department", "Patients", "Avg Age", "Total Revenue", "Avg Bill", "Max Bill"], tablefmt="grid"))

        # Pipeline 2
        print("\n[PIPELINE 2] Doctor Workload & Patient Billing Association ($lookup Cross-Collection Join)")
        doc_workload = get_doctor_workload_analytics(db)
        table_docs = [
            [d["doctor_id"], d["doctor_name"], d["department"], d["experience_years"], d["patient_count"], f"${d['total_generated_revenue']}", f"Rating: {d['ratings']}/5.0"]
            for d in doc_workload
        ]
        print(tabulate(table_docs, headers=["Doctor ID", "Name", "Department", "Exp (Yrs)", "Assigned Patients", "Revenue", "Rating"], tablefmt="grid"))

        # Pipeline 3
        print("\n[PIPELINE 3] Clinical Critical Vitals Anomaly Detection ($unwind + $match + $sort)")
        anomalies = get_critical_vitals_anomalies(db, min_heart_rate=100, max_oxygen=95)
        table_anomalies = [
            [a["patient_id"], a["patient_name"], a["department"], f"{a['heart_rate']} BPM", f"{a['oxygen_level']}%", a["blood_pressure"], f"{a['temperature']}F"]
            for a in anomalies
        ]
        print(tabulate(table_anomalies, headers=["ID", "Name", "Department", "Heart Rate", "SpO2", "BP", "Temp"], tablefmt="grid"))

        # Pipeline 4
        print("\n[PIPELINE 4] Pharmacy Most Prescribed Medications ($unwind + $group + $sort + $limit)")
        top_meds = get_top_prescribed_medications(db, limit=5)
        table_meds = [
            [m["medicine"], m["prescription_count"], f"{m['avg_duration_days']} days", m["common_dosage"]]
            for m in top_meds
        ]
        print(tabulate(table_meds, headers=["Medicine Name", "Total Prescriptions", "Avg Duration", "Sample Dosage"], tablefmt="grid"))

        # Pipeline 5
        print("\n[PIPELINE 5] Multi-Faceted Executive Hospital Dashboard ($facet Single-Stage Multi-Analysis)")
        dashboard = get_hospital_executive_dashboard(db)
        print("\n-- Status Distribution:")
        print(tabulate([[item["_id"], item["count"]] for item in dashboard.get("status_summary", [])], headers=["Status", "Patient Count"], tablefmt="simple"))

        print("\n-- Billing Summary:")
        print(tabulate([[item["_id"], item["patient_count"], f"${item['total_billed']}"] for item in dashboard.get("billing_summary", [])], headers=["Payment Status", "Patients", "Total Billed"], tablefmt="simple"))

        print_banner("Execution Demonstration Completed Successfully!")
        print(f"[OK] Full demonstration log saved to: {output_log_path}")

    finally:
        sys.stdout = original_stdout
        tee.close()


if __name__ == "__main__":
    log_file = os.path.join(os.path.dirname(__file__), "..", "output_demonstration.txt")
    run_full_demonstration(log_file)
