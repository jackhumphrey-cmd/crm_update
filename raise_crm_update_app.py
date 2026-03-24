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
#   Update["LegacyId"] → CRM["Recurring Gift Transaction Id"]
#   → pull CRM["Recurring Id"] into RecurringGiftId
#
# TransactionSource:
#   Always set to "RaiseDonors"
# -----------------------------

# Step 1: NewTransactionId = "rd2-" + LegacyId
update["NewTransactionId"] = "rd2-" + update["LegacyId"]

# Step 2: Join → CRM on LegacyId = CRM Recurring Gift Transaction Id
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
#   - Add Costs to Amount on original row
#   - Append a new split row with:
#       ProjectCode    = "CREDITCARDCOSTS"
#       ProjectName    = "Processing Fees"
#       ProjectAmount  = Costs value
# -----------------------------

def is_covers_cost(val):
    return str(val).strip().lower() == "true"

split_rows = []

for _, row in update.iterrows():
    if is_covers_cost(row.get("CoversCost", "")):
        try:
            amount = float(row["Amount"])
            costs = float(row["Costs"])
            row["Amount"] = str(round(amount + costs, 2))
        except (ValueError, TypeError):
            pass

        split_row = row.copy()
        split_row["ProjectCode"] = "CREDITCARDCOSTS"
        split_row["ProjectName"] = "Processing Fees"
        split_row["ProjectAmount"] = row["Costs"]
        split_rows.append(split_row)

# Rebuild update with modified amounts, then append split rows
if split_rows:
    split_df = pd.DataFrame(split_rows)
    output = pd.concat([update, split_df], ignore_index=True)
else:
    output = update.copy()

# Sort so split rows appear directly below their parent row
output = output.sort_values(by="TransactionId", kind="stable").reset_index(drop=True)

# -----------------------------
# Summary Metrics
# -----------------------------
def is_missing(series):
    return series.isna() | (series.astype(str).str.lower() == "nan")

missing_recurring_gift = is_missing(output["RecurringGiftId"]).sum()
missing_new_transaction = is_missing(output["NewTransactionId"]).sum()
covers_cost_count = update["CoversCost"].apply(is_covers_cost).sum()

st.subheader("Mapping Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Rows (incl. splits)", len(output))
col2.metric("Missing RecurringGiftId", missing_recurring_gift)
col3.metric("Missing NewTransactionId", missing_new_transaction)
col4.metric("CoversCost Split Rows Added", len(split_rows))

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
# 🔍 DEBUGGER PANEL
# =========================================================
st.subheader("🔍 Mapping Debugger")

debug_df = output[["TransactionId", "LegacyId", "NewTransactionId", "RecurringGiftId", "TransactionSource"]].copy()

debug_df["Schedule Match"] = debug_df["NewTransactionId"].apply(
    lambda x: "✅" if pd.notna(x) and str(x).lower() != "nan" else "❌"
)
debug_df["CRM Match"] = debug_df["RecurringGiftId"].apply(
    lambda x: "✅" if pd.notna(x) and str(x).lower() != "nan" else "❌"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("NewTransactionId Matched", (debug_df["Schedule Match"] == "✅").sum())
col2.metric("NewTransactionId Missing", (debug_df["Schedule Match"] == "❌").sum())
col3.metric("CRM Matched", (debug_df["CRM Match"] == "✅").sum())
col4.metric("CRM Unmatched", (debug_df["CRM Match"] == "❌").sum())

status_filter = st.selectbox(
    "Filter rows",
    ["All", "NewTransactionId Matched", "NewTransactionId Missing", "CRM Matched", "CRM Unmatched"]
)

if status_filter == "NewTransactionId Matched":
    filtered = debug_df[debug_df["Schedule Match"] == "✅"]
elif status_filter == "NewTransactionId Missing":
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
