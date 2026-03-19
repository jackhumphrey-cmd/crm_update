import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="🔄 Recurring Gift Update Builder",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Recurring Gift Update Builder")
st.markdown("Populate update templates using CRM exports and schedule data.")

# -----------------------------
# File Uploads
# -----------------------------
st.sidebar.header("Upload Files")
update_file = st.sidebar.file_uploader("Update Template", type=["csv"])
schedule_file = st.sidebar.file_uploader("Schedule File", type=["csv"])
crm_file = st.sidebar.file_uploader("CRM Export", type=["csv"])

if not update_file or not schedule_file or not crm_file:
    st.sidebar.warning("Please upload all three files.")

if update_file and schedule_file and crm_file:

    with st.spinner("Processing..."):

        # -----------------------------
        # Load Files
        # -----------------------------
        update = pd.read_csv(update_file)
        schedule = pd.read_csv(schedule_file)
        crm = pd.read_csv(crm_file)

        # -----------------------------
        # Normalize key fields
        # -----------------------------
        update["LegacyId"] = update["LegacyId"].astype(str).str.strip()

        crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].astype(str).str.strip()
        crm["Recurring Gift Id"] = crm["Recurring Gift Id"].astype(str).str.strip()

        schedule["LegacyId"] = schedule["LegacyId"].astype(str).str.strip()
        schedule["RecurringId"] = schedule["RecurringId"].astype(str).str.strip()

        # -----------------------------
        # STEP 1: CRM → Update
        # Populate RecurringId
        # -----------------------------
        crm_subset = crm[[
            "Recurring Gift Transaction Id",
            "Recurring Gift Id"
        ]].drop_duplicates()

        crm_subset = crm_subset.rename(columns={
            "Recurring Gift Transaction Id": "LegacyId",
            "Recurring Gift Id": "RecurringId"
        })

        update = update.merge(
            crm_subset,
            on="LegacyId",
            how="left"
        )

        # -----------------------------
        # STEP 2: Schedule → Update
        # Populate NewTransactionId
        # -----------------------------
        schedule_subset = schedule[[
            "LegacyId",
            "RecurringId"
        ]].drop_duplicates()

        schedule_subset = schedule_subset.rename(columns={
            "RecurringId": "NewTransactionId"
        })

        update = update.merge(
            schedule_subset,
            on="LegacyId",
            how="left"
        )

        # -----------------------------
        # Data Quality Checks
        # -----------------------------
        missing_recurring = update["RecurringId"].isna().sum()
        missing_new_txn = update["NewTransactionId"].isna().sum()

    # -----------------------------
    # Dashboard
    # -----------------------------
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rows", len(update))
    col2.metric("Missing RecurringId (CRM)", missing_recurring)
    col3.metric("Missing NewTransactionId (Schedule)", missing_new_txn)

    # -----------------------------
    # Preview
    # -----------------------------
    st.subheader("Preview")
    st.dataframe(update, use_container_width=True)

    # -----------------------------
    # Download
    # -----------------------------
    csv = update.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Updated File",
        csv,
        "recurring_updates.csv",
        "text/csv"
    )

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
        st.download_button(
            "Download Problem Rows",
            problem_csv,
            "problem_rows.csv",
            "text/csv"
        )
