from datetime import datetime, timedelta
import re

def get_key_by_value(dictionary, search_value):
    return next((key for key, value in dictionary.items() if value == search_value), None)

def parse_date_time(date_string):
    # Define months in Armenian
    months_armenian = {
        "հունվար": 1, "փետրվար": 2, "մարտ": 3, "ապրիլ": 4, 
        "մայիս": 5, "հունիս": 6, "հուլիս": 7, "օգոստոս": 8, 
        "սեպտեմբեր": 9, "հոկտեմբեր": 10, "նոյեմբեր": 11, "դեկտեմբեր": 12
    }
    
    # Define regex pattern to extract information
    pattern = r"(\d+)-ին (\w+)ի (\d+)-ը ժամը (\d+):(\d+)-ից մինչև (\w+)ի (\d+)-ը (\d+):(\d+)-ն"
    match = re.match(pattern, date_string)
    
    if match:
        day_start = int(match.group(1))
        month_start = months_armenian[match.group(2)]
        hour_start = int(match.group(3))
        minute_start = int(match.group(4))
        
        day_end = int(match.group(6))
        month_end = months_armenian[match.group(5)]
        hour_end = int(match.group(7))
        minute_end = int(match.group(8))
        
        # Create datetime objects
        start_date = datetime(datetime.now().year, month_start, day_start, hour_start, minute_start)
        end_date = datetime(datetime.now().year, month_end, day_end, hour_end, minute_end)
        
        # Adjust end date if it is before the start date
        if end_date < start_date:
            end_date += timedelta(days=1)
        
        return start_date, end_date
    else:
        return None, None
