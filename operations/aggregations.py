"""
MongoDB Aggregation Pipelines for Smart Hospital System.
Demonstrates multi-stage pipelines using PyMongo:
$match, $group, $sort, $project, $unwind, $lookup, and $facet.
"""

from typing import List, Dict, Any


def get_department_analytics(db) -> List[Dict[str, Any]]:
    """
    Pipeline 1: Department-wise Patient Count, Demographics & Financial Revenue.
    Stages:
      1. $match   - Filter out archived records.
      2. $group   - Group by 'department', compute metrics (count, avg age, financial aggregates).
      3. $project - Format output, round numbers, rename fields.
      4. $sort    - Sort by total revenue descending.
    """
    pipeline = [
        {
            "$match": {
                "status": {"$ne": "Archived"}
            }
        },
        {
            "$group": {
                "_id": "$department",
                "total_patients": {"$sum": 1},
                "average_age": {"$avg": "$age"},
                "total_revenue": {"$sum": "$billing.total_amount"},
                "avg_bill_amount": {"$avg": "$billing.total_amount"},
                "max_bill_amount": {"$max": "$billing.total_amount"},
                "min_bill_amount": {"$min": "$billing.total_amount"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "department": "$_id",
                "total_patients": 1,
                "average_age": 1,
                "total_revenue": 1,
                "avg_bill_amount": 1,
                "max_bill_amount": 1,
                "min_bill_amount": 1
            }
        },
        {
            "$sort": {"total_revenue": -1}
        }
    ]
    return list(db.patients.aggregate(pipeline))


def get_doctor_workload_analytics(db) -> List[Dict[str, Any]]:
    """
    Pipeline 2: Doctor Workload & Patient Revenue Association ($lookup).
    Demonstrates referencing resolution (JOIN) between 'doctors' and 'patients'.
    Stages:
      1. $lookup  - Join 'patients' collection on doctor_id == assigned_doctor_id.
      2. $project - Calculate total assigned patients, calculate total patient billing.
      3. $sort    - Sort doctors by total patient count descending.
    """
    pipeline = [
        {
            "$lookup": {
                "from": "patients",
                "localField": "doctor_id",
                "foreignField": "assigned_doctor_id",
                "as": "patient_records"
            }
        },
        {
            "$project": {
                "_id": 0,
                "doctor_id": 1,
                "doctor_name": "$name",
                "specialization": 1,
                "department": 1,
                "experience_years": 1,
                "consultation_fee": 1,
                "ratings": 1,
                "patient_count": {"$size": "$patient_records"},
                "total_generated_revenue": {
                    "$sum": "$patient_records.billing.total_amount"
                }
            }
        },
        {
            "$sort": {"patient_count": -1, "ratings": -1}
        }
    ]
    return list(db.doctors.aggregate(pipeline))


def get_critical_vitals_anomalies(
    db,
    min_heart_rate: int = 100,
    max_oxygen: int = 95
) -> List[Dict[str, Any]]:
    """
    Pipeline 3: Clinical Critical Vitals Anomaly Detection ($unwind).
    Flattens the embedded 'vitals_history' array to inspect individual historical readings.
    Stages:
      1. $unwind  - Deconstructs 'vitals_history' array.
      2. $match   - Filters vital records where heart_rate >= min_heart_rate OR oxygen_level <= max_oxygen.
      3. $project - Formats the patient and vital reading details.
      4. $sort    - Sorts by severity (heart_rate descending).
    """
    pipeline = [
        {
            "$unwind": "$vitals_history"
        },
        {
            "$match": {
                "$or": [
                    {"vitals_history.heart_rate": {"$gte": min_heart_rate}},
                    {"vitals_history.oxygen_level": {"$lte": max_oxygen}}
                ]
            }
        },
        {
            "$project": {
                "_id": 0,
                "patient_id": 1,
                "patient_name": "$name",
                "department": 1,
                "timestamp": "$vitals_history.timestamp",
                "blood_pressure": "$vitals_history.blood_pressure",
                "heart_rate": "$vitals_history.heart_rate",
                "oxygen_level": "$vitals_history.oxygen_level",
                "temperature": "$vitals_history.temperature"
            }
        },
        {
            "$sort": {"heart_rate": -1}
        }
    ]
    return list(db.patients.aggregate(pipeline))


def get_top_prescribed_medications(db, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Pipeline 4: Pharmacy Inventory & Medication Frequency Analysis ($unwind + $group).
    Stages:
      1. $unwind  - Flattens 'prescriptions' embedded array.
      2. $group   - Groups by medicine name, counts prescriptions, averages dosage duration.
      3. $sort    - Sorts by total prescriptions descending.
      4. $limit   - Returns top N prescribed medications.
    """
    pipeline = [
        {
            "$unwind": "$prescriptions"
        },
        {
            "$group": {
                "_id": "$prescriptions.medicine",
                "prescription_count": {"$sum": 1},
                "avg_duration_days": {"$avg": "$prescriptions.days"},
                "common_dosage": {"$first": "$prescriptions.dosage"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "medicine": "$_id",
                "prescription_count": 1,
                "avg_duration_days": 1,
                "common_dosage": 1
            }
        },
        {
            "$sort": {"prescription_count": -1}
        },
        {
            "$limit": limit
        }
    ]
    return list(db.patients.aggregate(pipeline))


def get_hospital_executive_dashboard(db) -> Dict[str, Any]:
    """
    Pipeline 5: Multi-Faceted Executive KPI Dashboard using $facet.
    Runs multiple aggregation pipelines within a single stage on the same dataset.
    Sub-pipelines:
      1. status_summary: Bed allocation by status (Admitted, Discharged, Observation).
      2. billing_summary: Distribution of payments (Paid, Pending, Insurance Claimed).
      3. age_demographics: Age groups and average expenditure.
    """
    pipeline = [
        {
            "$facet": {
                "status_summary": [
                    {
                        "$group": {
                            "_id": "$status",
                            "count": {"$sum": 1}
                        }
                    },
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
                ],
                "gender_breakdown": [
                    {
                        "$group": {
                            "_id": "$gender",
                            "count": {"$sum": 1},
                            "avg_age": {"$avg": "$age"}
                        }
                    }
                ]
            }
        }
    ]
    results = list(db.patients.aggregate(pipeline))
    return results[0] if results else {}
