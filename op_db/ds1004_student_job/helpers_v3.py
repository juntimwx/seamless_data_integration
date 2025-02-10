import pandas as pd
import re

def get_citizen_id_series(df_data, df_sql):
    """
    คืนค่า Series ของรหัสบัตรประชาชน (หรือพาสปอร์ต) สำหรับแต่ละ 'Student ID' ใน df_data
    โดยเทียบกับ 'Code' ใน df_sql เพื่อดึง 'CitizenNumber' หรือ 'Passport' ตามเงื่อนไข:
      - หาก 'CitizenNumber' เป็นค่าว่าง ('') หรือ NaN ให้ใช้ค่า 'Passport' แทน
      - หากมี 'CitizenNumber' ให้ใช้ค่านั้นทันที
    """
    # 1) แปลงชนิดข้อมูลของคอลัมน์ 'Student ID' เป็นสตริง (เผื่อกรณีเป็นตัวเลข จะได้ Map ได้ตรง)
    student_ids = df_data['Student ID'].astype(str)

    # 2) สร้าง Dictionary สำหรับ 'CitizenNumber' โดยใช้ 'Code' เป็น Key
    citizen_dict = df_sql.set_index('Code')['CitizenNumber'].to_dict()

    # 3) สร้าง Dictionary สำหรับ 'Passport' โดยใช้ 'Code' เป็น Key
    passport_dict = df_sql.set_index('Code')['Passport'].to_dict()

    # 4) ฟังก์ชันภายใน เพื่อดึง 'CitizenNumber' หรือ 'Passport' ตามเงื่อนไข
    def get_citizen_or_passport(student_id):
        citizen_number = citizen_dict.get(student_id, None)
        # เช็คว่าเป็น NaN หรือเป็น String ว่าง
        if pd.isna(citizen_number) or citizen_number == '':
            # ถ้าไม่มี CitizenNumber ให้ใช้ Passport แทน
            return passport_dict.get(student_id, '')
        else:
            return citizen_number

    # 5) สร้าง Series ใหม่สำหรับ 'CITIZEN_ID'
    citizen_id_series = student_ids.apply(get_citizen_or_passport)

    return citizen_id_series


def get_work_status_series(df_data):
    mapping_work_status = {
        'Unemployed before graduation and employed after graduation': '1',
        'Unemployed before graduation and be employed after graduation': '1',  # ความหมายตรงกับแบบแรก
        'Employed and currently pursuing a higher degree': '2',
        'Be employed and currently continue in greater degree': '2',  # ความหมายตรงกับข้อ 2
        'Unemployed': '3',
        'Currently pursuing a higher degree': '4',
        'Employed in the same field before and after graduation': '5',
        'Be employed in the same field before and after graduation': '5',  # ความหมายตรงกับข้อ 5
        'Employed before and change the field work after graduation': '6',
        'Be employed before and change the field work after graduation': '6',  # ความหมายตรงกับข้อ 6
        'Employed before graduation and promoted after graduation in the same field': '7'
    }
    
    return df_data['Currently Employed Status'].map(mapping_work_status)#.fillna('')


def get_military_status_series(df_data, df_sql):
    """
    คืนค่า Series แสดงสถานะทางทหาร (เป็น string) ตามเงื่อนไข:
      - ถ้า 'Student ID' (ใน df_data) ตรงกับ 'Code' (ใน df_sql)
      - และค่า Gender ใน df_sql เป็น 'male'
        => ใช้ mapping_military_status ในการแปลง
      - กรณีอื่นให้คืน '-'
    """
    # 1) กำหนด mapping สำหรับค่าข้อความทางทหาร -> สตริง '0' หรือ '1'
    mapping_military_status = {
        'Taken a draft deferment period or Exempted from military service or Conscripted - อยู่ในช่วงผ่อนผันเกณฑ์ทหาร หรือได้รับการยกเว้น หรือผ่านการเกณฑ์ทหารแล้ว': '0',
        'อยู่ในระหว่างการเป็นทหารเกณฑ์': '1'
    }
    
    # 2) แปลง 'Student ID' ใน df_data ให้เป็น string เพื่อให้ match กับ df_sql['Code']
    df_data['Student ID'] = df_data['Student ID'].astype(str)
    
    # 3) สร้าง dictionary จาก df_sql: key = 'Code', value = 'Gender'
    gender_dict = df_sql.set_index('Code')['Gender'].to_dict()
    
    # 4) ฟังก์ชันภายในสำหรับ apply
    def map_military_status(row):
        # ดึง Student ID และค่าที่บอกสถานะทหาร
        student_id = row['Student ID']
        mil_status = row['Military Status (Male only) -  สถานะการเกณฑ์ทหาร(เฉพาะเพศชาย)']
        
        # ดู gender ของ student_id นี้ใน df_sql
        gender_value = gender_dict.get(student_id, None)
        
        # ถ้าเป็นผู้ชาย (male) ให้แปลงตาม mapping
        # ถ้าไม่มีใน mapping ให้ใช้ '' หรือ ค่าว่าง เป็น default
        if gender_value == 'male':
            return mapping_military_status.get(mil_status, '')
        else:
            # ถ้า gender ไม่ใช่ male หรือหาไม่เจอใน dictionary ให้คืน '-'
            return '-'
    
    # 5) ใช้ .apply(...) เพื่อสร้าง Series ใหม่
    return df_data.apply(map_military_status, axis=1)


def get_ordinate_status_series(df_data):
    mapping_ordinate_status ={
        'Not being as a priest - ไม่ได้เป็นนักบวช': '1',
        'อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา น้อยกว่า 3 เดือน': '2',
        'อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา 4 เดือน - 1 ปี': '3',
        'อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา มากกว่า 1 ปี': '4',
        'อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา ไม่มีกำหนด': '5'
    }
    
    return df_data['Being Ordained as a Priest Status -  สถานะการเป็นนักบวช'].map(mapping_ordinate_status)#.fillna('')


def get_occup_type_series(df_data):
    """
        หมวด 01 (ข้าราชการ /เจ้าหน้าที่หน่วยงานของรัฐ) สำหรับงานข้าราชการหรือเจ้าหน้าที่ภาครัฐ
        หมวด 02 (รัฐวิสาหกิจ) สำหรับพนักงานในรัฐวิสาหกิจ เช่น Staff/Employee in a State-Enterprise Agency
        หมวด 03 (พนักงานบริษัท/องค์กรธุรกิจเอกชน) รวมถึงงานในภาคเอกชนที่มักเป็นพนักงาน เช่น Staff/Employee in a private company, Guest Service Agent (Hotel), developer, Digital Marketing, Entertainment, Hotel industry, Life insurance, Flight attendant, Five stars hotel industry, hospitality
        หมวด 04 (ดำเนินธุรกิจอิสระ/เจ้าของกิจการ) รวมถึงงานที่เกี่ยวกับการดำเนินธุรกิจส่วนตัวหรือเป็น Freelance เช่น Your own business/family business, Director of Photography/ Cinematographer, Bussiness, Consulting, Freelance, Start-up Business, Investment academy..., Real Esate business, Barber/Hairstylist
        หมวด 05 (พนักงานองค์การต่างประเทศ/ระหว่างประเทศ) สำหรับงานในองค์การต่างประเทศ
    """
    mapping_occup_type = {
        'Civil Servant/Employee in a government organization': '01',
        'Staff/Employee in a State-Enterprise Agency': '02',
        'Staff/Employee in a private company': '03',
        'Guest Service Agent (Hotel)': '03',
        'developer': '03',
        'Digital Marketing': '03',
        'Entertainment': '03',
        'Hotel industry': '03',
        'Life insurance': '03',
        'Flight attendant': '03',
        'Five stars hotel industry': '03',
        'hospitality': '03',
        'Investment academy and service providers and also investment affiliate': '04',
        'Real Esate business': '04',
        'Barber/Hairstylist': '04',
        'Start-up Business': '04',
        'Director of Photography/ Cinematographer': '04',
        'Your own business/family business': '04',
        'Bussiness': '04',
        'Consulting': '04',
        'Freelance': '04',
        'Employee in an international organization': '05'
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น 00 เพื่อกรอกข้อมูลเพิ่มเติม
            mapped_value = mapping_occup_type.get(row['Type of Job'], '00')

        return mapped_value

    return df_data.apply(map_data, axis=1)
    
    # return df_data.apply(lambda row: mapping_occup_type.get(row['Type of Job']) if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)
    

def get_occup_type_text(df_data):
    # เรียกใช้ฟังก์ชัน get_occup_type_series เพื่อรับ Series ของ Occupation Type
    occup_type_series = get_occup_type_series(df_data)
    def map_data(row):
        occup_type = str(occup_type_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if occup_type == '00':
            # ถ้า occup_type เท่ากับ '0' ตอบกลับเป็นค่า Type of Job
            mapped_value = row['Type of Job']
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)


def get_talent_series(df_data):
    mapping_talent = {
        "Herb knowledge": "00",
        "Communication": "00",
        "people skill": "00",
        "Marketing": "00",
        "Finance": "00",
        "Confidence": "00",
        "Flexibility and discipline": "00",
        "Flexibility and discipline": "00",
        "Analysis": "00",
        "Cooperative Education": "00",
        "Analytical skill": "00",
        "Communication Skill": "00",
        "Analyzing and Creativity": "00",
        "Bussiness": "00",
        "Analytical thinking and perseverance": "00",
        "Personality": "00",
        "Business marketing": "00",
        "Creativity": "00",
        "-": "00",
        "Online courses": "00",
        "Technical knowledge": "00",
        "Academic/Scientific Writing": "00",
        "My enthusiasm": "00",
        "Culinary skills": "00",
        "Logical Thinking": "00",
        "Economics and Marketing Skills": "00",
        "Critical Thinking": "00",
        "Social skills": "00",
        "Financial knowledge": "00",
        "Knowledge from the International Relations and Global Affiars studies": "00",
        "Product managment / Innovation": "00",
        "Management": "00",
        "The ability to learn quickly": "00",
        "Analytics, Management": "00",
        "Sales and Marketing": "00",
        "Ability to learn new things and adaptability towards changes": "00",
        "Accounting": "00",
        "Communications": "00",
        "Mindset; proactive, discipline, proactive finding opportunities.": "00",
        "Interpersonal Skills": "00",
        "hospitality": "00",
        "My Pitching Skill ;)": "00",
        "Foreign Languages": "01",
        "Foreign Languages and Art": "01",  # เลือก "01" เพราะมี Foreign Languages อยู่ด้วย
        "Computer literacy": "02",
        "Extra curriculum activities": "03",
        "Art": "04",
        "Sport": "05",
        "Actor": "06",
    }

    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น 00 เพื่อกรอกข้อมูลเพิ่มเติม
            mapped_value = mapping_talent.get(row['Which skill can most help you to get employed?'], '00')

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_talent.get(row['Which skill can most help you to get employed?']) if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)


def get_talent_text(df_data):
    talent_series = get_talent_series(df_data)
    def map_data(row):
        talent = str(talent_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if talent == '00':
            # ถ้า occup_type เท่ากับ '0' ตอบกลับเป็นค่า Which skill can most help you to get employed?
            mapped_value = row['Which skill can most help you to get employed?']
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)
    
    # return df_data.apply(lambda row: row['Which skill can most help you to get employed?'] if str(talent_series.loc[row.name]) == '00' else '', axis=1)


def get_position_type_series(df_data):
    mapping_position = {
        "marketing supporter": "241960",           # นักการตลาด / เจ้าหน้าที่การตลาด
        "marketing officer": "241960",
        "employee": "X11020",
        "co-owner": "X11020",
        "english teacher": "232010",               # ครูระดับมัธยมศึกษา (ตัวอย่าง)
        "sales": "241960",
        "uniqlo manager candidate": "122430",      # ผู้จัดการฝ่ายค้าปลีก
        "trade officer": "X11020",
        "assistant research project manager": "X11020",
        "junior developer": "213210",              # โปรแกรมเมอร์ / วิศวกรซอฟต์แวร์
        "marketing": "241960",
        "investment banking associate": "X11020",
        "library assistant": "414110",             # เจ้าหน้าที่ห้องสมุด
        "associate analyst": "X11020",
        "content moderator": "X11020",
        "cabin crew": "511120",                    # พนักงานต้อนรับบนเครื่องบิน
        "guest service agent": "422210",           # พนักงานต้อนรับทั่วไป (ตัวอย่าง)
        "software engineer": "213210",
        "property consultant": "131730",           # ผู้จัดการทั่วไปด้านทรัพย์สิน
        "marketing admin and data support": "241960",
        "developer": "213210",
        "mt financial controller": "123120",       # ผู้จัดการฝ่ายการเงินและการบัญชี
        "tax consultant - transfer pricing": "X11020",
        "program administrator (pa)": "411520",      # เลขานุการ
        "data analyst": "X11020",
        "managing director": "121030",             # ผู้บริหารระดับสูงของหน่วยงานเอกชน
        "-": "X11030",                             # ไม่ระบุ
        "sales manager": "123320",                 # ผู้จัดการฝ่ายขาย / ส่งเสริมการขาย
        "general manager": "121040",               # ผู้บริหารของหน่วยงานเอกชน
        "manager": "121040",
        "test engineer": "X11020",
        "international sales executive": "241960",
        "clinical trial assistant/coordinator": "X11020",
        "commercial data specialist": "X11020",
        "system engineer": "213160",               # วิศวกรระบบ (ตัวอย่าง)
        "it support": "312210",                    # ช่างเทคนิคระบบคอมพิวเตอร์
        "graphic designer": "347135",              # นักออกแบบภาพกราฟิก
        "marketing and accountant": "123120",
        "customer experience specialist": "X11020",
        "software developer": "213210",
        "architectural design manager (interiors demand creation)": "214125",  # สถาปนิกตกแต่งภายใน
        "business development international support": "X11020",
        "data engineer": "213210",
        "social media manager and digital marketer": "241960",
        "experience designer": "X11020",
        "online marketing": "241960",
        "business owner": "X11020",
        "product developer": "X11020",
        "analysts": "X11020",
        "business architecture analyst": "X11020",
        "management trainee": "X11010",             # ผู้เข้าสู่แรงงานใหม่ / ผู้ฝึกงาน
        "marketing executives": "241960",
        "human resource officer, practitioner level": "X11020",
        "foreman": "X11020",
        "research executive": "X11020",
        "ceo": "121010",                           # ประธานกรรมการ
        "project manager": "X11020",
        "director of photography": "122965",       # ผู้จัดการกองถ่ายทำภาพยนตร์ (ตัวอย่าง)
        "overseas sales": "241960",
        "packaging designer": "X11020",
        "self-employed": "X11020",
        "finance and marketing": "123120",
        "ta and secretary": "411520",
        "assistant office manager": "X11020",
        "f&b coordinator": "512150",               # พนักงานบริการในโรงแรม
        "corporate banking service officer": "421220",  # เจ้าหน้าที่รับจ่ายเงินในธนาคาร
        "consultant": "XZ1020",                    # รอปรับปรุงรหัส (ผู้เชี่ยวชาญ)
        "executive secretary to md": "411520",
        "it officer": "312210",
        "laboratory technician": "X11020",
        "campaign specialist": "X11020",
        "executive researcher": "X11020",
        "product operations admin": "X11020",
        "associate marketing": "241960",
        "marketing executive": "241960",
        "store operator": "X11020",
        "teacher": "232010",
        "kols supports": "X11020",
        "performance marketing analyst": "241960",
        "administration": "X11020",
        "graphic desingner": "347135",
        "ui designer": "347135",
        "corporal": "11010",                       # ตำแหน่งในทหาร (ตัวอย่าง)
        "campaign analyst": "X11020",
        "financial analyst": "X11020",
        "android engineer": "213210",
        "sales & marketing coordinator and personal assistant to cluster director of sales and marketing": "241960",
        "analyst": "X11020",
        "freelance": "X11020",
        "technician": "X11020",
        "md": "121010",
        "intelligence officer": "X11020",
        "artist management": "X11020",
        "events coordinator": "X11020",
        "digital designer": "347135",
        "junior graphic designer": "347135",
        "marketing coordinator and graphic designer": "347135",
        "digital marketing and sales": "241960",
        "sales account executive": "241960",
        "pmo": "X11020",
        "software engineer associate": "213210",
        "financial/currency analyst": "X11020",
        "associate": "X11020",
        "staff": "X11020",
        "director": "121010",
        "trust and safety associates": "X11020",
        "social media specialist assistant": "241960",
        "assistant planned manager": "X11020",
        "qc engineer": "X11020",
        "marketing": "241960",
        "business owner": "X11020",
        "ecom business development executive": "X11020",
        "art gallery assistant": "X11020",
        "media planner": "X11020",
        "demand planner (uflp)": "X11020",
        "groups & events coordinator": "X11020",
        "business development rep": "X11020",
        "marketing assistant": "241960",
        "medical writer": "X11020",
        "transfer pricing consultant": "X11020",
        "management traniee": "X11010",
        "content creator": "X11020",
        "account payable officer": "X11020",
        "marketer": "241960",
        "actor": "245510",                        # นักแสดง
        "graphic designer(draftman)": "347135",
        "video editor": "X11020",
        "influ maketing": "241960",
        "investment advisor": "X11020",
        "incubation and onboarding": "X11020",
        "digital marketing analyst": "241960",
        "sales & marketing": "241960",
        "account payable officer": "X11020",
        "graphic designer": "347135",
        "account executive": "X11020",
        "english content writer": "245115",        # นักเขียนด้านวิชาการ
        "communications executive": "X11020",
        "commis": "X11020",
        "product operations administrator": "X11020",
        "credit analyt": "X11020",
        "personal assistant to director": "411520",
        "category management analyst": "X11020",
        "hr": "X11020",
        "export sales coordinator": "X11020",
        "imc for home appliances electronic": "X11020",
        "junior executive e-commerce": "X11020",
        "owner": "X11020",
        "backend dev": "213210",
        "marketing managers": "241960",
        "business development": "X11020",
        "editor": "245115",
        "solution consultant": "XZ1020",
        "sales coordinator": "X11020",
        "associate manager": "X11020",
        "marketing manager": "241960",
        "project coordinator": "X11020",
        "human resource": "X11020",
        "junior graphic designer": "347135",
        "strategic planner": "X11020",
        "project management staff": "X11020",
        "marketing consultant": "XZ1020",
        "junior ads optimizer": "X11020",
        "front office": "X11020",
        "project manager": "X11020",
        "export sales": "X11020",
        "digital marketing+social media executive": "241960",
        "gm": "121040",
        "property consultance": "131730",
        "project assistant": "X11020",
        "sales coordinator": "X11020",
        "web programmer": "213210",
        "business developer": "X11020",
        "corporate communications executive": "X11020",
        "recruiter": "X11020",
        "accounting officer": "412120",
        "associate consultant - finance and accounting": "X11020",
        "media planning executive": "X11020",
        "full stack developer": "213210",
        "visual merchandising": "X11020",
        "digital marketing coordinator": "241960",
        "quality assurance engineer": "X11020",
        "producer": "X11020",
        "managing director, sales and marketing manager": "121030",
        "ae": "X11020",
        "consulting analyst": "XZ1020",
        "military officer": "11010",
        "digital marketing associate": "241960",
        "executive lounge agent": "511120",
        "football academy administrator/ content creator": "X11020",
        "business development associate": "X11020",
        "self-owned": "X11020",
        "agency": "X11020",
        "sales executive": "241960",
        "admin": "X11020",
        "assistant to the thailand representative to the acwc for women's rights": "X11020",
        "it business analyst": "X11020",
        "pr and marketing": "241960",
        "digital marketing association": "241960",
        "translator": "244440",
        "finance support": "X11020",                              # งานสนับสนุนด้านการเงิน (ไม่ชัดเจน)
        "staff outsourcing support": "X11020",                        # งานสนับสนุนบุคลากรภายนอก (ไม่ชัดเจน)
        "executive": "X11020",                                        # ตำแหน่งผู้บริหารทั่วไป (ไม่ระบุชัด)
        "key account manager": "241960",                              # ผู้จัดการลูกค้าสำคัญ (งานการตลาด/ขาย)
        "interpreter": "244440",                                      # นักแปลภาษา (สำหรับแปลภาษา/แปลความ)
        "communication intern": "X11020",                             # ฝึกงานด้านการสื่อสาร
        "marketing executiv": "241960",                               # (ตำแหน่งที่คล้ายกับ marketing executive)
        "digital marketing, kol specialist": "241960",                # งานด้านการตลาดดิจิทัลและ KOL
        "concierge officer": "422210",                                # งานบริการรับรอง (ในโรงแรม/บริการ)
        "designer": "347135",                                         # นักออกแบบ (กราฟิก/ดีไซน์)
        "brand strategist": "241960",                                 # นักวางกลยุทธ์แบรนด์ (รวมงานการตลาด)
        "affiliated key account manager": "241960",                   # ผู้จัดการลูกค้าสำคัญ (ในเครือ)
        "research assistant": "X11020",                                # ผู้ช่วยวิจัย
        "overall management": "121040",                               # ผู้บริหารทั่วไป
        "fullstack developer": "213210",                              # วิศวกร/โปรแกรมเมอร์ Full Stack
        "foreign kindergarten teacher coordinator": "232010",         # ผู้ประสานงาน/ผู้ดูแลครูอนุบาล (ตัวอย่าง)
        "strategic project assistant officer": "X11020",              # ผู้ช่วยงานโครงการเชิงกลยุทธ์ (ทั่วไป)
        "market ops": "241960",                                       # งานปฏิบัติการด้านการตลาด
        "junior finance officer": "X11020",                           # เจ้าหน้าที่การเงินระดับจูเนียร์
        "marketing staff": "241960",                                  # พนักงานการตลาด
        "marketing, graphic designer": "347135",                      # รวมงานออกแบบและการตลาด (เลือกใช้รหัสออกแบบ)
        "assistant graphic visual": "347135",                         # ผู้ช่วยด้านงานออกแบบภาพ
        "executive assistant": "411520",                              # ผู้ช่วยผู้บริหาร (เลขานุการ)
        "it application support analyst": "312210",                   # งาน IT support (Application)
        "admin assistant": "X11020",                                  # ผู้ช่วยฝ่ายบริหารทั่วไป
        "flight attendant": "511120",                                 # พนักงานต้อนรับบนเครื่องบิน
        "media director": "X11020",                                   # ผู้บริหารด้านสื่อ (ไม่ชัดเจน)
        "team assistant": "X11020",                                   # ผู้ช่วยทีม (ทั่วไป)
        "strategy & portfolio management professional": "X11020",     # ผู้เชี่ยวชาญด้านกลยุทธ์และการบริหารพอร์ตโฟลิโอ (ทั่วไป)
        "customer service and operation stuff": "X11020",             # งานบริการลูกค้าและปฏิบัติการ (ทั่วไป)
        "full time actress/ model": "245510",                         # นักแสดง/นางแบบ (ใช้รหัสนักแสดง)
        "management team": "121040",                                  # ทีมผู้บริหาร
        "research and development": "X11020",                         # งานวิจัยและพัฒนา
        "assistant": "X11020",                                        # ผู้ช่วย (ทั่วไป)
        "entrepreneur in residence": "X11020",                        # ผู้ประกอบการในฐานะที่ปรึกษา/อยู่ในโครงการ
        "officer": "X11020",                                          # ตำแหน่งเจ้าหน้าที่ (ทั่วไป)
        "reservation": "422210",                                      # งานจอง/บริการรับจอง (โรงแรม/การท่องเที่ยว)
        "full-stack developer": "213210",                             # วิศวกร/โปรแกรมเมอร์ Full Stack
        "freelance graphic designer": "347135",                       # นักออกแบบกราฟิกอิสระ
        "people onboarding project coordinator": "X11020",            # ผู้ประสานงาน onboarding (ทั่วไป)
        "country officer": "X11020",                                  # เจ้าหน้าที่ประจำประเทศ (ทั่วไป)
        "recruitment consultant / realter": "X11020",                 # ที่ปรึกษาด้านสรรหา/นายหน้าอสังหาริมทรัพย์
        "specialist - beds network": "X11020",                        # ผู้เชี่ยวชาญด้านเครือข่ายเตียง (โรงแรม/บริการ)
        "assistant managing director/marketing manager": "241960",    # ผู้ช่วยผู้บริหาร/ผู้จัดการการตลาด
        "sale executives": "241960",                                  # ผู้บริหารฝ่ายขาย
        "new model control": "X11020",                                # งานควบคุมนางแบบ/โมเดล (ทั่วไป)
        "customer service": "X11020",                                 # งานบริการลูกค้า
        "creative content creator": "X11020",                         # ผู้สร้างเนื้อหาสร้างสรรค์ (ทั่วไป)
        "digital marketing junior executives": "241960",            # พนักงานการตลาดดิจิทัลระดับจูเนียร์
        "founder": "X11020",                                          # ผู้ก่อตั้ง (ทั่วไป)
        "ceo/manager": "121010",                                      # ผู้บริหารสูงสุด / ผู้จัดการ
        "vkam - vendor key account management": "241960",            # งานจัดการลูกค้าสำคัญด้าน vendor
        "content creator and admin": "X11020",                        # ผู้สร้างเนื้อหาและผู้ช่วยงานธุรการ
        "advisor": "X11020",                                          # ที่ปรึกษา (ทั่วไป)
        "administrative assistant": "X11020",                         # ผู้ช่วยงานธุรการ
        "credit analyst": "X11020",                                   # นักวิเคราะห์เครดิต (ทั่วไป)
        "accounting receivable officer": "412120",                    # เจ้าหน้าที่บัญชีลูกหนี้
        "managment trainee": "X11010",                                # ผู้เข้าสู่แรงงานใหม่ / ผู้ฝึกงาน
        "wealth associate": "X11020",                                 # เจ้าหน้าที่ด้านความมั่งคั่ง (ทั่วไป)
        "seller proformance": "241960",                               # (งานขาย/ประสิทธิภาพการขาย)
        "catering sales coordinator": "241960",                     # ผู้ประสานงานฝ่ายขายในธุรกิจอาหารและเครื่องดื่ม
        "marketing communication": "241960",                          # งานการสื่อสารการตลาด
        "chairman": "121010",                                         # ประธานกรรมการ
        "sell and marketing": "241960",                               # งานขายและการตลาด
        "sales management": "123320",                                 # ผู้จัดการฝ่ายขาย
        "cabin attendant": "511120",                                  # พนักงานต้อนรับในห้องโดยสาร
        "accountant a/r": "412120",                                   # นักบัญชี (ลูกหนี้)
        "community officer": "X11020",                                # เจ้าหน้าที่ชุมชน (ทั่วไป)
        "business assistant": "X11020",                               # ผู้ช่วยธุรกิจ (ทั่วไป)
        "team assistant": "X11020",                                   # (ซ้ำกับรายการก่อนหน้า)
        "brand ambassador": "241960",                                 # ทูตแบรนด์ / ผู้ส่งเสริมแบรนด์
        "reservation agent": "422210",                                # เจ้าหน้าที่จอง/บริการจอง
        "attache": "X11020",                                          # ผู้ช่วยเจ้าหน้าที่ต่างประเทศ (ทั่วไป)
        "associate consultant": "XZ1020",                             # ที่ปรึกษาระดับร่วม (รอปรับปรุงรหัส)
        "receptionist": "X11020",                                     # พนักงานต้อนรับ
        "sale executive": "241960",                                   # ผู้บริหารงานขาย
        "procurement": "X11020",                                      # งานจัดซื้อ (ทั่วไป)
        "sale officer": "241960",                                     # เจ้าหน้าที่ขาย
        "controller executive": "X11020",                             # ผู้ควบคุม/ตรวจสอบ (ทั่วไป)
        "assistant manager": "121040",                                # ผู้ช่วยผู้จัดการ (ทั่วไป)
        "associate corporate innovation consultant": "XZ1020",        # ที่ปรึกษานวัตกรรมองค์กร (รอปรับปรุงรหัส)
        "project associate": "X11020",                                # ผู้ช่วยงานโครงการ
        "registration assistant": "X11020",                           # ผู้ช่วยงานลงทะเบียน
        "marketing communications officer": "241960",               # เจ้าหน้าที่สื่อสารการตลาด
        "accounting clerk - account payable": "412120",               # พนักงานบัญชีเจ้าหน้าที่ (ลูกหนี้)
        "service dalivery": "X11020",                                 # งานบริการส่งมอบ (Service delivery)
        "marketing associate": "241960",                              # ผู้ช่วยงานการตลาด
        "marketing / tour leader": "241960",                          # งานการตลาดและนำเที่ยว
        "finance controlling and planning officer": "123120",         # ผู้ควบคุมและวางแผนด้านการเงิน
        "ux/ui graphic designer": "347135",                           # นักออกแบบ UX/UI
        "freelance artist": "347135",                                 # ศิลปินอิสระ (ใช้รหัสนักออกแบบกราฟิก)
        "project coorfinator": "X11020",                              # (Project coordinator – typo)
        "pro consul": "XZ1020",                                       # (ที่ปรึกษา – ย่อรูปแบบ)
        "program support officer": "X11020",                          # เจ้าหน้าที่สนับสนุนโปรแกรม
        "sale": "241960",                                             # งานขาย
        "ai consultant": "XZ1020",                                    # ที่ปรึกษาด้าน AI (รอปรับปรุงรหัส)
        "concierge": "422210",                                        # งานบริการรับรอง
        "barber": "X11020"                                            # ช่างตัดผม (ไม่ระบุชัดเจน)
    }

       # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น X11030 ผู้ไม่แจ้งชื่ออาชีพ
            if str(row['Position']).strip().lower() == '':
                mapped_value = 'X11030'
            else:
                mapped_value = mapping_position.get(str(row['Position']).strip().lower())

        return mapped_value

    return df_data.apply(map_data, axis=1)
    
    # def map_position_status(row):
    #     # ทำความสะอาดข้อมูลใน 'Position' โดยลบช่องว่างส่วนเกิน
    #     cleaned_data = str(row['Position']).strip().lower()
    #     if str(work_status_series.loc[row.name]) not in ['3', '4']:
    #         if cleaned_data == '':
    #             return 'X11030'
    #         return mapping_position.get(cleaned_data)
    #     else:
    #         return ''
    
    # # 5) ใช้ .apply(...) เพื่อสร้าง Series ใหม่
    # return df_data.apply(map_position_status, axis=1)


def get_work_name_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่นักศึกษากรอกข้อมูล
            mapped_value = row['Organization name']

        return mapped_value

    return df_data.apply(map_data, axis=1)
    
    # return df_data.apply(lambda row: row['Organization name'] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)
    

def get_work_type_series(df_data):
    mapping_work_type = {
        "small family owned business": "N",  # กิจกรรมการบริหารและบริการสนับสนุนอื่น ๆ (ทั่วไป)
        "power & energy / oil & gas / heating, ventilation & air conditioning": "D",  # ไฟฟ้า ก๊าซ ไอน้ำและระบบการปรับอากาศ
        "hospitality / catering": "I",        # ที่พักแรมและบริการด้านอาหาร
        "education": "P",                      # การศึกษา
        "art / entertainment / recreation": "R",  # ศิลปะ ความบันเทิงและนันทนาการ
        "general business services": "N",      # กิจกรรมการบริหารและบริการสนับสนุนอื่น ๆ
        "logistics and warehouse": "H",        # การขนส่งและสถานที่เก็บสินค้า
        "professional / science / academic": "M",  # กิจกรรมวิชาชีพ วิทยาศาสตร์และกิจกรรมทางวิชาการ
        "international organization / international association": "U",  # กิจกรรมขององค์การระหว่างประเทศและภาคีสมาชิก
        "financial services/insurance": "K",   # กิจกรรมทางการเงินและการประกันภัย
        "real estate": "L",                    # กิจกรรมเกี่ยวกับอสังหาริมทรัพย์
        "production": "C",                     # การผลิต
        "healthcare / charity / non-profit organization": "Q",  # กิจกรรมด้านสุขภาพและงานสังคมสงเคราะห์
        "information and communication": "J",  # ข้อมูลข่าวสารและการสื่อสาร
        "management consultancy & business support service": "N",  # กิจกรรมการบริหารและบริการสนับสนุนอื่น ๆ
        "motor vehicles retail and whole sale / auto repair": "G",   # การขายส่งและการขายปลีกการซ่อมยานยนต์และจักรยานยนต์
        "civil services (government, armed forces) / social security": "O",  # การบริหารราชการ  การป้องกันประเทศ  และการประกันสังคมภาคบังคับ
        "construction": "F",                   # การก่อสร้าง
        "water supply / wastewater treatment / waste management / related activities": "E",  # การจัดหาน้ำ การจัดการน้ำเสียและของเสีย รวมถึงกิจกรรมที่เกี่ยวข้อง
        "agriculture / forestry / fisheries": "A"  # เกษตรกรรม การป่าไม้และการประมง
    }
    
   # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
            mapped_value = mapping_work_type.get(row['Industry'].strip().lower())

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_work_type.get(row['Industry'].strip().lower()) if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)


def get_work_tel_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น 00 เพื่อกรอกข้อมูลเพิ่มเติม
            mapped_value = row['Phone number of your workplace (optional)']

        return mapped_value

    return df_data.apply(map_data, axis=1)
    
    # return df_data.apply(lambda row: row['Phone number of your workplace (optional)'] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)


def get_work_address_name_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 3 || 4
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่า value
            mapped_value = row['QN_WORK_ADD']

        return mapped_value

    return df_data.apply(map_data, axis=1)

def get_work_address_moo_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 3 || 4
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่า value
            mapped_value = row['QN_WORK_MOO']

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_work_address_building_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 3 || 4
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่า value
            mapped_value = row['QN_WORK_BUILDING']

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_work_address_soi_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 3 || 4
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่า value
            mapped_value = row['QN_WORK_SOI']

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_work_address_street_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 3 || 4
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่า value
            mapped_value = row['QN_WORK_STREET']

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_work_address_tambon_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 3 || 4
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่า value
            mapped_value = row['QN_WORK_TAMBON']

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_work_address_country_series(df_data):
    address_country = {
        "thailand": "TH",
        "japan": "JP",
        "south korea": "KR",
        "myanmar": "MM",
        "qatar": "QA",
        "no data": "no data"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    return df_data.apply(lambda row: address_country.get(row['QN_WORK_COUNTRY_ID'].strip().lower()) if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)


def get_work_address_zipcode_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 3 || 4
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่า value
            mapped_value = row['QN_WORK_TAMBON']

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_work_email_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น 00 เพื่อกรอกข้อมูลเพิ่มเติม
            mapped_value = row['Email of your workplace (optional)']

        return mapped_value

    return df_data.apply(map_data, axis=1)
    
    # return df_data.apply(lambda row: row['Email of your workplace (optional)'] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)


def get_work_salary_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น 00 เพื่อกรอกข้อมูลเพิ่มเติม
            mapped_value = row['Monthly salary or earned income']

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: row['Monthly salary or earned income'] if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)


def get_satisfy_type_series(df_data):
    mapping_work_satisfy = {
        "yes": "01",  # พอใจ
        "still unknow": "00",  # ไม่ทราบ/อื่นๆให้ระบุ
        "no (not match with your qualification/ability)": "04",  # ไม่ได้ใช้ความรู้ที่เรียนมา
        "no (little payment)": "05",  # ค่าตอบแทนต่ำ
        "no (undesirable working system)": "02",  # ระบบงานไม่ดี
        "no (no stability)": "06",  # ขาดความมั่นคง
        "no (no opportunity for promotion)": "07",  # ขาดความก้าวหน้า
        "50-50": "00",  # ไม่ชัดเจน/อื่นๆ
        "wishes to start own business venture": "00",  # อื่นๆให้ระบุ
        "somewhat satisfied , the job require moving/the base salary is less than expected; however, it's consider good in this industry": "05",  # เนื่องจากค่าตอบแทนต่ำเป็นปัญหา
        "no (undesirable co-worker)": "03",  # ผู้ร่วมงานไม่ดี
        "yes i’m satisfied and no (no opportunity for promotion)": "07",  # ขาดความก้าวหน้า
        "seeking out other alternatives": "00",  # ไม่ชัดเจน
        "client problems": "00",  # ไม่ชัดเจน
        "want to learn more in those filed": "00",  # ไม่ระบุชัดเจน
        "still in job training process so not sure": "00",  # ไม่แน่ใจ/อื่นๆ
        "low salary and job scope": "05",  # ค่าตอบแทนต่ำ
        "i am satisfied but i would also like to gain experience being a corporate employee": "01",  # พอใจ
        "unmotivated": "00",  # ไม่ชัดเจน (อื่นๆ)
        "not really": "00",  # ไม่ชัดเจน
        "somewhat satisfied": "01",  # พอใจ (ระดับหนึ่ง)
        "still deciding": "00",  # ไม่แน่ใจ
        "yes, with co worker. no, i have to talk to people who are not cooperating and hard to predict": "03",  # ผู้ร่วมงานไม่ดี
        "still figuring it out": "00",  # ไม่แน่ใจ
        "yes, as of now": "01",  # พอใจ
        "on a certain level, yes.": "01"  # พอใจ
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น 00 เพื่อกรอกข้อมูลเพิ่มเติม
            mapped_value = mapping_work_satisfy.get(row['Are you satisfied with your work?'].strip().lower(), '00')

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_work_satisfy.get(row['Are you satisfied with your work?'].strip().lower()) if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)


def get_satisfy_text(df_data):
    satisfy_type_series = get_satisfy_type_series(df_data)
    def map_data(row):
        satisfy_type = str(satisfy_type_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if satisfy_type == '00':
            # ถ้า occup_type เท่ากับ '0' Are you satisfied with your work?
            mapped_value = row['Are you satisfied with your work?']
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)
    
    # return df_data.apply(lambda row: row['Are you satisfied with your work?'] if str(satisfy_type_series.loc[row.name]) == '00' else '', axis=1)


def get_time_find_work_series(df_data):
    mapping_time_findwork = {
        "1 - 2 months": "02",
        "7 - 9 months": "04",
        "getting a job immediately": "01",
        "3 - 6 months": "03",
        "10 - 12 months": "05",
        "an old job (have been working there even before or during the university study)": "07",
        "over 1 year": "06"
    }

    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
            mapped_value = mapping_time_findwork.get(row['After you graduated, how long did it take you to get a job?'].strip().lower())

        return mapped_value

    return df_data.apply(map_data, axis=1)

    # return df_data.apply(lambda row: mapping_time_findwork.get(row['After you graduated, how long did it take you to get a job?'].strip().lower()) if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)


def get_match_education_series(df_data):
    mapping_time_findwork = {
        "yes": "1",
        "no": "2"
    }

    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
            mapped_value = mapping_time_findwork.get(row['Have you worked in the field that you graduated?'].strip().lower())

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_time_findwork.get(row['Have you worked in the field that you graduated?'].strip().lower()) if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)


def get_apply_education_series(df_data):
    mapping_apply_edu = {
        "to a very great extent": "01",
        "to a great extent": "02",
        "to a moderate extent": "03",
        "a little": "04",
        "very little": "05",
        "05 - very little": "05"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
            mapped_value = mapping_apply_edu.get(row['How can you apply your knowledge to your work?'].strip().lower())

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_apply_edu.get(row['How can you apply your knowledge to your work?'].strip().lower()) if str(work_status_series.loc[row.name]) not in ['3', '4'] else '', axis=1)


def get_cause_nowork_series(df_data):
    mapping_cause_nowork = {
        "could not find a job": "3",
        "don’t want to work now": "1",
        "waiting for the application’s result": "2",
        "willing to be a freelancer": "4",
        "recently quit old job": "0",
        "study in china": "0",
        "helping my parent’s business": "0",
        "recovering after surgery": "0",
        "taking a language course": "0",
        "waiting for the interview": "2",
        "previous employment does not fit with my interest": "0",
        "could not find a job so will pursue the japanese in abroad": "3",
        "hard to find a job as a foreigner in th": "3",
        "own business": "4",
        "family business": "4",
        "prepare to turn pro golf": "0",
        "working on my own clothing business": "4",
        "master's degree": "0",
        "just come back from study english abroad": "0",
        "willing to be a freelancer, but would like to hold down a stable job at the same time.": "4",
        "study master degree": "0",
        "consideration of further studies": "0",
        "i’m just back from work and travel": "0",
        "study": "0",
        "doing freelancing jobs while looking for university to pursue master degree": "4",
        "family’s business": "4",
        "recently got back from work&travel program": "0",
        "still finding a job": "3",
        "do my own business": "4",
        "will pursue master’s degree": "0",
        "waiting for visa and contract to be sent": "2",
        "still hesitant about the job": "0"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_cause_nowork.get(row['If you are unemployed, please specify the most significant reasons:'].strip().lower(),'0')
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)

    # return df_data.apply(lambda row: mapping_cause_nowork.get(row['If you are unemployed, please specify the most significant reasons:'].strip().lower()) if str(work_status_series.loc[row.name]) in ['3'] else '', axis=1)


def get_cause_nowork_text(df_data):
    cause_nowork_series = get_cause_nowork_series(df_data)
    def map_data(row):
        cause_nowork = str(cause_nowork_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if cause_nowork == '0':
            # ถ้า occup_type เท่ากับ '0' If you are unemployed, please specify the most significant reasons:
            mapped_value = row['If you are unemployed, please specify the most significant reasons:']
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)
    
    # return df_data.apply(lambda row: row['If you are unemployed, please specify the most significant reasons:'] if str(cause_nowork_series.loc[row.name]) == '0' else '', axis=1)


def get_problem_find_work_series(df_data):
    mapping_prob_findwork = {
        "yes (could not find a desired job)": "03",  # หางานที่ถูกใจไม่ได้
        "yes (health issues)": "10",                 # ปัญหาด้านสุขภาพ
        "yes (gpa does not meet the requirement)": "14",  # เกรดเฉลี่ยไม่ถึงเกณฑ์ที่กำหนด
        "no": "01",                                  # ไม่มีปัญหา
        "yes (little salary)": "08",                 # เงินเดือนน้อย
        "yes (lack of experience)": "13",            # ขาดประสบการณ์ในการทำงาน
        "yes (lack personal support)": "05",         # ขาดคนสนับสนุน
        "yes (lack information on job availability)": "02",  # ไม่ทราบแหล่งงาน
        "yes (no thai language ability)": "11",       # ขาดทักษะภาษาต่างประเทศ
        "no response from company": "07",            # หน่วยงานไม่ต้องการ
        "yes (rejected by an organization)": "07",   # หน่วยงานไม่ต้องการ
        "yes (does not yet suit lifestyle and life values)": "00",  # อื่นๆให้ระบุ
        "yes(don’t want to take an examination)": "04",  # ต้องสอบจึงไม่อยากสมัคร
        "lack of diploma": "00",                     # อื่นๆให้ระบุ
        "yes - companies do not hire foreigner fresh graduate easily": "00",  # อื่นๆให้ระบุ
        "yes (lack of foreign language skill)": "11", # ขาดทักษะภาษาต่างประเทศ
        "yes (lack of personal support, lack of native language skill, and lack of experience)": "00",  # อื่นๆให้ระบุ (รวมหลายปัญหา)
        "visa/work permit": "00",                    # อื่นๆให้ระบุ
        "lack of goals, don't know what to do": "00",  # อื่นๆให้ระบุ
        "not sure which fields of work i want to work in": "00"  # อื่นๆให้ระบุ
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_prob_findwork.get(row['Do you have any problem in getting a job?'].strip().lower(),'00')
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_prob_findwork.get(row['Do you have any problem in getting a job?'].strip().lower()) if str(work_status_series.loc[row.name]) in ['3'] else '', axis=1)


def get_problem_find_work_text(df_data):
    problem_find_work_series = get_problem_find_work_series(df_data)
    def map_data(row):
        problem_find_work = str(problem_find_work_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if problem_find_work == '00':
            # ถ้า occup_type เท่ากับ '0' Do you have any problem in getting a job?
            mapped_value = row['Do you have any problem in getting a job?']
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)
    
    # return df_data.apply(lambda row: row['Do you have any problem in getting a job?'] if str(problem_find_work_series.loc[row.name]) == '00' else '', axis=1)


def get_workneed_series(df_data):
    mapping_workneed = {
        "thailand": "01",
        "thailand": "01",
        "korea, japan": "02",
        "nepal": "02",
        "oversea": "02",
        "thailand or china": "02",  # มีจีนซึ่งเป็นต่างประเทศ จึงเลือก 02
        "us, eu, aus, canada": "02",
        "overseas - us, uk, japan, korea": "02",
        "europe / singapore": "02",
        "right now, i personally want to get a job in thailand first to earn some experience. in the future, i hope to work in overseas like in china or hong kong.": "01",
        "i can work in thailand but oversea is a better choice": "02",
        "japan": "02",
        "thailand first, then emigrate to new zealand": "01",
        "oversea, working in switzerland": "02",
        "either": "01",  # หากไม่ระบุชัดเจนจะถือเป็นทำงานในประเทศเป็นค่า default
        "prefer work in china": "02",
        "any is fine": "01",  # หากไม่มีข้อจำกัด ให้ถือเป็นในประเทศ (default)
        "overseas, hopefully some where in north america": "02",
        "japanese": "02",
        "as long as english is spokenw": "02",
        "both is fine": "01",  # หากตอบทั้งสอง แต่ไม่ระบุความชอบชัดเจน เราเลือก default เป็น 01
        "both, overseas preferably the us": "02",
        "overseas. the uk or dubai": "02",
        "oversea england": "02",
        "overseas": "02",
        "in thailand": "01",
        "usa or other english speaking countries": "02",
        "no": "01",  # หากตอบว่า "no" (ไม่ได้ระบุว่าต้องการทำงานต่างประเทศ) ให้ถือเป็น 01
        "oversea - china": "02",
        "uk": "02",
        "i would like to work temporary oversea in europe such as germany.": "02",
        "thailand and oversea": "01",  # หากมีทั้งสอง แต่เริ่มต้นทำงานในไทย เราเลือก 01
        "both": "01",
        "i prefer working oversea such as the united states and australia": "02",
        "australia": "02",
        "i prefer to work in either": "01",
        "new zealand": "02",
        "europe or usa": "02",
        "thailand for now": "01",
        "can be both in thailand and oversea": "01",
        "oversea, new zealand and australia": "02",
        "thai": "01",
        "i can live/stay in any places": "01",
        "oversea: usa": "02",
        "in thailand": "01",
        "-": "no data",  # ไม่ระบุ
        "oversea (china)": "02",
        "thailand is fine but oversea is more preferable (malaysia, singapore, western countries)": "02",
        "usa": "02",
        "oversea, usa": "02",
        "korea": "02",
        "i prefer to work in thailand.": "01",
        "oversea, australia": "02",
        "both. to explore more opportunities": "01",
        "i prefer oversea. either england or australia": "02",
        "both domestic and oversea (australia, singapore": "01"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_workneed.get(row['Do you prefer to work in Thailand or oversea?  Please specify the country.'].strip().lower())
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_workneed.get(row['Do you prefer to work in Thailand or oversea?  Please specify the country.'].strip().lower()) if str(work_status_series.loc[row.name]) in ['3'] else '', axis=1)


def get_work_country_series(df_data):
    mapping_nationality = {
        "thailand": "TH",
        "korea, japan": "KR",  # เลือกรหัสแรกคือ KR
        "nepal": "NP",
        "oversea": "no data", # ระบุเป็นต่างประเทศ แต่ไม่ได้ระบุประเทศ ใส่เป็น no data
        "thailand or china": "TH",  # เลือกรหัสแรกคือ TH
        "us, eu, aus, canada": "US",  # เลือกรหัสแรกคือ US
        "overseas - us, uk, japan, korea": "US",  # เลือกรหัสแรกคือ US
        "europe / singapore": "EU",  # เลือกรหัสแรกคือ EU (แม้ว่า EU จะไม่อยู่ในตาราง แต่ใช้เพื่อบ่งบอกกลุ่มยุโรป)
        "right now, i personally want to get a job in thailand first to earn some experience. in the future, i hope to work in overseas like in china or hong kong.": "TH",
        "i can work in thailand but oversea is a better choice": "TH",  # เลือกรหัสแรกคือ TH
        "japan": "JP",
        "thailand first, then emigrate to new zealand": "TH",  # เลือกรหัสแรกคือ TH
        "oversea, working in switzerland": "CH",  # รหัสสวิตเซอร์แลนด์คือ CH
        "either": "",
        "prefer work in china": "CN",
        "any is fine": "",
        "overseas, hopefully some where in north america": "US",  # เลือกรหัสแรกคือ US
        "japanese": "JP",
        "as long as english is spokenw": "",
        "both is fine": "",
        "both, overseas preferably the us": "US",  # เลือกรหัสแรกคือ US
        "overseas. the uk or dubai": "GB",  # เลือกรหัสแรกคือ GB
        "oversea england": "GB",
        "overseas": "",
        "in thailand": "TH",
        "usa or other english speaking countries": "US",  # เลือกรหัสแรกคือ US
        "no": "",
        "oversea - china": "CN",
        "uk": "GB",
        "i would like to work temporary oversea in europe such as germany.": "DE",
        "thailand and oversea": "TH",  # เลือกรหัสแรกคือ TH
        "both": "",
        "i prefer working oversea such as the united states and australia": "US",  # เลือกรหัสแรกคือ US
        "australia": "AU",
        "i prefer to work in either": "",
        "new zealand": "NZ",
        "europe or usa": "EU",  # เลือกรหัสแรกคือ EU
        "thailand for now": "TH",
        "can be both in thailand and oversea": "TH",
        "oversea, new zealand and australia": "NZ",  # เลือกรหัสแรกคือ NZ
        "thai": "TH",
        "i can live/stay in any places": "",
        "oversea: usa": "US",
        "in thailand": "TH",
        "-": "",
        "oversea (china)": "CN",
        "thailand is fine but oversea is more preferable (malaysia, singapore, western countries)": "TH",  # เลือกรหัสแรกคือ TH
        "usa": "US",
        "oversea, usa": "US",
        "korea": "KR",
        "i prefer to work in thailand.": "TH",
        "oversea, australia": "AU",
        "both. to explore more opportunities": "",
        "i prefer oversea. either england or australia": "GB",  # เลือกรหัสแรกคือ GB
        "both domestic and oversea (australia, singapore": "AU"  # เลือกรหัสแรกคือ AU
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_nationality.get(row['Do you prefer to work in Thailand or oversea?  Please specify the country.'].strip().lower())
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_nationality.get(row['Do you prefer to work in Thailand or oversea?  Please specify the country.'].strip().lower()) if str(work_status_series.loc[row.name]) in ['3'] else '', axis=1)


def get_work_position_series(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบเป็นค่า value
            mapped_value = row['What is your preference position?']
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: str(row["What is your preference position?"]).strip() if str(work_status_series.loc[row.name]) in ['3'] else '', axis=1)
    

def get_work_series(df_data):
    mapping_workneed = {
        "thailand": "01",
        "thailand": "01",
        "korea, japan": "02",
        "nepal": "02",
        "oversea": "02",
        "thailand or china": "02",  # มีจีนซึ่งเป็นต่างประเทศ จึงเลือก 02
        "us, eu, aus, canada": "02",
        "overseas - us, uk, japan, korea": "02",
        "europe / singapore": "02",
        "right now, i personally want to get a job in thailand first to earn some experience. in the future, i hope to work in overseas like in china or hong kong.": "01",
        "i can work in thailand but oversea is a better choice": "02",
        "japan": "02",
        "thailand first, then emigrate to new zealand": "01",
        "oversea, working in switzerland": "02",
        "either": "01",  # หากไม่ระบุชัดเจนจะถือเป็นทำงานในประเทศเป็นค่า default
        "prefer work in china": "02",
        "any is fine": "01",  # หากไม่มีข้อจำกัด ให้ถือเป็นในประเทศ (default)
        "overseas, hopefully some where in north america": "02",
        "japanese": "02",
        "as long as english is spokenw": "02",
        "both is fine": "01",  # หากตอบทั้งสอง แต่ไม่ระบุความชอบชัดเจน เราเลือก default เป็น 01
        "both, overseas preferably the us": "02",
        "overseas. the uk or dubai": "02",
        "oversea england": "02",
        "overseas": "02",
        "in thailand": "01",
        "usa or other english speaking countries": "02",
        "no": "01",  # หากตอบว่า "no" (ไม่ได้ระบุว่าต้องการทำงานต่างประเทศ) ให้ถือเป็น 01
        "oversea - china": "02",
        "uk": "02",
        "i would like to work temporary oversea in europe such as germany.": "02",
        "thailand and oversea": "01",  # หากมีทั้งสอง แต่เริ่มต้นทำงานในไทย เราเลือก 01
        "both": "01",
        "i prefer working oversea such as the united states and australia": "02",
        "australia": "02",
        "i prefer to work in either": "01",
        "new zealand": "02",
        "europe or usa": "02",
        "thailand for now": "01",
        "can be both in thailand and oversea": "01",
        "oversea, new zealand and australia": "02",
        "thai": "01",
        "i can live/stay in any places": "01",
        "oversea: usa": "02",
        "in thailand": "01",
        "-": "no data",  # ไม่ระบุ
        "oversea (china)": "02",
        "thailand is fine but oversea is more preferable (malaysia, singapore, western countries)": "02",
        "usa": "02",
        "oversea, usa": "02",
        "korea": "02",
        "i prefer to work in thailand.": "01",
        "oversea, australia": "02",
        "both. to explore more opportunities": "01",
        "i prefer oversea. either england or australia": "02",
        "both domestic and oversea (australia, singapore": "01"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_workneed.get(row['Do you prefer to work in Thailand or oversea?  Please specify the country.'].strip().lower(),'0')
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_workneed.get(row['Do you prefer to work in Thailand or oversea?  Please specify the country.'].strip().lower()) if str(work_status_series.loc[row.name]) in ['3'] else '', axis=1)


def get_skill_development_text(df_data):
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบเป็นค่า value
            mapped_value = str(row['What is your skills or curriculum that you want to improve?']).strip()
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: str(row['What is your skills or curriculum that you want to improve?']).strip() if str(work_status_series.loc[row.name]) in ['3'] else '', axis=1)


def get_disclosure_agreement_text(df_data):
    mapping_disclosure_agreement= {
        "no, i am not willing to reveal any information.": "0",
        "i am willing to reveal the information for all employers.": "1",
        "i am willing to reveal the information for all employers except in insurance and direct sale industry.": "3",
        "i am willing to reveal the information for all employers except in workforce, insurance and direct sale industry.": "4",
        "i am willing to reveal the information for all employers except in workforce industry.": "2"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_disclosure_agreement.get(str(row['Are you willing to reveal this information for employers/organization to applying a job?']).strip().lower(),'0')
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_disclosure_agreement.get(str(row['Are you willing to reveal this information for employers/organization to applying a job?']).strip().lower()) if str(work_status_series.loc[row.name]) in ['3'] else '', axis=1)


def get_require_education_series(df_data):
    mapping_required_education = {
        "yes": "1",
        "no": "2"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 2 || 4
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['2', '4']:
            # ถ้า work_status เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
            mapped_value = mapping_required_education.get(str(row['Do you want to further your study?']).strip().lower())

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: mapping_required_education.get(str(row['Do you want to further your study?']).strip().lower()) if str(work_status_series.loc[row.name]) in ['2','4'] else '', axis=1)


def get_level_education_series(df_data):
    mapping_level_education = {
        "master's degree": "60",   # ปริญญาโท
        "a certificate/specialization (which offers higher rate of salary than a doctor’s degree.)": "90",  # ประกาศนียบัตรหรือหลักสูตรเฉพาะ(ที่บรรจุในอัตราเงินเดือนสูงกว่าปริญญาเอก)
        "graduate diploma": "50",  # ประกาศนียบัตรบัณฑิต
        "bachelor's degree": "40", # ปริญญาตรี
        "doctoral degree": "80",   # ปริญญาเอก
        "a higher graduate diploma": "70",  # ประกาศนียบัตรบัณฑิตชั้นสูง
        "cfa": "90",               # ประกาศนียบัตรหรือหลักสูตรเฉพาะ (ในที่นี้ถือว่าเป็นหลักสูตรเฉพาะ)
        "currently in master’s degree": "60",  # ปริญญาโท
        "md": "80",                # MD ถือเป็นปริญญาเอกในด้านการแพทย์
        "language courses": "30"   # ประกาศนียบัตรวิชาชีพชั้นสูง (ในกรณีที่เป็นหลักสูตรหรือประกาศนียบัตรด้านภาษา)
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 2 || 4
    work_status_series = get_work_status_series(df_data)
    # เรียกใช้ฟังก์ชัน get_require_education_series เพื่อรับ Series ของความต้องการเรียนต่อ == 1
    required_education_series = get_require_education_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])
        required_education = str(required_education_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['2', '4']:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
            mapped_value = mapping_level_education.get(str(row['What level you want to further your study?']).strip().lower())
        else:
            if required_education == '1':
                # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
                mapped_value = mapping_level_education.get(str(row['What level you want to further your study?']).strip().lower())
            else:
                mapped_value = ''
            # ถ้า work_status ไม่เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            # mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # required_education_series = get_require_education_series(df_data)
    
    # def map_level_education(row):
    #     # ทำความสะอาดข้อมูลใน 'Position' โดยลบช่องว่างส่วนเกิน
    #     cleaned_data = str(row['What level you want to further your study?']).strip().lower()
    #     if str(work_status_series.loc[row.name]) in ['2', '4']:
    #         if str(required_education_series.loc[row.name]) == '1':
    #             return mapping_level_education.get(cleaned_data)
    #         else:
    #             return ''
    #     else:
    #         return ''
    
    # # 5) ใช้ .apply(...) เพื่อสร้าง Series ใหม่
    # return df_data.apply(map_level_education, axis=1)


def get_program_education_series(df_data):
    mapping_program_education = {
        "same field of study": "1",
        "different field of study": "2"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 2 || 4
    work_status_series = get_work_status_series(df_data)
    # เรียกใช้ฟังก์ชัน get_require_education_series เพื่อรับ Series ของความต้องการเรียนต่อ == 1
    required_education_series = get_require_education_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])
        required_education = str(required_education_series.loc[row.name])
        
        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['2', '4']:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
            mapped_value = mapping_program_education.get(str(row['What field you want to further your study?']).strip().lower())
        else:
            if required_education == '1':
                # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
                mapped_value = mapping_program_education.get(str(row['What field you want to further your study?']).strip().lower())
            else:
                mapped_value = ''
            # ถ้า work_status ไม่เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            # mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # required_education_series = get_require_education_series(df_data)
    
    # def map_program_education(row):
    #     # ทำความสะอาดข้อมูลใน 'Position' โดยลบช่องว่างส่วนเกิน
    #     cleaned_data = str(row['What field you want to further your study?']).strip().lower()
    #     if str(work_status_series.loc[row.name]) not in ['2', '4']:
    #         if str(required_education_series.loc[row.name]) == '1':
    #             return mapping_program_education.get(cleaned_data)
    #         else:
    #             return ''
    #     else:
    #         return ''
    
    # # 5) ใช้ .apply(...) เพื่อสร้าง Series ใหม่
    # return df_data.apply(map_program_education, axis=1)


def get_program_education_id_series(df_data):
    mapping_program_education = {
        "Business": "000013",  # BUSINESS
        "Design & Illustration / 3D": "003359",  # 3D ANIMATION/DIGITAL EFFECTS
        "Cultural Heritage Management": "001956",  # ARCHITECTURAL HERITAGE MANAGEMENT AND TOURISM
        "Creative Communications": "000125",  # COMMUNICATION ARTS
        "Related marketing or business": "000027",  # การจัดการการตลาด
        "Psychology": "000395",  # จิตวิทยา
        "Marketing": "000101",  # การตลาด
        "Biomedical science": "000448",  # ชีวเวชศาสตร์
        "Business management, HR": "000053",  # การจัดการทรัพยากรมนุษย์
        "I haven't decided yet": "000000",  # ยังไม่ระบุ
        "Data": "000063",  # BUSINESS DATA ANALYSIS
        "Environmental Science": "000482",  # ENVIRONMENTAL SCIENCE
        "Biology": "000431",  # ชีววิทยา
        "Finance": "000318",  # การเงิน
        "N/A": "000000",  # ไม่ระบุ
        "Quantitative Finance": "001740",  # เศรษฐศาสตร์การเงิน
        "Risk": "001944",  # การจัดการความเสี่ยง
        "Marketing (duplicate)": "000101",  # การตลาด
        "Philosophy": "000630",  # ปรัชญา
        "Global Business": "000093",  # BUSINESS MANAGEMENT
        "Finance / Financial Engineering": "000318",  # เลือกเป็น “การเงิน” ไว้ก่อน
        "Business , marketing, branding": "000027",  # การจัดการการตลาด (หรือการตลาด)
        "Biological and chemical engineering for a sustainable bioeconomy": "000102",  # CHEMICAL ENGINEERING (ใกล้เคียงสุด)
        "Data Analytics": "000063",  # BUSINESS DATA ANALYSIS
        "Clinical Pharmacology/ Drug Development": "000447",  # ชีวเภสัชกรรม (BIOPHARMACEUTICS)
        "Management / Finance": "000024",  # การจัดการ (ควบคู่การเงิน)
        "Cookery": "000315",  # การอาหาร
        "Data Science": "000063",  # BUSINESS DATA ANALYSIS (ไม่มี data science ตรงตัว เลือกใกล้เคียง)
        "Business Management": "000093",  # BUSINESS MANAGEMENT
        "Marketing or Advertisement": "000339",  # การโฆษณา (หรือใช้การตลาด 000101 ก็ได้)
        "Fashion Merchandising": "000536",  # FASHION DESIGN
        "Computer Science": "000167",  # COMPUTER SCIENCE
        "Consumer psychology/ psychology": "000395",  # จิตวิทยา
        "International Relations": "000368",  # ความสัมพันธ์ระหว่างประเทศ
        "Dietetics and Nutrition": "000926",  # วิทยาศาสตร์การอาหารและโภชนาการ
        "not sure yet": "000000",
        "Business (duplicate)": "000013",
        "Material Science": "000856",  # วัสดุศาสตร์
        "MBA": "000050",  # BUSINESS ADMINISTRATION
        "Mba": "000050",  # BUSINESS ADMINISTRATION
        "Occupational Psychology": "000411",  # จิตวิทยาอุตสาหกรรมและองค์การ
        "Sport Science": "000919",  # วิทยาศาสตร์การกีฬา
        "Architect": "001119",  # สถาปัตยกรรม
        "Product Management": "000031",  # การจัดการการผลิต
        "BBA / Management": "000050",  # BUSINESS ADMINISTRATION
        "Music Production": "001309",  # MUSIC COMPOSITION (ใกล้เคียง)
        "Bussiness Management": "000093",  # BUSINESS MANAGEMENT
        "Cinematography": "000728",  # ภาพยนตร์
        "Visual Communication / Fashion Business": "000125",  # COMMUNICATION ARTS (หรือ 000536 ก็ได้)
        "I haven't decided yet.": "000000",
        "Teaching certification in Biology": "000437",  # ชีววิทยาศึกษา
        "MBA (Master of Business Administration)": "000050", 
        "Psychology (duplicate)": "000395",
        "Nutrition and Dietetics": "000926", 
        "undecide": "000000",
        "Entrepreneur and Management": "000323",  # การเป็นผู้ประกอบการ
        "in relating to business": "000013",
        "Not yet design": "000000",
        "Forecast and planning analysis. Data analysis.": "000063",
        "Software Engineer": "000997",  # วิศวกรรมซอฟต์แวร์
        "chemistry": "001283",  # CHEMISTRY
        "Politics": "000325",  # การเมืองการปกครอง
        "Languages or film studies": "000728",  # ภาพยนตร์ (หรือเลือกสายภาษาก็ได้)
        "Public Relations": "000174",  # การประชาสัมพันธ์
        "UI / UX": "000305",  # การออกแบบ (ใกล้เคียงสุด)
        "Musical theatre": "000540",  # นาฏศิลปสากล (แทน Musical theatre)
        "Politics and International Relations with specialised focus in international conflict and security studies": "000369", 
        "MANAGEMENT ENGINEERING": "000057",  # การจัดการทางวิศวกรรม
        "-": "000000",
        "MBA Management/Marketing": "000050",
        "Will think about it": "000000",
        "Entrepreneur": "000323",
        "Computer Science (specialization currently unsure)": "000167",
        "Film Directing": "000728",
        "Bussiness": "000013",
        "Occupational Health and Safety": "001241",  # อาชีวอนามัย
        "Music": "000470",  # ดนตรี
        "Fashion": "000536",  # FASHION DESIGN
        "Tourism and Hospitality": "000107",  # การท่องเที่ยว
        "Business or language": "000013",
        "BBA, accounting": "000165",  # การบัญชีและการภาษีอากร (เป็นตัวอย่าง)
        "Digital Marketing": "001079",  # ELECTRONIC MARKETING
        "Infectious Diseases and Viral Therapeutics": "000822",  # ระบาดวิทยา (พอใกล้เคียงโรคติดเชื้อ)
        "Medicine": "001565",  # แพทยศาสตร์
        "Physiology": "001130",  # สรีรวิทยา
        "Management": "000024",
        "Information Technology Management or similar fields": "000960",  # INFORMATION SYSTEMS MANAGEMENT
        "English as a foreign language": "000285",  # การสอนภาษาอังกฤษเป็นภาษาต่างประเทศ
        "Digital Marketing (duplicate)": "001079",
        "Interaction UX&UI": "000305",  # การออกแบบ
        "Art": "000555",  # FINE ARTS
        "Business and Marketing": "000101",
        "maketing": "000101",
        "Human computer interaction": "000994",  # วิศวกรรมคอมพิวเตอร์ (ใกล้สุด)
        "Biomedical related": "000448",
        "MSc Finance": "000318",
        "about real estate": "000529",  # ธุรกิจอสังหาริมทรัพย์
        "Marketing field": "000101",
        "Unsure": "000000",
        "Revenue Management": "000318",  # การเงิน
        "Health Food Innovation Management": "000926",
        "Medicine (duplicate)": "001565",
        "Hospitality Management": "000161",  # การบริหารโรงแรม
        "statistics": "001125",  # สถิติ
        "Language": "000757",  # ภาษาอังกฤษ (เป็นตัวแทน)
        "Entrepreneurship and Innovation Management": "000323",
        "Data (duplicate)": "000063",
        "Media / Entertainment": "000125",
        "Business Analytics": "000063",
        "Branding, Marketing": "000101",
        "Not studying": "000000",
        "Master of Management": "000093",
        "Social and Digital Marketing": "001079",
        "General Management": "000054",  # การจัดการทั่วไป
        "Fashion Design": "000536",
        "Agriculture": "000317",  # การเกษตร
        "Sound creator": "000488",  # ดุริยางคศึกษา (หรือจะเลือกดนตรีสากล)
        "Business Administration": "000050",
        "International business": "000527",  # ธุรกิจระหว่างประเทศ
        "Logistics": "000026",
        "Economics": "001534",  # เศรษฐศาสตร์
        "Business / Marketing": "000101",
        "Chinese Language": "000730",  # ภาษาจีน
        "Don’t know yet": "000000",
        "Computer engineering": "000994",
        "Hospitality": "000343",  # การโรงแรม
        "Economic": "001534",
        "MBA, but also sciences": "000050",
        "Data Analysis": "000063",
        "Law": "000001",  # กฎหมาย
        "Business management": "000093",
        "Undecided": "000000",
        "Music Business": "000470",  # ดนตรี (ตัวแทน)
        "Business Management/HR": "000053",
        "Finance & technology, innovation management": "000318",  # การเงิน (เป็นตัวแทน)
        "International management": "000064",  # การจัดการธุรกิจระหว่างประเทศ
        "Strategic Communication Management": "000125",
        "Faculty of Law": "000001",
        "Media and Communication": "000125",
        "Event management": "000232",  # CONVENTION AND EVENT MANAGEMENT
        "Innovation and entrepreneurship": "000476",  # ENTREPRENEURSHIP
        "Sales/Marketing": "000101",
        "Energy transition/ policy development / sustainability": "000678",  # พลังงานทดแทน
        "Market research": "000101",
        "International development studies": "000283",  # DEVELOPMENT COMMUNICATION (หรือ EDUCATION) เลือกเป็นตัวอย่าง
        "Product Managment/Innovation/Design haven't decide yet": "000000",
        "Advertising tactics": "000339",  # การโฆษณา
        "Sound design": "000470",  # ดนตรี (หรือสาขาดนตรี/เสียง)
        "International Business Management": "000064",  # การจัดการธุรกิจระหว่างประเทศ
        "Psychology or Business": "000000",  # ยังไม่แน่
        "Logistics, Luxury brand management": "000026",
        "Digital Marketing / Communications": "001079",
        "Leadership and management": "000024",
        "Digital marketing (maybe/ not sure yet)": "001079",
        "Nutrition": "000926",
        "not decided yet": "000000",
        "Art and design": "000305",
        "IB": "000527",  # ธุรกิจระหว่างประเทศ
        "Real estate": "000529",
        "Computer Science / Data Analystic": "000167",
        "I am not sure": "000000",
        "Not yet to decide": "000000",
        "Good governance/Political Science/International Relations/Public Policy": "000369", 
        "Public Policy, Sustainable Development": "000561",  # นโยบายสาธารณะ
        "Cosmetics Science": "000000",  # ไม่พบตรง
        "ir": "000368",  # ความสัมพันธ์ระหว่างประเทศ
        "Chinese Economy": "001676",  # จีนในระบบเศรษฐกิจโลก
        "UX/UI or product design": "000305",
        "Interpretation and translation": "000336",  # การแปลและการล่าม
        "Artificial Intelligence": "000167",  # COMPUTER SCIENCE (แทน AI)
        "Fashion Management": "000536", 
        "Law, international relations": "000007",  # กฎหมายระหว่างประเทศ
        "Supply chain and logistic management": "000026",
        "Liberal Arts": "001738",  # ศิลปศาสตร์
        "Product Design": "000311",  # การออกแบบผลิตภัณฑ์
        "Business and Management": "000093",
        "May be International commercial laws, international business management, or something relate to risk management in business": "002530",  # กฎหมายการค้าระหว่างประเทศ
        "Business administration": "000050",
        "Management (Marketing)": "000101",  # การตลาด
        "graphic design and art": "000305",
        "Mbi": "000063",  # สมมติให้เป็น Business Data
        "Master in management": "000024",
        "Cosmetic Chemistry": "000000",
        "Import and export": "000000",
        "Policy": "000561",
        "Doctor of medicine": "001565",
        "Branding and Marketing": "000101",
        "Economics": "001534",
        "Economic development, International Development": "000284",  # DEVELOPMENT ECONOMICS
        "AI / ML": "000167", 
        "Still not sure but will be business-related": "000000",
        "Marketing but maybe something more exciting and more specific": "000101",
        "Public policy/ Marine resources management": "000561", 
        "Sustainability": "000219",  # การพัฒนาอย่างยั่งยืน
        "Medical Sciences": "000931", 
        "Haven’t decided": "000000",
        "International Relations or International Law": "000368", 
        "Media and communications": "000125",
        "Art Entertainment Music": "000555",  # FINE ARTS (ตัวแทน)
        "I’m currently studying environmental engineering and management": "001023",  # วิศวกรรมสิ่งแวดล้อม
        "Matsci": "000856",  # วัสดุศาสตร์
        "Languages": "000757",  # ภาษาอังกฤษ (ตัวแทน)
        "Investment": "000318",  # การเงิน
        "International Business": "000527",
        "Management scholl": "000024",  # การจัดการ
        "Businedd": "000013",
        "Entrepreneurship": "000323",
        "Communication design": "000305",
        "Finance/ Accounting/ Businesses": "000318", 
        "Law, Advance International Relations": "000007",
        "MBA": "000050",
        "TBA": "000000",
        "Economic and International Economic & Finance": "001534",
        "Dentistry": "000514",
        "Branding": "000101",
        "Graphic": "000305",
        "MBA, Marketing": "000050",
        "Project management": "000245",  # การวางแผนและประเมินผลโครงการ (ใกล้เคียง)
        "I want to study in more culture and literature.": "000785",  # ภาษาและวรรณคดีไทย
        "International Development": "000284",
        "Finance, and economics": "000318",
        "Development Planning": "000240",  # การวางแผนภาคและเมือง
        "Management (duplicate)": "000024",
        "Master of Business Administration": "000050",
        "Management of Innovation": "000024",  # การจัดการ (กว้าง ๆ)
        "Counseling Psychology": "000397",  # จิตวิทยาการปรึกษา
        "Accountancy": "000163",  # การบัญชีบริหาร
        "maybe Law": "000000",
        "Human Rights and Humanitarian Assistance": "001177",  # สิทธิมนุษยชน
        "Social Innovation and enterpreneurship, ethical marketing": "000323",
        "Food Science": "000926",
        "International Political Economy": "001541",  # เศรษฐศาสตร์การเมือง
        "law or marketing": "000000",
        "Chef": "000315",  # การอาหาร
        "Innovation and Entreprenuership": "000476",  # ENTREPRENEURSHIP
        "Refugee protection (Children, elders, etc)": "000000",
        "Toursim - Hospitality": "000107",
        "Accounting": "000163",
        "Business innovation": "000060",  # การจัดการธุรกิจ (หรือจะเลือก 000000 ก็ได้)
        "Property": "000529",
        "MBA programme": "000050",
        "Market and digital communication": "001079",
        "Data Analytics and Human Resources Management": "000000",  # ไม่มีตรงมาก
        "Development Studies": "000283",
        "Global development": "000283",
        "Com Sci / AI / Law": "000000",
        "Immunology": "000902",  # วิทยาภูมิคุ้มกัน
        "Social Policy": "000562",  # นโยบายและการวางแผนสังคม
        "Science": "000904",  # วิทยาศาสตร์
        "strategic security": "000000",
        "Political science": "000837",  # รัฐศาสตร์
        "International History": "000625",  # ประวัติศาสตร์เอเชียตะวันออกเฉียงใต้ (เป็นตัวแทน)
        ".": "000000",
        "marketing": "000101",  # การตลาด
        "fashion": "000536",  # FASHION DESIGN
        "Not sure yet": "000000",
        "business": "000013",  # BUSINESS
    }

    # เรียกใช้ฟังก์ชัน get_program_education_series เพื่อรับ Series ของสถานะการทำงาน
    program_education_series = get_program_education_series(df_data)
    
    def map_data(row):
        program_education = str(program_education_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if program_education == '2':
            # ถ้า program_education เท่ากับ '2' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_program_education.get(str(row['Please specify field of study.']).strip())
            if str(row['Please specify field of study.']).strip() == 'N/A' or pd.isna(row['Please specify field of study.']):
                mapped_value = "000000"
        else:
            # ถ้า program_education เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)

    # def map_program_education_id(row):
    #     # ทำความสะอาดข้อมูลใน 'Please specify field of study.' โดยลบช่องว่างส่วนเกิน
    #     cleaned_data = str(row['Please specify field of study.'])#.strip().lower()
    #     if str(program_education_series.loc[row.name]) == '2':
    #         return mapping_program_education.get(cleaned_data)
    #     else:
    #         return ''
    
    # # 5) ใช้ .apply(...) เพื่อสร้าง Series ใหม่
    # return df_data.apply(map_program_education_id, axis=1)


def get_type_university_series(df_data):
    mapping_type_univ = {
        "public": "1",    # รัฐบาล
        "private": "2",   # เอกชน
        "overseas": "3"  # ต่างประเทศ
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 2 || 4
    work_status_series = get_work_status_series(df_data)
    # เรียกใช้ฟังก์ชัน get_require_education_series เพื่อรับ Series ของความต้องการเรียนต่อ == 1
    required_education_series = get_require_education_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])
        required_education = str(required_education_series.loc[row.name])
        
        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['2', '4']:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
            mapped_value = mapping_type_univ.get(str(row['What type of university/institute you want to further your study?']).strip().lower())
        else:
            if required_education == '1':
                # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
                mapped_value = mapping_type_univ.get(str(row['What type of university/institute you want to further your study?']).strip().lower())
            else:
                mapped_value = ''
            # ถ้า work_status ไม่เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            # mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)

    # required_education_series = get_require_education_series(df_data)
    
    # def map_type_education(row):
    #     # ทำความสะอาดข้อมูลใน 'type university' โดยลบช่องว่างส่วนเกิน
    #     cleaned_data = str(row['What type of university/institute you want to further your study?']).strip().lower()
    #     if str(work_status_series.loc[row.name]) not in ['2', '4']:
    #         if str(required_education_series.loc[row.name]) == '1':
    #             return mapping_type_univ.get(cleaned_data)
    #         else:
    #             return ''
    #     else:
    #         return ''
    
    # # 5) ใช้ .apply(...) เพื่อสร้าง Series ใหม่
    # return df_data.apply(map_type_education, axis=1)


def get_cause_education_series(df_data):
    mapping_cause_education = {
        "parent’s desire": "1",  # เป็นความต้องการของบิดา/มารดา หรือผู้ปกครอง
        "my own desire": "4",    # เป็นความต้องการของตนเอง
        "career requirement": "2",  # งานที่ต้องการต้องใช้วุฒิสูงกว่า ปริญญาตรี
        "scholarship acquirement": "3",  # ได้รับทุนศึกษาต่อ
        "not studying man….": "0",  # อื่นๆให้ระบุ
        "growth in career path": "4",  # เป็นความต้องการของตนเอง
        "more knowledge": "4",  # เป็นความต้องการของตนเอง
        "exploring overseas' academic and also for the sake of career advancement": "4",  # เป็นความต้องการของตนเอง
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 2 || 4
    work_status_series = get_work_status_series(df_data)
    # เรียกใช้ฟังก์ชัน get_require_education_series เพื่อรับ Series ของความต้องการเรียนต่อ == 1
    required_education_series = get_require_education_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])
        required_education = str(required_education_series.loc[row.name])
    
        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['2', '4']:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
            mapped_value = mapping_cause_education.get((str(row['What are the reasons for furthering your study?']).strip().lower()),'0')
        else:
            if required_education == '1':
                # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
                mapped_value = mapping_cause_education.get((str(row['What are the reasons for furthering your study?']).strip().lower()),'0')
            else:
                mapped_value = ''
            # ถ้า work_status ไม่เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            # mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)
    # required_education_series = get_require_education_series(df_data)
    
    # def map_cause_education(row):
    #     # ทำความสะอาดข้อมูลใน 'reasons for furthering your study' โดยลบช่องว่างส่วนเกิน
    #     cleaned_data = str(row['What are the reasons for furthering your study?']).strip().lower()
    #     if str(work_status_series.loc[row.name]) not in ['2', '4']:
    #         if str(required_education_series.loc[row.name]) == '1':
    #             return mapping_cause_education.get(cleaned_data)
    #         else:
    #             return ''
    #     else:
    #         return ''
    
    # # 5) ใช้ .apply(...) เพื่อสร้าง Series ใหม่
    # return df_data.apply(map_cause_education, axis=1)


def get_cause_education_text(df_data):
    
    # เรียกใช้ฟังก์ชัน get_cause_education_series เพื่อรับ Series ของสถานะการทำงาน
    cause_education_series = get_cause_education_series(df_data)
    def map_data(row):
        value = str(cause_education_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if value == '0':
            # ถ้า cause_education_series เท่ากับ '0' ตอบกลับเป็นค่า What are the reasons for furthering your study?
            mapped_value = row['What are the reasons for furthering your study?']
        else:
            # ถ้า cause_education_series เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)
    
    # return df_data.apply(lambda row: row['What are the reasons for furthering your study?'].strip() if str(cause_education_series.loc[row.name]) == '0' else '', axis=1)


def get_problem_education_series(df_data):
    mapping_problem_education = {
        "no": "01",  # ไม่มีปัญหา
        "yes (lack of academic qualifications)": "03",  # คุณสมบัติในการสมัครเรียน
        "yes (lack of financial support)": "05",  # ขาดแคลนเงินทุน
        "all of the above": "00",  # อื่นๆให้ระบุ (ตอบหลายข้อ)
        "i'm not sure if studying in thailand or abroad would be the better option": "02",  # ข้อมูลสถานที่ศึกษาต่อไม่เพียงพอ
        """i"m not sure if studying in Thailand or abroad would be the better option""": "02",  # ข้อมูลสถานที่ศึกษาต่อไม่เพียงพอ
        "yes (insufficient required knowledge)": "04",  # ขาดความรู้พื้นฐานในการศึกษาต่อ
        "yes (insufficient institution information)": "02",  # ข้อมูลสถานที่ศึกษาต่อไม่เพียงพอ
        "yes (not yet pass audition)": "03",  # คุณสมบัติในการสมัครเรียน (ผ่านการออดิชั่น)
        "studying in thai language": "00",  # อื่นๆให้ระบุ
        "yes (unavailable free time)": "00",  # อื่นๆให้ระบุ
        "yes because the university system changed to put all the grades from exchange university back to muic, when back then students can choose which courses to transfer back, and i was not satisfy with the results since they put me to study with master's degree students and the head of exchange unit was not being nice once i sent the grade results": "00",  # อื่นๆให้ระบุ
        "not sure about field of studies": "00",  # อื่นๆให้ระบุ
        "work condition": "00",  # อื่นๆให้ระบุ
        "have not decided which field to study yet.": "00",  # อื่นๆให้ระบุ
        "i want to gain experience in working before continuing studying.": "00",  # อื่นๆให้ระบุ
        "money and chore problem lol": "05",  # ขาดแคลนเงินทุน
        "some problems with lack of physical diploma before the graduation ceremony (however it’s been resolved)": "03",  # คุณสมบัติในการสมัครเรียน
        "yes (lack of work experience)": "00",  # อื่นๆให้ระบุ
        "working": "00",  # อื่นๆให้ระบุ
        "lack of working experiences": "00",  # อื่นๆให้ระบุ
    }
    
        # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 2 || 4
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 2 || 4
    work_status_series = get_work_status_series(df_data)
    # เรียกใช้ฟังก์ชัน get_require_education_series เพื่อรับ Series ของความต้องการเรียนต่อ == 1
    required_education_series = get_require_education_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])
        required_education = str(required_education_series.loc[row.name])
    
        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['2', '4']:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
            mapped_value = mapping_problem_education.get(str(row['Do you have any problem in furthering your study?']).strip().lower())
        else:
            if required_education == '1':
                # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
                mapped_value = mapping_problem_education.get(str(row['Do you have any problem in furthering your study?']).strip().lower())
            else:
                mapped_value = ''
            # ถ้า work_status ไม่เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            # mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)

    # required_education_series = get_require_education_series(df_data)
    
    # def map_problem_education(row):
    #     # ทำความสะอาดข้อมูลใน 'problem in furthering your study' โดยลบช่องว่างส่วนเกิน
    #     cleaned_data = str(row['Do you have any problem in furthering your study?']).strip().lower()
    #     if str(work_status_series.loc[row.name]) not in ['2', '4']:
    #         if str(required_education_series.loc[row.name]) == '1':
    #             return mapping_problem_education.get(cleaned_data)
    #         else:
    #             return ''
    #     else:
    #         return ''
    
    # # 5) ใช้ .apply(...) เพื่อสร้าง Series ใหม่
    # return df_data.apply(map_problem_education, axis=1)


def get_problem_education_text(df_data):
    
    # เรียกใช้ฟังก์ชัน get_problem_education_series เพื่อรับ Series ของสถานะการทำงาน
    problem_education_series = get_problem_education_series(df_data)
    def map_data(row):
        value = str(problem_education_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if value == '00':
            # ถ้า cause_education_series เท่ากับ '00' ตอบกลับเป็นค่า Do you have any problem in furthering your study?
            mapped_value = row['Do you have any problem in furthering your study?']
        else:
            # ถ้า cause_education_series เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)

    # return df_data.apply(lambda row: row['Do you have any problem in furthering your study?'].strip() if str(problem_education_series.loc[row.name]) == '00' else '', axis=1)


def get_parse_program_data(df):
    """
    รับ DataFrame ที่มีคอลัมน์ 'program_data' ซึ่งเก็บสตริงในรูปแบบ
      "QN_ADDPROGRAM1 (AX) English Language, QN_ADDPROGRAM2 (AY) Computer, QN_ADDPROGRAM3 (AZ) Accounting, 
       QN_ADDPROGRAM4 (BA) Internet, QN_ADDPROGRAM5 (BB) Job training, QN_ADDPROGRAM6 (BC) Research Methodology, 
       QN_ADDPROGRAM8 (BE) Chinese Language, QN_ADDPROGRAM9 (BF) Languages in ASEAN"
       
    ฟังก์ชันนี้จะทำการ:
      1. ตัดส่วน "QN_ADDPROGRAMx (??)" ออกออก เพื่อให้เหลือเฉพาะข้อความหลัก
      2. ตรวจสอบข้อความที่ได้เทียบกับ mapping ที่กำหนดไว้
      3. กำหนดค่าให้กับคอลัมน์ต่าง ๆ ดังนี้:
         - QN_ADDPROGRAM1, QN_ADDPROGRAM2, QN_ADDPROGRAM3, QN_ADDPROGRAM4,
           QN_ADDPROGRAM5, QN_ADDPROGRAM6, QN_ADDPROGRAM8, QN_ADDPROGRAM9
         - รายการที่ไม่ตรงกับ mapping จะถือเป็น "อื่นๆ" 
           โดยตั้งค่า QN_ADDPROGRAM7 = 1 และเก็บข้อความไว้ใน QN_ADDPROGRAM7_TXT
           
    คอลัมน์ใหม่ทั้งหมดที่จะเพิ่ม:
      QN_ADDPROGRAM1, QN_ADDPROGRAM2, QN_ADDPROGRAM3, QN_ADDPROGRAM4,
      QN_ADDPROGRAM5, QN_ADDPROGRAM6, QN_ADDPROGRAM7, QN_ADDPROGRAM8,
      QN_ADDPROGRAM9, QN_ADDPROGRAM7_TXT
    """
    # กำหนดชื่อคอลัมน์ใหม่ที่ต้องการเพิ่ม
    new_columns = ['QN_ADDPROGRAM1', 'QN_ADDPROGRAM2', 'QN_ADDPROGRAM3', 
                   'QN_ADDPROGRAM4', 'QN_ADDPROGRAM5', 'QN_ADDPROGRAM6', 
                   'QN_ADDPROGRAM7', 'QN_ADDPROGRAM8', 'QN_ADDPROGRAM9', 
                   'QN_ADDPROGRAM7_TXT']
    
    # สร้างคอลัมน์ใหม่ใน DataFrame โดยตั้งค่าเริ่มต้นเป็น 0 (หรือค่าว่างสำหรับข้อความ)
    for col in new_columns:
        df[col] = 0
    df['QN_ADDPROGRAM7_TXT'] = ""
    
    # กำหนด mapping ระหว่างข้อความ (หลังจากตัด prefix) กับคอลัมน์ที่ต้องการ
    mapping = {
        "English Language": "QN_ADDPROGRAM1",
        "Computer": "QN_ADDPROGRAM2",
        "Accounting": "QN_ADDPROGRAM3",
        "Internet": "QN_ADDPROGRAM4",
        "Job training": "QN_ADDPROGRAM5",
        "Research Methodology": "QN_ADDPROGRAM6",
        "Chinese Language": "QN_ADDPROGRAM8",
        "Languages in ASEAN": "QN_ADDPROGRAM9"
    }
    
    # Pattern สำหรับตัดส่วน "QN_ADDPROGRAMx (??)" ออก
    prefix_pattern = r"^QN_ADDPROGRAM\d+\s*\([A-Z]{2}\)\s*"
    
    # ประมวลผลแต่ละแถวใน DataFrame
    for index, row in df.iterrows():
        # สมมุติว่าในแต่ละแถวข้อมูลอยู่ในคอลัมน์ 'What courses at Mahidol University should be promoted to help contribute to your career? (You can choose more than 1 item)'
        raw_data = str(row['What courses at Mahidol University should be promoted to help contribute to your career? (You can choose more than 1 item)'])
        # แยกรายการตามเครื่องหมายจุลภาค
        items = [item.strip() for item in raw_data.split(",")]
        others = []
        
        for item in items:
            # ตัด prefix "QN_ADDPROGRAMx (??)" ออก ด้วย regex
            text = re.sub(prefix_pattern, "", item)
            # ตรวจสอบว่า text ที่ได้อยู่ใน mapping หรือไม่
            if text in mapping:
                col = mapping[text]
                df.at[index, col] = 1
            else:
                # หากไม่อยู่ใน mapping ถือว่าเป็นรายการ "อื่นๆ"
                others.append(text)
        
        # ถ้ามีรายการที่ไม่ตรงกับ mapping
        if others:
            df.at[index, 'QN_ADDPROGRAM7'] = 1
            df.at[index, 'QN_ADDPROGRAM7_TXT'] = ", ".join(others)
    
    return df

