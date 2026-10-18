"""
MongoDB Vector Search & AI Clinical Assistant Engine.
Implements vector embeddings, cosine similarity search, MongoDB Atlas $vectorSearch
pipeline synthesis, and AI diagnostic insights.
"""

import re
import numpy as np
from typing import List, Dict, Any, Tuple

# Vector Dimension for Clinical Semantic Embeddings
VECTOR_DIMENSION = 64

# Clinical Domain Concept Anchors (Vocabulary mappings to semantic clusters)
CLINICAL_CLUSTERS = {
    # Cluster 0-11: Cardiology / Vascular
    "cardio": [
        "heart", "cardiac", "angina", "hypertension", "bp", "blood pressure",
        "pulse", "tachycardia", "chest pain", "angioplasty", "artery", "troponin",
        "palpitation", "myocardial", "infarction", "atorvastatin", "metoprolol"
    ],
    # Cluster 12-23: Neurology / Brain / Sensory
    "neuro": [
        "migraine", "headache", "brain", "neurological", "aura", "seizure",
        "mri", "vertigo", "dizziness", "nerve", "sumatriptan", "propranolol",
        "betahistine", "cranial", "syncope", "stroke"
    ],
    # Cluster 24-35: Orthopedics / Musculoskeletal
    "ortho": [
        "knee", "joint", "bone", "fracture", "replacement", "post-op", "physiotherapy",
        "enoxaparin", "tramadol", "radius", "cast", "orthopedic", "pain", "swelling",
        "arthritis", "ligament", "ibuprofen"
    ],
    # Cluster 36-47: Pulmonology / Respiratory
    "pulmo": [
        "pneumonia", "respiratory", "oxygen", "spo2", "lungs", "cough", "breath",
        "dyspnea", "antibiotic", "ceftriaxone", "inhaler", "fever", "chills", "hypoxemia"
    ],
    # Cluster 48-55: Gastroenterology / Infection / General Medicine
    "gastro": [
        "gastroenteritis", "stomach", "vomiting", "diarrhea", "infection", "fever",
        "ciprofloxacin", "hydration", "ors", "paracetamol", "nausea", "abdomen"
    ],
    # Cluster 56-63: Vitals & Severity Markers
    "severity": [
        "critical", "emergency", "observation", "admitted", "acute", "severe",
        "high risk", "unstable", "elevated", "abnormal"
    ]
}


def _hash_token_to_subvector(token: str, seed: int, dim: int = 8) -> np.ndarray:
    """Deterministically generates a normalized pseudo-random feature subvector."""
    rng = np.random.default_rng(abs(hash(token) + seed) % (2**32))
    vec = rng.standard_normal(dim)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def generate_clinical_embedding(text: str) -> List[float]:
    """
    Generates a 64-dimensional dense semantic vector embedding for medical text.
    Combines concept cluster weights with subvector projections.
    Returns:
        List of 64 floats (normalized to unit Euclidean length L2 = 1.0).
    """
    if not text:
        return [0.0] * VECTOR_DIMENSION

    tokens = [t.lower() for t in re.findall(r"\b[a-zA-Z0-9\-\+]+\b", text)]
    if not tokens:
        return [0.0] * VECTOR_DIMENSION

    dense_vector = np.zeros(VECTOR_DIMENSION, dtype=np.float64)

    # Base semantic concept weighting across clusters
    cluster_offsets = {
        "cardio": (0, 12),
        "neuro": (12, 24),
        "ortho": (24, 36),
        "pulmo": (36, 48),
        "gastro": (48, 56),
        "severity": (56, 64)
    }

    matched_tokens = 0
    for token in tokens:
        for cluster_name, keywords in CLINICAL_CLUSTERS.items():
            start_idx, end_idx = cluster_offsets[cluster_name]
            dim_span = end_idx - start_idx
            if any(token in kw or kw in token for kw in keywords):
                matched_tokens += 1
                # Project into this domain's subspace
                subvec = _hash_token_to_subvector(token, seed=start_idx, dim=dim_span)
                dense_vector[start_idx:end_idx] += subvec * 1.8

        # Universal fallback for general medical vocabulary
        subvec_all = _hash_token_to_subvector(token, seed=42, dim=VECTOR_DIMENSION)
        dense_vector += subvec_all * 0.25

    # L2 Normalization (ensures dot-product is equivalent to cosine similarity)
    norm = np.linalg.norm(dense_vector)
    if norm > 0:
        dense_vector = dense_vector / norm

    return [round(float(val), 6) for val in dense_vector]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    a = np.array(vec_a, dtype=np.float64)
    b = np.array(vec_b, dtype=np.float64)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def perform_mongo_vector_search(
    db,
    query_text: str,
    top_k: int = 4,
    department_filter: str = None
) -> List[Dict[str, Any]]:
    """
    Simulates / performs MongoDB Vector Search:
    1. Embeds query_text into a 64-dim dense vector.
    2. Searches patient documents in MongoDB containing 'clinical_embedding'.
    3. Calculates cosine similarity score (0.0 to 1.0).
    4. Returns top_k matched patients ranked by semantic relevance.
    """
    query_vector = generate_clinical_embedding(query_text)

    # Filter query
    match_query = {"status": {"$ne": "Archived"}}
    if department_filter and department_filter != "All":
        match_query["department"] = department_filter

    projection = {
        "_id": 0,
        "patient_id": 1,
        "name": 1,
        "age": 1,
        "gender": 1,
        "department": 1,
        "status": 1,
        "medical_notes": 1,
        "prescriptions": 1,
        "assigned_doctor_id": 1,
        "clinical_embedding": 1
    }

    patients = list(db.patients.find(match_query, projection))
    scored_results = []

    for patient in patients:
        doc_vector = patient.get("clinical_embedding")
        if not doc_vector:
            # Generate dynamically if document didn't have one cached
            notes_text = " ".join(patient.get("medical_notes", [])) + " " + patient.get("department", "")
            doc_vector = generate_clinical_embedding(notes_text)

        score = cosine_similarity(query_vector, doc_vector)
        # Convert to percentage 0-100%
        match_percentage = round(max(0.0, score) * 100, 1)

        result_item = {
            "patient_id": patient["patient_id"],
            "name": patient["name"],
            "age": patient["age"],
            "gender": patient["gender"],
            "department": patient["department"],
            "status": patient["status"],
            "medical_notes": patient.get("medical_notes", []),
            "prescriptions": patient.get("prescriptions", []),
            "similarity_score": round(score, 4),
            "match_percentage": match_percentage
        }
        scored_results.append(result_item)

    # Sort descending by similarity
    scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_results[:top_k]


def get_atlas_vector_search_pipeline(query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Synthesizes the official MongoDB Atlas $vectorSearch Aggregation Pipeline stage.
    This can be displayed in the UI and Viva to show how MongoDB Atlas executes Vector Search!
    """
    return [
        {
            "$vectorSearch": {
                "index": "clinical_vector_index",
                "path": "clinical_embedding",
                "queryVector": query_vector[:8] + ["... (64 dimensions total)"],
                "numCandidates": 50,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "patient_id": 1,
                "name": 1,
                "department": 1,
                "medical_notes": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]


def generate_ai_clinical_summary(query: str, matched_patients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates AI Clinical Insights based on the retrieved nearest-neighbor cases in MongoDB.
    """
    if not matched_patients:
        return {
            "confidence": "Low",
            "primary_department": "General Medicine",
            "recommendation": "No closely correlated patient records found in current database.",
            "common_medications": []
        }

    top_match = matched_patients[0]
    top_dept = top_match["department"]
    avg_score = sum(p["match_percentage"] for p in matched_patients) / len(matched_patients)

    # Collect common medicines from matched cases
    all_meds = []
    for p in matched_patients:
        for rx in p.get("prescriptions", []):
            all_meds.append(rx.get("medicine"))
    unique_meds = list(dict.fromkeys(all_meds))[:4]

    insights = [
        f"Query semantic profile correlates highest with hospital department: **{top_dept}**.",
        f"Top matched clinical history: Patient **{top_match['name']}** ({top_match['patient_id']}) with {top_match['match_percentage']}% similarity.",
        f"Observed clinical patterns in database: {', '.join(top_match.get('medical_notes', ['Routine checkup']))}."
    ]

    return {
        "confidence": "High" if avg_score > 60 else "Moderate",
        "average_similarity": round(avg_score, 1),
        "primary_department": top_dept,
        "insights": insights,
        "suggested_medications": unique_meds,
        "retrieved_cases_count": len(matched_patients)
    }
