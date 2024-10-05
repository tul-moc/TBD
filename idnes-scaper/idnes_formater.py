from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, "cs_CZ.UTF-8")

def create_formatted_date(original_date):
    try:
        if original_date is None:
            return None

        date_string = original_date.split(',')[0].strip()
        if date_string is None:
            return None
        
        if len(date_string.split()) == 4:
            parsed_date = datetime.strptime(date_string, '%d. %B %Y %H:%M')
        else:
            parsed_date = datetime.strptime(date_string, '%d. %B %Y')
            parsed_date = parsed_date.replace(hour=0, minute=0)

        return parsed_date.isoformat()
    except Exception as e:
        print(f"Error getting formatted created date: {e}")
        return None