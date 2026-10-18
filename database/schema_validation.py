"""
MongoDB Schema Validation Rules using $jsonSchema.
Enforces data integrity, required fields, data types, and range constraints
directly at the MongoDB database level.
"""

from typing import Dict, Any


def get_patient_validator() -> Dict[str, Any]:
    """
    Returns the $jsonSchema validator for the 'patients' collection.
    Enforces strict BSON types, required fields, enums, and nested structures.
    """
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "patient_id",
                "name",
                "age",
                "gender",
                "blood_group",
                "department",
                "status",
                "assigned_doctor_id",
                "billing"
            ],
            "properties": {
                "patient_id": {
                    "bsonType": "string",
                    "pattern": "^PAT-[0-9]{4}$",
                    "description": "Unique patient identifier in format PAT-XXXX (required)"
                },
                "name": {
                    "bsonType": "string",
                    "minLength": 2,
                    "maxLength": 100,
                    "description": "Full name of the patient (required string)"
                },
                "age": {
                    "bsonType": "int",
                    "minimum": 0,
                    "maximum": 125,
                    "description": "Patient age in years (integer 0-125)"
                },
                "gender": {
                    "enum": ["Male", "Female", "Other"],
                    "description": "Gender must be Male, Female, or Other"
                },
                "blood_group": {
                    "enum": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                    "description": "Standard blood group type"
                },
                "department": {
                    "enum": [
                        "Cardiology",
                        "Neurology",
                        "Orthopedics",
                        "General Medicine",
                        "Pediatrics",
                        "Oncology"
                    ],
                    "description": "Assigned hospital department"
                },
                "status": {
                    "enum": ["Admitted", "Discharged", "Under Observation", "Outpatient"],
                    "description": "Current patient status in hospital"
                },
                "assigned_doctor_id": {
                    "bsonType": "string",
                    "pattern": "^DOC-[0-9]{3}$",
                    "description": "Referenced Doctor ID in format DOC-XXX"
                },
                "vitals_history": {
                    "bsonType": "array",
                    "description": "Embedded list of vital sign measurements",
                    "items": {
                        "bsonType": "object",
                        "required": ["timestamp", "heart_rate", "blood_pressure", "oxygen_level"],
                        "properties": {
                            "timestamp": {
                                "bsonType": "date",
                                "description": "Date and time of vitals recording"
                            },
                            "blood_pressure": {
                                "bsonType": "string",
                                "description": "BP measurement e.g., 120/80"
                            },
                            "heart_rate": {
                                "bsonType": "int",
                                "minimum": 30,
                                "maximum": 240,
                                "description": "Pulse in BPM"
                            },
                            "temperature": {
                                "bsonType": ["double", "int"],
                                "minimum": 90.0,
                                "maximum": 110.0,
                                "description": "Body temperature in Fahrenheit"
                            },
                            "oxygen_level": {
                                "bsonType": "int",
                                "minimum": 50,
                                "maximum": 100,
                                "description": "SpO2 percentage (50-100)"
                            }
                        }
                    }
                },
                "prescriptions": {
                    "bsonType": "array",
                    "description": "Embedded array of active prescriptions",
                    "items": {
                        "bsonType": "object",
                        "required": ["medicine", "dosage", "frequency", "days"],
                        "properties": {
                            "medicine": {"bsonType": "string"},
                            "dosage": {"bsonType": "string"},
                            "frequency": {"bsonType": "string"},
                            "days": {"bsonType": "int", "minimum": 1}
                        }
                    }
                },
                "billing": {
                    "bsonType": "object",
                    "required": ["room_charges", "consultation_fee", "medicine_charges", "total_amount", "payment_status"],
                    "properties": {
                        "room_charges": {"bsonType": ["double", "int"]},
                        "consultation_fee": {"bsonType": ["double", "int"]},
                        "medicine_charges": {"bsonType": ["double", "int"]},
                        "total_amount": {"bsonType": ["double", "int"]},
                        "payment_status": {
                            "enum": ["Paid", "Pending", "Partially Paid", "Insurance Claimed"]
                        }
                    }
                }
            }
        }
    }


def get_doctor_validator() -> Dict[str, Any]:
    """
    Returns the $jsonSchema validator for the 'doctors' collection.
    """
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["doctor_id", "name", "specialization", "department", "experience_years", "consultation_fee"],
            "properties": {
                "doctor_id": {
                    "bsonType": "string",
                    "pattern": "^DOC-[0-9]{3}$",
                    "description": "Unique doctor code format DOC-XXX"
                },
                "name": {"bsonType": "string", "minLength": 2},
                "specialization": {"bsonType": "string"},
                "department": {"bsonType": "string"},
                "experience_years": {"bsonType": "int", "minimum": 0, "maximum": 60},
                "consultation_fee": {"bsonType": ["double", "int"], "minimum": 0},
                "ratings": {"bsonType": ["double", "int"], "minimum": 0, "maximum": 5}
            }
        }
    }


def apply_schema_validations(db, is_mock: bool = False) -> None:
    """
    Applies or updates collection validation rules and creates indexes in MongoDB.
    """
    if is_mock:
        print("[*] Mock Mode: Schema validators noted (mock skips server-side collMod).")
        return

    # Apply Patient Validator
    existing_collections = db.list_collection_names()
    patient_validator = get_patient_validator()
    doctor_validator = get_doctor_validator()

    if "patients" not in existing_collections:
        db.create_collection("patients", validator=patient_validator)
        print("[✓] Created 'patients' collection with $jsonSchema validation.")
    else:
        db.command({
            "collMod": "patients",
            "validator": patient_validator,
            "validationLevel": "moderate"
        })
        print("[✓] Updated 'patients' collection with $jsonSchema validation.")

    # Apply Doctor Validator
    if "doctors" not in existing_collections:
        db.create_collection("doctors", validator=doctor_validator)
        print("[✓] Created 'doctors' collection with $jsonSchema validation.")
    else:
        db.command({
            "collMod": "doctors",
            "validator": doctor_validator,
            "validationLevel": "moderate"
        })
        print("[✓] Updated 'doctors' collection with $jsonSchema validation.")

    # Apply Indexes
    db.patients.create_index("patient_id", unique=True)
    db.patients.create_index([("department", 1), ("status", 1)])
    db.patients.create_index("vitals_history.heart_rate")
    db.doctors.create_index("doctor_id", unique=True)
    print("[✓] Created MongoDB Indexes (Unique, Compound, Multikey).")
