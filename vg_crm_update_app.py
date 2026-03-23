import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="🔄 CRM Update Builder",
    page_icon="🔄",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #f0f7fb;
    background-image:
        radial-gradient(ellipse 70% 40% at 55% 0%, rgba(26,140,181,0.18) 0%, transparent 65%),
        radial-gradient(ellipse 40% 30% at 5% 95%, rgba(11,126,163,0.1) 0%, transparent 60%);
}

#MainMenu, footer, header { visibility: hidden; }

/* ── Page header ── */
.page-header { padding: 1.8rem 0 0.5rem; }
.page-badge {
    display: inline-block;
    background: rgba(11,126,163,0.1);
    border: 1px solid rgba(11,126,163,0.25);
    color: #0b7ea3;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    margin-bottom: 0.9rem;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #0d2d3d;
    letter-spacing: -0.03em;
    margin: 0 0 0.4rem;
    line-height: 1.15;
}
.page-title span {
    background: linear-gradient(135deg, #0b7ea3 0%, #1ab5d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.page-sub {
    font-size: 0.88rem;
    color: #6a8fa0;
    font-weight: 300;
    margin: 0 0 1.5rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid rgba(11,126,163,0.1) !important;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown p {
    color: #0d2d3d !important;
}
[data-testid="stSidebarHeader"] { display: none; }

/* ── File uploaders ── */
[data-testid="stFileUploader"] {
    border: 1px solid rgba(11,126,163,0.2) !important;
    border-radius: 12px !important;
    padding: 0.5rem 0.75rem !important;
    background: rgba(240,247,251,0.6) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(11,126,163,0.4) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid rgba(11,126,163,0.1);
    border-radius: 14px;
    padding: 1.4rem 1.6rem !important;
    box-shadow: 0 1px 3px rgba(11,126,163,0.05), 0 4px 12px rgba(11,126,163,0.06);
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: #7aaabb !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.35 !important;
    margin-bottom: 0.4rem !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #0d2d3d !important;
}

/* ── Section headings ── */
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #0d2d3d !important;
    letter-spacing: -0.02em !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-color: #0b7ea3 !important;
}

/* ── Buttons ── */
.stDownloadButton button, .stButton button {
    background: linear-gradient(135deg, #0b7ea3 0%, #1a8cb5 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.2rem !important;
    box-shadow: 0 2px 8px rgba(11,126,163,0.28) !important;
    transition: opacity 0.2s !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    opacity: 0.88 !important;
    box-shadow: 0 4px 14px rgba(11,126,163,0.38) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    border-color: rgba(11,126,163,0.25) !important;
    border-radius: 9px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid rgba(11,126,163,0.1) !important;
    box-shadow: 0 1px 3px rgba(11,126,163,0.04) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #0b7ea3 !important; }

/* ── Footer ── */
.hub-footer {
    text-align: center;
    margin-top: 2.5rem;
    font-size: 0.71rem;
    color: #a8c8d8;
    letter-spacing: 0.04em;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div class="page-badge">LRD Internal Tools</div>
    <h1 class="page-title">Virtuous Giving <span>CRM Update Builder</span></h1>
    <p class="page-sub">Map and export CRM update files for Virtuous Giving migrations.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Uploads
# -----------------------------
update_file = st.sidebar.file_uploader("Update Template", type=["csv"])
crm_file = st.sidebar.file_uploader("CRM Export", type=["csv"])
schedule_file = st.sidebar.file_uploader("Schedule File", type=["csv"])

if not update_file or not crm_file or not schedule_file:
    st.warning("Please upload all three files: Update Template, CRM Export, and Schedule File.")
    st.stop()

# -----------------------------
# Load Files
# -----------------------------
update = pd.read_csv(update_file, dtype=str)
crm = pd.read_csv(crm_file, dtype=str)
schedule = pd.read_csv(schedule_file, dtype=str)

update.columns = update.columns.str.strip()
crm.columns = crm.columns.str.strip()
schedule.columns = schedule.columns.str.strip()

# -----------------------------
# Validate required columns
# -----------------------------
required_update = ["TransactionId", "LegacyId", "Amount", "Costs"]
required_crm = ["Recurring Gift Transaction Id", "Recurring Id"]
required_schedule = ["Recurring Id", "LegacyId"]

for col in required_update:
    if col not in update.columns:
        st.error(f"Update file missing column: {col}")
        st.stop()

for col in required_crm:
    if col not in crm.columns:
        st.error(f"CRM file missing column: {col}")
        st.stop()

for col in required_schedule:
    if col not in schedule.columns:
        st.error(f"Schedule file missing column: {col}")
        st.stop()

# -----------------------------
# Normalize IDs
# -----------------------------
def normalize(val):
    return str(val).strip().replace(".0", "") if pd.notna(val) else val

update["TransactionId"] = update["TransactionId"].apply(normalize)
update["LegacyId"] = update["LegacyId"].apply(normalize)
crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].apply(normalize)
crm["Recurring Id"] = crm["Recurring Id"].apply(normalize)
schedule["Recurring Id"] = schedule["Recurring Id"].apply(normalize)
schedule["LegacyId"] = schedule["LegacyId"].apply(normalize)

# -----------------------------
# Data Integrity Checks
# -----------------------------
dup_update = update["TransactionId"].duplicated().sum()
dup_crm = crm["Recurring Gift Transaction Id"].duplicated().sum()
dup_schedule = schedule["Recurring Id"].duplicated().sum()

st.subheader("Data Integrity Checks")

col1, col2, col3 = st.columns(3)
col1.metric("Duplicate TransactionIds (Update)", dup_update)
col2.metric("Duplicate Transaction IDs (CRM)", dup_crm)
col3.metric("Duplicate Recurring Ids (Schedule)", dup_schedule)

if dup_update > 0:
    st.warning("Duplicate TransactionIds found in Update file.")
if dup_crm > 0:
    st.warning("Duplicate Transaction IDs found in CRM file.")
if dup_schedule > 0:
    st.warning("Duplicate Recurring Ids found in Schedule file.")

# -----------------------------
# MAPPING
# -----------------------------

# Step 1: Join Update → Schedule on LegacyId to get NewTransactionId
sched_slim = schedule[["LegacyId", "Recurring Id"]].rename(columns={
    "LegacyId": "Sched_LegacyId",
    "Recurring Id": "Sched_RecurringId"
})

merged = update.merge(sched_slim, how="left", left_on="LegacyId", right_on="Sched_LegacyId")

# NewTransactionId comes from Schedule["Recurring Id"]
merged["NewTransactionId"] = merged["Sched_RecurringId"]

# Step 2: Join → CRM on Sched_LegacyId = CRM Recurring Gift Transaction Id
crm_slim = crm[["Recurring Gift Transaction Id", "Recurring Id"]].rename(columns={
    "Recurring Id": "CRM_RecurringId"
})

merged = merged.merge(crm_slim, how="left", left_on="Sched_LegacyId", right_on="Recurring Gift Transaction Id")

# RecurringGiftId comes from CRM["Recurring Id"]
merged["RecurringGiftId"] = merged["CRM_RecurringId"]

# Drop helper columns
merged = merged.drop(columns=[
    "Sched_LegacyId", "Sched_RecurringId",
    "Recurring Gift Transaction Id", "CRM_RecurringId"
], errors="ignore")

update = merged

# -----------------------------
# Summary Metrics
# -----------------------------
def is_missing(series):
    return series.isna() | (series.astype(str).str.lower() == "nan")

missing_recurring_gift = is_missing(update["RecurringGiftId"]).sum()
missing_new_transaction = is_missing(update["NewTransactionId"]).sum()

st.subheader("Mapping Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Total Rows", len(update))
col2.metric("Missing RecurringGiftId", missing_recurring_gift)
col3.metric("Missing NewTransactionId", missing_new_transaction)

# -----------------------------
# Preview Output
# -----------------------------
st.subheader("Preview Output")
st.dataframe(update, use_container_width=True)

# -----------------------------
# Download Output
# -----------------------------
csv = update.to_csv(index=False).encode("utf-8")
st.download_button("Download Updated File", csv, "crm_updates.csv")

# =========================================================
# DEBUGGER PANEL
# =========================================================
st.subheader("🔍 Mapping Debugger")

debug_df = update[["TransactionId", "LegacyId", "NewTransactionId", "RecurringGiftId"]].copy()

debug_df["Schedule Match"] = debug_df["NewTransactionId"].apply(
    lambda x: "✅" if pd.notna(x) and str(x).lower() != "nan" else "❌"
)
debug_df["CRM Match"] = debug_df["RecurringGiftId"].apply(
    lambda x: "✅" if pd.notna(x) and str(x).lower() != "nan" else "❌"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Schedule Matched", (debug_df["Schedule Match"] == "✅").sum())
col2.metric("Schedule Unmatched", (debug_df["Schedule Match"] == "❌").sum())
col3.metric("CRM Matched", (debug_df["CRM Match"] == "✅").sum())
col4.metric("CRM Unmatched", (debug_df["CRM Match"] == "❌").sum())

status_filter = st.selectbox(
    "Filter rows",
    ["All", "Schedule Matched", "Schedule Unmatched", "CRM Matched", "CRM Unmatched"]
)

if status_filter == "Schedule Matched":
    filtered = debug_df[debug_df["Schedule Match"] == "✅"]
elif status_filter == "Schedule Unmatched":
    filtered = debug_df[debug_df["Schedule Match"] == "❌"]
elif status_filter == "CRM Matched":
    filtered = debug_df[debug_df["CRM Match"] == "✅"]
elif status_filter == "CRM Unmatched":
    filtered = debug_df[debug_df["CRM Match"] == "❌"]
else:
    filtered = debug_df

st.dataframe(filtered, use_container_width=True)

st.download_button(
    "Download Debug Report",
    filtered.to_csv(index=False).encode("utf-8"),
    "mapping_debug_report.csv"
)

# -----------------------------
# Problem Rows
# -----------------------------
problem_rows = update[
    is_missing(update["RecurringGiftId"]) | is_missing(update["NewTransactionId"])
]

if len(problem_rows) > 0:
    st.subheader("Problem Rows")
    st.dataframe(problem_rows, use_container_width=True)
    st.download_button(
        "Download Problem Rows",
        problem_rows.to_csv(index=False).encode("utf-8"),
        "problem_rows.csv"
    )

st.markdown("""
<div class="hub-footer">
    Built for efficient recurring data migrations &nbsp;·&nbsp; LRD Tools
</div>
""", unsafe_allow_html=True)
