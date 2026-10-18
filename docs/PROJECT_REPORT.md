# Project Report: Smart Hospital & Patient Care Management System (MediTrack)

**Student Name**: Ojaswi Bhardwaj  
**Registration No.**: 12319444 | **Roll No.**: 37  
**Subject**: CSE494 | **Section**: K3P23SD  
**GitHub Repository**: [https://github.com/ojaswi1234/mongo_project.git](https://github.com/ojaswi1234/mongo_project.git)  
**Live Deployment URL**: [https://mongo-project-nwjl.onrender.com](https://mongo-project-nwjl.onrender.com)  
**Course Outcome Alignment**: CO4, CO5, CO6 | **Bloom's Taxonomy Level**: L2, L3 — 30 Marks  
**Technology Stack**: MongoDB 6.0+, PyMongo 4.6+, Python (Flask), Atlas Vector Search, Chart.js  

---

## 1. Abstract

Modern healthcare organizations face challenges in managing patient data due to the velocity, heterogeneity, and high dimensionality of clinical records. Traditional Relational Database Management Systems (RDBMS) impose rigid tabular schemas that necessitate multi-table normalization (8 to 12 joins per patient encounter) and frequent schema migrations when medical diagnostic fields evolve. 

This project designs and implements **MediTrack**, a full-stack, document-oriented hospital information system built on **MongoDB** and **Python (PyMongo)**. MediTrack utilizes a **hybrid data model** that embeds high-velocity, co-located clinical data (vitals history, prescriptions, medical notes) while referencing shared entities (doctors, departments). The system enforces database-level data integrity using MongoDB **`$jsonSchema` validation**, executes atomic array updates (`$push`, `$addToSet`, `$inc`), and powers an executive intelligence dashboard through **multi-stage aggregation pipelines** (`$match`, `$group`, `$unwind`, `$lookup`, `$facet`). Furthermore, MediTrack integrates **MongoDB Vector Search**, storing explainable 10-dimensional clinical symptom vectors directly inside patient documents to provide an **AI Clinical Case Retrieval & Diagnostic Assistant**.

---

## 2. Problem Statement & Real-World Relevance

### 2.1 Problem Description
In hospital emergency rooms and inpatient wards, patient diagnostic data is inherently polymorphic:
- A cardiology patient requires continuous cardiac telemetry and blood pressure monitoring.
- A neurology patient requires Glasgow Coma Scale logs and MRI diagnostic records.
- Prescriptions and dosages vary continuously throughout admission.

In a relational database (SQL), modeling this structure requires separate tables for `Patients`, `Vitals`, `Doctors`, `Prescriptions`, and `Billing`. Retrieving a patient's complete medical chart requires joining 5+ tables, causing read latency and complex transaction locking under high concurrent write loads.

### 2.2 Real-World Significance
By adopting MongoDB as an operational document store and vector database:
1. **Zero JOIN Latency on Critical Lookups**: A patient's demographics, clinical history, and recent vital signs are co-located in a single BSON document, retrievable in a single disk read ($O(1)$ indexed lookup).
2. **Clinical Safety & Schema Integrity**: MongoDB's `$jsonSchema` engine prevents invalid medical entries (e.g., negative blood pressure, out-of-range temperatures, malformed identifiers) directly at the database engine level.
3. **Atomic Streaming Updates**: Attending nurses append new vital readings using MongoDB's `$push` operator without locking or rewriting the entire patient document.
4. **AI-Assisted Diagnostic Triage**: By storing dense vector embeddings inside MongoDB documents, medical professionals can query unstructured clinical symptoms using natural language to retrieve semantically correlated historical cases and treatment plans.

---

## 3. Database Architecture & Document Design

### 3.1 Data Modeling Strategy: Hybrid (Embedded vs. Referenced)

MongoDB provides two primary modeling strategies: **Embedding** (denormalization) and **Referencing** (normalization). MediTrack implements a **hybrid data architecture**:

```
+-------------------------------------------------------------+
|                      PATIENTS COLLECTION                    |
+-------------------------------------------------------------+
| - _id: ObjectId                                             |
| - patient_id: "PAT-1001" (Unique Index)                     |
| - name: "Robert Miller"                                     |
| - age: 62, gender: "Male", blood_group: "A+"                |
| - department: "Cardiology", status: "Admitted"              |
| - assigned_doctor_id: "DOC-201" (REFERENCE -> doctors)      |
|                                                             |
| [EMBEDDED 1:N] vitals_history: [                            |
|     { timestamp, blood_pressure, heart_rate, spo2, temp }   |
| ]                                                           |
|                                                             |
| [EMBEDDED 1:N] prescriptions: [                             |
|     { medicine, dosage, frequency, days }                   |
| ]                                                           |
|                                                             |
| [EMBEDDED 1:1] billing: {                                   |
|     room_charges, consultation_fee, medicine_charges, total |
| }                                                           |
|                                                             |
| [VECTOR EMBEDDING] clinical_embedding: [0.95, 0.10, ... 10D]|
+-------------------------------------------------------------+
                            |
           (Referenced via assigned_doctor_id)
                            v
+-------------------------------------------------------------+
|                      DOCTORS COLLECTION                     |
+-------------------------------------------------------------+
| - _id: ObjectId                                             |
| - doctor_id: "DOC-201" (Unique Index)                       |
| - name: "Dr. Sarah Jenkins"                                 |
| - specialization: "Chief Cardiologist"                      |
| - department: "Cardiology"                                  |
| - experience_years: 16                                      |
| - consultation_fee: 150.0                                   |
| - available_days: ["Monday", "Wednesday", "Friday"]         |
| - ratings: 4.9                                              |
+-------------------------------------------------------------+
```

#### Why Embed `vitals_history` and `prescriptions`?
- **High Read Locality**: In 98% of clinical workflows, a patient's vitals and medications are accessed together with their personal record.
- **Bounded Cardinality**: A typical hospital stay produces 20 to 100 vital readings (well within MongoDB's 16 MB document size limit).
- **Atomic Modification**: Appending a new vital sign is accomplished via a single atomic `$push` operation without multi-document transaction overhead.

#### Why Reference `doctors` and `departments`?
- **Unbounded Cardinality**: A senior physician treats thousands of patients over years. Embedding the doctor inside each patient document would duplicate doctor information thousands of times, causing data redundancy and update anomalies if a doctor changes departments or fees.

---

## 4. Schema Validation Rules (`$jsonSchema`)

Data integrity is enforced at the MongoDB database level using `$jsonSchema`. Any insert or update violating the schema is rejected with a `WriteError`.

### Validation Implementation:
```javascript
db.createCollection("patients", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "patient_id", "name", "age", "gender", "blood_group",
        "department", "status", "assigned_doctor_id", "billing"
      ],
      properties: {
        patient_id: {
          bsonType: "string",
          pattern: "^PAT-[0-9]{4}$",
          description: "Must match format PAT-XXXX (e.g. PAT-1001)"
        },
        name: {
          bsonType: "string",
          minLength: 2,
          maxLength: 100
        },
        age: {
          bsonType: "int",
          minimum: 0,
          maximum: 125,
          description: "Age must be an integer between 0 and 125"
        },
        gender: {
          enum: ["Male", "Female", "Other"]
        },
        blood_group: {
          enum: ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        },
        department: {
          enum: ["Cardiology", "Neurology", "Orthopedics", "General Medicine", "Pediatrics", "Oncology"]
        },
        status: {
          enum: ["Admitted", "Discharged", "Under Observation", "Outpatient", "Archived"]
        },
        assigned_doctor_id: {
          bsonType: "string",
          pattern: "^DOC-[0-9]{3}$"
        },
        vitals_history: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["timestamp", "heart_rate", "blood_pressure", "oxygen_level"],
            properties: {
              heart_rate: { bsonType: "int", minimum: 30, maximum: 240 },
              oxygen_level: { bsonType: "int", minimum: 50, maximum: 100 }
            }
          }
        }
      }
    }
  },
  validationLevel: "moderate",
  validationAction: "error"
});
```

---

## 5. CRUD Operations Implementation

### 5.1 CREATE Operation
Inserts a compliant BSON document into the `patients` collection while automatically generating its 10-dimensional clinical symptom vector:
```python
def create_patient(db, patient_data):
    if "clinical_embedding" not in patient_data:
        notes = " ".join(patient_data.get("medical_notes", [])) + " " + patient_data.get("department", "")
        patient_data["clinical_embedding"] = generate_clinical_embedding(notes)
    
    result = db.patients.insert_one(patient_data)
    return {"success": True, "inserted_id": str(result.inserted_id)}
```

### 5.2 READ Operation with Complex Filters & `$elemMatch`
Demonstrates querying embedded arrays where multiple conditions must hold true simultaneously on the **same** array element:
```python
# Find patients with dangerous tachycardia (HR >= 100) and hypoxemia (SpO2 <= 95)
query = {
    "vitals_history": {
        "$elemMatch": {
            "heart_rate": {"$gte": 100},
            "oxygen_level": {"$lte": 95}
        }
    }
}
critical_patients = list(db.patients.find(query, {"_id": 0, "name": 1, "department": 1, "vitals_history": 1}))
```

### 5.3 UPDATE Operations (`$push`, `$inc`, `$set`)
1. **Appending to Embedded Array (`$push`)**:
```python
db.patients.update_one(
    {"patient_id": "PAT-1001"},
    {"$push": {"vitals_history": new_vital_check}}
)
```
2. **Atomic Numeric Increments on Billing (`$inc`)**:
```python
db.patients.update_one(
    {"patient_id": "PAT-1001"},
    {
        "$inc": {"billing.medicine_charges": 50.0, "billing.total_amount": 50.0},
        "$set": {"billing.payment_status": "Pending"}
    }
)
```

### 5.4 DELETE Operation (Soft Deletion / Audit Trail)
In medical systems, physical deletion destroys legal medical history. MediTrack implements logical soft deletion:
```python
db.patients.update_one(
    {"patient_id": "PAT-1004"},
    {"$set": {"status": "Archived", "is_archived": True, "archived_at": datetime.now()}}
)
```

---

## 6. Advanced Aggregation Pipelines

MediTrack implements 5 distinct aggregation pipelines to deliver business and clinical intelligence:

### Pipeline 1: Department-wise Patient Demographics & Financial Revenue
- **Stages**: `$match` $\rightarrow$ `$group` $\rightarrow$ `$project` $\rightarrow$ `$sort`
- **Purpose**: Computes departmental patient volume, average age, and aggregate billed revenue.
```javascript
db.patients.aggregate([
  { $match: { status: { $ne: "Archived" } } },
  {
    $group: {
      _id: "$department",
      total_patients: { $sum: 1 },
      average_age: { $avg: "$age" },
      total_revenue: { $sum: "$billing.total_amount" },
      avg_bill: { $avg: "$billing.total_amount" }
    }
  },
  { $sort: { total_revenue: -1 } }
]);
```

### Pipeline 2: Doctor Workload & Cross-Collection Join (`$lookup`)
- **Stages**: `$lookup` $\rightarrow$ `$project` $\rightarrow$ `$sort`
- **Purpose**: Resolves the referencing relationship between `doctors` and `patients` to measure doctor caseload and generated revenue without client-side joins.
```javascript
db.doctors.aggregate([
  {
    $lookup: {
      from: "patients",
      localField: "doctor_id",
      foreignField: "assigned_doctor_id",
      as: "patient_records"
    }
  },
  {
    $project: {
      _id: 0,
      doctor_id: 1,
      doctor_name: "$name",
      department: 1,
      patient_count: { $size: "$patient_records" },
      total_revenue: { $sum: "$patient_records.billing.total_amount" }
    }
  },
  { $sort: { patient_count: -1 } }
]);
```

### Pipeline 3: Clinical Critical Vitals Anomaly Detection (`$unwind` + `$match`)
- **Stages**: `$unwind` $\rightarrow$ `$match` $\rightarrow$ `$project` $\rightarrow$ `$sort`
- **Purpose**: Flattens the embedded `vitals_history` array to isolate and alert medical staff on individual life-threatening readings across the hospital.
```javascript
db.patients.aggregate([
  { $unwind: "$vitals_history" },
  {
    $match: {
      $or: [
        { "vitals_history.heart_rate": { $gte: 100 } },
        { "vitals_history.oxygen_level": { $lte: 95 } }
      ]
    }
  },
  { $sort: { "vitals_history.heart_rate": -1 } }
]);
```

### Pipeline 4: Pharmacy Inventory & Medication Frequency (`$unwind` + `$group`)
- **Stages**: `$unwind` $\rightarrow$ `$group` $\rightarrow$ `$sort` $\rightarrow$ `$limit`
- **Purpose**: Identifies the most frequently prescribed drugs and average dosage duration to optimize pharmacy procurement.

### Pipeline 5: Multi-Faceted Executive KPI Dashboard (`$facet`)
- **Stages**: `$facet` (Parallel execution)
- **Purpose**: Evaluates bed status distribution and financial payment status in a single database round-trip query.
```javascript
db.patients.aggregate([
  {
    $facet: {
      status_summary: [
        { $group: { _id: "$status", count: { $sum: 1 } } }
      ],
      billing_summary: [
        {
          $group: {
            _id: "$billing.payment_status",
            total_billed: { $sum: "$billing.total_amount" },
            patient_count: { $sum: 1 }
          }
        }
      ]
    }
  }
]);
```

---

## 7. MongoDB as a Vector Database & AI Clinical Assistant

### 7.1 How MongoDB Functions as a Vector Database
In modern AI architectures, vector search allows searching unstructured data by **meaning** rather than exact keyword matches. MongoDB natively supports vector storage and search:
1. **Vector Storage**: Clinical symptom embeddings are stored directly in documents as standard BSON arrays of IEEE 754 floating-point numbers (`clinical_embedding: [0.95, 0.10, 0.00, ...]`).
2. **Unified Data Architecture**: Unlike architectures requiring external vector databases (e.g. Pinecone) synced via message queues, MongoDB houses transactional metadata, live vitals, and vector embeddings in the **same document**.
3. **MongoDB Atlas `$vectorSearch`**: In production, MongoDB Atlas creates an HNSW (Hierarchical Navigable Small World) index and performs nearest-neighbor vector search directly within aggregation pipelines:
```javascript
db.patients.aggregate([
  {
    $vectorSearch: {
      index: "clinical_vector_index",
      path: "clinical_embedding",
      queryVector: [0.90, 0.15, 0.0, 0.10, ...],
      numCandidates: 100,
      limit: 5
    }
  },
  {
    $project: {
      name: 1, department: 1, medical_notes: 1,
      similarity_score: { $meta: "vectorSearchScore" }
    }
  }
]);
```

### 7.2 AI Clinical Assistant Workflow
1. The physician enters an unstructured symptom description (e.g., *"acute chest pain and elevated palpitations"*).
2. The AI engine computes an explainable 10-dimensional clinical symptom vector $Q$ covering 10 primary indicators: Chest Pain, Headache, Fever, Cough, Shortness of Breath, Fatigue, Dizziness, Nausea, Hypertension, and Joint Pain.
3. The engine computes vector cosine similarity against all patient embeddings in MongoDB:
   $$\text{Cosine Similarity} = \frac{Q \cdot D}{\|Q\| \|D\|}$$
4. The system ranks the closest matching patient documents, displays match percentages, and synthesizes clinical recommendations and commonly prescribed medications.

---

## 8. Web Application Architecture

The system features a web architecture powered by **Python Flask**, **Tailwind CSS**, and **Chart.js**:
- **Interactive Dashboard (`/`)**: Displays real-time KPIs, bed occupancy progress bars, and recent admissions.
- **Patient Directory (`/patients`)**: Filterable directory supporting real-time department and status querying.
- **Patient Profile & Charting (`/patient/<id>`)**: Visualizes historical vital trends via interactive Chart.js line graphs, and provides modals for live `$push` and `$inc` updates.
- **Patient Admission Form (`/patients/new`)**: Interactive form demonstrating real-time `$jsonSchema` validation errors and success confirmations.
- **Aggregation Intelligence (`/analytics`)**: Visual dashboard displaying interactive bar charts, doughnut charts, and query syntax viewers.
- **AI Vector Search (`/ai-search`)**: Web interface for natural language symptom search with similarity meters and Atlas query inspection.

---

## 9. Conclusion

The MediTrack project successfully demonstrates the design and implementation of a production-grade MongoDB application tailored to healthcare management:
- It solves the problem of relational join bottlenecks through an optimized hybrid document model.
- It guarantees strict data integrity via database-level `$jsonSchema` rules.
- It executes high-performance atomic array and numeric mutations (`$push`, `$inc`).
- It extracts strategic operational insights using multi-stage aggregation pipelines (`$lookup`, `$facet`, `$unwind`).
- It positions MongoDB at the forefront of modern AI engineering by utilizing its capabilities as a unified **Operational and Vector Database**.
