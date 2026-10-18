"""
Seed dataset for Smart Hospital MongoDB System.
Populates realistic hospital data for doctors, patients, and departments.
"""

from datetime import datetime, timedelta
from typing import Dict, Any


def get_seed_doctors():
    return [
        {
            "doctor_id": "DOC-201",
            "name": "Dr. Sarah Jenkins",
            "specialization": "Chief Cardiologist",
            "department": "Cardiology",
            "experience_years": 16,
            "consultation_fee": 150.0,
            "contact": {"phone": "+1-555-0191", "email": "sjenkins@smarthospital.org"},
            "available_days": ["Monday", "Wednesday", "Friday"],
            "ratings": 4.9
        },
        {
            "doctor_id": "DOC-202",
            "name": "Dr. Rajesh Sharma",
            "specialization": "Senior Neurologist",
            "department": "Neurology",
            "experience_years": 14,
            "consultation_fee": 160.0,
            "contact": {"phone": "+1-555-0192", "email": "rsharma@smarthospital.org"},
            "available_days": ["Tuesday", "Thursday", "Saturday"],
            "ratings": 4.8
        },
        {
            "doctor_id": "DOC-203",
            "name": "Dr. Emily Taylor",
            "specialization": "Orthopedic Surgeon",
            "department": "Orthopedics",
            "experience_years": 11,
            "consultation_fee": 130.0,
            "contact": {"phone": "+1-555-0193", "email": "etaylor@smarthospital.org"},
            "available_days": ["Monday", "Tuesday", "Thursday"],
            "ratings": 4.7
        },
        {
            "doctor_id": "DOC-204",
            "name": "Dr. Marcus Vance",
            "specialization": "Lead Pediatrician",
            "department": "Pediatrics",
            "experience_years": 9,
            "consultation_fee": 110.0,
            "contact": {"phone": "+1-555-0194", "email": "mvance@smarthospital.org"},
            "available_days": ["Monday", "Wednesday", "Thursday", "Friday"],
            "ratings": 4.9
        },
        {
            "doctor_id": "DOC-205",
            "name": "Dr. Anita Desai",
            "specialization": "Consultant Physician",
            "department": "General Medicine",
            "experience_years": 12,
            "consultation_fee": 95.0,
            "contact": {"phone": "+1-555-0195", "email": "adesai@smarthospital.org"},
            "available_days": ["Monday", "Tuesday", "Wednesday", "Friday"],
            "ratings": 4.6
        }
    ]


def get_seed_departments():
    return [
        {
            "department_id": "DEP-01",
            "department_name": "Cardiology",
            "head_doctor": "Dr. Sarah Jenkins",
            "floor": 3,
            "total_beds": 30,
            "occupied_beds": 22
        },
        {
            "department_id": "DEP-02",
            "department_name": "Neurology",
            "head_doctor": "Dr. Rajesh Sharma",
            "floor": 4,
            "total_beds": 25,
            "occupied_beds": 18
        },
        {
            "department_id": "DEP-03",
            "department_name": "Orthopedics",
            "head_doctor": "Dr. Emily Taylor",
            "floor": 2,
            "total_beds": 20,
            "occupied_beds": 14
        },
        {
            "department_id": "DEP-04",
            "department_name": "General Medicine",
            "head_doctor": "Dr. Anita Desai",
            "floor": 1,
            "total_beds": 40,
            "occupied_beds": 31
        }
    ]


def get_seed_patients():
    now = datetime.now()
    return [
        {
            "patient_id": "PAT-1001",
            "name": "Robert Miller",
            "age": 62,
            "gender": "Male",
            "blood_group": "A+",
            "contact": {
                "phone": "+1-555-1001",
                "email": "rmiller@gmail.com",
                "emergency_contact": "Mary Miller (+1-555-1002)"
            },
            "department": "Cardiology",
            "status": "Admitted",
            "assigned_doctor_id": "DOC-201",
            "admission_date": now - timedelta(days=4),
            "discharge_date": None,
            "vitals_history": [
                {
                    "timestamp": now - timedelta(days=3),
                    "blood_pressure": "145/95",
                    "heart_rate": 105,
                    "temperature": 99.1,
                    "oxygen_level": 94
                },
                {
                    "timestamp": now - timedelta(days=2),
                    "blood_pressure": "135/88",
                    "heart_rate": 88,
                    "temperature": 98.6,
                    "oxygen_level": 96
                },
                {
                    "timestamp": now - timedelta(hours=6),
                    "blood_pressure": "128/82",
                    "heart_rate": 78,
                    "temperature": 98.4,
                    "oxygen_level": 98
                }
            ],
            "medical_notes": ["History of hypertension", "Angioplasty recommended"],
            "prescriptions": [
                {"medicine": "Atorvastatin", "dosage": "20mg", "frequency": "Once daily at night", "days": 30},
                {"medicine": "Metoprolol", "dosage": "50mg", "frequency": "Twice daily", "days": 15}
            ],
            "billing": {
                "room_charges": 1600.0,
                "consultation_fee": 450.0,
                "medicine_charges": 280.0,
                "total_amount": 2330.0,
                "payment_status": "Partially Paid"
            }
        },
        {
            "patient_id": "PAT-1002",
            "name": "Sophia Chen",
            "age": 45,
            "gender": "Female",
            "blood_group": "B+",
            "contact": {
                "phone": "+1-555-1003",
                "email": "schen@yahoo.com",
                "emergency_contact": "Kevin Chen (+1-555-1004)"
            },
            "department": "Neurology",
            "status": "Admitted",
            "assigned_doctor_id": "DOC-202",
            "admission_date": now - timedelta(days=2),
            "discharge_date": None,
            "vitals_history": [
                {
                    "timestamp": now - timedelta(days=1),
                    "blood_pressure": "125/80",
                    "heart_rate": 82,
                    "temperature": 98.7,
                    "oxygen_level": 97
                },
                {
                    "timestamp": now - timedelta(hours=4),
                    "blood_pressure": "120/78",
                    "heart_rate": 74,
                    "temperature": 98.6,
                    "oxygen_level": 99
                }
            ],
            "medical_notes": ["Chronic migraine aura", "MRI brain completed with normal findings"],
            "prescriptions": [
                {"medicine": "Sumatriptan", "dosage": "50mg", "frequency": "As needed", "days": 10},
                {"medicine": "Propranolol", "dosage": "40mg", "frequency": "Once daily", "days": 60}
            ],
            "billing": {
                "room_charges": 800.0,
                "consultation_fee": 320.0,
                "medicine_charges": 190.0,
                "total_amount": 1310.0,
                "payment_status": "Paid"
            }
        },
        {
            "patient_id": "PAT-1003",
            "name": "David Wilson",
            "age": 71,
            "gender": "Male",
            "blood_group": "O+",
            "contact": {
                "phone": "+1-555-1005",
                "email": "dwilson@outlook.com",
                "emergency_contact": "Susan Wilson (+1-555-1006)"
            },
            "department": "Orthopedics",
            "status": "Admitted",
            "assigned_doctor_id": "DOC-203",
            "admission_date": now - timedelta(days=6),
            "discharge_date": None,
            "vitals_history": [
                {
                    "timestamp": now - timedelta(days=5),
                    "blood_pressure": "138/85",
                    "heart_rate": 92,
                    "temperature": 100.2,
                    "oxygen_level": 95
                },
                {
                    "timestamp": now - timedelta(days=1),
                    "blood_pressure": "130/80",
                    "heart_rate": 80,
                    "temperature": 98.8,
                    "oxygen_level": 97
                }
            ],
            "medical_notes": ["Total knee replacement post-op day 3", "Physiotherapy ongoing"],
            "prescriptions": [
                {"medicine": "Enoxaparin", "dosage": "40mg", "frequency": "Subcutaneous daily", "days": 14},
                {"medicine": "Tramadol", "dosage": "50mg", "frequency": "Twice daily", "days": 7}
            ],
            "billing": {
                "room_charges": 2400.0,
                "consultation_fee": 650.0,
                "medicine_charges": 890.0,
                "total_amount": 3940.0,
                "payment_status": "Insurance Claimed"
            }
        },
        {
            "patient_id": "PAT-1004",
            "name": "Amina Morales",
            "age": 28,
            "gender": "Female",
            "blood_group": "AB+",
            "contact": {
                "phone": "+1-555-1007",
                "email": "amorales@gmail.com",
                "emergency_contact": "Carlos Morales (+1-555-1008)"
            },
            "department": "General Medicine",
            "status": "Discharged",
            "assigned_doctor_id": "DOC-205",
            "admission_date": now - timedelta(days=7),
            "discharge_date": now - timedelta(days=1),
            "vitals_history": [
                {
                    "timestamp": now - timedelta(days=6),
                    "blood_pressure": "118/75",
                    "heart_rate": 115,
                    "temperature": 102.4,
                    "oxygen_level": 95
                },
                {
                    "timestamp": now - timedelta(days=2),
                    "blood_pressure": "115/72",
                    "heart_rate": 72,
                    "temperature": 98.4,
                    "oxygen_level": 99
                }
            ],
            "medical_notes": ["Acute gastroenteritis fully resolved", "Patient discharged safely"],
            "prescriptions": [
                {"medicine": "Ciprofloxacin", "dosage": "500mg", "frequency": "Twice daily", "days": 5},
                {"medicine": "ORS Solution", "dosage": "1 packet", "frequency": "As needed", "days": 3}
            ],
            "billing": {
                "room_charges": 1200.0,
                "consultation_fee": 285.0,
                "medicine_charges": 140.0,
                "total_amount": 1625.0,
                "payment_status": "Paid"
            }
        },
        {
            "patient_id": "PAT-1005",
            "name": "Ethan Wright",
            "age": 53,
            "gender": "Male",
            "blood_group": "O-",
            "contact": {
                "phone": "+1-555-1009",
                "email": "ewright@corp.com",
                "emergency_contact": "Laura Wright (+1-555-1010)"
            },
            "department": "Cardiology",
            "status": "Under Observation",
            "assigned_doctor_id": "DOC-201",
            "admission_date": now - timedelta(hours=14),
            "discharge_date": None,
            "vitals_history": [
                {
                    "timestamp": now - timedelta(hours=12),
                    "blood_pressure": "155/100",
                    "heart_rate": 118,
                    "temperature": 98.6,
                    "oxygen_level": 93
                },
                {
                    "timestamp": now - timedelta(hours=2),
                    "blood_pressure": "140/90",
                    "heart_rate": 96,
                    "temperature": 98.5,
                    "oxygen_level": 95
                }
            ],
            "medical_notes": ["Suspected unstable angina", "Troponin I levels borderline elevated"],
            "prescriptions": [
                {"medicine": "Aspirin", "dosage": "75mg", "frequency": "Once daily", "days": 30},
                {"medicine": "Nitroglycerin", "dosage": "0.4mg", "frequency": "Sublingual as needed", "days": 10}
            ],
            "billing": {
                "room_charges": 500.0,
                "consultation_fee": 150.0,
                "medicine_charges": 110.0,
                "total_amount": 760.0,
                "payment_status": "Pending"
            }
        },
        {
            "patient_id": "PAT-1006",
            "name": "Maria Garcia",
            "age": 34,
            "gender": "Female",
            "blood_group": "A-",
            "contact": {
                "phone": "+1-555-1011",
                "email": "mgarcia@gmail.com",
                "emergency_contact": "Elena Garcia (+1-555-1012)"
            },
            "department": "General Medicine",
            "status": "Admitted",
            "assigned_doctor_id": "DOC-205",
            "admission_date": now - timedelta(days=3),
            "discharge_date": None,
            "vitals_history": [
                {
                    "timestamp": now - timedelta(days=2),
                    "blood_pressure": "110/70",
                    "heart_rate": 78,
                    "temperature": 101.5,
                    "oxygen_level": 96
                },
                {
                    "timestamp": now - timedelta(hours=8),
                    "blood_pressure": "112/74",
                    "heart_rate": 72,
                    "temperature": 99.0,
                    "oxygen_level": 98
                }
            ],
            "medical_notes": ["Bacterial pneumonia responding well to IV antibiotics"],
            "prescriptions": [
                {"medicine": "Ceftriaxone", "dosage": "1g", "frequency": "IV daily", "days": 7},
                {"medicine": "Paracetamol", "dosage": "650mg", "frequency": "SOS", "days": 5}
            ],
            "billing": {
                "room_charges": 900.0,
                "consultation_fee": 285.0,
                "medicine_charges": 350.0,
                "total_amount": 1535.0,
                "payment_status": "Partially Paid"
            }
        },
        {
            "patient_id": "PAT-1007",
            "name": "Liam Johnson",
            "age": 19,
            "gender": "Male",
            "blood_group": "B-",
            "contact": {
                "phone": "+1-555-1013",
                "email": "ljohnson@college.edu",
                "emergency_contact": "Mark Johnson (+1-555-1014)"
            },
            "department": "Orthopedics",
            "status": "Discharged",
            "admission_date": now - timedelta(days=10),
            "discharge_date": now - timedelta(days=2),
            "assigned_doctor_id": "DOC-203",
            "vitals_history": [
                {
                    "timestamp": now - timedelta(days=9),
                    "blood_pressure": "120/80",
                    "heart_rate": 68,
                    "temperature": 98.4,
                    "oxygen_level": 99
                }
            ],
            "medical_notes": ["Fracture of distal radius - cast applied, healed properly"],
            "prescriptions": [
                {"medicine": "Ibuprofen", "dosage": "400mg", "frequency": "Twice daily after meals", "days": 5},
                {"medicine": "Calcium + Vitamin D3", "dosage": "500mg", "frequency": "Once daily", "days": 30}
            ],
            "billing": {
                "room_charges": 600.0,
                "consultation_fee": 260.0,
                "medicine_charges": 120.0,
                "total_amount": 980.0,
                "payment_status": "Paid"
            }
        },
        {
            "patient_id": "PAT-1008",
            "name": "Pooja Patel",
            "age": 39,
            "gender": "Female",
            "blood_group": "AB-",
            "contact": {
                "phone": "+1-555-1015",
                "email": "ppatel@tech.com",
                "emergency_contact": "Amit Patel (+1-555-1016)"
            },
            "department": "Neurology",
            "status": "Under Observation",
            "assigned_doctor_id": "DOC-202",
            "admission_date": now - timedelta(hours=18),
            "discharge_date": None,
            "vitals_history": [
                {
                    "timestamp": now - timedelta(hours=16),
                    "blood_pressure": "130/82",
                    "heart_rate": 84,
                    "temperature": 98.6,
                    "oxygen_level": 98
                }
            ],
            "medical_notes": ["Vertigo and dizziness episodes under diagnostic assessment"],
            "prescriptions": [
                {"medicine": "Betahistine", "dosage": "16mg", "frequency": "Three times daily", "days": 14}
            ],
            "billing": {
                "room_charges": 400.0,
                "consultation_fee": 160.0,
                "medicine_charges": 80.0,
                "total_amount": 640.0,
                "payment_status": "Pending"
            }
        }
    ]


from ai.vector_engine import generate_clinical_embedding


def populate_seed_data(db, drop_existing: bool = True):
    """
    Populates sample seed records into the database with pre-computed vector embeddings.
    """
    if drop_existing:
        db.doctors.delete_many({})
        db.departments.delete_many({})
        db.patients.delete_many({})

    doctors = get_seed_doctors()
    departments = get_seed_departments()
    patients = get_seed_patients()

    # Pre-generate vector embeddings for each patient document
    for p in patients:
        notes_str = " ".join(p.get("medical_notes", [])) + " " + p.get("department", "")
        p["clinical_embedding"] = generate_clinical_embedding(notes_str)

    db.doctors.insert_many(doctors)
    db.departments.insert_many(departments)
    db.patients.insert_many(patients)

    return {
        "doctors_inserted": len(doctors),
        "departments_inserted": len(departments),
        "patients_inserted": len(patients)
    }
