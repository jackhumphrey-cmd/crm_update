import streamlit as st

st.set_page_config(
    page_title="LRD Migration Hub",
    page_icon="💳",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(99,57,255,0.25) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 80% 80%, rgba(0,200,180,0.08) 0%, transparent 60%);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 3rem; padding-bottom: 3rem; max-width: 680px; }

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 3rem 0 2.5rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,57,255,0.15);
    border: 1px solid rgba(99,57,255,0.4);
    color: #a78bfa;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    margin-bottom: 1.4rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: #f0eeff;
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin: 0 0 1rem;
}
.hero-title span {
    background: linear-gradient(135deg, #a78bfa 0%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1rem;
    color: #8884a8;
    font-weight: 300;
    margin: 0;
    line-height: 1.6;
}

/* ── Cards ── */
.tool-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    transition: border-color 0.2s, background 0.2s, transform 0.2s;
    text-decoration: none;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.tool-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(99,57,255,0.06) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.25s;
}
.tool-card:hover {
    border-color: rgba(99,57,255,0.45);
    background: rgba(255,255,255,0.055);
    transform: translateY(-2px);
}
.tool-card:hover::before { opacity: 1; }

.card-icon {
    font-size: 1.6rem;
    width: 48px;
    height: 48px;
    background: rgba(99,57,255,0.12);
    border: 1px solid rgba(99,57,255,0.2);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.card-body { flex: 1; }
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #ede9fe;
    margin: 0 0 0.3rem;
    letter-spacing: -0.01em;
}
.card-desc {
    font-size: 0.82rem;
    color: #6b6888;
    margin: 0;
    line-height: 1.5;
}
.card-arrow {
    color: #4b4868;
    font-size: 1.1rem;
    flex-shrink: 0;
    transition: color 0.2s, transform 0.2s;
}
.tool-card:hover .card-arrow {
    color: #a78bfa;
    transform: translateX(3px);
}

/* ── Divider label ── */
.section-label {
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #3d3a55;
    text-align: center;
    margin: 2rem 0 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.section-label::before, .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}

/* ── Footer ── */
.hub-footer {
    text-align: center;
    margin-top: 2.5rem;
    font-size: 0.72rem;
    color: #3a3755;
    letter-spacing: 0.04em;
}

/* ── Streamlit link_button override ── */
.stLinkButton a {
    background: linear-gradient(135deg, #6339ff, #4f46e5) !important;
    border: none !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 0.45rem 1.1rem !important;
    letter-spacing: 0.02em;
    transition: opacity 0.2s !important;
}
.stLinkButton a:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-badge">LRD Internal Tools</div>
    <h1 class="hero-title">Migration <span>Hub</span></h1>
    <p class="hero-sub">Select a workflow below to launch the right tool for your migration.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-label">CRM Update Tools</div>', unsafe_allow_html=True)

# ── Virtuous Giving Card ──
with st.container(border=False):
    st.markdown("""
    <div class="tool-card">
        <div class="card-icon">🏛️</div>
        <div class="card-body">
            <p class="card-title">Virtuous Giving CRM Updates</p>
            <p class="card-desc">Build and export CRM update files for Virtuous Giving.</p>
        </div>
        <div class="card-arrow">→</div>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("Launch →", "https://vg-crm-update.streamlit.app", use_container_width=False)

st.write("")

# ── Raise Card ──
with st.container(border=False):
    st.markdown("""
    <div class="tool-card">
        <div class="card-icon">🔄</div>
        <div class="card-body">
            <p class="card-title">LRD → Raise CRM Updates</p>
            <p class="card-desc">Map and export CRM update files for LRD to Raise migrations.</p>
        </div>
        <div class="card-arrow">→</div>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("Launch →", "https://raise-crm-update.streamlit.app", use_container_width=False)

# ── Footer ──
st.markdown("""
<div class="hub-footer">
    Built for efficient recurring data migrations &nbsp;·&nbsp; LRD Tools
</div>
""", unsafe_allow_html=True)
