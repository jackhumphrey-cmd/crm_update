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

# -----------------------------
# Normalize columns
# -----------------------------
update.columns = update.columns.str.strip()
crm.columns = crm.columns.str.strip()
schedule.columns = schedule.columns.str.strip()

# -----------------------------
# Validate required columns
# -----------------------------
required_update = ["LegacyId", "Amount", "CoversCost", "Costs"]
required_crm = ["Recurring Gift Transaction Id", "Recurring Gift Id"]
required_schedule = ["LegacyId", "Recurring Id"]

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
    return str(val).strip().replace(".0", "")

update["LegacyId"] = update["LegacyId"].apply(normalize)
crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].apply(normalize)
crm["Recurring Gift Id"] = crm["Recurring Gift Id"].astype(str).str.strip()
schedule["LegacyId"] = schedule["LegacyId"].apply(normalize)
schedule["Recurring Id"] = schedule["Recurring Id"].astype(str).str.strip()

# -----------------------------
# Data Integrity Checks
# -----------------------------
dup_update = update["LegacyId"].duplicated().sum()
dup_crm = crm["Recurring Gift Transaction Id"].duplicated().sum()
dup_schedule = schedule["LegacyId"].duplicated().sum()

st.subheader("Data Integrity Checks")

col1, col2, col3 = st.columns(3)
col1.metric("Duplicate LegacyIds (Update)", dup_update)
col2.metric("Duplicate Transaction IDs (CRM)", dup_crm)
col3.metric("Duplicate LegacyIds (Schedule)", dup_schedule)

if dup_update > 0:
    st.warning("Duplicate LegacyIds found in Update file.")
if dup_crm > 0:
    st.warning("Duplicate Transaction IDs found in CRM file.")
if dup_schedule > 0:
    st.warning("Duplicate LegacyIds found in Schedule file.")

# -----------------------------
# MAPPING
#
# Join 1: Update["LegacyId"] → CRM["Recurring Gift Transaction Id"]
#         → fills RecurringGiftId from CRM["Recurring Gift Id"]
#
# Join 2: Update["LegacyId"] → Schedule["LegacyId"]
#         → fills NewTransactionId from Schedule["Recurring Id"]
# -----------------------------

# Join 1: CRM mapping
merged = update.merge(
    crm[["Recurring Gift Transaction Id", "Recurring Gift Id"]],
    how="left",
    left_on="LegacyId",
    right_on="Recurring Gift Transaction Id"
)
merged["RecurringGiftId"] = merged["Recurring Gift Id"]
merged = merged.drop(columns=["Recurring Gift Transaction Id", "Recurring Gift Id"])

# Join 2: Schedule mapping
merged = merged.merge(
    schedule[["LegacyId", "Recurring Id"]],
    how="left",
    on="LegacyId",
    suffixes=("", "_schedule")
)
merged["NewTransactionId"] = merged["Recurring Id"]
merged = merged.drop(columns=["Recurring Id"])

merged["TransactionSource"] = "RaiseDonors"

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
missing_recurring_gift = update["RecurringGiftId"].isna().sum()
missing_new_transaction = update["NewTransactionId"].isna().sum()

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

debug_df = update[["LegacyId", "RecurringGiftId", "NewTransactionId"]].copy()

# Re-join CRM for debug visibility
debug_df = debug_df.merge(
    crm[["Recurring Gift Transaction Id", "Recurring Gift Id"]],
    how="left",
    left_on="LegacyId",
    right_on="Recurring Gift Transaction Id"
)

# Re-join Schedule for debug visibility
debug_df = debug_df.merge(
    schedule[["LegacyId", "Recurring Id"]],
    how="left",
    on="LegacyId"
)

debug_df["CRM Match"] = debug_df["RecurringGiftId"].apply(
    lambda x: "✅" if pd.notna(x) and str(x).lower() != "nan" else "❌"
)
debug_df["Schedule Match"] = debug_df["NewTransactionId"].apply(
    lambda x: "✅" if pd.notna(x) and str(x).lower() != "nan" else "❌"
)

crm_matched = (debug_df["CRM Match"] == "✅").sum()
crm_unmatched = (debug_df["CRM Match"] == "❌").sum()
sched_matched = (debug_df["Schedule Match"] == "✅").sum()
sched_unmatched = (debug_df["Schedule Match"] == "❌").sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("CRM Matched", crm_matched)
col2.metric("CRM Unmatched", crm_unmatched)
col3.metric("Schedule Matched", sched_matched)
col4.metric("Schedule Unmatched", sched_unmatched)

status_filter = st.selectbox(
    "Filter rows",
    ["All", "CRM Matched", "CRM Unmatched", "Schedule Matched", "Schedule Unmatched"]
)

if status_filter == "CRM Matched":
    filtered = debug_df[debug_df["CRM Match"] == "✅"]
elif status_filter == "CRM Unmatched":
    filtered = debug_df[debug_df["CRM Match"] == "❌"]
elif status_filter == "Schedule Matched":
    filtered = debug_df[debug_df["Schedule Match"] == "✅"]
elif status_filter == "Schedule Unmatched":
    filtered = debug_df[debug_df["Schedule Match"] == "❌"]
else:
    filtered = debug_df

st.dataframe(
    filtered[[
        "LegacyId",
        "Recurring Gift Transaction Id",
        "RecurringGiftId",
        "CRM Match",
        "Recurring Id",
        "NewTransactionId",
        "Schedule Match",
    ]],
    use_container_width=True
)

st.download_button(
    "Download Debug Report",
    filtered.to_csv(index=False).encode("utf-8"),
    "mapping_debug_report.csv"
)

# -----------------------------
# Problem Rows
# -----------------------------
def is_missing(series):
    return series.isna() | (series.astype(str).str.lower() == "nan")

problem_rows = update[is_missing(update["RecurringGiftId"]) | is_missing(update["NewTransactionId"])]

if len(problem_rows) > 0:
    st.subheader("Problem Rows")
    st.dataframe(problem_rows, use_container_width=True)
    st.download_button(
        "Download Problem Rows",
        problem_rows.to_csv(index=False).encode("utf-8"),
        "problem_rows.csv"
    )
