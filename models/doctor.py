"""
Doctor Data Model definition and helper.
"""

from typing import Dict, List, Optional, Any


class DoctorModel:
    """
    Convenience wrapper to construct valid Doctor documents.
    """

    @staticmethod
    def build_document(
        doctor_id: str,
        name: str,
        specialization: str,
        department: str,
        experience_years: int,
        consultation_fee: float,
        phone: str = "",
        email: str = "",
        available_days: Optional[List[str]] = None,
        ratings: float = 5.0
    ) -> Dict[str, Any]:
        return {
            "doctor_id": doctor_id,
            "name": name,
            "specialization": specialization,
            "department": department,
            "experience_years": int(experience_years),
            "consultation_fee": float(consultation_fee),
            "contact": {
                "phone": phone,
                "email": email
            },
            "available_days": available_days or ["Monday", "Wednesday", "Friday"],
            "ratings": float(ratings)
        }
