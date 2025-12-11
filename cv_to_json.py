import os
import json
from google import genai
from google.genai import types

# --- CONFIGURATION ---
CV_FILE_PATH = "cv_text.txt"
# API_KEY = "write_your_api_key_here" # REPLACE THIS with your actual Gemini API Key
try:
    with open("api_key.txt", "r") as f:
        API_KEY = f.read().strip() # .strip() removes invisible newlines or spaces
except FileNotFoundError:
    print("Error: 'api_key.txt' file not found. Please create it and paste your key inside.")
    exit()
MODEL_NAME = "gemini-2.5-flash"

def read_cv_file(file_path: str) -> str:
    """Reads the CV text from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print("Please create the file and paste the CV content into it.")
        exit(1)

def create_gemini_payload_config() -> tuple[str, types.GenerateContentConfig]:
    """
    Creates the system prompt and configuration object for the Gemini API call 
    to perform structured CV parsing with strict anonymization.
    """
    
    # 1. Define the desired output structure (JSON Schema)
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "title": types.Schema(type=types.Type.STRING, description="The highest-level functional title or primary role of the candidate (e.g., Fractional CFO | Strategic Financial Leader)."),
            "gender": types.Schema(type=types.Type.STRING, description="The candidate's gender."),
            "experience_summary": types.Schema(type=types.Type.STRING, description="A generalized summary of the candidate's total experience, focusing on tenure and type of firm (e.g., 20+ years, Global consulting firm background). Must NOT include specific company names or brand names like 'Big4'. Must be of maximum 10 words"),
            "sector_focus": types.Schema(type=types.Type.STRING, description="The primary industry sectors the candidate focuses on."),
            "location": types.Schema(type=types.Type.STRING, description="The candidate's general geographic region and availability (e.g., North America (Remote/Hybrid)). Must NOT include city names, but can include country names."),
            "experience": types.Schema(
                type=types.Type.ARRAY,
                description="A list of key roles and professional achievements. Must find minimum 3 or maximum 4 in total",
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "job_title": types.Schema(type=types.Type.STRING, description="The functional title of the role or section. Must NOT include company name or specific dates."),
                        "description": types.Schema(type=types.Type.STRING, description="The generalized context of the role (e.g., Executive at a Leading Technology Group, Board Member at a Private Equity Fund). Must NOT include the company's specific name. Must use attractive, MVP terms"),
                        "achievements": types.Schema(
                            type=types.Type.ARRAY,
                            description="A list of quantified and critical achievements for this role. Ensure quantifiable metrics remain but unique project names are generalized. Must find atleast 2 or maximum 3 in total.",
                            items=types.Schema(type=types.Type.STRING)
                        )
                    },
                    required=["job_title", "description", "achievements"]
                )
            ),
            "core_strengths": types.Schema(
                type=types.Type.ARRAY,
                description="A list of minimum 3, maximum 4 high-level core competencies or skills.",
                items=types.Schema(type=types.Type.STRING)
            )
        },
        required=["title", "gender", "experience_summary", "sector_focus", "location", "experience", "core_strengths"]
    )

    # 2. Define the System Instruction (The model's persona and rules)
    system_prompt = (
        "You are an expert CV parser and recruiter assistant focused on creating highly anonymized candidate profiles. "
        "Your task is to extract all relevant information from the provided unstructured CV text and format it STRICTLY "
        "according to the given JSON Schema. "
        "CRITICAL RULE: NEVER include specific company names, client names, names of unique organizations (like 'Big4' or 'Innovation Fund'), "
        "or exact date ranges (e.g., 2020 – Present, 2018-2020) in the final JSON output. "
        "You MUST generalize all identifiable data: replace company names with generic industry types (e.g., 'Leading SaaS Provider'), "
        "replace date ranges with approximate tenure (e.g., '10+ Years'), and replace unique group names with functional descriptions."
    )
    
    # 3. Construct the Configuration
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        response_schema=response_schema,
        temperature=0.0 # Use low temperature for deterministic parsing tasks
    )

    return system_prompt, config

def call_gemini_api(cv_text: str, api_key: str):
    """Initializes the client and calls the Gemini API."""
    print("--- 🤖 Gemini API Call ---")
    
    if api_key == "write_your_api_key_here":
        print("!!! WARNING: Please replace 'write_your_api_key_here' with your actual API key.")
        print("Cannot proceed with API call.")
        return

    # Initialize the client with the provided API Key
    client = genai.Client(api_key=api_key)
    
    # Get the configuration
    system_prompt, config = create_gemini_payload_config()

    print(f"Model: {MODEL_NAME}")
    print(f"System Instruction: '{system_prompt[:80]}...'")
    print("Sending request for structured, anonymized JSON output...")

    try:
        # Call the API
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[cv_text],
            config=config
        )

        print("\n--- ✅ Anonymized and Structured JSON Output from Gemini ---")
        
        # The response text will be a JSON string due to the config
        # We parse it and print it with indentation for readability
        json_output = json.loads(response.text)
        output_path = "json_output.json"
        with open(output_path, 'w') as f:
            f.write(json.dumps(json_output, indent=4))

        # print(json.dumps(json_output, indent=4))
        
    except Exception as e:
        print(f"\n--- ❌ ERROR DURING API CALL ---")
        print(f"An error occurred: {e}")
        print("Please check your API key, network connection, and ensure the SDK is installed.")


if __name__ == "__main__":
    print(f"--- 📄 CV Parser and Anonymizer ---")
    
    # 1. Read CV from file
    cv_text = read_cv_file(CV_FILE_PATH)
    print(f"Successfully read CV content from '{CV_FILE_PATH}'.\n")
    
    # 2. Call the Gemini API
    call_gemini_api(cv_text, API_KEY)
    
    print("\n" + "="*50)
    print("Process Complete. The output is the structured, anonymized CV profile.")
    # Would you like me to run the regex-based parsing to compare the outputs?