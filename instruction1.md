# Outages Information Parsing for Yerevan City

## Input Text Format
- You will receive Armenian text containing information about outages in Yerevan city.
- The text includes street names with numbers and classifications (streets, houses, buildings), time of the outage, and optionally state and province information. There may be other important information as well.

## Custom Instructions
1. **Extract Street Information:**
   - Look for mentions of street names in the text.
   - Identify any associated numbers and classifications (streets, houses, buildings) with those streets. Include words like "նրբանցքներ" in the streets part.

2. **Identify Outage Time:**
   - Find mentions of the outage start and end times. This could be specific, meaning there might be different times for different streets, therefore you should be careful.
   - Extract the information in a structured format (e.g., YYYY-MM-DDTHH:mm).

3. **Extract City and Province Information:**
   - Look for a header-like section at the beginning of the text.
   - Extract the city and province information from this section. If the city is not mentioned in the header, look for the city name in the remaining text.

4. **Generate JSON Output:**
   - Create a JSON object with the following structure:
     ```json
     {
         "state": "Շրջան",
         "city": "Երևան",
         "province": "Արաբկիր",
         "outages": [
             {
                 "street": " ' Սայաթ-Նովա փողոց 23 Տներ', 'xxxx ## ', .... ",
                 "time": {
                     "start": "YYYY-MM-DDTHH:mm",
                     "end": "YYYY-MM-DDTHH:mm"
                 }
             },
             {
                 "street": "Մարաշ վարչական շրջան, Նորքի Այգիներ փողոցներ",
                 "time": {
                     "start": "YYYY-MM-DDTHH:mm",
                     "end": "YYYY-MM-DDTHH:mm"
                 }
             }
         ]
     }
     ```

5. **Handling Ambiguity:**
   - If there are ambiguous or unclear parts in the text, handle them appropriately. You can revise it twice to understand it better.

6. **Additional Notes:**
   - Exclude certain words like 'ջրամատակարարումը' and 'կդադարեցվի' from the street names.
   - If there is no province or state mentioned, do not include them in the JSON output.
   - If there are abbreviations like M. Saryan, do not expand them.
   - Do not make up any information if it is not explicitly mentioned in the text.

