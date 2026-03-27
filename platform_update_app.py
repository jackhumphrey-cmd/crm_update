import pandas as pd
import streamlit as st
import re as _re

st.set_page_config(
    page_title="🔄 CRM Update Builder v3",
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

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid rgba(11,126,163,0.1) !important;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown p { color: #0d2d3d !important; }
[data-testid="stSidebarHeader"] { display: none; }

[data-testid="stFileUploader"] {
    border: 1px solid rgba(11,126,163,0.2) !important;
    border-radius: 12px !important;
    padding: 0.5rem 0.75rem !important;
    background: rgba(240,247,251,0.6) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(11,126,163,0.4) !important;
}

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

h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #0d2d3d !important;
    letter-spacing: -0.02em !important;
}

[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-color: #0b7ea3 !important;
}

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

[data-testid="stSelectbox"] > div > div {
    border-color: rgba(11,126,163,0.25) !important;
    border-radius: 9px !important;
}

[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid rgba(11,126,163,0.1) !important;
    box-shadow: 0 1px 3px rgba(11,126,163,0.04) !important;
}

.stSpinner > div { border-top-color: #0b7ea3 !important; }

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
    <h1 class="page-title">CRM <span>Update Builder v3</span></h1>
    <p class="page-sub">Map and export CRM update files using CRM and Raise exports.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Uploads
# -----------------------------
update_file = st.sidebar.file_uploader("Update Template", type=["csv"])
crm_file    = st.sidebar.file_uploader("CRM Export", type=["csv"])
raise_file  = st.sidebar.file_uploader("Raise Export", type=["csv"])

if not update_file or not crm_file or not raise_file:
    st.warning("Please upload all three files: Update Template, CRM Export, and Raise Export.")
    st.stop()

# -----------------------------
# Load Files
# -----------------------------
update = pd.read_csv(update_file, dtype=str)
crm    = pd.read_csv(crm_file, dtype=str)
raise_df = pd.read_csv(raise_file, dtype=str)

update.columns   = update.columns.str.strip()
crm.columns      = crm.columns.str.strip()
raise_df.columns = raise_df.columns.str.strip()

# -----------------------------
# Validate required columns
# -----------------------------
required_update = ["TransactionId", "LegacyId", "Amount", "Costs", "CoversCost", "TransactionSource"]
required_crm    = ["Recurring Gift Transaction Id", "Recurring Gift Id"]
required_raise  = ["Profile Number", "Id"]

for col in required_update:
    if col not in update.columns:
        st.error(f"Update Template missing column: {col}")
        st.stop()

for col in required_crm:
    if col not in crm.columns:
        st.error(f"CRM Export missing column: {col}")
        st.stop()

for col in required_raise:
    if col not in raise_df.columns:
        st.error(f"Raise Export missing column: {col}")
        st.stop()

# -----------------------------
# Normalize IDs
# -----------------------------
def normalize(val):
    return str(val).strip().replace(".0", "") if pd.notna(val) else ""

update["TransactionId"]   = update["TransactionId"].apply(normalize)
update["LegacyId"]        = update["LegacyId"].fillna("").astype(str).str.strip()
crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].apply(normalize)
crm["Recurring Gift Id"]             = crm["Recurring Gift Id"].apply(normalize)
raise_df["Profile Number"] = raise_df["Profile Number"].apply(normalize)
raise_df["Id"]             = raise_df["Id"].apply(normalize)

# -----------------------------
# Data Integrity Checks
# -----------------------------
dup_update = update["TransactionId"].duplicated().sum()
dup_crm    = crm["Recurring Gift Transaction Id"].duplicated().sum()
dup_raise  = raise_df["Profile Number"].duplicated().sum()

st.subheader("Data Integrity Checks")

col1, col2, col3 = st.columns(3)
col1.metric("Duplicate TransactionIds (Update)", dup_update)
col2.metric("Duplicate Transaction IDs (CRM)", dup_crm)
col3.metric("Duplicate Profile Numbers (Raise)", dup_raise)

if dup_update > 0:
    st.warning("Duplicate TransactionIds found in Update Template.")
if dup_crm > 0:
    st.warning("Duplicate Transaction IDs found in CRM Export.")
if dup_raise > 0:
    st.warning("Duplicate Profile Numbers found in Raise Export.")

# -----------------------------
# DEDUP before merging to prevent row multiplication
# -----------------------------
crm_deduped   = crm.drop_duplicates(subset=["Recurring Gift Transaction Id"], keep="first")
raise_deduped = raise_df.drop_duplicates(subset=["Profile Number"], keep="first")

# -----------------------------
# MAPPING
#
# RecurringGiftId:
#   Update["TransactionId"] → CRM["Recurring Gift Transaction Id"]
#   → pull CRM["Recurring Gift Id"]
#
# NewTransactionId:
#   Update["TransactionId"] → Raise["Profile Number"]
#   → pull Raise["Id"]
# -----------------------------

# Step 1: Map RecurringGiftId via CRM
crm_slim = crm_deduped[["Recurring Gift Transaction Id", "Recurring Gift Id"]].rename(columns={
    "Recurring Gift Transaction Id": "CRM_TxnId",
    "Recurring Gift Id": "CRM_RecurringGiftId"
})

update = update.merge(crm_slim, how="left", left_on="TransactionId", right_on="CRM_TxnId")
update["RecurringGiftId"] = update["CRM_RecurringGiftId"]
update = update.drop(columns=["CRM_TxnId", "CRM_RecurringGiftId"], errors="ignore")

# Step 2: Map NewTransactionId via Raise export
raise_slim = raise_deduped[["Profile Number", "Id"]].rename(columns={
    "Profile Number": "Raise_ProfileNumber",
    "Id": "Raise_Id"
})

update = update.merge(raise_slim, how="left", left_on="TransactionId", right_on="Raise_ProfileNumber")
update["NewTransactionId"] = update["Raise_Id"]
update = update.drop(columns=["Raise_ProfileNumber", "Raise_Id"], errors="ignore")

# Step 3: Set TransactionSource to RaiseDonors
update["TransactionSource"] = "RaiseDonors"

# -----------------------------
# CoversCost Project Split
# -----------------------------

def is_covers_cost(val):
    return str(val).strip().lower() == "true"

def is_blank(val):
    return pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() == "nan"

def find_next_project_slot(row, columns):
    i = 1
    while True:
        code_col = f"Project{i}Code"
        name_col = f"Project{i}Name"
        amt_col  = f"Project{i}Amount"
        if code_col not in columns and name_col not in columns and amt_col not in columns:
            return None
        if is_blank(row.get(code_col, "")) and is_blank(row.get(name_col, "")) and is_blank(row.get(amt_col, "")):
            return i
        i += 1

output = update.copy()

# Pre-create the next available project slot so the finder always has somewhere to write
existing_project_nums = set()
for col in output.columns:
    m = _re.match(r"Project(\d+)(Code|Name|Amount)", col)
    if m:
        existing_project_nums.add(int(m.group(1)))

if existing_project_nums:
    next_slot = max(existing_project_nums) + 1
    for suffix in ["Code", "Name", "Amount"]:
        col = f"Project{next_slot}{suffix}"
        if col not in output.columns:
            output[col] = ""

covers_cost_count = 0

for idx, row in output.iterrows():
    if is_covers_cost(row.get("CoversCost", "")):
        try:
            amount = float(row["Amount"])
            costs  = float(row["Costs"])
            output.at[idx, "Amount"] = str(round(amount + costs, 2))
        except (ValueError, TypeError):
            pass

        slot = find_next_project_slot(row, output.columns.tolist())
        if slot is not None:
            output.at[idx, f"Project{slot}Code"]   = "CREDITCARDCOSTS"
            output.at[idx, f"Project{slot}Name"]   = "Processing Fees"
            output.at[idx, f"Project{slot}Amount"] = row["Costs"]
            covers_cost_count += 1
        else:
            st.warning(
                f"Row {idx} (TransactionId: {row.get('TransactionId', '')}) "
                f"has no available project slot for the CoversCost split."
            )

# -----------------------------
# Summary Metrics
# -----------------------------
def is_missing(series):
    return series.isna() | (series.astype(str).str.lower() == "nan")

missing_recurring_gift  = is_missing(output["RecurringGiftId"]).sum()
missing_new_transaction = is_missing(output["NewTransactionId"]).sum()

st.subheader("Mapping Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Rows", len(output))
col2.metric("Missing RecurringGiftId", missing_recurring_gift)
col3.metric("Missing NewTransactionId", missing_new_transaction)
col4.metric("CoversCost Splits Applied", covers_cost_count)

# -----------------------------
# Preview Output
# -----------------------------
st.subheader("Preview Output")
st.dataframe(output, use_container_width=True)

# -----------------------------
# Download Output
# -----------------------------
csv = output.to_csv(index=False).encode("utf-8")
st.download_button("Download Updated File", csv, "crm_updates_v3.csv")

# =========================================================
# DEBUGGER PANEL
# =========================================================
st.subheader("🔍 Mapping Debugger")

debug_df = output[["TransactionId", "LegacyId", "NewTransactionId", "RecurringGiftId", "TransactionSource"]].copy()

debug_df["NewTxn Match"] = debug_df["NewTransactionId"].apply(
    lambda x: "✅" if pd.notna(x) and str(x).lower() not in ("nan", "") else "❌"
)
debug_df["CRM Match"] = debug_df["RecurringGiftId"].apply(
    lambda x: "✅" if pd.notna(x) and str(x).lower() != "nan" else "❌"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("NewTransactionId Matched", (debug_df["NewTxn Match"] == "✅").sum())
col2.metric("NewTransactionId Missing",  (debug_df["NewTxn Match"] == "❌").sum())
col3.metric("CRM Matched",   (debug_df["CRM Match"] == "✅").sum())
col4.metric("CRM Unmatched", (debug_df["CRM Match"] == "❌").sum())

status_filter = st.selectbox(
    "Filter rows",
    ["All", "NewTransactionId Matched", "NewTransactionId Missing", "CRM Matched", "CRM Unmatched"]
)

if status_filter == "NewTransactionId Matched":
    filtered = debug_df[debug_df["NewTxn Match"] == "✅"]
elif status_filter == "NewTransactionId Missing":
    filtered = debug_df[debug_df["NewTxn Match"] == "❌"]
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
    "mapping_debug_report_v3.csv"
)

# -----------------------------
# Problem Rows
# -----------------------------
problem_rows = output[
    is_missing(output["RecurringGiftId"]) | is_missing(output["NewTransactionId"])
]

if len(problem_rows) > 0:
    st.subheader("Problem Rows")
    st.dataframe(problem_rows, use_container_width=True)
    st.download_button(
        "Download Problem Rows",
        problem_rows.to_csv(index=False).encode("utf-8"),
        "problem_rows_v3.csv"
    )

st.markdown("""
<div class="hub-footer">
    Built for efficient recurring data migrations &nbsp;·&nbsp; LRD Tools
</div>
""", unsafe_allow_html=True)
