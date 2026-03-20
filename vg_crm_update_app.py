import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="🔄 CRM Update Builder",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 CRM Update Builder")

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
required_update = ["TransactionId", "Amount", "CoversCost", "Costs"]
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
#
# NewTransactionId:
#   Update["TransactionId"] → Schedule["Recurring Id"] (UUID match)
#   → pull Schedule["Recurring Id"] into NewTransactionId
#
# RecurringGiftId:
#   Update["TransactionId"] → Schedule["Recurring Id"] → get Schedule["LegacyId"]
#   → Schedule["LegacyId"] → CRM["Recurring Gift Transaction Id"]
#   → pull CRM["Recurring Id"] into RecurringGiftId
# -----------------------------

# Step 1: Join Update → Schedule on UUID
# Rename schedule cols to avoid collision with update's own LegacyId column
sched_slim = schedule[["Recurring Id", "LegacyId"]].rename(columns={
    "Recurring Id": "Sched_RecurringId",
    "LegacyId": "Sched_LegacyId"
})

merged = update.merge(sched_slim, how="left", left_on="TransactionId", right_on="Sched_RecurringId")

# NewTransactionId comes directly from Schedule["Recurring Id"] (the UUID)
merged["NewTransactionId"] = merged["Sched_RecurringId"]

# Step 2: Join → CRM on Sched_LegacyId = CRM Recurring Gift Transaction Id
crm_slim = crm[["Recurring Gift Transaction Id", "Recurring Id"]].rename(columns={
    "Recurring Id": "CRM_RecurringId"
})

merged = merged.merge(crm_slim, how="left", left_on="Sched_LegacyId", right_on="Recurring Gift Transaction Id")

# RecurringGiftId comes from CRM["Recurring Id"]
merged["RecurringGiftId"] = merged["CRM_RecurringId"]

merged["TransactionSource"] = "RaiseDonors"

# Drop helper columns
merged = merged.drop(columns=[
    "Sched_RecurringId", "Sched_LegacyId",
    "Recurring Gift Transaction Id", "CRM_RecurringId"
], errors="ignore")

update = merged

# -----------------------------
# CoversCost Logic
# -----------------------------
update["CoversCost"] = update["CoversCost"].astype(str).str.lower() == "true"
update["Amount"] = pd.to_numeric(update["Amount"], errors="coerce").fillna(0)
update["Costs"] = pd.to_numeric(update["Costs"], errors="coerce").fillna(0)

mask = update["CoversCost"]
update.loc[mask, "Amount"] = update.loc[mask, "Amount"] + update.loc[mask, "Costs"]

# -----------------------------
# Add CREDITCARDCOSTS split
# -----------------------------
project_cols = [col for col in update.columns if "Project" in col and "Code" in col]
next_index = len(project_cols) + 1

code_col = f"Project{next_index}Code"
name_col = f"Project{next_index}Name"
amount_col = f"Project{next_index}Amount"

update[code_col] = ""
update[name_col] = ""
update[amount_col] = ""

update.loc[mask, code_col] = "CREDITCARDCOSTS"
update.loc[mask, name_col] = "Processing Fees"
update.loc[mask, amount_col] = update.loc[mask, "Costs"]

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
# 🔍 DEBUGGER PANEL
# =========================================================
st.subheader("🔍 Mapping Debugger")

debug_df = update[["TransactionId", "NewTransactionId", "RecurringGiftId"]].copy()

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
