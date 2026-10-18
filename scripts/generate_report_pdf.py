"""
Generates the official Academic Project Report PDF for Smart Hospital MongoDB System (MediTrack).
Styled cleanly and uncompressed, matching MongoDB_Practical_Viva_Guide.pdf:
- Clean Helvetica typography (9.5pt body, 13.5pt leading, generous spacing).
- Uncluttered, direct, concise technical explanations without bloat.
- Clean 8.2pt Courier code blocks with comfortable padding.
- Intact outer framing border and centered LPU logo (lpu.PNG) on every page.
- Exactly 4 pages:
  Page 1: Title, Metadata, Problem Relevance, Schema Design (Hybrid model)
  Page 2: Validation ($jsonSchema), PyMongo Connection & Indexes, CRUD Operations
  Page 3: Aggregation Pipelines (3 core clinical pipelines), Query Outputs
  Page 4: Viva Defense (Q&A style), Deliverables, Evaluation Sign-Off
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas


class LPUAcademicCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        w, h = 595.28, 841.89  # A4 Portrait

        # 1. Outer framing border
        self.setStrokeColor(colors.HexColor("#0f172a"))
        self.setLineWidth(0.8)
        self.rect(24, 24, w - 48, h - 48, stroke=1, fill=0)

        # 2. Centered College Logo at top of every page
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "lpu.PNG")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(__file__), "lpu.PNG")
        if not os.path.exists(logo_path):
            logo_path = r"C:\Users\ojasw\Desktop\lpu.PNG"

        if os.path.exists(logo_path):
            logo_w = 120
            logo_h = 44
            logo_x = (w - logo_w) / 2
            logo_y = h - 24 - logo_h - 4
            self.drawImage(logo_path, logo_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')

        # 3. Running Footer
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(38, 14, "Smart Hospital Management System (MediTrack) • CSE494 CA2")
        self.drawRightString(w - 38, 14, f"Page {self._pageNumber} of {total_pages}")

        self.restoreState()


def make_code_box(code_str, font_size=8.2, leading=10.8):
    """Clean, comfortable monospaced code block matching the reference guide."""
    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=font_size,
        leading=leading,
        textColor=colors.HexColor("#0f172a")
    )
    html_code = (
        code_str.replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('\n', '<br/>')
        .replace(' ', '&nbsp;')
    )
    t = Table([[Paragraph(html_code, code_style)]], colWidths=[515])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def build_report_pdf(filename="SmartHospital_Project_Report.pdf"):
    # Printable width: 515.28 pt (Left=40, Right=40)
    # Printable height: 734.89 pt (Top=75, Bottom=32)
    doc = SimpleDocTemplate(
        filename,
        pagesize=(595.28, 841.89),
        leftMargin=40,
        rightMargin=40,
        topMargin=75,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()

    # Spacious, comfortable typography matching MongoDB_Practical_Viva_Guide.pdf
    title_main = ParagraphStyle(
        'MainTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=colors.HexColor("#0f172a")
    )

    title_sub = ParagraphStyle(
        'SubTitle',
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        alignment=1,
        textColor=colors.HexColor("#475569")
    )

    meta_text = ParagraphStyle(
        'MetaText',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        alignment=1,
        textColor=colors.HexColor("#334155")
    )

    sec_title = ParagraphStyle(
        'SecTitle',
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15.5,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=7,
        spaceAfter=3
    )

    sub_title = ParagraphStyle(
        'SubHead',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=4,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'ReportBody',
        fontName='Helvetica',
        fontSize=9.3,
        leading=13.2,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        'ReportBullet',
        fontName='Helvetica',
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=2.5
    )

    viva_q = ParagraphStyle(
        'VivaQ',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=5,
        spaceAfter=1
    )

    viva_a = ParagraphStyle(
        'VivaA',
        fontName='Helvetica',
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE, METADATA, PROBLEM & DOCUMENT DESIGN
    # =========================================================================

    story.append(Paragraph("Smart Hospital Management System", title_main))
    story.append(Spacer(1, 2))
    story.append(Paragraph("MongoDB &amp; PyMongo Implementation &bull; CA2 Practical Project Report", title_sub))
    story.append(Spacer(1, 4))

    meta_info = (
        "<b>Student:</b> Ojaswi Bhardwaj &nbsp;|&nbsp; <b>Reg No:</b> 12319444 &nbsp;|&nbsp; "
        "<b>Roll No:</b> 37 &nbsp;|&nbsp; <b>Section:</b> K3P23SD &nbsp;|&nbsp; <b>Subject:</b> CSE494<br/>"
        "<b>GitHub:</b> <font color='#0d9488'><u>https://github.com/ojaswi1234/mongo_project.git</u></font> &nbsp;|&nbsp; "
        "<b>Live App:</b> <font color='#0d9488'><u>https://mongo-project-nwjl.onrender.com</u></font>"
    )
    story.append(Paragraph(meta_info, meta_text))
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#cbd5e1"), spaceBefore=1, spaceAfter=6))

    # Assigned Question Brief
    q1_text = (
        "<b>Assigned Problem (CA2 Q1):</b> <i>Design and implement a MongoDB application demonstrating "
        "document structure design, validation rules, CRUD operations, PyMongo connection, aggregation queries, "
        "and explain query outputs and architectural choices during viva.</i>"
    )
    t_q1 = Table([[Paragraph(q1_text, body_style)]], colWidths=[515])
    t_q1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('LINELEFT', (0, 0), (0, -1), 2.5, colors.HexColor("#0d9488")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_q1)
    story.append(Spacer(1, 6))

    # 1. Problem Selection & Relevance
    story.append(Paragraph("1. Problem Selected & Real-World Clinical Relevance", sec_title))
    p1 = (
        "Hospitals generate continuous streams of clinical data: second-by-second vitals, medications, "
        "physician consults, and billing ledgers. In traditional relational databases (SQL), fetching an active "
        "patient chart requires 6 to 8 table joins, causing read latency and row-locking bottlenecks during emergencies."
    )
    story.append(Paragraph(p1, body_style))
    p2 = (
        "<b>MediTrack</b> leverages MongoDB's document model to solve this. An inpatient's vitals, prescriptions, "
        "and bill items are stored inside a single document. The entire medical chart is fetched in an instant, "
        "single-read O(1) query without joins. Attending nurses can stream new vitals atomically using "
        "<font name='Courier'>$push</font> without locking the parent record."
    )
    story.append(Paragraph(p2, body_style))
    story.append(Spacer(1, 5))

    # 2. Database and Document Design
    story.append(Paragraph("2. Database Architecture & Document Design (Hybrid Model)", sec_title))
    p3 = (
        "The project applies a production <b>Hybrid Data Modeling Pattern</b> to balance read speed and storage:"
    )
    story.append(Paragraph(p3, body_style))
    story.append(Paragraph(
        "&bull; <b>Embedded Pattern (patients):</b> Vitals history, prescriptions, and billing are embedded. "
        "They have a 1-to-few bounded relationship (&lt;50 items per stay) and are always queried together with the patient.",
        bullet_style
    ))
    story.append(Paragraph(
        "&bull; <b>Referenced Pattern (doctors):</b> Doctors are stored in a separate collection and referenced "
        "via <font name='Courier'>assigned_doctor_id</font>. A single physician treats thousands of patients over time (unbounded 1:N). "
        "Referencing prevents duplicate physician records and update anomalies.",
        bullet_style
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Sample Inpatient BSON Document (patients collection):", sub_title))
    sample_doc = (
        "{\n"
        '  "_id": ObjectId("6712ab4e8910cd1234567890"),\n'
        '  "patient_id": "PAT-1001",                   // Validated format (^PAT-[0-9]{4}$)\n'
        '  "name": "Robert Miller", "age": 62, "gender": "Male", "blood_group": "A+",\n'
        '  "department": "Cardiology", "status": "Admitted", "assigned_doctor_id": "DOC-201",\n'
        '  "vitals_history": [                         // Embedded Time-Series Array\n'
        '    { "timestamp": ISODate("2026-10-18T08:00:00Z"), "heart_rate": 105, "oxygen_level": 94 }\n'
        '  ],\n'
        '  "prescriptions": [                          // Embedded Medications\n'
        '    { "medicine": "Atorvastatin", "dosage": "20mg", "days": 30 }\n'
        '  ],\n'
        '  "billing": { "room_charges": 1600.0, "total_amount": 2330.0, "payment_status": "Paid" }\n'
        "}"
    )
    story.append(make_code_box(sample_doc, font_size=8.0, leading=10.5))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: VALIDATION, PYMONGO & CRUD OPERATIONS
    # =========================================================================

    # 3. Validation Rules
    story.append(Paragraph("3. Validation Rules Implemented ($jsonSchema)", sec_title))
    p_val = (
        "Database-level schema validation prevents corrupt or invalid clinical records from being saved. "
        "MongoDB enforces validation rules using <font name='Courier'>$jsonSchema</font> with <font name='Courier'>validationAction: 'error'</font>:"
    )
    story.append(Paragraph(p_val, body_style))
    story.append(Paragraph(
        "&bull; <b>Standardized ID:</b> <font name='Courier'>patient_id</font> must match regex pattern <font name='Courier'>^PAT-[0-9]{4}$</font> (e.g., PAT-1001).",
        bullet_style
    ))
    story.append(Paragraph(
        "&bull; <b>Sanity Bounds:</b> <font name='Courier'>age</font> must be an integer between 0 and 125. Telemetry heart rate and oxygen levels are restricted to valid physiological ranges.",
        bullet_style
    ))
    story.append(Paragraph(
        "&bull; <b>Clinical Enumerations:</b> <font name='Courier'>gender</font> ('Male', 'Female', 'Other') and <font name='Courier'>status</font> ('Admitted', 'Under Observation', 'Discharged', 'Archived').",
        bullet_style
    ))
    story.append(Spacer(1, 2))

    val_test = (
        "// Negative Test: Attempting to insert an invalid document\n"
        "db.patients.insertOne({ patient_id: 'INVALID_ID', age: 160, gender: 'Alien' })\n"
        "// Result: pymongo.errors.WriteError: Document failed validation"
    )
    story.append(make_code_box(val_test, font_size=8.0, leading=10.5))
    story.append(Spacer(1, 6))

    # 4. PyMongo Implementation & Indexing
    story.append(Paragraph("4. PyMongo Implementation & Index Architecture", sec_title))
    p_pymongo = (
        "The Python backend connects to MongoDB using PyMongo with connection pooling and automated failover:"
    )
    story.append(Paragraph(p_pymongo, body_style))

    pymongo_code = (
        "from pymongo import MongoClient\n"
        "\n"
        "# Connection Pooling with timeout failover\n"
        "client = MongoClient(MONGODB_URI, maxPoolSize=50, serverSelectionTimeoutMS=2500)\n"
        "db = client['smarthospital']\n"
        "\n"
        "# 1. Unique Primary Index: Fast O(1) lookups and prevents duplicate IDs\n"
        "db.patients.create_index([('patient_id', 1)], unique=True)\n"
        "\n"
        "# 2. Compound Census Index: Speeds up filtered ward census queries\n"
        "db.patients.create_index([('department', 1), ('status', 1)])"
    )
    story.append(make_code_box(pymongo_code, font_size=8.0, leading=10.5))
    story.append(Spacer(1, 6))

    # 5. CRUD Queries Used
    story.append(Paragraph("5. CRUD Queries Used (Implementation & Operators)", sec_title))
    p_crud = (
        "The application performs safe atomic CRUD operations without read-modify-write race conditions:"
    )
    story.append(Paragraph(p_crud, body_style))

    crud_code = (
        "# 1. CREATE: Insert validated patient record\n"
        "db.patients.insert_one(patient_doc)\n"
        "\n"
        "# 2. READ: Filtered query with field projection\n"
        "cardio_patients = db.patients.find(\n"
        "    {'department': 'Cardiology', 'status': 'Admitted'},\n"
        "    {'name': 1, 'age': 1, 'blood_group': 1, 'billing.total_amount': 1}\n"
        ")\n"
        "\n"
        "# 3. READ ($elemMatch): Matches vitals breached in the exact same reading\n"
        "critical_cases = db.patients.find({\n"
        "    'vitals_history': {'$elemMatch': {'heart_rate': {'$gte': 100}, 'oxygen_level': {'$lte': 95}}}\n"
        "})\n"
        "\n"
        "# 4. UPDATE ($push & $inc): Atomic vitals append and billing calculation\n"
        "db.patients.update_one({'patient_id': 'PAT-1001'}, {'$push': {'vitals_history': new_vital}})\n"
        "db.patients.update_one({'patient_id': 'PAT-1001'}, {'$inc': {'billing.total_amount': 250.0}})\n"
        "\n"
        "# 5. DELETE: HIPAA-compliant soft delete (archives record instead of hard removal)\n"
        "db.patients.update_one({'patient_id': 'PAT-1001'}, {'$set': {'status': 'Archived', 'is_archived': True}})"
    )
    story.append(make_code_box(crud_code, font_size=7.8, leading=10.2))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: AGGREGATION PIPELINES & QUERY OUTPUTS
    # =========================================================================

    # 6. Aggregation Pipelines Used
    story.append(Paragraph("6. Aggregation Pipelines Used", sec_title))
    p_agg = (
        "MongoDB's Aggregation Framework executes server-side pipelines to process clinical analytics in real time:"
    )
    story.append(Paragraph(p_agg, body_style))
    story.append(Spacer(1, 2))

    agg_code = (
        "# Pipeline 1: Department Census & Financial Distribution ($match -> $group -> $sort)\n"
        "dept_analytics = list(db.patients.aggregate([\n"
        "    { '$match': { 'status': { '$ne': 'Archived' } } },\n"
        "    { '$group': {\n"
        "        '_id': '$department',\n"
        "        'total_patients': { '$sum': 1 },\n"
        "        'total_revenue': { '$sum': '$billing.total_amount' },\n"
        "        'avg_age': { '$avg': '$age' }\n"
        "    }},\n"
        "    { '$sort': { 'total_revenue': -1 } }\n"
        "]))\n"
        "\n"
        "# Pipeline 2: Doctor Caseload with Cross-Collection Join ($lookup -> $project -> $sort)\n"
        "doc_workload = list(db.doctors.aggregate([\n"
        "    { '$lookup': {\n"
        "        'from': 'patients',\n"
        "        'localField': 'doctor_id',\n"
        "        'foreignField': 'assigned_doctor_id',\n"
        "        'as': 'cases'\n"
        "    }},\n"
        "    { '$project': {\n"
        "        'name': 1, 'department': 1,\n"
        "        'patient_count': { '$size': '$cases' }\n"
        "    }},\n"
        "    { '$sort': { 'patient_count': -1 } }\n"
        "]))\n"
        "\n"
        "# Pipeline 3: Critical Vitals Triage Anomaly Alert ($unwind -> $match -> $project)\n"
        "triage_alerts = list(db.patients.aggregate([\n"
        "    { '$unwind': '$vitals_history' },\n"
        "    { '$match': {\n"
        "        '$or': [\n"
        "            { 'vitals_history.heart_rate': { '$gte': 100 } },\n"
        "            { 'vitals_history.oxygen_level': { '$lte': 95 } }\n"
        "        ]\n"
        "    }},\n"
        "    { '$project': { 'patient_id': 1, 'name': 1, 'vitals': '$vitals_history' } }\n"
        "]))"
    )
    story.append(make_code_box(agg_code, font_size=7.8, leading=10.2))
    story.append(Spacer(1, 6))

    # 7. Output Obtained from the Queries
    story.append(Paragraph("7. Output Obtained from the Queries (Verified Test Results)", sec_title))
    p_out = (
        "Actual outputs obtained from automated test script execution (<font name='Courier'>scripts/run_demo.py</font>):"
    )
    story.append(Paragraph(p_out, body_style))
    story.append(Spacer(1, 2))

    out_block = (
        "1. Schema Validation Rejection Test:\n"
        "   Insert: patient_id='INVALID_ID', age=160\n"
        "   Result: [OK] WriteError: Document failed validation rules.\n"
        "\n"
        "2. Department Analytics Pipeline ($group & $sort):\n"
        "   • Orthopedics : 1 Patient  | Total Revenue: $3,940.00 | Avg Age: 71.0 yrs\n"
        "   • Cardiology  : 3 Patients | Total Revenue: $3,835.00 | Avg Age: 48.7 yrs\n"
        "   • Neurology   : 1 Patient  | Total Revenue: $1,310.00 | Avg Age: 45.0 yrs\n"
        "\n"
        "3. Doctor Caseload Pipeline ($lookup):\n"
        "   • Dr. Sarah Jenkins (Cardiology)  : 3 assigned patients\n"
        "   • Dr. Michael Chen  (Neurology)   : 1 assigned patient\n"
        "\n"
        "4. Critical Vitals Triage Alert ($unwind & $match):\n"
        "   • PAT-1005 (Ethan Wright)  : HR = 118 BPM, SpO2 = 93% -> CRITICAL\n"
        "   • PAT-1001 (Robert Miller) : HR = 105 BPM, SpO2 = 94% -> CRITICAL\n"
        "   • PAT-1004 (Amina Morales) : HR = 115 BPM, SpO2 = 95% -> URGENT"
    )
    story.append(make_code_box(out_block, font_size=8.0, leading=10.5))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: VIVA DEFENSE, DELIVERABLES & SIGN-OFF
    # =========================================================================

    # 8. Why Particular Queries or Structures Were Selected
    story.append(Paragraph("8. Why Particular Queries or Structures Were Selected (Viva Defense)", sec_title))
    p_viva_intro = (
        "Key architectural justifications formatted for oral presentation and viva defense:"
    )
    story.append(Paragraph(p_viva_intro, body_style))

    story.append(Paragraph("Q: Why embed vitals and prescriptions instead of using separate collections?", viva_q))
    story.append(Paragraph(
        "<b>A:</b> High read locality. Doctors and nurses view vitals and medications together on almost every chart lookup. "
        "Because vitals are bounded (&lt;50 readings per hospital stay), embedding avoids slow table joins and provides instant O(1) single-document reads.",
        viva_a
    ))

    story.append(Paragraph("Q: Why reference doctors instead of embedding them?", viva_q))
    story.append(Paragraph(
        "<b>A:</b> One doctor treats thousands of patients over years (an unbounded 1-to-many relationship). "
        "Embedding doctor profiles would duplicate data across thousands of records and cause update anomalies when doctor fees or details change.",
        viva_a
    ))

    story.append(Paragraph("Q: Why use atomic operators ($push, $inc) instead of find-and-save in Python?", viva_q))
    story.append(Paragraph(
        "<b>A:</b> Multiple healthcare workers modify patient charts concurrently. Atomic operators update data directly inside the MongoDB engine, "
        "preventing lost updates and race conditions without requiring heavy multi-document locks.",
        viva_a
    ))

    story.append(Paragraph("Q: Why use $elemMatch for telemetry queries instead of dot notation?", viva_q))
    story.append(Paragraph(
        "<b>A:</b> Standard dot queries match if <i>any</i> reading has high heart rate and <i>any other</i> reading has low oxygen. "
        "<font name='Courier'>$elemMatch</font> guarantees that both abnormal thresholds occurred in the <b>exact same measurement event</b>, preventing false triage alerts.",
        viva_a
    ))
    story.append(Spacer(1, 4))

    # 9. Deliverables Summary
    story.append(Paragraph("9. Project Deliverables Summary", sec_title))
    story.append(Paragraph(
        "&bull; <b>Working Application Code:</b> Clean Flask &amp; PyMongo codebase (<font name='Courier'>app.py</font>) &bull; GitHub: <font color='#0d9488'><u>https://github.com/ojaswi1234/mongo_project.git</u></font><br/>"
        "&bull; <b>Live Cloud Deployment:</b> Deployed on Render: <font color='#0d9488'><u>https://mongo-project-nwjl.onrender.com</u></font><br/>"
        "&bull; <b>Automated Test Suite:</b> Execution script (<font name='Courier'>python scripts/run_demo.py</font>) generating <font name='Courier'>output_demonstration.txt</font><br/>"
        "&bull; <b>Project Presentation:</b> Slide deck summarizing queries and architecture (<font name='Courier'>SmartHospital_Presentation.pdf</font>)",
        bullet_style
    ))
    story.append(Spacer(1, 8))

    # 10. Academic Sign-Off Block
    story.append(Paragraph("10. Academic Evaluation &amp; Submission Sign-Off", sec_title))
    sign_data = [
        [
            Paragraph(
                "<b>Student Declaration:</b><br/>"
                "I declare that this project, queries, and report are my original work for CSE494 CA2.<br/><br/>"
                "<b>Signature:</b> ___________________________<br/>"
                "<b>Name:</b> Ojaswi Bhardwaj (Reg: 12319444)<br/>"
                "<b>Date:</b> 19<sup>th</sup> October, 2026",
                body_style
            ),
            Paragraph(
                "<b>Faculty Evaluator:</b><br/>"
                "Project demonstration, database schema, queries, and viva defense evaluated.<br/><br/>"
                "<b>Signature:</b> ___________________________<br/>"
                "<b>Marks Awarded:</b> _________ / 30<br/>"
                "<b>Date:</b> ___________________________",
                body_style
            )
        ]
    ]
    t_sign = Table(sign_data, colWidths=[252, 252])
    t_sign.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor("#0f172a")),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_sign)

    # Build Document
    doc.build(story, canvasmaker=LPUAcademicCanvas)
    print(f"[OK] Report PDF successfully generated: {filename}")


if __name__ == "__main__":
    output_pdf = os.path.join(os.path.dirname(__file__), "..", "SmartHospital_Project_Report.pdf")
    build_report_pdf(output_pdf)
    docs_pdf = os.path.join(os.path.dirname(__file__), "..", "docs", "SmartHospital_Project_Report.pdf")
    build_report_pdf(docs_pdf)
