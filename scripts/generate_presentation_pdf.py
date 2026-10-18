"""
Generates the formal academic Presentation Slide Deck PDF for Smart Hospital MongoDB System.
Uses ReportLab with landscape letter layout (11 x 8.5 in) formatted as high-impact presentation slides
with header banners, structured cards, callouts, and speaking notes.
"""

import os
import sys
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas


class SlideCanvas(canvas.Canvas):
    """Draws slide borders, top accent bars, and bottom slide numbering."""
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
            self.draw_slide_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_slide_decorations(self, total_slides):
        self.saveState()
        w, h = landscape(letter)

        # Omit slide decoration on title slide (Slide 1)
        if self._pageNumber > 1:
            # Top Accent Bar
            self.setFillColor(colors.HexColor("#0f766e"))
            self.rect(0, h - 10, w, 10, fill=True, stroke=False)

            # Bottom Running Footer
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0f766e"))
            self.drawString(40, 24, "MediTrack")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(88, 24, "| MongoDB Healthcare System & AI Vector Search")
            self.drawRightString(w - 40, 24, f"Slide {self._pageNumber} of {total_slides}")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(40, 36, w - 40, 36)

        self.restoreState()


def build_presentation_pdf(filename="SmartHospital_Presentation.pdf"):
    # 11 x 8.5 inches (Landscape Letter)
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=44
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#0f766e")    # Teal-700
    c_dark = colors.HexColor("#0f172a")       # Slate-900
    c_slate = colors.HexColor("#334155")      # Slate-700
    c_muted = colors.HexColor("#64748b")      # Slate-500
    c_indigo = colors.HexColor("#4338ca")     # Indigo-700
    c_card_bg = colors.HexColor("#f8fafc")    # Slate-50
    c_card_border = colors.HexColor("#e2e8f0")

    slide_title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_dark,
        spaceAfter=3
    )

    slide_subtitle_style = ParagraphStyle(
        'SlideSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_primary,
        spaceAfter=14
    )

    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_slate,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'SlideBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_slate,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'SlideCode',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0f766e")
    )

    story = []

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("COURSE OUTCOMES: CO4, CO5, CO6 (LEVEL 2 & 3) — 30 MARKS EVALUATION", ParagraphStyle('TopBadge', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=c_primary, alignment=1, spaceAfter=15)))
    
    t_title = Paragraph("MediTrack: Smart Hospital Care System<br/>with MongoDB & AI Vector Search", ParagraphStyle('BigTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=28, leading=34, textColor=c_dark, alignment=1, spaceAfter=12))
    story.append(t_title)

    t_sub = Paragraph("Designing Document Schemas, Engine Validation ($jsonSchema), Atomic Array Telemetry,<br/>Multi-Stage Aggregation Pipelines, and Clinical Vector Retrieval", ParagraphStyle('BigSub', parent=styles['Normal'], fontName='Helvetica', fontSize=12, leading=17, textColor=c_primary, alignment=1, spaceAfter=30))
    story.append(t_sub)

    info_box = [
        [
            Paragraph("<b>Presenter:</b> <font color='#0f766e'><b>Ojaswi Bhardwaj</b></font>", body_style),
            Paragraph("<b>Reg No:</b> <b>12319444</b> | <b>Roll No:</b> <b>37</b>", body_style),
            Paragraph("<b>Subject:</b> <b>CSE494</b> | <b>Section:</b> <b>K3P23SD</b>", body_style)
        ],
        [
            Paragraph('<b>Live URL:</b> <font color="#0f766e"><a href="https://mongo-project-nwjl.onrender.com"><u>mongo-project-nwjl.onrender.com</u></a></font>', body_style),
            Paragraph('<b>GitHub:</b> <font color="#0f766e"><a href="https://github.com/ojaswi1234/mongo_project.git"><u>github.com/ojaswi1234/mongo_project</u></a></font>', body_style),
            Paragraph("<b>Tech Stack:</b> MongoDB 6.0+ & PyMongo", body_style)
        ]
    ]
    t_info = Table(info_box, colWidths=[3.2 * inch, 3.2 * inch, 3.2 * inch])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdfa")),
        ('BOX', (0, 0), (-1, -1), 1, c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#ccfbf1")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_info)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: THE PROBLEM STATEMENT & REAL-WORLD RELEVANCE
    # =========================================================================
    story.append(Paragraph("1. The Problem Statement & Real-World Relevance", slide_title_style))
    story.append(Paragraph("Why modern clinical environments demand document-oriented architectures over legacy RDBMS", slide_subtitle_style))

    c1 = [
        Paragraph("<b>The Relational Healthcare Bottleneck</b>", card_title_style),
        Paragraph("&bull; In SQL databases, patient charts are fragmented across 8+ normalized tables (Patients, Vitals, Prescriptions, Doctors, Billing).", bullet_style),
        Paragraph("&bull; Retrieving an emergency patient chart requires 5+ table JOINs, causing high latency under concurrent ward loads.", bullet_style),
        Paragraph("&bull; Diagnostic fields evolve constantly (e.g. ICU telemetry, MRI scans), requiring costly schema migrations.", bullet_style)
    ]
    c2 = [
        Paragraph("<b>The MongoDB Solution (MediTrack)</b>", card_title_style),
        Paragraph("&bull; <b>Zero-Join Lookups:</b> Co-locates demographics, continuous vitals, and medications in a single BSON document ($O(1)$ read).", bullet_style),
        Paragraph("&bull; <b>Atomic Streaming:</b> Appends fresh vital telemetry using MongoDB's atomic <font name='Courier'>$push</font> without locking records.", bullet_style),
        Paragraph("&bull; <b>Embedded AI Vector Search:</b> Stores 10-dim clinical symptom vectors directly in the document for semantic matching.", bullet_style)
    ]

    t_s2 = Table([[c1, c2]], colWidths=[4.8 * inch, 4.8 * inch])
    t_s2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#fff1f2")),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#f0fdfa")),
        ('BOX', (0, 0), (0, 0), 1, colors.HexColor("#fecdd3")),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor("#99f6e4")),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_s2)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: HYBRID DATA MODELING (EMBEDDED VS REFERENCED)
    # =========================================================================
    story.append(Paragraph("2. Database Architecture: Hybrid Document Design", slide_title_style))
    story.append(Paragraph("Disciplined engineering balance between high-locality embedding and scalable referencing", slide_subtitle_style))

    box_embed = [
        Paragraph("<b>EMBEDDED DOCUMENTS (1-to-Few)</b>", card_title_style),
        Paragraph("<b>Fields:</b> <font name='Courier'>vitals_history</font>, <font name='Courier'>prescriptions</font>, <font name='Courier'>billing</font>", body_style),
        Paragraph("&bull; <b>High Read Locality:</b> Queried together with the patient in 99% of requests.", bullet_style),
        Paragraph("&bull; <b>Bounded Size:</b> Average 20–50 readings per stay (&lt;10 KB total, far below 16MB BSON limit).", bullet_style),
        Paragraph("&bull; <b>Atomic Mutation:</b> Allows single-operation updates via <font name='Courier'>$push</font> and <font name='Courier'>$inc</font>.", bullet_style)
    ]
    box_ref = [
        Paragraph("<b>REFERENCED COLLECTIONS (1-to-Many)</b>", card_title_style),
        Paragraph("<b>Fields:</b> <font name='Courier'>assigned_doctor_id</font> &rarr; <font name='Courier'>doctors</font> collection", body_style),
        Paragraph("&bull; <b>Unbounded Growth:</b> A doctor treats thousands of patients over years.", bullet_style),
        Paragraph("&bull; <b>Zero Duplication:</b> Doctor profiles, fees, and ratings exist in only one place.", bullet_style),
        Paragraph("&bull; <b>Cross-Collection Analytics:</b> Seamlessly joined in analytics via <font name='Courier'>$lookup</font>.", bullet_style)
    ]

    t_s3 = Table([[box_embed, box_ref]], colWidths=[4.8 * inch, 4.8 * inch])
    t_s3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_card_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_card_border),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_s3)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: SCHEMA VALIDATION ($jsonSchema)
    # =========================================================================
    story.append(Paragraph("3. Engine-Level Schema Validation ($jsonSchema)", slide_title_style))
    story.append(Paragraph("Enforcing strict medical type safety, regex patterns, and range boundaries inside MongoDB", slide_subtitle_style))

    v_left = [
        Paragraph("<b>Validation Specification</b>", card_title_style),
        Paragraph("&bull; <b>patient_id:</b> Regex pattern <font name='Courier'>^PAT-[0-9]{4}$</font>", bullet_style),
        Paragraph("&bull; <b>age:</b> BSON int, minimum 0, maximum 125", bullet_style),
        Paragraph("&bull; <b>gender & blood_group:</b> Strict Enum taxonomies", bullet_style),
        Paragraph("&bull; <b>vitals_history.heart_rate:</b> Int bounds 30–240 BPM", bullet_style),
        Paragraph("&bull; <b>vitals_history.oxygen_level:</b> Int bounds 50–100 SpO2 %", bullet_style),
        Paragraph("&bull; <b>Action:</b> <font name='Courier'>validationAction: 'error'</font> blocks writes.", bullet_style)
    ]
    v_right = [
        Paragraph("<b>Sample Rejection Test Output</b>", card_title_style),
        Paragraph("Testing invalid document insertion:<br/>"
                  "&bull; <font name='Courier'>patient_id: 'INVALID_ID'</font> (violates regex)<br/>"
                  "&bull; <font name='Courier'>age: 155</font> (violates maximum 125)<br/>"
                  "&bull; <font name='Courier'>gender: 'Alien'</font> (violates enum)", body_style),
        Paragraph("<b>Result:</b> <font color='#b91c1c'>WriteError: Document failed validation</font><br/>"
                  "Proves database engine guarantees clinical safety independent of client code.", body_style)
    ]

    t_s4 = Table([[v_left, v_right]], colWidths=[4.8 * inch, 4.8 * inch])
    t_s4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_card_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_card_border),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_s4)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: CRUD OPERATIONS & ARRAY OPERATORS
    # =========================================================================
    story.append(Paragraph("4. PyMongo CRUD Operations & Array Operators", slide_title_style))
    story.append(Paragraph("Demonstrating high-concurrency atomic mutations and simultaneous array condition matching", slide_subtitle_style))

    crud_data = [
        [
            Paragraph("<b>CREATE</b>", card_title_style),
            Paragraph("<b>READ ($elemMatch)</b>", card_title_style),
            Paragraph("<b>UPDATE ($push / $inc)</b>", card_title_style),
            Paragraph("<b>DELETE (Soft Delete)</b>", card_title_style)
        ],
        [
            Paragraph("Inserts validated document with auto-generated 10-dim symptom vector embedding.<br/><br/><font name='Courier'>db.patients.insert_one(doc)</font>", body_style),
            Paragraph("Matches patients where heart_rate &ge; 100 AND SpO2 &le; 95 on the <b>exact same reading</b>.<br/><br/><font name='Courier'>$elemMatch: {hr, spo2}</font>", body_style),
            Paragraph("Appends vitals to array via <font name='Courier'>$push</font>.<br/>Increments billing via <font name='Courier'>$inc</font> with zero read-modify-write race conditions.", body_style),
            Paragraph("HIPAA compliant logical archive.<br/><br/><font name='Courier'>$set: {status: 'Archived', is_archived: True}</font>", body_style)
        ]
    ]
    t_crud = Table(crud_data, colWidths=[2.4 * inch, 2.4 * inch, 2.4 * inch, 2.4 * inch])
    t_crud.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_card_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_card_border),
        ('GRID', (0, 0), (-1, -1), 0.5, c_card_border),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_crud)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: AGGREGATION PIPELINES (OPERATIONS & STAFFING)
    # =========================================================================
    story.append(Paragraph("5. Aggregations: Operations & Staffing Intelligence", slide_title_style))
    story.append(Paragraph("Extracting high-level executive insights without transferring raw collections over the network", slide_subtitle_style))

    p1_box = [
        Paragraph("<b>PIPELINE 1: Department Financials & Volumes</b>", card_title_style),
        Paragraph("<b>Stages:</b> <font name='Courier'>$match &rarr; $group &rarr; $project &rarr; $sort</font>", body_style),
        Paragraph("&bull; Groups all admitted patients by <font name='Courier'>department</font>.", bullet_style),
        Paragraph("&bull; Computes total active census, average age, and aggregate billing.", bullet_style),
        Paragraph("&bull; <b>Result:</b> Orthopedics ($3,940 total, 1 pt), Cardiology ($3,835 total, 3 pts).", bullet_style)
    ]
    p2_box = [
        Paragraph("<b>PIPELINE 2: Doctor Workload ($lookup Join)</b>", card_title_style),
        Paragraph("<b>Stages:</b> <font name='Courier'>$lookup &rarr; $project &rarr; $sort</font>", body_style),
        Paragraph("&bull; Joins <font name='Courier'>doctors</font> with <font name='Courier'>patients</font> where <font name='Courier'>doctor_id == assigned_doctor_id</font>.", bullet_style),
        Paragraph("&bull; Computes caseload size via <font name='Courier'>$size</font> and total billing contribution.", bullet_style),
        Paragraph("&bull; <b>Result:</b> Dr. Sarah Jenkins (3 patients, $3,835 rev), Dr. Emily Taylor (1 patient, $3,940 rev).", bullet_style)
    ]

    t_s6 = Table([[p1_box, p2_box]], colWidths=[4.8 * inch, 4.8 * inch])
    t_s6.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_card_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_card_border),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_s6)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: AGGREGATIONS: CLINICAL & EXECUTIVE INTELLIGENCE
    # =========================================================================
    story.append(Paragraph("6. Aggregations: Clinical Triage & Executive KPI", slide_title_style))
    story.append(Paragraph("Demonstrating array deconstruction ($unwind) and single-query parallel dashboards ($facet)", slide_subtitle_style))

    p34_box = [
        Paragraph("<b>PIPELINE 3: Critical Vitals Triage ($unwind)</b>", card_title_style),
        Paragraph("&bull; Flattens embedded <font name='Courier'>vitals_history</font> array into distinct document stream.", bullet_style),
        Paragraph("&bull; Matches anomalous physiological thresholds (HR &ge; 100 BPM or SpO2 &le; 95%).", bullet_style),
        Paragraph("&bull; Ranks critical patient alerts across hospital by heart rate severity.", bullet_style),
        Spacer(1, 4),
        Paragraph("<b>PIPELINE 4: Pharmacy Prescription Frequency</b>", card_title_style),
        Paragraph("&bull; Flattens <font name='Courier'>prescriptions</font> array and groups by drug name to optimize stock.", bullet_style)
    ]
    p5_box = [
        Paragraph("<b>PIPELINE 5: Executive Multi-Faceted KPI ($facet)</b>", card_title_style),
        Paragraph("<b>Single Database Round-Trip:</b> Executes multiple independent sub-pipelines concurrently on the same input documents:", body_style),
        Paragraph("&bull; <b>Sub-Pipeline A:</b> Inpatient status breakdown (4 Admitted, 1 Observation, 1 Archived).", bullet_style),
        Paragraph("&bull; <b>Sub-Pipeline B:</b> Financial realization breakdown ($5,315 Paid, $3,940 Claimed, $1,455 Pending).", bullet_style),
        Paragraph("&bull; <b>Advantage:</b> 66% reduction in network round-trips for executive dashboard generation.", bullet_style)
    ]

    t_s7 = Table([[p34_box, p5_box]], colWidths=[4.8 * inch, 4.8 * inch])
    t_s7.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_card_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_card_border),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_s7)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: MONGODB AS A VECTOR DATABASE (AI CLINICAL ASSISTANT)
    # =========================================================================
    story.append(Paragraph("7. MongoDB as a Vector Database & AI Clinical Assistant", slide_title_style))
    story.append(Paragraph("Querying clinical cases by semantic meaning rather than exact keyword matches", slide_subtitle_style))

    vec_left = [
        Paragraph("<b>Why MongoDB for Vectors?</b>", card_title_style),
        Paragraph("&bull; <b>Single Data Store:</b> Eliminates syncing between MongoDB and Pinecone/Weaviate (zero sync drift).", bullet_style),
        Paragraph("&bull; <b>Unified Document:</b> Transactional vitals, medical notes, and 10-dim symptom vectors live together.", bullet_style),
        Paragraph("&bull; <b>Atlas Vector Search:</b> Uses native HNSW index via <font name='Courier'>$vectorSearch</font> aggregation operator.", bullet_style),
        Paragraph("&bull; <b>Hybrid Filtering:</b> Allows combining vector similarity with traditional metadata filters (e.g. department).", bullet_style)
    ]
    vec_right = [
        Paragraph("<b>Live AI Clinical Assistant Workflow</b>", card_title_style),
        Paragraph("1. Physician types: <i>'acute chest pain and elevated palpitations'</i>.", body_style),
        Paragraph("2. System generates a 10-dimensional clinical symptom vector $Q$.", body_style),
        Paragraph("3. Performs cosine similarity search across MongoDB patient charts.", body_style),
        Paragraph("4. <b>Result:</b> Matches PAT-1005 (100.0%) and PAT-1001 (70.7%) with <b>High Confidence</b>.", body_style),
        Paragraph("5. AI synthesizes diagnostic summary and suggests common medications (Atorvastatin, Metoprolol).", body_style)
    ]

    t_s8 = Table([[vec_left, vec_right]], colWidths=[4.8 * inch, 4.8 * inch])
    t_s8.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f5f3ff")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#ddd6fe")),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_s8)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: FULL-STACK WEB PORTAL ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("8. Full-Stack Web Portal Architecture", slide_title_style))
    story.append(Paragraph("Clean, responsive clinical dashboard powered by Flask, Tailwind CSS, and Chart.js", slide_subtitle_style))

    web_pages = [
        [Paragraph("<b>Route</b>", body_style), Paragraph("<b>View Name</b>", body_style), Paragraph("<b>Key Architectural Capabilities Demonstrated</b>", body_style)],
        [Paragraph("<font name='Courier'>/</font>", code_style), Paragraph("Executive Dashboard", body_style), Paragraph("Real-time KPI metrics, department bed occupancy meters, and recent admissions.", body_style)],
        [Paragraph("<font name='Courier'>/patients</font>", code_style), Paragraph("Patient Directory", body_style), Paragraph("Filterable table with department dropdown, status badges, and dynamic regex search.", body_style)],
        [Paragraph("<font name='Courier'>/patient/&lt;id&gt;</font>", code_style), Paragraph("Patient Chart & Telemetry", body_style), Paragraph("Interactive Chart.js vital curves, prescriptions, and modals for atomic $push and $inc updates.", body_style)],
        [Paragraph("<font name='Courier'>/patients/new</font>", code_style), Paragraph("Admission Form", body_style), Paragraph("Interactive test form with 'Fill Invalid Sample' button demonstrating $jsonSchema rejection.", body_style)],
        [Paragraph("<font name='Courier'>/analytics</font>", code_style), Paragraph("Aggregation Hub", body_style), Paragraph("Visual charts and collapsible query code viewers for Pipelines 1 to 5.", body_style)],
        [Paragraph("<font name='Courier'>/ai-search</font>", code_style), Paragraph("AI Vector Search", body_style), Paragraph("Natural language clinical query box, similarity meters, and Atlas $vectorSearch syntax.", body_style)]
    ]
    t_web = Table(web_pages, colWidths=[1.6 * inch, 2.2 * inch, 5.8 * inch])
    t_web.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_web)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 10: CONCLUSION & DELIVERABLES CHECKLIST
    # =========================================================================
    story.append(Paragraph("9. Conclusion & Deliverables Summary", slide_title_style))
    story.append(Paragraph("Complete satisfaction of Course Outcomes CO4, CO5, and CO6 with enterprise deliverables", slide_subtitle_style))

    d_left = [
        Paragraph("<b>Submitted Project Deliverables</b>", card_title_style),
        Paragraph("&bull; <b>Full Codebase:</b> Complete Python/PyMongo full-stack repository.", bullet_style),
        Paragraph("&bull; <b>Formal PDF Report:</b> <font name='Courier'>SmartHospital_Project_Report.pdf</font>", bullet_style),
        Paragraph("&bull; <b>Presentation Deck PDF:</b> <font name='Courier'>SmartHospital_Presentation.pdf</font>", bullet_style),
        Paragraph("&bull; <b>Raw MongoDB Script:</b> <font name='Courier'>scripts/mongo_queries.js</font> for mongosh / Compass.", bullet_style),
        Paragraph("&bull; <b>Execution Proof Log:</b> <font name='Courier'>output_demonstration.txt</font> with test records.", bullet_style),
        Paragraph("&bull; <b>Viva Defense Guide:</b> 15 model Q&A with schema justifications.", bullet_style)
    ]
    d_right = [
        Paragraph("<b>Key Academic Takeaways</b>", card_title_style),
        Paragraph("&bull; Document databases excel at hierarchical, co-located healthcare telemetry.", bullet_style),
        Paragraph("&bull; Hybrid data modeling prevents relational JOIN bottlenecks while avoiding data duplication.", bullet_style),
        Paragraph("&bull; Database-level schema validation provides structural safety in schemaless systems.", bullet_style),
        Paragraph("&bull; MongoDB functions as a high-performance unified Operational and Vector Database.", bullet_style),
        Spacer(1, 6),
        Paragraph("<b>Thank you! Questions and Live Demonstration welcome.</b>", ParagraphStyle('Thanks', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=c_primary))
    ]

    t_s10 = Table([[d_left, d_right]], colWidths=[4.8 * inch, 4.8 * inch])
    t_s10.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_card_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_card_border),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_s10)

    doc.build(story, canvasmaker=SlideCanvas)
    print(f"[OK] Presentation PDF compiled successfully: {filename}")


if __name__ == "__main__":
    output_pdf = os.path.join(os.path.dirname(__file__), "..", "SmartHospital_Presentation.pdf")
    build_presentation_pdf(output_pdf)
