import re
from collections import namedtuple
import os
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import streamlit as st

# 1. Configuration & Data Structures
load_dotenv()
st.set_page_config(page_title="Executive Catalogue", layout="wide")

Executive = namedtuple('Executive', ['id', 'experience', 'gender', 'location', 'sector_focus', 'title'])
Highlight = namedtuple('Highlight', ['id', 'company_descri', 'details', 'display_order', 'position_title', 'executive_id'])
Strength = namedtuple('Strength', ['id', 'display_order', 'strength_descrip', 'executive_id'])

# --- HELPER FUNCTION FOR HIGHLIGHTING ---
def highlight_text(text, query):
    """Wraps the search query in HTML mark tags for yellow highlighting."""
    if not query or not text:
        return text
    # Use regex for case-insensitive replacement while preserving original casing
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark style='background-color: yellow; color: black;'>{m.group()}</mark>", text)

# 2. Data Fetching Logic (unchanged)
@st.cache_data
def get_full_profiles():
    # ... (Keep your existing get_full_profiles code here)
    connection = None
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"), port=os.getenv("DB_PORT")
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM executives ORDER BY id")
        exec_records = cursor.fetchall()
        
        # Mapping executives
        executives = []
        for row in exec_records:
            e_id, exp, gen, loc, sectors_raw, titles_raw = row
            executives.append(Executive(e_id, exp, gen, loc, [s.strip() for s in sectors_raw.split(',')], [t.strip() for t in titles_raw.split('|')]))

        cursor.execute("SELECT * FROM executive_highlights ORDER BY executive_id, display_order")
        highlights = [Highlight(*row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM executive_strengths ORDER BY executive_id, display_order")
        strengths = [Strength(*row) for row in cursor.fetchall()]

        return executives, highlights, strengths
    except (Exception, Error) as error:
        st.error(f"Database Error: {error}")
        return [], [], []
    finally:
        if connection: connection.close()

# 3. Load Data
execs, all_highlights, all_strengths = get_full_profiles()

# 4. Global Filtering Algorithm
st.sidebar.header("Search Filters")
search_query = st.sidebar.text_input("Search by Keyword", "").lower()
all_sectors = sorted(list(set(s for e in execs for s in e.sector_focus)))
selected_sectors = st.sidebar.multiselect("Filter by Sector", all_sectors)

filtered_execs = []
is_deep_search = False

def sector_match(e):
    return any(s in e.sector_focus for s in selected_sectors) if selected_sectors else True

# Step 1: Primary Search
for e in execs:
    full_title_text = " ".join(e.title).lower()
    full_sector_text = " ".join(e.sector_focus).lower()
    if (search_query in full_title_text or search_query in full_sector_text) and sector_match(e):
        filtered_execs.append(e)

# Step 2: Fallback Deep Search
if len(filtered_execs) == 0 and search_query:
    is_deep_search = True
    for e in execs:
        if not sector_match(e): continue
        e_highlights = [h for h in all_highlights if h.executive_id == e.id]
        e_strengths = [s for s in all_strengths if s.executive_id == e.id]
        deep_content = f"{e.experience} {e.gender} {e.location} " 
        deep_content += " ".join([f"{h.position_title} {h.company_descri} {h.details}" for h in e_highlights])
        deep_content += " ".join([s.strength_descrip for s in e_strengths])
        if search_query in deep_content.lower().replace('\\n', ' '):
            filtered_execs.append(e)

# 5. UI Layout
st.title("Fractional Executives Catalogue")

if is_deep_search and filtered_execs:
    st.warning(f"No matches in Title/Sector. Highlighting results found in deeper profile details.")

for e in filtered_execs:
    e_highlights = [h for h in all_highlights if h.executive_id == e.id]
    e_strengths = [s for s in all_strengths if s.executive_id == e.id]
    
    # We apply highlighting to the header if it matches (optional)
    full_title_label = " | ".join(e.title)

    with st.expander(full_title_label, expanded=is_deep_search): # Auto-expand if deep match found
        st.markdown(f"**Gender:** {e.gender}")
        st.markdown(f"**Experience:** {e.experience}")
        st.markdown(f"**Location:** {e.location}")
        st.markdown(f"**Sector Focus:** {', '.join(e.sector_focus)}")
        st.markdown("---")

        for h in e_highlights:
            # Highlight Position and Company
            h_title = highlight_text(h.position_title, search_query)
            h_comp = highlight_text(h.company_descri, search_query) if h.company_descri else ""
            
            header_html = f"<b>{h_title}</b>" + (f" — {h_comp}" if h_comp else "")
            st.markdown(header_html, unsafe_allow_html=True)
            
            if h.details:
                detail_text = h.details.replace('\\n', '\n')
                for line in detail_text.split('\n'):
                    if line.strip():
                        # Highlight the specific detail line
                        highlighted_line = highlight_text(line.strip(), search_query)
                        st.markdown(f"→ {highlighted_line}", unsafe_allow_html=True)
            st.write("") 

        if e_strengths:
            st.markdown("**Core Strengths:**")
            for s in e_strengths:
                # Highlight strength description
                highlighted_strength = highlight_text(s.strength_descrip, search_query)
                st.markdown(f"→ {highlighted_strength}", unsafe_allow_html=True)
        st.write("\n") 

if not filtered_execs:
    st.info("No profiles match the current filter criteria.")