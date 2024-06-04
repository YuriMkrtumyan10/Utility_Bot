import requests
from bs4 import BeautifulSoup
import re

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

def extract_segment(article_text):
    start_phrase = "Երևան քաղաք՝"
    end_phrase = "մարզ"

    start_index = article_text.find(start_phrase)
    end_index = article_text.find(end_phrase, start_index)

    if start_index != -1 and end_index != -1:
        segment = article_text[start_index:end_index + len(end_phrase)]
        last_comma_index = segment.rfind(",")
        if last_comma_index != -1:
            segment = segment[:last_comma_index]
        return segment
    else:
        return "Segment not found."

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
    url = 'https://www.ena.am/Info.aspx?id=5&lang=1'  # Replace with the URL you want to scrape
    data = get_data(url)
    segment = extract_segment(data)
    result = extract_data(segment)
    # print(result)
    for i in result:
        print(i['time'])
        # print('-------------')
        # print(i['time'])
        print(i['streets'])
    # print(result)
# run()
