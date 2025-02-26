def extract_year_range(year_range_str):
    """
    Extracts only the first Gregorian year from a string containing both
    Gregorian and Buddhist years.

    Args:
        year_range_str (str): Input string (e.g., "2023 - 2024 (2566 - 2567)").

    Returns:
        str: The first Gregorian year (e.g., "2023").
    """
    # Split out the Gregorian part (before '(')
    gregorian_part = year_range_str.split('(')[0].strip()
    # Split by '-' and take the first year
    first_year = gregorian_part.split('-')[0].strip()
    return first_year


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


# ใน helpers/function.py

def extract_start_time_range(time_range):
    """
    ดึงเวลาเริ่มต้นจากช่วงเวลาที่ให้มา

    Parameters:
    time_range (str): ช่วงเวลาที่มีรูปแบบ "HH:MM - HH:MM"

    Returns:
    str or None: เวลาเริ่มต้นในรูปแบบ "HH:MM" หรือ None หากไม่สามารถแยกได้
    """
    # ตรวจสอบว่าค่า time_range เป็นสตริงหรือไม่
    if isinstance(time_range, str):
        # ค้นหาตำแหน่งของขีด (-) ในสตริง
        dash_index = time_range.find("-")
        # ตรวจสอบว่ามีขีด (-) อยู่ในสตริงหรือไม่
        if dash_index != -1:
            # ดึงสตริงก่อนขีด (-) และลบช่องว่างทั้งสองข้าง
            return time_range[:dash_index].strip()
    # คืนค่า None หากไม่ใช่สตริงหรือไม่มีขีด (-)
    return None  # หรือค่าเริ่มต้นอื่นๆ เช่น ''


def extract_end_time_range(time_range):
    """
    ดึงเวลาสิ้นสุดจากช่วงเวลาที่ให้มา

    Parameters:
    time_range (str): ช่วงเวลาที่มีรูปแบบ "HH:MM - HH:MM"

    Returns:
    str or None: เวลาสิ้นสุดในรูปแบบ "HH:MM" หรือ None หากไม่สามารถแยกได้
    """
    # ตรวจสอบว่าค่า time_range เป็นสตริงหรือไม่
    if isinstance(time_range, str):
        # ค้นหาตำแหน่งของขีด (-) ในสตริง
        dash_index = time_range.find("-")
        # ตรวจสอบว่ามีขีด (-) อยู่ในสตริงหรือไม่
        if dash_index != -1:
            # ดึงสตริงหลังขีด (-) และลบช่องว่างทั้งสองข้าง
            return time_range[dash_index + 1:].strip()
    # คืนค่า None หากไม่ใช่สตริงหรือไม่มีขีด (-)
    return None  # หรือค่าเริ่มต้นอื่นๆ เช่น ''

