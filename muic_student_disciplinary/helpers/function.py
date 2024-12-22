def extract_year_range(year_range_str):
    """
    Extracts the Gregorian year range from a string containing both Gregorian
    and Buddhist years.

    Args:
        year_range_str (str): Input string (e.g., "2023 - 2024 (2566 - 2567)").

    Returns:
        str: Extracted Gregorian year range (e.g., "2023 - 2024").
    """
    # Split the input string to extract the Gregorian part
    gregorian_part = year_range_str.split('(')[0].strip()
    return gregorian_part


def thai_date_to_iso(thai_date_str):
    """
    Converts a Thai date string in the format 'D เดือน พ.ศ.' to ISO format 'YYYY-MM-DD'.
    
    Args:
        thai_date_str (str): Thai date string (e.g., '3 เม.ย. 2567').

    Returns:
        str: ISO date string (e.g., '2024-04-03').
    """
    # Month mapping for Thai months to English
    thai_to_english_months = {
        "ม.ค.": "01",
        "ก.พ.": "02",
        "มี.ค.": "03",
        "เม.ย.": "04",
        "พ.ค.": "05",
        "มิ.ย.": "06",
        "ก.ค.": "07",
        "ส.ค.": "08",
        "ก.ย.": "09",
        "ต.ค.": "10",
        "พ.ย.": "11",
        "ธ.ค.": "12"
    }

    # Split the date string
    day, thai_month, thai_year = thai_date_str.split()

    # Convert Thai year to Gregorian year
    gregorian_year = int(thai_year) - 543

    # Map the Thai month to English month
    month = thai_to_english_months[thai_month]

    # Format the date to "YYYY-MM-DD"
    formatted_date = f"{gregorian_year}-{month}-{int(day):02d}"

    return formatted_date


