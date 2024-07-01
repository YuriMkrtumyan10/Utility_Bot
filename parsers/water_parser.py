import subprocess
from bs4 import BeautifulSoup
from datetime import datetime
import re
from helpers.constants import armenian_months, districts
from helpers.helpers import get_key_by_value
from helpers.db import upsert_water

def get_data(url):
    today = datetime.today()
    day = today.day 
    month = armenian_months[today.month - 1] + 'ի'
    today_armenian = f"{month} {day}-ին"

    print(day)
    all_panel_group_texts = []
    page = 1
    found_today = True
    
    while found_today:
        paginated_url = f"{url}?page={page}"
        
        # Use wget to fetch the HTML content with specific User-Agent header
        wget_command = ['wget', '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', '-qO-', paginated_url]
        
        try:
            html_content = subprocess.run(wget_command, capture_output=True, text=True, check=True).stdout
        except subprocess.CalledProcessError as e:
            print(f"Failed to retrieve the page '{paginated_url}'. Error: {e}")
            found_today = False
            continue
        
        soup = BeautifulSoup(html_content, 'html.parser')
        panel_groups = soup.find_all(class_='panel-group')
        
        matched_panels = [
            panel for panel in panel_groups 
            if today_armenian in panel.get_text(strip=True) 
            and "Երևան" in panel.get_text(strip=True)
        ]
        
        if not matched_panels:
            found_today = False
        else:
            panel_group_data = [
                {"id": panel.get("id"), "text": panel.get_text(strip=True)} for panel in matched_panels
            ]
            all_panel_group_texts.extend(panel_group_data)
            page += 1
    
    return all_panel_group_texts

def parse_string(panel):
    details = {}
    message = panel["text"]
    match = re.search(r'Երևանի (.*?) վարչական', message)
    
    if match:
        details["post_id"] = panel["id"].replace("accordion", "")
        details['state'] = 0
        details['type'] = 1
        details['city'] = 0
        details['province'] = get_key_by_value(districts, match.group(1))
        
        street_message = re.search(r'կդադարեցվի (.*)ջրամատակարարումը', message.replace("\xa0", " ")).group(1)
        details['streets'] = ' '.join(street_message.strip().split())
        details['full_message'] = message
    
    return details

url = 'https://interactive.vjur.am'  # Replace with the URL you want to scrape
panel_group_items = get_data(url)

def run():
    print("total water count: " + str(len(panel_group_items)))
    for index, item in enumerate(panel_group_items):
        details = parse_string(item)
        upsert_water(details)
