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

if not update_file or not crm_file:
    st.warning("Please upload both files.")
    st.stop()

# -----------------------------
# Load Files
# -----------------------------
update = pd.read_csv(update_file, dtype=str)
crm = pd.read_csv(crm_file, dtype=str)

# -----------------------------
# Normalize columns
# -----------------------------
update.columns = update.columns.str.strip()
crm.columns = crm.columns.str.strip()

# -----------------------------
# Validate columns
# -----------------------------
required_update = ["LegacyId", "Amount", "CoversCost", "Costs"]
required_crm = ["Recurring Gift Transaction Id", "Recurring Gift Id"]

for col in required_update:
    if col not in update.columns:
        st.error(f"Update file missing column: {col}")
        st.stop()

for col in required_crm:
    if col not in crm.columns:
        st.error(f"CRM file missing column: {col}")
        st.stop()

# -----------------------------
# Normalize keys
# -----------------------------
update["LegacyId"] = update["LegacyId"].astype(str).str.strip()

crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].astype(str).str.strip()
crm["Recurring Gift Id"] = crm["Recurring Gift Id"].astype(str).str.strip()

# -----------------------------
# 🚨 DUPLICATE DETECTION
# -----------------------------
dup_update = update["LegacyId"].duplicated().sum()
dup_crm = crm["Recurring Gift Transaction Id"].duplicated().sum()

st.subheader("Data Integrity Checks")

col1, col2 = st.columns(2)
col1.metric("Duplicate LegacyIds (Update)", dup_update)
col2.metric("Duplicate Transaction IDs (CRM)", dup_crm)

if dup_update > 0:
    st.warning("Update file contains duplicate LegacyIds — mapping may be unreliable")

if dup_crm > 0:
    st.warning("CRM file contains duplicate Transaction IDs — using first match only")

# Optional: download duplicates
dup_rows = update[update["LegacyId"].duplicated(keep=False)]
if len(dup_rows) > 0:
    st.download_button(
        "Download Duplicate Update Rows",
        dup_rows.to_csv(index=False).encode("utf-8"),
        "duplicate_update_rows.csv"
    )

# -----------------------------
# Build CRM lookup (SAFE)
# -----------------------------
crm_lookup = (
    crm.drop_duplicates("Recurring Gift Transaction Id")
    .set_index("Recurring Gift Transaction Id")
)

# -----------------------------
# Map RecurringId
# -----------------------------
update["RecurringId"] = update["LegacyId"].map(
    crm_lookup["Recurring Gift Id"]
)

# -----------------------------
# Safer NewTransactionId
# -----------------------------
update["MatchedTransactionId"] = update["LegacyId"].map(
    crm_lookup.index.to_series()
)

update["NewTransactionId"] = update["MatchedTransactionId"].apply(
    lambda x: f"rd2-{x}" if pd.notna(x) else None
)

# -----------------------------
# Transaction Source
# -----------------------------
update["TransactionSource"] = "RaiseDonors"

# -----------------------------
# CoversCost Logic
# -----------------------------
update["CoversCost"] = update["CoversCost"].astype(str).str.lower() == "true"
update["Amount"] = pd.to_numeric(update["Amount"], errors="coerce").fillna(0)
update["Costs"] = pd.to_numeric(update["Costs"], errors="coerce").fillna(0)

mask = update["CoversCost"]

# Add Costs into Amount
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
# Metrics
# -----------------------------
missing_recurring = update["RecurringId"].isna().sum()
missing_txn = update["NewTransactionId"].isna().sum()

st.subheader("Mapping Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Rows", len(update))
col2.metric("Missing RecurringId", missing_recurring)
col3.metric("Missing NewTransactionId", missing_txn)

# -----------------------------
# Preview
# -----------------------------
st.dataframe(update, use_container_width=True)

# -----------------------------
# Download
# -----------------------------
csv = update.to_csv(index=False).encode("utf-8")
st.download_button("Download Updated File", csv, "crm_updates.csv")

# -----------------------------
# Problem Rows
# -----------------------------
problem_rows = update[
    (update["RecurringId"].isna()) |
    (update["NewTransactionId"].isna())
]

if len(problem_rows) > 0:
    st.subheader("Problem Rows")
    st.download_button(
        "Download Problem Rows",
        problem_rows.to_csv(index=False).encode("utf-8"),
        "problem_rows.csv"
    )
