def get_work_address_text(df_data):
    
    def extract_house_number(address):
        match = re.search(r'\d+', str(address))
        return match.group() if match else "no data"
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)

    # Use apply so that every row is processed.
    results = df_data['The address of your workplace (optional)'].apply(extract_house_number)
    
    # return df_data.apply(lambda row: results if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)
    return df_data.apply(lambda row: results.loc[row.name] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '',axis=1)


def get_work_address_moo_text(df_data):
     
    def extract_moo(address):
        """
        ดึงข้อมูล 'หมู่' (หรือ 'Moo') ตามด้วยตัวเลขจากที่อยู่
        รองรับทั้งคำว่า "หมู่", "หมู่ที่" และ "Moo"
        """
        
        # แปลง address เป็นสตริงเพื่อให้ re.search ทำงานได้
        address_str = str(address)
        # ใช้ pattern ที่รองรับทั้งภาษาไทยและอังกฤษ
        # (?:หมู่(?:ที่)?|Moo) จับคำว่า "หมู่", "หมู่ที่" หรือ "Moo" แล้วตามด้วยตัวเลข
        pattern = r'(?:หมู่(?:ที่)?|Moo)\s*(\d+)'
        match = re.search(pattern, address_str, flags=re.IGNORECASE)
        return match.group(1) if match else ""
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    
    # สร้าง Series สำหรับข้อมูลหมู่ โดยใช้ apply กับคอลัมน์ที่อยู่
    results = df_data['The address of your workplace (optional)'].apply(extract_moo)
    
    # คืนค่า Series สำหรับแต่ละแถว
    # ถ้าสถานะการทำงานไม่ใช่ '3' หรือ '4' ให้คืนค่า moo ที่สกัดได้จาก results
    # แต่ถ้าเป็น '3' หรือ '4' ให้คืนค่าว่าง ('')
    return df_data.apply(
        lambda row: results.loc[row.name] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '',
        axis=1
    )


def get_work_address_building_info(df_data):
    def extract_building_name(address):
        """
        สกัดชื่ออาคาร/ตึกจากที่อยู่
        โดยจับข้อความที่มีตัวอักษร (ไทย-อังกฤษ) ตามด้วยคำว่า
        "อาคาร", "ตึก", "Building" หรือ "Tower"
        โดยใช้ lookbehind (?<!\d) เพื่อไม่ให้รวมตัวเลขนำหน้า
        """
        if pd.isnull(address):
            return "no data"
        address_str = str(address)
        pattern = r'(?<!\d)([A-Za-zก-๙\s\-]+(?:อาคาร|ตึก|Building|Tower))'
        match = re.search(pattern, address_str, flags=re.IGNORECASE)
        return match.group(1).strip() if match else "no data"
    
    def extract_floor(address):
        """
        สกัดข้อมูลชั้นจากที่อยู่ โดยรองรับทั้งกรณีที่ตัวเลขอยู่ก่อนหรือหลังคำว่า "ชั้น" หรือ "Floor"
        ตัวอย่าง: "21st Floor" จะจับได้เป็น "21st" และ "ชั้น 3" จะจับได้เป็น "3"
        """
        if pd.isnull(address):
            return "no data"
        address_str = str(address)
        # ลองจับกรณีที่ตัวเลขอยู่ก่อนคำว่า Floor หรือ ชั้น
        pattern1 = r'([\d]+(?:st|nd|rd|th)?)\s*(?=Floor|ชั้น)'
        match = re.search(pattern1, address_str, flags=re.IGNORECASE)
        if match:
            return match.group(1)
        # ลองจับกรณีที่คำว่า Floor หรือ ชั้นมาก่อนแล้วตามด้วยตัวเลขหรือรหัส
        pattern2 = r'(?:Floor|ชั้น)\s*([\dA-Za-z]+)'
        match = re.search(pattern2, address_str, flags=re.IGNORECASE)
        if match:
            return match.group(1)
        return "no data"
    
    # เรียกใช้ฟังก์ชัน get_work_status_series (ที่มีอยู่ในโค้ดของคุณ) เพื่อดึงสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    
    # สกัดชื่ออาคารและชั้นจากคอลัมน์ที่อยู่
    building_names = df_data['The address of your workplace (optional)'].apply(extract_building_name)
    floors = df_data['The address of your workplace (optional)'].apply(extract_floor)
    
    def format_output(row):
        # ถ้าสถานะการทำงานเป็น '3' หรือ '4' คืนค่าว่าง
        if str(work_status_series.loc[row.name]) in ['3', '4']:
            return ''
        building = building_names.loc[row.name]
        floor = floors.loc[row.name]
        result = ""
        if building != "no data":
            result += f"{building}"
        if floor != "no data":
            result += f" {floor}"
        if result == "":
            result = "no data"
        return result
    
    return df_data.apply(format_output, axis=1)


def get_work_address_soi(df_data):
    def extract_soi(address):
        """
        ดึงข้อมูล 'ซอย' (หรือ 'Soi') ตามด้วยตัวอักษรหรือตัวเลข
        รูปแบบนี้จะค้นหาคำว่า "ซอย" หรือ "Soi" แล้วตามด้วยข้อความ (ตัวอักษรไทย, ตัวอักษรภาษาอังกฤษ, ตัวเลข, หรือขีดกลาง)
        """
        if pd.isnull(address):
            return "no data"
        address_str = str(address)
        # pattern: จับคำว่า ซอย หรือ Soi ตามด้วยช่องว่างแล้วจับตัวอักษรและตัวเลข (รวมทั้งตัวอักษรไทยในช่วง \u0E00-\u0E7F)
        pattern = r'(?:ซอย|Soi)\s*([\w\u0E00-\u0E7F-]+)'
        match = re.search(pattern, address_str, flags=re.IGNORECASE)
        return match.group(1) if match else "no data"
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน (ต้องมีอยู่แล้วในโค้ดของคุณ)
    work_status_series = get_work_status_series(df_data)
    
    # สกัดข้อมูลซอยจากคอลัมน์ที่อยู่
    results = df_data['The address of your workplace (optional)'].apply(extract_soi)
    
    # คืนค่า Series ทีละแถว โดยใช้เงื่อนไขจาก work_status_series:
    # หากสถานะการทำงานไม่ใช่ '3' หรือ '4' ให้คืนค่าที่สกัดได้จาก results
    # แต่ถ้าเป็น '3' หรือ '4' ให้คืนค่าว่าง ('')
    return df_data.apply(
        lambda row: results.loc[row.name] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '',
        axis=1
    )


def get_work_address_road_info(df_data):
    def extract_road(address):
        """
        ดึงข้อมูลถนนจากที่อยู่
        รองรับคำว่า "ถนน", "Road" หรือ "Rd" โดยจับข้อความที่มีตัวอักษรและช่องว่าง
        ตัวอย่าง: "622 Emporium Tower, 21st Floor / 4-5, Sukhumvit Road, Klongton Sub-district, Klongtoey District, Bangkok 10110 Thailand"
        จะสกัดได้ "Sukhumvit Road"
        """
        if pd.isnull(address):
            return "no data"
        address_str = str(address)
        # รูปแบบนี้จะจับกลุ่มที่มีตัวอักษร ตัวเลขและช่องว่าง จากนั้นลงท้ายด้วยคำว่า "ถนน", "Road" หรือ "Rd"
        pattern = r'([\w\s\-]+(?:ถนน|Road|Rd))'
        match = re.search(pattern, address_str, flags=re.IGNORECASE)
        return match.group(1).strip() if match else "no data"
    
    # เรียกใช้ฟังก์ชัน get_work_status_series (ซึ่งคุณต้องมีอยู่แล้วในโปรเจ็กต์ของคุณ)
    work_status_series = get_work_status_series(df_data)
    
    # สกัดข้อมูลถนนจากคอลัมน์ที่อยู่
    results = df_data['The address of your workplace (optional)'].apply(extract_road)
    
    # คืนค่า Series ทีละแถว โดยใช้เงื่อนไขจาก work_status_series:
    # ถ้าสถานะการทำงานไม่ใช่ '3' หรือ '4' ให้คืนค่าที่สกัดได้จาก results,
    # แต่ถ้าเป็น '3' หรือ '4' ให้คืนค่าว่าง ('')
    return df_data.apply(
        lambda row: results.loc[row.name] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '',
        axis=1
    )
    

def get_work_address_subdistrict(df_data):
    def extract_subdistrict(address):
        """
        สกัดข้อมูลตำบลจากที่อยู่
        ค้นหาคำว่า "ตำบล" ตามด้วยข้อความ (รวมตัวอักษรไทย ภาษาอังกฤษ ช่องว่าง หรือขีด)
        """
        if pd.isnull(address):
            return "no data"
        address_str = str(address)
        # Pattern นี้จะจับข้อความที่อยู่หลังคำว่า "ตำบล" พร้อมอนุญาตช่องว่างและตัวอักษร
        pattern = r'ตำบล\s*([\w\u0E00-\u0E7F\s\-]+)'
        match = re.search(pattern, address_str)
        return match.group(1).strip() if match else "no data"
    
    # เรียกใช้ฟังก์ชัน get_work_status_series (ซึ่งคุณต้องมีอยู่แล้วในโปรเจ็กต์)
    work_status_series = get_work_status_series(df_data)
    
    # สกัดข้อมูลตำบลจากคอลัมน์ที่อยู่
    results = df_data['The address of your workplace (optional)'].apply(extract_subdistrict)
    
    # คืนค่า Series ทีละแถว โดยใช้เงื่อนไขจาก work_status_series:
    # หากสถานะการทำงานไม่ใช่ '3' หรือ '4' ให้คืนค่าที่สกัดได้จาก results
    # แต่ถ้าเป็น '3' หรือ '4' ให้คืนค่าว่าง ('')
    return df_data.apply(
        lambda row: results.loc[row.name] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '',
        axis=1
    )


def get_work_address_country(df_data):
    def extract_country(address):
        """
        สกัดข้อมูลประเทศจากที่อยู่
        - หากที่อยู่มีเครื่องหมายจุลภาค จะใช้ส่วนสุดท้ายของการแบ่ง (หลังจากลบตัวเลขออก)
        - หากไม่มีเครื่องหมายจุลภาค จะใช้คำสุดท้ายของที่อยู่ (โดยลบเครื่องหมายพิเศษออก)
        """
        if pd.isnull(address):
            return "no data"
        address_str = str(address)
        
        # หากมีจุลภาค ให้แบ่งตามจุลภาค
        if ',' in address_str:
            parts = address_str.split(',')
            candidate = parts[-1].strip()
            candidate = re.sub(r'\d+', '', candidate).strip()  # ลบตัวเลขออก เช่น รหัสไปรษณีย์
            if candidate:
                return candidate
        
        # กรณีที่ไม่มีจุลภาค ให้ใช้คำสุดท้ายของที่อยู่
        tokens = address_str.split()
        if tokens:
            candidate = tokens[-1].strip(' ,.')
            return candidate
        
        return "no data"
    
    # เรียกใช้ฟังก์ชัน get_work_status_series (ซึ่งคุณต้องมีอยู่แล้วในโปรเจ็กต์ของคุณ)
    work_status_series = get_work_status_series(df_data)
    
    # สกัดข้อมูลประเทศจากคอลัมน์ที่อยู่
    results = df_data['The address of your workplace (optional)'].apply(extract_country)
    
    # คืนค่า Series ทีละแถว โดยใช้เงื่อนไขจาก work_status_series:
    # หากสถานะการทำงานไม่ใช่ '3' หรือ '4' ให้คืนค่าที่สกัดได้จาก results
    # แต่ถ้าเป็น '3' หรือ '4' ให้คืนค่าว่าง ('')
    return df_data.apply(
        lambda row: results.loc[row.name] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '',
        axis=1
    )
    
    
def get_work_address_postal_code(df_data):
    def extract_postal_code(address):
        """
        สกัดข้อมูลรหัสไปรษณีย์จากที่อยู่
        ค้นหาตัวเลขห้าตัวติดต่อกัน (รูปแบบรหัสไปรษณีย์ในไทย)
        """
        if pd.isnull(address):
            return "no data"
        address_str = str(address)
        # Pattern สำหรับรหัสไปรษณีย์ไทย (5 หลัก)
        match = re.search(r'\b\d{5}\b', address_str)
        return match.group(0) if match else "no data"
    
    # เรียกใช้ฟังก์ชัน get_work_status_series (ซึ่งคุณต้องมีอยู่แล้วในโปรเจ็กต์)
    work_status_series = get_work_status_series(df_data)
    
    # สกัดข้อมูลรหัสไปรษณีย์จากคอลัมน์ที่อยู่
    results = df_data['The address of your workplace (optional)'].apply(extract_postal_code)
    
    # คืนค่า Series ทีละแถว โดยใช้เงื่อนไขจาก work_status_series:
    # หากสถานะการทำงานไม่ใช่ '3' หรือ '4' ให้คืนค่าที่สกัดได้จาก results,
    # แต่ถ้าเป็น '3' หรือ '4' ให้คืนค่าว่าง ('')
    return df_data.apply(
        lambda row: results.loc[row.name] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '',
        axis=1
    )
