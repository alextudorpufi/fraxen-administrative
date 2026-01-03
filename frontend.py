import re
import streamlit as st
from database import fetch_all_data, Executive, Highlight, Strength

st.set_page_config(page_title="Executive Catalogue", layout="wide")

# --- UI UTILITIES ---
def highlight_text(text, query):
    if not query or not text: return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark style='background-color: yellow; color: black;'>{m.group()}</mark>", text)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    return fetch_all_data()

execs, all_highlights, all_strengths = load_data()

# --- FILTERING LOGIC ---
st.sidebar.header("Search Filters")
search_query = st.sidebar.text_input("Search by Keyword", "").lower()
all_sectors = sorted(list(set(s for e in execs for s in e.sector_focus)))
selected_sectors = st.sidebar.multiselect("Filter by Sector", all_sectors)

def get_filtered_data(query, sectors):
    def sector_match(e):
        return any(s in e.sector_focus for s in sectors) if sectors else True

    # Primary Search
    primary = [e for e in execs if (query in " ".join(e.title).lower() or query in " ".join(e.sector_focus).lower()) and sector_match(e)]
    if primary or not query:
        return primary, False

    # Deep Search Fallback
    deep_results = []
    for e in execs:
        if not sector_match(e): continue
        e_h = [h for h in all_highlights if h.executive_id == e.id]
        e_s = [s for s in all_strengths if s.executive_id == e.id]
        content = f"{e.experience} {e.gender} {e.location} {' '.join([h.details for h in e_h])} {' '.join([s.strength_descrip for s in e_s])}"
        if query in content.lower().replace('\\n', ' '):
            deep_results.append(e)
    return deep_results, True

filtered_execs, is_deep_search = get_filtered_data(search_query, selected_sectors)

# --- UI RENDERING ---
st.title("Fractional Executives Catalogue")
if is_deep_search and filtered_execs:
    st.warning("Matches found in deeper profile details.")

for e in filtered_execs:
    e_h = [h for h in all_highlights if h.executive_id == e.id]
    e_s = [s for s in all_strengths if s.executive_id == e.id]
    
    with st.expander(" | ".join(e.title), expanded=is_deep_search):
        st.write(f"**Gender:** {e.gender}  \n**Experience:** {e.experience}  \n**Location:** {e.location}")
        st.markdown("---")
        for h in e_h:
            st.markdown(f"<b>{highlight_text(h.position_title, search_query)}</b> — {highlight_text(h.company_descri, search_query)}", unsafe_allow_html=True)
            for line in h.details.replace('\\n', '\n').split('\n'):
                if line.strip():
                    st.markdown(f"→ {highlight_text(line.strip(), search_query)}", unsafe_allow_html=True)
        if e_s:
            st.markdown("**Core Strengths:**")
            for s in e_s:
                st.markdown(f"→ {highlight_text(s.strength_descrip, search_query)}", unsafe_allow_html=True)