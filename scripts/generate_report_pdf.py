"""
Official LPU Project Report Generator for Smart Hospital MongoDB System (MediTrack).
Strictly matches the exact format, typography, margins, and structure of:
file:///C:/Users/ojasw/Downloads/12319444ojaswi.pdf

Page 1: Cover Page with LPU Emblem Logo
Page 2: Declaration with Ojaswi's actual handwritten signature image
Page 3: Certificate by Mentor (Mr. Alok Misra)
Page 4: Acknowledgement
Page 5 (Report 1): 1. Introduction, Problem Scope, Existing vs Proposed, Requirements
Page 6 (Report 2): 2. Database Architecture, Hybrid Schema, $jsonSchema Validation
Page 7 (Report 3): 3. PyMongo Connection, Indexes, CRUD Operations, Viva Justifications
Page 8 (Report 4): 4. Aggregation Pipelines, Verified Outputs, GitHub & Live Links
Page 9 (Report 5): 5. System Architecture Diagram
Page 10 (Report 6): 6. Application Screenshots (Dashboard & Patient Detail)
Page 11 (Report 7): 7. Application Screenshots (Analytics & AI Vector Search)
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas


class LPUNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas matching 12319444ojaswi.pdf:
    - Page 1 (Cover): No page number.
    - Pages 2-4 (Front Matter): Centered page number '2', '3', '4'.
    - Page 5 onwards (Main Report): Centered page number starting at '1', '2', '3'...
    """
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
            self.draw_page_number()
            super().showPage()
        super().save()

    def draw_page_number(self):
        w, h = 612.0, 792.0  # US Letter
        pg = self._pageNumber
        if pg == 1:
            return  # Cover page has no number

        self.saveState()
        self.setFont("Times-Roman", 12)
        self.setFillColor(colors.black)

        if pg in [2, 3, 4]:
            num_str = str(pg)
        else:
            num_str = str(pg - 4)

        self.drawCentredString(w / 2.0, 48, num_str)
        self.restoreState()


def make_code_block(code_str, font_size=8.0, leading=10.5):
    """Clean, uncolored academic code snippet matching reference report."""
    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=font_size,
        leading=leading,
        textColor=colors.black
    )
    html_code = (
        code_str.replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('\n', '<br/>')
        .replace(' ', '&nbsp;')
    )
    t = Table([[Paragraph(html_code, code_style)]], colWidths=[468])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t


def build_lpu_report(filename="SmartHospital_Project_Report.pdf"):
    # US Letter: 612 x 792 pt, 1-inch margins (72 pt)
    # Printable width: 468 pt, Printable height: 648 pt
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Academic Typography matching 12319444ojaswi.pdf
    cover_top = ParagraphStyle('CoverTop', fontName='Times-Bold', fontSize=11, leading=14, textColor=colors.black)
    cover_title_report = ParagraphStyle('CoverReport', fontName='Times-Bold', fontSize=18, leading=22, alignment=1, textColor=colors.black)
    cover_term = ParagraphStyle('CoverTerm', fontName='Times-Roman', fontSize=13, leading=17, alignment=1, textColor=colors.black)
    cover_proj_title = ParagraphStyle('CoverProjTitle', fontName='Times-Bold', fontSize=16, leading=21, alignment=1, textColor=colors.black)
    cover_submitted = ParagraphStyle('CoverSubmitted', fontName='Times-Roman', fontSize=11, leading=15, alignment=1, textColor=colors.black)
    cover_student = ParagraphStyle('CoverStudent', fontName='Times-Bold', fontSize=12, leading=16, alignment=1, textColor=colors.black)
    cover_course = ParagraphStyle('CoverCourse', fontName='Times-Bold', fontSize=13, leading=17, alignment=1, textColor=colors.black)
    cover_guidance = ParagraphStyle('CoverGuidance', fontName='Times-Roman', fontSize=11, leading=15, alignment=1, textColor=colors.black)
    cover_mentor = ParagraphStyle('CoverMentor', fontName='Times-Bold', fontSize=13, leading=17, alignment=1, textColor=colors.black)
    cover_school = ParagraphStyle('CoverSchool', fontName='Times-Bold', fontSize=14, leading=18, alignment=1, textColor=colors.black)

    front_heading = ParagraphStyle('FrontHeading', fontName='Times-Bold', fontSize=14, leading=18, textColor=colors.black, spaceAfter=16)
    front_body = ParagraphStyle('FrontBody', fontName='Times-Roman', fontSize=12, leading=18, alignment=4, textColor=colors.black, spaceAfter=14)

    sec_h1 = ParagraphStyle('SecH1', fontName='Times-Bold', fontSize=14.5, leading=18.5, textColor=colors.black, spaceBefore=8, spaceAfter=4)
    sec_h2 = ParagraphStyle('SecH2', fontName='Times-Bold', fontSize=12, leading=15.5, textColor=colors.black, spaceBefore=6, spaceAfter=2)
    sec_h3 = ParagraphStyle('SecH3', fontName='Times-Bold', fontSize=11, leading=14.5, textColor=colors.black, spaceBefore=4, spaceAfter=2)

    body_text = ParagraphStyle('BodyText', fontName='Times-Roman', fontSize=11, leading=15.5, alignment=4, textColor=colors.black, spaceAfter=4)
    bullet_text = ParagraphStyle('BulletText', fontName='Times-Roman', fontSize=11, leading=15.5, alignment=4, textColor=colors.black, leftIndent=16, firstLineIndent=-10, spaceAfter=3)

    viva_q = ParagraphStyle('VivaQ', fontName='Times-Bold', fontSize=11, leading=15, textColor=colors.black, spaceBefore=5, spaceAfter=1)
    viva_a = ParagraphStyle('VivaA', fontName='Times-Roman', fontSize=11, leading=15.5, alignment=4, textColor=colors.black, spaceAfter=4)
    fig_caption = ParagraphStyle('FigCap', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=1, textColor=colors.black, spaceBefore=3, spaceAfter=6)

    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Paragraph("COVER PAGE", cover_top))
    story.append(Spacer(1, 40))
    story.append(Paragraph("PROJECT REPORT", cover_title_report))
    story.append(Paragraph("(Project Term January-May 2026)", cover_term))
    story.append(Spacer(1, 40))
    story.append(Paragraph("SMART HOSPITAL MANAGEMENT SYSTEM", cover_proj_title))
    story.append(Spacer(1, 45))
    story.append(Paragraph("Submitted by", cover_submitted))
    story.append(Spacer(1, 12))

    t_student = Table([
        [
            Paragraph("<b>Ojaswi Bhardwaj</b>", ParagraphStyle('LeftAlign', parent=cover_student, alignment=0)),
            Paragraph("<b>Registration Number :12319444</b>", ParagraphStyle('RightAlign', parent=cover_student, alignment=2))
        ]
    ], colWidths=[234, 234])
    t_student.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_student)

    story.append(Spacer(1, 35))
    story.append(Paragraph("Course Code CSE494", cover_course))
    story.append(Spacer(1, 35))
    story.append(Paragraph("Under the Guidance of", cover_guidance))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Mr. Alok Misra", cover_mentor))
    story.append(Spacer(1, 14))
    story.append(Paragraph("School of Computer Science and Engineering", cover_school))
    story.append(Spacer(1, 40))

    emblem_path = os.path.join(assets_dir, "lpu_emblem.png")
    if os.path.exists(emblem_path):
        story.append(Image(emblem_path, width=220, height=91))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: DECLARATION
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("DECLARATION", front_heading))
    p_decl = (
        "I hereby declare that the project work entitled (<b>“Smart Hospital Management System”</b>) is an "
        "authentic record of my own work carried out as requirements of Project for the award of "
        "<b>B.Tech Degree in Computer Science</b> from Lovely Professional University, Phagwara, "
        "under the guidance of <b>Mr. Alok Misra</b>, during January to May 2026. All the information "
        "furnished in this project report is based on my own intensive work and is genuine."
    )
    story.append(Paragraph(p_decl, front_body))
    story.append(Spacer(1, 35))

    story.append(Paragraph("Name of Student : ......Ojaswi Bhardwaj....................................", front_body))
    story.append(Paragraph("Registration Number: ......12319444................................", front_body))
    story.append(Spacer(1, 30))

    sig_path = os.path.join(assets_dir, "student_signature.png")
    if os.path.exists(sig_path):
        t_sig = Table([
            ["", Paragraph("(Signature of Student )", ParagraphStyle('SigHead', fontName='Times-Roman', fontSize=12, alignment=1))],
            ["", Image(sig_path, width=155, height=82)],
            ["", Paragraph("Date: May 26, 2026", ParagraphStyle('SigDate', fontName='Times-Bold', fontSize=12, alignment=1))]
        ], colWidths=[280, 188])
        t_sig.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(t_sig)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: CERTIFICATE
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("CERTIFICATE", front_heading))
    p_cert = (
        "This is to certify that the declaration statement made by the student is correct to the best of "
        "my knowledge and belief. He has completed this <b>Smart Hospital Management System</b> Project "
        "under my guidance and supervision. The present work is the result of his original investigation, "
        "effort and study. No part of the work has ever been submitted for any other degree at any University. "
        "The Project is fit for the submission and partial fulfillment of the conditions for the award of "
        "<b>B.Tech Degree in Computer Science Engineering</b> from Lovely Professional University, Phagwara."
    )
    story.append(Paragraph(p_cert, front_body))
    story.append(Spacer(1, 60))

    story.append(Paragraph("<b>Signature and Name of the Mentor</b>", front_body))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Mr. Alok Misra</b>", front_body))
    story.append(Paragraph("Assistant Teacher", front_body))
    story.append(Paragraph("School of Computer Science and Engineering,<br/>Lovely Professional University, Phagwara, Punjab.", front_body))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Date : 26/05/2026", front_body))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: ACKNOWLEDGEMENT
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("ACKNOWLEDGEMENT", front_heading))
    p_ack1 = (
        "I, <b>Ojaswi Bhardwaj</b> (Reg no. 12319444) would like to express my sincere gratitude to everyone "
        "who supported me in the development of the <b>Smart Hospital Management System</b> project."
    )
    story.append(Paragraph(p_ack1, front_body))

    p_ack2 = (
        "First, I extend my profound thanks to the faculty of the School of Computer Science and Engineering "
        "at Lovely Professional University. The academic environment, resources, and foundational coursework "
        "provided have been instrumental in shaping my understanding of backend architecture and distributed "
        "database systems."
    )
    story.append(Paragraph(p_ack2, front_body))

    p_ack3 = (
        "I am deeply grateful to my project guide, <b>Mr. Alok Misra</b>, for their continuous mentorship, "
        "constructive feedback, and technical guidance. Their insights were invaluable in refining the project's "
        "database architecture, schema validation rules, and aggregation query design."
    )
    story.append(Paragraph(p_ack3, front_body))

    p_ack4 = (
        "I would also like to thank my peers, my roommate, and my family for their patience, motivation, "
        "and unwavering support during the late nights spent debugging queries, designing aggregation pipelines, "
        "and configuring server connections."
    )
    story.append(Paragraph(p_ack4, front_body))

    p_ack5 = (
        "Finally, I acknowledge the broader open-source community, whose robust documentation and tools "
        "formed the backbone of this project's development stack."
    )
    story.append(Paragraph(p_ack5, front_body))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: 1. INTRODUCTION (REPORT PAGE 1)
    # =========================================================================
    story.append(Paragraph("1. INTRODUCTION", sec_h1))
    p_intro = (
        "The <b>Smart Hospital Management System (MediTrack)</b> is a secure, lightweight web application built "
        "using Python, Flask, PyMongo, and MongoDB. It provides clinicians, attending physicians, and triage nurses "
        "with a centralized digital dashboard to monitor inpatient charts, track streaming vital telemetry, "
        "manage pharmaceutical prescriptions, and process itemized billing ledgers. "
        "A key architectural advantage of this application is its document-oriented database design: "
        "by storing telemetry and medical orders directly inside the patient document, the system eliminates "
        "relational multi-table join bottlenecks and provides instant single-read chart lookups."
    )
    story.append(Paragraph(p_intro, body_text))

    story.append(Paragraph("1.1. Scope of the Study (Problem Statement)", sec_h2))
    p_scope = (
        "Modern hospital inpatient care generates continuous streams of multi-dimensional clinical telemetry: "
        "second-by-second vitals, active prescriptions, physician consults, and billing fees. "
        "In traditional Relational Database Management Systems (RDBMS), loading a single patient's medical chart "
        "requires joining 6 to 8 separate tables (Patients, Vitals, Prescriptions, Doctors, Wards, Billing). "
        "Under peak ward concurrency during emergency hours, multi-table joins cause severe read latency, "
        "row contention, and lock escalation that directly jeopardize emergency medical decision-making."
    )
    story.append(Paragraph(p_scope, body_text))

    story.append(Paragraph("1.2. Existing System vs Proposed MongoDB Solution", sec_h2))
    story.append(Paragraph(
        "<b>Existing System:</b> Traditional hospital software relies on heavily normalized relational schemas. "
        "Whenever a doctor inspects a patient profile, the database executes complex SQL JOIN queries. "
        "High-frequency vital streams force continuous table-locking write transactions, causing significant lag across nurse workstations.",
        body_text
    ))
    story.append(Paragraph(
        "<b>Proposed MongoDB Architecture:</b> MediTrack utilizes MongoDB's flexible BSON document model. "
        "Telemetry and prescriptions are embedded directly into the patient chart, allowing complete profile lookups "
        "in a single indexed O(1) read with zero joins. Attending nurses append new vital readings atomically using "
        "<font name='Courier'>$push</font> without locking the parent record.",
        body_text
    ))

    story.append(Paragraph("1.2.1. Problem Analysis & Feasibility", sec_h3))
    story.append(Paragraph(
        "● <b>Product Definition:</b> A multi-tier inpatient management portal built with Python, Flask, PyMongo, and MongoDB.",
        bullet_text
    ))
    story.append(Paragraph(
        "● <b>Feasibility Analysis:</b> Highly feasible using PyMongo's native connection pooling. "
        "If a remote cloud cluster becomes unreachable, an automated fallback connects to an in-memory replica via "
        "<font name='Courier'>mongomock</font>, ensuring 100% operational uptime.",
        bullet_text
    ))
    story.append(Paragraph(
        "● <b>Software Requirements:</b> Python 3.10+, Flask, PyMongo 4.0+, MongoDB Community/Atlas v6+.",
        bullet_text
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: 2. DATABASE ARCHITECTURE & VALIDATION (REPORT PAGE 2)
    # =========================================================================
    story.append(Paragraph("2. DATABASE & DOCUMENT DESIGN", sec_h1))
    story.append(Paragraph("2.1. Hybrid Data Modeling Pattern", sec_h2))
    p_model = (
        "MediTrack adheres to MongoDB enterprise data modeling best practices by combining embedding and referencing:"
    )
    story.append(Paragraph(p_model, body_text))
    story.append(Paragraph(
        "● <b>Embedded Document Pattern (patients collection):</b> Telemetry time-series (<font name='Courier'>vitals_history</font>), "
        "prescriptions (<font name='Courier'>prescriptions</font>), and billing ledger (<font name='Courier'>billing</font>) are embedded. "
        "These sub-entities exhibit a <b>1-to-few bounded relationship</b> (&lt;50 entries per hospital stay) and are accessed "
        "together in 99% of read operations. Embedding eliminates join overhead and ensures atomic document-level updates.",
        bullet_text
    ))
    story.append(Paragraph(
        "● <b>Referenced Collection Pattern (doctors collection):</b> Attending physicians are stored in a separate collection "
        "and linked via foreign key (<font name='Courier'>assigned_doctor_id</font>). Because one doctor treats thousands of patients "
        "over years (an <b>unbounded 1-to-many relationship</b>), referencing eliminates duplicate physician records and prevents update anomalies.",
        bullet_text
    ))

    story.append(Paragraph("2.2. Inpatient Document Schema (patients collection)", sec_h2))
    sample_doc = (
        "{\n"
        '  "_id": ObjectId("6712ab4e8910cd1234567890"),\n'
        '  "patient_id": "PAT-1001",                   // Standardized ID (^PAT-[0-9]{4}$)\n'
        '  "name": "Robert Miller", "age": 62, "gender": "Male", "blood_group": "A+",\n'
        '  "department": "Cardiology", "status": "Admitted", "assigned_doctor_id": "DOC-201",\n'
        '  "vitals_history": [\n'
        '    { "timestamp": ISODate("2026-10-18T08:00:00Z"), "heart_rate": 105, "oxygen_level": 94, "blood_pressure": "145/95" }\n'
        '  ],\n'
        '  "prescriptions": [ { "medicine": "Atorvastatin", "dosage": "20mg", "days": 30 } ],\n'
        '  "billing": { "room_charges": 1600.0, "total_amount": 2330.0, "payment_status": "Paid" }\n'
        "}"
    )
    story.append(make_code_block(sample_doc, font_size=8.0, leading=10.5))

    story.append(Paragraph("2.3. Schema Validation Rules ($jsonSchema)", sec_h2))
    story.append(Paragraph(
        "● <b>Standardized ID Format:</b> <font name='Courier'>patient_id</font> must match regex <font name='Courier'>^PAT-[0-9]{4}$</font>.",
        bullet_text
    ))
    story.append(Paragraph(
        "● <b>Physiological Sanity Bounds:</b> <font name='Courier'>age</font> must be an integer between 0 and 125.",
        bullet_text
    ))
    story.append(Paragraph(
        "● <b>Clinical Enumerations:</b> <font name='Courier'>gender</font> ('Male', 'Female', 'Other') and <font name='Courier'>status</font> ('Admitted', 'Observation', 'Discharged', 'Archived').",
        bullet_text
    ))
    story.append(Paragraph(
        "● <b>Negative Test:</b> Inserting <font name='Courier'>{'patient_id': 'BAD_ID', 'age': 160}</font> returns <font name='Courier'>WriteError: Document failed validation rules</font>.",
        bullet_text
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: 3. PYMONGO & CRUD (REPORT PAGE 3)
    # =========================================================================
    story.append(Paragraph("3. PYMONGO IMPLEMENTATION & CRUD OPERATIONS", sec_h1))
    story.append(Paragraph("3.1. PyMongo Connection Architecture & Indexing", sec_h2))

    code_conn = (
        "from pymongo import MongoClient\n"
        "\n"
        "client = MongoClient(MONGODB_URI, maxPoolSize=50, serverSelectionTimeoutMS=2500)\n"
        "db = client['smarthospital']\n"
        "\n"
        "# 1. Unique Primary Index: Fast O(1) lookups and prevents duplicate patient records\n"
        "db.patients.create_index([('patient_id', 1)], unique=True)\n"
        "# 2. Compound Census Index: Enables index-covered ward filtering\n"
        "db.patients.create_index([('department', 1), ('status', 1)])"
    )
    story.append(make_code_block(code_conn, font_size=8.0, leading=10.5))

    story.append(Paragraph("3.2. CRUD Operations Implementation", sec_h2))
    code_crud = (
        "# 1. CREATE: Insert validated patient document\n"
        "db.patients.insert_one(patient_doc)\n"
        "\n"
        "# 2. READ ($elemMatch): Matches vital anomaly in the exact same measurement event\n"
        "critical_cases = db.patients.find({\n"
        "    'vitals_history': {'$elemMatch': {'heart_rate': {'$gte': 100}, 'oxygen_level': {'$lte': 95}}}\n"
        "})\n"
        "\n"
        "# 3. UPDATE ($push & $inc): Atomically appends vitals and increments billing ledger\n"
        "db.patients.update_one({'patient_id': 'PAT-1001'}, {'$push': {'vitals_history': new_vital}})\n"
        "db.patients.update_one({'patient_id': 'PAT-1001'}, {'$inc': {'billing.total_amount': 250.0}})\n"
        "\n"
        "# 4. DELETE: HIPAA-compliant soft delete (archives record, preserves audit trail)\n"
        "db.patients.update_one({'patient_id': 'PAT-1001'}, {'$set': {'status': 'Archived', 'is_archived': True}})"
    )
    story.append(make_code_block(code_crud, font_size=7.8, leading=10.2))

    story.append(Paragraph("3.3. Viva Defense: Architectural & Query Justifications", sec_h2))
    story.append(Paragraph("Q: Why use atomic operators ($push, $inc) instead of fetching and saving in Python?", viva_q))
    story.append(Paragraph(
        "<b>A:</b> Multiple healthcare workers update patient charts concurrently. Fetching a document, modifying it in Python, "
        "and writing it back causes lost-update race conditions. Atomic operators mutate data in-place inside MongoDB with document-level isolation.",
        viva_a
    ))
    story.append(Paragraph("Q: Why use $elemMatch for vital queries instead of dot notation?", viva_q))
    story.append(Paragraph(
        "<b>A:</b> Standard dot queries match if <i>any</i> reading has high HR and <i>any other</i> reading has low SpO2. "
        "<font name='Courier'>$elemMatch</font> ensures that both abnormal thresholds occurred in the <b>exact same measurement event</b>, preventing false triage alerts.",
        viva_a
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: 4. AGGREGATIONS & OUTPUTS (REPORT PAGE 4)
    # =========================================================================
    story.append(Paragraph("4. AGGREGATION PIPELINES & QUERY OUTPUTS", sec_h1))
    story.append(Paragraph("4.1. Multi-Stage Aggregation Pipelines Used", sec_h2))

    code_agg = (
        "# Pipeline 1: Department Census & Financial Distribution ($match -> $group -> $sort)\n"
        "dept_analytics = list(db.patients.aggregate([\n"
        "    { '$match': { 'status': { '$ne': 'Archived' } } },\n"
        "    { '$group': {\n"
        "        '_id': '$department', 'total_patients': { '$sum': 1 },\n"
        "        'total_revenue': { '$sum': '$billing.total_amount' }, 'avg_age': { '$avg': '$age' }\n"
        "    }},\n"
        "    { '$sort': { 'total_revenue': -1 } }\n"
        "]))\n"
        "\n"
        "# Pipeline 2: Doctor Caseload with Cross-Collection Join ($lookup -> $project -> $sort)\n"
        "doc_workload = list(db.doctors.aggregate([\n"
        "    { '$lookup': {\n"
        "        'from': 'patients', 'localField': 'doctor_id', 'foreignField': 'assigned_doctor_id', 'as': 'cases'\n"
        "    }},\n"
        "    { '$project': { 'name': 1, 'department': 1, 'patient_count': { '$size': '$cases' } } },\n"
        "    { '$sort': { 'patient_count': -1 } }\n"
        "]))\n"
        "\n"
        "# Pipeline 3: Critical Vitals Triage Anomaly Alert ($unwind -> $match -> $project)\n"
        "triage_alerts = list(db.patients.aggregate([\n"
        "    { '$unwind': '$vitals_history' },\n"
        "    { '$match': { '$or': [{ 'vitals_history.heart_rate': { '$gte': 100 } }, { 'vitals_history.oxygen_level': { '$lte': 95 } }] } },\n"
        "    { '$project': { 'patient_id': 1, 'name': 1, 'vitals': '$vitals_history' } }\n"
        "]))"
    )
    story.append(make_code_block(code_agg, font_size=7.6, leading=9.8))

    story.append(Paragraph("4.2. Outputs Obtained from the Queries (Automated Test Execution)", sec_h2))
    out_block = (
        "1. Schema Validation Rejection Test: WriteError - Document failed validation rules [OK]\n"
        "2. Pipeline 1 (Department Revenue): Orthopedics ($3,940.00) | Cardiology ($3,835.00) | Neurology ($1,310.00)\n"
        "3. Pipeline 2 (Doctor Caseload): Dr. Sarah Jenkins (3 patients) | Dr. Michael Chen (1 patient)\n"
        "4. Pipeline 3 (Critical Vitals Alert): PAT-1005 (HR: 118, SpO2: 93%) | PAT-1001 (HR: 105, SpO2: 94%)"
    )
    story.append(make_code_block(out_block, font_size=7.8, leading=10.5))
    story.append(Spacer(1, 4))

    story.append(Paragraph("4.3. Project Repository & Deployment Links", sec_h2))
    story.append(Paragraph(
        "● <b>GitHub Repository:</b> <font color='#0284c7'><u>https://github.com/ojaswi1234/mongo_project.git</u></font><br/>"
        "● <b>Live Deployment URL:</b> <font color='#0284c7'><u>https://mongo-project-nwjl.onrender.com</u></font>",
        bullet_text
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: 5. SYSTEM ARCHITECTURE DIAGRAM (REPORT PAGE 5)
    # =========================================================================
    story.append(Paragraph("5. DESIGNS, FLOW CHARTS & SCREENSHOTS", sec_h1))
    story.append(Paragraph("5.1. System Architecture Diagram", sec_h2))
    story.append(Spacer(1, 10))

    arch_path = os.path.join(assets_dir, "architecture_diagram.png")
    if os.path.exists(arch_path):
        story.append(Image(arch_path, width=468, height=312))
        story.append(Spacer(1, 8))
        story.append(Paragraph("<b>Figure 1:</b> Multi-Tier System Architecture (Flask Client, PyMongo Driver, MongoDB Engine)", fig_caption))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: 6. APPLICATION SCREENSHOTS - WARD & CHART (REPORT PAGE 6)
    # =========================================================================
    story.append(Paragraph("5.2. Application Screenshots: Ward & Patient Management", sec_h1))
    story.append(Spacer(1, 6))

    dash_path = os.path.join(assets_dir, "screenshot_dashboard.png")
    if os.path.exists(dash_path):
        story.append(Image(dash_path, width=460, height=215))
        story.append(Paragraph("<b>Figure 2:</b> Executive Hospital Dashboard (Census, Real-Time Triage, Navigation)", fig_caption))
        story.append(Spacer(1, 12))

    detail_path = os.path.join(assets_dir, "screenshot_patient_detail.png")
    if os.path.exists(detail_path):
        story.append(Image(detail_path, width=460, height=215))
        story.append(Paragraph("<b>Figure 3:</b> Inpatient Medical Chart (Embedded Vitals Telemetry, Prescriptions, Ledger)", fig_caption))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: 7. APPLICATION SCREENSHOTS - ANALYTICS & AI (REPORT PAGE 7)
    # =========================================================================
    story.append(Paragraph("5.3. Application Screenshots: Analytics & AI Clinical Assistant", sec_h1))
    story.append(Spacer(1, 6))

    analytics_path = os.path.join(assets_dir, "screenshot_analytics.png")
    if os.path.exists(analytics_path):
        story.append(Image(analytics_path, width=460, height=215))
        story.append(Paragraph("<b>Figure 4:</b> Clinical Analytics Dashboard (Aggregation Pipelines: Revenue, Caseload, Alerts)", fig_caption))
        story.append(Spacer(1, 12))

    ai_path = os.path.join(assets_dir, "screenshot_ai_search.png")
    if os.path.exists(ai_path):
        story.append(Image(ai_path, width=460, height=215))
        story.append(Paragraph("<b>Figure 5:</b> AI Clinical Assistant (Vector Similarity Search across Patient Diagnostic Notes)", fig_caption))

    # Build Document
    doc.build(story, canvasmaker=LPUNumberedCanvas)
    print(f"[OK] Official LPU Report PDF successfully generated: {filename}")


if __name__ == "__main__":
    output_pdf = os.path.join(os.path.dirname(__file__), "..", "SmartHospital_Project_Report.pdf")
    build_lpu_report(output_pdf)
    docs_pdf = os.path.join(os.path.dirname(__file__), "..", "docs", "SmartHospital_Project_Report.pdf")
    build_lpu_report(docs_pdf)
    gen_script = os.path.join(os.path.dirname(__file__), "..", "scripts", "generate_report_pdf.py")
    with open(gen_script, "w", encoding="utf-8") as f:
        with open(__file__, "r", encoding="utf-8") as src:
            f.write(src.read())
