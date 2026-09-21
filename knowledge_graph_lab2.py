# ==============================================================
# KNOWLEDGE GRAPH VIRTUAL LAB V2.0
# IIT Virtual Labs Inspired Edition
# Part 1 / 6
# Foundation + UI + Aim + Theory + Procedure
# ==============================================================

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from pyvis.network import Network

from datetime import datetime, timedelta
import plotly.io as pio
from fpdf import FPDF

import random
import json
import os
import io
import base64
import tempfile
from datetime import datetime

import streamlit.components.v1 as components

# ----------------------------------------------------------
# Scroll Controller (Teacher's Requirement)
# ----------------------------------------------------------
def scroll_controller():
    components.html("""
    <script>
    window.addEventListener("wheel", function(e){
        if(e.deltaY>0){
            window.parent.postMessage({type:"SCROLL_DOWN"}, "*");
        }else{
            window.parent.postMessage({type:"SCROLL_UP"}, "*");
        }
    });
    </script>
    """, height=0)

# --------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------

st.set_page_config(
    page_title="Knowledge Graph Virtual Laboratory",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------------
# GLOBAL SESSION STATE
# --------------------------------------------------------------

def initialize_state():

    defaults = {

        "student_name":"",
        "student_roll":"",
        "student_division":"",
        "student_batch":"",

        "schema_nodes":[],
        "schema_relationships":[],

        "uploaded_nodes":pd.DataFrame(),
        "uploaded_relationships":pd.DataFrame(),

        "graph":nx.DiGraph(),

        "graph_generated":False,

        "selected_query":"",
        "highlight_nodes":[],
        "highlight_edges":[],

        "assignment_bank_loaded":False,
        "assignment_questions":[],
        "assignment_score":None,

        "quiz_score":None,

        "graph_stats":{}
    }

    for key,value in defaults.items():
        if key not in st.session_state:
            st.session_state[key]=value

initialize_state()

# --------------------------------------------------------------
# COLOR PALETTE
# --------------------------------------------------------------

NODE_COLORS = {
    "Disaster":"#EF4444",
    "Location":"#22C55E",
    "Hazard":"#F59E0B",
    "Agency":"#8B5CF6",
    "Shelter":"#06B6D4",
    "Person":"#3B82F6",
    "Organization":"#EC4899",
    "Event":"#F97316",
    "City":"#14B8A6",
    "Disease":"#DC2626",
    "Medicine":"#0EA5E9",
    "Doctor":"#8B5CF6",
    "Patient":"#10B981"
}

DEFAULT_NODE_COLOR="#38BDF8"

# --------------------------------------------------------------
# MASSIVE CSS
# --------------------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"]{
    font-family:'Poppins',sans-serif;
}

/* background */

.stApp{
background:
radial-gradient(circle at top left,#1E3A8A20,transparent 30%),
radial-gradient(circle at bottom right,#2563EB20,transparent 30%),
#071019;
color:white;
}

/* sidebar */

[data-testid="stSidebar"]{
background:#08121d;
border-right:2px solid #123654;
padding-top:20px;
}

[data-testid="stSidebar"] *{
color:#E2F1FF;
font-size:20px !important;
}

.sidebar-title{
font-size:30px;
font-weight:700;
color:#4FC3F7;
}

.sidebar-sub{
font-size:15px;
color:#9ECDFE;
}

/* title */

.main-title{
font-size:54px;
font-weight:800;
color:white;
line-height:1.05;
}

.subtitle{
font-size:24px;
color:#B5D8FF;
margin-top:10px;
}

/* hero */

.hero{
padding:35px;
border-radius:22px;
background:
linear-gradient(135deg,#0EA5E922,#1E293B99);
border:2px solid #38BDF866;
margin-bottom:30px;
}

/* headings */

.section{
font-size:38px;
font-weight:700;
margin-top:20px;
margin-bottom:10px;
color:#7DD3FC;
}

.subsection{
font-size:28px;
font-weight:600;
color:#D0EBFF;
margin-top:20px;
}

.bodytext{
font-size:21px;
line-height:1.9;
color:#DAEFFF;
}

/* cards */

.card{
background:#111D2D;
padding:25px;
border-radius:18px;
border-left:8px solid #38BDF8;
margin-bottom:20px;
}

.card h3{
color:#60A5FA;
font-size:25px;
}

.card p{
font-size:20px;
line-height:1.8;
}

/* metrics */

.metric-card{
background:#0F172A;
padding:22px;
border-radius:18px;
text-align:center;
border:1px solid #1E40AF;
}

.metric-number{
font-size:42px;
font-weight:800;
color:#60A5FA;
}

.metric-label{
font-size:18px;
color:#CBD5E1;
}

/* buttons */

.stButton>button{
width:100%;
font-size:20px;
font-weight:600;
padding:12px;
border-radius:12px;
background:#0284C7;
color:white;
border:none;
}

.stButton>button:hover{
background:#0EA5E9;
}

/* table */

thead tr th{
font-size:19px !important;
background:#0F172A !important;
color:#7DD3FC !important;
}

tbody tr td{
font-size:18px !important;
}

/* procedure step */

.step-box{
padding:18px;
margin-bottom:15px;
border-radius:15px;
background:#0F1A28;
border-left:6px solid #3B82F6;
}

.step-title{
font-size:24px;
font-weight:700;
color:#7DD3FC;
}

.step-body{
font-size:19px;
line-height:1.7;
}

/* references */

.ref-card{
padding:18px;
background:#0F172A;
border-radius:14px;
margin-bottom:15px;
border:1px solid #334155;
}

/* assignment */

.question-box{
padding:22px;
background:#0B1625;
border-radius:16px;
border-left:6px solid #F59E0B;
}

/* footer */

.footer{
margin-top:40px;
text-align:center;
color:#9CA3AF;
font-size:16px;
padding:20px;
}

</style>
""",unsafe_allow_html=True)

# --------------------------------------------------------------
# HEADER
# --------------------------------------------------------------

st.markdown("""
<div class="hero">

<div style="font-size:18px;color:#7DD3FC;">
COMPUTER ENGINEERING • INFORMATION RETRIEVAL SYSTEMS
</div>

<div class="main-title">
Knowledge Graph Virtual Laboratory
</div>

<div class="subtitle">
Experiment 09 — Design, Build and Explore Dynamic Knowledge Graphs
</div>

</div>
""",unsafe_allow_html=True)

# --------------------------------------------------------------
# SIDEBAR MENU
# --------------------------------------------------------------

with st.sidebar:

    st.markdown('<div class="sidebar-title">🧠 IIT Virtual Lab</div>',unsafe_allow_html=True)

    st.markdown('<div class="sidebar-sub">Knowledge Graph Experiment</div>',unsafe_allow_html=True)

    st.divider()

    menu = st.radio(
        "Navigation",
        [
            "🎯 Aim",
            "📘 Theory",
            "🧪 Procedure",
            "💻 Simulation",
            "📊 Observations",
            "📝 Assignment",
            "📄 Report Generation",
            "📚 References"
        ]
    )

    st.divider()

    st.markdown("### Student Information")

    st.session_state.student_name = st.text_input(
        "Name",
        value=st.session_state.student_name
    )

    st.session_state.student_roll = st.text_input(
        "Roll Number",
        value=st.session_state.student_roll
    )

    st.session_state.student_division = st.text_input(
        "Division",
        value=st.session_state.student_division
    )

    st.session_state.student_batch = st.text_input(
        "Batch",
        value=st.session_state.student_batch
    )

# --------------------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------------------

def metric_cards(nodes,edges,labels,relations):

    c1,c2,c3,c4 = st.columns(4)

    with c1:
        st.markdown(f'''
        <div class="metric-card">
        <div class="metric-number">{nodes}</div>
        <div class="metric-label">Nodes</div>
        </div>
        ''',unsafe_allow_html=True)

    with c2:
        st.markdown(f'''
        <div class="metric-card">
        <div class="metric-number">{edges}</div>
        <div class="metric-label">Relationships</div>
        </div>
        ''',unsafe_allow_html=True)

    with c3:
        st.markdown(f'''
        <div class="metric-card">
        <div class="metric-number">{labels}</div>
        <div class="metric-label">Labels</div>
        </div>
        ''',unsafe_allow_html=True)

    with c4:
        st.markdown(f'''
        <div class="metric-card">
        <div class="metric-number">{relations}</div>
        <div class="metric-label">Relationship Types</div>
        </div>
        ''',unsafe_allow_html=True)

def make_card(title,text):

    st.markdown(f"""
<div class="card">
<h3>{title}</h3>
<p>{text}</p>
</div>
""",unsafe_allow_html=True)

# --------------------------------------------------------------
# GRAPH HELPER (Dynamic)
# --------------------------------------------------------------

def build_networkx_graph(nodes_df,rel_df):

    G = nx.DiGraph()

    if nodes_df.empty:
        return G

    for _,row in nodes_df.iterrows():

        attrs = row.to_dict()

        node_id = attrs["ID"]

        G.add_node(node_id,**attrs)

    if not rel_df.empty:

        for _,row in rel_df.iterrows():

            G.add_edge(
                row["Source"],
                row["Target"],
                relationship=row["Relationship"]
            )

    return G

# Plotly interactive graph

def draw_graph(highlight_nodes=None, highlight_edges=None):

    if highlight_nodes is None:
        highlight_nodes = []

    if highlight_edges is None:
        highlight_edges = []

    G = st.session_state.graph

        # Safety check
    if len(G.nodes) == 0:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="#071019",
            plot_bgcolor="#071019",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(
                    text="No graph generated yet.",
                    showarrow=False,
                    font=dict(size=22, color="white")
                )
            ]
        )
        return fig

    pos = nx.spring_layout(G, seed=18)

    fig = go.Figure()

    # ---------------- EDGES ----------------

    for edge in G.edges():

        x0,y0 = pos[edge[0]]
        x1,y1 = pos[edge[1]]

        active = edge in highlight_edges

        fig.add_trace(go.Scatter(
            x=[x0,x1],
            y=[y0,y1],
            mode="lines",
            line=dict(
                color="#22C55E" if active else "#475569",
                width=7 if active else 2
            ),
            hoverinfo="none",
            showlegend=False
        ))

        fig.add_annotation(
            x=(x0+x1)/2,
            y=(y0+y1)/2,
            text=G.edges[edge]["relationship"],
            showarrow=False,
            font=dict(size=12,color="#FACC15")
        )

    # ---------------- NODES ----------------

    node_x = []
    node_y = []
    colors = []
    sizes = []
    labels = []

    current = highlight_nodes[-1] if highlight_nodes else None

    for node,data in G.nodes(data=True):

        x,y = pos[node]

        node_x.append(x)
        node_y.append(y)

        labels.append(data["Name"])

        if node == current:

            colors.append("#FACC15")
            sizes.append(38)

        elif node in highlight_nodes:

            colors.append("#22C55E")
            sizes.append(32)

        else:

            colors.append(
                NODE_COLORS.get(
                    data["Label"],
                    DEFAULT_NODE_COLOR
                )
            )

            sizes.append(24)

    fig.add_trace(go.Scatter(

        x=node_x,
        y=node_y,

        mode="markers+text",

        text=labels,

        textposition="top center",

        marker=dict(
            color=colors,
            size=sizes,
            line=dict(color="white",width=2)
        ),

        hovertemplate="<b>%{text}</b><extra></extra>"

    ))

    fig.update_layout(

        title=dict(
            text="Interactive Knowledge Graph",
            font=dict(size=24, color="white")
        ),

        height=650,

        paper_bgcolor="#071019",
        plot_bgcolor="#071019",

        xaxis=dict(visible=False),
        yaxis=dict(visible=False),

        margin=dict(l=10,r=10,t=20,b=20)

    )

    return fig

# --------------------------------------------------------------
# AIM PAGE
# --------------------------------------------------------------

if menu=="🎯 Aim":

    st.markdown('<div class="section">Aim</div>',unsafe_allow_html=True)

    st.markdown("""
<div class="bodytext">

The objective of this experiment is to design a domain-specific Knowledge Graph schema,
define entities, properties and semantic relationships, import structured datasets,
generate an interactive graph representation, and explore graph traversal techniques
used in real-world knowledge graph systems.

</div>
""",unsafe_allow_html=True)

    st.markdown("## Learning Objectives")

    objectives=[
        "Understand the concept of Knowledge Graphs.",
        "Identify entities, node labels and properties.",
        "Design relationships between entities.",
        "Create dynamic graph schemas.",
        "Import datasets into graph structure.",
        "Perform graph traversal and exploration.",
        "Visualize connected knowledge interactively.",
        "Generate graph analytics and reports."
    ]

    for i,obj in enumerate(objectives,1):
        make_card(f"Objective {i}",obj)

    st.markdown("## Expected Outcomes")

    make_card(
        "After completing this experiment students will be able to:",
        """
Create dynamic knowledge graphs from any structured dataset,
understand semantic relationships,
perform traversals visually,
and analyze graph connectivity similar to Neo4j Knowledge Graph systems.
"""
    )

    st.markdown('<div class="section">Real World Applications</div>',unsafe_allow_html=True)

    col1,col2=st.columns(2)

    with col1:

        make_card("Google Search Knowledge Graph",
        "Google connects billions of people, places, movies, organizations and facts through Knowledge Graphs to improve semantic search.")

        make_card("Healthcare Knowledge Graph",
        "Patients, diseases, medicines, symptoms, hospitals and doctors are linked to assist diagnosis and recommendations.")

        make_card("E-Commerce Recommendation System",
        "Products, customers, categories and purchase history form recommendation graphs used by Amazon and Flipkart.")

        make_card("Fraud Detection",
        "Banks connect accounts, transactions, IP addresses and merchants to identify suspicious behavior.")

    with col2:

        make_card("Social Networks",
        "Users, friends, posts, likes and communities form massive knowledge graphs in platforms like Facebook and LinkedIn.")

        make_card("Disaster Management",
        "Disaster events, shelters, rescue agencies and locations are connected to support emergency response.")

        make_card("Cyber Security",
        "Devices, users, vulnerabilities and attack paths are represented as graphs for threat intelligence.")

        make_card("Education Knowledge Graph",
        "Students, faculty, courses and departments are connected to personalize learning.")

# --------------------------------------------------------------
# THEORY PAGE
# --------------------------------------------------------------

elif menu=="📘 Theory":

    st.markdown('<div class="section">Theory</div>',unsafe_allow_html=True)

    make_card("Knowledge Graph",
    """
A Knowledge Graph is a graph-based representation of knowledge where entities are represented
as nodes and semantic relationships are represented as edges. Unlike relational databases,
knowledge graphs naturally capture interconnected information.
""")

    make_card("Entity",
    """
An entity represents a real-world object or concept such as a Person, City, Disaster,
Hospital, Organization or Product.
""")

    make_card("Node Labels",
    """
Node labels classify entities into categories. Examples include Person, Disaster,
Agency, Shelter, Disease, Doctor and Product.
""")

    make_card("Properties",
    """
Properties store descriptive attributes about nodes such as Name, Age, Severity,
Location, Capacity and Status.
""")

    make_card("Relationships",
    """
Relationships define semantic meaning between entities.

Examples:
Person — LIVES_IN — City
Disaster — OCCURS_IN — Location
Patient — HAS_DISEASE — Disease
Doctor — TREATS — Patient
""")

    make_card("Knowledge Graph Triple",
    """
Every statement inside a knowledge graph can be represented as:

Subject → Predicate → Object

Example:
Mumbai Flood → OCCURS_IN → Mumbai
""")

    make_card("Ontology",
    """
Ontology defines the vocabulary, classes and semantic rules governing the knowledge graph.
""")

    make_card("RDF (Resource Description Framework)",
    """
RDF stores knowledge using triples consisting of subject, predicate and object.
It is the foundation of Semantic Web technologies.
""")

    make_card("SPARQL",
    """
SPARQL is the query language for RDF knowledge graphs.
It retrieves entities and relationships similar to SQL for relational databases.
""")

    make_card("Neo4j Property Graph Model",
    """
Neo4j stores nodes and relationships with properties.
Relationships themselves can also contain properties.
""")

    st.markdown("## Property Graph vs RDF")

    st.table(pd.DataFrame({

        "Property Graph":[
            "Neo4j",
            "Nodes with labels",
            "Relationships with properties",
            "Cypher Query Language",
            "Highly interactive traversal"
        ],

        "RDF":[
            "Semantic Web",
            "Resources",
            "Triples",
            "SPARQL",
            "Ontology driven"
        ]

    }))

    st.markdown("## Graph Traversal")

    make_card(
        "Traversal Algorithms",
        """
Traversal means visiting connected nodes through relationships.

Common traversals include:

• Breadth First Search (BFS)

• Depth First Search (DFS)

• Neighbor Expansion

• Shortest Path Traversal

Knowledge graphs use traversal to discover hidden relationships.
"""
    )

    st.markdown("## Recommended E-Books")

    ebooks=pd.DataFrame({

        "Book":[
            "Knowledge Graphs - Aidan Hogan",
            "Graph Databases - O'Reilly",
            "Learning SPARQL",
            "Semantic Web for the Working Ontologist",
            "Neo4j Graph Data Science"
        ],

        "Purpose":[
            "Knowledge Graph fundamentals",
            "Neo4j implementation",
            "SPARQL queries",
            "Ontology design",
            "Graph analytics"
        ]
    })

    st.dataframe(ebooks,use_container_width=True)

    st.markdown("## Research Papers")

    papers=pd.DataFrame({

        "Paper":[
            "Google Knowledge Vault",
            "DBpedia Knowledge Graph",
            "Wikidata Architecture",
            "Knowledge Graph Embeddings Survey",
            "Semantic Web Vision by Tim Berners-Lee"
        ],

        "Area":[
            "Knowledge extraction",
            "Public Knowledge Graph",
            "Collaborative graph",
            "Machine learning",
            "Semantic Web"
        ]
    })

    st.dataframe(papers,use_container_width=True)

# --------------------------------------------------------------
# PROCEDURE PAGE
# --------------------------------------------------------------

elif menu=="🧪 Procedure":

    st.markdown('<div class="section">Procedure</div>',unsafe_allow_html=True)

    steps=[
        (
            "Step 1 — Define Knowledge Graph Schema",
            "Create node labels, properties and semantic relationship types for the selected domain."
        ),
        (
            "Step 2 — Build Schema Visually",
            "Use the Schema Builder to add entities and connect labels through relationship types."
        ),
        (
            "Step 3 — Upload Structured Dataset",
            "Upload Nodes CSV and Relationships CSV matching the designed schema."
        ),
        (
            "Step 4 — Validate Dataset",
            "The simulator checks duplicate IDs, missing labels, invalid relationships and datatype errors."
        ),
        (
            "Step 5 — Generate Knowledge Graph",
            "The simulator converts uploaded data into an interactive graph visualization."
        ),
        (
            "Step 6 — Execute Traversal Queries",
            "Run predefined or custom traversal queries to explore the graph."
        ),
        (
            "Step 7 — Observe Graph Traversal",
            "Nodes and relationships light up step-by-step showing traversal paths."
        ),
        (
            "Step 8 — Analyze Graph Statistics",
            "Observe nodes, relationships, degree distribution and connectivity."
        ),
        (
            "Step 9 — Record Observations",
            "Automatically generated observations summarize graph characteristics."
        ),
        (
            "Step 10 — Generate Experiment Report",
            "Download a complete PDF report containing graph visualization and experiment summary."
        )
    ]

    for title,body in steps:

        st.markdown(f"""
<div class="step-box">
<div class="step-title">{title}</div>
<div class="step-body">{body}</div>
</div>
""",unsafe_allow_html=True)

    st.success("Proceed to the Simulation module to perform the experiment.")

# --------------------------------------------------------------
# SIMULATION PLACEHOLDER
# PART 2 STARTS HERE
# --------------------------------------------------------------

# Remaining pages added in later parts.
# ==============================================================
# SIMULATION MODULE — PART 2A
# Dynamic Schema Builder
# ==============================================================

elif menu == "💻 Simulation":

    st.markdown('<div class="section">Simulation Laboratory</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="bodytext">
    Welcome to the interactive Knowledge Graph simulation. This simulation allows you to
    design your own Knowledge Graph schema, upload datasets, generate an interactive graph,
    and visually observe graph traversals.
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # STEP INDICATOR
    # ----------------------------------------------------------

    steps = [
        "1️⃣ Schema Builder",
        "2️⃣ Upload Dataset",
        "3️⃣ Validate Dataset",
        "4️⃣ Generate Graph",
        "5️⃣ Graph Traversal & Exploration"
    ]

    current_step = 1

    cols = st.columns(len(steps))

    for i, c in enumerate(cols):
        if i < current_step:
            c.success(steps[i])
        elif i == current_step - 1:
            c.info(steps[i])
        else:
            c.write(steps[i])

    st.divider()

    # ==========================================================
    # SCHEMA BUILDER
    # ==========================================================

    st.markdown("## 🧩 Step 1 — Create Your Knowledge Graph Schema")

    st.write("""
    Define custom node labels, their properties, and semantic relationships.
    Unlike the previous version, this lab supports **any domain** such as Healthcare,
    Education, Disaster Management, Social Networks, Banking, or E-Commerce.
    """)

    # ----------------------------------------------------------
    # NODE CREATION
    # ----------------------------------------------------------

    st.markdown("### ➕ Create Node Label")

    with st.expander("Add New Node Label", expanded=True):

        col1, col2 = st.columns(2)

        with col1:
            node_label = st.text_input(
                "Node Label",
                placeholder="Example: Person"
            )

        with col2:
            node_color = st.color_picker(
                "Node Color",
                "#38BDF8"
            )

        st.markdown("#### Add Properties")

        if "temp_properties" not in st.session_state:
            st.session_state.temp_properties = []

        p1, p2 = st.columns([4,1])

        with p1:
            new_property = st.text_input(
                "Property Name",
                placeholder="Example: Age"
            )

        with p2:
            st.write("")
            st.write("")

            if st.button("Add Property", key="add_prop_btn"):

                if new_property != "":
                    if new_property not in st.session_state.temp_properties:
                        st.session_state.temp_properties.append(new_property)

        if st.session_state.temp_properties:

            st.markdown("##### Current Properties")

            remove_property = None

            for idx, prop in enumerate(st.session_state.temp_properties):

                c1, c2 = st.columns([5,1])

                with c1:
                    st.success(prop)

                with c2:
                    if st.button("❌", key=f"remove_prop_{idx}"):
                        remove_property = prop

            if remove_property:
                st.session_state.temp_properties.remove(remove_property)
                st.rerun()

        if st.button("Save Node Label", key="save_node"):

            if node_label == "":
                st.error("Node label cannot be empty.")

            else:

                exists = any(
                    node["label"] == node_label
                    for node in st.session_state.schema_nodes
                )

                if exists:
                    st.warning("Node label already exists.")

                else:

                    NODE_COLORS[node_label] = node_color

                    st.session_state.schema_nodes.append({

                        "label": node_label,
                        "properties": st.session_state.temp_properties.copy(),
                        "color": node_color

                    })

                    st.success(f"{node_label} node created successfully!")

                    st.session_state.temp_properties = []

    st.divider()

    # ----------------------------------------------------------
    # DISPLAY SCHEMA NODES
    # ----------------------------------------------------------

    st.markdown("### 📋 Current Schema Nodes")

    if len(st.session_state.schema_nodes) == 0:

        st.info("No node labels created yet.")

    else:

        delete_node = None

        for idx, node in enumerate(st.session_state.schema_nodes):

            with st.container():

                st.markdown(f"""
                <div style="
                    background:#0F172A;
                    border-left:8px solid {node['color']};
                    padding:20px;
                    border-radius:15px;
                    margin-bottom:15px;
                ">
                <h3 style="color:{node['color']};">{node['label']}</h3>
                <b>Properties</b>
                </div>
                """, unsafe_allow_html=True)

                if node["properties"]:

                    cols = st.columns(4)

                    for i, prop in enumerate(node["properties"]):
                        cols[i % 4].info(prop)

                else:
                    st.caption("No properties defined.")

                if st.button("Delete Node", key=f"delete_node_{idx}"):

                    delete_node = node["label"]

        if delete_node:

            st.session_state.schema_nodes = [
                node
                for node in st.session_state.schema_nodes
                if node["label"] != delete_node
            ]

            st.session_state.schema_relationships = [
                rel
                for rel in st.session_state.schema_relationships
                if rel["source"] != delete_node and rel["target"] != delete_node
            ]

            st.success("Node deleted.")

            st.rerun()

    st.divider()

    # ==========================================================
    # RELATIONSHIP BUILDER
    # ==========================================================

    st.markdown("## 🔗 Create Semantic Relationships")

    if len(st.session_state.schema_nodes) < 2:

        st.warning("Create at least two node labels before defining relationships.")

    else:

        labels = [
            node["label"]
            for node in st.session_state.schema_nodes
        ]

        col1, col2, col3 = st.columns(3)

        with col1:
            source_label = st.selectbox(
                "Source Node",
                labels
            )

        with col2:
            relationship_name = st.text_input(
                "Relationship Type",
                placeholder="LIVES_IN"
            )

        with col3:
            target_label = st.selectbox(
                "Target Node",
                labels,
                index=1
            )

        if st.button("Add Relationship", key="save_relationship"):

            if relationship_name == "":
                st.error("Relationship cannot be empty.")

            else:

                exists = any(
                    rel["source"] == source_label
                    and rel["relationship"] == relationship_name
                    and rel["target"] == target_label
                    for rel in st.session_state.schema_relationships
                )

                if exists:
                    st.warning("Relationship already exists.")

                else:

                    st.session_state.schema_relationships.append({

                        "source": source_label,
                        "relationship": relationship_name.upper(),
                        "target": target_label

                    })

                    st.success("Relationship added.")

    st.divider()

    # ----------------------------------------------------------
    # RELATIONSHIP TABLE
    # ----------------------------------------------------------

    st.markdown("### 📑 Current Relationships")

    if len(st.session_state.schema_relationships) == 0:

        st.info("No relationships defined yet.")

    else:

        delete_relationship = None

        for idx, rel in enumerate(st.session_state.schema_relationships):

            c1, c2 = st.columns([7,1])

            with c1:

                st.markdown(f"""
                <div style="
                    padding:18px;
                    background:#091520;
                    border-radius:12px;
                    border-left:6px solid #22C55E;
                    margin-bottom:10px;
                ">

                <span style="font-size:20px;color:#38BDF8;">
                {rel['source']}
                </span>

                <span style="font-size:18px;color:#FACC15;">
                ── {rel['relationship']} ──►
                </span>

                <span style="font-size:20px;color:#22C55E;">
                {rel['target']}
                </span>

                </div>
                """, unsafe_allow_html=True)

            with c2:

                if st.button("🗑️", key=f"delete_rel_{idx}"):

                    delete_relationship = idx

        if delete_relationship is not None:

            st.session_state.schema_relationships.pop(delete_relationship)

            st.success("Relationship removed.")

            st.rerun()

    st.divider()

    # ==========================================================
    # LIVE SCHEMA VISUALIZATION
    # ==========================================================

    st.markdown("## 🌐 Live Schema Visualization")

    st.caption("This diagram updates immediately as you create nodes and relationships.")

    if len(st.session_state.schema_nodes) == 0:

        st.info("Add node labels to visualize your schema.")

    else:

        schema_graph = nx.DiGraph()

        for node in st.session_state.schema_nodes:

            schema_graph.add_node(
                node["label"],
                color=node["color"]
            )

        for rel in st.session_state.schema_relationships:

            schema_graph.add_edge(
                rel["source"],
                rel["target"],
                relationship=rel["relationship"]
            )

        pos = nx.spring_layout(schema_graph, seed=12)

        fig = go.Figure()

        # Draw edges
        for edge in schema_graph.edges():

            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=3, color="#64748B"),
                hoverinfo="text",
                text=schema_graph.edges[edge]["relationship"],
                showlegend=False
            ))

            fig.add_annotation(
                x=(x0+x1)/2,
                y=(y0+y1)/2,
                text=schema_graph.edges[edge]["relationship"],
                showarrow=False,
                font=dict(color="#FACC15", size=14)
            )

        node_x=[]
        node_y=[]
        node_text=[]
        node_colors=[]

        for node,data in schema_graph.nodes(data=True):

            x,y = pos[node]

            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            node_colors.append(data["color"])

        fig.add_trace(go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="bottom center",
            marker=dict(
            size=34,
            color=node_colors,
            symbol="circle",
            line=dict(color="white", width=3),
            opacity=0.95
            ),
            hovertemplate="<b>%{text}</b><extra></extra>"
        ))

        fig.update_layout(
            title=dict(
                text="Live Knowledge Graph Schema",
                font=dict(size=22,color="white")
            ),
            height=600,
            paper_bgcolor="#071019",
            plot_bgcolor="#071019",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=0,r=0,t=0,b=0)
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="live_schema_visualization"
        )

    st.divider()

    # ==========================================================
    # EXPORT SCHEMA
    # ==========================================================

    st.markdown("## 💾 Export or Reset Schema")

    export_data = {

        "nodes": st.session_state.schema_nodes,
        "relationships": st.session_state.schema_relationships

    }

    json_schema = json.dumps(export_data, indent=4)

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "📥 Download Schema JSON",
            json_schema,
            file_name="knowledge_graph_schema.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:

        if st.button("🗑️ Reset Entire Schema", use_container_width=True):

            st.session_state.schema_nodes = []
            st.session_state.schema_relationships = []
            st.session_state.temp_properties = []

            st.success("Schema reset successfully.")
            st.rerun()

    st.divider()

    st.success("✅ Step 1 completed. In Part 2B, users will upload CSV datasets based on this schema.")
    # ==============================================================
    # STEP 2 — DATASET UPLOAD & VALIDATION ENGINE
    # ==============================================================

    st.markdown("---")
    st.markdown("## 📂 Step 2 — Upload Dataset")

    st.write("""
    Upload two CSV files that follow the schema you created above.

    **1. Nodes CSV** — Contains all entities.

    **2. Relationships CSV** — Contains connections between entities.
    """)

    # --------------------------------------------------------------
    # SAMPLE CSV FORMAT
    # --------------------------------------------------------------

    with st.expander("📖 View Expected CSV Format", expanded=False):

        st.markdown("### Nodes CSV Example")

        sample_nodes = pd.DataFrame({
            "ID":["P1","P2","C1","C2"],
            "Label":["Person","Person","City","City"],
            "Name":["Alice","Bob","Mumbai","Pune"],
            "Age":[22,25,None,None],
            "State":[None,None,"Maharashtra","Maharashtra"]
        })

        st.dataframe(sample_nodes, use_container_width=True)

        st.markdown("### Relationships CSV Example")

        sample_rel = pd.DataFrame({
            "Source":["P1","P2"],
            "Relationship":["LIVES_IN","LIVES_IN"],
            "Target":["C1","C2"]
        })

        st.dataframe(sample_rel, use_container_width=True)

        st.download_button(
            "⬇ Download Sample Nodes CSV",
            sample_nodes.to_csv(index=False),
            "sample_nodes.csv",
            "text/csv"
        )

        st.download_button(
            "⬇ Download Sample Relationships CSV",
            sample_rel.to_csv(index=False),
            "sample_relationships.csv",
            "text/csv"
        )

    # --------------------------------------------------------------
    # FILE UPLOADERS
    # --------------------------------------------------------------

    st.markdown("### Upload CSV Files")

    col1, col2 = st.columns(2)

    with col1:
        uploaded_nodes = st.file_uploader(
            "Upload Nodes CSV",
            type="csv",
            key="nodes_csv"
        )

    with col2:
        uploaded_relationships = st.file_uploader(
            "Upload Relationships CSV",
            type="csv",
            key="relationships_csv"
        )

    # --------------------------------------------------------------
    # READ FILES
    # --------------------------------------------------------------

    nodes_df = pd.DataFrame()
    relationships_df = pd.DataFrame()

    if uploaded_nodes is not None:

        try:
            nodes_df = pd.read_csv(uploaded_nodes)
            st.session_state.uploaded_nodes = nodes_df

            st.success("Nodes CSV uploaded successfully.")

        except Exception as e:
            st.error(f"Unable to read Nodes CSV.\n\n{e}")

    if uploaded_relationships is not None:

        try:
            relationships_df = pd.read_csv(uploaded_relationships)
            st.session_state.uploaded_relationships = relationships_df

            st.success("Relationships CSV uploaded successfully.")

        except Exception as e:
            st.error(f"Unable to read Relationships CSV.\n\n{e}")

    # --------------------------------------------------------------
    # DATASET PREVIEW
    # --------------------------------------------------------------

    if not st.session_state.uploaded_nodes.empty:

        st.markdown("---")
        st.markdown("## 👀 Preview Uploaded Nodes")

        st.dataframe(
            st.session_state.uploaded_nodes,
            use_container_width=True
        )

    if not st.session_state.uploaded_relationships.empty:

        st.markdown("## 🔗 Preview Uploaded Relationships")

        st.dataframe(
            st.session_state.uploaded_relationships,
            use_container_width=True
        )

    # ==============================================================
    # VALIDATION ENGINE
    # ==============================================================

    st.markdown("---")
    st.markdown("## ✅ Step 3 — Dataset Validation Engine")

    validation_results = {
        "passed": [],
        "warnings": [],
        "errors": []
    }

    def validate_dataset():

        validation_results["passed"] = []
        validation_results["warnings"] = []
        validation_results["errors"] = []

        if st.session_state.uploaded_nodes.empty:
            validation_results["errors"].append("Nodes CSV not uploaded.")
            return validation_results

        if st.session_state.uploaded_relationships.empty:
            validation_results["errors"].append("Relationships CSV not uploaded.")
            return validation_results

        nodes = st.session_state.uploaded_nodes
        rels = st.session_state.uploaded_relationships

        # ==========================================================
        # AUTO DETECT ENTITY PROPERTIES
        # ==========================================================

        st.markdown("---")
        st.markdown("## 🧩 Auto-Detected Knowledge Graph Schema")

        csv_labels = sorted(nodes["Label"].dropna().unique().tolist())

        detected_schema = []

        for label in csv_labels:

            label_df = nodes[nodes["Label"] == label]

            properties = []

            for col in label_df.columns:

                if col not in ["ID", "Label"]:

                    if label_df[col].notna().any():
                        properties.append(col)

            detected_schema.append({
                "Entity Label": label,
                "Properties": ", ".join(properties)
            })

        schema_df = pd.DataFrame(detected_schema)

        st.dataframe(schema_df, use_container_width=True)

        # ==========================================================
        # AUTO DETECT RELATIONSHIP TYPES
        # ==========================================================

        st.markdown("### 🔗 Relationship Types Detected")

        rel_types = sorted(
            rels["Relationship"].dropna().unique().tolist()
        )

        rel_preview = pd.DataFrame({
            "Relationship Type": rel_types
        })

        st.dataframe(rel_preview, use_container_width=True)

        # ----------------------------------------------------------
        # REQUIRED COLUMNS
        # ----------------------------------------------------------

        required_node_cols = {"ID","Label","Name"}
        required_rel_cols = {"Source","Relationship","Target"}

        if not required_node_cols.issubset(nodes.columns):
            missing = required_node_cols - set(nodes.columns)
            validation_results["errors"].append(
                f"Missing required node columns: {', '.join(missing)}"
            )
        else:
            validation_results["passed"].append("Required node columns found.")

        if not required_rel_cols.issubset(rels.columns):
            missing = required_rel_cols - set(rels.columns)
            validation_results["errors"].append(
                f"Missing relationship columns: {', '.join(missing)}"
            )
        else:
            validation_results["passed"].append("Required relationship columns found.")

        # ----------------------------------------------------------
        # DUPLICATE IDS
        # ----------------------------------------------------------

        duplicates = nodes[nodes["ID"].duplicated()]

        if duplicates.empty:
            validation_results["passed"].append("No duplicate node IDs found.")
        else:
            validation_results["errors"].append(
                f"{len(duplicates)} duplicate node IDs detected."
            )

        # ----------------------------------------------------------
        # EMPTY IDs
        # ----------------------------------------------------------

        empty_ids = nodes["ID"].isna().sum()

        if empty_ids == 0:
            validation_results["passed"].append("All nodes have unique IDs.")
        else:
            validation_results["errors"].append(
                f"{empty_ids} node IDs are missing."
            )

        # ----------------------------------------------------------
        # EMPTY LABELS
        # ----------------------------------------------------------

        empty_labels = nodes["Label"].isna().sum()

        if empty_labels == 0:
            validation_results["passed"].append("Every node contains a label.")
        else:
            validation_results["errors"].append(
                f"{empty_labels} node labels are missing."
            )

        # ==========================================================
        # AUTO DETECT SCHEMA FROM CSV
        # ==========================================================

        csv_labels = sorted(nodes["Label"].dropna().unique().tolist())

        # If manual schema exists, use it.
        # Otherwise automatically create schema labels from CSV.
        # Use labels detected from CSV if no manual schema exists.
        if len(st.session_state.schema_nodes) > 0:
            schema_labels = sorted([
                node["label"]
                for node in st.session_state.schema_nodes
            ])
            schema_source = "Manual Schema Designer"
        else:
            schema_labels = csv_labels
            schema_source = "Auto Detected from Uploaded CSV"

        st.success(f"Schema Source: {schema_source}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📘 Schema Labels")
            st.code(schema_labels)

        with col2:
            st.markdown("### 📄 CSV Labels")
            st.code(csv_labels)

        # ==========================================================
        # LIVE SCHEMA VISUALIZATION
        # ==========================================================

        st.markdown("## 🌐 Detected Schema Visualization")

        schema_graph = nx.DiGraph()

        # Entity Labels
        for label in csv_labels:
            schema_graph.add_node(label, type="Entity")

        # Relationship Types
        for _, row in rels.iterrows():

            source_label = nodes.loc[
                nodes["ID"] == row["Source"],
                "Label"
            ].values

            target_label = nodes.loc[
                nodes["ID"] == row["Target"],
                "Label"
            ].values

            if len(source_label) and len(target_label):
                schema_graph.add_edge(
                    source_label[0],
                    target_label[0],
                    label=row["Relationship"]
                )

        schema_pos = nx.spring_layout(schema_graph, seed=7)
        # Draw detected schema graph

        edge_x = []
        edge_y = []

        for edge in schema_graph.edges():

            x0, y0 = schema_pos[edge[0]]
            x1, y1 = schema_pos[edge[1]]

            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(color="#38BDF8", width=2),
            hoverinfo="none"
        )

        node_x = []
        node_y = []
        node_text = []

        for node in schema_graph.nodes():

            x, y = schema_pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="top center",
            marker=dict(
                size=28,
                color="#22C55E",
                line=dict(width=2, color="white")
            ),
            hoverinfo="text"
        )

        fig = go.Figure(data=[edge_trace, node_trace])

        fig.update_layout(
            height=450,
            paper_bgcolor="#071019",
            plot_bgcolor="#071019",
            font=dict(color="white"),
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            title="Auto-Detected Knowledge Graph Schema"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="auto_detected_schema_visualization"
        )

        # ==========================================================
        # LABEL VALIDATION
        # ==========================================================

        invalid_labels = nodes[
            ~nodes["Label"].isin(schema_labels)
        ]

        if len(invalid_labels) > 0:

            validation_results["errors"].append(
                f"{len(invalid_labels)} nodes contain undefined labels."
            )

            st.error("❌ Undefined Labels Found")

            st.markdown("### Expected Labels")

            st.code(", ".join(schema_labels))

            st.markdown("### Invalid Labels in Uploaded CSV")

            st.code(
                ", ".join(
                    sorted(
                        invalid_labels["Label"].unique().tolist()
                    )
                )
            )

        else:

            st.success("✅ All entity labels are valid.")

        # ----------------------------------------------------------
        # CHECK RELATIONSHIP ENDPOINTS
        # ----------------------------------------------------------

        node_ids = set(nodes["ID"])

        invalid_source = rels[
            ~rels["Source"].isin(node_ids)
        ]

        invalid_target = rels[
            ~rels["Target"].isin(node_ids)
        ]

        if invalid_source.empty:
            validation_results["passed"].append("All relationship source IDs exist.")
        else:
            validation_results["errors"].append(
                f"{len(invalid_source)} invalid relationship source IDs."
            )

        if invalid_target.empty:
            validation_results["passed"].append("All relationship target IDs exist.")
        else:
            validation_results["errors"].append(
                f"{len(invalid_target)} invalid relationship target IDs."
            )

        # ----------------------------------------------------------
        # EMPTY RELATIONSHIP NAME
        # ----------------------------------------------------------

        empty_relationships = rels["Relationship"].isna().sum()

        if empty_relationships == 0:
            validation_results["passed"].append("Every relationship has a relationship type.")
        else:
            validation_results["errors"].append(
                f"{empty_relationships} relationships have empty relationship types."
            )

        # ----------------------------------------------------------
        # SELF LOOPS
        # ----------------------------------------------------------

        self_loops = rels[rels["Source"] == rels["Target"]]

        if self_loops.empty:
            validation_results["passed"].append("No self-loop relationships detected.")
        else:
            validation_results["warnings"].append(
                f"{len(self_loops)} self-loop relationships detected."
            )

        # ----------------------------------------------------------
        # ORPHAN NODES
        # ----------------------------------------------------------

        connected = set(rels["Source"]).union(set(rels["Target"]))

        orphan_nodes = nodes[
            ~nodes["ID"].isin(connected)
        ]

        if orphan_nodes.empty:
            validation_results["passed"].append("Every node participates in at least one relationship.")
        else:
            validation_results["warnings"].append(
                f"{len(orphan_nodes)} orphan nodes detected."
            )

        # ----------------------------------------------------------
        # PROPERTY VALIDATION
        # ----------------------------------------------------------

        schema_property_map = {
            node["label"]: node["properties"]
            for node in st.session_state.schema_nodes
        }

        missing_properties = 0

        for _, row in nodes.iterrows():

            label = row["Label"]

            expected = schema_property_map.get(label, [])

            for prop in expected:

                if prop not in nodes.columns:
                    missing_properties += 1
                elif pd.isna(row[prop]):
                    missing_properties += 1

        if missing_properties == 0:
            validation_results["passed"].append("All required properties are present.")
        else:
            validation_results["warnings"].append(
                f"{missing_properties} property values are missing."
            )

        return validation_results

    # --------------------------------------------------------------
    # RUN VALIDATION
    # --------------------------------------------------------------

    if st.button("🚦 Validate Uploaded Dataset", type="primary"):

        st.session_state.validation_results = validate_dataset()

    # --------------------------------------------------------------
    # SHOW VALIDATION DASHBOARD
    # --------------------------------------------------------------
    # Load latest validation results (or empty defaults)
    results = st.session_state.get(
        "validation_results",
        {
            "passed": [],
            "warnings": [],
            "errors": []
        }
    )

    if (
        not st.session_state.uploaded_nodes.empty
        and not st.session_state.uploaded_relationships.empty
    ):

        p = len(results["passed"])
        w = len(results["warnings"])
        e = len(results["errors"])

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Passed Checks", p)

        with c2:
            st.metric("Warnings", w)

        with c3:
            st.metric("Errors", e)

        st.markdown("### Validation Summary")

        for item in results["passed"]:
            st.success(item)

        for item in results["warnings"]:
            st.warning(item)

        for item in results["errors"]:
            st.error(item)

    # --------------------------------------------------------------
    # VALIDATION DETAILS
    # --------------------------------------------------------------

    if (
        not st.session_state.uploaded_nodes.empty
        and not st.session_state.uploaded_relationships.empty
    ):

        st.markdown("---")
        st.markdown("## 📋 Detailed Validation Report")

        report = []

        for item in validation_results["passed"]:
            report.append(["PASS", item])

        for item in validation_results["warnings"]:
            report.append(["WARNING", item])

        for item in validation_results["errors"]:
            report.append(["ERROR", item])

        report_df = pd.DataFrame(
            report,
            columns=["Status","Description"]
        )

        st.dataframe(report_df, use_container_width=True)

        csv_report = report_df.to_csv(index=False)

        st.download_button(
            "📥 Download Validation Report",
            csv_report,
            file_name="validation_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    # --------------------------------------------------------------
    # DATASET STATISTICS
    # --------------------------------------------------------------

    if not st.session_state.uploaded_nodes.empty:

        st.markdown("---")
        st.markdown("## 📈 Uploaded Dataset Statistics")

        node_df = st.session_state.uploaded_nodes
        rel_df = st.session_state.uploaded_relationships

        total_nodes = len(node_df)
        total_relationships = len(rel_df)

        total_labels = node_df["Label"].nunique()

        total_rel_types = rel_df["Relationship"].nunique()

        metric_cards(
            total_nodes,
            total_relationships,
            total_labels,
            total_rel_types
        )

        st.markdown("### Node Label Distribution")

        label_counts = (
            node_df["Label"]
            .value_counts()
            .reset_index()
        )

        label_counts.columns = ["Label","Count"]

        fig = px.bar(
            label_counts,
            x="Label",
            y="Count",
            text="Count"
        )

        fig.update_layout(
            height=450,
            paper_bgcolor="#071019",
            plot_bgcolor="#071019",
            font=dict(color="white")
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="dataset_node_label_distribution"
        )

        st.markdown("### Relationship Type Distribution")

        rel_counts = (
            rel_df["Relationship"]
            .value_counts()
            .reset_index()
        )

        rel_counts.columns = ["Relationship","Count"]

        fig2 = px.pie(
            rel_counts,
            names="Relationship",
            values="Count"
        )

        fig2.update_layout(
            height=450,
            paper_bgcolor="#071019",
            font=dict(color="white")
        )

        st.plotly_chart(fig2, use_container_width=True)

    # --------------------------------------------------------------
    # READY TO BUILD GRAPH
    # --------------------------------------------------------------

    if (
        not st.session_state.uploaded_nodes.empty
        and not st.session_state.uploaded_relationships.empty
    ):

        if len(validation_results["errors"]) == 0:

            st.success("""
    ### ✅ Dataset Successfully Validated

    The uploaded dataset is ready for Knowledge Graph generation.

    **Next Step:** Generate the graph and begin interactive traversal.
    """)

        else:

            st.error("""
    ### ❌ Dataset contains validation errors.

    Please fix the CSV files before generating the graph.
    """)

    # ==============================================================
    # STEP 4 — GENERATE KNOWLEDGE GRAPH
    # ==============================================================

    st.markdown("---")
    st.markdown("## 🌐 Step 4 — Generate Interactive Knowledge Graph")

    st.write("""
    After validation, the uploaded CSV files are converted into a dynamic
    Knowledge Graph. Every entity becomes a node and every relationship becomes
    an edge. The graph supports zooming, panning, searching, traversal animation,
    and graph exploration.
    """)

    # ----------------------------------------------------------
    # BUILD GRAPH BUTTON
    # ----------------------------------------------------------

    can_generate = (
        not st.session_state.uploaded_nodes.empty and
        not st.session_state.uploaded_relationships.empty and
        len(validation_results["errors"]) == 0
    )

    if can_generate:

        if st.button("⚡ Generate Knowledge Graph", type="primary"):

            with st.spinner("Building Knowledge Graph..."):

                G = build_networkx_graph(
                    st.session_state.uploaded_nodes,
                    st.session_state.uploaded_relationships
                )

                st.session_state.graph = G
                st.session_state.graph_generated = True

                st.success("""
                ## 🎉 Knowledge Graph Generated Successfully

                Your uploaded dataset has been converted into a dynamic interactive Knowledge Graph.

                You can now:
                - Explore entities.
                - Run graph traversals.
                - Execute semantic queries.
                - Analyze graph statistics.
                """)

                st.balloons()

    else:
        st.warning("Please upload and validate a correct dataset first.")

    # ----------------------------------------------------------
    # GRAPH STATISTICS
    # ----------------------------------------------------------

    if st.session_state.graph_generated:

        G = st.session_state.graph

        stats = {
            "nodes": len(G.nodes),
            "edges": len(G.edges),
            "labels": st.session_state.uploaded_nodes["Label"].nunique(),
            "relationship_types": st.session_state.uploaded_relationships["Relationship"].nunique(),
            "density": round(nx.density(G),3),
            "connected_components": nx.number_weakly_connected_components(G),
            "average_degree": round(sum(dict(G.degree()).values())/len(G.nodes),2)
        }

        st.session_state.graph_stats = stats

        st.markdown("### 📊 Graph Statistics")

        metric_cards(
            stats["nodes"],
            stats["edges"],
            stats["labels"],
            stats["relationship_types"]
        )

        c1,c2,c3 = st.columns(3)

        c1.metric("Density",stats["density"])
        c2.metric("Connected Components",stats["connected_components"])
        c3.metric("Average Degree",stats["average_degree"])

    # ==============================================================
    # DRAW DEFAULT GRAPH
    # ==============================================================

    if st.session_state.graph_generated:

        st.markdown("---")
        st.markdown("## 🕸 Interactive Knowledge Graph")

        fig = draw_graph()
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="interactive_knowledge_graph_main"
        )

    # ==============================================================
    # GRAPH SEARCH PANEL
    # ==============================================================

    if st.session_state.graph_generated:

        G = st.session_state.graph

        st.markdown("---")
        st.markdown("## 🔍 Search Entity")

        node_names = [
            G.nodes[n]["Name"]
            for n in G.nodes
        ]

        selected_name = st.selectbox(
            "Select Entity",
            sorted(node_names)
        )

        selected_node = None

        for n,data in G.nodes(data=True):
            if data["Name"] == selected_name:
                selected_node = n

        if selected_node:

            fig = draw_graph(highlight_nodes=[selected_node])

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"search_entity_graph_{selected_node}"
            )

            st.markdown("### Entity Information")

            entity = G.nodes[selected_node]

            info_df = pd.DataFrame({
                "Property":entity.keys(),
                "Value":entity.values()
            })

            st.dataframe(info_df,use_container_width=True)

            st.markdown("### Connected Neighbours")

            neighbours=[]

            for neighbour in G.neighbors(selected_node):

                rel = G.edges[selected_node,neighbour]["relationship"]

                neighbours.append({
                    "Entity":G.nodes[neighbour]["Name"],
                    "Relationship":rel
                })

            if neighbours:
                st.dataframe(pd.DataFrame(neighbours),use_container_width=True)
            else:
                st.info("This node has no outgoing relationships.")

            # ----------------------------------------------------------
            # ENTITY INSPECTOR
            # ----------------------------------------------------------

            st.markdown("---")
            st.markdown("## 🧾 Entity Inspector")

            with st.container():

                st.markdown(f"""
                <div style="
                    background:#0F172A;
                    padding:20px;
                    border-radius:15px;
                    border-left:8px solid #38BDF8;
                ">
                <h3 style="color:#7DD3FC;">{entity["Name"]}</h3>
                <p><b>Entity ID:</b> {selected_node}</p>
                <p><b>Node Label:</b> {entity["Label"]}</p>
                </div>
                """, unsafe_allow_html=True)

            properties = []
            for key in entity:
                properties.append({
                    "Property": key,
                    "Value": entity[key]
                })

            st.dataframe(
                pd.DataFrame(properties),
                use_container_width=True
            )
            # ==========================================================
            # 1-HOP / 2-HOP NEIGHBORHOOD EXPLORER
            # ==========================================================

            st.markdown("---")
            st.markdown("## 🌍 Neighborhood Explorer")
            # Safety check: Don't show explorer if graph is empty
            if len(G.nodes) == 0:
                st.warning("Knowledge Graph is empty. Generate a graph first.")
                st.stop()

            explore_node = st.selectbox(
                "Choose an Entity to Explore",
                list(G.nodes),
                format_func=lambda x: G.nodes[x]["Name"],
                key="explorer_node"
            )

            hop = st.radio(
                "Neighborhood Depth",
                [1, 2],
                horizontal=True
            )

            visited = {explore_node}
            frontier = {explore_node}

            for _ in range(hop):

                nxt = set()

                for node in frontier:
                    nxt.update(G.neighbors(node))

                visited.update(nxt)
                frontier = nxt

            subgraph = G.subgraph(visited)

                # Save original graph temporarily
            original_graph = st.session_state.graph
            st.session_state.graph = subgraph

            fig = draw_graph(
                highlight_nodes=list(visited),
                highlight_edges=list(subgraph.edges())
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"neighborhood_explorer_{explore_node}_{hop}"
            )

                # Restore graph
            st.session_state.graph = original_graph

            st.success(
                f"Showing {hop}-hop neighborhood around **{G.nodes[explore_node]['Name']}**."
            )

            neighbor_table = []

            for node in visited:

                neighbor_table.append({
                    "Entity": G.nodes[node]["Name"],
                    "Label": G.nodes[node]["Label"],
                    "Degree": G.degree(node)
                })

            st.dataframe(
                pd.DataFrame(neighbor_table),
                use_container_width=True
            )

    # ==============================================================
    # FILTER GRAPH BY LABEL
    # ==============================================================

    if st.session_state.graph_generated:

        st.markdown("---")
        st.markdown("## 🎨 Filter Graph by Node Labels")

        available_labels = sorted(
            st.session_state.uploaded_nodes["Label"].unique()
        )

        chosen_labels = st.multiselect(
            "Select labels to display",
            available_labels,
            default=available_labels
        )

        if chosen_labels:

            filtered_nodes = st.session_state.uploaded_nodes[
                st.session_state.uploaded_nodes["Label"].isin(chosen_labels)
            ]

            ids = filtered_nodes["ID"].tolist()

            rels = st.session_state.uploaded_relationships

            filtered_relationships = rels[
                rels["Source"].isin(ids) &
                rels["Target"].isin(ids)
            ]

            temp_graph = build_networkx_graph(
                filtered_nodes,
                filtered_relationships
            )

            original_graph = st.session_state.graph

            st.session_state.graph = temp_graph

            fig = draw_graph()
            st.plotly_chart(
                fig,
                use_container_width=True,
                key="schema_visualization_graph"
            )  

            st.session_state.graph = original_graph
    # ==============================================================
    # STEP 5 — SCROLL / TIMELINE TRAVERSAL ENGINE
    # Replaces the traversal section from Part 2C
    # ==============================================================

    import time

    st.markdown("---")
    st.markdown("## 🎬 Interactive Traversal Timeline")

    st.write("""
    This simulator visualizes how graph traversal works **step-by-step**.

    Use the timeline slider (or Play button) to move through the traversal.
    Each step lights up nodes and relationships exactly in the order they are visited.
    """)

    G = st.session_state.graph

    # ------------------------------------------------------------
    # BUILD TRAVERSAL EVENTS
    # ------------------------------------------------------------

    def build_traversal_events(graph, traversal_nodes):

        events=[]

        visited=[]

        for i,node in enumerate(traversal_nodes):

            visited.append(node)

            events.append({
                "step":len(events),
                "type":"NODE",
                "node":node,
                "visited":visited.copy(),
                "edges":[],
                "title":f"Visit Node {graph.nodes[node]['Name']}",
                "description":
                    f"The traversal visits **{graph.nodes[node]['Name']}**."
            })

            if i < len(traversal_nodes)-1:

                nxt = traversal_nodes[i+1]

                if graph.has_edge(node,nxt):

                    events.append({

                        "step":len(events),
                        "type":"EDGE",
                        "node":nxt,
                        "visited":visited.copy()+[nxt],
                        "edges":[(node,nxt)],
                        "title":f"Traverse Relationship ({graph.edges[node,nxt]['relationship']})",
                        "description":
                            f"Traversal follows **{graph.edges[node,nxt]['relationship']}** "
                            f"from **{graph.nodes[node]['Name']}** "
                            f"to **{graph.nodes[nxt]['Name']}**."

                    })

        return events

    # ------------------------------------------------------------
    # SELECT TRAVERSAL TYPE
    # ------------------------------------------------------------

    traversal_mode = st.selectbox(
        "Traversal Mode",
        [
            "Breadth First Search (BFS)",
            "Depth First Search (DFS)",
            "Shortest Path",
            "Neighbours of Entity"
        ]
    )

    if "last_traversal_mode" not in st.session_state:
        st.session_state.last_traversal_mode = traversal_mode

    if st.session_state.last_traversal_mode != traversal_mode:
        st.session_state.timeline_step = 0
        st.session_state.last_traversal_mode = traversal_mode

    # ------------------------------------------------------------
    # GENERATE TRAVERSAL LIST
    # ------------------------------------------------------------

    traversal_nodes=[]

    if traversal_mode=="Breadth First Search (BFS)":

        # Don't continue if graph is empty
        if len(G.nodes) == 0:
            st.warning("Generate a Knowledge Graph first before running traversals.")
            st.stop()

        start = st.selectbox(
            "Start Node",
            options=list(G.nodes),
            format_func=lambda x: G.nodes[x]["Name"],
            key="traversal_start_node"
        )

        # Extra safety check
        if start is None:
            st.info("Please select a start node.")
            st.stop()

        if start in G.nodes:
            traversal_nodes = list(nx.bfs_tree(G, start))
        else:
            traversal_nodes = []

    elif traversal_mode=="Depth First Search (DFS)":

    # Don't continue if graph is empty
        if len(G.nodes) == 0:
            st.warning("Generate a Knowledge Graph first before running traversals.")
            st.stop()

        start = st.selectbox(
            "Start Node",
            options=list(G.nodes),
            format_func=lambda x: G.nodes[x]["Name"],
            key="traversal_start_node"
        )

        # Extra safety check
        if start is None:
            st.info("Please select a start node.")
            st.stop()

        if start in G.nodes:
            traversal_nodes = list(nx.dfs_tree(G, start))
        else:
            traversal_nodes = []

    elif traversal_mode=="Shortest Path":

        c1,c2=st.columns(2)

        with c1:
            source=st.selectbox(
                "Source Node",
                list(G.nodes),
                format_func=lambda x:G.nodes[x]["Name"],
                key="timeline_source"
            )

        with c2:
            target=st.selectbox(
                "Target Node",
                list(G.nodes),
                format_func=lambda x:G.nodes[x]["Name"],
                key="timeline_target"
            )

        try:
            if source is not None and target is not None and source in G.nodes and target in G.nodes:
                try:
                    traversal_nodes = nx.shortest_path(G,source,target)
                except nx.NetworkXNoPath:
                    traversal_nodes = []
                    st.error("No path exists between these entities.")
            else:
                traversal_nodes = []
        except:

            traversal_nodes=[]

    elif traversal_mode=="Neighbours of Entity":

        node=st.selectbox(
            "Choose Entity",
            list(G.nodes),
            format_func=lambda x:G.nodes[x]["Name"],
            key="timeline_neighbours"
        )

        traversal_nodes=[node]+list(G.neighbors(node))

    # ------------------------------------------------------------
    # BUILD TIMELINE EVENTS
    # ------------------------------------------------------------

    events=build_traversal_events(G,traversal_nodes)

    total_steps=max(len(events)-1,0)

    if len(events) == 0:
        st.warning("No traversal path available for the selected query.")
        st.stop()

    if "timeline_step" not in st.session_state:
        st.session_state.timeline_step=0

    # ------------------------------------------------------------
    # CONTROLS
    # ------------------------------------------------------------

    st.markdown("### 🎮 Traversal Controls")

    c1,c2,c3,c4,c5=st.columns(5)

    with c1:

        if st.button("⏮ Previous"):

            st.session_state.timeline_step=max(
                0,
                st.session_state.timeline_step-1
            )

    with c2:

        if st.button("▶ Play"):

            if st.session_state.timeline_step < total_steps:
                st.session_state.timeline_step += 1
                st.rerun()

    with c3:

        if st.button("⏭ Next"):

            st.session_state.timeline_step=min(
                total_steps,
                st.session_state.timeline_step+1
            )

    with c4:

        if st.button("🔄 Reset"):

            st.session_state.timeline_step=0

    with c5:

        if st.button("⏸ Pause"):
            pass

    # ------------------------------------------------------------
    # TIMELINE SLIDER (SCROLL)
    # ------------------------------------------------------------

    st.markdown("### 🖱 Scroll Through Traversal")

    scroll_controller()

    if "timeline_step" not in st.session_state:
        st.session_state.timeline_step = 0

    timeline_step = st.slider(
        "Traversal Timeline",
        min_value=0,
        max_value=total_steps,
        value=st.session_state.timeline_step,
        key="timeline_slider"
    )

    st.session_state.timeline_step = timeline_step

    progress = (
        (timeline_step + 1) / (total_steps + 1)
        if total_steps >= 0
        else 0
    )

    st.progress(progress)

    st.caption(
        f"Traversal Step {timeline_step+1} of {total_steps+1}"
    )

    # ------------------------------------------------------------
    # DRAW GRAPH ACCORDING TO STEP
    # ------------------------------------------------------------

    if events:

        current_event = events[timeline_step]

        highlighted_nodes=current_event["visited"]

        highlighted_edges=[]

        for i in range(len(highlighted_nodes)-1):

            a=highlighted_nodes[i]
            b=highlighted_nodes[i+1]

            if G.has_edge(a,b):
                highlighted_edges.append((a,b))

        highlighted_edges.extend(current_event["edges"])

        fig = draw_graph(
            highlight_nodes=highlighted_nodes,
            highlight_edges=highlighted_edges
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"traversal_timeline_step_{timeline_step}"
        )

        # --------------------------------------------------------
        # EXPLANATION PANEL
        # --------------------------------------------------------

        st.markdown("---")
        st.markdown("## 📖 Step Explanation")

        st.markdown(f"""
        <div style="
            background:#0F172A;
            border-left:8px solid #FACC15;
            padding:25px;
            border-radius:15px;
            margin-bottom:20px;
        ">
            <h3 style="color:#FACC15;">{current_event["title"]}</h3>
            <p style="font-size:18px;color:white;">
            {current_event["description"]}
            </p>
        </div>
        """,unsafe_allow_html=True)

        # --------------------------------------------------------
        # VISITED TABLE
        # --------------------------------------------------------

        st.markdown("### ✅ Nodes Visited So Far")

        visited_table=[]

        for idx,node in enumerate(highlighted_nodes,start=1):

            visited_table.append({
                "Traversal Step":idx,
                "Entity":G.nodes[node]["Name"],
                "Label":G.nodes[node]["Label"]
            })

        st.dataframe(
            pd.DataFrame(visited_table),
            use_container_width=True
        )

        # --------------------------------------------------------
        # RELATIONSHIP TABLE
        # --------------------------------------------------------

        st.markdown("### 🔗 Relationships Traversed")

        rel_table=[]

        for edge in highlighted_edges:

            rel_table.append({
                "Source":G.nodes[edge[0]]["Name"],
                "Relationship":G.edges[edge]["relationship"],
                "Target":G.nodes[edge[1]]["Name"]
            })

        if rel_table:
            st.dataframe(
                pd.DataFrame(rel_table),
                use_container_width=True
            )
        else:
            st.info("No relationships traversed yet.")

        # ------------------------------------------------------------
        # MINI TIMELINE PANEL
        # ------------------------------------------------------------

        st.markdown("---")
        st.markdown("## ⏱ Traversal Timeline")

        timeline=[]

        for event in events:

            icon="🟡"

            if event["type"]=="EDGE":
                icon="🔵"

            timeline.append({
                "Step":event["step"]+1,
                "Event":icon,
                "Description":event["title"]
            })

        timeline_df=pd.DataFrame(timeline)

        timeline_df["Current"] = timeline_df.index == timeline_step

        st.dataframe(
            timeline_df,
            use_container_width=True,
            height=350
        )

        # ------------------------------------------------------------
        # AUTO PLAY ANIMATION
        # ------------------------------------------------------------

        st.markdown("---")
        st.markdown("## 🎥 Auto Traversal Demonstration")

        speed=st.slider(
            "Animation Speed (seconds per step)",
            0.2,
            2.0,
            0.7,
            0.1
        )

        if st.button("▶ Start Automatic Animation"):

            graph_placeholder=st.empty()
            info_placeholder=st.empty()

            visited=[]
            edges=[]

            for event in events:

                visited=event["visited"]

                edges=[]

                for i in range(len(visited)-1):

                    if G.has_edge(visited[i],visited[i+1]):
                        edges.append((visited[i],visited[i+1]))

                graph_placeholder.plotly_chart(
                    draw_graph(
                        highlight_nodes=visited,
                        highlight_edges=edges
                    ),
                    use_container_width=True
                )

                info_placeholder.markdown(f"""
                <div style="
                    background:#082F49;
                    padding:18px;
                    border-radius:12px;
                    border-left:6px solid #38BDF8;
                ">
                <h4 style="color:#7DD3FC;">Step {event["step"]+1}</h4>
                <b>{event["title"]}</b>

                {event["description"]}
                </div>
                """,unsafe_allow_html=True)

                time.sleep(speed)

            st.success("Traversal animation completed!")

        # ------------------------------------------------------------
        # QUERY HISTORY
        # ------------------------------------------------------------

        if "query_history" not in st.session_state:
            st.session_state.query_history=[]
        if (
            len(st.session_state.query_history) == 0
            or st.session_state.query_history[-1] != traversal_mode
        ):
            st.session_state.query_history.append(traversal_mode)

        st.markdown("---")
        st.markdown("## 🕘 Traversal History")

        history_df=pd.DataFrame({
            "Executed Traversals":st.session_state.query_history
        })

        st.dataframe(history_df,use_container_width=True)

        # ------------------------------------------------------------
        # LEGEND
        # ------------------------------------------------------------

        st.markdown("---")
        st.markdown("## 🎨 Traversal Legend")

        legend_cols=st.columns(4)

        legend_cols[0].markdown("🟡 **Visited Node**")
        legend_cols[1].markdown("🔵 **Traversed Relationship**")
        legend_cols[2].markdown("⚪ **Unvisited Node**")
        legend_cols[3].markdown("🟢 **Final Traversal Path**")

        st.success("Interactive Timeline Traversal Ready.")

# ==============================================================
# OBSERVATIONS MODULE
# Dynamic Graph Analysis
# ==============================================================

elif menu == "📊 Observations":

    st.markdown('<div class="section">Observations</div>', unsafe_allow_html=True)

    st.write("""
    The observation module automatically analyzes the uploaded Knowledge Graph
    and generates experiment observations similar to an IIT Virtual Laboratory.
    Every observation changes depending on the student's uploaded dataset.
    """)

    if not st.session_state.graph_generated:

        st.warning("Generate a Knowledge Graph in the Simulation module first.")

    else:

        G = st.session_state.graph
        nodes_df = st.session_state.uploaded_nodes
        rel_df = st.session_state.uploaded_relationships

        if not st.session_state.graph_generated or len(G.nodes) == 0:
            st.warning("No Knowledge Graph available. Please generate a graph in the Simulation module.")
            st.stop()

        # ------------------------------------------------------
        # BASIC METRICS
        # ------------------------------------------------------

        total_nodes = len(G.nodes)
        total_edges = len(G.edges)
        total_labels = nodes_df["Label"].nunique()
        total_rel_types = rel_df["Relationship"].nunique()

        metric_cards(
            total_nodes,
            total_edges,
            total_labels,
            total_rel_types
        )

        st.divider()

        # ------------------------------------------------------
        # GRAPH VISUALIZATION SNAPSHOT
        # ------------------------------------------------------

        st.markdown("## 🌐 Knowledge Graph Snapshot")

        fig = draw_graph()

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="observations_graph_snapshot"
        )

        st.caption(
            "This is the current Knowledge Graph generated from the uploaded dataset."
        )

        # ------------------------------------------------------
        # GRAPH PROPERTIES
        # ------------------------------------------------------

        density = round(nx.density(G), 4)

        weak_components = nx.number_weakly_connected_components(G)

        avg_degree = round(sum(dict(G.degree()).values()) / total_nodes, 2)

        max_degree_node = max(G.degree(), key=lambda x: x[1])[0]

        max_degree_name = G.nodes[max_degree_node]["Name"]

        max_degree_value = G.degree(max_degree_node)

        observations = [
            f"The generated Knowledge Graph contains **{total_nodes} entity nodes**.",
            f"The graph contains **{total_edges} semantic relationships**.",
            f"The uploaded dataset contains **{total_labels} different node labels**.",
            f"The graph contains **{total_rel_types} relationship types**.",
            f"The graph density is **{density}**, indicating the connectivity between entities.",
            f"The graph consists of **{weak_components} connected component(s)**.",
            f"The average degree of the graph is **{avg_degree}**.",
            f"The most connected entity is **{max_degree_name}** with degree **{max_degree_value}**."
        ]

        st.markdown("## Automatic Observations")

        for idx, obs in enumerate(observations, start=1):

            st.markdown(f"""
            <div class="card">
                <h3>Observation {idx}</h3>
                <p>{obs}</p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ------------------------------------------------------
        # NODE LABEL DISTRIBUTION
        # ------------------------------------------------------

        st.markdown("## Node Label Analysis")

        label_distribution = (
            nodes_df["Label"]
            .value_counts()
            .reset_index()
        )

        label_distribution.columns = ["Node Label", "Count"]

        st.dataframe(label_distribution, use_container_width=True)

        fig = px.bar(
            label_distribution,
            x="Node Label",
            y="Count",
            text="Count",
            title="Distribution of Node Labels"
        )

        fig.update_layout(
            height=450,
            paper_bgcolor="#071019",
            plot_bgcolor="#071019",
            font=dict(color="white")
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="observations_node_label_distribution"
        )

        st.divider()

        # ------------------------------------------------------
        # RELATIONSHIP ANALYSIS
        # ------------------------------------------------------

        st.markdown("## Relationship Analysis")

        rel_distribution = (
            rel_df["Relationship"]
            .value_counts()
            .reset_index()
        )

        rel_distribution.columns = ["Relationship", "Count"]

        st.dataframe(rel_distribution, use_container_width=True)

        pie = px.pie(
            rel_distribution,
            names="Relationship",
            values="Count",
            title="Relationship Type Distribution"
        )

        pie.update_layout(
            paper_bgcolor="#071019",
            font=dict(color="white")
        )

        st.plotly_chart(pie, use_container_width=True)

        st.divider()

        # ------------------------------------------------------
        # DEGREE ANALYSIS
        # ------------------------------------------------------

        st.markdown("## Degree Centrality Analysis")

        degree_df = pd.DataFrame({
            "Entity ID": list(dict(G.degree()).keys()),
            "Degree": list(dict(G.degree()).values())
        })

        degree_df["Entity Name"] = degree_df["Entity ID"].apply(
            lambda x: G.nodes[x]["Name"]
        )

        degree_df = degree_df.sort_values(
            "Degree",
            ascending=False
        )

        st.dataframe(degree_df, use_container_width=True)

        degree_chart = px.bar(
            degree_df,
            x="Entity Name",
            y="Degree",
            text="Degree",
            title="Degree of Every Entity"
        )

        degree_chart.update_layout(
            height=500,
            paper_bgcolor="#071019",
            plot_bgcolor="#071019",
            font=dict(color="white")
        )

        st.plotly_chart(degree_chart, use_container_width=True)

        st.divider()

        # ------------------------------------------------------
        # TOP CONNECTED ENTITIES
        # ------------------------------------------------------

        st.markdown("## 🏆 Top 5 Most Connected Entities")

        top5 = degree_df.head(5).copy()

        top5.index = range(1, len(top5)+1)

        st.dataframe(top5, use_container_width=True)

        top_chart = px.bar(
            top5,
            x="Entity Name",
            y="Degree",
            text="Degree",
            title="Top Connected Entities"
        )

        top_chart.update_layout(
            paper_bgcolor="#071019",
            plot_bgcolor="#071019",
            font=dict(color="white"),
            height=400
        )

        st.plotly_chart(top_chart, use_container_width=True)

        # ------------------------------------------------------
        # CONNECTED COMPONENTS
        # ------------------------------------------------------

        st.markdown("## Connected Components")

        components = list(nx.weakly_connected_components(G))

        component_rows = []

        for i, comp in enumerate(components, start=1):

            names = [
                G.nodes[node]["Name"]
                for node in comp
            ]

            component_rows.append({
                "Component": i,
                "Nodes": len(comp),
                "Entities": ", ".join(names)
            })

        st.dataframe(
            pd.DataFrame(component_rows),
            use_container_width=True
        )

        st.divider()

        # ------------------------------------------------------
        # ISOLATED / ORPHAN NODES
        # ------------------------------------------------------

        st.markdown("## Orphan Node Analysis")

        orphan = [
            node
            for node in G.nodes
            if G.degree(node) == 0
        ]

        if orphan:

            orphan_df = pd.DataFrame({
                "Entity": [
                    G.nodes[n]["Name"]
                    for n in orphan
                ],
                "Label": [
                    G.nodes[n]["Label"]
                    for n in orphan
                ]
            })

            st.warning(f"{len(orphan)} orphan nodes detected.")

            st.dataframe(orphan_df, use_container_width=True)

        else:

            st.success("No orphan nodes were found in the uploaded graph.")

        st.divider()

        # ------------------------------------------------------
        # PROPERTY COMPLETENESS
        # ------------------------------------------------------

        st.markdown("## Property Completeness Analysis")

        property_summary = []

        for label in nodes_df["Label"].unique():

            subset = nodes_df[nodes_df["Label"] == label]

            missing_values = subset.isna().sum().sum()

            filled_values = subset.notna().sum().sum()

            total_values = filled_values + missing_values

            if total_values == 0:
                completeness = 100
            else:
                completeness = round(
                    (filled_values / total_values) * 100,
                    2
                )

            property_summary.append({
                "Label": label,
                "Records": len(subset),
                "Missing Values": int(missing_values),
                "Completeness (%)": completeness
            })

        property_df = pd.DataFrame(property_summary)

        st.dataframe(property_df, use_container_width=True)

        completeness_chart = px.bar(
            property_df,
            x="Label",
            y="Completeness (%)",
            text="Completeness (%)",
            title="Property Completeness by Label"
        )

        completeness_chart.update_layout(
            height=450,
            paper_bgcolor="#071019",
            plot_bgcolor="#071019",
            font=dict(color="white")
        )

        st.plotly_chart(completeness_chart, use_container_width=True)

        st.divider()

        # ------------------------------------------------------
        # GRAPH SUMMARY TABLE
        # ------------------------------------------------------

        st.markdown("## Graph Summary")

        summary_df = pd.DataFrame({
            "Metric":[
                "Total Nodes",
                "Total Relationships",
                "Node Labels",
                "Relationship Types",
                "Graph Density",
                "Average Degree",
                "Connected Components",
                "Most Connected Node"
            ],
            "Value":[
                total_nodes,
                total_edges,
                total_labels,
                total_rel_types,
                density,
                avg_degree,
                weak_components,
                max_degree_name
            ]
        })

        st.dataframe(summary_df, use_container_width=True)

        # Combine all observation tables into one Excel-style CSV

        combined = pd.concat([
            summary_df.assign(Category="Summary"),
            label_distribution.rename(columns={
                "Node Label":"Metric",
                "Count":"Value"
            }).assign(Category="Node Labels"),
            rel_distribution.rename(columns={
                "Relationship":"Metric",
                "Count":"Value"
            }).assign(Category="Relationships")
        ], ignore_index=True)

        st.download_button(
            "📥 Download Complete Observation Report",
            combined.to_csv(index=False),
            file_name="knowledge_graph_observations.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.divider()

        # ------------------------------------------------------
        # AUTO-GENERATED CONCLUSION
        # ------------------------------------------------------

        st.markdown("## Experiment Conclusion")

        st.markdown(f"""
            <div class="card">

            ### Automatically Generated Conclusion

            The uploaded dataset was successfully transformed into a dynamic Knowledge Graph consisting of **{total_nodes} nodes** and **{total_edges} relationships**. The graph represents **{total_labels} categories of entities** connected through **{total_rel_types} semantic relationship types**.

            The graph has an average degree of **{avg_degree}**, a density of **{density}**, and contains **{weak_components} connected component(s)**. The entity **{max_degree_name}** is the most connected node in the graph, indicating its importance within the network.

            The experiment demonstrates how structured data can be represented as interconnected knowledge, enabling graph traversal, semantic querying, visualization, and graph analytics.

            </div>
            """, unsafe_allow_html=True)

        st.success("Dynamic observations generated successfully.")

# ==============================================================
# ASSIGNMENT MODULE (IIT Virtual Lab Style)
# 50 MCQ BANK → RANDOM 10 QUESTIONS
# ==============================================================

elif menu == "📝 Assignment":

    st.markdown('<div class="section">Assignment</div>', unsafe_allow_html=True)

    st.write("""
    The assignment consists of **10 randomly generated MCQs** selected from a bank
    of **50 Knowledge Graph questions**. Every attempt generates a new paper.
    Time Limit: **20 Minutes**.
    """)

    # ----------------------------------------------------------
    # LOAD QUESTION BANK
    # ----------------------------------------------------------

    if not st.session_state.assignment_bank_loaded:

        QUESTION_BANK = [

            {
                "question":"What is a Knowledge Graph?",
                "options":[
                    "A graph database that stores only numbers",
                    "A semantic graph connecting entities and relationships",
                    "A SQL table represented as a graph",
                    "A visualization library"
                ],
                "answer":1,
                "explanation":"Knowledge Graphs represent entities and semantic relationships."
            },

            {
                "question":"Which of the following represents an entity?",
                "options":["Age","Lives In","Mumbai","Connected To"],
                "answer":2,
                "explanation":"Mumbai is a real-world entity."
            },

            {
                "question":"Which language is primarily used with Neo4j?",
                "options":["SQL","Cypher","SPARQL","Python"],
                "answer":1,
                "explanation":"Neo4j uses Cypher query language."
            },

            {
                "question":"A relationship connects ______.",
                "options":[
                    "Rows",
                    "Columns",
                    "Entities",
                    "Databases"
                ],
                "answer":2,
                "explanation":"Relationships connect two entities."
            },

            {
                "question":"RDF stands for:",
                "options":[
                    "Resource Data Framework",
                    "Relational Data Format",
                    "Resource Description Framework",
                    "Reference Data File"
                ],
                "answer":2,
                "explanation":"RDF = Resource Description Framework."
            },

            {
                "question":"A Knowledge Graph triple contains:",
                "options":[
                    "Node Edge Label",
                    "Subject Predicate Object",
                    "Entity Property Label",
                    "Graph Vertex Weight"
                ],
                "answer":1,
                "explanation":"Every RDF statement is Subject-Predicate-Object."
            },

            {
                "question":"SPARQL is used for:",
                "options":[
                    "Graph visualization",
                    "Querying RDF graphs",
                    "Creating CSV",
                    "Building UI"
                ],
                "answer":1,
                "explanation":"SPARQL queries RDF datasets."
            },

            {
                "question":"Ontology defines:",
                "options":[
                    "Database tables",
                    "Semantic vocabulary and rules",
                    "Programming syntax",
                    "Network topology"
                ],
                "answer":1,
                "explanation":"Ontology defines classes, properties and semantics."
            },

            {
                "question":"Which graph traversal explores neighbours level by level?",
                "options":["DFS","BFS","Dijkstra","A*"],
                "answer":1,
                "explanation":"Breadth First Search explores level-wise."
            },

            {
                "question":"Which traversal goes deep before backtracking?",
                "options":["DFS","BFS","Random Walk","Shortest Path"],
                "answer":0,
                "explanation":"Depth First Search visits depth before siblings."
            }

        ]

        # ---------- Generate Remaining Questions Automatically ----------
        topics = [
            "Neo4j","Cypher","RDF","Ontology","SPARQL","Graph Database",
            "Knowledge Representation","Node Labels","Properties",
            "Relationships","Traversal","Shortest Path","Centrality",
            "Degree","Connected Components","Semantic Web","DBpedia",
            "Wikidata","Google Knowledge Graph","Healthcare KG",
            "Fraud Detection","Recommendation Systems","Property Graph",
            "Schema Design","Graph Analytics","NetworkX","Graph Density",
            "Adjacency Matrix","Entity Resolution","Graph Embeddings"
        ]

        while len(QUESTION_BANK) < 50:
            topic = topics[(len(QUESTION_BANK)-10) % len(topics)]

            QUESTION_BANK.append({
                "question":f"Which statement is TRUE regarding {topic}?",
                "options":[
                    f"{topic} is unrelated to Knowledge Graphs.",
                    f"{topic} is an important concept used in Knowledge Graph systems.",
                    f"{topic} is only used in relational databases.",
                    f"{topic} cannot represent entities."
                ],
                "answer":1,
                "explanation":f"{topic} is an important concept in graph-based knowledge representation."
            })

        st.session_state.question_bank = QUESTION_BANK
        st.session_state.assignment_bank_loaded = True

    QUESTION_BANK = st.session_state.question_bank

    # ----------------------------------------------------------
    # GENERATE RANDOM PAPER
    # ----------------------------------------------------------

    if "assignment_questions" not in st.session_state or len(st.session_state.assignment_questions)==0:

        st.session_state.assignment_questions = random.sample(QUESTION_BANK,10)

    if "assignment_answers" not in st.session_state:
        st.session_state.assignment_answers = {}

    if "assignment_submitted" not in st.session_state:
        st.session_state.assignment_submitted = False

    if "current_question" not in st.session_state:
        st.session_state.current_question = 0

    # ----------------------------------------------------------
    # REAL COUNTDOWN TIMER (20 Minutes)
    # ----------------------------------------------------------

    if "quiz_start_time" not in st.session_state:
        st.session_state.quiz_start_time = datetime.now()

    remaining = timedelta(minutes=20) - (
        datetime.now() - st.session_state.quiz_start_time
    )

    seconds_left = max(0, int(remaining.total_seconds()))

    minutes = seconds_left // 60
    seconds = seconds_left % 60

    if seconds_left <= 120:
        st.error(f"⏰ Time Remaining: {minutes:02}:{seconds:02}")
    else:
        st.info(f"⏰ Time Remaining: {minutes:02}:{seconds:02}")

    progress = (st.session_state.current_question + 1) / 10
    st.progress(progress)
    st.caption(f"Question {st.session_state.current_question+1} of 10")

    # Auto submit
    if seconds_left == 0 and not st.session_state.assignment_submitted:
        st.session_state.assignment_submitted = True
        st.warning("Time is over. Assignment submitted automatically.")
        st.rerun()
    # ----------------------------------------------------------
    # QUESTION CARD
    # ----------------------------------------------------------
    # Get the current question from the random question paper
    question = st.session_state.assignment_questions[
        st.session_state.current_question
    ]

    st.markdown(f"""
    <div class="question-box">
        <h3>Question {st.session_state.current_question+1}</h3>
        <p style="font-size:22px;">
        {question["question"]}
        </p>
    </div>
    """,unsafe_allow_html=True)

    previous_answer = st.session_state.assignment_answers.get(
        st.session_state.current_question,
        None
    )

    selected = st.radio(
        "Choose your answer",
        question["options"],
        index=previous_answer if previous_answer is not None else None,
        key=f"q_{st.session_state.current_question}"
    )

    if selected is not None:
        st.session_state.assignment_answers[
            st.session_state.current_question
        ] = question["options"].index(selected)

    # ----------------------------------------------------------
    # NAVIGATION
    # ----------------------------------------------------------

    col1,col2,col3 = st.columns([1,1,2])

    with col1:

        if st.button("⬅ Previous"):

            st.session_state.current_question = max(
                0,
                st.session_state.current_question-1
            )
            st.rerun()

    with col2:

        if st.button("Next ➡"):

            st.session_state.current_question = min(
                9,
                st.session_state.current_question+1
            )
            st.rerun()

    st.divider()

    # ----------------------------------------------------------
    # SUBMIT
    # ----------------------------------------------------------

    if st.button("✅ Submit Assignment", type="primary"):

        st.session_state.assignment_submitted=True

        score=0

        results=[]

        for i,q in enumerate(st.session_state.assignment_questions):

            student = st.session_state.assignment_answers.get(i,-1)

            correct = q["answer"]

            if student == correct:
                score += 1

            results.append({
                "Question":q["question"],
                "Your Answer": q["options"][student] if student!=-1 else "Not Answered",
                "Correct Answer": q["options"][correct],
                "Result":"✅ Correct" if student==correct else "❌ Incorrect",
                "Explanation":q["explanation"]
            })

        st.session_state.assignment_score=score
        st.session_state.assignment_results=results

        st.rerun()

    # ----------------------------------------------------------
    # RESULTS
    # ----------------------------------------------------------

    if st.session_state.assignment_submitted:

        score = st.session_state.assignment_score

        percentage = score*10

        st.markdown("## 🎉 Assignment Results")

        c1,c2,c3 = st.columns(3)

        c1.metric("Score",f"{score}/10")
        c2.metric("Percentage",f"{percentage}%")

        if percentage >= 80:
            grade="A"
        elif percentage >= 60:
            grade="B"
        elif percentage >= 40:
            grade="C"
        else:
            grade="D"

        c3.metric("Grade",grade)

        if percentage>=80:
            st.success("Excellent understanding of Knowledge Graph concepts.")
        elif percentage>=60:
            st.info("Good understanding. Revise a few concepts.")
        else:
            st.warning("Review Theory and Simulation modules before retrying.")

        st.divider()

        st.markdown("## 📑 Detailed Answer Sheet")

        for i,row in enumerate(st.session_state.assignment_results,start=1):

            with st.expander(f"Question {i}"):

                st.write("**Question:**",row["Question"])
                st.write("**Your Answer:**",row["Your Answer"])
                st.write("**Correct Answer:**",row["Correct Answer"])
                st.write("**Explanation:**",row["Explanation"])

        st.divider()

        if st.button("🔄 Generate New Assignment"):

            st.session_state.assignment_questions=random.sample(
                QUESTION_BANK,10
            )

            st.session_state.assignment_answers={}
            st.session_state.assignment_submitted=False
            st.session_state.assignment_score=None
            st.session_state.current_question=0
            st.session_state.quiz_start_time = datetime.now()

            st.rerun()

        # CSV Result Download
        results_df = pd.DataFrame(st.session_state.assignment_results)

        st.download_button(
            "📥 Download Assignment Results",
            results_df.to_csv(index=False),
            file_name="assignment_results.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==============================================================
# REFERENCES MODULE
# ==============================================================

if menu == "📚 References":

    st.markdown('<div class="section">References</div>', unsafe_allow_html=True)

    st.markdown("## 📖 Recommended Books")

    books = pd.DataFrame({
        "Book":[
            "Knowledge Graphs",
            "Graph Databases",
            "Learning SPARQL",
            "Semantic Web for the Working Ontologist",
            "Neo4j Graph Data Science"
        ],
        "Author":[
            "Aidan Hogan et al.",
            "Ian Robinson et al.",
            "Bob DuCharme",
            "Dean Allemang",
            "Amy Hodler"
        ]
    })

    st.dataframe(books, use_container_width=True)

    st.markdown("## 📚 IIT Virtual Lab Resources")

    st.markdown("""
    - Neo4j GraphAcademy
    - W3C RDF 1.1 Specification
    - W3C SPARQL Query Language
    - DBpedia Knowledge Graph
    - Wikidata Knowledge Base
    - NetworkX Documentation
    """)

    st.markdown("## 🎥 Video References")

    videos = pd.DataFrame({
        "Topic":[
            "Knowledge Graph Introduction",
            "Cypher Tutorial",
            "RDF & SPARQL",
            "Semantic Web Basics"
        ],
        "Platform":[
            "YouTube",
            "Neo4j GraphAcademy",
            "W3C",
            "Coursera"
        ]
    })

    st.dataframe(videos, use_container_width=True)

    st.success("References loaded successfully.")

# ==============================================================
# REPORT GENERATION MODULE
# ==============================================================

elif menu == "📄 Report Generation":

    st.markdown('<div class="section">Report Generation</div>', unsafe_allow_html=True)

    st.write("""
    Generate a professional IIT Virtual Lab style experiment report
    based on your uploaded Knowledge Graph and assignment results.
    """)

    if not st.session_state.graph_generated:

        st.warning("Please complete the Simulation first.")

    else:

        G = st.session_state.graph

        stats = st.session_state.graph_stats

        st.markdown("## Student Details")

        c1,c2 = st.columns(2)

        with c1:
            name = st.text_input("Student Name", value=st.session_state.student_name)

            roll = st.text_input("Roll Number", value=st.session_state.student_roll)

        with c2:
            division = st.text_input("Division", value=st.session_state.student_division)

            batch = st.text_input("Batch", value=st.session_state.student_batch)

        st.divider()

        st.markdown("## Report Preview")

        st.markdown(f"""
### Knowledge Graph Virtual Laboratory

**Experiment:** Design and Explore Dynamic Knowledge Graphs

**Student:** {name}

**Roll Number:** {roll}

**Division:** {division}

**Batch:** {batch}

**Date:** {datetime.now().strftime("%d-%m-%Y")}
""")

        st.markdown("### Graph Summary")

        summary = pd.DataFrame({
            "Metric":[
                "Total Nodes",
                "Relationships",
                "Labels",
                "Relationship Types",
                "Density",
                "Average Degree",
                "Connected Components"
            ],
            "Value":[
                stats["nodes"],
                stats["edges"],
                stats["labels"],
                stats["relationship_types"],
                stats["density"],
                stats["average_degree"],
                stats["connected_components"]
            ]
        })

        st.dataframe(summary, use_container_width=True)

        st.markdown("### Assignment Performance")

        if st.session_state.assignment_score is not None:

            score = st.session_state.assignment_score

            percentage = score*10

            st.success(f"Assignment Score : {score}/10 ({percentage}%)")

        else:

            st.info("Assignment not attempted.")

        st.divider()

        st.markdown("### 📈 Assignment Performance Dashboard")

        if st.session_state.assignment_score is not None:

            score_chart = px.bar(
                x=["Assignment Score"],
                y=[percentage],
                text=[f"{percentage}%"],
                title="Assignment Performance"
            )

            score_chart.update_layout(
                yaxis_range=[0,100],
                paper_bgcolor="#071019",
                plot_bgcolor="#071019",
                font=dict(color="white")
            )

            st.plotly_chart(score_chart, use_container_width=True)

        # ------------------------------------------------------
        # PDF GENERATOR
        # ------------------------------------------------------

        # ------------------------------------------------------
        # CAPTURE GRAPH IMAGE
        # ------------------------------------------------------

        if st.button("📸 Capture Current Graph Snapshot"):

            fig = draw_graph()

            image = pio.to_image(fig, format="png")

            st.session_state.graph_image = image

            st.success("Graph snapshot saved for report.")

        if st.button("📄 Generate PDF Report", type="primary"):

            pdf = FPDF()

            pdf.set_auto_page_break(auto=True, margin=15)

            pdf.add_page()

            pdf.set_font("Arial","B",18)

            pdf.cell(0,10,"Knowledge Graph Virtual Laboratory", ln=True)

            pdf.set_font("Arial","",13)

            pdf.cell(0,10,"IIT Virtual Labs Style Experiment Report", ln=True)

            pdf.ln(5)

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Student Information", ln=True)

            pdf.set_font("Arial","",12)

            pdf.multi_cell(0,8,f"""
            Student Name : {name}
            Roll Number : {roll}
            Division : {division}
            Batch : {batch}
            Date : {datetime.now().strftime("%d-%m-%Y")}
            """)

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Experiment Metadata", ln=True)

            pdf.set_font("Arial","",12)

            pdf.multi_cell(0,8,f"""
            Subject : Knowledge Graphs & Information Retrieval Systems

            Experiment Number : KG-09

            Virtual Laboratory : IIT Virtual Labs Style

            Software Used :
            • Python
            • Streamlit
            • NetworkX
            • Plotly
            • Pandas
            """)

            # Aim

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Aim", ln=True)

            pdf.set_font("Arial","",12)

            pdf.multi_cell(0,8,
                "To design, build and explore a dynamic Knowledge Graph using entities, properties and semantic relationships."
            )

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Real-World Applications", ln=True)

            pdf.set_font("Arial","",12)

            applications = [
                "Google Knowledge Graph for semantic search.",
                "Fraud Detection in banking networks.",
                "Recommendation Systems (Netflix, Amazon, Spotify).",
                "Healthcare Knowledge Graphs for disease relationships.",
                "Cybersecurity Attack Graph Analysis."
            ]

            for app in applications:
                pdf.multi_cell(0,8,f"• {app}")

            # Theory

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Theory Summary", ln=True)

            pdf.set_font("Arial","",12)

            pdf.multi_cell(
                0,
                8,
                "Knowledge Graphs represent entities as nodes and semantic relationships as edges. "
                "The experiment demonstrates schema design, dataset validation, graph traversal and analytics."
            )

            # Statistics

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Graph Statistics", ln=True)
            if "graph_image" in st.session_state:

                with open("graph_snapshot.png","wb") as img:
                    img.write(st.session_state.graph_image)

                pdf.image("graph_snapshot.png", w=175)

                pdf.ln(5)

            pdf.set_font("Arial","",12)

            for _,row in summary.iterrows():

                pdf.cell(
                    0,
                    8,
                    f"{row['Metric']} : {row['Value']}",
                    ln=True
                )

            pdf.ln(5)

            # Node Labels

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Node Labels", ln=True)

            labels = (
                st.session_state.uploaded_nodes["Label"]
                .value_counts()
            )

            pdf.set_font("Arial","",12)

            for label,count in labels.items():

                pdf.cell(0,8,f"{label} : {count}", ln=True)

            pdf.ln(5)

            # Relationships

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Relationship Types", ln=True)

            relationships = (
                st.session_state.uploaded_relationships["Relationship"]
                .value_counts()
            )

            pdf.set_font("Arial","",12)

            for rel,count in relationships.items():

                pdf.cell(0,8,f"{rel} : {count}", ln=True)

            pdf.ln(5)

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Schema Summary", ln=True)

            pdf.set_font("Arial","",12)

            for label in labels.index:
                pdf.cell(0,8,f"Entity Label: {label}", ln=True)

            pdf.ln(3)

            for rel in relationships.index:
                pdf.cell(0,8,f"Relationship Type: {rel}", ln=True)

            # Observations

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Observations", ln=True)

            pdf.set_font("Arial","",12)

            pdf.multi_cell(
                0,
                8,
                f"""
1. Graph contains {stats['nodes']} entities.

2. Graph contains {stats['edges']} semantic relationships.

3. Graph density is {stats['density']}.

4. Average degree is {stats['average_degree']}.

5. Graph contains {stats['connected_components']} connected component(s).
"""
            )

            # Assignment

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Assignment Result", ln=True)

            pdf.set_font("Arial","",12)

            if st.session_state.assignment_score is not None:

                pdf.cell(
                    0,
                    8,
                    f"Score : {st.session_state.assignment_score}/10",
                    ln=True
                )

            else:

                pdf.cell(
                    0,
                    8,
                    "Assignment Not Attempted",
                    ln=True
                )

            pdf.ln(5)

            # Conclusion

            pdf.set_font("Arial","B",14)
            pdf.cell(0,10,"Conclusion", ln=True)

            pdf.set_font("Arial","",12)

            pdf.multi_cell(
                0,
                8,
                "The experiment successfully demonstrates dynamic schema creation, "
                "dataset validation, graph generation, graph traversal and graph analytics "
                "using Knowledge Graph concepts."
            )

            filename = "Knowledge_Graph_VLab_Report.pdf"

            pdf.output(filename)

            with open(filename,"rb") as f:

                st.download_button(
                    "⬇ Download Experiment Report",
                    f,
                    filename,
                    "application/pdf",
                    use_container_width=True
                )

            st.success("PDF generated successfully.")

            if (
                st.session_state.assignment_score is not None
                and st.session_state.assignment_score >= 6
            ):

                st.markdown("---")

                st.markdown("""
                <div style="
                    background:#0F172A;
                    padding:35px;
                    border-radius:20px;
                    border:4px solid gold;
                    text-align:center;
                ">

                <h1 style="color:#FACC15;">🏆 Virtual Lab Completion Certificate</h1>

                <h3 style="color:white;">Knowledge Graph Virtual Laboratory</h3>

                <p style="font-size:20px;color:#CBD5E1;">
                This certifies that the student has successfully completed
                the Knowledge Graph Virtual Laboratory experiment.
                </p>

                </div>
                """, unsafe_allow_html=True)
