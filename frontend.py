import re
import json
import io
import os
import streamlit as st
import pandas as pd
from database import fetch_all_data, Executive, Highlight, Strength

# --- PAGE CONFIG ---
st.set_page_config(page_title="Executive Catalyst Catalogue", layout="wide")

# --- SIMPLE PAGE NAV ---
st.sidebar.header("📄 Pages")
selected_page = st.sidebar.radio(
    "Go to",
    ["Catalogue", "Instant Profile Tool"],
    index=0,
    key="page"
)

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

# --- DATA NORMALIZATION ---
# Normalize `sector_focus` values to lowercase and strip whitespace to
# avoid case mismatches like 'Sustainability' vs 'sustainability'.
def get_normalized_sectors(e):
    """Safely extracts and normalizes sectors without mutating the DB object."""
    try:
        sf = getattr(e, 'sector_focus', None)
        if not sf:
            return []

        # Catch cases where the DB returns a comma-separated string instead of a list
        if isinstance(sf, str):
            sf = sf.split(',')

        return [s.strip().lower() for s in sf if s and s.strip()]
    except Exception:
        return []

# Optional integration helpers
try:
    from json_to_sql import generate_sql_script
except Exception:
    generate_sql_script = None

try:
    import json_to_pptx as pptx_module
except Exception:
    pptx_module = None

# --- PAIN POINT MAPPING ---
PAIN_POINTS = {
    "📉 Sales are flatlining": ["Commercial", "Sales", "Branding", "Growth", "FMCG", "Business Development"],
    "💸 Is this even profitable?": ["CFO", "Finance", "Financial", "Exit", "Turnaround", "Investment", "Risk"],
    "⚙️ Tech/Ops are a mess": ["Operations", "Logistics", "IT", "Digitalization", "Transformation", "Infrastructure", "COO"],
    "👫 People & Culture issues": ["HR", "Leadership", "Coaching", "Governance", "Advisor", "People"]
}

def render_catalogue_page():
    # --- DATA LOADING ---
    @st.cache_data
    def load_data():
        try:
            return fetch_all_data()
        except Exception:
            return [], [], []

    execs, all_highlights, all_strengths = load_data()
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🎯 Solve a Problem")

    # Callback to automatically populate keywords when a pain-point is selected
    def update_keywords():
        pain = st.session_state.pain_point
        if pain:
            st.session_state.keywords = ", ".join(PAIN_POINTS[pain])

    selected_pain = st.sidebar.selectbox(
        "What's your biggest headache?", 
        options=list(PAIN_POINTS.keys()),
        index=None,
        placeholder="Select a pain-point...",
        key="pain_point",
        on_change=update_keywords
    )

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Refine Search")

    search_input = st.sidebar.text_input("Keywords", key="keywords")
    query_words = [word.strip() for word in search_input.replace(',', ' ').split() if word.strip()]

    # Build normalized sector list safely using the new helper
    norm_sectors = set()
    for e in execs:
        norm_sectors.update(get_normalized_sectors(e))

    # Use .title() for formatting and a set to guarantee unique display options
    display_sectors = sorted(set(s.title() for s in norm_sectors))

    selected_display = st.sidebar.multiselect(
        "Filter by Sector Focus",
        display_sectors,
        placeholder="Select sectors...",
        key="sectors"
    )

    # Convert selected display values back to lowercase form for filtering
    selected_sectors = [s.lower() for s in selected_display]

    # Extra controls
    st.sidebar.markdown("---")
    sort_by = st.sidebar.selectbox("Sort results by", ["Relevance (score)", "Experience length"], index=0, key="sort_by")

    # Callback to force all widget states back to neutral
    def clear_all_filters():
        st.session_state.pain_point = None
        st.session_state.keywords = ""
        st.session_state.sectors = []
        st.session_state.sort_by = "Relevance (score)"

    # The on_click parameter handles the reset and auto-reruns the page perfectly
    st.sidebar.button("Clear filters", on_click=clear_all_filters)

    # --- INTERNAL RANKING & FILTERING LOGIC ---
    def get_ranked_data(query_list, sectors):
        def sector_match(e):
            e_sectors = get_normalized_sectors(e)
            return any(s in e_sectors for s in sectors) if sectors else True

        ranked_results = []

        for e in execs:
            if not sector_match(e):
                continue

            e_h = [h for h in all_highlights if h.executive_id == e.id]
            e_s = [s for s in all_strengths if s.executive_id == e.id]

            e_sectors = get_normalized_sectors(e)

            # Combine all text for background scoring
            content_blobs = [
                " ".join(getattr(e, 'title', [])) if getattr(e, 'title', None) else "",
                " ".join(e_sectors),
                getattr(e, 'experience', '') or "",
                " ".join([f"{getattr(h, 'position_title', '')} {getattr(h, 'company_descri', '')} {getattr(h, 'details', '')}" for h in e_h]),
                " ".join([getattr(s, 'strength_descrip', '') for s in e_s])
            ]
            full_text = " ".join(content_blobs)

            # Calculate Internal Score
            score = 0
            if query_list:
                for word in query_list:
                    pattern = rf"\b{re.escape(word)}('s)?\b"
                    matches = re.findall(pattern, full_text, re.IGNORECASE)
                    score += len(matches)

            # Appending matched executives
            if not query_list or score > 0:
                ranked_results.append({"exec": e, "h": e_h, "s": e_s, "score": score})

        # Sort by score descending
        return sorted(ranked_results, key=lambda x: x['score'], reverse=True)

    # Initial ranking
    ranked_execs = get_ranked_data(query_words, selected_sectors)

    # Apply sorting preference
    if sort_by == "Experience length":
        ranked_execs = sorted(ranked_execs, key=lambda x: len(x['exec'].experience) if getattr(x['exec'], 'experience', None) else 0, reverse=True)

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
            st.write(f"**Sectors:** {', '.join([s.title() for s in get_normalized_sectors(e)])}")
            st.markdown("---")

            # ACTIONS: Export / View
            def build_profile_json(executive, highlights, strengths):
                # Build a minimal profile dict compatible with converters
                profile = {
                    "title": " | ".join(executive.title) if getattr(executive, 'title', None) else "",
                    "gender": getattr(executive, 'gender', '') or "",
                    "experience_summary": getattr(executive, 'experience', '') or "",
                    "sector_focus": ", ".join([s.title() for s in get_normalized_sectors(executive)]),
                    "location": getattr(executive, 'location', '') or "",
                    "experience": [],
                    "core_strengths": [s.strength_descrip for s in strengths] if strengths else []
                }

                for h in highlights:
                    details_text = getattr(h, 'details', '') or ""
                    achievements = [ln.strip() for ln in details_text.replace('\\r', '').split('\\n') if ln.strip()]
                    profile['experience'].append({
                        'job_title': getattr(h, 'position_title', '') or '',
                        'description': getattr(h, 'company_descri', '') or '',
                        'achievements': achievements
                    })

                return profile

            col_left, col_right = st.columns([1, 3])
            with col_left:
                try:
                    json_data = build_profile_json(e, e_h, e_s)
                except Exception as ex:
                    json_data = None
                    st.error(f"Error building profile JSON: {ex}")

                if json_data:
                    pretty_json = json.dumps(json_data, ensure_ascii=False, indent=2)
                    if st.button(f"View JSON — #{rank}"):
                        st.json(json_data)

                    st.download_button(label="Download JSON", data=pretty_json, file_name=f"profile_{rank}.json", mime="application/json")

                    # SQL export
                    if generate_sql_script:
                        try:
                            sql_text = generate_sql_script(json_data)
                            st.download_button(label="Download SQL", data=sql_text, file_name=f"profile_{rank}.sql", mime="text/sql")
                        except Exception as ex:
                            st.warning(f"SQL generation failed: {ex}")
                    else:
                        st.info("SQL export unavailable (missing generator).")

                    # PPTX export (best-effort)
                    if pptx_module:
                        if st.button(f"Export PPTX — #{rank}"):
                            json_path = os.path.join(os.getcwd(), 'json_output.json')
                            try:
                                with open(json_path, 'w', encoding='utf-8') as jf:
                                    json.dump(json_data, jf, ensure_ascii=False, indent=2)
                                pptx_module.main()
                                output_path = os.path.join(os.getcwd(), getattr(pptx_module, 'OUTPUT_FILE', 'New_Profile_Final.pptx'))
                                if os.path.exists(output_path):
                                    with open(output_path, 'rb') as f:
                                        st.download_button(label='Download PPTX', data=f, file_name=os.path.basename(output_path), mime='application/vnd.openxmlformats-officedocument.presentationml.presentation')
                                else:
                                    st.warning('PPTX generation finished but output file not found.')
                            except Exception as ex:
                                st.error(f"PPTX export failed: {ex}")
                    else:
                        st.info("PPTX export unavailable (pptx module missing).")

            with col_right:
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


def render_test_tool_page():
    st.title("Test Tool")
    st.write("This is a placeholder page for your next tool. Replace this with the new workflow.")


if selected_page == "Catalogue":
    render_catalogue_page()
else:
    render_test_tool_page()