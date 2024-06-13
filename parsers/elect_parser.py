import requests
from bs4 import BeautifulSoup
import re
from helpers.helpers import armenian_date_to_ymd
from helpers.db import upsert_elect
def get_data(url):
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract the article content
        article = soup.find('article')
        if article:
            spans = article.find_all('span', recursive=False)
            cleaned_text = []

            for span in spans:
                text = span.get_text(separator="", strip=True)
                cleaned_text.append(text)

            return "\n".join(cleaned_text)
        else:
            return "No article found."
    else:
        return f"Failed to fetch the URL: {response.status_code}"


def extract_segments(article_text):
    start_phrase = "Երևան քաղաք՝"
    end_phrase = "մարզ"

    # Create a regex pattern to find all segments and their corresponding dates
    segment_date_pattern = re.compile(
        f"«Հայաստանի էլեկտրական ցանցեր» փակ բաժնետիրական ընկերությունը տեղեկացնում է, որ(.*?)պլանային նորոգման աշխատանքներ իրականացնելու.*?({re.escape(start_phrase)}.*?{re.escape(end_phrase)})",
        re.DOTALL
    )

    matches = segment_date_pattern.finditer(article_text)

    segments_with_dates = []
    for match in matches:
        date = match.group(1).strip()
        segment = match.group(2).strip()
        last_comma_index = segment.rfind(",")
        if last_comma_index != -1:
            segment = segment[:last_comma_index]
        segments_with_dates.append({"content": segment, "date": date})

    if segments_with_dates:
        return segments_with_dates
    else:
        return [{"content": "Segment not found.", "date": "Date not found."}]

    
def extract_data(segment):
    segment = re.sub(r'\s+', ' ', segment)
    pattern = r"(\d{2}։\d{2}-\d{2}:\d{2})"

    # matches = re.findall(pattern, segment, re.DOTALL | re.MULTILINE)
    splits = re.split(pattern, segment)
    results = []
    for i in range(1, len(splits), 2):
        r = {}
        r['time'] = splits[i]
        r['streets'] = splits[i + 1]
        results.append(r)
    return results
    # Extract time
    # time_matches = re.findall(r'\b\d\s*\d\s*։\s*\d{2}-\d\s*\d\s*:\s*\d\s*\d\b', segment)
    # if time_matches:
    #     start_time, end_time = time_matches[0]
    #     time = f"{start_time}-{end_time}"
    # else:
    #     time = "Time not found"

    # Extract street names
    # street_matches = re.findall(r'[Ա-ՖԱ-ֆ\s\d-]+[^\d\s-]', segment)
    # streets = ' '.join(street_matches)

def run():
    total_count = 0
    url = 'https://www.ena.am/Info.aspx?id=5&lang=1'  # Replace with the URL you want to scrape
    data = get_data(url)
    segment = extract_segments(data)
    for i in segment:
        i['date'] = armenian_date_to_ymd(i["date"])
        result = extract_data(i["content"])
        # print(result)
        total_count += len(result)
        for j in result:
            # print(j['time'])
            # print(i['time'])
            # print(j['streets'])
            upsert_elect(i['date'], j['time'], j['streets'], "Երևան")
        # print(result)
    print("total elect count: " + str(len(result)))
# run()
