import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="🔄 CRM Update Builder v2",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 CRM Update Builder v2")

# -----------------------------
# Uploads
# -----------------------------
update_file = st.sidebar.file_uploader("Update Template", type=["csv"])
crm_file = st.sidebar.file_uploader("CRM Export", type=["csv"])

if not update_file or not crm_file:
    st.warning("Please upload both files: Update Template and CRM Export.")
    st.stop()

# -----------------------------
# Load Files
# -----------------------------
update = pd.read_csv(update_file, dtype=str)
crm = pd.read_csv(crm_file, dtype=str)

update.columns = update.columns.str.strip()
crm.columns = crm.columns.str.strip()

# -----------------------------
# Validate required columns
# -----------------------------
required_update = ["TransactionId", "LegacyId", "Amount", "Costs", "CoversCost", "TransactionSource"]
required_crm = ["Recurring Gift Transaction Id", "Recurring Id"]

for col in required_update:
    if col not in update.columns:
        st.error(f"Update file missing column: {col}")
        st.stop()

for col in required_crm:
    if col not in crm.columns:
        st.error(f"CRM file missing column: {col}")
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

# -----------------------------
# Data Integrity Checks
# -----------------------------
dup_update = update["TransactionId"].duplicated().sum()
dup_crm = crm["Recurring Gift Transaction Id"].duplicated().sum()

st.subheader("Data Integrity Checks")

col1, col2 = st.columns(2)
col1.metric("Duplicate TransactionIds (Update)", dup_update)
col2.metric("Duplicate Transaction IDs (CRM)", dup_crm)

if dup_update > 0:
    st.warning("Duplicate TransactionIds found in Update file.")
if dup_crm > 0:
    st.warning("Duplicate Transaction IDs found in CRM file.")

# -----------------------------
# MAPPING
#
# NewTransactionId:
#   "rd2-" + Update["LegacyId"]
#
# RecurringGiftId:
#   Update["LegacyId"] -> CRM["Recurring Gift Transaction Id"]
#   -> pull CRM["Recurring Id"] into RecurringGiftId
#
# TransactionSource:
#   Always set to "RaiseDonors"
# -----------------------------

# Step 1: NewTransactionId = "rd2-" + LegacyId
update["NewTransactionId"] = "rd2-" + update["LegacyId"]

# Step 2: Join -> CRM on LegacyId = CRM Recurring Gift Transaction Id
crm_slim = crm[["Recurring Gift Transaction Id", "Recurring Id"]].rename(columns={
    "Recurring Id": "CRM_RecurringId"
})

update = update.merge(crm_slim, how="left", left_on="LegacyId", right_on="Recurring Gift Transaction Id")

# RecurringGiftId comes from CRM["Recurring Id"]
update["RecurringGiftId"] = update["CRM_RecurringId"]

# Drop helper columns
update = update.drop(columns=["Recurring Gift Transaction Id", "CRM_RecurringId"], errors="ignore")

# Step 3: Set TransactionSource to RaiseDonors
update["TransactionSource"] = "RaiseDonors"

# -----------------------------
# CoversCost Project Split
#
# For rows where CoversCost == "True":
#   - Add Costs to Amount on the original row
#   - Find the next available ProjectN slot (Code/Name/Amount all blank)
#     and fill in CREDITCARDCOSTS / Processing Fees / Costs value
# -----------------------------

def is_covers_cost(val):
    return str(val).strip().lower() == "true"

def is_blank(val):
    return pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() == "nan"

def find_next_project_slot(row, columns):
    """Return the lowest N where ProjectNCode, ProjectNName, ProjectNAmount are all blank."""
    i = 1
    while True:
        code_col = f"Project{i}Code"
        name_col = f"Project{i}Name"
        amt_col  = f"Project{i}Amount"
        # If none of these columns exist in the file, there are no more slots
        if code_col not in columns and name_col not in columns and amt_col not in columns:
            return None
        if is_blank(row.get(code_col, "")) and is_blank(row.get(name_col, "")) and is_blank(row.get(amt_col, "")):
            return i
        i += 1

output = update.copy()
covers_cost_count = 0

for idx, row in output.iterrows():
    if is_covers_cost(row.get("CoversCost", "")):
        # Add Costs to Amount on original row
        try:
            amount = float(row["Amount"])
            costs  = float(row["Costs"])
            output.at[idx, "Amount"] = str(round(amount + costs, 2))
        except (ValueError, TypeError):
            pass

        # Find next available project slot and write split values in-place
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
st.download_button("Download Updated File", csv, "crm_updates_v2.csv")

# =========================================================
# DEBUGGER PANEL
# =========================================================
st.subheader("🔍 Mapping Debugger")

debug_df = output[["TransactionId", "LegacyId", "NewTransactionId", "RecurringGiftId", "TransactionSource"]].copy()

debug_df["NewTxn Match"] = debug_df["NewTransactionId"].apply(
    lambda x: "✅" if pd.notna(x) and str(x).lower() != "nan" else "❌"
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
    "mapping_debug_report_v2.csv"
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
        "problem_rows_v2.csv"
    )
