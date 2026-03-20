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
update_file = st.file_uploader("Upload Update Template", type=["csv"])
crm_file = st.file_uploader("Upload CRM Export", type=["csv"])

if not update_file or not crm_file:
    st.warning("Please upload both files.")
    st.stop()

# -----------------------------
# Load Files
# -----------------------------
update = pd.read_csv(update_file, dtype=str)
crm = pd.read_csv(crm_file, dtype=str)

# -----------------------------
# Clean column names
# -----------------------------
update.columns = update.columns.str.strip()
crm.columns = crm.columns.str.strip()

# -----------------------------
# Validate required columns
# -----------------------------
required_update_cols = ["LegacyId", "Amount", "CoversCost", "Costs"]
required_crm_cols = ["Recurring Gift Transaction Id", "Recurring Gift Id"]

for col in required_update_cols:
    if col not in update.columns:
        st.error(f"Update file missing column: {col}")
        st.stop()

for col in required_crm_cols:
    if col not in crm.columns:
        st.error(f"CRM file missing column: {col}")
        st.stop()

# -----------------------------
# Clean ID values
# -----------------------------
def clean(x):
    return str(x).strip().replace(".0", "")

update["LegacyId"] = update["LegacyId"].apply(clean)
crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].apply(clean)

# -----------------------------
# CRM lookup table
# -----------------------------
crm_map = crm[
    ["Recurring Gift Transaction Id", "Recurring Gift Id"]
].drop_duplicates()

# -----------------------------
# Merge (CORE LOGIC)
# -----------------------------
update = update.merge(
    crm_map,
    how="left",
    left_on="LegacyId",
    right_on="Recurring Gift Transaction Id"
)

# -----------------------------
# Populate fields
# -----------------------------
update["RecurringId"] = update["Recurring Gift Id"]
update["NewTransactionId"] = "rd2-" + update["LegacyId"]
update["TransactionSource"] = "RaiseDonors"

# -----------------------------
# Drop helper columns
# -----------------------------
update = update.drop(columns=["Recurring Gift Transaction Id", "Recurring Gift Id"])

# -----------------------------
# CoversCost logic
# -----------------------------
update["CoversCost"] = update["CoversCost"].astype(str).str.lower() == "true"
update["Amount"] = pd.to_numeric(update["Amount"], errors="coerce").fillna(0)
update["Costs"] = pd.to_numeric(update["Costs"], errors="coerce").fillna(0)

mask = update["CoversCost"]

# Add Costs into Amount when applicable
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
# Summary
# -----------------------------
st.subheader("Mapping Summary")

matched = update["RecurringId"].notna().sum()
total = len(update)

col1, col2 = st.columns(2)
col1.metric("Total Rows", total)
col2.metric("Matched RecurringIds", f"{matched} / {total}")

# -----------------------------
# Preview
# -----------------------------
st.subheader("Output Preview")
st.dataframe(update, use_container_width=True)

# -----------------------------
# Download
# -----------------------------
csv = update.to_csv(index=False).encode("utf-8")
st.download_button("Download Output CSV", csv, "crm_updates.csv")

# -----------------------------
# Debug Panel
# -----------------------------
st.subheader("🔍 Mapping Debugger")

debug = update.copy()

debug["MatchStatus"] = debug["RecurringId"].apply(
    lambda x: "Matched" if pd.notna(x) else "No Match"
)

filter_option = st.selectbox("Filter Rows", ["All", "Matched", "No Match"])

if filter_option == "Matched":
    debug = debug[debug["MatchStatus"] == "Matched"]
elif filter_option == "No Match":
    debug = debug[debug["MatchStatus"] == "No Match"]

st.dataframe(
    debug[
        [
            "LegacyId",
            "RecurringId",
            "NewTransactionId",
            "MatchStatus"
        ]
    ],
    use_container_width=True
)

st.download_button(
    "Download Debug Report",
    debug.to_csv(index=False).encode("utf-8"),
    "debug_report.csv"
)
