# ==============================================================
# KNOWLEDGE GRAPH VIRTUAL LAB V2.1
# Virtual Labs Inspired Edition — light theme, query explorer
# ==============================================================

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime
import plotly.io as pio
from fpdf import FPDF

import random
import json
import time

import streamlit.components.v1 as components

# --------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------

st.set_page_config(
    page_title="Knowledge Graph Virtual Laboratory",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------------------
# GLOBAL SESSION STATE
# --------------------------------------------------------------

def initialize_state():

    defaults = {

        "student_name": "",
        "student_roll": "",
        "student_division": "",
        "student_batch": "",

        "schema_nodes": [],
        "schema_relationships": [],

        "uploaded_nodes": pd.DataFrame(),
        "uploaded_relationships": pd.DataFrame(),

        "graph": nx.DiGraph(),
        "graph_generated": False,

        "pretest_bank_loaded": False,
        "pretest_questions": [],
        "pretest_answers": {},
        "pretest_submitted": False,
        "pretest_score": None,

        "posttest_bank_loaded": False,
        "posttest_questions": [],
        "posttest_answers": {},
        "posttest_submitted": False,
        "posttest_score": None,

        "query_step": 0,
        "query_history": [],

        "graph_stats": {}
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_state()

# --------------------------------------------------------------
# COLOR PALETTE (node colors on the graph canvas)
# --------------------------------------------------------------

NODE_COLORS = {
    "Disaster": "#EF4444",
    "Location": "#43A047",
    "Hazard": "#F59E0B",
    "Agency": "#8B5CF6",
    "Shelter": "#06B6D4",
    "Person": "#3B82F6",
    "Organization": "#EC4899",
    "Event": "#F97316",
    "City": "#14B8A6",
    "Disease": "#DC2626",
    "Medicine": "#0EA5E9",
    "Doctor": "#8B5CF6",
    "Patient": "#10B981"
}

DEFAULT_NODE_COLOR = "#38BDF8"

# Consistent dark text color used everywhere instead of "white"
TEXT_DARK = "#1F2937"
BLUE = "#2B8FC8"
BLUE_DARK = "#2D5D88"
ORANGE = "#FF6600"
GREEN = "#2E9B4F"

# --------------------------------------------------------------
# VIRTUAL LAB UI THEME  (matches the reference screenshot)
# --------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

:root{
    --vlab-blue:#2B8FC8;
    --vlab-blue-dark:#2D5D88;
    --vlab-orange:#FF6600;
    --vlab-green:#2E9B4F;
}

*{box-sizing:border-box;}
html,body,[class*="css"]{
    font-family:'Roboto',Arial,sans-serif!important;
    color:#1F2937!important;
}

/* FORCE LIGHT THEME EVERYWHERE */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stSidebar"], section, main, div[data-baseweb="popover"], div[data-baseweb="menu"]{
    background-color:#FFFFFF!important;
    color:#1F2937!important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"], [role="option"]{
    background:#FFFFFF!important;
    color:#222222!important;
}
[data-testid="stCodeBlock"]{background:#F7F7F7!important;}
code{background:#F5F5F5!important;color:#333!important;}

body,.stApp{margin:0!important;background:#fff!important;}
header[data-testid="stHeader"]{display:none!important;}
#MainMenu,footer{display:none!important;visibility:hidden!important;}

.block-container{
    max-width:none!important;
    width:100%!important;
    padding:0!important;
    margin:0!important;
}
div[data-testid="stAppViewContainer"]{background:#fff!important;}
div[data-testid="stAppViewContainer"] > section{padding:0!important;}

/* HEADER */
.vlab-header{
    height:100px;
    width:100%;
    background:#fff;
    display:flex;
    align-items:center;
    border-bottom:6px solid var(--vlab-orange);
    padding:0 28px;
    gap:22px;
}
.vlab-menu-box{
    width:44px;height:44px;flex:0 0 44px;
    border:1px solid #E3E3E3;border-radius:8px;
    display:flex;align-items:center;justify-content:center;
}
.vlab-hamburger{width:22px;height:16px;position:relative;}
.vlab-hamburger span{
    position:absolute;left:0;width:22px;height:2px;
    background:#777;border-radius:2px;
}
.vlab-hamburger span:nth-child(1){top:0;}
.vlab-hamburger span:nth-child(2){top:7px;}
.vlab-hamburger span:nth-child(3){top:14px;}

.vlab-logo{display:flex;align-items:center;gap:10px;}
.vlab-logo-icon{font-size:34px;line-height:1;}
.vlab-logo-text{display:flex;flex-direction:column;line-height:1.05;}
.vlab-logo-text .l1{font-size:23px;font-weight:700;color:var(--vlab-blue);}
.vlab-logo-text .l2{font-size:23px;font-weight:700;color:var(--vlab-green);margin-top:-4px;}
.vlab-logo-text .l3{font-size:11px;color:#8A8A8A;margin-top:2px;}

.vlab-header-right{
    margin-left:auto;height:100%;
    display:flex;align-items:center;gap:14px;
}
.vlab-rating{
    color:#FFC400;font-size:22px;letter-spacing:-2px;
    white-space:nowrap;margin-right:12px;line-height:1;
}
.vlab-rate,.vlab-bug{
    height:42px;padding:0 22px;border:0;border-radius:16px;
    background:var(--vlab-blue);color:#fff;font-family:Roboto,Arial,sans-serif;
    font-size:14px;font-weight:500;display:flex;align-items:center;
    justify-content:center;white-space:nowrap;
}

/* BREADCRUMB */
.vlab-breadcrumb{
    padding:22px 28px 22px;background:#fff;
    color:#2B86C3;font-size:22px;font-weight:400;line-height:1.3;
}
.vlab-breadcrumb .chevron{
    display:inline-block;margin:0 8px;font-size:26px;
    line-height:0;vertical-align:-3px;font-weight:300;color:#9DB8C9;
}

/* MAIN TWO-COLUMN LAYOUT */
div[data-testid="stHorizontalBlock"]:first-of-type{
    width:100%!important;
    gap:0!important;
    align-items:stretch!important;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div:first-child{
    border-right:1px solid #E7E7E7!important;
    min-height:650px!important;
    padding:18px 0 40px 0!important;
    background:#FBFDFE!important;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(2){
    padding:28px 52px 60px 52px!important;
    max-width:1180px!important;
}

/* LEFT NAV */
.vlab-left-nav div[data-testid="stRadio"] > label{display:none!important;}
.vlab-left-nav div[data-testid="stRadio"] > div{
    display:flex!important;flex-direction:column!important;
    gap:2px!important;width:100%!important;
}
.vlab-left-nav div[data-testid="stRadio"] > div > label{
    width:100%!important;min-height:44px!important;
    padding:10px 0 10px 28px!important;margin:0!important;
    border:0!important;border-radius:0!important;
    background:transparent!important;color:var(--vlab-blue-dark)!important;
    font-size:17px!important;font-weight:500!important;
    line-height:24px!important;cursor:pointer!important;
}
.vlab-left-nav div[data-testid="stRadio"] > div > label:hover{
    color:var(--vlab-orange)!important;
}
.vlab-left-nav div[data-testid="stRadio"] > div > label:has(input:checked){
    color:var(--vlab-orange)!important;font-weight:600!important;
    border-left:4px solid var(--vlab-orange)!important;
    padding-left:24px!important;
    background:#FFF6EF!important;
}
.vlab-left-nav input[type="radio"]{display:none!important;}

/* EXPERIMENT TITLE */
.vlab-experiment-title{
    text-align:center;color:var(--vlab-blue);font-size:28px;
    line-height:1.3;font-weight:500;margin:0 0 22px 0;
    padding:0 0 18px;border-bottom:1px solid #E6E6E6;
}

/* CONTENT */
.section{
    color:var(--vlab-blue)!important;font-size:26px!important;
    line-height:1.25!important;font-weight:500!important;
    margin:36px 0 16px!important;padding:0 0 10px!important;
    border-bottom:1px solid #E6E6E6!important;
}
.subsection{
    color:var(--vlab-blue)!important;font-size:22px!important;
    font-weight:500!important;margin:22px 0 10px!important;
}
.bodytext,.step-body{
    color:#1F2937!important;font-size:16px!important;
    line-height:1.7!important;font-weight:400!important;
}
.card,.step-box,.question-box,.reference-box{
    background:#FAFCFE!important;border:1px solid #E9EEF2!important;
    border-radius:12px!important;box-shadow:none!important;
    padding:18px 20px!important;margin-bottom:16px!important;
}
.card h3,.step-title{
    color:var(--vlab-blue)!important;font-size:20px!important;
    font-weight:600!important;margin:0 0 8px!important;
}
.card p{color:#1F2937!important;font-size:16px!important;line-height:1.7!important;}
.icon-badge{font-size:26px;margin-right:8px;}

/* BUTTONS / INPUTS */
.stButton>button,.stDownloadButton>button{
    min-height:42px!important;border:0!important;border-radius:14px!important;
    background:var(--vlab-blue)!important;color:#fff!important;
    font-size:15px!important;font-weight:500!important;box-shadow:none!important;
}
.stButton>button:hover,.stDownloadButton>button:hover{
    background:#217EAE!important;color:#fff!important;
}
.stTextInput input,.stNumberInput input,.stTextArea textarea,
.stSelectbox div[data-baseweb="select"]>div,
.stMultiSelect div[data-baseweb="select"]>div{
    border:1px solid #D3D3D3!important;border-radius:8px!important;
    background:#fff!important;color:#222!important;font-size:15px!important;
}
label{font-size:14px!important;color:#333!important;}
.stRadio>div>label{font-size:15px!important;color:#333!important;}
.stFileUploader{border:1px dashed #CFCFCF!important;border-radius:10px!important;background:#FAFAFA!important;}
.stAlert{border-radius:10px!important;}
[data-testid="stExpander"]{border:1px solid #E3E3E3!important;border-radius:10px!important;box-shadow:none!important;margin-bottom:14px!important;}
hr{border-color:#E5E5E5!important;margin:26px 0!important;}

/* Extra breathing room between Streamlit columns / widgets */
div[data-testid="stHorizontalBlock"]{gap:12px!important;}
div[data-testid="column"]{padding:2px!important;}
div[data-testid="stVerticalBlock"]{gap:0.45rem!important;}

/* COMPACT SIMULATION LAYOUT */
.stApp:has(.simulation-page-marker) div[data-testid="stHorizontalBlock"]{gap:10px!important;}
.stApp:has(.simulation-page-marker) div[data-testid="column"]{padding:1px!important;}
.stApp:has(.simulation-page-marker) div[data-testid="stVerticalBlock"]{gap:0.28rem!important;}
.stApp:has(.simulation-page-marker) .subsection{
    margin:16px 0 6px!important;
    padding-bottom:5px!important;
    font-size:20px!important;
}
.stApp:has(.simulation-page-marker) .bodytext{line-height:1.5!important;}
.stApp:has(.simulation-page-marker) hr{margin:10px 0!important;}
.stApp:has(.simulation-page-marker) .stButton>button{min-height:38px!important;}
.stApp:has(.simulation-page-marker) [data-testid="stExpander"]{margin-bottom:6px!important;}

.metric-card{
    background:#FAFCFE!important;border:1px solid #E3E3E3!important;
    border-radius:12px!important;padding:16px!important;text-align:center;
}
.metric-number{font-size:26px!important;color:var(--vlab-blue)!important;font-weight:600!important;}
.metric-label{font-size:13px!important;color:#555!important;margin-top:4px;}
thead tr th{background:#F3F3F3!important;color:#333!important;font-size:13px!important;}
tbody tr td{font-size:13px!important;color:#222!important;}

/* REAL-WORLD APPLICATION IMAGE CARDS */
.real-world-card{
    background:#FFFFFF!important;
    border:1px solid #E3E9EE!important;
    border-radius:10px!important;
    overflow:hidden!important;
    margin-bottom:12px!important;
}
.real-world-card img{
    display:block!important;
    width:100%!important;
    height:150px!important;
    object-fit:cover!important;
}
.real-world-card-body{padding:12px 14px!important;}
.real-world-card h3{
    color:var(--vlab-blue)!important;
    font-size:18px!important;
    font-weight:600!important;
    margin:0 0 5px!important;
}
.real-world-card p{
    color:#333!important;
    font-size:14px!important;
    line-height:1.5!important;
    margin:0!important;
}

/* FOOTER */
.vlab-footer{
    margin:50px 0 0;padding:22px 28px;background:#F7F9FB;
    border-top:1px solid #E3E3E3;color:#666;font-size:12px;line-height:1.8;
}

@media(max-width:900px){
    .vlab-header{padding:0 14px;}
    .vlab-rating{display:none;}
    .vlab-rate,.vlab-bug{font-size:13px;padding:0 13px;height:38px;}
    .vlab-breadcrumb{font-size:18px;padding:16px 14px;}
    div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(2){padding:18px 20px 50px!important;}
    .vlab-left-nav div[data-testid="stRadio"] > div > label{font-size:16px!important;padding-left:20px!important;}
    .vlab-experiment-title{font-size:22px;}
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# VIRTUAL LAB HEADER (no external images — CSS/emoji logo only)
# --------------------------------------------------------------

st.markdown("""
<div class="vlab-header">
    <div class="vlab-menu-box">
        <div class="vlab-hamburger"><span></span><span></span><span></span></div>
    </div>
    <div class="vlab-logo">
        <div class="vlab-logo-icon">🧪</div>
        <div class="vlab-logo-text">
            <div class="l1">Virtual</div>
            <div class="l2">Labs</div>
            <div class="l3">An MoE Govt of India Initiative</div>
        </div>
    </div>
    <div class="vlab-header-right">
        <div class="vlab-rating" aria-label="rating">★★★★☆</div>
        <div class="vlab-rate">Rate Me</div>
        <div class="vlab-bug">Report a Bug</div>
    </div>
</div>
<div class="vlab-breadcrumb">
    Computer Engineering
    <span class="chevron">›</span>
    Knowledge Graph &amp; Information Retrieval Systems
    <span class="chevron">›</span>
    Experiments
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# LEFT NAVIGATION + CONTENT COLUMN
# --------------------------------------------------------------

nav_col, content_col = st.columns([1.05, 6.95], gap="small")

with nav_col:
    st.markdown('<div class="vlab-left-nav">', unsafe_allow_html=True)
    nav_menu = st.radio(
        "Experiment Navigation",
        ["Aim", "Theory", "Pretest", "Procedure", "Simulation", "Posttest",
         "References", "Contributors", "Feedback"],
        label_visibility="collapsed",
        key="vlab_navigation"
    )
    st.markdown('</div>', unsafe_allow_html=True)

if "active_vlab_page" not in st.session_state:
    st.session_state.active_vlab_page = nav_menu
if "last_vlab_nav" not in st.session_state:
    st.session_state.last_vlab_nav = nav_menu
if nav_menu != st.session_state.last_vlab_nav:
    st.session_state.active_vlab_page = nav_menu
    st.session_state.last_vlab_nav = nav_menu

menu = st.session_state.active_vlab_page

with content_col:
    st.markdown("""
    <div class="vlab-experiment-title">
        Design, Build and Explore Dynamic Knowledge Graphs
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------------
    # HELPER FUNCTIONS
    # ------------------------------------------------------------

    def metric_cards(nodes, edges, labels, relations):

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f'''
            <div class="metric-card">
            <div class="metric-number">{nodes}</div>
            <div class="metric-label">Nodes</div>
            </div>
            ''', unsafe_allow_html=True)

        with c2:
            st.markdown(f'''
            <div class="metric-card">
            <div class="metric-number">{edges}</div>
            <div class="metric-label">Relationships</div>
            </div>
            ''', unsafe_allow_html=True)

        with c3:
            st.markdown(f'''
            <div class="metric-card">
            <div class="metric-number">{labels}</div>
            <div class="metric-label">Labels</div>
            </div>
            ''', unsafe_allow_html=True)

        with c4:
            st.markdown(f'''
            <div class="metric-card">
            <div class="metric-number">{relations}</div>
            <div class="metric-label">Relationship Types</div>
            </div>
            ''', unsafe_allow_html=True)

    def make_card(title, text, icon=""):

        icon_html = f'<span class="icon-badge">{icon}</span>' if icon else ""

        st.markdown(f"""
    <div class="card">
    <h3>{icon_html}{title}</h3>
    <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)

    def make_image_card(title, text, image_url):
        st.markdown(f"""
        <div class="real-world-card">
            <img src="{image_url}" alt="{title}" loading="lazy">
            <div class="real-world-card-body">
                <h3>{title}</h3>
                <p>{text}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


    def clean_layout(fig, height=600, title=None):
        """Apply one consistent, light layout to every plotly figure."""
        layout_kwargs = dict(
            height=height,
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color=TEXT_DARK, size=13),
            margin=dict(l=20, r=20, t=50 if title else 20, b=20),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        if title:
            layout_kwargs["title"] = dict(text=title, font=dict(size=20, color=BLUE))
        fig.update_layout(**layout_kwargs)
        return fig

    # ------------------------------------------------------------
    # GRAPH HELPERS
    # ------------------------------------------------------------

    def build_networkx_graph(nodes_df, rel_df):

        G = nx.DiGraph()

        if nodes_df.empty:
            return G

        for _, row in nodes_df.iterrows():
            attrs = row.to_dict()
            node_id = attrs["ID"]
            G.add_node(node_id, **attrs)

        if not rel_df.empty:
            for _, row in rel_df.iterrows():
                G.add_edge(row["Source"], row["Target"], relationship=row["Relationship"])

        return G

    def draw_graph(highlight_nodes=None, highlight_edges=None, active_edge=None):

        if highlight_nodes is None:
            highlight_nodes = []
        if highlight_edges is None:
            highlight_edges = []

        G = st.session_state.graph

        if len(G.nodes) == 0:
            fig = go.Figure()
            fig.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[dict(
                    text="No graph generated yet.",
                    showarrow=False,
                    font=dict(size=20, color=TEXT_DARK)
                )]
            )
            return fig

        pos = nx.spring_layout(G, seed=18)

        fig = go.Figure()

        # ---------------- EDGES ----------------
        for edge in G.edges():

            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            is_active = (edge == active_edge)
            is_highlighted = edge in highlight_edges

            if is_active:
                color, width = ORANGE, 8
            elif is_highlighted:
                color, width = "#43A047", 5
            else:
                color, width = "#B9CBD6", 2

            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode="lines",
                line=dict(color=color, width=width),
                hoverinfo="none",
                showlegend=False
            ))

            fig.add_annotation(
                x=(x0 + x1) / 2, y=(y0 + y1) / 2,
                text=G.edges[edge]["relationship"],
                showarrow=False,
                font=dict(size=12, color=BLUE_DARK if not is_active else ORANGE)
            )

        # ---------------- NODES ----------------
        node_x, node_y, colors, sizes, labels = [], [], [], [], []
        current = highlight_nodes[-1] if highlight_nodes else None

        for node, data in G.nodes(data=True):

            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            labels.append(data["Name"])

            if node == current:
                colors.append(BLUE)
                sizes.append(38)
            elif node in highlight_nodes:
                colors.append("#43A047")
                sizes.append(32)
            else:
                colors.append(NODE_COLORS.get(data["Label"], DEFAULT_NODE_COLOR))
                sizes.append(24)

        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            textfont=dict(color=TEXT_DARK, size=12),
            marker=dict(color=colors, size=sizes, line=dict(color="white", width=2)),
            hovertemplate="<b>%{text}</b><extra></extra>"
        ))

        clean_layout(fig, height=500, title="Interactive Knowledge Graph")

        return fig

    # ------------------------------------------------------------
    # AIM PAGE
    # ------------------------------------------------------------

    if menu == "Aim":

        st.markdown('<div class="section">Objective</div>', unsafe_allow_html=True)

        st.markdown("""
    <div class="bodytext">
    The objective of this experiment is to design a domain-specific Knowledge Graph schema,
    define entities, properties and semantic relationships, import structured datasets,
    generate an interactive graph representation, and explore graph queries
    used in real-world knowledge graph systems.
    </div>
    """, unsafe_allow_html=True)

        st.markdown('<div class="subsection">Learning Objectives</div>', unsafe_allow_html=True)

        objectives = [
            ("🎯", "Understand the concept of Knowledge Graphs."),
            ("🏷️", "Identify entities, node labels and properties."),
            ("🔗", "Design relationships between entities."),
            ("🧩", "Create dynamic graph schemas."),
            ("📥", "Import datasets into graph structure."),
            ("🔍", "Run queries and explore graph connections."),
            ("🕸️", "Visualize connected knowledge interactively."),
            ("📊", "Generate graph analytics and reports."),
        ]

        for i, (icon, obj) in enumerate(objectives, 1):
            make_card(f"Objective {i}", obj, icon=icon)

        st.markdown('<div class="subsection">Expected Outcomes</div>', unsafe_allow_html=True)

        make_card(
            "After completing this experiment students will be able to:",
            "Create dynamic knowledge graphs from any structured dataset, "
            "understand semantic relationships, run queries visually, "
            "and analyze graph connectivity similar to Neo4j Knowledge Graph systems.",
            icon="✅"
        )

        st.markdown('<div class="section">Real World Applications</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="bodytext">Examples below use real photographs to visually connect '
            'Knowledge Graph concepts with their practical application areas.</div>',
            unsafe_allow_html=True
        )

        REAL_WORLD_IMAGES = {
            "Google Search Knowledge Graph":
                "https://images.unsplash.com/photo-1573804633927-bfcbcd909acd?auto=format&fit=crop&w=900&q=80",
            "Healthcare Knowledge Graph":
                "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=900&q=80",
            "E-Commerce Recommendation System":
                "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=900&q=80",
            "Fraud Detection":
                "https://images.unsplash.com/photo-1559526324-593bc073d938?auto=format&fit=crop&w=900&q=80",
            "Social Networks":
                "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=900&q=80",
            "Disaster Management":
                "https://images.unsplash.com/photo-1547683905-f686c993aae5?auto=format&fit=crop&w=900&q=80",
            "Cyber Security":
                "https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=900&q=80",
            "Education Knowledge Graph":
                "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=900&q=80"
        }

        col1, col2 = st.columns(2)

        with col1:
            make_image_card("Google Search Knowledge Graph",
                "Google connects people, places, movies, organizations and facts to support semantic search and entity understanding.",
                REAL_WORLD_IMAGES["Google Search Knowledge Graph"])
            make_image_card("Healthcare Knowledge Graph",
                "Patients, diseases, medicines, symptoms, hospitals and doctors can be connected to support clinical information systems.",
                REAL_WORLD_IMAGES["Healthcare Knowledge Graph"])
            make_image_card("E-Commerce Recommendation System",
                "Products, customers, categories and purchase history can be represented as connected entities for recommendation systems.",
                REAL_WORLD_IMAGES["E-Commerce Recommendation System"])
            make_image_card("Fraud Detection",
                "Accounts, transactions, devices, merchants and locations can be connected to identify suspicious relationship patterns.",
                REAL_WORLD_IMAGES["Fraud Detection"])

        with col2:
            make_image_card("Social Networks",
                "Users, friends, posts, interactions and communities form large connected graphs used for relationship analysis.",
                REAL_WORLD_IMAGES["Social Networks"])
            make_image_card("Disaster Management",
                "Disasters, affected locations, shelters, agencies, resources and response teams can be connected for emergency coordination.",
                REAL_WORLD_IMAGES["Disaster Management"])
            make_image_card("Cyber Security",
                "Devices, users, vulnerabilities, indicators and attack paths can be represented as graphs for threat analysis.",
                REAL_WORLD_IMAGES["Cyber Security"])
            make_image_card("Education Knowledge Graph",
                "Students, faculty, courses, departments and learning resources can be connected to support academic discovery.",
                REAL_WORLD_IMAGES["Education Knowledge Graph"])

    # ------------------------------------------------------------
    # THEORY PAGE
    # ------------------------------------------------------------

    elif menu == "Theory":

        st.markdown('<div class="section">Theory</div>', unsafe_allow_html=True)

        make_card("Knowledge Graph",
            "A Knowledge Graph is a graph-based representation of knowledge where entities are represented "
            "as nodes and semantic relationships are represented as edges. Unlike relational databases, "
            "knowledge graphs naturally capture interconnected information.", icon="🕸️")

        make_card("Entity",
            "An entity represents a real-world object or concept such as a Person, City, Disaster, "
            "Hospital, Organization or Product.", icon="🏷️")

        make_card("Node Labels",
            "Node labels classify entities into categories. Examples include Person, Disaster, "
            "Agency, Shelter, Disease, Doctor and Product.", icon="🔖")

        make_card("Properties",
            "Properties store descriptive attributes about nodes such as Name, Age, Severity, "
            "Location, Capacity and Status.", icon="📋")

        make_card("Relationships",
            "Relationships define semantic meaning between entities, for example "
            "Person – LIVES_IN – City, Disaster – OCCURS_IN – Location, "
            "Patient – HAS_DISEASE – Disease, Doctor – TREATS – Patient.", icon="🔗")

        make_card("Ontology",
            "Ontology defines the vocabulary, classes and semantic rules governing the knowledge graph.", icon="📚")

        make_card("RDF (Resource Description Framework)",
            "RDF stores knowledge using triples consisting of subject, predicate and object. "
            "It is the foundation of Semantic Web technologies.", icon="🧬")

        make_card("SPARQL",
            "SPARQL is the query language for RDF knowledge graphs. "
            "It retrieves entities and relationships similar to SQL for relational databases.", icon="❓")

        make_card("Neo4j Property Graph Model",
            "Neo4j stores nodes and relationships with properties. "
            "Relationships themselves can also contain properties.", icon="🗄️")

        # ---------------- VISUAL: Subject-Predicate-Object triple ----------------

        st.markdown('<div class="subsection">Visualizing a Knowledge Graph Triple</div>', unsafe_allow_html=True)

        triple_fig = go.Figure()

        triple_fig.add_trace(go.Scatter(
            x=[0, 1], y=[0.5, 0.5], mode="lines",
            line=dict(color=BLUE, width=4), hoverinfo="none", showlegend=False
        ))
        triple_fig.add_annotation(x=0.5, y=0.62, text="OCCURS_IN", showarrow=False,
                                   font=dict(size=15, color=BLUE_DARK))

        triple_fig.add_trace(go.Scatter(
            x=[0, 1], y=[0.5, 0.5], mode="markers+text",
            text=["Mumbai Flood", "Mumbai"],
            textposition="bottom center",
            textfont=dict(size=15, color=TEXT_DARK),
            marker=dict(size=42, color=[NODE_COLORS["Disaster"], NODE_COLORS["City"]],
                        line=dict(color="white", width=2)),
            hovertemplate="<b>%{text}</b><extra></extra>", showlegend=False
        ))

        triple_fig.update_layout(
            xaxis=dict(visible=False, range=[-0.3, 1.3]),
            yaxis=dict(visible=False, range=[0.2, 0.8]),
            height=220, paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            margin=dict(l=10, r=10, t=10, b=10)
        )

        st.plotly_chart(triple_fig, use_container_width=True, key="theory_triple_example")

        st.caption("Subject → Predicate → Object: every statement in a knowledge graph follows this pattern.")

        st.markdown('<div class="subsection">Property Graph vs RDF</div>', unsafe_allow_html=True)

        st.table(pd.DataFrame({
            "Property Graph": ["Neo4j", "Nodes with labels", "Relationships with properties",
                                "Cypher Query Language", "Highly interactive traversal"],
            "RDF": ["Semantic Web", "Resources", "Triples", "SPARQL", "Ontology driven"]
        }))

        st.markdown('<div class="subsection">Graph Traversal Concepts</div>', unsafe_allow_html=True)

        make_card(
            "Traversal Algorithms",
            "Traversal means visiting connected nodes through relationships. Common approaches include "
            "Breadth First Search (BFS), Depth First Search (DFS), Neighbor Expansion and Shortest Path search. "
            "The Simulation module lets you run each of these as a query and watch it animate hop by hop.",
            icon="🧭"
        )

        st.markdown('<div class="subsection">Recommended E-Books</div>', unsafe_allow_html=True)

        ebooks = pd.DataFrame({
            "Book": ["Knowledge Graphs - Aidan Hogan", "Graph Databases - O'Reilly", "Learning SPARQL",
                     "Semantic Web for the Working Ontologist", "Neo4j Graph Data Science"],
            "Purpose": ["Knowledge Graph fundamentals", "Neo4j implementation", "SPARQL queries",
                        "Ontology design", "Graph analytics"]
        })
        st.dataframe(ebooks, use_container_width=True)

        st.markdown('<div class="subsection">Research Papers</div>', unsafe_allow_html=True)

        papers = pd.DataFrame({
            "Paper": ["Google Knowledge Vault", "DBpedia Knowledge Graph", "Wikidata Architecture",
                      "Knowledge Graph Embeddings Survey", "Semantic Web Vision by Tim Berners-Lee"],
            "Area": ["Knowledge extraction", "Public Knowledge Graph", "Collaborative graph",
                     "Machine learning", "Semantic Web"]
        })
        st.dataframe(papers, use_container_width=True)

    # ------------------------------------------------------------
    # PRETEST PAGE — bank of 50, random 10, all on one page
    # ------------------------------------------------------------

    elif menu == "Pretest":

        st.markdown('<div class="section">Pretest</div>', unsafe_allow_html=True)
        st.markdown('<div class="bodytext">Answer the following questions to check your prior understanding '
                     'of Knowledge Graph concepts before performing the experiment.</div>', unsafe_allow_html=True)

        if not st.session_state.pretest_bank_loaded:

            PRETEST_BANK = [
                {"q": "Which structure is primarily used to represent entities and their relationships in a Knowledge Graph?",
                 "o": ["Table only", "Graph", "Spreadsheet only", "Image"], "a": 1},
                {"q": "In a property graph, what does a node normally represent?",
                 "o": ["An entity or concept", "Only a database table", "Only a query", "A file format"], "a": 0},
                {"q": "What represents the semantic connection between two nodes?",
                 "o": ["Relationship", "Column name", "File path", "Index"], "a": 0},
                {"q": "Which traversal explores connected nodes level by level?",
                 "o": ["DFS", "BFS", "Sorting", "Hashing"], "a": 1},
                {"q": "Which of the following is a common Knowledge Graph application?",
                 "o": ["Semantic search", "Text formatting", "Image compression", "Keyboard control"], "a": 0},
                {"q": "A Knowledge Graph triple is made up of:",
                 "o": ["Node, Edge, Weight", "Subject, Predicate, Object", "Row, Column, Cell", "Key, Value, Index"], "a": 1},
                {"q": "Which of these is an example of an entity, not a relationship?",
                 "o": ["LIVES_IN", "TREATS", "Mumbai", "OCCURS_IN"], "a": 2},
                {"q": "What do node labels do in a Knowledge Graph?",
                 "o": ["Classify entities into categories", "Store passwords", "Sort a spreadsheet", "Compress images"], "a": 0},
                {"q": "Properties in a graph typically store:",
                 "o": ["Descriptive attributes of a node", "The graph layout algorithm", "The database engine name", "Network latency"], "a": 0},
                {"q": "Which query language is closely associated with Neo4j?",
                 "o": ["SPARQL", "Cypher", "SQL", "GraphQL"], "a": 1},
            ]

            topics = ["Neo4j", "Cypher", "RDF", "Ontology", "SPARQL", "Graph Database",
                      "Knowledge Representation", "Node Labels", "Properties", "Relationships",
                      "Traversal", "Shortest Path", "Centrality", "Degree", "Connected Components",
                      "Semantic Web", "DBpedia", "Wikidata", "Google Knowledge Graph", "Healthcare KG",
                      "Fraud Detection", "Recommendation Systems", "Property Graph", "Schema Design",
                      "Graph Analytics", "NetworkX", "Graph Density", "Adjacency Matrix",
                      "Entity Resolution", "Graph Embeddings", "Semantic Search", "Triple Store",
                      "Directed Graph", "Undirected Graph", "Graph Query", "Node Degree",
                      "Weakly Connected Component", "Graph Visualization", "Data Import",
                      "Data Validation"]

            i = 0
            while len(PRETEST_BANK) < 50:
                topic = topics[i % len(topics)]
                PRETEST_BANK.append({
                    "q": f"Which statement is TRUE regarding {topic} in the context of Knowledge Graphs?",
                    "o": [f"{topic} is unrelated to Knowledge Graphs.",
                          f"{topic} is a concept used in Knowledge Graph systems.",
                          f"{topic} can only be used in spreadsheets.",
                          f"{topic} cannot represent entities or relationships."],
                    "a": 1
                })
                i += 1

            st.session_state.pretest_bank = PRETEST_BANK
            st.session_state.pretest_bank_loaded = True

        if len(st.session_state.pretest_questions) == 0:
            st.session_state.pretest_questions = random.sample(st.session_state.pretest_bank, 10)

        for i, q in enumerate(st.session_state.pretest_questions):
            st.markdown(f'<div class="question-box"><b>Question {i+1}</b><br>{q["q"]}</div>', unsafe_allow_html=True)
            prev = st.session_state.pretest_answers.get(i, None)
            answer = st.radio("Select one answer", q["o"], key=f"pretest_q_{i}",
                               index=prev if prev is not None else None)
            if answer is not None:
                st.session_state.pretest_answers[i] = q["o"].index(answer)

        if st.button("Submit Pretest", type="primary"):
            score = sum(st.session_state.pretest_answers.get(i, -1) == q["a"]
                        for i, q in enumerate(st.session_state.pretest_questions))
            st.session_state.pretest_score = score
            st.session_state.pretest_submitted = True
            st.rerun()

        if st.session_state.pretest_submitted:
            score = st.session_state.get("pretest_score", 0)
            st.success(f"Pretest completed. Score: {score}/{len(st.session_state.pretest_questions)}")

            if st.button("Generate New Pretest"):
                st.session_state.pretest_questions = random.sample(st.session_state.pretest_bank, 10)
                st.session_state.pretest_answers = {}
                st.session_state.pretest_submitted = False
                st.session_state.pretest_score = None
                st.rerun()

    # ------------------------------------------------------------
    # PROCEDURE PAGE
    # ------------------------------------------------------------

    elif menu == "Procedure":

        st.markdown('<div class="section">Procedure</div>', unsafe_allow_html=True)

        steps = [
            ("Step 1 - Define Knowledge Graph Schema",
             "Create node labels, properties and semantic relationship types for the selected domain."),
            ("Step 2 - Build Schema Visually",
             "Use the Schema Builder to add entities and connect labels through relationship types."),
            ("Step 3 - Upload Structured Dataset",
             "Upload Nodes CSV and Relationships CSV matching the designed schema."),
            ("Step 4 - Validate Dataset",
             "The simulator checks duplicate IDs, missing labels, invalid relationships and datatype errors."),
            ("Step 5 - Generate Knowledge Graph",
             "The simulator converts uploaded data into an interactive graph visualization."),
            ("Step 6 - Run Queries",
             "Choose a query type (neighbours, shortest path, outward exploration, deep chain) and run it."),
            ("Step 7 - Watch the Query Animate",
             "Nodes and relationships light up step-by-step showing exactly which hop and relation is used."),
            ("Step 8 - Analyze Graph Statistics",
             "Observe nodes, relationships, degree distribution and connectivity."),
            ("Step 9 - Record Observations",
             "Automatically generated observations summarize graph characteristics."),
            ("Step 10 - Generate Experiment Report",
             "Download a complete PDF report containing graph visualization and experiment summary.")
        ]

        for title, body in steps:
            st.markdown(f"""
    <div class="step-box">
    <div class="step-title">{title}</div>
    <div class="step-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)

        st.success("Proceed to the Simulation module to perform the experiment.")

    # ==============================================================
    # SIMULATION MODULE
    # ==============================================================

    elif menu == "Simulation":

        st.markdown('<div class="section">Simulation Laboratory</div>', unsafe_allow_html=True)
        st.markdown('<div class="simulation-page-marker"></div>', unsafe_allow_html=True)

        navc1, navc2 = st.columns(2)
        with navc1:
            if st.button("View Observations", use_container_width=True):
                st.session_state.active_vlab_page = "Observations"
                st.rerun()
        with navc2:
            if st.button("Open Report Generation", use_container_width=True):
                st.session_state.active_vlab_page = "Report Generation"
                st.rerun()

        st.markdown("""
        <div class="bodytext">
        Welcome to the interactive Knowledge Graph simulation. Design your own schema, upload datasets,
        generate an interactive graph, and run queries to see exactly how a knowledge graph is traversed.
        </div>
        """, unsafe_allow_html=True)

        steps_labels = ["1. Schema Builder", "2. Upload Dataset", "3. Validate Dataset",
                         "4. Generate Graph", "5. Run Queries"]

        cols = st.columns(len(steps_labels))
        for i, c in enumerate(cols):
            if i == 0:
                c.info(steps_labels[i])
            else:
                c.write(steps_labels[i])

        st.divider()

        # ==========================================================
        # SCHEMA BUILDER
        # ==========================================================

        st.markdown('<div class="subsection">Step 1 — Create Your Knowledge Graph Schema</div>', unsafe_allow_html=True)

        st.write("Define custom node labels, their properties, and semantic relationships. "
                 "This lab supports any domain such as Healthcare, Education, Disaster Management, "
                 "Social Networks, Banking, or E-Commerce.")

        st.markdown("#### Create Node Label")

        with st.expander("Add New Node Label", expanded=True):

            col1, col2 = st.columns(2)
            with col1:
                node_label = st.text_input("Node Label", placeholder="Example: Person")
            with col2:
                node_color = st.color_picker("Node Color", "#38BDF8")

            st.markdown("**Add Properties**")

            if "temp_properties" not in st.session_state:
                st.session_state.temp_properties = []

            p1, p2 = st.columns([4, 1])
            with p1:
                new_property = st.text_input("Property Name", placeholder="Example: Age")
            with p2:
                st.write("")
                st.write("")
                if st.button("Add Property", key="add_prop_btn"):
                    if new_property != "" and new_property not in st.session_state.temp_properties:
                        st.session_state.temp_properties.append(new_property)

            if st.session_state.temp_properties:
                st.markdown("**Current Properties**")
                remove_property = None
                for idx, prop in enumerate(st.session_state.temp_properties):
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        st.success(prop)
                    with c2:
                        if st.button("Remove", key=f"remove_prop_{idx}"):
                            remove_property = prop
                if remove_property:
                    st.session_state.temp_properties.remove(remove_property)
                    st.rerun()

            if st.button("Save Node Label", key="save_node"):
                if node_label == "":
                    st.error("Node label cannot be empty.")
                else:
                    exists = any(node["label"] == node_label for node in st.session_state.schema_nodes)
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

        st.markdown('<div class="subsection">Current Schema Nodes</div>', unsafe_allow_html=True)

        if len(st.session_state.schema_nodes) == 0:
            st.info("No node labels created yet.")
        else:
            delete_node = None
            for idx, node in enumerate(st.session_state.schema_nodes):
                with st.container():
                    st.markdown(f"""
                    <div style="background:#F5FAFD;border-left:6px solid {node['color']};
                        padding:16px 18px;border-radius:12px;margin-bottom:12px;">
                    <h4 style="color:{node['color']};margin:0 0 6px 0;">{node['label']}</h4>
                    <b style="color:#1F2937;">Properties</b>
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
                st.session_state.schema_nodes = [n for n in st.session_state.schema_nodes if n["label"] != delete_node]
                st.session_state.schema_relationships = [
                    r for r in st.session_state.schema_relationships
                    if r["source"] != delete_node and r["target"] != delete_node
                ]
                st.success("Node deleted.")
                st.rerun()

        st.divider()

        st.markdown('<div class="subsection">Create Semantic Relationships</div>', unsafe_allow_html=True)

        if len(st.session_state.schema_nodes) < 2:
            st.warning("Create at least two node labels before defining relationships.")
        else:
            labels = [n["label"] for n in st.session_state.schema_nodes]

            col1, col2, col3 = st.columns(3)
            with col1:
                source_label = st.selectbox("Source Node", labels)
            with col2:
                relationship_name = st.text_input("Relationship Type", placeholder="LIVES_IN")
            with col3:
                target_label = st.selectbox("Target Node", labels, index=1)

            if st.button("Add Relationship", key="save_relationship"):
                if relationship_name == "":
                    st.error("Relationship cannot be empty.")
                else:
                    exists = any(
                        r["source"] == source_label and r["relationship"] == relationship_name
                        and r["target"] == target_label
                        for r in st.session_state.schema_relationships
                    )
                    if exists:
                        st.warning("Relationship already exists.")
                    else:
                        st.session_state.schema_relationships.append({
                            "source": source_label, "relationship": relationship_name.upper(),
                            "target": target_label
                        })
                        st.success("Relationship added.")

        st.divider()

        st.markdown('<div class="subsection">Current Relationships</div>', unsafe_allow_html=True)

        if len(st.session_state.schema_relationships) == 0:
            st.info("No relationships defined yet.")
        else:
            delete_relationship = None
            for idx, rel in enumerate(st.session_state.schema_relationships):
                c1, c2 = st.columns([7, 1])
                with c1:
                    st.markdown(f"""
                    <div style="padding:16px 18px;background:#F8FBFD;border-radius:12px;
                        border-left:6px solid #43A047;margin-bottom:10px;">
                    <span style="font-size:18px;color:{BLUE};">{rel['source']}</span>
                    <span style="font-size:16px;color:{BLUE_DARK};"> — {rel['relationship']} → </span>
                    <span style="font-size:18px;color:#43A047;">{rel['target']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    if st.button("Remove", key=f"delete_rel_{idx}"):
                        delete_relationship = idx

            if delete_relationship is not None:
                st.session_state.schema_relationships.pop(delete_relationship)
                st.success("Relationship removed.")
                st.rerun()

        st.divider()

        st.markdown('<div class="subsection">Live Schema Visualization</div>', unsafe_allow_html=True)
        st.caption("This diagram updates immediately as you create nodes and relationships.")

        if len(st.session_state.schema_nodes) == 0:
            st.info("Add node labels to visualize your schema.")
        else:
            schema_graph = nx.DiGraph()
            for node in st.session_state.schema_nodes:
                schema_graph.add_node(node["label"], color=node["color"])
            for rel in st.session_state.schema_relationships:
                schema_graph.add_edge(rel["source"], rel["target"], relationship=rel["relationship"])

            pos = nx.spring_layout(schema_graph, seed=12)
            fig = go.Figure()

            for edge in schema_graph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                fig.add_trace(go.Scatter(
                    x=[x0, x1], y=[y0, y1], mode="lines",
                    line=dict(width=3, color="#94A9B8"), hoverinfo="text",
                    text=schema_graph.edges[edge]["relationship"], showlegend=False
                ))
                fig.add_annotation(x=(x0 + x1) / 2, y=(y0 + y1) / 2,
                                    text=schema_graph.edges[edge]["relationship"],
                                    showarrow=False, font=dict(color=BLUE_DARK, size=14))

            node_x, node_y, node_text, node_colors = [], [], [], []
            for node, data in schema_graph.nodes(data=True):
                x, y = pos[node]
                node_x.append(x); node_y.append(y); node_text.append(node); node_colors.append(data["color"])

            fig.add_trace(go.Scatter(
                x=node_x, y=node_y, mode="markers+text", text=node_text,
                textposition="bottom center", textfont=dict(color=TEXT_DARK, size=13),
                marker=dict(size=34, color=node_colors, symbol="circle",
                            line=dict(color="white", width=3), opacity=0.95),
                hovertemplate="<b>%{text}</b><extra></extra>"
            ))

            clean_layout(fig, height=400, title="Live Knowledge Graph Schema")

            st.plotly_chart(fig, use_container_width=True, key="live_schema_visualization")

        st.divider()

        st.markdown('<div class="subsection">Export or Reset Schema</div>', unsafe_allow_html=True)

        export_data = {"nodes": st.session_state.schema_nodes, "relationships": st.session_state.schema_relationships}
        json_schema = json.dumps(export_data, indent=4)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download Schema JSON", json_schema, file_name="knowledge_graph_schema.json",
                                mime="application/json", use_container_width=True)
        with col2:
            if st.button("Reset Entire Schema", use_container_width=True):
                st.session_state.schema_nodes = []
                st.session_state.schema_relationships = []
                st.session_state.temp_properties = []
                st.success("Schema reset successfully.")
                st.rerun()

        st.divider()
        st.success("Step 1 completed. Next, upload CSV datasets based on this schema.")

        # ==========================================================
        # STEP 2 - DATASET UPLOAD
        # ==========================================================

        st.markdown('<div class="subsection">Step 2 — Upload Dataset</div>', unsafe_allow_html=True)

        st.write("Upload two CSV files that follow the schema you created above: a **Nodes CSV** "
                  "containing all entities, and a **Relationships CSV** containing connections between entities.")

        with st.expander("View Expected CSV Format", expanded=False):

            st.markdown("**Nodes CSV Example — Extended Demonstration Dataset**")
            sample_nodes = pd.DataFrame({
                "ID": [
                    "P1","P2","P3","P4","D1","D2","C1","C2","C3",
                    "H1","H2","DR1","DR2","M1","M2","O1","O2","S1",
                    "A1","A2","E1","E2","R1","R2"
                ],
                "Label": [
                    "Person","Person","Person","Person","Disease","Disease",
                    "City","City","City","Hospital","Hospital","Doctor","Doctor",
                    "Medicine","Medicine","Organization","Organization","Shelter",
                    "Agency","Agency","Event","Event","Patient","Patient"
                ],
                "Name": [
                    "Aarav Sharma","Priya Patel","Rohan Mehta","Ananya Rao",
                    "Diabetes","Hypertension","Mumbai","Pune","Nashik",
                    "KEM Hospital","Ruby Hall Clinic","Dr. Meera Shah","Dr. Arjun Rao",
                    "Metformin","Amlodipine","Health Ministry","City Disaster Cell",
                    "Shivaji Nagar Shelter","NDRF","Municipal Corporation",
                    "Mumbai Flood 2025","Pune Flood 2025","Rahul Verma","Sneha Kulkarni"
                ],
                "Age": [
                    21,24,29,31,None,None,None,None,None,None,None,45,39,
                    None,None,None,None,None,None,None,None,None,52,36
                ],
                "State": [
                    "Maharashtra","Maharashtra","Maharashtra","Maharashtra",
                    None,None,"Maharashtra","Maharashtra","Maharashtra",
                    "Maharashtra","Maharashtra",None,None,None,None,
                    "Delhi","Maharashtra", "Maharashtra","Maharashtra","Maharashtra",
                    "Maharashtra","Maharashtra","Maharashtra","Maharashtra"
                ],
                "Specialty": [
                    None,None,None,None,None,None,None,None,None,None,None,
                    "Endocrinology","Cardiology",None,None,None,None,None,None,None,None,None,None,None
                ],
                "Capacity": [
                    None,None,None,None,None,None,None,None,None,1200,800,
                    None,None,None,None,None,None,500,None,None,None,None,None,None
                ],
                "Severity": [
                    None,None,None,None,"Moderate","High",None,None,None,None,None,
                    None,None,None,None,None,None,None,None,None,"High","Medium",None,None
                ],
                "Status": [
                    "Active","Active","Active","Active","Managed","Managed",
                    "Active","Active","Active","Operational","Operational","Available",
                    "Available","Prescribed","Prescribed","Active","Active","Open",
                    "Deployed","Active","Resolved","Resolved","Under Care","Under Care"
                ]
            })
            st.dataframe(sample_nodes, use_container_width=True, height=300, hide_index=True)

            st.markdown("**Relationships CSV Example — Extended Demonstration Dataset**")
            sample_rel = pd.DataFrame({
                "Source": [
                    "P1","P2","P3","P4","P1","P2","P3","P4",
                    "P1","P2","P3","P4","D1","D2","DR1","DR2",
                    "H1","H2","O1","O2","A1","A2","E1","E2",
                    "E1","E2","R1","R2","R1","R2","A1","A2"
                ],
                "Relationship": [
                    "LIVES_IN","LIVES_IN","LIVES_IN","LIVES_IN",
                    "HAS_DISEASE","HAS_DISEASE","HAS_DISEASE","HAS_DISEASE",
                    "VISITS","VISITS","VISITS","VISITS",
                    "TREATED_WITH","TREATED_WITH","WORKS_AT","WORKS_AT",
                    "LOCATED_IN","LOCATED_IN","MANAGES","SUPPORTS",
                    "RESPONDS_TO","RESPONDS_TO","OCCURS_IN","OCCURS_IN",
                    "AFFECTS","AFFECTS","LIVES_IN","LIVES_IN",
                    "RECEIVES_CARE","RECEIVES_CARE","RESPONDS_TO","RESPONDS_TO"
                ],
                "Target": [
                    "C1","C1","C2","C3","D1","D2","D1","D2",
                    "H1","H2","H1","H2","M1","M2","H1","H2",
                    "C1","C2","O1","O2","E1","E2","C1","C2",
                    "C1","C2","C1","C2","H1","H2","E1","E2"
                ]
            })
            st.dataframe(sample_rel, use_container_width=True, height=260, hide_index=True)

            st.caption(
                "The sample is intentionally larger so students can test filtering, neighbourhood exploration, "
                "BFS/DFS traversal, shortest-path queries and graph statistics without first preparing their own CSV files."
            )

            st.download_button("Download Sample Nodes CSV", sample_nodes.to_csv(index=False),
                                "sample_nodes.csv", "text/csv")
            st.download_button("Download Sample Relationships CSV", sample_rel.to_csv(index=False),
                                "sample_relationships.csv", "text/csv")

        st.markdown("**Upload CSV Files**")

        col1, col2 = st.columns(2)
        with col1:
            uploaded_nodes = st.file_uploader("Upload Nodes CSV", type="csv", key="nodes_csv")
        with col2:
            uploaded_relationships = st.file_uploader("Upload Relationships CSV", type="csv", key="relationships_csv")

        if uploaded_nodes is not None:
            try:
                st.session_state.uploaded_nodes = pd.read_csv(uploaded_nodes)
                st.success("Nodes CSV uploaded successfully.")
            except Exception as e:
                st.error(f"Unable to read Nodes CSV.\n\n{e}")

        if uploaded_relationships is not None:
            try:
                st.session_state.uploaded_relationships = pd.read_csv(uploaded_relationships)
                st.success("Relationships CSV uploaded successfully.")
            except Exception as e:
                st.error(f"Unable to read Relationships CSV.\n\n{e}")

        if not st.session_state.uploaded_nodes.empty:
            st.markdown('<div class="subsection">Preview Uploaded Nodes</div>', unsafe_allow_html=True)
            st.dataframe(st.session_state.uploaded_nodes, use_container_width=True, height=280)

        if not st.session_state.uploaded_relationships.empty:
            st.markdown('<div class="subsection">Preview Uploaded Relationships</div>', unsafe_allow_html=True)
            st.dataframe(st.session_state.uploaded_relationships, use_container_width=True, height=240)

        # ==========================================================
        # VALIDATION ENGINE
        # ==========================================================

        st.markdown('<div class="subsection">Step 3 — Dataset Validation Engine</div>', unsafe_allow_html=True)

        validation_results = {"passed": [], "warnings": [], "errors": []}

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

            required_node_cols = {"ID", "Label", "Name"}
            required_rel_cols = {"Source", "Relationship", "Target"}

            if not required_node_cols.issubset(nodes.columns):
                missing = required_node_cols - set(nodes.columns)
                validation_results["errors"].append(f"Missing required node columns: {', '.join(missing)}")
            else:
                validation_results["passed"].append("Required node columns found.")

            if not required_rel_cols.issubset(rels.columns):
                missing = required_rel_cols - set(rels.columns)
                validation_results["errors"].append(f"Missing relationship columns: {', '.join(missing)}")
            else:
                validation_results["passed"].append("Required relationship columns found.")

            duplicates = nodes[nodes["ID"].duplicated()]
            if duplicates.empty:
                validation_results["passed"].append("No duplicate node IDs found.")
            else:
                validation_results["errors"].append(f"{len(duplicates)} duplicate node IDs detected.")

            empty_ids = nodes["ID"].isna().sum()
            if empty_ids == 0:
                validation_results["passed"].append("All nodes have unique IDs.")
            else:
                validation_results["errors"].append(f"{empty_ids} node IDs are missing.")

            empty_labels = nodes["Label"].isna().sum()
            if empty_labels == 0:
                validation_results["passed"].append("Every node contains a label.")
            else:
                validation_results["errors"].append(f"{empty_labels} node labels are missing.")

            csv_labels = sorted(nodes["Label"].dropna().unique().tolist())

            st.markdown('<div class="subsection">Auto-Detected Knowledge Graph Schema</div>', unsafe_allow_html=True)

            detected_schema = []
            for label in csv_labels:
                label_df = nodes[nodes["Label"] == label]
                properties = [col for col in label_df.columns
                              if col not in ["ID", "Label"] and label_df[col].notna().any()]
                detected_schema.append({"Entity Label": label, "Properties": ", ".join(properties)})

            st.dataframe(pd.DataFrame(detected_schema), use_container_width=True)

            st.markdown("**Relationship Types Detected**")
            rel_types = sorted(rels["Relationship"].dropna().unique().tolist())
            st.dataframe(pd.DataFrame({"Relationship Type": rel_types}), use_container_width=True)

            if len(st.session_state.schema_nodes) > 0:
                schema_labels = sorted([n["label"] for n in st.session_state.schema_nodes])
                schema_source = "Manual Schema Designer"
            else:
                schema_labels = csv_labels
                schema_source = "Auto Detected from Uploaded CSV"

            st.success(f"Schema Source: {schema_source}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Schema Labels**")
                st.code(schema_labels)
            with col2:
                st.markdown("**CSV Labels**")
                st.code(csv_labels)

            invalid_labels = nodes[~nodes["Label"].isin(schema_labels)]
            if len(invalid_labels) > 0:
                validation_results["errors"].append(f"{len(invalid_labels)} nodes contain undefined labels.")
                st.error("Undefined Labels Found")
                st.markdown("**Expected Labels**")
                st.code(", ".join(schema_labels))
                st.markdown("**Invalid Labels in Uploaded CSV**")
                st.code(", ".join(sorted(invalid_labels["Label"].unique().tolist())))
            else:
                st.success("All entity labels are valid.")

            node_ids = set(nodes["ID"])
            invalid_source = rels[~rels["Source"].isin(node_ids)]
            invalid_target = rels[~rels["Target"].isin(node_ids)]

            if invalid_source.empty:
                validation_results["passed"].append("All relationship source IDs exist.")
            else:
                validation_results["errors"].append(f"{len(invalid_source)} invalid relationship source IDs.")

            if invalid_target.empty:
                validation_results["passed"].append("All relationship target IDs exist.")
            else:
                validation_results["errors"].append(f"{len(invalid_target)} invalid relationship target IDs.")

            empty_relationships = rels["Relationship"].isna().sum()
            if empty_relationships == 0:
                validation_results["passed"].append("Every relationship has a relationship type.")
            else:
                validation_results["errors"].append(f"{empty_relationships} relationships have empty relationship types.")

            self_loops = rels[rels["Source"] == rels["Target"]]
            if self_loops.empty:
                validation_results["passed"].append("No self-loop relationships detected.")
            else:
                validation_results["warnings"].append(f"{len(self_loops)} self-loop relationships detected.")

            connected = set(rels["Source"]).union(set(rels["Target"]))
            orphan_nodes = nodes[~nodes["ID"].isin(connected)]
            if orphan_nodes.empty:
                validation_results["passed"].append("Every node participates in at least one relationship.")
            else:
                validation_results["warnings"].append(f"{len(orphan_nodes)} orphan nodes detected.")

            schema_property_map = {n["label"]: n["properties"] for n in st.session_state.schema_nodes}
            missing_properties = 0
            for _, row in nodes.iterrows():
                expected = schema_property_map.get(row["Label"], [])
                for prop in expected:
                    if prop not in nodes.columns or pd.isna(row[prop]):
                        missing_properties += 1

            if missing_properties == 0:
                validation_results["passed"].append("All required properties are present.")
            else:
                validation_results["warnings"].append(f"{missing_properties} property values are missing.")

            return validation_results

        if st.button("Validate Uploaded Dataset", type="primary"):
            st.session_state.validation_results = validate_dataset()

        results = st.session_state.get("validation_results", {"passed": [], "warnings": [], "errors": []})

        if not st.session_state.uploaded_nodes.empty and not st.session_state.uploaded_relationships.empty:

            p, w, e = len(results["passed"]), len(results["warnings"]), len(results["errors"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Passed Checks", p)
            c2.metric("Warnings", w)
            c3.metric("Errors", e)

            st.markdown("**Validation Summary**")
            for item in results["passed"]:
                st.success(item)
            for item in results["warnings"]:
                st.warning(item)
            for item in results["errors"]:
                st.error(item)

            st.markdown('<div class="subsection">Detailed Validation Report</div>', unsafe_allow_html=True)

            report = ([["PASS", i] for i in results["passed"]] +
                      [["WARNING", i] for i in results["warnings"]] +
                      [["ERROR", i] for i in results["errors"]])

            report_df = pd.DataFrame(report, columns=["Status", "Description"])
            st.dataframe(report_df, use_container_width=True)

            st.download_button("Download Validation Report", report_df.to_csv(index=False),
                                file_name="validation_report.csv", mime="text/csv", use_container_width=True)

        if not st.session_state.uploaded_nodes.empty:

            st.markdown('<div class="subsection">Uploaded Dataset Statistics</div>', unsafe_allow_html=True)

            node_df = st.session_state.uploaded_nodes
            rel_df = st.session_state.uploaded_relationships

            metric_cards(len(node_df), len(rel_df), node_df["Label"].nunique(),
                         rel_df["Relationship"].nunique())

            st.markdown("**Node Label Distribution**")
            label_counts = node_df["Label"].value_counts().reset_index()
            label_counts.columns = ["Label", "Count"]
            fig = px.bar(label_counts, x="Label", y="Count", text="Count")
            clean_layout(fig, height=420)
            st.plotly_chart(fig, use_container_width=True, key="dataset_node_label_distribution")

            st.markdown("**Relationship Type Distribution**")
            rel_counts = rel_df["Relationship"].value_counts().reset_index()
            rel_counts.columns = ["Relationship", "Count"]
            fig2 = px.pie(rel_counts, names="Relationship", values="Count")
            clean_layout(fig2, height=420)
            st.plotly_chart(fig2, use_container_width=True)

        if not st.session_state.uploaded_nodes.empty and not st.session_state.uploaded_relationships.empty:
            if len(validation_results["errors"]) == 0:
                st.success("Dataset successfully validated. Ready for Knowledge Graph generation.")
            else:
                st.error("Dataset contains validation errors. Please fix the CSV files before generating the graph.")

        # ==========================================================
        # STEP 4 - GENERATE KNOWLEDGE GRAPH
        # ==========================================================

        st.markdown('<div class="subsection">Step 4 — Generate Interactive Knowledge Graph</div>', unsafe_allow_html=True)

        st.write("After validation, the uploaded CSV files are converted into a dynamic Knowledge Graph. "
                  "Every entity becomes a node and every relationship becomes an edge.")

        can_generate = (not st.session_state.uploaded_nodes.empty and
                        not st.session_state.uploaded_relationships.empty and
                        len(validation_results["errors"]) == 0)

        if can_generate:
            if st.button("Generate Knowledge Graph", type="primary"):
                with st.spinner("Building Knowledge Graph..."):
                    G = build_networkx_graph(st.session_state.uploaded_nodes, st.session_state.uploaded_relationships)
                    st.session_state.graph = G
                    st.session_state.graph_generated = True
                    st.success("Knowledge Graph generated successfully. You can now run queries and analyze the graph.")
                    st.balloons()
        else:
            st.warning("Please upload and validate a correct dataset first.")

        if st.session_state.graph_generated:

            G = st.session_state.graph

            stats = {
                "nodes": len(G.nodes), "edges": len(G.edges),
                "labels": st.session_state.uploaded_nodes["Label"].nunique(),
                "relationship_types": st.session_state.uploaded_relationships["Relationship"].nunique(),
                "density": round(nx.density(G), 3),
                "connected_components": nx.number_weakly_connected_components(G),
                "average_degree": round(sum(dict(G.degree()).values()) / len(G.nodes), 2)
            }
            st.session_state.graph_stats = stats

            st.markdown('<div class="subsection">Graph Statistics</div>', unsafe_allow_html=True)
            metric_cards(stats["nodes"], stats["edges"], stats["labels"], stats["relationship_types"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Density", stats["density"])
            c2.metric("Connected Components", stats["connected_components"])
            c3.metric("Average Degree", stats["average_degree"])

            st.markdown('<div class="subsection">Interactive Knowledge Graph</div>', unsafe_allow_html=True)
            st.plotly_chart(draw_graph(), use_container_width=True, key="interactive_knowledge_graph_main")

        # ==========================================================
        # SEARCH + NEIGHBORHOOD EXPLORER
        # ==========================================================

        if st.session_state.graph_generated:

            G = st.session_state.graph

            st.markdown('<div class="subsection">Search Entity</div>', unsafe_allow_html=True)

            node_names = [G.nodes[n]["Name"] for n in G.nodes]
            selected_name = st.selectbox("Select Entity", sorted(node_names))

            selected_node = None
            for n, data in G.nodes(data=True):
                if data["Name"] == selected_name:
                    selected_node = n

            if selected_node:

                fig = draw_graph(highlight_nodes=[selected_node])
                st.plotly_chart(fig, use_container_width=True, key=f"search_entity_graph_{selected_node}")

                entity = G.nodes[selected_node]

                st.markdown(f"""
                <div style="background:#F5FAFD;padding:18px 20px;border-radius:12px;border-left:6px solid {BLUE};">
                <h4 style="color:{BLUE};margin:0 0 6px 0;">{entity["Name"]}</h4>
                <p style="margin:0;"><b>Entity ID:</b> {selected_node} &nbsp;|&nbsp; <b>Node Label:</b> {entity["Label"]}</p>
                </div>
                """, unsafe_allow_html=True)

                info_df = pd.DataFrame({"Property": entity.keys(), "Value": entity.values()})
                st.dataframe(info_df, use_container_width=True)

                st.markdown("**Connected Neighbours**")
                neighbours = []
                for neighbour in G.neighbors(selected_node):
                    rel = G.edges[selected_node, neighbour]["relationship"]
                    neighbours.append({"Entity": G.nodes[neighbour]["Name"], "Relationship": rel})

                if neighbours:
                    st.dataframe(pd.DataFrame(neighbours), use_container_width=True)
                else:
                    st.info("This node has no outgoing relationships.")

                st.markdown('<div class="subsection">Neighborhood Explorer</div>', unsafe_allow_html=True)

                if len(G.nodes) == 0:
                    st.warning("Knowledge Graph is empty. Generate a graph first.")
                    st.stop()

                explore_node = st.selectbox("Choose an Entity to Explore", list(G.nodes),
                                             format_func=lambda x: G.nodes[x]["Name"], key="explorer_node")
                hop = st.radio("Neighborhood Depth", [1, 2], horizontal=True)

                visited = {explore_node}
                frontier = {explore_node}
                for _ in range(hop):
                    nxt = set()
                    for node in frontier:
                        nxt.update(G.neighbors(node))
                    visited.update(nxt)
                    frontier = nxt

                subgraph = G.subgraph(visited)
                original_graph = st.session_state.graph
                st.session_state.graph = subgraph

                fig = draw_graph(highlight_nodes=list(visited), highlight_edges=list(subgraph.edges()))
                st.plotly_chart(fig, use_container_width=True, key=f"neighborhood_explorer_{explore_node}_{hop}")

                st.session_state.graph = original_graph

                st.success(f"Showing {hop}-hop neighborhood around **{G.nodes[explore_node]['Name']}**.")

                neighbor_table = [{"Entity": G.nodes[n]["Name"], "Label": G.nodes[n]["Label"], "Degree": G.degree(n)}
                                   for n in visited]
                st.dataframe(pd.DataFrame(neighbor_table), use_container_width=True)

        if st.session_state.graph_generated:

            st.markdown('<div class="subsection">Filter Graph by Node Labels</div>', unsafe_allow_html=True)

            available_labels = sorted(st.session_state.uploaded_nodes["Label"].unique())
            chosen_labels = st.multiselect("Select labels to display", available_labels, default=available_labels)

            if chosen_labels:
                filtered_nodes = st.session_state.uploaded_nodes[
                    st.session_state.uploaded_nodes["Label"].isin(chosen_labels)]
                ids = filtered_nodes["ID"].tolist()
                rels = st.session_state.uploaded_relationships
                filtered_relationships = rels[rels["Source"].isin(ids) & rels["Target"].isin(ids)]

                temp_graph = build_networkx_graph(filtered_nodes, filtered_relationships)
                original_graph = st.session_state.graph
                st.session_state.graph = temp_graph

                fig = draw_graph()
                st.plotly_chart(fig, use_container_width=True, key="filtered_label_graph")

                st.session_state.graph = original_graph

        # ==============================================================
        # STEP 5 - QUERY EXPLORER (replaces the old traversal timeline)
        # ==============================================================

        st.markdown('<div class="subsection">Step 5 — Run Knowledge Graph Queries</div>', unsafe_allow_html=True)

        st.write("Pick a query type below. As the query runs, the graph animates one hop at a time so you can "
                 "see exactly which relationship is being followed at each step.")

        G = st.session_state.graph

        def build_query_events(graph, path_nodes):
            events = []
            visited = []
            for i, node in enumerate(path_nodes):
                visited.append(node)
                events.append({
                    "step": len(events), "node": node, "visited": visited.copy(), "edge": None,
                    "title": f"Visit {graph.nodes[node]['Name']}",
                    "description": f"The query is now at **{graph.nodes[node]['Name']}**."
                })
                if i < len(path_nodes) - 1:
                    nxt = path_nodes[i + 1]
                    if graph.has_edge(node, nxt):
                        rel_name = graph.edges[node, nxt]["relationship"]
                        events.append({
                            "step": len(events), "node": nxt, "visited": visited.copy() + [nxt],
                            "edge": (node, nxt),
                            "title": f"Follow relationship {rel_name}",
                            "description": (f"The query follows the **{rel_name}** relationship "
                                             f"from **{graph.nodes[node]['Name']}** to **{graph.nodes[nxt]['Name']}**.")
                        })
            return events

        query_type = st.selectbox(
            "Query Type",
            ["Show Direct Relationships of an Entity",
             "Explore Outward Connections (Level by Level)",
             "Follow a Deep Connection Chain",
             "Find Shortest Connection Between Two Entities"]
        )

        if "last_query_type" not in st.session_state:
            st.session_state.last_query_type = query_type
        if st.session_state.last_query_type != query_type:
            st.session_state.query_step = 0
            st.session_state.last_query_type = query_type

        path_nodes = []

        if len(G.nodes) == 0:
            st.warning("Generate a Knowledge Graph first before running queries.")
            st.stop()

        if query_type == "Show Direct Relationships of an Entity":
            node = st.selectbox("Choose Entity", list(G.nodes), format_func=lambda x: G.nodes[x]["Name"],
                                 key="query_neighbours")
            path_nodes = [node] + list(G.neighbors(node))

        elif query_type == "Explore Outward Connections (Level by Level)":
            start = st.selectbox("Start Entity", list(G.nodes), format_func=lambda x: G.nodes[x]["Name"],
                                  key="query_bfs_start")
            path_nodes = list(nx.bfs_tree(G, start)) if start in G.nodes else []

        elif query_type == "Follow a Deep Connection Chain":
            start = st.selectbox("Start Entity", list(G.nodes), format_func=lambda x: G.nodes[x]["Name"],
                                  key="query_dfs_start")
            path_nodes = list(nx.dfs_tree(G, start)) if start in G.nodes else []

        elif query_type == "Find Shortest Connection Between Two Entities":
            c1, c2 = st.columns(2)
            with c1:
                source = st.selectbox("Source Entity", list(G.nodes), format_func=lambda x: G.nodes[x]["Name"],
                                       key="query_source")
            with c2:
                target = st.selectbox("Target Entity", list(G.nodes), format_func=lambda x: G.nodes[x]["Name"],
                                       key="query_target")
            try:
                path_nodes = nx.shortest_path(G, source, target)
            except nx.NetworkXNoPath:
                path_nodes = []
                st.error("No path exists between these entities.")

        events = build_query_events(G, path_nodes)
        total_steps = max(len(events) - 1, 0)

        if len(events) == 0:
            st.warning("No result available for the selected query.")
            st.stop()

        st.markdown("**Query Controls**")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("Previous"):
                st.session_state.query_step = max(0, st.session_state.query_step - 1)
        with c2:
            if st.button("Next Step"):
                st.session_state.query_step = min(total_steps, st.session_state.query_step + 1)
        with c3:
            if st.button("Reset"):
                st.session_state.query_step = 0
        with c4:
            speed = st.slider("Animation Speed (sec/step)", 0.1, 2.0, 0.6, 0.1,
                               help="Move the slider left to speed the animation up.")

        query_step = st.slider("Query Timeline", min_value=0, max_value=total_steps,
                                value=st.session_state.query_step, key="query_slider")
        st.session_state.query_step = query_step

        progress = (query_step + 1) / (total_steps + 1) if total_steps >= 0 else 0
        st.progress(progress)
        st.caption(f"Query Step {query_step + 1} of {total_steps + 1}")

        current_event = events[query_step]
        highlighted_nodes = current_event["visited"]
        highlighted_edges = []
        for i in range(len(highlighted_nodes) - 1):
            a, b = highlighted_nodes[i], highlighted_nodes[i + 1]
            if G.has_edge(a, b):
                highlighted_edges.append((a, b))

        fig = draw_graph(highlight_nodes=highlighted_nodes, highlight_edges=highlighted_edges,
                          active_edge=current_event["edge"])
        st.plotly_chart(fig, use_container_width=True, key=f"query_step_{query_step}")

        st.markdown(f"""
        <div style="background:#F5FAFD;border-left:6px solid {BLUE};padding:20px;border-radius:12px;margin-bottom:16px;">
            <h4 style="color:{BLUE};margin:0 0 6px 0;">{current_event["title"]}</h4>
            <p style="font-size:16px;color:{TEXT_DARK};margin:0;">{current_event["description"]}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Entities Visited So Far**")
        visited_table = [{"Step": idx, "Entity": G.nodes[n]["Name"], "Label": G.nodes[n]["Label"]}
                          for idx, n in enumerate(highlighted_nodes, start=1)]
        st.dataframe(pd.DataFrame(visited_table), use_container_width=True)

        st.markdown("**Relationships Used in This Query**")
        rel_table = [{"Source": G.nodes[a]["Name"], "Relationship": G.edges[a, b]["relationship"],
                      "Target": G.nodes[b]["Name"]} for a, b in highlighted_edges]
        if rel_table:
            st.dataframe(pd.DataFrame(rel_table), use_container_width=True)
        else:
            st.info("No relationships used yet.")

        st.markdown('<div class="subsection">Auto-Run Query Animation</div>', unsafe_allow_html=True)

        if st.button("Play Full Animation"):

            graph_placeholder = st.empty()
            info_placeholder = st.empty()

            for event in events:
                visited = event["visited"]
                edges = [(visited[i], visited[i + 1]) for i in range(len(visited) - 1)
                         if G.has_edge(visited[i], visited[i + 1])]

                graph_placeholder.plotly_chart(
                    draw_graph(highlight_nodes=visited, highlight_edges=edges, active_edge=event["edge"]),
                    use_container_width=True
                )

                info_placeholder.markdown(f"""
                <div style="background:#F5FAFD;padding:16px 18px;border-radius:12px;border-left:6px solid {BLUE};">
                <h4 style="color:{BLUE};margin:0 0 6px 0;">Step {event["step"] + 1}</h4>
                <b style="color:{TEXT_DARK};">{event["title"]}</b><br>
                <span style="color:{TEXT_DARK};">{event["description"]}</span>
                </div>
                """, unsafe_allow_html=True)

                time.sleep(speed)

            st.success("Query animation completed!")

        if ("query_history" not in st.session_state or len(st.session_state.query_history) == 0
                or st.session_state.query_history[-1] != query_type):
            st.session_state.query_history.append(query_type)

        st.markdown('<div class="subsection">Query History</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"Executed Queries": st.session_state.query_history}), use_container_width=True)

        st.markdown('<div class="subsection">Query Legend</div>', unsafe_allow_html=True)

        legend_cols = st.columns(3)
        legend_cols[0].markdown(f'<span style="color:{BLUE};">●</span> **Current node**', unsafe_allow_html=True)
        legend_cols[1].markdown('<span style="color:#43A047;">●</span> **Visited node / relationship**', unsafe_allow_html=True)
        legend_cols[2].markdown(f'<span style="color:{ORANGE};">●</span> **Relationship being followed right now**', unsafe_allow_html=True)

        st.success("Query Explorer ready.")

    # ==============================================================
    # OBSERVATIONS MODULE
    # ==============================================================

    elif menu == "Observations":

        st.markdown('<div class="section">Observations</div>', unsafe_allow_html=True)

        st.write("The observation module automatically analyzes the uploaded Knowledge Graph and generates "
                  "experiment observations. Every observation changes depending on the student's uploaded dataset.")

        if not st.session_state.graph_generated:
            st.warning("Generate a Knowledge Graph in the Simulation module first.")
        else:
            G = st.session_state.graph
            nodes_df = st.session_state.uploaded_nodes
            rel_df = st.session_state.uploaded_relationships

            if len(G.nodes) == 0:
                st.warning("No Knowledge Graph available. Please generate a graph in the Simulation module.")
                st.stop()

            total_nodes = len(G.nodes)
            total_edges = len(G.edges)
            total_labels = nodes_df["Label"].nunique()
            total_rel_types = rel_df["Relationship"].nunique()

            metric_cards(total_nodes, total_edges, total_labels, total_rel_types)
            st.divider()

            st.markdown('<div class="subsection">Knowledge Graph Snapshot</div>', unsafe_allow_html=True)
            st.plotly_chart(draw_graph(), use_container_width=True, key="observations_graph_snapshot")
            st.caption("This is the current Knowledge Graph generated from the uploaded dataset.")

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

            st.markdown('<div class="subsection">Automatic Observations</div>', unsafe_allow_html=True)
            for idx, obs in enumerate(observations, start=1):
                make_card(f"Observation {idx}", obs)

            st.divider()

            st.markdown('<div class="subsection">Node Label Analysis</div>', unsafe_allow_html=True)
            label_distribution = nodes_df["Label"].value_counts().reset_index()
            label_distribution.columns = ["Node Label", "Count"]
            st.dataframe(label_distribution, use_container_width=True)

            fig = px.bar(label_distribution, x="Node Label", y="Count", text="Count")
            clean_layout(fig, height=420, title="Distribution of Node Labels")
            st.plotly_chart(fig, use_container_width=True, key="observations_node_label_distribution")

            st.divider()

            st.markdown('<div class="subsection">Relationship Analysis</div>', unsafe_allow_html=True)
            rel_distribution = rel_df["Relationship"].value_counts().reset_index()
            rel_distribution.columns = ["Relationship", "Count"]
            st.dataframe(rel_distribution, use_container_width=True)

            pie = px.pie(rel_distribution, names="Relationship", values="Count")
            clean_layout(pie, height=420, title="Relationship Type Distribution")
            st.plotly_chart(pie, use_container_width=True)

            st.divider()

            st.markdown('<div class="subsection">Degree Centrality Analysis</div>', unsafe_allow_html=True)
            degree_df = pd.DataFrame({"Entity ID": list(dict(G.degree()).keys()),
                                       "Degree": list(dict(G.degree()).values())})
            degree_df["Entity Name"] = degree_df["Entity ID"].apply(lambda x: G.nodes[x]["Name"])
            degree_df = degree_df.sort_values("Degree", ascending=False)
            st.dataframe(degree_df, use_container_width=True)

            degree_chart = px.bar(degree_df, x="Entity Name", y="Degree", text="Degree")
            clean_layout(degree_chart, height=480, title="Degree of Every Entity")
            st.plotly_chart(degree_chart, use_container_width=True)

            st.divider()

            st.markdown('<div class="subsection">Top 5 Most Connected Entities</div>', unsafe_allow_html=True)
            top5 = degree_df.head(5).copy()
            top5.index = range(1, len(top5) + 1)
            st.dataframe(top5, use_container_width=True)

            top_chart = px.bar(top5, x="Entity Name", y="Degree", text="Degree")
            clean_layout(top_chart, height=400, title="Top Connected Entities")
            st.plotly_chart(top_chart, use_container_width=True)

            st.markdown('<div class="subsection">Connected Components</div>', unsafe_allow_html=True)
            components = list(nx.weakly_connected_components(G))
            component_rows = [{"Component": i, "Nodes": len(comp),
                                "Entities": ", ".join(G.nodes[n]["Name"] for n in comp)}
                               for i, comp in enumerate(components, start=1)]
            st.dataframe(pd.DataFrame(component_rows), use_container_width=True)

            st.divider()

            st.markdown('<div class="subsection">Orphan Node Analysis</div>', unsafe_allow_html=True)
            orphan = [n for n in G.nodes if G.degree(n) == 0]
            if orphan:
                orphan_df = pd.DataFrame({"Entity": [G.nodes[n]["Name"] for n in orphan],
                                           "Label": [G.nodes[n]["Label"] for n in orphan]})
                st.warning(f"{len(orphan)} orphan nodes detected.")
                st.dataframe(orphan_df, use_container_width=True)
            else:
                st.success("No orphan nodes were found in the uploaded graph.")

            st.divider()

            st.markdown('<div class="subsection">Property Completeness Analysis</div>', unsafe_allow_html=True)
            property_summary = []
            for label in nodes_df["Label"].unique():
                subset = nodes_df[nodes_df["Label"] == label]
                missing_values = subset.isna().sum().sum()
                filled_values = subset.notna().sum().sum()
                total_values = filled_values + missing_values
                completeness = 100 if total_values == 0 else round((filled_values / total_values) * 100, 2)
                property_summary.append({"Label": label, "Records": len(subset),
                                          "Missing Values": int(missing_values), "Completeness (%)": completeness})

            property_df = pd.DataFrame(property_summary)
            st.dataframe(property_df, use_container_width=True)

            completeness_chart = px.bar(property_df, x="Label", y="Completeness (%)", text="Completeness (%)")
            clean_layout(completeness_chart, height=420, title="Property Completeness by Label")
            st.plotly_chart(completeness_chart, use_container_width=True)

            st.divider()

            st.markdown('<div class="subsection">Graph Summary</div>', unsafe_allow_html=True)
            summary_df = pd.DataFrame({
                "Metric": ["Total Nodes", "Total Relationships", "Node Labels", "Relationship Types",
                           "Graph Density", "Average Degree", "Connected Components", "Most Connected Node"],
                "Value": [total_nodes, total_edges, total_labels, total_rel_types, density, avg_degree,
                          weak_components, max_degree_name]
            })
            st.dataframe(summary_df, use_container_width=True)

            combined = pd.concat([
                summary_df.assign(Category="Summary"),
                label_distribution.rename(columns={"Node Label": "Metric", "Count": "Value"}).assign(Category="Node Labels"),
                rel_distribution.rename(columns={"Relationship": "Metric", "Count": "Value"}).assign(Category="Relationships")
            ], ignore_index=True)

            st.download_button("Download Complete Observation Report", combined.to_csv(index=False),
                                file_name="knowledge_graph_observations.csv", mime="text/csv",
                                use_container_width=True)

            st.divider()

            st.markdown('<div class="subsection">Experiment Conclusion</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="card">
                <h3>Automatically Generated Conclusion</h3>
                <p>The uploaded dataset was successfully transformed into a dynamic Knowledge Graph consisting of
                <b>{total_nodes} nodes</b> and <b>{total_edges} relationships</b>. The graph represents
                <b>{total_labels} categories of entities</b> connected through <b>{total_rel_types} semantic
                relationship types</b>.</p>
                <p>The graph has an average degree of <b>{avg_degree}</b>, a density of <b>{density}</b>, and
                contains <b>{weak_components} connected component(s)</b>. The entity <b>{max_degree_name}</b> is
                the most connected node in the graph, indicating its importance within the network.</p>
                <p>The experiment demonstrates how structured data can be represented as interconnected knowledge,
                enabling graph queries, semantic exploration, visualization, and graph analytics.</p>
                </div>
                """, unsafe_allow_html=True)

            st.success("Dynamic observations generated successfully.")

    # ==============================================================
    # POSTTEST MODULE — bank of 50, random 10, all on one page, no timer
    # ==============================================================

    elif menu == "Posttest":

        st.markdown('<div class="section">Posttest</div>', unsafe_allow_html=True)

        st.write("The posttest consists of **10 randomly generated MCQs** selected from a bank of "
                 "**50 Knowledge Graph questions**. Every attempt generates a new paper. "
                 "Answer all questions on this page, then submit.")

        if not st.session_state.posttest_bank_loaded:

            QUESTION_BANK = [
                {"question": "What is a Knowledge Graph?",
                 "options": ["A graph database that stores only numbers",
                             "A semantic graph connecting entities and relationships",
                             "A SQL table represented as a graph", "A visualization library"],
                 "answer": 1, "explanation": "Knowledge Graphs represent entities and semantic relationships."},
                {"question": "Which of the following represents an entity?",
                 "options": ["Age", "Lives In", "Mumbai", "Connected To"], "answer": 2,
                 "explanation": "Mumbai is a real-world entity."},
                {"question": "Which language is primarily used with Neo4j?",
                 "options": ["SQL", "Cypher", "SPARQL", "Python"], "answer": 1,
                 "explanation": "Neo4j uses Cypher query language."},
                {"question": "A relationship connects ______.",
                 "options": ["Rows", "Columns", "Entities", "Databases"], "answer": 2,
                 "explanation": "Relationships connect two entities."},
                {"question": "RDF stands for:",
                 "options": ["Resource Data Framework", "Relational Data Format",
                             "Resource Description Framework", "Reference Data File"], "answer": 2,
                 "explanation": "RDF = Resource Description Framework."},
                {"question": "A Knowledge Graph triple contains:",
                 "options": ["Node Edge Label", "Subject Predicate Object", "Entity Property Label",
                             "Graph Vertex Weight"], "answer": 1,
                 "explanation": "Every RDF statement is Subject-Predicate-Object."},
                {"question": "SPARQL is used for:",
                 "options": ["Graph visualization", "Querying RDF graphs", "Creating CSV", "Building UI"],
                 "answer": 1, "explanation": "SPARQL queries RDF datasets."},
                {"question": "Ontology defines:",
                 "options": ["Database tables", "Semantic vocabulary and rules", "Programming syntax",
                             "Network topology"], "answer": 1,
                 "explanation": "Ontology defines classes, properties and semantics."},
                {"question": "Which query explores neighbours level by level?",
                 "options": ["DFS", "BFS", "Dijkstra", "A*"], "answer": 1,
                 "explanation": "Breadth First Search explores level-wise."},
                {"question": "Which query goes deep before backtracking?",
                 "options": ["DFS", "BFS", "Random Walk", "Shortest Path"], "answer": 0,
                 "explanation": "Depth First Search visits depth before siblings."}
            ]

            topics = ["Neo4j", "Cypher", "RDF", "Ontology", "SPARQL", "Graph Database",
                      "Knowledge Representation", "Node Labels", "Properties", "Relationships",
                      "Query Traversal", "Shortest Path", "Centrality", "Degree", "Connected Components",
                      "Semantic Web", "DBpedia", "Wikidata", "Google Knowledge Graph", "Healthcare KG",
                      "Fraud Detection", "Recommendation Systems", "Property Graph", "Schema Design",
                      "Graph Analytics", "NetworkX", "Graph Density", "Adjacency Matrix",
                      "Entity Resolution", "Graph Embeddings"]

            i = 0
            while len(QUESTION_BANK) < 50:
                topic = topics[i % len(topics)]
                QUESTION_BANK.append({
                    "question": f"Which statement is TRUE regarding {topic}?",
                    "options": [f"{topic} is unrelated to Knowledge Graphs.",
                                f"{topic} is an important concept used in Knowledge Graph systems.",
                                f"{topic} is only used in relational databases.",
                                f"{topic} cannot represent entities."],
                    "answer": 1,
                    "explanation": f"{topic} is an important concept in graph-based knowledge representation."
                })
                i += 1

            st.session_state.question_bank = QUESTION_BANK
            st.session_state.posttest_bank_loaded = True

        QUESTION_BANK = st.session_state.question_bank

        if len(st.session_state.posttest_questions) == 0:
            st.session_state.posttest_questions = random.sample(QUESTION_BANK, 10)

        for i, q in enumerate(st.session_state.posttest_questions):

            st.markdown(f"""
            <div class="question-box">
                <h4 style="color:{BLUE};margin:0 0 8px 0;">Question {i + 1}</h4>
                <p style="font-size:17px;color:{TEXT_DARK};margin:0;">{q["question"]}</p>
            </div>
            """, unsafe_allow_html=True)

            prev = st.session_state.posttest_answers.get(i, None)
            selected = st.radio("Choose your answer", q["options"], key=f"posttest_q_{i}",
                                 index=prev if prev is not None else None)
            if selected is not None:
                st.session_state.posttest_answers[i] = q["options"].index(selected)

        st.divider()

        if st.button("Submit Posttest", type="primary"):

            st.session_state.posttest_submitted = True
            score = 0
            results = []

            for i, q in enumerate(st.session_state.posttest_questions):
                student = st.session_state.posttest_answers.get(i, -1)
                correct = q["answer"]
                if student == correct:
                    score += 1
                results.append({
                    "Question": q["question"],
                    "Your Answer": q["options"][student] if student != -1 else "Not Answered",
                    "Correct Answer": q["options"][correct],
                    "Result": "Correct" if student == correct else "Incorrect",
                    "Explanation": q["explanation"]
                })

            st.session_state.posttest_score = score
            st.session_state.posttest_results = results
            st.rerun()

        if st.session_state.posttest_submitted:

            score = st.session_state.posttest_score
            percentage = score * 10

            st.markdown('<div class="subsection">Posttest Results</div>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("Score", f"{score}/10")
            c2.metric("Percentage", f"{percentage}%")

            if percentage >= 80:
                grade = "A"
            elif percentage >= 60:
                grade = "B"
            elif percentage >= 40:
                grade = "C"
            else:
                grade = "D"
            c3.metric("Grade", grade)

            if percentage >= 80:
                st.success("Excellent understanding of Knowledge Graph concepts.")
            elif percentage >= 60:
                st.info("Good understanding. Revise a few concepts.")
            else:
                st.warning("Review Theory and Simulation modules before retrying.")

            st.divider()

            st.markdown('<div class="subsection">Detailed Answer Sheet</div>', unsafe_allow_html=True)

            for i, row in enumerate(st.session_state.posttest_results, start=1):
                with st.expander(f"Question {i}"):
                    st.write("**Question:**", row["Question"])
                    st.write("**Your Answer:**", row["Your Answer"])
                    st.write("**Correct Answer:**", row["Correct Answer"])
                    st.write("**Explanation:**", row["Explanation"])

            st.divider()

            if st.button("Generate New Posttest"):
                st.session_state.posttest_questions = random.sample(QUESTION_BANK, 10)
                st.session_state.posttest_answers = {}
                st.session_state.posttest_submitted = False
                st.session_state.posttest_score = None
                st.rerun()

            results_df = pd.DataFrame(st.session_state.posttest_results)
            st.download_button("Download Posttest Results", results_df.to_csv(index=False),
                                file_name="posttest_results.csv", mime="text/csv", use_container_width=True)

    # ==============================================================
    # CONTRIBUTORS MODULE
    # ==============================================================

    if menu == "Contributors":

        st.markdown('<div class="section">Contributors</div>', unsafe_allow_html=True)
        st.markdown('<div class="bodytext">Students who developed and integrated this Knowledge Graph '
                     'Virtual Laboratory experiment.</div>', unsafe_allow_html=True)

        contributors = pd.DataFrame({
            "Roll No.": [41, 42, 44, 45],
            "Name": ["Shivam Makhija", "Paawan Matani", "Manas Mungekar", "Sohan Nagothi"]
        })
        st.dataframe(contributors, use_container_width=True, hide_index=True)

        st.markdown('<div class="subsection">Development Contribution</div>', unsafe_allow_html=True)
        for _, row in contributors.iterrows():
            make_card(f"Roll No. {row['Roll No.']} - {row['Name']}",
                      "Knowledge Graph Virtual Laboratory design, implementation, testing and documentation.")

    # ==============================================================
    # FEEDBACK MODULE
    # ==============================================================

    elif menu == "Feedback":

        st.markdown('<div class="section">Feedback</div>', unsafe_allow_html=True)
        st.markdown('<div class="bodytext">Please provide feedback about the experiment, simulation interface '
                     'and learning experience.</div>', unsafe_allow_html=True)

        with st.form("feedback_form"):
            rating = st.selectbox("Overall experience", ["Excellent", "Good", "Satisfactory", "Needs Improvement"])
            comment = st.text_area("Comments", height=140, placeholder="Enter your feedback")
            submitted = st.form_submit_button("Submit Feedback")
            if submitted:
                st.success("Thank you. Your feedback has been recorded for this session.")

    # ==============================================================
    # REFERENCES MODULE
    # ==============================================================

    if menu == "References":

        st.markdown('<div class="section">References</div>', unsafe_allow_html=True)

        st.markdown('<div class="subsection">Recommended Books</div>', unsafe_allow_html=True)
        books = pd.DataFrame({
            "Book": ["Knowledge Graphs", "Graph Databases", "Learning SPARQL",
                     "Semantic Web for the Working Ontologist", "Neo4j Graph Data Science"],
            "Author": ["Aidan Hogan et al.", "Ian Robinson et al.", "Bob DuCharme", "Dean Allemang", "Amy Hodler"]
        })
        st.dataframe(books, use_container_width=True)

        st.markdown('<div class="subsection">Virtual Lab Resources</div>', unsafe_allow_html=True)
        st.markdown("""
        - Neo4j GraphAcademy
        - W3C RDF 1.1 Specification
        - W3C SPARQL Query Language
        - DBpedia Knowledge Graph
        - Wikidata Knowledge Base
        - NetworkX Documentation
        """)

        st.markdown('<div class="subsection">Video References</div>', unsafe_allow_html=True)
        videos = pd.DataFrame({
            "Topic": ["Knowledge Graph Introduction", "Cypher Tutorial", "RDF & SPARQL", "Semantic Web Basics"],
            "Platform": ["YouTube", "Neo4j GraphAcademy", "W3C", "Coursera"]
        })
        st.dataframe(videos, use_container_width=True)

        st.success("References loaded successfully.")

    # ==============================================================
    # REPORT GENERATION MODULE
    # ==============================================================

    elif menu == "Report Generation":

        st.markdown('<div class="section">Report Generation</div>', unsafe_allow_html=True)

        st.write("Generate a professional Virtual Lab style experiment report based on your uploaded "
                  "Knowledge Graph and assignment results.")

        if not st.session_state.graph_generated:
            st.warning("Please complete the Simulation first.")
        else:
            G = st.session_state.graph
            stats = st.session_state.graph_stats

            st.markdown('<div class="subsection">Student Details</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Student Name", value=st.session_state.student_name)
                roll = st.text_input("Roll Number", value=st.session_state.student_roll)
            with c2:
                division = st.text_input("Division", value=st.session_state.student_division)
                batch = st.text_input("Batch", value=st.session_state.student_batch)

            st.divider()

            st.markdown('<div class="subsection">Report Preview</div>', unsafe_allow_html=True)

            st.markdown(f"""
    ### Knowledge Graph Virtual Laboratory

    **Experiment:** Design and Explore Dynamic Knowledge Graphs

    **Student:** {name}  **Roll Number:** {roll}  **Division:** {division}  **Batch:** {batch}

    **Date:** {datetime.now().strftime("%d-%m-%Y")}
    """)

            st.markdown("**Graph Summary**")

            summary = pd.DataFrame({
                "Metric": ["Total Nodes", "Relationships", "Labels", "Relationship Types", "Density",
                           "Average Degree", "Connected Components"],
                "Value": [stats["nodes"], stats["edges"], stats["labels"], stats["relationship_types"],
                          stats["density"], stats["average_degree"], stats["connected_components"]]
            })
            st.dataframe(summary, use_container_width=True)

            st.markdown("**Posttest Performance**")
            if st.session_state.posttest_score is not None:
                score = st.session_state.posttest_score
                percentage = score * 10
                st.success(f"Posttest Score : {score}/10 ({percentage}%)")
            else:
                percentage = 0
                st.info("Posttest not attempted.")

            st.divider()

            if st.session_state.posttest_score is not None:
                score_chart = px.bar(x=["Posttest Score"], y=[percentage], text=[f"{percentage}%"])
                clean_layout(score_chart, height=350, title="Posttest Performance")
                score_chart.update_layout(yaxis=dict(visible=True, range=[0, 100]))
                st.plotly_chart(score_chart, use_container_width=True)

            if st.button("Capture Current Graph Snapshot"):
                fig = draw_graph()
                image = pio.to_image(fig, format="png")
                st.session_state.graph_image = image
                st.success("Graph snapshot saved for report.")

            if st.button("Generate PDF Report", type="primary"):

                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()

                pdf.set_font("Arial", "B", 18)
                pdf.cell(0, 10, "Knowledge Graph Virtual Laboratory", ln=True)
                pdf.set_font("Arial", "", 13)
                pdf.cell(0, 10, "Virtual Labs Style Experiment Report", ln=True)
                pdf.ln(5)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Student Information", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 8, f"""
                Student Name : {name}
                Roll Number : {roll}
                Division : {division}
                Batch : {batch}
                Date : {datetime.now().strftime("%d-%m-%Y")}
                """)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Experiment Metadata", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 8, """
                Subject : Knowledge Graphs & Information Retrieval Systems
                Experiment Number : KG-09
                Software Used : Python, Streamlit, NetworkX, Plotly, Pandas
                """)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Aim", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 8, "To design, build and explore a dynamic Knowledge Graph using entities, "
                                     "properties and semantic relationships.")

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Real-World Applications", ln=True)
                pdf.set_font("Arial", "", 12)
                for app in ["Google Knowledge Graph for semantic search.",
                            "Fraud Detection in banking networks.",
                            "Recommendation Systems (Netflix, Amazon, Spotify).",
                            "Healthcare Knowledge Graphs for disease relationships.",
                            "Cybersecurity Attack Graph Analysis."]:
                    pdf.multi_cell(0, 8, f"- {app}")

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Theory Summary", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 8, "Knowledge Graphs represent entities as nodes and semantic relationships as "
                                     "edges. The experiment demonstrates schema design, dataset validation, graph "
                                     "queries and analytics.")

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Graph Statistics", ln=True)
                if "graph_image" in st.session_state:
                    with open("graph_snapshot.png", "wb") as img:
                        img.write(st.session_state.graph_image)
                    pdf.image("graph_snapshot.png", w=175)
                    pdf.ln(5)

                pdf.set_font("Arial", "", 12)
                for _, row in summary.iterrows():
                    pdf.cell(0, 8, f"{row['Metric']} : {row['Value']}", ln=True)
                pdf.ln(5)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Node Labels", ln=True)
                labels = st.session_state.uploaded_nodes["Label"].value_counts()
                pdf.set_font("Arial", "", 12)
                for label, count in labels.items():
                    pdf.cell(0, 8, f"{label} : {count}", ln=True)
                pdf.ln(5)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Relationship Types", ln=True)
                relationships = st.session_state.uploaded_relationships["Relationship"].value_counts()
                pdf.set_font("Arial", "", 12)
                for rel, count in relationships.items():
                    pdf.cell(0, 8, f"{rel} : {count}", ln=True)
                pdf.ln(5)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Observations", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 8, f"""
    1. Graph contains {stats['nodes']} entities.
    2. Graph contains {stats['edges']} semantic relationships.
    3. Graph density is {stats['density']}.
    4. Average degree is {stats['average_degree']}.
    5. Graph contains {stats['connected_components']} connected component(s).
    """)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Posttest Result", ln=True)
                pdf.set_font("Arial", "", 12)
                if st.session_state.posttest_score is not None:
                    pdf.cell(0, 8, f"Score : {st.session_state.posttest_score}/10", ln=True)
                else:
                    pdf.cell(0, 8, "Posttest Not Attempted", ln=True)
                pdf.ln(5)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Conclusion", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 8, "The experiment successfully demonstrates dynamic schema creation, dataset "
                                     "validation, graph generation, graph queries and graph analytics using "
                                     "Knowledge Graph concepts.")

                filename = "Knowledge_Graph_VLab_Report.pdf"
                pdf.output(filename)

                with open(filename, "rb") as f:
                    st.download_button("Download Experiment Report", f, filename, "application/pdf",
                                        use_container_width=True)

                st.success("PDF generated successfully.")

                if st.session_state.posttest_score is not None and st.session_state.posttest_score >= 6:
                    st.markdown("---")
                    st.markdown(f"""
                    <div style="background:#F5FAFD;padding:35px;border-radius:18px;border:1px solid #D3E4EE;text-align:center;">
                    <h1 style="color:{BLUE_DARK};">Virtual Lab Completion Certificate</h1>
                    <h3 style="color:{BLUE};">Knowledge Graph Virtual Laboratory</h3>
                    <p style="font-size:15px;color:#444;">This certifies that the student has successfully completed
                    the Knowledge Graph Virtual Laboratory experiment.</p>
                    </div>
                    """, unsafe_allow_html=True)

    # --------------------------------------------------------------
    # VLAB FOOTER
    # --------------------------------------------------------------

    st.markdown("""
    <div class="vlab-footer">
      <div class="vlab-footer-title"><b>Knowledge Graph Virtual Laboratory</b></div>
      <div class="vlab-footer-links">Virtual Labs &nbsp;|&nbsp; Ministry of Education, Government of India</div>
      <div class="vlab-footer-links">Community Links &nbsp; Sakshat Portal &nbsp; Outreach Portal &nbsp; FAQ &nbsp; Contact Us</div>
      <div class="vlab-footer-links">This student-developed experiment follows the structure and learning flow of the Virtual Labs platform.</div>
    </div>
    """, unsafe_allow_html=True)
