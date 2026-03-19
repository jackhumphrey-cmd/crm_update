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
# Validate required columns
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
# Normalize IDs (IMPORTANT)
# -----------------------------
def normalize(val):
    return str(val).strip().replace(".0", "")

update["LegacyId"] = update["LegacyId"].apply(normalize)
crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].apply(normalize)
crm["Recurring Gift Id"] = crm["Recurring Gift Id"].astype(str).str.strip()

# -----------------------------
# Data Integrity Checks
# -----------------------------
dup_update = update["LegacyId"].duplicated().sum()
dup_crm = crm["Recurring Gift Transaction Id"].duplicated().sum()

st.subheader("Data Integrity Checks")

col1, col2 = st.columns(2)
col1.metric("Duplicate LegacyIds (Update)", dup_update)
col2.metric("Duplicate Transaction IDs (CRM)", dup_crm)

if dup_update > 0:
    st.warning("Duplicate LegacyIds found in Update file.")

if dup_crm > 0:
    st.warning("Duplicate Transaction IDs found in CRM file.")

# -----------------------------
# 🔥 MERGE-BASED MAPPING (FIXED)
# -----------------------------
merged = update.merge(
    crm[["Recurring Gift Transaction Id", "Recurring Gift Id"]],
    how="left",
    left_on="LegacyId",
    right_on="Recurring Gift Transaction Id"
)

# Populate fields
merged["RecurringId"] = merged["Recurring Gift Id"]
merged["NewTransactionId"] = merged["LegacyId"].apply(
    lambda x: f"rd2-{x}" if pd.notna(x) else None
)
merged["TransactionSource"] = "RaiseDonors"

# Drop helper columns
merged = merged.drop(columns=["Recurring Gift Transaction Id", "Recurring Gift Id"])

# Replace working dataframe
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
missing_recurring = update["RecurringId"].isna().sum()

st.subheader("Mapping Summary")

col1, col2 = st.columns(2)
col1.metric("Total Rows", len(update))
col2.metric("Missing RecurringId", missing_recurring)

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
# 🔍 DEBUGGER PANEL (UNCHANGED BUT NOW MORE POWERFUL)
# =========================================================
st.subheader("🔍 Mapping Debugger")

debug_df = update.merge(
    crm[["Recurring Gift Transaction Id", "Recurring Gift Id"]],
    how="left",
    left_on="LegacyId",
    right_on="Recurring Gift Transaction Id"
)

debug_df["MatchStatus"] = debug_df["Recurring Gift Id"].apply(
    lambda x: "Matched" if pd.notna(x) else "No Match"
)

col1, col2 = st.columns(2)
col1.metric("Matched Rows", (debug_df["MatchStatus"] == "Matched").sum())
col2.metric("Unmatched Rows", (debug_df["MatchStatus"] == "No Match").sum())

status_filter = st.selectbox(
    "Filter rows",
    ["All", "Matched", "No Match"]
)

if status_filter == "Matched":
    filtered = debug_df[debug_df["MatchStatus"] == "Matched"]
elif status_filter == "No Match":
    filtered = debug_df[debug_df["MatchStatus"] == "No Match"]
else:
    filtered = debug_df

st.dataframe(
    filtered[
        [
            "LegacyId",
            "Recurring Gift Transaction Id",
            "Recurring Gift Id",
            "MatchStatus"
        ]
    ],
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
problem_rows = update[update["RecurringId"].isna()]

if len(problem_rows) > 0:
    st.subheader("Problem Rows")
    st.download_button(
        "Download Problem Rows",
        problem_rows.to_csv(index=False).encode("utf-8"),
        "problem_rows.csv"
    )
