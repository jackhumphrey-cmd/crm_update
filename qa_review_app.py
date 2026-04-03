import pandas as pd
import streamlit as st
import re

st.set_page_config(
    page_title="🔍 Migration QA Tool",
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
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div class="page-badge">LRD Internal Tools</div>
    <h1 class="page-title">Migration <span>QA Tool</span></h1>
    <p class="page-sub">Run quality assurance checks on your final migration file before import.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Upload
# -----------------------------
migration_file = st.sidebar.file_uploader("Migration File (CSV)", type=["csv"])

if not migration_file:
    st.warning("Please upload your migration file to begin.")
    st.stop()

with st.spinner("Running QA checks..."):

    df = pd.read_csv(migration_file, dtype=str, keep_default_na=False)
    df.columns = df.columns.str.strip()

    # -----------------------------
    # Constants
    # -----------------------------
    REQUIRED_FIELDS = [
        "FirstName", "LastName", "Email", "PaymentMethodType",
        "PaymentMethodId", "Amount", "Frequency", "NextPaymentDate",
        "CustomerId", "Project1Code", "Project1Name", "Project1Amount"
    ]
    VALID_PAYMENT_TYPES = {"Credit", "ACH"}
    VALID_FREQUENCIES   = {"Monthly", "Weekly", "Annually", "Fortnightly", "Quarterly", "Semiannually"}
    DATE_PATTERN        = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
    MULTI_NAME_PATTERN  = re.compile(r"&| and ", re.IGNORECASE)

    # Detect all ProjectN amount columns dynamically
    project_amount_cols = sorted(
        [c for c in df.columns if re.match(r"Project\d+Amount", c)],
        key=lambda x: int(re.search(r"\d+", x).group())
    )

    # -----------------------------
    # Run checks row-by-row
    # -----------------------------
    flags = []

    for idx, row in df.iterrows():
        row_flags = []

        # 1. Missing required fields
        for field in REQUIRED_FIELDS:
            val = row.get(field, "")
            if pd.isna(val) or str(val).strip() == "":
                row_flags.append(f"Missing: {field}")

        # 2. Project splits must sum to Amount
        try:
            total_amount = float(row.get("Amount", 0) or 0)
            split_total  = sum(
                float(row.get(col, 0) or 0)
                for col in project_amount_cols
                if str(row.get(col, "")).strip() not in ("", "nan")
            )
            if project_amount_cols and round(split_total, 2) != round(total_amount, 2):
                row_flags.append(
                    f"Split mismatch: splits sum to {round(split_total, 2)}, Amount is {round(total_amount, 2)}"
                )
        except (ValueError, TypeError):
            row_flags.append("Split mismatch: could not parse Amount or project amounts")

        # 3. Excel error values or #N/A in PaymentMethodId or CustomerId
        for field in ["PaymentMethodId", "CustomerId"]:
            val = str(row.get(field, "")).strip()
            if val.startswith("#"):
                row_flags.append(f"Unmapped ID: {field} = {val}")

        # 4. PaymentMethodType must be Credit or ACH
        pmt = str(row.get("PaymentMethodType", "")).strip()
        if pmt and pmt not in VALID_PAYMENT_TYPES:
            row_flags.append(f"Invalid PaymentMethodType: '{pmt}'")

        # 5. NextPaymentDate format must be D/M/YYYY or DD/MM/YYYY (no timestamps)
        date_val = str(row.get("NextPaymentDate", "")).strip()
        if date_val and not DATE_PATTERN.match(date_val):
            row_flags.append(f"Invalid date format: '{date_val}'")

        # 6. Multiple names in FirstName (& or ' and ')
        first_name = str(row.get("FirstName", "")).strip()
        if MULTI_NAME_PATTERN.search(first_name):
            row_flags.append(f"Multiple names in FirstName: '{first_name}'")

        # 7. Frequency must be one of the valid values
        freq = str(row.get("Frequency", "")).strip()
        if freq and freq not in VALID_FREQUENCIES:
            row_flags.append(f"Invalid Frequency: '{freq}'")

        flags.append("; ".join(row_flags) if row_flags else "")

    df["QA_Flags"] = flags
    df["QA_Pass"]  = df["QA_Flags"] == ""

    clean_rows    = df[df["QA_Pass"]]
    flagged_rows  = df[~df["QA_Pass"]]

    # -----------------------------
    # Per-check counts for summary
    # -----------------------------
    def count_flag(keyword):
        return df["QA_Flags"].str.contains(keyword, na=False).sum()

    total          = len(df)
    total_pass     = len(clean_rows)
    total_fail     = len(flagged_rows)
    missing_count  = count_flag("Missing:")
    split_count    = count_flag("Split mismatch")
    na_count       = count_flag("Unmapped ID")
    pmt_count      = count_flag("Invalid PaymentMethodType")
    date_count     = count_flag("Invalid date format")
    name_count     = count_flag("Multiple names")
    freq_count     = count_flag("Invalid Frequency")

# -----------------------------
# QA Summary — top metrics
# -----------------------------
st.subheader("QA Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Total Rows", total)
col2.metric("Passed", total_pass)
col3.metric("Flagged", total_fail)

st.write("")

if total_fail == 0:
    st.success("✅ All rows passed QA — file looks good to import!")
else:
    st.warning(f"{total_fail} row(s) have QA issues. Review the checks below before importing.")

st.write("")

# -----------------------------
# Per-check expanders
# -----------------------------
checks = [
    ("Missing Required Fields",     "Missing:",                  missing_count),
    ("Split Amount Mismatches",     "Split mismatch",            split_count),
    ("Unmapped IDs (#N/A)",         "Unmapped ID",               na_count),
    ("Invalid Payment Type",        "Invalid PaymentMethodType", pmt_count),
    ("Invalid Date Format",         "Invalid date format",       date_count),
    ("Multiple Names in FirstName", "Multiple names",            name_count),
    ("Invalid Frequency",           "Invalid Frequency",         freq_count),
]

for label, keyword, count in checks:
    status = "✅" if count == 0 else "⚠️"
    with st.expander(f"{status} {label} — {count} row(s)"):
        if count == 0:
            st.success("No issues found.")
        else:
            subset = df[df["QA_Flags"].str.contains(keyword, na=False)]
            cols_to_show = [c for c in ["FirstName", "LastName", "Email", "LegacyId", "QA_Flags"] if c in subset.columns]
            st.dataframe(subset[cols_to_show], use_container_width=True)
            st.download_button(
                f"Download — {label}",
                subset.to_csv(index=False).encode("utf-8"),
                f"qa_{keyword.replace(' ', '_').replace(':', '').lower()}.csv",
                "text/csv",
                key=f"dl_{keyword}"
            )

st.write("")

# -----------------------------
# Downloads
# -----------------------------
st.subheader("Downloads")

col1, col2, col3 = st.columns(3)

with col1:
    if len(flagged_rows) > 0:
        st.download_button(
            "Download Flagged Rows",
            flagged_rows.to_csv(index=False).encode("utf-8"),
            "qa_flagged_rows.csv",
            "text/csv"
        )

with col2:
    st.download_button(
        "Download Clean Rows",
        clean_rows.drop(columns=["QA_Flags", "QA_Pass"], errors="ignore").to_csv(index=False).encode("utf-8"),
        "qa_clean_rows.csv",
        "text/csv"
    )

with col3:
    st.download_button(
        "Download Full File with Flags",
        df.to_csv(index=False).encode("utf-8"),
        "qa_full_output.csv",
        "text/csv"
    )

st.markdown("""
<div class="hub-footer">
    Built for efficient recurring data migrations &nbsp;·&nbsp; LRD Tools
</div>
""", unsafe_allow_html=True)
