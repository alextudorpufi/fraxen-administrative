import json

# The JSON output you provided
# JSON_INPUT = {
#     "title": "Senior HR Leader | Strategic HR Practitioner",
#     "gender": "Female",
#     "experience_summary": "20+ years global HR leadership across diverse industries.",
#     "sector_focus": "FMCG, Manufacturing, Banking, Consulting",
#     "location": "Romania (Remote/Hybrid)",
#     "experience": [
#         {
#             "job_title": "Managing Partner",
#             "description": "Founder of a strategic HR consulting firm, driving organizational excellence.",
#             "achievements": [
#                 "Provides strategic advisory in HR transformation, talent development, and organizational design.",
#                 "Leads initiatives for optimizing workforce performance and cultural alignment."
#             ]
#         },
#         {
#             "job_title": "Group HR Director",
#             "description": "Executive at a large industrial conglomerate, overseeing HR across multiple entities.",
#             "achievements": [
#                 "Directed HR strategy across 27 entities, aligning people operations with group-wide transformation.",
#                 "Negotiated and implemented 7 Collective Labor Agreements, ensuring labor harmony.",
#                 "Designed and rolled out a new Group Compensation & Benefits strategy, enhancing retention."
#             ]
#         },
#         {
#             "job_title": "Group HR Director",
#             "description": "Senior HR leader at a global dairy industry leader, managing country-wide HR functions.",
#             "achievements": [
#                 "Led HR integration of 4 acquired groups, 8 factories, and multiple commercial teams.",
#                 "Managed €40M HR annual budget, contributing to a 14.2% increase in FCF over 5 years.",
#                 "Reduced voluntary turnover from 25.5% to 10% and improved engagement to 82%."
#             ]
#         },
#         {
#             "job_title": "Senior Regional HR Manager",
#             "description": "Regional HR leader at a global Fortune 500 manufacturing company, driving EMEA HR strategy.",
#             "achievements": [
#                 "Progressed through multiple roles, coordinating HR strategy across a region of 10 countries.",
#                 "Led HR strategy, workforce transformation, and organizational design projects across 22 countries.",
#                 "Served as EMEA Compensation & Benefits Subject Matter Expert, managing annual compensation cycles across 13 countries."
#             ]
#         }
#     ],
#     "core_strengths": [
#         "HR Strategy & Transformation",
#         "Organizational Design & Workforce Optimization",
#         "Compensation & Benefits (EMEA SME)",
#         "Industrial & Employee Relations"
#     ]
# }

def escape_sql(text: str) -> str:
    """Escapes single quotes for SQL insertion."""
    return text.replace("'", "''")

def generate_sql_script(data: dict, placeholder_id: str = "[EXECUTIVE_ID_PLACEHOLDER]") -> str:
    """
    Converts the structured executive JSON data into a series of SQL INSERT statements.
    
    Args:
        data: The structured JSON dictionary of the executive profile.
        placeholder_id: A placeholder string for the foreign key (executive_id).
        
    Returns:
        A single string containing all SQL INSERT statements.
    """
    sql_script = []
    
    # 1. INSERT INTO executives (Primary Table)
    # The primary table holds the summary data
    executives_insert = f"""
INSERT INTO executives (title, gender, experience, sector_focus, location)
VALUES (
    '{escape_sql(data['title'])}',
    '{escape_sql(data['gender'])}',
    '{escape_sql(data['experience_summary'])}',
    '{escape_sql(data['sector_focus'])}',
    '{escape_sql(data['location'])}'
);

-- NOTE: The ID below must be updated manually after the first INSERT executes and returns the new ID.
"""
    sql_script.append(executives_insert)
    
    # 2. INSERT INTO executive_highlights (Experience Details)
    # This table requires a loop through the 'experience' list
    highlights_inserts = []
    for i, exp in enumerate(data['experience'], start=1):
        # Join the achievements into a single string, separating lines with \n
        details = "\\n".join(exp['achievements'])
        
        insert_statement = f"""
INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
({placeholder_id}, '{escape_sql(exp['job_title'])}', '{escape_sql(exp['description'])}',
'{escape_sql(details)}',
{i});
"""
        highlights_inserts.append(insert_statement)
        
    sql_script.append("".join(highlights_inserts))

    # 3. INSERT INTO executive_strengths (Core Strengths)
    # This table requires a loop through the 'core_strengths' list
    strengths_inserts = []
    for i, strength in enumerate(data['core_strengths'], start=1):
        insert_statement = f"""
INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
({placeholder_id}, '{escape_sql(strength)}', {i});
"""
        strengths_inserts.append(insert_statement)
        
    sql_script.append("".join(strengths_inserts))
    
    return "\n".join(sql_script).strip()

# --- Execution ---
if __name__ == "__main__":

    json_input_path = "json_output.json"
    with open(json_input_path, 'r', encoding='utf-8') as file:
        raw_json_input = file.read()
        json_input = json.loads(raw_json_input)
        sql_output = generate_sql_script(json_input)
    
    print("--- Generated SQL Insertion Script ---")
    sql_output_path = "sql_output.sql"
    with open(sql_output_path, 'w') as file:
        file.write(sql_output)
        # print(sql_output)
    
    print("\n" + "="*50)
    print("### ⚠️ Action Required:")
    print("Replace all instances of '[EXECUTIVE_ID_PLACEHOLDER]' with the actual ID generated by the first INSERT statement (INSERT INTO executives).")