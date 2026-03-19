import pandas as pd
import streamlit as st

st.title("Simple CRM Mapping Test")

update_file = st.file_uploader("Upload Update File", type=["csv"])
crm_file = st.file_uploader("Upload CRM File", type=["csv"])

if update_file and crm_file:

    update = pd.read_csv(update_file, dtype=str)
    crm = pd.read_csv(crm_file, dtype=str)

    # Clean columns
    update.columns = update.columns.str.strip()
    crm.columns = crm.columns.str.strip()

    # Normalize IDs
    update["LegacyId"] = update["LegacyId"].astype(str).str.strip()
    crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].astype(str).str.strip()

    # SIMPLE MERGE
    result = update.merge(
        crm[["Recurring Gift Transaction Id", "Recurring Gift Id"]],
        how="left",
        left_on="LegacyId",
        right_on="Recurring Gift Transaction Id"
    )

    # Output ONLY what we care about
    st.subheader("Mapping Result")

    st.dataframe(
        result[[
            "LegacyId",
            "Recurring Gift Transaction Id",
            "Recurring Gift Id"
        ]],
        use_container_width=True
    )

    # Quick success metric
    matches = result["Recurring Gift Id"].notna().sum()
    total = len(result)

    st.metric("Matches Found", f"{matches} / {total}")
