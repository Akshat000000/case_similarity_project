import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import ui.api_client as api

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(layout="wide")

st.title("📚 Case Explorer")
st.caption("Browse judicial cases from the database with AI Summaries")

# -----------------------------
# CSS Styling
# -----------------------------
st.markdown("""
<style>
.case-card {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    padding: 1.3rem;
    border-radius: 14px;
    margin-bottom: 1.2rem;
    border: 1px solid rgba(150,150,150,0.15);
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}
.case-title {
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.case-summary {
    font-size: 0.9rem;
    opacity: 0.9;
    background-color: rgba(100, 100, 100, 0.1);
    padding: 10px;
    border-radius: 8px;
    margin-top: 5px;
}
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    color: white;
    margin-bottom: 0.6rem;
}
.sim-link {
    cursor: pointer;
    color: #4a90e2;
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Helper Wrappers (Caching)
# -----------------------------

@st.cache_data(ttl=60)
def get_random_cases_cached(limit=10):
    return api.fetch_random_cases(limit)

@st.cache_data(ttl=300)
def get_similar_cases_cached(text, ignore_id):
    results = api.search_cases(text)
    # Filter self and return top 5
    filtered = [r for r in results if str(r.get('case_id')) != str(ignore_id)]
    return filtered[:5]

@st.cache_data(ttl=300)
def get_case_details_cached(case_id):
    return api.fetch_case_details(case_id)

# -----------------------------
# Check Backend Health
# -----------------------------
if not api.check_backend_health():
    st.error("⚠️ Backend API is not reachable. Please ensure the backend server is running on port 8000.")
    st.stop()


# -----------------------------
# State Management
# -----------------------------
if "explorer_cases" not in st.session_state:
    st.session_state["explorer_cases"] = get_random_cases_cached(10)

if "view_case_id" not in st.session_state:
    st.session_state["view_case_id"] = None


# -----------------------------
# View Controller
# -----------------------------

# --- VIEW MODE: SINGLE CASE DETAILS ---
if st.session_state["view_case_id"]:
    case_id = st.session_state["view_case_id"]
    
    # Back button
    if st.button("⬅️ Back to Random Explorer"):
        st.session_state["view_case_id"] = None
        st.rerun()
        
    case_details = get_case_details_cached(case_id)
    
    if case_details:
        st.subheader(f"📄 Case Details: {case_details.get('case_id')}")
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            decision = case_details.get("decision") or "Unknown"
            color = "#2ecc71" if decision == "accepted" else "#e74c3c" if decision == "rejected" else "#95a5a6"
            
            st.markdown(f"""
            <div style="background-color: #262626; padding: 20px; border-radius: 10px; border: 1px solid #333;">
                <h3 style="margin:0; color: #fff;">{case_details.get('case_id')}</h3>
                <span style="background-color:{color}; color:white; padding:4px 12px; border-radius:12px; font-size:0.8rem; display:inline-block; margin-top:10px;">
                    {decision.upper()}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            if case_details.get("decision_reason"):
                st.markdown("#### 🧠 Expert Reasoning")
                st.info(case_details["decision_reason"])
                
        with c2:
            st.markdown("#### 📜 Full Judgment Text")
            st.text_area("Full Text", case_details.get("text", ""), height=600)
    else:
        st.error("Case not found or failed to fetch details.")
        if st.button("Reset"):
            st.session_state["view_case_id"] = None
            st.rerun()

# --- VIEW MODE: LIST EXPLORER ---
else:
    if st.button("🔄 Refresh Cases"):
        st.cache_data.clear()
        st.session_state["explorer_cases"] = get_random_cases_cached(10)
        st.rerun()

    random_cases = st.session_state.get("explorer_cases", [])
    
    if not random_cases:
        st.warning("No cases loaded. Check API connection.")
    else:
        cols = st.columns(2)
        
        for idx, case in enumerate(random_cases):
            col = cols[idx % 2]
            case_id = case.get("case_id")
            text = case.get("text")
            decision = case.get("decision")
            
            decision_label = decision if decision else "Unknown"
            badge_color = "#2ecc71" if decision_label.lower() == "accepted" else ("#e74c3c" if decision_label.lower() == "rejected" else "#95a5a6")
            
            display_summary = text[:350] + "..." if len(text) > 350 else text

            with col:
                st.markdown(f"""
                <div class="case-card">
                    <div class="case-title">🆔 Case ID: {case_id}</div>
                    <span class="badge" style="background:{badge_color};">
                        {decision_label.capitalize()}
                    </span>
                    <div class="case-summary">{display_summary}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"📖 Read Full Case ({case_id})"):
                    st.write(text)
                
                # Fetch similar cases automatically (cached)
                # Displayed outside the expander now
                similar_cases = get_similar_cases_cached(text, case_id)
                
                st.markdown("<b>🔗 Similar Cases</b>", unsafe_allow_html=True)
                
                if not similar_cases:
                    st.caption("No similar cases found.")
                else:
                    # Display as horizontal pills locally within the column
                    # Since columns are narrow, maybe just wrap buttons
                    s_cols = st.columns(5)
                    for i, sim in enumerate(similar_cases):
                        if i >= 5: break
                        sim_id = sim.get('case_id')
                        match_score = int(sim.get('final_score', 0) * 100)
                        
                        # Small buttons
                        if s_cols[i].button(f"{sim_id}\n{match_score}%", key=f"btn_{case_id}_{sim_id}", help="Click to view details"):
                            st.session_state["view_case_id"] = sim_id
                            st.rerun()

    # Footer
    st.info("🔄 Refresh the page to explore more random cases from the database.")
