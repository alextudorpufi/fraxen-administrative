import re
import streamlit as st
import pandas as pd
from database import fetch_all_data, Executive, Highlight, Strength

# --- PAGE CONFIG ---
st.set_page_config(page_title="Executive Catalyst Catalogue", layout="wide")

# --- UI UTILITIES ---
def highlight_text(text, query_list):
    """Highlights standalone words or words with 's from the query list."""
    if not query_list or not text:
        return text
    # Word boundary regex to avoid partial matches (e.g., IT vs Hospitality)
    valid_queries = [rf"\b{re.escape(q)}('s)?\b" for q in query_list if q.strip()]
    if not valid_queries:
        return text
    pattern = re.compile(f"({'|'.join(valid_queries)})", re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark style='background-color: #FFEB3B; color: black; padding: 0 2px; border-radius: 2px;'>{m.group()}</mark>", text)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    return fetch_all_data()

execs, all_highlights, all_strengths = load_data()

# --- PAIN POINT MAPPING ---
PAIN_POINTS = {
    "📉 Sales are flatlining": ["Commercial", "Sales", "Branding", "Growth", "FMCG", "Business Development"],
    "💸 Is this even profitable?": ["CFO", "Finance", "Financial", "Exit", "Turnaround", "Investment", "Risk"],
    "⚙️ Tech/Ops are a mess": ["Operations", "Logistics", "IT", "Digitalization", "Transformation", "Infrastructure", "COO"],
    "👫 People & Culture issues": ["HR", "Leadership", "Coaching", "Governance", "Advisor", "People"]
}

# --- SIDEBAR FILTERS ---
st.sidebar.header("🎯 Solve a Problem")
selected_pain = st.sidebar.selectbox(
    "What's your biggest headache?", 
    options=list(PAIN_POINTS.keys()),
    index=None,
    placeholder="Select a pain-point..."
)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Refine Search")

default_keywords = ""
if selected_pain:
    default_keywords = ", ".join(PAIN_POINTS[selected_pain])

search_input = st.sidebar.text_input("Keywords", value=default_keywords)
query_words = [word.strip() for word in search_input.replace(',', ' ').split() if word.strip()]

all_sectors = sorted(list(set(s for e in execs for s in e.sector_focus)))
selected_sectors = st.sidebar.multiselect(
    "Filter by Sector Focus", 
    all_sectors,
    placeholder="Select sectors..."
)

# --- INTERNAL RANKING & FILTERING LOGIC ---
def get_ranked_data(query_list, sectors):
    def sector_match(e):
        return any(s in e.sector_focus for s in sectors) if sectors else True

    ranked_results = []

    for e in execs:
        if not sector_match(e): 
            continue
        
        e_h = [h for h in all_highlights if h.executive_id == e.id]
        e_s = [s for s in all_strengths if s.executive_id == e.id]
        
        # Combine all text for background scoring
        content_blobs = [
            " ".join(e.title),
            " ".join(e.sector_focus),
            e.experience,
            " ".join([f"{h.position_title} {h.company_descri} {h.details}" for h in e_h]),
            " ".join([s.strength_descrip for s in e_s])
        ]
        full_text = " ".join(content_blobs)

        # Calculate Internal Score
        score = 0
        if query_list:
            for word in query_list:
                pattern = rf"\b{re.escape(word)}('s)?\b"
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                score += len(matches)
        
        # Appending matched executives, either by non-filtering or score
        if not query_list or score > 0:
            ranked_results.append({"exec": e, "h": e_h, "s": e_s, "score": score})

    # Sort by score descending
    return sorted(ranked_results, key=lambda x: x['score'], reverse=True)

ranked_execs = get_ranked_data(query_words, selected_sectors)

# --- MAIN UI ---
st.title("Fractional Executives Catalogue")

if selected_pain:
    st.info(f"**Ranking experts for:** {selected_pain}. (Searching for: {', '.join(query_words)})")

if not ranked_execs:
    st.error("No matches found. Try broadening your keywords.")

# --- RENDER RESULTS ---
for rank, item in enumerate(ranked_execs, 1):
    e = item["exec"]
    e_h = item["h"]
    e_s = item["s"]
    score = item["score"]
    
    # Display only the titles + ranks
    header_label = f"#{rank} | {' | '.join(e.title)}"
    
    # Auto-expand the first ig
    is_expanded = True if (rank == 1 and score > 0) else False

    with st.expander(header_label, expanded=is_expanded):
        # Top Meta Data
        st.write(f"**Experience:** {e.experience}  |  **Location:** {e.location}  |  **Gender:** {e.gender}")
        st.write(f"**Sectors:** {', '.join(e.sector_focus)}")
        
        st.markdown("---")
        
        # Career Highlights
        st.subheader("Career Highlights")
        for h in e_h:
            st.markdown(f"<b>{highlight_text(h.position_title, query_words)}</b> — {highlight_text(h.company_descri, query_words)}", unsafe_allow_html=True)
            for line in h.details.replace('\\n', '\n').split('\n'):
                if line.strip():
                    st.markdown(f"→ {highlight_text(line.strip(), query_words)}", unsafe_allow_html=True)
        
        # Core Strengths
        if e_s:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Core Strengths:**")
            for s in e_s:
                st.markdown(f"→ {highlight_text(s.strength_descrip, query_words)}", unsafe_allow_html=True)

# --- SIDEBAR FOOTER ---
st.sidebar.markdown("---")
st.sidebar.write(f"**Results Found:** {len(ranked_execs)}")