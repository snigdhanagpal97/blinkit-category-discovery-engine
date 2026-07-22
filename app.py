import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Blinkit Category Discovery Engine",
    page_icon="🟡",
    layout="wide",
)

# ---------------------------------------------------------
# BLINKIT-INSPIRED CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background-color: #F8F7F2;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1400px;
    }

    h1, h2, h3 {
        color: #171717;
    }

    .hero {
        background: #F8CB46;
        padding: 34px 38px;
        border-radius: 20px;
        margin-bottom: 25px;
    }

    .hero h1 {
        margin: 0;
        font-size: 44px;
        font-weight: 800;
    }

    .hero p {
        margin-top: 10px;
        font-size: 18px;
        max-width: 800px;
        color: #292929;
    }

    .section-label {
        color: #0C831F;
        font-weight: 800;
        font-size: 13px;
        letter-spacing: 1.3px;
        margin-bottom: 4px;
    }

    .insight-box {
        background: #FFF4CC;
        border: 1px solid #F8CB46;
        border-radius: 14px;
        padding: 18px;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .method-card {
        background: white;
        border: 1px solid #E6E3DA;
        border-radius: 14px;
        padding: 18px;
        min-height: 150px;
    }

    .evidence-card {
        background: white;
        border: 1px solid #E7E4DB;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E7E4DB;
        padding: 18px;
        border-radius: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("data/dashboard_data.csv")


df = load_data()

# Normalize boolean
if "discovery_relevant" in df.columns:
    df["discovery_relevant"] = (
        df["discovery_relevant"]
        .astype(str)
        .str.lower()
        .map({"true": True, "false": False})
        .fillna(False)
    )

# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🟡 Blinkit Category Discovery Engine</h1>
        <p>
        Exploring what prevents quick-commerce customers from expanding
        beyond habitual categories — from awareness to consideration to confidence.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------

st.markdown('<div class="section-label">RESEARCH OVERVIEW</div>', unsafe_allow_html=True)
st.header("From broad listening to discovery evidence")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Public conversations", "3,776")
c2.metric("Discovery candidates", "674")
c3.metric("Retrieval rate", "17.8%")

potential = (
    int(df["discovery_relevant"].sum())
    if "discovery_relevant" in df.columns
    else 0
)

c4.metric("Potential discovery signals", f"{potential:,}")

st.caption(
    "Directional public-conversation research — not a representative sample "
    "of Blinkit's customer population."
)

# ---------------------------------------------------------
# RESEARCH FUNNEL
# ---------------------------------------------------------

st.divider()

st.markdown('<div class="section-label">METHODOLOGY</div>', unsafe_allow_html=True)
st.header("High recall first. Precision second.")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        """
        <div class="method-card">
        <h3>🌐 01 · Listen</h3>
        <b>3,776 conversations</b>
        <p>Capture organic quick-commerce conversations across public sources.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        """
        <div class="method-card">
        <h3>🔎 02 · Retrieve</h3>
        <b>674 candidates</b>
        <p>Transparent query families surface potentially relevant evidence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        """
        <div class="method-card">
        <h3>🤖 03 · Classify</h3>
        <b>674 / 674</b>
        <p>Claude applies a controlled behavioral taxonomy.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        """
        <div class="method-card">
        <h3>👤 04 · Validate</h3>
        <b>Human review</b>
        <p>Only evidence-supported signals advance to insight synthesis.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="insight-box">
    <b>⚠️ Retrieval ≠ evidence.</b><br>
    Candidate generation intentionally optimizes for recall.
    Structured classification and human validation provide precision.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------

st.divider()

st.markdown('<div class="section-label">EVIDENCE EXPLORER</div>', unsafe_allow_html=True)
st.header("Explore the conversations behind the research")

filtered = df.copy()

f1, f2, f3 = st.columns(3)

if "platform" in df.columns:
    platforms = sorted(df["platform"].dropna().astype(str).unique())
    selected_platforms = f1.multiselect(
        "Platform",
        platforms,
        default=platforms,
    )

    filtered = filtered[
        filtered["platform"].astype(str).isin(selected_platforms)
    ]

if "new_category_barrier" in df.columns:
    barriers = sorted(
        df["new_category_barrier"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_barriers = f2.multiselect(
        "Barrier",
        barriers,
        default=barriers,
    )

    filtered = filtered[
        filtered["new_category_barrier"]
        .astype(str)
        .isin(selected_barriers)
    ]

if "primary_theme" in df.columns:
    themes = sorted(
        df["primary_theme"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_themes = f3.multiselect(
        "Theme",
        themes,
        default=themes,
    )

    filtered = filtered[
        filtered["primary_theme"]
        .astype(str)
        .isin(selected_themes)
    ]

f4, f5 = st.columns(2)

if "consideration_level" in df.columns:
    levels = sorted(
        df["consideration_level"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_levels = f4.multiselect(
        "Consideration level",
        levels,
        default=levels,
    )

    filtered = filtered[
        filtered["consideration_level"]
        .astype(str)
        .isin(selected_levels)
    ]

relevant_only = f5.toggle(
    "Show discovery-relevant signals only",
    value=True,
)

if relevant_only and "discovery_relevant" in filtered.columns:
    filtered = filtered[filtered["discovery_relevant"] == True]

st.write(f"**{len(filtered):,} conversations shown**")

# ---------------------------------------------------------
# CONVERSATION CARDS
# ---------------------------------------------------------

for _, row in filtered.head(100).iterrows():

    platform = row.get("platform", "Unknown")
    source = row.get("source", "")
    barrier = row.get("new_category_barrier", "none")
    theme = row.get("primary_theme", "")
    consideration = row.get("consideration_level", "")
    text = row.get("text", "")
    jtbd = row.get("jtbd", "")

    st.markdown(
        f"""
        <div class="evidence-card">
            <b>{platform}</b> · {source}
            <br><br>
            “{text}”
            <br><br>
            <small>
            <b>Barrier:</b> {barrier}
            &nbsp;&nbsp; | &nbsp;&nbsp;
            <b>Theme:</b> {theme}
            &nbsp;&nbsp; | &nbsp;&nbsp;
            <b>Consideration:</b> {consideration}
            </small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if pd.notna(jtbd) and str(jtbd).strip():
        with st.expander("View Jobs-to-be-Done"):
            st.write(jtbd)

# ---------------------------------------------------------
# LIMITATIONS
# ---------------------------------------------------------

st.divider()

st.markdown('<div class="section-label">RESEARCH LIMITATIONS</div>', unsafe_allow_html=True)
st.header("What this data cannot tell us")

l1, l2, l3 = st.columns(3)

with l1:
    st.info(
        "**Public-review bias**\n\n"
        "Strong positive and negative experiences are likely overrepresented."
    )

with l2:
    st.info(
        "**Consideration blind spot**\n\n"
        "Platforms users never considered rarely appear in review data."
    )

with l3:
    st.info(
        "**Directional, not representative**\n\n"
        "Corpus distributions should not be interpreted as customer incidence."
    )

st.caption(
    "Independent Product Management research project. "
    "Not affiliated with Blinkit or Eternal Limited."
)
