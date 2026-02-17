import streamlit as st
import sys
import os
import pandas as pd
from pyvis.network import Network
import tempfile
import streamlit.components.v1 as components

# --------------------------------------------------
# Add project root to path
# --------------------------------------------------
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import ui.api_client as api
from utils.text_preprocessing import highlight_text

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Case Search",
    layout="wide"
)

st.title("🔍 Case Search")
st.caption("Search similar judicial cases with explainable ranking")

# --------------------------------------------------
# Check Backend Health
# --------------------------------------------------
if not api.check_backend_health():
    st.error("⚠️ Backend API is not reachable. Please ensure the backend server is running on port 8000.")
    st.stop()

# --------------------------------------------------
# Initialize session state
# --------------------------------------------------
if "search_results" not in st.session_state:
    st.session_state["search_results"] = None

if "query_text" not in st.session_state:
    st.session_state["query_text"] = ""

# --------------------------------------------------
# Search input
# --------------------------------------------------
with st.form(key="search_form"):
    st.text_area(
        "Enter case description",
        key="query_text_input",  # Unique widget key
        value=st.session_state["query_text"],
        height=220,
        placeholder="Enter your case description here..."
    )

    submit_button = st.form_submit_button("🔎 Search Similar Cases")

if submit_button:
    current_query = st.session_state["query_text_input"]
    st.session_state["query_text"] = current_query
    
    if not current_query.strip():
        st.warning("Please enter a case description.")
    else:
        with st.spinner("Searching similar cases..."):
            # Call API instead of local pipeline
            results = api.search_cases(current_query)

        st.session_state["search_results"] = results
        if results:
            st.success("Search completed successfully.")
        else:
            st.warning("No results found.")

# --------------------------------------------------
# Display results
# --------------------------------------------------
results = st.session_state.get("search_results")

if results:
    # Sidebar Filters
    st.sidebar.header("Filter Results")
    filter_decision = st.sidebar.selectbox(
        "Decision Outcome",
        options=["Select", "Accepted", "Rejected"],
        index=0
    )

    if filter_decision == "Select":
        filtered_results = results
    else:
        filtered_results = [
            r for r in results 
            if r["decision"] == filter_decision.lower()
        ]

    # Tabs for different views
    tab_list, tab_graph = st.tabs(["📄 List View", "🕸️ Graph View"])

    # --------------------------------------------------
    # TAB 1: List View
    # --------------------------------------------------
    with tab_list:
        if not filtered_results:
            st.warning("No cases match your filters.")
        else:
            st.subheader(f"📄 Top Similar Cases ({len(filtered_results)} matches)")
        
            for idx, r in enumerate(filtered_results, start=1):
                decision_badge = (
                    "🟢 Accepted"
                    if r.get("decision") == "accepted"
                    else "🔴 Rejected"
                )

                st.markdown(
                    f"""
                    ### #{idx} — Case ID: `{r['case_id']}`
                    **Decision:** {decision_badge}  
                    **Embedding Similarity:** `{round(r.get('embed_score', 0) * 100, 2)}%`  
                    **Final Score:** `{round(r.get('final_score', 0) * 100, 2)}%`

                    """
                )

                with st.expander("📊 Why this case is ranked here"):
                    breakdown = r.get("score_breakdown")
                    if breakdown:
                        df = pd.DataFrame({
                            "Factor": [
                                "Embedding Similarity",
                                "Cross-Encoder Relevance",
                                "Decision Outcome",
                                "Reasoning Availability"
                            ],
                            "Contribution (%)": [
                                breakdown["embedding"] * 100,
                                breakdown["cross_encoder"] * 100,
                                breakdown["decision"] * 100,
                                breakdown["reasoning"] * 100,
                            ]
                        })
                        st.bar_chart(df.set_index("Factor"))
                    else:
                        st.info("Score breakdown not available.")

                with st.expander("📖 Read Full Case"):
                    if r.get("decision_reason"):
                        st.markdown("**Reasoning (Expert Summary):**")
                        st.success(r["decision_reason"])

                    st.markdown("**Full Case Judgment:**")
                    full_text = r.get("full_text", "N/A")
                    query_str = st.session_state.get("query_text", "")
                    highlighted = highlight_text(full_text, query_str)
                    st.markdown(f"<div style='background-color:rgba(255,255,255,0.05); padding:15px; border-radius:5px;'>{highlighted}</div>", unsafe_allow_html=True)
                
                st.divider()

    # --------------------------------------------------
    # TAB 2: Graph View
    # --------------------------------------------------
    with tab_graph:
        if not filtered_results:
            st.warning("No cases match your filters.")
        else:
            st.markdown("### 🕸️ Case Similarity Graph")
            
            # Prepare Network
            net = Network(
                height="600px",
                width="100%",
                directed=False,
                bgcolor="#1a1a1a",
                font_color="white"
            )
            net.force_atlas_2based()

            case_ids = [r["case_id"] for r in filtered_results]

            # Add nodes
            for i, r in enumerate(filtered_results):
                color = "#55efc4" if r.get("decision") == "accepted" else "#ff7675"
                score = round(r.get("final_score", 0) * 100, 1)
                tooltip = f"Case: {r['case_id']}\nScore: {score}%\nDecision: {r['decision']}"
                size = 25 - (i * 2)

                net.add_node(
                    r["case_id"],
                    label=r["case_id"],
                    title=tooltip,
                    color=color,
                    size=size,
                    borderWidth=2,
                    borderWidthSelected=4,
                    font={'size': 14, 'face': 'Inter'}
                )

            # Add edges (mesh)
            for i in range(len(filtered_results)):
                for j in range(i + 1, len(filtered_results)):
                    r1 = filtered_results[i]
                    r2 = filtered_results[j]
                    s1 = r1.get('embed_score', 0)
                    s2 = r2.get('embed_score', 0)
                    avg_sim = (s1 + s2) / 2
                    
                    net.add_edge(
                        r1["case_id"],
                        r2["case_id"],
                        value=1,
                        title=f"Similarity Score: {round(avg_sim * 100, 1)}%",
                        color="rgba(255, 255, 255, 0.15)"
                    )

            # Render Graph
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                net.save_graph(tmp.name)
                with open(tmp.name, "r", encoding="utf-8") as f:
                    html_content = f.read()

                # Inject CSS
                html_content = html_content.replace(
                    "</head>", 
                    """<style>
                    div.vis-tooltip {
                        background-color: rgba(0,0,0,0.8);
                        color: #fff;
                        padding: 10px;
                        border-radius: 8px;
                        font-family: 'Inter', sans-serif;
                        font-size: 14px;
                        border: 1px solid #444;
                    }
                    </style></head>"""
                )
                
                components.html(
                    html_content,
                    height=620,
                    scrolling=False
                )

            # Case Inspector
            st.divider()
            st.subheader("📖 Selected Case Details")
            
            c1, c2 = st.columns([1, 2])
            with c1:
                selected_case_id = st.selectbox("🔎 Select Node (Case ID):", case_ids)
                selected_case = next(c for c in filtered_results if c["case_id"] == selected_case_id)
                
                st.markdown(f"""
                <div style="background-color: #262626; padding: 20px; border-radius: 10px; border: 1px solid #333;">
                    <h3 style="margin:0; color: #fff;">{selected_case['case_id']}</h3>
                    <p style="margin-bottom:15px; color: #888; font-size: 0.9rem;">Rank: #{case_ids.index(selected_case_id) + 1}</p>
                </div>
                """, unsafe_allow_html=True)

                if selected_case.get("decision_reason"):
                    st.markdown("#### 🧠 Expert Reasoning")
                    st.info(selected_case["decision_reason"])

            with c2:
                st.markdown("#### 📜 Full Judgment Text")
                
                query = st.session_state.get("query_text", "")
                formatted_text = highlight_text(selected_case.get("full_text", ""), query)

                st.markdown(
                    f"<div style='height: 500px; overflow-y: auto; background-color: #1e1e1e; padding: 20px; border-radius: 8px; border: 1px solid #333; color: #ddd; line-height: 1.6;'>{formatted_text}</div>", 
                    unsafe_allow_html=True
                )

# --------------------------------------------------
# Clear results
# --------------------------------------------------
if st.session_state["search_results"]:
    if st.button("🔄 Clear Search Results"):
        st.session_state["search_results"] = None
        st.session_state["query_text"] = ""
        # Also clear the widget key if it exists
        if "query_text_input" in st.session_state:
            st.session_state["query_text_input"] = ""
        st.rerun()
