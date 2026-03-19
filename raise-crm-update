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
schedule_file = st.sidebar.file_uploader("Schedule File", type=["csv"])
crm_file = st.sidebar.file_uploader("CRM Export", type=["csv"])
raise_file = st.sidebar.file_uploader("Raise Recurring Export", type=["csv"])

if not update_file or not schedule_file or not crm_file or not raise_file:
    st.warning("Please upload all four files.")
    st.stop()

# -----------------------------
# Load Files
# -----------------------------
update = pd.read_csv(update_file, dtype=str)
schedule = pd.read_csv(schedule_file, dtype=str)
crm = pd.read_csv(crm_file, dtype=str)
raise_df = pd.read_csv(raise_file, dtype=str)

# -----------------------------
# Normalize columns
# -----------------------------
update.columns = update.columns.str.strip()
schedule.columns = schedule.columns.str.strip()
crm.columns = crm.columns.str.strip()
raise_df.columns = raise_df.columns.str.strip()

# -----------------------------
# Validate required columns
# -----------------------------
required_update = ["LegacyId", "Amount", "CoversCost", "Costs"]
required_crm = ["Recurring Gift Transaction Id"]
required_raise = ["Profile Number", "Id"]

for col in required_update:
    if col not in update.columns:
        st.error(f"Update file missing column: {col}")
        st.stop()

for col in required_crm:
    if col not in crm.columns:
        st.error(f"CRM file missing column: {col}")
        st.stop()

for col in required_raise:
    if col not in raise_df.columns:
        st.error(f"Raise file missing column: {col}")
        st.stop()

# -----------------------------
# Normalize key fields
# -----------------------------
update["LegacyId"] = update["LegacyId"].astype(str).str.strip()

crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].astype(str).str.strip()

raise_df["Profile Number"] = raise_df["Profile Number"].astype(str).str.strip()
raise_df["Id"] = raise_df["Id"].astype(str).str.strip()

# -----------------------------
# STEP 1: CRM lookup
# LegacyId -> Recurring Gift Transaction Id
# -----------------------------
crm_lookup = crm.drop_duplicates("Recurring Gift Transaction Id")
crm_lookup = crm_lookup.set_index("Recurring Gift Transaction Id").index.to_series()

# This basically validates existence — keeps your original logic intact
update["Recurring Gift Transaction Id"] = update["LegacyId"].map(crm_lookup)

# -----------------------------
# STEP 2: Raise lookup
# Profile Number -> Id
# -----------------------------
raise_lookup = (
    raise_df.drop_duplicates("Profile Number")
    .set_index("Profile Number")["Id"]
)

# -----------------------------
# STEP 3: Populate NewTransactionId
# -----------------------------
update["NewTransactionId"] = update["Recurring Gift Transaction Id"].map(raise_lookup)

# -----------------------------
# Transaction Source update
# -----------------------------
update["TransactionSource"] = "RaiseDonors"

# -----------------------------
# CoversCost Logic
# -----------------------------
update["CoversCost"] = update["CoversCost"].astype(str).str.lower() == "true"
update["Amount"] = pd.to_numeric(update["Amount"], errors="coerce").fillna(0)
update["Costs"] = pd.to_numeric(update["Costs"], errors="coerce").fillna(0)

# Add costs to Amount where applicable
mask = update["CoversCost"]

update.loc[mask, "Amount"] = update.loc[mask, "Amount"] + update.loc[mask, "Costs"]

# -----------------------------
# Add CREDITCARDCOSTS split
# -----------------------------
# Find next available Project slot
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
missing_txn = update["NewTransactionId"].isna().sum()

col1, col2 = st.columns(2)
col1.metric("Total Rows", len(update))
col2.metric("Missing NewTransactionId", missing_txn)

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
problem_rows = update[update["NewTransactionId"].isna()]

if len(problem_rows) > 0:
    st.subheader("Problem Rows")
    problem_csv = problem_rows.to_csv(index=False).encode("utf-8")
    st.download_button("Download Problem Rows", problem_csv, "problem_rows.csv")
