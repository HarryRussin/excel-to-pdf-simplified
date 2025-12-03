# clean_data.py

import os
import json
import time
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# --- CONFIGURATION ---
INPUT_FILE = "input.csv"
OUTPUT_CLEAN_CSV = "Final_Campaign_List.csv"

# Load environment variables (API Key)
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API Key not found! Ensure you have a .env file with GOOGLE_API_KEY.")

genai.configure(api_key=API_KEY)
MODEL = genai.GenerativeModel('gemini-2.5-flash') 

def analyze_batch_with_gemini(csv_chunk):
    """Sends a small batch of rows to Gemini for smart cleaning and enrichment."""
    
    prompt = f"""
    You are a Data Processing Assistant. Transform the raw Salesforce CSV data into a clean JSON list.

    ### INPUT DATA (CSV format):
    {csv_chunk}

    ### RULES:
    1. **Salutation:** Infer this from the 'Job Title' (e.g., "Ambassador" -> "Amb.", "Dr.", "Mr.").
    2. **Title:** - If Title is missing (NaN/None), use your internal knowledge to **fill it in** if the person is a known public figure.
       - Clean the title (e.g., remove "Ambassador" if moved to Salutation).
    3. **Organization:** Clean the affiliation.
    4. **To Double Check:** If you filled in a missing Title from your knowledge, write "Inferred Title". Otherwise, leave blank.
       
    ### OUTPUT FORMAT:
    Return ONLY a JSON list of objects. Do not use markdown (```json).
    Keys MUST BE: "Salutation", "First Name", "Last Name", "Title", "Organization", "To Double Check"
    """
    
    try:
        response = MODEL.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"   ⚠️ Warning: Error processing batch: {e}. Skipping batch.")
        return []

def clean_and_enrich_data():
    """Reads CSV, runs Gemini enrichment, and saves the resulting DataFrame to CSV."""
    print("\n--- 1. Running Data Cleaning and Enrichment (Gemini API) ---")
    
    try:
        df = pd.read_csv(INPUT_FILE, skiprows=11)
    except Exception:
        print("Could not read with skiprows=11. Trying header=11.")
        df = pd.read_csv(INPUT_FILE, header=11)

    input_cols = ['First Name', 'Last Name', 'Job Title', 'Primary Affiliation']
    df = df[input_cols]

    all_rows = []
    batch_size = 15
    
    print(f"Processing {len(df)} records...")

    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        print(f"   - Sending batch {i} to {i+batch_size}...")
        
        processed_data = analyze_batch_with_gemini(batch.to_csv(index=False))
        all_rows.extend(processed_data)
        
        time.sleep(1)

    final_df = pd.DataFrame(all_rows)
    
    # Ensure correct column order before saving
    cols = ["Salutation", "First Name", "Last Name", "Title", "Organization", "To Double Check"]
    final_df = final_df[cols]
    
    final_df.to_csv(OUTPUT_CLEAN_CSV, index=False)
    print(f"✅ Data Enrichment Complete. Saved to {OUTPUT_CLEAN_CSV}")

if __name__ == "__main__":
    clean_and_enrich_data()