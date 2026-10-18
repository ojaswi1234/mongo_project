"""
Patient Data Model definition and validation helpers.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


class PatientModel:
    """
    Convenience wrapper to construct valid Patient documents conforming to the
    MongoDB $jsonSchema validator.
    """

    @staticmethod
    def build_document(
        patient_id: str,
        name: str,
        age: int,
        gender: str,
        blood_group: str,
        department: str,
        status: str,
        assigned_doctor_id: str,
        phone: str = "",
        email: str = "",
        emergency_contact: str = "",
        admission_date: Optional[datetime] = None,
        discharge_date: Optional[datetime] = None,
        vitals_history: Optional[List[Dict[str, Any]]] = None,
        medical_notes: Optional[List[str]] = None,
        prescriptions: Optional[List[Dict[str, Any]]] = None,
        room_charges: float = 0.0,
        consultation_fee: float = 0.0,
        medicine_charges: float = 0.0,
        payment_status: str = "Pending"
    ) -> Dict[str, Any]:
        """
        Builds a compliant MongoDB Patient document dictionary.
        """
        total_amount = float(room_charges + consultation_fee + medicine_charges)
        return {
            "patient_id": patient_id,
            "name": name,
            "age": int(age),
            "gender": gender,
            "blood_group": blood_group,
            "department": department,
            "status": status,
            "assigned_doctor_id": assigned_doctor_id,
            "contact": {
                "phone": phone,
                "email": email,
                "emergency_contact": emergency_contact
            },
            "admission_date": admission_date or datetime.now(),
            "discharge_date": discharge_date,
            "vitals_history": vitals_history or [],
            "medical_notes": medical_notes or [],
            "prescriptions": prescriptions or [],
            "billing": {
                "room_charges": float(room_charges),
                "consultation_fee": float(consultation_fee),
                "medicine_charges": float(medicine_charges),
                "total_amount": total_amount,
                "payment_status": payment_status
            }
        }
