import json
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def generate_exact_lop():
    # 1. Read CSV
    try:
        df = pd.read_csv('Final_Campaign_List.csv')
    except FileNotFoundError:
        print("Error: Please ensure 'Final_Campaign_List.csv' is in the folder.")
        return

    # 2. Clean Data
    df = df.fillna('')
    
    participants = []
    for _, row in df.iterrows():
        # Build Name
        salutation = str(row.get('Salutation', '')).strip()
        first = str(row.get('First Name', '')).strip()
        last = str(row.get('Last Name', '')).strip()
        
        # Skip empty rows
        if not last: continue

        full_name = f"{salutation} {first} {last}".strip()

        # Build Title
        title = str(row.get('Title', '')).strip()
        org = str(row.get('Organization', '')).strip()
        
        if title and org:
            details = f"{title}, {org}"
        else:
            details = f"{title}{org}"

        participants.append({'name': full_name, 'details': details})

    # 3. Load optional event metadata (event_info.json) and render Template
    event_defaults = {
        'event_title': "A Conversation with Kataeb Party’s Samy Gemayel",
        'event_date': "Wednesday, November 19, 2025",
        'event_time': "2:00 PM - 3:30 PM ET",
        'venue_name': "Middle East Institute",
        'venue_address': "1763 N St. NW\nWashington, DC 20036",
        'logo_path': '',
        'top_right_label': '',
    }

    event_file = Path('event_info.json')
    if event_file.exists():
        try:
            with open(event_file, 'r', encoding='utf-8') as ef:
                event_data = json.load(ef)
                # Merge defaults with provided metadata
                for k, v in event_defaults.items():
                    if k in event_data and event_data[k]:
                        event_defaults[k] = event_data[k]
        except Exception as e:
            print(f"Warning: failed to read event_info.json: {e}. Using defaults.")

    env = Environment(loader=FileSystemLoader('.'))
    try:
        # Make sure you saved the HTML above as 'lop_template_exact.html'
        template = env.get_template('lop_template_exact.html')
    except Exception as e:
        print(f"Error: Could not find template file. {e}")
        return

    html_output = template.render(participants=participants,
                                  event_title=event_defaults['event_title'],
                                  event_date=event_defaults['event_date'],
                                  event_time=event_defaults['event_time'],
                                  venue_name=event_defaults['venue_name'],
                                  venue_address=event_defaults['venue_address'],
                                  logo_path=event_defaults.get('logo_path', ''),
                                  top_right_label=event_defaults.get('top_right_label', ''))

    # 4. Output
    with open('Final_LOP_Exact.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print("✅ Generated 'Final_LOP_Exact.html' matching the uploaded style.")

if __name__ == "__main__":
    generate_exact_lop()