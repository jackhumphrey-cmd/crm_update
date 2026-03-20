import streamlit as st

st.set_page_config(
    page_title="LRD Migration Hub",
    page_icon="💳",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #f5f4f0;
    background-image:
        radial-gradient(ellipse 70% 40% at 60% 0%, rgba(190,180,255,0.25) 0%, transparent 65%),
        radial-gradient(ellipse 40% 30% at 10% 90%, rgba(180,230,220,0.2) 0%, transparent 60%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 3rem; padding-bottom: 3rem; max-width: 660px; }

/* Hide all default streamlit elements inside card areas */
.stLinkButton { display: none !important; }

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 2.5rem 0 2rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,57,255,0.08);
    border: 1px solid rgba(99,57,255,0.18);
    color: #6339ff;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: #1a1830;
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin: 0 0 0.9rem;
}
.hero-title span {
    background: linear-gradient(135deg, #6339ff 0%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 0.95rem;
    color: #8b87a8;
    font-weight: 300;
    margin: 0;
    line-height: 1.6;
}

/* ── Section label ── */
.section-label {
    font-size: 0.67rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #b0adc8;
    text-align: center;
    margin: 1.8rem 0 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.section-label::before, .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(0,0,0,0.07);
}

/* ── Cards ── */
.tool-card {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 18px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
    text-decoration: none;
}
.tool-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 12px 32px rgba(99,57,255,0.1);
    transform: translateY(-2px);
    border-color: rgba(99,57,255,0.2);
}

.card-icon {
    font-size: 1.4rem;
    width: 46px;
    height: 46px;
    background: linear-gradient(135deg, #ede9ff 0%, #e0f2fe 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.card-body { flex: 1; }
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #1a1830;
    margin: 0 0 0.25rem;
    letter-spacing: -0.01em;
}
.card-desc {
    font-size: 0.8rem;
    color: #9c98b8;
    margin: 0;
    line-height: 1.5;
}
.card-btn {
    flex-shrink: 0;
    background: linear-gradient(135deg, #6339ff 0%, #4f46e5 100%);
    color: #fff !important;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 500;
    text-decoration: none !important;
    padding: 0.5rem 1.1rem;
    border-radius: 9px;
    letter-spacing: 0.01em;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(99,57,255,0.25);
    transition: opacity 0.2s, box-shadow 0.2s;
}
.card-btn:hover {
    opacity: 0.88;
    box-shadow: 0 4px 14px rgba(99,57,255,0.35);
}

/* ── Footer ── */
.hub-footer {
    text-align: center;
    margin-top: 2.2rem;
    font-size: 0.71rem;
    color: #c0bdd6;
    letter-spacing: 0.04em;
}
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

# ── Cards ──
st.markdown("""
<a class="tool-card" href="https://vg-crm-update.streamlit.app" target="_blank">
    <div class="card-icon">🏛️</div>
    <div class="card-body">
        <p class="card-title">Virtuous Giving CRM Updates</p>
        <p class="card-desc">Build and export CRM update files for Virtuous Giving.</p>
    </div>
    <span class="card-btn">Launch →</span>
</a>

<a class="tool-card" href="https://raise-crm-update.streamlit.app" target="_blank">
    <div class="card-icon">🔄</div>
    <div class="card-body">
        <p class="card-title">LRD → Raise CRM Updates</p>
        <p class="card-desc">Map and export CRM update files for LRD to Raise migrations.</p>
    </div>
    <span class="card-btn">Launch →</span>
</a>
""", unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div class="hub-footer">
    Built for efficient recurring data migrations &nbsp;·&nbsp; LRD Tools
</div>
""", unsafe_allow_html=True)
