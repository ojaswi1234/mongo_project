# MediTrack: Viva Voce & Technical Defense Preparation Guide

**Course Outcomes Covered**: CO4, CO5, CO6 (NoSQL Database Design, PyMongo, Aggregations, Vector Search)

---

## Part 1: Top 15 Viva Voce Questions & Model Answers

### Q1: Why did you choose MongoDB over a traditional Relational Database (like MySQL) for this project?
**Answer:**
Healthcare data is inherently **hierarchical and polymorphic**. A single patient visit involves varying vitals, differing prescription counts, and changing diagnoses. 
- In MySQL, storing this requires 5+ normalized tables (`Patients`, `VitalsHistory`, `Prescriptions`, `Doctors`, `Billing`) linked by foreign keys. Fetching a patient's chart requires expensive multi-table JOINs.
- In MongoDB, we use a **hybrid document model** where vitals and prescriptions are embedded directly inside the patient document. This allows a **single $O(1)$ disk read** to fetch the complete patient chart with zero joins, while also supporting atomic streaming updates via `$push`.

---

### Q2: Explain the difference between Embedded Documents and Referenced Documents. How did you decide what to embed and what to reference?
**Answer:**
- **Embedded Documents (1-to-Few relationship)**: Stored inside the parent document. We embedded `vitals_history`, `prescriptions`, and `billing` because:
  1. They are queried together with the patient in 99% of requests (high read locality).
  2. Their cardinality is bounded (a typical patient has 10–50 vital records, well within MongoDB's 16MB document limit).
  3. Updates to vitals can be done atomically using `$push`.
- **Referenced Documents (1-to-Many / Many-to-Many relationship)**: Stored in separate collections linked by an ID. We referenced `doctors` and `departments` because:
  1. A doctor treats thousands of patients over time (unbounded growth).
  2. Embedding doctor details inside thousands of patient records would cause massive data duplication and update anomalies if a doctor changes departments or fees.

---

### Q3: What is the 16 MB BSON document size limit in MongoDB, and could `vitals_history` ever exceed it?
**Answer:**
MongoDB enforces a maximum BSON document size of **16 Megabytes** to prevent unbounded RAM consumption and ensure high-throughput serialization.
- In our design, a single vital measurement is approximately 120 bytes. A patient would need over **130,000 vital readings** before reaching 16 MB.
- In an ICU setting with second-by-second telemetry, industry best practice is the **Bucket Pattern** (creating a new document per day/hour) or MongoDB **Time Series Collections**. For standard hospital admissions, embedding is the optimal pattern.

---

### Q4: How does MongoDB Schema Validation work, and how did you implement it?
**Answer:**
While MongoDB is traditionally "schemaless," production systems require data integrity. MongoDB provides database-level validation using the **`$jsonSchema` operator** passed during `createCollection` or via the `collMod` command.
In our project:
- We enforced regex pattern matching (`^PAT-[0-9]{4}$`) for patient IDs.
- Integer boundaries for `age` (0 to 125) and `heart_rate` (30 to 240 BPM).
- Enum constraints for `gender` (`["Male", "Female", "Other"]`) and `department`.
If any insert or update violates these rules, the MongoDB engine rejects the write and throws a `WriteError` (DocumentValidationFailure).

---

### Q5: What is the difference between querying an array directly and using `$elemMatch`?
**Answer:**
- **Direct Query (`{"vitals_history.heart_rate": {$gte: 100}, "vitals_history.oxygen_level": {$lte: 95}}`)**: Matches if *any* vital has HR $\ge 100$ and *any* (possibly different) vital has SpO2 $\le 95$.
- **`$elemMatch` Query**: Requires that **both conditions are satisfied simultaneously on the exact same array element (same reading)**. This is crucial for medical triage, ensuring we only alert if a patient suffered tachycardia and hypoxemia at the same recorded point in time.

---

### Q6: What is the difference between `$push` and `$addToSet`?
**Answer:**
- **`$push`**: Appends a new item to an array regardless of whether it already exists (used for our continuous time-stamped vitals history).
- **`$addToSet`**: Appends an item to an array **only if it does not already exist**, preventing duplicate values (used when adding medications to prescriptions).

---

### Q7: What are MongoDB Aggregation Pipelines and how do they differ from MapReduce?
**Answer:**
The MongoDB Aggregation Framework processes documents through an ordered sequence of stages (pipeline), where the output of one stage serves as the input to the next.
- Unlike the older MapReduce framework (which relied on custom JavaScript execution and was deprecated in MongoDB 5.0), the Aggregation Pipeline runs as **native C++ optimized code** inside the MongoDB engine, utilizing indexes, streaming memory buffers, and SIMD hardware acceleration.

---

### Q8: How did you implement a JOIN in MongoDB? Explain your `$lookup` pipeline.
**Answer:**
MongoDB supports left outer joins across collections via the **`$lookup` stage**.
In our Doctor Workload Pipeline:
```javascript
{
  $lookup: {
    from: "patients",
    localField: "doctor_id",
    foreignField: "assigned_doctor_id",
    as: "patient_records"
  }
}
```
This joins the `doctors` collection with `patients` where `doctor_id == assigned_doctor_id`, aggregating all matching patient documents into an array field `patient_records`. We then use `$size` to count assigned patients and `$sum` to compute total revenue generated.

---

### Q9: What does the `$unwind` stage do, and why did you use it?
**Answer:**
The `$unwind` stage deconstructs an array field from input documents to output a distinct document for each element in the array.
- We used `$unwind: "$vitals_history"` in Pipeline 3 to flatten the historical vitals array. This allows downstream `$match` and `$sort` stages to inspect and rank individual clinical readings (e.g. sorting patients by the single highest heart rate recorded in hospital history).

---

### Q10: What is the `$facet` stage, and what problem does it solve?
**Answer:**
The `$facet` stage allows executing **multiple independent aggregation sub-pipelines** in parallel on the same set of input documents within a single query.
- Without `$facet`, generating a dashboard would require multiple network round-trips to the database (one query for status distribution, another for billing totals, another for demographics).
- `$facet` executes all three concurrently in one round trip, dramatically reducing network overhead.

---

### Q11: Can MongoDB be used as a Vector Database? How?
**Answer:**
**Yes!** MongoDB is widely used as a unified operational and vector database.
1. Documents store high-dimensional vector embeddings as standard BSON arrays of doubles (`clinical_embedding: [0.12, -0.45, ...]`).
2. In MongoDB Atlas, **Atlas Vector Search** builds a Hierarchical Navigable Small World (HNSW) index on these vector fields.
3. Queries are executed natively inside aggregation pipelines using the `$vectorSearch` stage, allowing semantic search combined with standard metadata filters (e.g., searching for chest pain symptoms filtered only by `department: "Cardiology"`).

---

### Q12: Why is storing vectors in MongoDB better than using a separate dedicated vector database like Pinecone?
**Answer:**
In a split architecture (MongoDB for operational data + Pinecone for vectors):
- Developers must maintain an ETL synchronization pipeline (Kafka/Change Streams).
- If a patient record is deleted or updated in MongoDB, synchronization drift can cause phantom or stale vector results.
- With MongoDB Vector Search, **operational data, transactional vitals, and vector embeddings reside in the exact same document**, ensuring zero sync lag and atomic updates.

---

### Q13: What is the role of PyMongo in this architecture?
**Answer:**
PyMongo is the official synchronous Python distribution driver for MongoDB. It:
1. Translates native Python dictionaries, lists, and datetime objects into binary BSON format.
2. Manages connection pooling, replica set failover, and automatic server discovery.
3. Provides full access to MongoDB CRUD methods (`insert_one`, `find`, `update_one`, `aggregate`).

---

### Q14: What is the difference between a Hard Delete and a Soft Delete? Why is Soft Delete preferred here?
**Answer:**
- **Hard Delete (`db.patients.delete_one()`)**: Physically removes the BSON document from disk.
- **Soft Delete (`db.patients.update_one({"patient_id": id}, {"$set": {"status": "Archived", "is_archived": True}})`**: Flags the document as archived without removing data.
- In healthcare systems, regulations (such as HIPAA) strictly prohibit permanent deletion of medical records. Soft delete maintains a permanent audit trail while excluding archived patients from active operational queries using `$ne: "Archived"`.

---

### Q15: What indexes did you create, and why?
**Answer:**
1. **Unique Index on `patient_id` and `doctor_id`**: Guarantees uniqueness and provides $O(1)$ lookup times.
2. **Compound Index on `(department, status)`**: Speeds up the most frequent operational query: listing admitted patients by department.
3. **Multikey Index on `vitals_history.heart_rate`**: Indexes individual elements of the embedded array for fast triage queries.

---

## Part 2: Quick Viva Defense Strategy

When presenting to the examiner:
1. **Open with the Problem Statement**: Emphasize how relational databases require 6+ joins for a patient chart, whereas MongoDB co-locates data for instant access.
2. **Demonstrate Schema Validation**: Use the "Fill Invalid Sample" button on the web form to show the examiner how MongoDB blocks invalid inputs.
3. **Show the Aggregation Tab**: Point out the 5 pipelines, especially `$lookup` (cross-collection join) and `$facet` (single-query multi-perspective analytics).
4. **Highlight the AI Vector Search Tab**: Show how doctors can type symptoms in natural language to find similar cases, and explain that embeddings are stored as native 64-double BSON arrays inside MongoDB documents.
