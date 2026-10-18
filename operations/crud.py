"""
CRUD Operations for Smart Hospital MongoDB System.
Demonstrates Create, Read, Update, Delete queries using PyMongo,
including atomic array modifications, projection, and schema violation handling.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pymongo.errors import DuplicateKeyError, WriteError


# ==============================================================================
# 1. CREATE OPERATIONS
# ==============================================================================

from ai.vector_engine import generate_clinical_embedding
import re


def create_patient(db, patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inserts a new patient document into the 'patients' collection.
    MongoDB $jsonSchema validation is automatically enforced by the engine.
    Also computes and stores a 64-dim vector embedding for MongoDB Vector Search.
    """
    # Defensive programmatic validation for mock mode or client-side check
    patient_id = str(patient_data.get("patient_id", ""))
    age = patient_data.get("age")
    gender = patient_data.get("gender")

    if not re.match(r"^PAT-[0-9]{4}$", patient_id):
        return {
            "success": False,
            "error": f"Schema Validation Error: patient_id '{patient_id}' must match pattern '^PAT-[0-9]{4}$' (e.g. PAT-1001)."
        }
    if not isinstance(age, int) or age < 0 or age > 125:
        return {
            "success": False,
            "error": f"Schema Validation Error: age '{age}' must be an integer between 0 and 125."
        }
    if gender not in ["Male", "Female", "Other"]:
        return {
            "success": False,
            "error": f"Schema Validation Error: gender '{gender}' must be one of ['Male', 'Female', 'Other']."
        }

    # Automatically compute 64-dim clinical vector embedding if not present
    if "clinical_embedding" not in patient_data:
        notes = " ".join(patient_data.get("medical_notes", [])) + " " + patient_data.get("department", "")
        patient_data["clinical_embedding"] = generate_clinical_embedding(notes)

    try:
        result = db.patients.insert_one(patient_data)
        return {
            "success": True,
            "inserted_id": str(result.inserted_id),
            "patient_id": patient_data.get("patient_id")
        }
    except DuplicateKeyError as e:
        return {
            "success": False,
            "error": f"Duplicate Error: Patient with ID '{patient_data.get('patient_id')}' already exists in database."
        }
    except WriteError as e:
        return {
            "success": False,
            "error": f"Database Schema Validation Failed: {e.details.get('errmsg', str(e))}"
        }


def create_doctor(db, doctor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inserts a new doctor document into the 'doctors' collection.
    """
    try:
        result = db.doctors.insert_one(doctor_data)
        return {
            "success": True,
            "inserted_id": str(result.inserted_id),
            "doctor_id": doctor_data.get("doctor_id")
        }
    except DuplicateKeyError:
        return {"success": False, "error": f"Doctor ID '{doctor_data.get('doctor_id')}' already exists."}
    except WriteError as e:
        return {"success": False, "error": f"Validation Error: {str(e)}"}


# ==============================================================================
# 2. READ / QUERY OPERATIONS
# ==============================================================================

def get_patient_by_id(db, patient_id: str, projection: Optional[Dict[str, int]] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single patient by ID with optional projection to limit returned fields.
    Optimized via unique index on 'patient_id'.
    """
    return db.patients.find_one({"patient_id": patient_id}, projection)


def search_patients_advanced(
    db,
    department: Optional[str] = None,
    status: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    blood_group: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Performs dynamic filtered queries using MongoDB query operators ($gte, $lte, $eq).
    Demonstrates multi-attribute indexing support.
    """
    query: Dict[str, Any] = {}

    if department:
        query["department"] = department
    if status:
        query["status"] = status
    if blood_group:
        query["blood_group"] = blood_group

    age_filter: Dict[str, int] = {}
    if min_age is not None:
        age_filter["$gte"] = min_age
    if max_age is not None:
        age_filter["$lte"] = max_age
    if age_filter:
        query["age"] = age_filter

    projection = {
        "_id": 0,
        "patient_id": 1,
        "name": 1,
        "age": 1,
        "gender": 1,
        "department": 1,
        "status": 1,
        "blood_group": 1,
        "billing.total_amount": 1,
        "billing.payment_status": 1
    }

    return list(db.patients.find(query, projection))


def find_patients_by_diagnosis_keyword(db, keyword: str) -> List[Dict[str, Any]]:
    """
    Searches patients where 'medical_notes' array contains strings matching the keyword regex.
    Demonstrates querying array elements in MongoDB.
    """
    query = {"medical_notes": {"$regex": keyword, "$options": "i"}}
    projection = {
        "_id": 0,
        "patient_id": 1,
        "name": 1,
        "department": 1,
        "medical_notes": 1
    }
    return list(db.patients.find(query, projection))


def find_patients_with_vitals_alert(db, min_heart_rate: int = 100, max_oxygen: int = 95) -> List[Dict[str, Any]]:
    """
    Demonstrates $elemMatch on embedded array of documents:
    Finds patients who had at least one recorded vital check where BOTH:
    heart_rate >= min_heart_rate AND oxygen_level <= max_oxygen simultaneously!
    """
    query = {
        "vitals_history": {
            "$elemMatch": {
                "heart_rate": {"$gte": min_heart_rate},
                "oxygen_level": {"$lte": max_oxygen}
            }
        }
    }
    projection = {
        "_id": 0,
        "patient_id": 1,
        "name": 1,
        "department": 1,
        "status": 1,
        "vitals_history": 1
    }
    return list(db.patients.find(query, projection))


# ==============================================================================
# 3. UPDATE OPERATIONS
# ==============================================================================

def update_patient_status(db, patient_id: str, new_status: str) -> Dict[str, Any]:
    """
    Updates patient admission/discharge status using $set.
    If status is 'Discharged', automatically sets discharge_date to current timestamp.
    """
    update_fields: Dict[str, Any] = {"status": new_status}
    if new_status == "Discharged":
        update_fields["discharge_date"] = datetime.now()

    result = db.patients.update_one(
        {"patient_id": patient_id},
        {"$set": update_fields}
    )
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "success": result.modified_count > 0
    }


def add_patient_vital_reading(db, patient_id: str, vital_reading: Dict[str, Any]) -> Dict[str, Any]:
    """
    Appends a new vital sign measurement to the embedded 'vitals_history' array using $push.
    Ensures zero downtime and avoids updating the whole document.
    """
    if "timestamp" not in vital_reading:
        vital_reading["timestamp"] = datetime.now()

    result = db.patients.update_one(
        {"patient_id": patient_id},
        {"$push": {"vitals_history": vital_reading}}
    )
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "success": result.modified_count > 0
    }


def add_prescription_to_patient(db, patient_id: str, prescription: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds a new medication to the 'prescriptions' array using $addToSet to avoid duplicates.
    """
    result = db.patients.update_one(
        {"patient_id": patient_id},
        {"$addToSet": {"prescriptions": prescription}}
    )
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "success": result.modified_count > 0
    }


def update_billing_charges(
    db,
    patient_id: str,
    additional_room_charge: float = 0.0,
    additional_medicine_charge: float = 0.0,
    new_payment_status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Demonstrates $inc (atomic numeric increment) and $set combined in an update.
    """
    inc_dict: Dict[str, float] = {}
    if additional_room_charge > 0:
        inc_dict["billing.room_charges"] = additional_room_charge
        inc_dict["billing.total_amount"] = additional_room_charge
    if additional_medicine_charge > 0:
        inc_dict["billing.medicine_charges"] = additional_medicine_charge
        inc_dict["billing.total_amount"] = (
            inc_dict.get("billing.total_amount", 0.0) + additional_medicine_charge
        )

    update_doc: Dict[str, Any] = {}
    if inc_dict:
        update_doc["$inc"] = inc_dict
    if new_payment_status:
        update_doc["$set"] = {"billing.payment_status": new_payment_status}

    if not update_doc:
        return {"matched_count": 0, "modified_count": 0, "success": False}

    result = db.patients.update_one({"patient_id": patient_id}, update_doc)
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "success": result.modified_count > 0
    }


# ==============================================================================
# 4. DELETE OPERATIONS
# ==============================================================================

def soft_delete_patient(db, patient_id: str) -> Dict[str, Any]:
    """
    Soft delete (Logical Deletion): Marks patient as 'Archived' instead of permanently
    dropping data. Demonstrates clinical regulatory compliance (HIPAA/audit-trail requirement).
    """
    result = db.patients.update_one(
        {"patient_id": patient_id},
        {"$set": {"is_archived": True, "status": "Archived", "archived_at": datetime.now()}}
    )
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "success": result.modified_count > 0
    }


def hard_delete_patient(db, patient_id: str) -> Dict[str, Any]:
    """
    Hard delete: Physically removes the document using delete_one.
    """
    result = db.patients.delete_one({"patient_id": patient_id})
    return {
        "deleted_count": result.deleted_count,
        "success": result.deleted_count > 0
    }
