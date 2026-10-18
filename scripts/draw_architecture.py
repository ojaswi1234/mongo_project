"""
Generates the system architecture diagram for Smart Hospital MongoDB system.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_architecture():
    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    ax.set_facecolor('#0f172a')
    fig.patch.set_facecolor('#0f172a')

    # Title
    ax.text(6, 7.5, "Smart Hospital Management System - Architecture Diagram", 
            fontsize=15, fontweight='bold', color='white', ha='center', va='center')

    # 1. User Client Layer
    box_client = patches.FancyBboxPatch((4.5, 6.2), 3.0, 0.7, boxstyle="round,pad=0.1", 
                                        ec="#38bdf8", fc="#1e293b", lw=1.5)
    ax.add_patch(box_client)
    ax.text(6, 6.55, "Healthcare Client (Web Browser / Tablet)\nClinicians, Triage Nurses, Billing Clerks", 
            fontsize=9.5, color='white', ha='center', va='center', fontweight='medium')

    # Arrow Down
    ax.annotate('', xy=(6, 5.4), xytext=(6, 6.2),
                arrowprops=dict(facecolor='#38bdf8', edgecolor='#38bdf8', width=1.5, headwidth=6))
    ax.text(6.1, 5.8, "HTTP / REST API", fontsize=8, color='#94a3b8')

    # 2. Flask Application Layer
    box_backend = patches.FancyBboxPatch((1.5, 3.8), 9.0, 1.6, boxstyle="round,pad=0.15", 
                                         ec="#818cf8", fc="#1e293b", lw=1.5)
    ax.add_patch(box_backend)
    ax.text(6, 5.15, "Flask Application Server & PyMongo Driver (app.py)", 
            fontsize=11, fontweight='bold', color='#c7d2fe', ha='center', va='center')

    # Components inside backend
    comps = [
        ("Route Handlers & Auth\n(Dashboard, Triage, Forms)", 2.8, 4.3),
        ("Connection Pool\n(MongoClient maxPool=50)", 6.0, 4.3),
        ("Query Builder & Atomic Ops\n($push, $inc, $elemMatch)", 9.2, 4.3)
    ]
    for text, cx, cy in comps:
        b = patches.FancyBboxPatch((cx - 1.3, cy - 0.35), 2.6, 0.7, boxstyle="round,pad=0.08", 
                                   ec="#475569", fc="#0f172a", lw=1)
        ax.add_patch(b)
        ax.text(cx, cy, text, fontsize=8, color='#e2e8f0', ha='center', va='center')

    # Arrows to Database Layer
    ax.annotate('', xy=(3.8, 2.7), xytext=(3.8, 3.8),
                arrowprops=dict(facecolor='#34d399', edgecolor='#34d399', width=1.5, headwidth=6))
    ax.text(2.6, 3.25, "$jsonSchema Validation\n& Atomic Ingestion", fontsize=8, color='#6ee7b7', ha='center')

    ax.annotate('', xy=(8.2, 2.7), xytext=(8.2, 3.8),
                arrowprops=dict(facecolor='#38bdf8', edgecolor='#38bdf8', width=1.5, headwidth=6))
    ax.text(9.4, 3.25, "Aggregation Framework\n($match, $group, $lookup)", fontsize=8, color='#7dd3fc', ha='center')

    # 3. Database Layer (MongoDB)
    box_db = patches.FancyBboxPatch((1.5, 0.6), 9.0, 2.1, boxstyle="round,pad=0.15", 
                                    ec="#34d399", fc="#1e293b", lw=1.5)
    ax.add_patch(box_db)
    ax.text(6, 2.45, "MongoDB Database Engine (smarthospital)", 
            fontsize=11, fontweight='bold', color='#6ee7b7', ha='center', va='center')

    db_comps = [
        ("patients Collection (Hybrid Embedded)\n• patient_id (Unique Index)\n• vitals_history (Embedded Array)\n• prescriptions (Embedded Array)\n• billing (Embedded Document)", 3.8, 1.45),
        ("doctors Collection (Referenced)\n• doctor_id (Primary Key)\n• department, contact, fee\n• Referenced by patients.\n  assigned_doctor_id ($lookup)", 8.2, 1.45)
    ]
    for text, cx, cy in db_comps:
        b = patches.FancyBboxPatch((cx - 2.0, cy - 0.6), 4.0, 1.2, boxstyle="round,pad=0.08", 
                                   ec="#059669", fc="#0f172a", lw=1)
        ax.add_patch(b)
        ax.text(cx, cy, text, fontsize=8, color='#e2e8f0', ha='center', va='center')

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig("assets/architecture_diagram.png", facecolor='#0f172a', bbox_inches='tight')
    plt.close()
    print("Generated assets/architecture_diagram.png")

if __name__ == "__main__":
    draw_architecture()
