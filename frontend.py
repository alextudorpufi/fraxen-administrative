import re
import json
import io
import os
import shutil
import subprocess
import sys
import zipfile
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
    st.title("Instant Profile Tool")
    st.write("Paste a CV, generate JSON, then export SQL or PPTX.")

    def load_cv_text() -> str:
        try:
            with open("cv_text.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    if "cv_text" not in st.session_state:
        st.session_state.cv_text = load_cv_text()

    cv_text = st.text_area("Paste CV text", height=300, key="cv_text")

    def run_script(script_name: str):
        return subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True
        )

    def sanitize_export_name(name: str) -> str:
        cleaned = name.strip()
        cleaned = cleaned.replace("/", "_").replace("\\", "_")
        return cleaned

    def build_pptx_with_title_suffix(suffix: str):
        try:
            with open("json_output.json", "r", encoding="utf-8") as f:
                original_text = f.read()
            data = json.loads(original_text)
        except Exception as ex:
            return False, f"Failed to read JSON: {ex}"

        base_title = (data.get("title") or "").strip()
        data["title"] = f"{base_title} - {suffix}" if base_title else suffix

        try:
            with open("json_output.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=2))

            result = run_script("json_to_pptx.py")
            output_text = f"{result.stdout}\n{result.stderr}".lower()
            if result.returncode != 0 or "error" in output_text:
                return False, "PPTX generation failed."
        finally:
            with open("json_output.json", "w", encoding="utf-8") as f:
                f.write(original_text)

        return True, "PPTX generated."

    def build_export_zip_bytes(export_base_name: str) -> tuple[bytes, str] | tuple[None, str]:
        """Builds a ZIP containing the current JSON/SQL/PPTX outputs for downloading to the client's computer."""
        if not os.path.exists("json_output.json"):
            return None, "json_output.json not found. Generate or save JSON first."

        safe_base = sanitize_export_name(export_base_name.strip()) if export_base_name else "export"
        if not safe_base:
            safe_base = "export"

        # Ensure SQL exists (best-effort)
        if not os.path.exists("sql_output.sql"):
            sql_result = run_script("json_to_sql.py")
            if sql_result.returncode != 0 or not os.path.exists("sql_output.sql"):
                return None, "SQL generation failed while preparing download."

        # Ensure PPTX exists (best-effort)
        pptx_output = "New_Profile_Final.pptx"
        if not os.path.exists(pptx_output):
            pptx_result = run_script("json_to_pptx.py")
            if pptx_result.returncode != 0 or not os.path.exists(pptx_output):
                return None, "PPTX generation failed while preparing download."

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write("json_output.json", arcname="json_output.json")
            zf.write("sql_output.sql", arcname="sql_output.sql")
            zf.write(pptx_output, arcname=pptx_output)

        buf.seek(0)
        return buf.getvalue(), f"{safe_base}.zip"

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("Run CV to JSON"):
            if not cv_text.strip():
                st.error("Please paste CV text first.")
            else:
                with open("cv_text.txt", "w", encoding="utf-8") as f:
                    f.write(cv_text)

                result = run_script("cv_to_json.py")
                output_text = f"{result.stdout}\n{result.stderr}".lower()
                json_exists = os.path.exists("json_output.json")
                if result.returncode != 0 or "error" in output_text or not json_exists:
                    st.error("JSON couldn't be generated.")
                else:
                    st.success("JSON generated.")

                with st.expander("cv_to_json.py output"):
                    if result.stdout:
                        st.code(result.stdout)
                    if result.stderr:
                        st.code(result.stderr)

    with col_b:
        if st.button("Run JSON to SQL"):
            if not os.path.exists("json_output.json"):
                st.error("json_output.json not found. Run CV to JSON first.")
            else:
                result = run_script("json_to_sql.py")
                if result.returncode != 0:
                    st.error("json_to_sql.py failed.")
                else:
                    st.success("SQL generated.")

                with st.expander("json_to_sql.py output"):
                    if result.stdout:
                        st.code(result.stdout)
                    if result.stderr:
                        st.code(result.stderr)

    with col_c:
        if st.button("Run JSON to PPTX"):
            if not os.path.exists("json_output.json"):
                st.error("json_output.json not found. Run CV to JSON first.")
            else:
                result = run_script("json_to_pptx.py")
                if result.returncode != 0:
                    st.error("json_to_pptx.py failed.")
                else:
                    st.success("PPTX generated.")

                with st.expander("json_to_pptx.py output"):
                    if result.stdout:
                        st.code(result.stdout)
                    if result.stderr:
                        st.code(result.stderr)

    st.markdown("---")

    if os.path.exists("json_output.json"):
        def load_json_text() -> str:
            try:
                with open("json_output.json", "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                return ""

        if "json_text" not in st.session_state:
            st.session_state.json_text = load_json_text()

        st.subheader("JSON Output")
        json_text = st.text_area("Edit JSON", height=300, key="json_text")

        col_json_a, col_json_b = st.columns(2)
        with col_json_a:
            if st.button("Save JSON"):
                try:
                    json_data = json.loads(json_text)
                except json.JSONDecodeError as ex:
                    st.error(f"Invalid JSON: {ex}")
                else:
                    with open("json_output.json", "w", encoding="utf-8") as f:
                        f.write(json.dumps(json_data, ensure_ascii=False, indent=2))
                    st.session_state.json_text = json.dumps(json_data, ensure_ascii=False, indent=2)
                    st.success("JSON saved.")

        with col_json_b:
            st.download_button(
                label="Download JSON",
                data=json_text,
                file_name="json_output.json",
                mime="application/json"
            )

    if os.path.exists("sql_output.sql"):
        def load_sql_text() -> str:
            try:
                with open("sql_output.sql", "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                return ""

        if "sql_text" not in st.session_state:
            st.session_state.sql_text = load_sql_text()

        st.subheader("SQL Output")
        sql_text = st.text_area("Edit SQL", height=240, key="sql_text")

        col_sql_a, col_sql_b = st.columns(2)
        with col_sql_a:
            if st.button("Save SQL"):
                with open("sql_output.sql", "w", encoding="utf-8") as f:
                    f.write(sql_text)
                st.success("SQL saved.")

        with col_sql_b:
            st.download_button(
                label="Download SQL",
                data=sql_text,
                file_name="sql_output.sql",
                mime="text/sql"
            )

    pptx_output = "New_Profile_Final.pptx"
    if os.path.exists(pptx_output):
        with open(pptx_output, "rb") as f:
            pptx_bytes = f.read()
        st.subheader("PPTX Output")
        st.download_button(
            label="Download PPTX",
            data=pptx_bytes,
            file_name=pptx_output,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

    st.markdown("---")

    st.subheader("Download to your computer")
    st.caption("Creates a ZIP with JSON + SQL + PPTX and downloads it via your browser.")

    download_name = st.text_input("Download name", key="download_name", value="export")
    if st.button("Prepare download (ZIP)"):
        zip_bytes, zip_name_or_error = build_export_zip_bytes(download_name or "export")
        if not zip_bytes:
            st.error(zip_name_or_error)
        else:
            st.session_state.export_zip_bytes = zip_bytes
            st.session_state.export_zip_name = zip_name_or_error
            st.success("Download ready.")

    if "export_zip_bytes" in st.session_state and st.session_state.export_zip_bytes:
        st.download_button(
            label="Download ZIP",
            data=st.session_state.export_zip_bytes,
            file_name=st.session_state.get("export_zip_name", "export.zip"),
            mime="application/zip"
        )

    st.markdown("---")
    st.subheader("Export to folder")
    if "export_stage" not in st.session_state:
        st.session_state.export_stage = "idle"

    if st.button("Export to folder"):
        if not os.path.exists("json_output.json"):
            st.error("json_output.json not found. Generate or save JSON first.")
        else:
            st.session_state.export_stage = "confirm"

    if st.session_state.export_stage == "confirm":
        st.info("Is the JSON above the one you want to use for export?")
        col_confirm_a, col_confirm_b = st.columns(2)
        with col_confirm_a:
            if st.button("Yes, continue"):
                st.session_state.export_stage = "name"
        with col_confirm_b:
            if st.button("No, cancel"):
                st.session_state.export_stage = "idle"

    if st.session_state.export_stage == "name":
        export_name = st.text_input("Export name", key="export_name")
        if st.button("Create export"):
            raw_name = export_name.strip()
            if raw_name and not raw_name.endswith("."):
                raw_name = f"{raw_name}."
            safe_name = sanitize_export_name(raw_name)
            if not raw_name:
                st.error("Please enter a name for the export folder.")
            else:
                sql_result = run_script("json_to_sql.py")
                if sql_result.returncode != 0 or not os.path.exists("sql_output.sql"):
                    st.error("SQL generation failed during export.")
                else:
                    ok, msg = build_pptx_with_title_suffix(raw_name)
                    if not ok:
                        st.error(msg)
                    else:
                        if not os.path.exists(pptx_output):
                            st.error("PPTX file not found after generation.")
                        else:
                            target_dir = os.path.join("profiles_to_insert", safe_name)
                            os.makedirs(target_dir, exist_ok=True)

                            pptx_named = f"New_Profile_Final({safe_name}).pptx"

                            shutil.copy2("json_output.json", os.path.join(target_dir, "json_output.json"))
                            shutil.copy2("sql_output.sql", os.path.join(target_dir, "sql_output.sql"))
                            shutil.copy2(pptx_output, os.path.join(target_dir, pptx_named))
                            st.success(f"Exported to {target_dir}.")
                            st.session_state.export_stage = "idle"


if selected_page == "Catalogue":
    render_catalogue_page()
else:
    render_test_tool_page()