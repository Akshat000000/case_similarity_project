import streamlit as st

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Case Similarity System",
    layout="wide"
)

# -----------------------------
# Header section
# -----------------------------
st.title("⚖️ Case Similarity System")
st.subheader("Explore, search, and analyze judicial cases intelligently")

st.markdown(
    """
    This platform helps you explore judicial cases, discover similar precedents,
    and understand legal decisions using intelligent search and visualization.
    """
)

st.divider()

# -----------------------------
# Feature cards
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📚 Case Explorer")
    st.caption("Browse Database")
    st.write("Explore randomly sampled cases, read full judgments, and discover similar precedents.")
    st.markdown("Get started via **Case Explorer** in the sidebar.")

with col2:
    st.markdown("#### 🔍 Case Search")
    st.caption("AI Semantic Search")
    st.write("Find relevant cases by description using our advanced embedding and reranking engine.")
    st.markdown("Get started via **Case Search** in the sidebar.")

with col3:
    st.markdown("#### 🕸️ Graph Analysis")
    st.caption("Visual Intelligence")
    st.write("Visualize relationships, clusters, and similarity scores between cases interactively.")
    st.markdown("Now available as a view within **Case Search**.")

st.divider()

# -----------------------------
# Footer / guidance
# -----------------------------
st.info(
    "👈 Use the sidebar on the left to navigate between different features."
)
