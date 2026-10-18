/**
 * Smart Hospital & Patient Care Management System (MediTrack)
 * MongoDB Shell (mongosh / Compass) Raw Scripts & Queries
 * 
 * Target Database: SmartHospitalDB
 * Demonstrates:
 * 1. Collection Creation with $jsonSchema Validation
 * 2. Secondary & Compound Indexing
 * 3. Seed Document Inserts
 * 4. CRUD Operations (Filtering, Projections, Atomic Array Updates)
 * 5. Advanced Multi-stage Aggregation Pipelines
 */

// Switch / Create Database
use SmartHospitalDB;

// =============================================================================
// SECTION 1: DATABASE INITIALIZATION & $jsonSchema VALIDATION
// =============================================================================

// 1.1 Drop existing collections if resetting
db.patients.drop();
db.doctors.drop();
db.departments.drop();

// 1.2 Create 'patients' collection with strict validation
db.createCollection("patients", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
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
      properties: {
        patient_id: {
          bsonType: "string",
          pattern: "^PAT-[0-9]{4}$",
          description: "Unique patient code (e.g., PAT-1001)"
        },
        name: {
          bsonType: "string",
          minLength: 2,
          maxLength: 100,
          description: "Full legal name"
        },
        age: {
          bsonType: "int",
          minimum: 0,
          maximum: 125,
          description: "Age in years"
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
              timestamp: { bsonType: "date" },
              blood_pressure: { bsonType: "string" },
              heart_rate: { bsonType: "int", minimum: 30, maximum: 240 },
              temperature: { bsonType: ["double", "int"] },
              oxygen_level: { bsonType: "int", minimum: 50, maximum: 100 }
            }
          }
        },
        billing: {
          bsonType: "object",
          required: ["room_charges", "consultation_fee", "medicine_charges", "total_amount", "payment_status"],
          properties: {
            room_charges: { bsonType: ["double", "int"] },
            consultation_fee: { bsonType: ["double", "int"] },
            medicine_charges: { bsonType: ["double", "int"] },
            total_amount: { bsonType: ["double", "int"] },
            payment_status: { enum: ["Paid", "Pending", "Partially Paid", "Insurance Claimed"] }
          }
        }
      }
    }
  },
  validationLevel: "moderate",
  validationAction: "error"
});

// 1.3 Create 'doctors' collection with validation
db.createCollection("doctors", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["doctor_id", "name", "specialization", "department", "experience_years", "consultation_fee"],
      properties: {
        doctor_id: { bsonType: "string", pattern: "^DOC-[0-9]{3}$" },
        name: { bsonType: "string" },
        experience_years: { bsonType: "int", minimum: 0 },
        consultation_fee: { bsonType: ["double", "int"], minimum: 0 }
      }
    }
  }
});

// =============================================================================
// SECTION 2: INDEX CREATION
// =============================================================================

// 2.1 Unique Indexes
db.patients.createIndex({ "patient_id": 1 }, { unique: true });
db.doctors.createIndex({ "doctor_id": 1 }, { unique: true });

// 2.2 Compound Index for frequent clinical filtering
db.patients.createIndex({ "department": 1, "status": 1 });

// 2.3 Multikey Index on embedded array for high-speed anomaly queries
db.patients.createIndex({ "vitals_history.heart_rate": 1 });


// =============================================================================
// SECTION 3: SEED INSERTS (SAMPLE DATA)
// =============================================================================

db.doctors.insertMany([
  {
    doctor_id: "DOC-201",
    name: "Dr. Sarah Jenkins",
    specialization: "Chief Cardiologist",
    department: "Cardiology",
    experience_years: NumberInt(16),
    consultation_fee: 150.0,
    available_days: ["Monday", "Wednesday", "Friday"],
    ratings: 4.9
  },
  {
    doctor_id: "DOC-202",
    name: "Dr. Rajesh Sharma",
    specialization: "Senior Neurologist",
    department: "Neurology",
    experience_years: NumberInt(14),
    consultation_fee: 160.0,
    available_days: ["Tuesday", "Thursday", "Saturday"],
    ratings: 4.8
  },
  {
    doctor_id: "DOC-203",
    name: "Dr. Emily Taylor",
    specialization: "Orthopedic Surgeon",
    department: "Orthopedics",
    experience_years: NumberInt(11),
    consultation_fee: 130.0,
    available_days: ["Monday", "Tuesday", "Thursday"],
    ratings: 4.7
  }
]);

db.patients.insertMany([
  {
    patient_id: "PAT-1001",
    name: "Robert Miller",
    age: NumberInt(62),
    gender: "Male",
    blood_group: "A+",
    department: "Cardiology",
    status: "Admitted",
    assigned_doctor_id: "DOC-201",
    admission_date: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000),
    vitals_history: [
      {
        timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
        blood_pressure: "145/95",
        heart_rate: NumberInt(105),
        temperature: 99.1,
        oxygen_level: NumberInt(94)
      },
      {
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
        blood_pressure: "128/82",
        heart_rate: NumberInt(78),
        temperature: 98.4,
        oxygen_level: NumberInt(98)
      }
    ],
    medical_notes: ["History of hypertension", "Angioplasty recommended"],
    prescriptions: [
      { medicine: "Atorvastatin", dosage: "20mg", frequency: "Daily", days: NumberInt(30) },
      { medicine: "Metoprolol", dosage: "50mg", frequency: "Twice daily", days: NumberInt(15) }
    ],
    billing: {
      room_charges: 1600.0,
      consultation_fee: 450.0,
      medicine_charges: 280.0,
      total_amount: 2330.0,
      payment_status: "Partially Paid"
    }
  },
  {
    patient_id: "PAT-1002",
    name: "Sophia Chen",
    age: NumberInt(45),
    gender: "Female",
    blood_group: "B+",
    department: "Neurology",
    status: "Admitted",
    assigned_doctor_id: "DOC-202",
    admission_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    vitals_history: [
      {
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
        blood_pressure: "120/78",
        heart_rate: NumberInt(74),
        temperature: 98.6,
        oxygen_level: NumberInt(99)
      }
    ],
    medical_notes: ["Chronic migraine aura", "MRI brain completed"],
    prescriptions: [
      { medicine: "Sumatriptan", dosage: "50mg", frequency: "As needed", days: NumberInt(10) }
    ],
    billing: {
      room_charges: 800.0,
      consultation_fee: 320.0,
      medicine_charges: 190.0,
      total_amount: 1310.0,
      payment_status: "Paid"
    }
  }
]);

// =============================================================================
// SECTION 4: CRUD QUERIES
// =============================================================================

// 4.1 CREATE: Test Validation Failure (Intentional error to test $jsonSchema)
try {
  db.patients.insertOne({
    patient_id: "INVALID-ID", // violates regex ^PAT-[0-9]{4}$
    name: "Bad Record",
    age: NumberInt(150),      // violates maximum 125
    gender: "Unknown"         // violates enum
  });
} catch(err) {
  print("Validation successfully caught invalid insert:", err.message);
}

// 4.2 READ: Find patients admitted in Cardiology with projection
db.patients.find(
  { department: "Cardiology", status: "Admitted" },
  { _id: 0, patient_id: 1, name: 1, age: 1, "billing.total_amount": 1 }
);

// 4.3 READ: Query embedded array using $elemMatch (Critical vitals check)
db.patients.find(
  {
    vitals_history: {
      $elemMatch: {
        heart_rate: { $gte: 100 },
        oxygen_level: { $lte: 95 }
      }
    }
  },
  { _id: 0, patient_id: 1, name: 1, department: 1, vitals_history: 1 }
);

// 4.4 UPDATE: Append new vital record to array using $push
db.patients.updateOne(
  { patient_id: "PAT-1001" },
  {
    $push: {
      vitals_history: {
        timestamp: new Date(),
        blood_pressure: "122/80",
        heart_rate: NumberInt(75),
        temperature: 98.6,
        oxygen_level: NumberInt(99)
      }
    }
  }
);

// 4.5 UPDATE: Atomic increment on billing amount using $inc
db.patients.updateOne(
  { patient_id: "PAT-1001" },
  {
    $inc: { "billing.medicine_charges": 50.0, "billing.total_amount": 50.0 },
    $set: { "billing.payment_status": "Pending" }
  }
);

// 4.6 DELETE: Soft delete (Recommended for clinical compliance)
db.patients.updateOne(
  { patient_id: "PAT-1002" },
  { $set: { status: "Archived", is_archived: true } }
);


// =============================================================================
// SECTION 5: ADVANCED AGGREGATION PIPELINES
// =============================================================================

// Pipeline 1: Department-wise Patient Demographics & Financial Revenue
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
  {
    $project: {
      _id: 0,
      department: "$_id",
      total_patients: 1,
      average_age: { $round: ["$average_age", 1] },
      total_revenue: { $round: ["$total_revenue", 2] },
      avg_bill: { $round: ["$avg_bill", 2] }
    }
  },
  { $sort: { total_revenue: -1 } }
]);

// Pipeline 2: Doctor Workload & Patient Revenue Association ($lookup)
db.doctors.aggregate([
  {
    $lookup: {
      from: "patients",
      localField: "doctor_id",
      foreignField: "assigned_doctor_id",
      as: "assigned_patients"
    }
  },
  {
    $project: {
      _id: 0,
      doctor_id: 1,
      doctor_name: "$name",
      department: 1,
      experience_years: 1,
      patient_count: { $size: "$assigned_patients" },
      total_revenue: { $sum: "$assigned_patients.billing.total_amount" }
    }
  },
  { $sort: { patient_count: -1 } }
]);

// Pipeline 3: Clinical Critical Vitals Anomaly Alert ($unwind + $match)
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
  {
    $project: {
      _id: 0,
      patient_id: 1,
      patient_name: "$name",
      department: 1,
      heart_rate: "$vitals_history.heart_rate",
      oxygen_level: "$vitals_history.oxygen_level",
      blood_pressure: "$vitals_history.blood_pressure",
      timestamp: "$vitals_history.timestamp"
    }
  },
  { $sort: { heart_rate: -1 } }
]);

// Pipeline 4: Pharmacy Most Prescribed Medications ($unwind + $group)
db.patients.aggregate([
  { $unwind: "$prescriptions" },
  {
    $group: {
      _id: "$prescriptions.medicine",
      prescription_count: { $sum: 1 },
      avg_duration_days: { $avg: "$prescriptions.days" }
    }
  },
  {
    $project: {
      _id: 0,
      medicine: "$_id",
      prescription_count: 1,
      avg_duration_days: { $round: ["$avg_duration_days", 1] }
    }
  },
  { $sort: { prescription_count: -1 } },
  { $limit: 5 }
]);

// Pipeline 5: Multi-Faceted Executive KPI Dashboard ($facet)
db.patients.aggregate([
  {
    $facet: {
      status_distribution: [
        { $group: { _id: "$status", count: { $sum: 1 } } }
      ],
      payment_summary: [
        {
          $group: {
            _id: "$billing.payment_status",
            total_amount: { $sum: "$billing.total_amount" },
            count: { $sum: 1 }
          }
        }
      ]
    }
  }
]);
