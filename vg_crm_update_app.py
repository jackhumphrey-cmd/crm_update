import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="🔄 Recurring Gift Update Builder",
    page_icon="🔄",
    layout="wide"
)

st.title("VG CRM Update Builder")

# -----------------------------
# Uploads
# -----------------------------
update_file = st.sidebar.file_uploader("Update Template", type=["csv"])
schedule_file = st.sidebar.file_uploader("Schedule File", type=["csv"])
crm_file = st.sidebar.file_uploader("CRM Export", type=["csv"])

if not update_file or not schedule_file or not crm_file:
    st.warning("Please upload all three files.")
    st.stop()

# -----------------------------
# Load Files (lightweight)
# -----------------------------
update = pd.read_csv(update_file, dtype=str)
schedule = pd.read_csv(schedule_file, dtype=str)
crm = pd.read_csv(crm_file, dtype=str)

# -----------------------------
# Column Validation (prevents crashes)
# -----------------------------
required_update = ["LegacyId"]
required_crm = ["Recurring Gift Transaction Id", "Recurring Gift Id"]
required_schedule = ["LegacyId", "RecurringId"]

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
# Normalize keys
# -----------------------------
update["LegacyId"] = update["LegacyId"].str.strip()
crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].str.strip()
crm["Recurring Gift Id"] = crm["Recurring Gift Id"].str.strip()
schedule["LegacyId"] = schedule["LegacyId"].str.strip()
schedule["RecurringId"] = schedule["RecurringId"].str.strip()

# -----------------------------
# Build lookup dictionaries (FAST + SAFE)
# -----------------------------

# CRM: LegacyId -> RecurringId
crm_lookup = (
    crm.drop_duplicates("Recurring Gift Transaction Id")
    .set_index("Recurring Gift Transaction Id")["Recurring Gift Id"]
)

# Schedule: LegacyId -> RecurringId (for NewTransactionId)
schedule_lookup = (
    schedule.drop_duplicates("LegacyId")
    .set_index("LegacyId")["RecurringId"]
)

# -----------------------------
# Apply mappings (NO MERGE = NO CRASH)
# -----------------------------
update["RecurringId"] = update["LegacyId"].map(crm_lookup)
update["NewTransactionId"] = update["LegacyId"].map(schedule_lookup)

# -----------------------------
# Metrics
# -----------------------------
missing_recurring = update["RecurringId"].isna().sum()
missing_new_txn = update["NewTransactionId"].isna().sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Rows", len(update))
col2.metric("Missing RecurringId", missing_recurring)
col3.metric("Missing NewTransactionId", missing_new_txn)

# -----------------------------
# Preview
# -----------------------------
st.dataframe(update, use_container_width=True)

# -----------------------------
# Download
# -----------------------------
csv = update.to_csv(index=False).encode("utf-8")
st.download_button("Download Updated File", csv, "updated_file.csv")

# -----------------------------
# Problem Rows
# -----------------------------
problem_rows = update[
    (update["RecurringId"].isna()) |
    (update["NewTransactionId"].isna())
]

if len(problem_rows) > 0:
    st.subheader("Problem Rows")
    problem_csv = problem_rows.to_csv(index=False).encode("utf-8")
    st.download_button("Download Problem Rows", problem_csv, "problem_rows.csv")
