import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import sqlite3

# conn = sqlite3.connect('utility_project.db')
# cursor = conn.cursor()


# def upsert(item):
#     cursor.execute("INSERT INTO outages (state, city, province, streets, post_id, type) VALUES (?, ?, ?, ?, ?, ?);",
#                     (item['state'], item['city'], item['province'], item['streets'], item['post_id'], item['type']))

#     return conn.commit()


# constants
armenian_months = [
    "Հունվար", "Փետրվար", "Մարտ", "Ապրիլ", "մայիսի", "Հունիս", 
    "Հուլիս", "Օգոստոս", "Սեպտեմբեր", "Հոկտեմբեր", "Նոյեմբեր", "Դեկտեմբեր"
]

districts = {
    0: "Աջափնյակ",
    1: "Ավան",
    2: "Արաբկիր",
    3: "Դավթաշեն",
    4: "Էրեբունի",
    5: "Կենտրոն",
    6: "Մալաթիա-Սեբաստիա",
    7: "Նոր Նորք",
    8: "Նորք-Մարաշ",
    9: "Նուբարաշեն",
    10: "Շենգավիթ",
    11: "Քանաքեռ-Զեյթուն"
}

# helpers
def get_key_by_value(dictionary, search_value):
    return next((key for key, value in dictionary.items() if value == search_value), None)

def get_panel_group_items_with_date(url):
    response = requests.get(url)
    
    # Get today's date
    today = datetime.today()
    day = 30 #today.day
    month = armenian_months[today.month - 1]
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
            
            # Filter elements that contain today's date in Armenian
            matched_panels = [
                panel for panel in panel_groups 
                if today_armenian in panel.get_text(strip=True) and "Երևան" in panel.get_text(strip=True)
            ]
            # If no panels matched, stop the loop
            if not matched_panels:
                found_today = False
            else:
                # Extract the text from each matched panel

                panel_group_data = [
                    {"id": panel.get("id"), "text": panel.get_text(strip=True)} for panel in matched_panels
                ]

                all_panel_group_texts.extend(panel_group_data)
                
                # Move to the next page
                page += 1
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            found_today = False
    
    return all_panel_group_texts

# def extract_details(text):
#     state = re.compile(r'Վթարային ջրանջատում (\w+)')

#     # city_and_region_regex = re.compile(r'Վթարային ջրանջատում\s+(\S+)\s+(\S+)\s+վարչական շրջանում')
#     # time_regex = re.compile(r'ժամը\s+(\d{2}:\d{2})-(\d{2}:\d{2})')
#     # street_regex = re.compile(r'([\u0531-\u0556\u0561-\u0587]+\s+\d+\s*փ\.\s+\d+\s*[\u0531-\u0556\u0561-\u0587]*)')

#     state = state.search(text)
#     # time = time_regex.search(text)
#     # street = street_regex.search(text)

#     details = {
#         "state": state.group(1)[:-1]
#         # "city": city_and_region.group(1) if city_and_region else None,
#         # "region": city_and_region.group(2) if city_and_region else None,
#         # "time_start": time.group(1) if time else None,
#         # "time_end": time.group(2) if time else None,
#         # "street": street.group(0) if street else None
#     }
    
#     return details

def parse_string(panel):
    # match = re.search(r'Վթարային ջրանջատում (\S+) (?:մարզի)?', string)
    # if match:
    #     details = {}
    #     location = match.group(1)
    #     if 'մարզ' in string:
    #         details['state'] = location[:-1]
    #         details['city'] = None
    #     else:
    #         details['state'] = location[:-1]
    #         details['city'] = location[:-1]

    #     village_match = re.search(r'(\S+) գյուղում', string)
    #     if village_match:
    #         village = village_match.group(1)
    #         details['village'] = village
        
    #     if 'քաղաքում' in string:
    #         city_match = re.search(r'(\S+) քաղաքի (.*) ', string)
    #         # print(city)
    #         if city_match:
    #             details['city'] = city_match.group(1)
    #             details['address'] = city_match.group(2)
            
    #     return details
    details = {}
    message = panel["text"]
    print(id)
    match = re.search(r'Երևանի (\S+)', message)
    if match:
        details["post_id"] = panel["id"].replace("accordion", "")
        details['state'] = 0
        details['type'] = 1
        details['city'] = 0
        details['province'] = get_key_by_value(districts, match.group(1))
        message = re.search(r'կդադարեցվի (.*)ջրամատակարարումը', message.replace("\xa0", " ")).group(1)
        details['streets'] = message = ' '.join(message.strip().split())
        # details['streets'] = re.split(r', (?!\d)', message)


    return details

# Example usage
url = 'https://www.ena.am/Info.aspx?id=5&lang=1'  # Replace with the URL you want to scrape
panel_group_items = get_panel_group_items_with_date(url)

# Extract and print the details from each panel group item
for index, item in enumerate(panel_group_items):
    details = parse_string(item)
#     print(upsert(details))
# conn.close()
