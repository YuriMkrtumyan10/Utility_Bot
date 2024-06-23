import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from helpers.constants import armenian_months, districts
from helpers.helpers import get_key_by_value
from helpers.db import upsert_water

def get_data(url):
    response = requests.get(url)
    
    today = datetime.today()
    day = today.day - 2 
    month = armenian_months[today.month - 1] + 'ի'
    today_armenian = f"{month} {day}-ին"

    all_panel_group_texts = []
    page = 1
    found_today = True
    
    while found_today:
        paginated_url = f"{url}?page={page}"
        
        response = requests.get(paginated_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            found_today = False
    
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
        
        
        # date time moment 
        # match = re.search(r'(\d{2}:\d{2})-(\d{2}:\d{2})', panel["text"])

        # if match:
        #     details['start'] = match.group(1)
        #     details['end'] = match.group(2)
        # else:
        #     # start_date_str, end_date_str = 
        #     date_soup = re.search(r'ս\.թ (.*?) կդադարեցվի', message)
        #     print(date_soup.group(1))
        #     start_date, end_date = parse_date_time(date_soup.group(1))
        #     print(start_date, end_date)
        #     # print(start_date_str)
        #     # print(end_date_str)

    return details

#         # details['streets'] = re.split(r', (?!\d)', message)

url = 'https://interactive.vjur.am'  # Replace with the URL you want to scrape
panel_group_items = get_data(url)
def run():
    print("total water count: " + str(len(panel_group_items)))
    for index, item in enumerate(panel_group_items):
        details = parse_string(item)
        # print(details['post_id'])
        upsert_water(details)
        # print(details['city'])
        # print(details['streets'])
