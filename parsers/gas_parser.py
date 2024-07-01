import requests
from bs4 import BeautifulSoup
import re
from helpers.helpers import armenian_date_to_ymd
from helpers.db import upsert_gas

def get_data(url):
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        content = soup.find(class_='page_text_cont').get_text()
        pattern = r'Պլանային աշխատանքներ իրականացնելու նպատակով՝(.*?)։'

        matches = re.finditer(pattern, content, re.DOTALL)
        results = []

        for match in matches:
            match_group = match.group(0)
            if "Երևան" in match_group:
                results.append(' '.join(match_group.split()[4:]))

        return results
    else:
        return f"Failed to fetch the URL: {response.status_code}"

def format_data(data):
    formated_data = []
    for i in data:
        row = {}
        date = re.match(r'^\S+ \S+', i).group()
        row["message"] = re.sub(r'^\S+ \S+ ', '', i)
        # row["message"] = row["message"].replace("-ից մինչև ժամը ", ":")
        row["date"] = armenian_date_to_ymd(date)
        # matches = re.split(r'(կդադարեցվի )', row["message"])

        # first_string = matches[0] + matches[1]
        # second_string = matches[2]
        # first_string = first_string.replace('ժամը ', '')
        # first_string = first_string.replace('ից մինչև ', '')
        # first_string = first_string.replace('-ն, կդադարեցվի ', '')
        # row["time"] = first_string
        # row["message"] = second_string
        formated_data.append(row)
    return formated_data

url = 'https://armenia-am.gazprom.com/notice/announcement/plan/'
def run():
    data = get_data(url)
    data = format_data(data)
    print("total gas count: " + str(len(data)))
    for row in data:
        upsert_gas(row['date'], row['message'], "Երևան")
    # for index, item in enumerate(panel_group_items):
    #     details = parse_string(item)
    #     # print(details['post_id'])
    #     print(upsert(details))
