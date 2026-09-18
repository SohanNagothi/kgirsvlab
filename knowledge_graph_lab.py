import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import json
import io


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Knowledge Graph Virtual Lab",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(14,165,233,0.08), transparent 25%),
        radial-gradient(circle at 90% 20%, rgba(139,92,246,0.08), transparent 25%),
        #07111f;
    color: #e5edf7;
}

[data-testid="stSidebar"] {
    background: #091522;
    border-right: 1px solid rgba(148,163,184,0.15);
}

[data-testid="stSidebar"] * {
    color: #dbeafe;
}

.lab-title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -1.5px;
    margin-bottom: 5px;
}

.lab-subtitle {
    color: #94a3b8;
    font-size: 16px;
    margin-bottom: 30px;
}

.eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #38bdf8;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.section-title {
    font-size: 28px;
    font-weight: 750;
    margin-top: 10px;
}

.hero {
    padding: 34px;
    border: 1px solid rgba(56,189,248,0.20);
    border-radius: 20px;
    background:
        linear-gradient(135deg,
        rgba(14,165,233,0.10),
        rgba(30,41,59,0.35));
    margin-bottom: 25px;
}

.card {
    padding: 22px;
    border-radius: 16px;
    background: rgba(15,23,42,0.72);
    border: 1px solid rgba(148,163,184,0.13);
    margin-bottom: 16px;
}

.card-title {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 8px;
}

.card-text {
    color: #94a3b8;
    line-height: 1.65;
}

.schema-node {
    padding: 16px;
    border-radius: 14px;
    background: #0f1d2e;
    border: 1px solid rgba(56,189,248,0.20);
    margin-bottom: 10px;
}

.schema-label {
    font-family: 'JetBrains Mono', monospace;
    color: #38bdf8;
    font-weight: 600;
}

.schema-property {
    color: #94a3b8;
    font-size: 13px;
    margin-top: 5px;
}

.stat-card {
    background: rgba(15,23,42,0.80);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
}

.stat-number {
    font-size: 30px;
    font-weight: 800;
    color: #38bdf8;
}

.stat-label {
    color: #94a3b8;
    font-size: 13px;
    margin-top: 4px;
}

.import-success {
    padding: 18px;
    border-radius: 14px;
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.30);
}

.import-title {
    color: #34d399;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

.code-box {
    background: #020617;
    border: 1px solid rgba(148,163,184,0.15);
    padding: 18px;
    border-radius: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #cbd5e1;
}

.result-box {
    padding: 20px;
    border-radius: 14px;
    background: rgba(14,165,233,0.06);
    border: 1px solid rgba(56,189,248,0.20);
}

.footer {
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid rgba(148,163,184,0.12);
    color: #64748b;
    text-align: center;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATASET
# ============================================================

NODES = [

    # DISASTERS
    {
        "id": "D01",
        "label": "Disaster",
        "name": "Nashik Flood",
        "date": "2026-07-18",
        "severity": "High",
        "status": "Active"
    },
    {
        "id": "D02",
        "label": "Disaster",
        "name": "Mumbai Flood",
        "date": "2026-07-20",
        "severity": "Medium",
        "status": "Monitoring"
    },
    {
        "id": "D03",
        "label": "Disaster",
        "name": "Sikkim Landslide",
        "date": "2026-08-02",
        "severity": "High",
        "status": "Response"
    },
    {
        "id": "D04",
        "label": "Disaster",
        "name": "Chennai Cyclone",
        "date": "2026-08-11",
        "severity": "Medium",
        "status": "Monitoring"
    },

    # LOCATIONS
    {
        "id": "L01",
        "label": "Location",
        "name": "Nashik",
        "state": "Maharashtra",
        "country": "India"
    },
    {
        "id": "L02",
        "label": "Location",
        "name": "Mumbai",
        "state": "Maharashtra",
        "country": "India"
    },
    {
        "id": "L03",
        "label": "Location",
        "name": "Gangtok",
        "state": "Sikkim",
        "country": "India"
    },
    {
        "id": "L04",
        "label": "Location",
        "name": "Chennai",
        "state": "Tamil Nadu",
        "country": "India"
    },

    # HAZARDS
    {
        "id": "H01",
        "label": "Hazard",
        "name": "Flood",
        "category": "Hydrological"
    },
    {
        "id": "H02",
        "label": "Hazard",
        "name": "Landslide",
        "category": "Geological"
    },
    {
        "id": "H03",
        "label": "Hazard",
        "name": "Cyclone",
        "category": "Meteorological"
    },

    # AGENCIES
    {
        "id": "A01",
        "label": "Agency",
        "name": "NDRF",
        "type": "Rescue Agency"
    },
    {
        "id": "A02",
        "label": "Agency",
        "name": "IMD",
        "type": "Weather Agency"
    },
    {
        "id": "A03",
        "label": "Agency",
        "name": "State Disaster Authority",
        "type": "Government Authority"
    },

    # SHELTERS
    {
        "id": "S01",
        "label": "Shelter",
        "name": "Nashik Relief Centre",
        "capacity": 500
    },
    {
        "id": "S02",
        "label": "Shelter",
        "name": "Mumbai Civic Shelter",
        "capacity": 800
    },
    {
        "id": "S03",
        "label": "Shelter",
        "name": "Gangtok Emergency Shelter",
        "capacity": 300
    }
]


RELATIONSHIPS = [

    {"source": "D01", "type": "OCCURS_IN", "target": "L01"},
    {"source": "D01", "type": "HAS_HAZARD", "target": "H01"},
    {"source": "D01", "type": "MANAGED_BY", "target": "A01"},
    {"source": "L01", "type": "HAS_SHELTER", "target": "S01"},

    {"source": "D02", "type": "OCCURS_IN", "target": "L02"},
    {"source": "D02", "type": "HAS_HAZARD", "target": "H01"},
    {"source": "D02", "type": "MANAGED_BY", "target": "A03"},
    {"source": "L02", "type": "HAS_SHELTER", "target": "S02"},

    {"source": "D03", "type": "OCCURS_IN", "target": "L03"},
    {"source": "D03", "type": "HAS_HAZARD", "target": "H02"},
    {"source": "D03", "type": "MANAGED_BY", "target": "A01"},
    {"source": "L03", "type": "HAS_SHELTER", "target": "S03"},

    {"source": "D04", "type": "OCCURS_IN", "target": "L04"},
    {"source": "D04", "type": "HAS_HAZARD", "target": "H03"},
    {"source": "D04", "type": "MANAGED_BY", "target": "A03"},

    {"source": "H03", "type": "MONITORED_BY", "target": "A02"},
    {"source": "H01", "type": "MONITORED_BY", "target": "A03"}
]


# ============================================================
# SESSION STATE
# ============================================================

def initialize_state():

    if "imported" not in st.session_state:
        st.session_state.imported = False

    if "trials" not in st.session_state:
        st.session_state.trials = []

    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = None

    if "student_name" not in st.session_state:
        st.session_state.student_name = ""

    if "student_roll" not in st.session_state:
        st.session_state.student_roll = ""


initialize_state()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_node(node_id):

    for node in NODES:
        if node["id"] == node_id:
            return node

    return None


def get_node_name(node_id):

    node = get_node(node_id)

    if node:
        return node.get("name", node_id)

    return node_id


def get_node_label(node_id):

    node = get_node(node_id)

    if node:
        return node.get("label", "")

    return ""


def get_connected_relationships(node_id):

    result = []

    for rel in RELATIONSHIPS:

        if rel["source"] == node_id or rel["target"] == node_id:

            result.append({
                "From": get_node_name(rel["source"]),
                "Relationship": rel["type"],
                "To": get_node_name(rel["target"])
            })

    return result


# ============================================================
# GRAPH CREATION
# ============================================================

def create_graph(selected_node=None):

    node_positions = {

        "D01": (0, 2.5),
        "D02": (0, 0.5),
        "D03": (0, -1.5),
        "D04": (0, -3.5),

        "L01": (-3.5, 2.5),
        "L02": (-3.5, 0.5),
        "L03": (-3.5, -1.5),
        "L04": (-3.5, -3.5),

        "H01": (3.5, 2.0),
        "H02": (3.5, -1.0),
        "H03": (3.5, -3.0),

        "A01": (6.5, 2.0),
        "A02": (6.5, -1.0),
        "A03": (6.5, -3.0),

        "S01": (-6.5, 2.5),
        "S02": (-6.5, 0.5),
        "S03": (-6.5, -1.5)
    }

    fig = go.Figure()

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    for rel in RELATIONSHIPS:

        x1, y1 = node_positions[rel["source"]]
        x2, y2 = node_positions[rel["target"]]

        fig.add_trace(
            go.Scatter(
                x=[x1, x2],
                y=[y1, y2],
                mode="lines",
                line=dict(
                    width=1.5,
                    color="#475569"
                ),
                hoverinfo="none",
                showlegend=False
            )
        )

        # relationship label
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        fig.add_annotation(
            x=mx,
            y=my,
            text=rel["type"],
            showarrow=False,
            font=dict(
                size=9,
                color="#94a3b8"
            ),
            bgcolor="#0b1726",
            bordercolor="#1e293b",
            borderwidth=1
        )

    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    groups = {
        "Disaster": "#ef4444",
        "Location": "#22c55e",
        "Hazard": "#f59e0b",
        "Agency": "#8b5cf6",
        "Shelter": "#06b6d4"
    }

    for node in NODES:

        node_id = node["id"]
        label = node["label"]

        x, y = node_positions[node_id]

        size = 30

        if selected_node == node_id:
            size = 42

        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                text=[node["name"]],
                textposition="bottom center",
                marker=dict(
                    size=size,
                    color=groups.get(label, "#38bdf8"),
                    line=dict(
                        width=2,
                        color="#e2e8f0"
                    )
                ),
                customdata=[[node_id, label]],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "ID: %{customdata[0]}<br>"
                    "Label: %{customdata[1]}"
                    "<extra></extra>"
                ),
                showlegend=False
            )
        )

    fig.update_layout(

        height=720,

        plot_bgcolor="#07111f",
        paper_bgcolor="#07111f",

        xaxis=dict(
            visible=False,
            range=[-8, 8]
        ),

        yaxis=dict(
            visible=False,
            range=[-5, 4]
        ),

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),

        hovermode="closest"
    )

    return fig


# ============================================================
# PDF REPORT
# ============================================================

class LabPDF(FPDF):

    def footer(self):

        self.set_y(-15)

        self.set_font(
            "Helvetica",
            "I",
            8
        )

        self.set_text_color(
            120,
            120,
            120
        )

        self.cell(
            0,
            10,
            f"Page {self.page_no()} | Knowledge Graph Virtual Laboratory",
            align="C"
        )


def generate_report():

    pdf = LabPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=18
    )

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        "B",
        18
    )

    pdf.cell(
        0,
        10,
        "Knowledge Graph Virtual Laboratory",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    pdf.cell(
        0,
        8,
        "Experiment 9 - Design a Knowledge Graph Schema and Import Data",
        ln=True
    )

    pdf.ln(6)

    pdf.set_font(
        "Helvetica",
        "B",
        11
    )

    pdf.cell(
        0,
        7,
        "Student Information",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    pdf.cell(
        0,
        6,
        f"Name: {st.session_state.student_name or 'N/A'}",
        ln=True
    )

    pdf.cell(
        0,
        6,
        f"Roll Number: {st.session_state.student_roll or 'N/A'}",
        ln=True
    )

    pdf.cell(
        0,
        6,
        f"Date: {datetime.now().strftime('%Y-%m-%d')}",
        ln=True
    )

    pdf.ln(6)

    pdf.set_font(
        "Helvetica",
        "B",
        11
    )

    pdf.cell(
        0,
        7,
        "Aim",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    pdf.multi_cell(
        0,
        6,
        "To design a domain-specific knowledge graph schema using node "
        "labels, properties and relationship types, and to import "
        "structured entity-relationship data into a virtual graph."
    )

    pdf.ln(5)

    pdf.set_font(
        "Helvetica",
        "B",
        11
    )

    pdf.cell(
        0,
        7,
        "Graph Statistics",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    pdf.cell(
        0,
        6,
        f"Total Nodes: {len(NODES)}",
        ln=True
    )

    pdf.cell(
        0,
        6,
        f"Total Relationships: {len(RELATIONSHIPS)}",
        ln=True
    )

    pdf.cell(
        0,
        6,
        f"Node Labels: {len(set(n['label'] for n in NODES))}",
        ln=True
    )

    pdf.cell(
        0,
        6,
        f"Relationship Types: {len(set(r['type'] for r in RELATIONSHIPS))}",
        ln=True
    )

    pdf.ln(5)

    pdf.set_font(
        "Helvetica",
        "B",
        11
    )

    pdf.cell(
        0,
        7,
        "Schema",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        9
    )

    schema = [
        "Disaster -> OCCURS_IN -> Location",
        "Disaster -> HAS_HAZARD -> Hazard",
        "Disaster -> MANAGED_BY -> Agency",
        "Location -> HAS_SHELTER -> Shelter",
        "Hazard -> MONITORED_BY -> Agency"
    ]

    for item in schema:
        pdf.cell(
            0,
            5,
            "- " + item,
            ln=True
        )

    pdf.ln(5)

    pdf.set_font(
        "Helvetica",
        "B",
        11
    )

    pdf.cell(
        0,
        7,
        "Quiz Result",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    score = st.session_state.quiz_score

    if score is None:
        pdf.cell(
            0,
            6,
            "Quiz not attempted.",
            ln=True
        )
    else:
        pdf.cell(
            0,
            6,
            f"Score: {score}/10",
            ln=True
        )

    pdf.ln(6)

    pdf.set_font(
        "Helvetica",
        "B",
        11
    )

    pdf.cell(
        0,
        7,
        "Conclusion",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    pdf.multi_cell(
        0,
        6,
        "The experiment demonstrated the design of a domain-specific "
        "knowledge graph using entities, node labels, properties and "
        "semantic relationships. Structured disaster-management data "
        "was validated and represented as a connected graph. The "
        "experiment illustrates how relationships between entities "
        "provide contextual information for graph-based exploration."
    )

    return bytes(pdf.output())


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "<div class='eyebrow'>VIRTUAL LAB / KG-09</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "## 🧠 Knowledge Graph Lab"
    )

    st.caption(
        "Knowledge Graphs & Information Retrieval Systems"
    )

    st.divider()

    section = st.radio(
        "LAB MODULES",
        [
            "Home / Aim",
            "Theory",
            "Schema Designer",
            "Data Import Lab",
            "Interactive Graph",
            "Graph Exploration",
            "Observations",
            "Quiz",
            "Report Generation"
        ]
    )

    st.divider()

    st.markdown("### Experiment Status")

    if st.session_state.imported:
        st.success("Graph Imported")
    else:
        st.warning("Data Not Imported")

    if st.session_state.quiz_score is not None:
        st.info(
            f"Quiz: {st.session_state.quiz_score}/10"
        )
    else:
        st.caption("Quiz: Not attempted")

    st.divider()

    st.caption(
        "Experiment 09 • Roll Numbers 41–45"
    )


# ============================================================
# HOME
# ============================================================

if section == "Home / Aim":

    st.markdown(
        "<div class='eyebrow'>EXPERIMENT 09</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='lab-title'>Design a Knowledge Graph<br>Schema & Import Data</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='lab-subtitle'>"
        "A virtual laboratory for modelling entities, semantic relationships "
        "and structured domain knowledge."
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">DOMAIN</div>
            <h2>Disaster Management Knowledge Graph</h2>
            <p style="color:#94a3b8;line-height:1.7;">
            In this experiment, disaster events, locations, hazards,
            agencies and shelters are represented as connected entities.
            Students design the graph schema and then import structured
            entity-relationship data into the virtual graph environment.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## Aim")

    st.write(
        "To design a domain-specific Knowledge Graph schema by defining "
        "node labels, properties and relationship types, and to import "
        "structured entity-relationship data into a virtual graph."
    )

    st.markdown("## Learning Objectives")

    objectives = [
        "Understand the basic architecture of a Knowledge Graph.",
        "Identify entities that can be represented as graph nodes.",
        "Define suitable node labels and properties.",
        "Design semantic relationship types between entities.",
        "Convert structured entity-relationship data into graph form.",
        "Explore connected entities through graph traversal."
    ]

    for i, objective in enumerate(objectives, 1):

        st.markdown(
            f"""
            <div class="card">
                <b>0{i}</b> &nbsp;&nbsp; {objective}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("## Expected Outcome")

    st.success(
        "A domain-specific Knowledge Graph containing connected disaster, "
        "location, hazard, agency and shelter entities."
    )


# ============================================================
# THEORY
# ============================================================

elif section == "Theory":

    st.markdown(
        "<div class='eyebrow'>MODULE 01</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-title'>Theory & Concepts</div>",
        unsafe_allow_html=True
    )

    st.write(
        "A Knowledge Graph represents real-world entities and the semantic "
        "relationships between them. Unlike a simple table, a graph directly "
        "represents how different entities are connected."
    )

    st.markdown("### 1. Knowledge Graph")

    st.info(
        "A Knowledge Graph is a structured representation of entities, "
        "their properties and the relationships connecting those entities."
    )

    st.markdown("### 2. Node")

    st.write(
        "A node represents an entity or concept in the domain."
    )

    st.code(
        "Disaster: Nashik Flood\n"
        "Location: Nashik\n"
        "Agency: NDRF"
    )

    st.markdown("### 3. Node Label")

    st.write(
        "A label identifies the category or type of a node."
    )

    st.code(
        "Nashik Flood → Disaster\n"
        "Nashik → Location\n"
        "NDRF → Agency"
    )

    st.markdown("### 4. Properties")

    st.write(
        "Properties store descriptive information about nodes."
    )

    st.code(
        "Disaster {\n"
        "    id: D01,\n"
        "    name: Nashik Flood,\n"
        "    severity: High,\n"
        "    status: Active\n"
        "}"
    )

    st.markdown("### 5. Relationship")

    st.write(
        "A relationship represents a semantic connection between two entities."
    )

    st.code(
        "(Nashik Flood) ──OCCURS_IN──> (Nashik)"
    )

    st.markdown("### 6. Knowledge Graph Triple")

    st.write(
        "A basic graph statement can be expressed as a subject, predicate "
        "and object."
    )

    st.code(
        "Subject       Predicate       Object\n"
        "Nashik Flood  OCCURS_IN       Nashik"
    )

    st.markdown("### Knowledge Graph Model")

    st.markdown(
        """
        <div class="code-box">
        ENTITY → PROPERTY → VALUE<br><br>
        ENTITY ── RELATIONSHIP ──> ENTITY<br><br>
        Multiple connected entities form a KNOWLEDGE GRAPH.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Procedure")

    steps = [
        "Identify entities from the selected domain.",
        "Group entities into meaningful node labels.",
        "Define properties for each node label.",
        "Identify meaningful semantic relationships.",
        "Prepare structured node and relationship records.",
        "Validate entity IDs and relationship endpoints.",
        "Import the records into the virtual graph.",
        "Explore the resulting graph and record observations."
    ]

    for i, step in enumerate(steps, 1):
        st.write(f"**Step {i}:** {step}")


# ============================================================
# SCHEMA DESIGNER
# ============================================================

elif section == "Schema Designer":

    st.markdown(
        "<div class='eyebrow'>MODULE 02</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-title'>Knowledge Graph Schema</div>",
        unsafe_allow_html=True
    )

    st.write(
        "The schema defines what types of entities exist, what properties "
        "they contain and how they can be connected."
    )

    st.markdown("### Node Labels")

    schema_data = [
        {
            "Node Label": "Disaster",
            "Properties": "id, name, date, severity, status"
        },
        {
            "Node Label": "Location",
            "Properties": "id, name, state, country"
        },
        {
            "Node Label": "Hazard",
            "Properties": "id, name, category"
        },
        {
            "Node Label": "Agency",
            "Properties": "id, name, type"
        },
        {
            "Node Label": "Shelter",
            "Properties": "id, name, capacity"
        }
    ]

    st.dataframe(
        pd.DataFrame(schema_data),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Relationship Types")

    relationship_schema = [
        ["Disaster", "OCCURS_IN", "Location"],
        ["Disaster", "HAS_HAZARD", "Hazard"],
        ["Disaster", "MANAGED_BY", "Agency"],
        ["Location", "HAS_SHELTER", "Shelter"],
        ["Hazard", "MONITORED_BY", "Agency"]
    ]

    st.dataframe(
        pd.DataFrame(
            relationship_schema,
            columns=[
                "Source Label",
                "Relationship",
                "Target Label"
            ]
        ),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Schema View")

    st.code(
        """
Disaster
 ├── OCCURS_IN ────────> Location
 ├── HAS_HAZARD ───────> Hazard
 └── MANAGED_BY ───────> Agency

Location
 └── HAS_SHELTER ──────> Shelter

Hazard
 └── MONITORED_BY ─────> Agency
        """,
        language="text"
    )

    st.markdown("### Schema Design Principles")

    principles = [
        "Use meaningful labels for different entity categories.",
        "Store descriptive information as properties.",
        "Use relationship types that describe the semantic connection.",
        "Avoid unnecessary relationships that do not add domain meaning.",
        "Use unique IDs so relationship endpoints can be resolved reliably."
    ]

    for principle in principles:
        st.write("• " + principle)


# ============================================================
# DATA IMPORT
# ============================================================

elif section == "Data Import Lab":

    st.markdown(
        "<div class='eyebrow'>MODULE 03</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-title'>Structured Data Import Lab</div>",
        unsafe_allow_html=True
    )

    st.write(
        "The following structured records represent the data that will be "
        "converted into the virtual Knowledge Graph."
    )

    tab1, tab2 = st.tabs(
        ["Node Records", "Relationship Records"]
    )

    with tab1:

        node_df = pd.DataFrame(NODES)

        st.dataframe(
            node_df,
            use_container_width=True,
            hide_index=True
        )

        csv_nodes = node_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Node Dataset",
            csv_nodes,
            "knowledge_graph_nodes.csv",
            "text/csv"
        )

    with tab2:

        rel_df = pd.DataFrame(RELATIONSHIPS)

        rel_df["Source Entity"] = rel_df["source"].apply(
            get_node_name
        )

        rel_df["Target Entity"] = rel_df["target"].apply(
            get_node_name
        )

        display_rel = rel_df[
            [
                "source",
                "Source Entity",
                "type",
                "target",
                "Target Entity"
            ]
        ]

        st.dataframe(
            display_rel,
            use_container_width=True,
            hide_index=True
        )

        csv_rel = rel_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Relationship Dataset",
            csv_rel,
            "knowledge_graph_relationships.csv",
            "text/csv"
        )

    st.divider()

    st.markdown("### Import Validation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Node Records",
            len(NODES)
        )

    with col2:
        st.metric(
            "Relationship Records",
            len(RELATIONSHIPS)
        )

    with col3:
        st.metric(
            "Node Labels",
            len(set(n["label"] for n in NODES))
        )

    st.markdown("### Run Import")

    if st.button(
        "⚡ Validate & Import Graph",
        type="primary",
        use_container_width=True
    ):

        valid_nodes = all(
            "id" in node and "label" in node
            for node in NODES
        )

        valid_relationships = all(
            rel["source"] in [n["id"] for n in NODES]
            and
            rel["target"] in [n["id"] for n in NODES]
            for rel in RELATIONSHIPS
        )

        if valid_nodes and valid_relationships:

            st.session_state.imported = True

            st.markdown(
                """
                <div class="import-success">
                    <div class="import-title">
                        ✓ IMPORT COMPLETE
                    </div>
                    <br>
                    ✓ Node records validated<br>
                    ✓ Relationship records validated<br>
                    ✓ Entity IDs resolved<br>
                    ✓ Relationship endpoints matched<br>
                    ✓ Graph structure generated
                </div>
                """,
                unsafe_allow_html=True
            )

            st.balloons()

        else:

            st.error(
                "Import failed. Check node IDs and relationship endpoints."
            )

    if st.session_state.imported:

        st.success(
            f"Virtual graph ready: {len(NODES)} nodes and "
            f"{len(RELATIONSHIPS)} relationships."
        )

        st.caption(
            "Note: This CA implements the graph experiment as a frontend "
            "virtual laboratory. No Neo4j database is required."
        )


# ============================================================
# INTERACTIVE GRAPH
# ============================================================

elif section == "Interactive Graph":

    st.markdown(
        "<div class='eyebrow'>MODULE 04</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-title'>Interactive Knowledge Graph</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.imported:

        st.warning(
            "Import the structured data first from the Data Import Lab."
        )

    else:

        st.write(
            "The graph below represents the imported entities and their "
            "semantic relationships."
        )

        label_filter = st.multiselect(
            "Filter Node Labels",
            options=[
                "Disaster",
                "Location",
                "Hazard",
                "Agency",
                "Shelter"
            ],
            default=[
                "Disaster",
                "Location",
                "Hazard",
                "Agency",
                "Shelter"
            ]
        )

        filtered_ids = [
            node["id"]
            for node in NODES
            if node["label"] in label_filter
        ]

        filtered_relationships = [
            rel
            for rel in RELATIONSHIPS
            if rel["source"] in filtered_ids
            and rel["target"] in filtered_ids
        ]

        original_nodes = NODES

        NODES = [
            node
            for node in original_nodes
            if node["id"] in filtered_ids
        ]

        original_relationships = RELATIONSHIPS

        RELATIONSHIPS = filtered_relationships

        fig = create_graph()

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "scrollZoom": True
            }
        )

        NODES = original_nodes
        RELATIONSHIPS = original_relationships

        st.info(
            "Tip: Hover over nodes to inspect their entity ID and label. "
            "Use zoom and pan controls to explore the graph."
        )

        st.markdown("### Select an Entity")

        selected = st.selectbox(
            "Choose an entity to inspect",
            options=[
                node["id"]
                for node in NODES
            ],
            format_func=lambda x:
                f"{x} — {get_node_name(x)}"
        )

        node = get_node(selected)

        if node:

            col1, col2 = st.columns([1, 2])

            with col1:

                st.markdown("#### Entity Properties")

                properties = {
                    k: v
                    for k, v in node.items()
                    if k not in ["id", "label"]
                }

                prop_df = pd.DataFrame(
                    list(properties.items()),
                    columns=["Property", "Value"]
                )

                st.dataframe(
                    prop_df,
                    use_container_width=True,
                    hide_index=True
                )

            with col2:

                st.markdown("#### Connected Relationships")

                connected = get_connected_relationships(
                    selected
                )

                if connected:

                    st.dataframe(
                        pd.DataFrame(connected),
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.info(
                        "No connected relationships found."
                    )


# ============================================================
# GRAPH EXPLORATION
# ============================================================

elif section == "Graph Exploration":

    st.markdown(
        "<div class='eyebrow'>MODULE 05</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-title'>Graph Exploration</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.imported:

        st.warning(
            "Please import the graph before exploring it."
        )

    else:

        query = st.selectbox(
            "Select an exploration operation",
            [
                "Show All Disasters",
                "Find Disasters in Maharashtra",
                "Find High Severity Disasters",
                "Show Disaster → Agency Connections",
                "Show Location → Shelter Connections",
                "Show Hazard → Monitoring Agency Connections"
            ]
        )

        results = []

        if query == "Show All Disasters":

            for node in NODES:

                if node["label"] == "Disaster":

                    results.append(node)

        elif query == "Find Disasters in Maharashtra":

            maharashtra_locations = {
                n["id"]
                for n in NODES
                if n["label"] == "Location"
                and n.get("state") == "Maharashtra"
            }

            for rel in RELATIONSHIPS:

                if (
                    rel["type"] == "OCCURS_IN"
                    and rel["target"] in maharashtra_locations
                ):

                    disaster = get_node(rel["source"])

                    if disaster:
                        results.append(disaster)

        elif query == "Find High Severity Disasters":

            results = [
                n
                for n in NODES
                if n["label"] == "Disaster"
                and n.get("severity") == "High"
            ]

        elif query == "Show Disaster → Agency Connections":

            for rel in RELATIONSHIPS:

                if rel["type"] == "MANAGED_BY":

                    results.append({
                        "Disaster": get_node_name(rel["source"]),
                        "Relationship": rel["type"],
                        "Agency": get_node_name(rel["target"])
                    })

        elif query == "Show Location → Shelter Connections":

            for rel in RELATIONSHIPS:

                if rel["type"] == "HAS_SHELTER":

                    results.append({
                        "Location": get_node_name(rel["source"]),
                        "Relationship": rel["type"],
                        "Shelter": get_node_name(rel["target"])
                    })

        elif query == "Show Hazard → Monitoring Agency Connections":

            for rel in RELATIONSHIPS:

                if rel["type"] == "MONITORED_BY":

                    results.append({
                        "Hazard": get_node_name(rel["source"]),
                        "Relationship": rel["type"],
                        "Agency": get_node_name(rel["target"])
                    })

        st.divider()

        if results:

            st.markdown(
                f"### {query}"
            )

            st.dataframe(
                pd.DataFrame(results),
                use_container_width=True,
                hide_index=True
            )

            st.success(
                f"{len(results)} result(s) found through graph exploration."
            )

        else:

            st.info(
                "No matching entities or relationships were found."
            )

        st.caption(
            "These are virtual graph-exploration operations for the "
            "frontend-based experiment; no Cypher or Neo4j database is used."
        )


# ============================================================
# OBSERVATIONS
# ============================================================

elif section == "Observations":

    st.markdown(
        "<div class='eyebrow'>MODULE 06</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-title'>Observations & Analysis</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.imported:

        st.warning(
            "Complete the Data Import step to generate observations."
        )

    else:

        total_nodes = len(NODES)
        total_relationships = len(RELATIONSHIPS)
        labels = len(set(n["label"] for n in NODES))
        rel_types = len(set(r["type"] for r in RELATIONSHIPS))

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Nodes",
                total_nodes
            )

        with c2:
            st.metric(
                "Relationships",
                total_relationships
            )

        with c3:
            st.metric(
                "Node Labels",
                labels
            )

        with c4:
            st.metric(
                "Relationship Types",
                rel_types
            )

        st.markdown("### Observed Results")

        observations = [
            f"The graph contains {total_nodes} entity nodes.",
            f"The entities are grouped into {labels} node labels.",
            f"The graph contains {total_relationships} semantic relationships.",
            f"{rel_types} different relationship types are used.",
            "Disasters are connected to geographical locations.",
            "Disasters are connected to their corresponding hazards.",
            "Disaster events are associated with responsible agencies.",
            "Locations can be connected to emergency shelters.",
            "Hazards can be connected to agencies responsible for monitoring them.",
            "The graph structure allows connected information to be explored across multiple entity types."
        ]

        for i, observation in enumerate(
            observations,
            1
        ):

            st.markdown(
                f"""
                <div class="card">
                    <b>{i:02}</b> &nbsp;&nbsp; {observation}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("### Analysis")

        st.write(
            "The experiment shows that a Knowledge Graph can represent "
            "information not only as individual entities but also through "
            "the relationships between those entities. For example, a "
            "disaster can be connected to a location, hazard and agency, "
            "allowing related information to be discovered by following "
            "graph relationships."
        )


# ============================================================
# QUIZ
# ============================================================

elif section == "Quiz":

    st.markdown(
        "<div class='eyebrow'>MODULE 07</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-title'>Concept Assessment</div>",
        unsafe_allow_html=True
    )

    st.write(
        "Answer all questions and submit the quiz to evaluate your "
        "understanding of Knowledge Graph concepts."
    )

    questions = [

        {
            "q": "What does a node represent in a Knowledge Graph?",
            "options": [
                "A relationship",
                "An entity or concept",
                "A database query",
                "A table index"
            ],
            "answer": 1
        },

        {
            "q": "In Disaster ──OCCURS_IN──> Location, what is OCCURS_IN?",
            "options": [
                "Node label",
                "Property",
                "Relationship type",
                "Entity ID"
            ],
            "answer": 2
        },

        {
            "q": "Which is a property of a Disaster node?",
            "options": [
                "severity",
                "OCCURS_IN",
                "Location",
                "HAS_HAZARD"
            ],
            "answer": 0
        },

        {
            "q": "What is the purpose of a unique entity ID?",
            "options": [
                "To identify nodes reliably",
                "To create random relationships",
                "To remove properties",
                "To hide nodes"
            ],
            "answer": 0
        },

        {
            "q": "Which relationship connects a disaster to a hazard?",
            "options": [
                "HAS_HAZARD",
                "HAS_SHELTER",
                "OCCURS_IN",
                "MONITORED_BY"
            ],
            "answer": 0
        },

        {
            "q": "Which component stores descriptive information about a node?",
            "options": [
                "Relationship",
                "Property",
                "Graph traversal",
                "Edge direction"
            ],
            "answer": 1
        },

        {
            "q": "What is a basic Knowledge Graph triple?",
            "options": [
                "Node, database, table",
                "Subject, predicate, object",
                "Label, CSV, query",
                "Property, index, database"
            ],
            "answer": 1
        },

        {
            "q": "Why are relationship types important?",
            "options": [
                "They describe the semantic connection between entities",
                "They delete nodes",
                "They replace all properties",
                "They prevent graph traversal"
            ],
            "answer": 0
        },

        {
            "q": "Which node represents a physical geographical entity in this experiment?",
            "options": [
                "Hazard",
                "Agency",
                "Location",
                "Disaster"
            ],
            "answer": 2
        },

        {
            "q": "What is the main advantage of representing connected data as a graph?",
            "options": [
                "Relationships can be explicitly explored",
                "All data becomes unstructured",
                "Properties become unnecessary",
                "Nodes cannot be connected"
            ],
            "answer": 0
        }

    ]

    with st.form("quiz_form"):

        answers = []

        for i, question in enumerate(
            questions,
            1
        ):

            st.markdown(
                f"### Question {i}"
            )

            st.write(
                question["q"]
            )

            answer = st.radio(
                "Select your answer:",
                question["options"],
                key=f"question_{i}"
            )

            answers.append(
                question["options"].index(answer)
            )

        submitted = st.form_submit_button(
            "Submit Quiz",
            type="primary",
            use_container_width=True
        )

    if submitted:

        score = 0

        for i, question in enumerate(
            questions
        ):

            if answers[i] == question["answer"]:
                score += 1

        st.session_state.quiz_score = score

        st.divider()

        percentage = score * 10

        if score >= 8:

            st.success(
                f"Excellent! Score: {score}/10 ({percentage}%)"
            )

        elif score >= 5:

            st.info(
                f"Good attempt. Score: {score}/10 ({percentage}%)"
            )

        else:

            st.warning(
                f"Review the theory and try again. Score: {score}/10 ({percentage}%)"
            )

    if st.session_state.quiz_score is not None:

        st.markdown(
            f"""
            <div class="result-box">
                <h3>Latest Quiz Score</h3>
                <div class="stat-number">
                    {st.session_state.quiz_score}/10
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# REPORT
# ============================================================

elif section == "Report Generation":

    st.markdown(
        "<div class='eyebrow'>MODULE 08</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-title'>Virtual Lab Report</div>",
        unsafe_allow_html=True
    )

    st.write(
        "Enter your details and generate a PDF record of the experiment."
    )

    col1, col2 = st.columns(2)

    with col1:

        student_name = st.text_input(
            "Student Name",
            value=st.session_state.student_name
        )

    with col2:

        student_roll = st.text_input(
            "Roll Number",
            value=st.session_state.student_roll
        )

    st.session_state.student_name = student_name
    st.session_state.student_roll = student_roll

    st.divider()

    st.markdown("### Report Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric(
            "Nodes",
            len(NODES)
        )

    with summary_col2:
        st.metric(
            "Relationships",
            len(RELATIONSHIPS)
        )

    with summary_col3:

        score = (
            st.session_state.quiz_score
            if st.session_state.quiz_score is not None
            else 0
        )

        st.metric(
            "Quiz Score",
            f"{score}/10"
        )

    if st.button(
        "Generate PDF Report",
        type="primary",
        use_container_width=True
    ):

        pdf_data = generate_report()

        st.success(
            "Report generated successfully."
        )

        st.download_button(
            "Download Lab Report",
            data=pdf_data,
            file_name="knowledge_graph_virtual_lab_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Knowledge Graphs & Information Retrieval Systems
        • Experiment 09
        • Virtual Laboratory
    </div>
    """,
    unsafe_allow_html=True
)