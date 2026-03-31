import pandas as pd
import streamlit as st
import re

st.set_page_config(
    page_title="Migration QA Review",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #f0f7fb;
    background-image:
        radial-gradient(ellipse 70% 40% at 55% 0%, rgba(26,140,181,0.18) 0%, transparent 65%),
        radial-gradient(ellipse 40% 30% at 5% 95%, rgba(11,126,163,0.1) 0%, transparent 60%);
}

#MainMenu, footer, header { visibility: hidden; }

.page-header { padding: 1.8rem 0 0.5rem; }
.page-badge {
    display: inline-block;
    background: rgba(11,126,163,0.1);
    border: 1px solid rgba(11,126,163,0.25);
    color: #0b7ea3;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    margin-bottom: 0.9rem;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #0d2d3d;
    letter-spacing: -0.03em;
    margin: 0 0 0.4rem;
    line-height: 1.15;
}
.page-title span {
    background: linear-gradient(135deg, #0b7ea3 0%, #1ab5d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.page-sub {
    font-size: 0.88rem;
    color: #6a8fa0;
    font-weight: 300;
    margin: 0 0 1.5rem;
}

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid rgba(11,126,163,0.1) !important;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown p { color: #0d2d3d !important; }
[data-testid="stSidebarHeader"] { display: none; }

[data-testid="stFileUploader"] {
    border: 1px solid rgba(11,126,163,0.2) !important;
    border-radius: 12px !important;
    padding: 0.5rem 0.75rem !important;
    background: rgba(240,247,251,0.6) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(11,126,163,0.4) !important;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid rgba(11,126,163,0.1);
    border-radius: 14px;
    padding: 1.4rem 1.6rem !important;
    box-shadow: 0 1px 3px rgba(11,126,163,0.05), 0 4px 12px rgba(11,126,163,0.06);
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: #7aaabb !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.35 !important;
    margin-bottom: 0.4rem !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #0d2d3d !important;
}

h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #0d2d3d !important;
    letter-spacing: -0.02em !important;
}

[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-color: #0b7ea3 !important;
}

.stDownloadButton button, .stButton button {
    background: linear-gradient(135deg, #0b7ea3 0%, #1a8cb5 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.2rem !important;
    box-shadow: 0 2px 8px rgba(11,126,163,0.28) !important;
    transition: opacity 0.2s !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    opacity: 0.88 !important;
    box-shadow: 0 4px 14px rgba(11,126,163,0.38) !important;
}

[data-testid="stSelectbox"] > div > div {
    border-color: rgba(11,126,163,0.25) !important;
    border-radius: 9px !important;
}

[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid rgba(11,126,163,0.1) !important;
    box-shadow: 0 1px 3px rgba(11,126,163,0.04) !important;
}

.stSpinner > div { border-top-color: #0b7ea3 !important; }

.hub-footer {
    text-align: center;
    margin-top: 2.5rem;
    font-size: 0.71rem;
    color: #a8c8d8;
    letter-spacing: 0.04em;
}

/* ── QA check section cards ── */
.check-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: #0d2d3d;
    letter-spacing: -0.01em;
    margin: 0.2rem 0 0.1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div class="page-badge">LRD Internal Tools</div>
    <h1 class="page-title">Migration <span>QA Review</span></h1>
    <p class="page-sub">Upload a migration file to run automated quality assurance checks before import.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Upload
# -----------------------------
migration_file = st.sidebar.file_uploader("Migration File (CSV)", type=["csv"])

if not migration_file:
    st.warning("Please upload a migration file to begin.")
    st.stop()

# -----------------------------
# Load
# -----------------------------
df = pd.read_csv(migration_file, dtype=str)
df.columns = df.columns.str.strip()

st.sidebar.success(f"{len(df)} rows loaded")

# -----------------------------
# Detect project split columns dynamically
# -----------------------------
project_amount_cols = sorted(
    [c for c in df.columns if re.match(r"Project\d+Amount", c)],
    key=lambda x: int(re.search(r"\d+", x).group())
)
project_code_cols = sorted(
    [c for c in df.columns if re.match(r"Project\d+Code", c)],
    key=lambda x: int(re.search(r"\d+", x).group())
)
project_name_cols = sorted(
    [c for c in df.columns if re.match(r"Project\d+Name", c)],
    key=lambda x: int(re.search(r"\d+", x).group())
)

# -----------------------------
# Helper
# -----------------------------
def is_blank(val):
    return pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() in ("nan", "none")

# =====================================================================
# QA CHECKS
# =====================================================================

# -- 1. Required fields missing --
required_fields = [
    "FirstName", "LastName", "Email", "PaymentMethodType",
    "PaymentMethodId", "Amount", "Frequency", "NextPaymentDate",
    "CustomerId", "Project1Code", "Project1Name", "Project1Amount"
]

missing_flags = {}
for field in required_fields:
    if field in df.columns:
        missing_flags[field] = df[field].apply(is_blank)
    else:
        missing_flags[field] = pd.Series([True] * len(df))

df["_missing_required"] = pd.DataFrame(missing_flags).any(axis=1)
missing_required_details = {f: missing_flags[f].sum() for f in required_fields if missing_flags[f].sum() > 0}

# -- 2. Project split amounts must equal Amount --
def check_split_mismatch(row):
    try:
        total = float(row["Amount"])
        split_sum = sum(
            float(row[c]) for c in project_amount_cols
            if c in row and not is_blank(row[c])
        )
        return abs(total - round(split_sum, 2)) > 0.01
    except (ValueError, TypeError):
        return False

df["_split_mismatch"] = df.apply(check_split_mismatch, axis=1)

# -- 3. #N/A in PaymentMethodId or CustomerId --
def has_na_error(val):
    return str(val).strip().upper() == "#N/A"

df["_payment_id_na"] = df["PaymentMethodId"].apply(has_na_error) if "PaymentMethodId" in df.columns else False
df["_customer_id_na"] = df["CustomerId"].apply(has_na_error) if "CustomerId" in df.columns else False
df["_id_na_error"] = df["_payment_id_na"] | df["_customer_id_na"]

# -- 4. PaymentMethodType must be Credit or ACH --
valid_payment_types = {"Credit", "ACH"}
df["_invalid_payment_type"] = df["PaymentMethodType"].apply(
    lambda x: str(x).strip() not in valid_payment_types if not is_blank(x) else False
) if "PaymentMethodType" in df.columns else False

# -- 5. NextPaymentDate format MM/DD/YYYY (no timestamps) --
date_pattern = re.compile(r"^\d{2}/\d{2}/\d{4}$")
df["_bad_date_format"] = df["NextPaymentDate"].apply(
    lambda x: not bool(date_pattern.match(str(x).strip())) if not is_blank(x) else False
) if "NextPaymentDate" in df.columns else False

# -- 6. Multiple names in FirstName (&  or ' and ') --
multi_name_pattern = re.compile(r"&| and ", re.IGNORECASE)
df["_multi_name"] = df["FirstName"].apply(
    lambda x: bool(multi_name_pattern.search(str(x))) if not is_blank(x) else False
) if "FirstName" in df.columns else False

# -- Overall flag --
flag_cols = [
    "_missing_required", "_split_mismatch", "_id_na_error",
    "_invalid_payment_type", "_bad_date_format", "_multi_name"
]
df["_any_issue"] = df[flag_cols].any(axis=1)
total_issues = df["_any_issue"].sum()

# =====================================================================
# SUMMARY DASHBOARD
# =====================================================================
st.subheader("QA Summary")

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Rows", len(df))
col2.metric("Rows with Issues", int(total_issues))
col3.metric("Missing Required Fields", int(df["_missing_required"].sum()))
col4.metric("Split Amount Mismatches", int(df["_split_mismatch"].sum()))
col5.metric("ID Mapping Errors (#N/A)", int(df["_id_na_error"].sum()))
col6.metric("Invalid Payment Types", int(df["_invalid_payment_type"].sum()))

col1b, col2b = st.columns(2)
col1b.metric("Bad Date Formats", int(df["_bad_date_format"].sum()))
col2b.metric("Multiple Names in FirstName", int(df["_multi_name"].sum()))

# Overall status
if total_issues == 0:
    st.success("✅ All checks passed — this file looks good to import!")
else:
    st.error(f"⚠️ {int(total_issues)} row(s) flagged across one or more checks. Review the details below.")

# =====================================================================
# INDIVIDUAL CHECK DETAILS
# =====================================================================
st.subheader("Check Details")

# -- 1. Missing required fields --
with st.expander(f"① Missing Required Fields — {int(df['_missing_required'].sum())} row(s)"):
    if missing_required_details:
        for field, count in missing_required_details.items():
            st.warning(f"**{field}**: {count} missing value(s)")
        problem = df[df["_missing_required"]][[c for c in ["FirstName","LastName","Email","PaymentMethodType",
            "PaymentMethodId","Amount","Frequency","NextPaymentDate",
            "CustomerId","Project1Code","Project1Name","Project1Amount",
            "LegacyId"] if c in df.columns]]
        st.dataframe(problem, use_container_width=True)
        st.download_button("Download Rows", problem.to_csv(index=False).encode(), "qa_missing_fields.csv")
    else:
        st.success("No missing required fields.")

# -- 2. Split mismatches --
with st.expander(f"② Project Split Amount Mismatches — {int(df['_split_mismatch'].sum())} row(s)"):
    if df["_split_mismatch"].sum() > 0:
        cols_to_show = (["FirstName", "LastName", "LegacyId", "Amount"] +
                        project_amount_cols + ["_split_mismatch"])
        problem = df[df["_split_mismatch"]][[c for c in cols_to_show if c in df.columns]].copy()
        problem["SplitSum"] = problem[[c for c in project_amount_cols if c in problem.columns]].apply(
            pd.to_numeric, errors="coerce").sum(axis=1).round(2)
        problem["Discrepancy"] = (
            pd.to_numeric(problem["Amount"], errors="coerce") - problem["SplitSum"]
        ).round(2)
        st.dataframe(problem, use_container_width=True)
        st.download_button("Download Rows", problem.to_csv(index=False).encode(), "qa_split_mismatch.csv")
    else:
        st.success("All project splits match their schedule amounts.")

# -- 3. #N/A ID errors --
with st.expander(f"③ ID Mapping Errors (#N/A) — {int(df['_id_na_error'].sum())} row(s)"):
    if df["_id_na_error"].sum() > 0:
        problem = df[df["_id_na_error"]][[c for c in
            ["FirstName","LastName","LegacyId","PaymentMethodId","CustomerId"] if c in df.columns]]
        st.warning(f"PaymentMethodId errors: {int(df['_payment_id_na'].sum())}  |  CustomerId errors: {int(df['_customer_id_na'].sum())}")
        st.dataframe(problem, use_container_width=True)
        st.download_button("Download Rows", problem.to_csv(index=False).encode(), "qa_id_errors.csv")
    else:
        st.success("No #N/A mapping errors found.")

# -- 4. Invalid payment types --
with st.expander(f"④ Invalid PaymentMethodType Values — {int(df['_invalid_payment_type'].sum())} row(s)"):
    if df["_invalid_payment_type"].sum() > 0:
        problem = df[df["_invalid_payment_type"]][[c for c in
            ["FirstName","LastName","LegacyId","PaymentMethodType"] if c in df.columns]]
        st.warning("Expected values: **Credit** or **ACH** only.")
        st.dataframe(problem, use_container_width=True)
        st.download_button("Download Rows", problem.to_csv(index=False).encode(), "qa_payment_type.csv")
    else:
        st.success("All PaymentMethodType values are valid.")

# -- 5. Bad date formats --
with st.expander(f"⑤ Invalid NextPaymentDate Format — {int(df['_bad_date_format'].sum())} row(s)"):
    if df["_bad_date_format"].sum() > 0:
        problem = df[df["_bad_date_format"]][[c for c in
            ["FirstName","LastName","LegacyId","NextPaymentDate"] if c in df.columns]]
        st.warning("Expected format: **MM/DD/YYYY** — timestamps or other formats are not accepted.")
        st.dataframe(problem, use_container_width=True)
        st.download_button("Download Rows", problem.to_csv(index=False).encode(), "qa_date_format.csv")
    else:
        st.success("All NextPaymentDate values are correctly formatted.")

# -- 6. Multiple names --
with st.expander(f"⑥ Multiple Names in FirstName — {int(df['_multi_name'].sum())} row(s)"):
    if df["_multi_name"].sum() > 0:
        problem = df[df["_multi_name"]][[c for c in
            ["FirstName","LastName","LegacyId","Email"] if c in df.columns]]
        st.warning("These rows contain '&' or ' and ' in the FirstName field, suggesting multiple donors.")
        st.dataframe(problem, use_container_width=True)
        st.download_button("Download Rows", problem.to_csv(index=False).encode(), "qa_multi_name.csv")
    else:
        st.success("No multiple names detected in FirstName.")

# =====================================================================
# FULL FILE PREVIEW
# =====================================================================
st.subheader("File Preview")
display_cols = [c for c in df.columns if not c.startswith("_")]
st.dataframe(df[display_cols], use_container_width=True)

# =====================================================================
# DOWNLOAD ALL FLAGGED ROWS
# =====================================================================
if total_issues > 0:
    flagged = df[df["_any_issue"]][display_cols]
    st.download_button(
        "⬇️ Download All Flagged Rows",
        flagged.to_csv(index=False).encode(),
        "qa_all_flagged.csv"
    )

st.markdown("""
<div class="hub-footer">
    Built for efficient recurring data migrations &nbsp;·&nbsp; LRD Tools
</div>
""", unsafe_allow_html=True)
