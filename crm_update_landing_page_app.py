import streamlit as st
st.set_page_config(
    page_title="LRD Migration Hub",
    page_icon="💳",
    layout="centered"
)
# -----------------------------
# Header
# -----------------------------
st.title("CRM Update Hub")
st.subheader("Choose your migration workflow to get started")
st.write("")
# -----------------------------
# Virtuous Giving CRM Updates Card
# -----------------------------
with st.container(border=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Virtuous Giving CRM Updates")
        st.write("Build and export CRM update files for Virtuous Giving.")
    with col2:
        st.write("")
        st.write("")
        st.link_button(
            "Launch →",
            "https://vg-crm-update.streamlit.app",
            use_container_width=True
        )
st.write("")
# -----------------------------
# LRD -> Raise CRM Updates Card
# -----------------------------
with st.container(border=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### LRD → Raise CRM Updates")
        st.write("Map and export CRM update files for LRD to Raise migrations.")
    with col2:
        st.write("")
        st.write("")
        st.link_button(
            "Launch →",
            "https://raise-crm-update.streamlit.app",
            use_container_width=True
        )
st.write("")
# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption("Built for efficient recurring data migrations • LRD Tools")
