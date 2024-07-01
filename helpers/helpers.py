from datetime import datetime, date

def get_key_by_value(dictionary, search_value):
    return next((key for key, value in dictionary.items() if value == search_value), None)


def armenian_date_to_ymd(date_str):
    armenian_months = {
        "հունվարի": 1,
        "փետրվարի": 2,
        "մարտի": 3,
        "ապրիլի": 4,
        "մայիսի": 5,
        "հունիսի": 6,
        "հուլիսի": 7,
        "օգոստոսի": 8,
        "սեպտեմբերի": 9,
        "հոկտեմբերի": 10,
        "նոյեմբերի": 11,
        "դեկտեմբերի": 12
    }

    parts = date_str.split()
    month_str = parts[0]
    day = int(parts[1][:-3])

    # Get the month number
    month = armenian_months[month_str]
    # Get the current year
    year = datetime.now().year

    # Create the date object
    date_obj = date(int(year), int(month), int(day))

    # Return the date in Y-m-d format
    return date_obj.strftime("%Y-%m-%d")
