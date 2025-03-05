import pandas as pd
import re


""" จับคู่เลขบัตรประชาชน หรือ passport กับรหัสนักศึกษา
    ส่งกลับค่า => เลขบัตรประชาชน หรือ passport กับรหัสนักศึกษา
"""
def get_citizen_id_series(df_data, df_sql):
    """
    คืนค่า Series ของรหัสบัตรประชาชน (หรือพาสปอร์ต) สำหรับแต่ละ 'Student ID-Final' ใน df_data
    โดยเทียบกับ 'Code' ใน df_sql เพื่อดึง 'CitizenNumber' หรือ 'Passport' ตามเงื่อนไข:
      - หาก 'CitizenNumber' เป็นค่าว่าง ('') หรือ NaN ให้ใช้ค่า 'Passport' แทน
      - หากมี 'CitizenNumber' ให้ใช้ค่านั้นทันที
    """
    # 1) แปลงชนิดข้อมูลของคอลัมน์ 'Student ID-Final' เป็นสตริง (เผื่อกรณีเป็นตัวเลข จะได้ Map ได้ตรง)
    student_ids = df_data['Student ID-Final'].astype(str)

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


""" จับคู่สถานะการมีงานทำ (จาก google form มีตัวเลือกให้เลือก) column => Currently Employed Status
    ส่งกลับเป็นค่าตัวเลข 1-7
"""
def get_work_status_series(df_data):
    mapping_work_status = {
        'Unemployed before graduation and employed after graduation' : '1',
        'Employed and currently pursuing a higher degree' : '2',
        'Unemployed' : '3',
        'Currently pursuing a higher degree' : '4',
        'Employed in the same field before and after graduation' : '5',
        'Employed before and change the field work after graduation' : '6',
        'Employed before graduation and promoted after graduation in the same field' : '7'
    }
    
    return df_data['Currently Employed Status'].map(mapping_work_status)


""" จับคู่สถานะทางทหาร (จาก google form มีตัวเลือกให้เลือก) column => Military Status (Male only) -  สถานะการเกณฑ์ทหาร(เฉพาะเพศชาย)
    ส่งกลับเป็นค่าตัวเลข 0-1 หรือ - กรณีเป็นผู้หญิง
"""
def get_military_status_series(df_data, df_sql):
    """
    คืนค่า Series แสดงสถานะทางทหาร (เป็น string) ตามเงื่อนไข:
      - ถ้า 'Student ID-Final' (ใน df_data) ตรงกับ 'Code' (ใน df_sql)
      - และค่า Gender ใน df_sql เป็น 'male'
        => ใช้ mapping_military_status ในการแปลง
      - กรณีอื่นให้คืน '-'
    """
    # 1 กำหนด mapping สำหรับค่าข้อความทางทหาร -> สตริง '0' หรือ '1'
    mapping_military_status = {
        'Taken a draft deferment period or Exempted from military service or Conscripted - อยู่ในช่วงผ่อนผันเกณฑ์ทหาร หรือได้รับการยกเว้น หรือผ่านการเกณฑ์ทหารแล้ว' : '0',
        'Serving in a military - อยู่ในระหว่างการเป็นทหารเกณฑ์' : '1'
    }
    
    # 2 แปลง 'Student ID-Final' ใน df_data ให้เป็น string เพื่อให้ match กับ df_sql['Code']
    df_data['Student ID-Final'] = df_data['Student ID-Final'].astype(str)
    
    # 3 สร้าง dictionary จาก df_sql: key = 'Code', value = 'Gender'
    gender_dict = df_sql.set_index('Code')['Gender'].to_dict()
    
    # 4 ฟังก์ชันภายในสำหรับ apply
    def map_military_status(row):
        # ดึง Student ID-Final และค่าที่บอกสถานะทหาร
        student_id = row['Student ID-Final']
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
    
    # 5 ใช้ .apply(...) เพื่อสร้าง Series ใหม่
    return df_data.apply(map_military_status, axis=1)


""" จับคู่สถานะการเป็นนักบวช (จาก google form มีตัวเลือกให้เลือก) column => Being Ordained as a Priest Status -  สถานะการเป็นนักบวช
    ส่งค่ากลับเป็น 1-5
"""
def get_ordinate_status_series(df_data):
    mapping_ordinate_status ={
        'Not being as a priest - ไม่ได้เป็นนักบวช': '1',
        'Being as a priest and will disrobe in 3 months - อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา น้อยกว่า 3 เดือน': '2',
        'Being as a priest and will disrobe in 4 - 12 months - อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา 4 เดือน - 1 ปี': '3',
        'Being as a priest and will disrobe more than 1 year - อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา มากกว่า 1 ปี': '4',
        'Being as a priest and do not have a plan to disrobe  - อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา ไม่มีกำหนด': '5'
    }
    
    return df_data['Being Ordained as a Priest Status -  สถานะการเป็นนักบวช'].map(mapping_ordinate_status)


""" จับคู่ประเภทงานที่ทำ (จาก google form มีตัวเลือกให้เลือก) column => Type of Job
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่จับคู่ได้กลับมา
    การจับคู่คือ ถ้าตรงกับตัวเลือกที่กำหนดใน google form ให้ส่งค่ากลับมา แต่ถ้าไม่ใช่ให้ส่ง 00 เท่านั้น
"""
def get_occup_type_series(df_data):
    """
        หมวด 01 (ข้าราชการ /เจ้าหน้าที่หน่วยงานของรัฐ) สำหรับงานข้าราชการหรือเจ้าหน้าที่ภาครัฐ
        หมวด 02 (รัฐวิสาหกิจ) สำหรับพนักงานในรัฐวิสาหกิจ เช่น Staff/Employee in a State-Enterprise Agency
        หมวด 03 (พนักงานบริษัท/องค์กรธุรกิจเอกชน) รวมถึงงานในภาคเอกชนที่มักเป็นพนักงาน เช่น Staff/Employee in a private company, Guest Service Agent (Hotel), developer, Digital Marketing, Entertainment, Hotel industry, Life insurance, Flight attendant, Five stars hotel industry, hospitality
        หมวด 04 (ดำเนินธุรกิจอิสระ/เจ้าของกิจการ) รวมถึงงานที่เกี่ยวกับการดำเนินธุรกิจส่วนตัวหรือเป็น Freelance เช่น Your own business/family business, Director of Photography/ Cinematographer, Bussiness, Consulting, Freelance, Start-up Business, Investment academy..., Real Esate business, Barber/Hairstylist
        หมวด 05 (พนักงานองค์การต่างประเทศ/ระหว่างประเทศ) สำหรับงานในองค์การต่างประเทศ
    """
    mapping_occup_type = {
        'Civil Servant/Employee in a government organization' : '01',
        'Staff/Employee in a State-Enterprise Agency' : '02',
        'Staff/Employee in a private company' : '03',
        'Your own business/family business' : '04',
        'Employee in an international organization' : '05',

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
    

""" จับคู่ประเภทงานที่ทำ เพิ่มเติม (จาก google form มีตัวเลือกให้เลือก) column => Type of Job
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_occup_type_series เป็น 00 ต้องส่งค่าที่นักศึกษากรอกกลับมา แต่ถ้านอกเหนือให้เป็นค่าว่างเท่านั้น
"""
# เงื่อนไขคือ ถ้า QN_OCCUP_TYPE หรือ get_occup_type_series ค่าเท่ากับ 00 จะต้องกรอกข้อมูลเพิ่มเติม ถ้าเป็นค่าอื่น ตอบเป็นค่าว่าง เท่านั้น
def get_occup_type_text(df_data):
    # เรียกใช้ฟังก์ชัน get_occup_type_series เพื่อรับ Series ของ Occupation Type
    occup_type_seties = get_occup_type_series(df_data)
    
    def map_data(row):
        occup_type = str(occup_type_seties.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if occup_type == '00':
            # ถ้า occup_type เท่ากับ '00' ตอบกลับเป็นค่า Type of Job
            mapped_value = row['Type of Job']
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)


""" จับคู่ความสามารถพิเศษ (จาก google form มีตัวเลือกให้เลือก) column => Which skill can most help you to get employed?
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่จับคู่ได้กลับมา
    การจับคู่คือ ถ้าตรงกับตัวเลือกที่กำหนดใน google form ให้ส่งค่ากลับมา แต่ถ้าไม่ใช่ให้ส่ง 00 เท่านั้น
"""
def get_talent_series(df_data):
    mapping_talent = {
        'Foreign Languages' : '01',
        'Computer literacy' : '02',
        'Extra curriculum activities' : '03',
        'Art' : '04',
        'Sport' : '05',
        'Traditional dance/Music' : '06',
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


""" จับคู่ความสามารถพิเศษ เพิ่มเติม (จาก google form มีตัวเลือกให้เลือก) column => Which skill can most help you to get employed?
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_talent_series เป็น 00 ต้องส่งค่าที่นักศึกษากรอกกลับมา แต่ถ้านอกเหนือให้เป็นค่าว่างเท่านั้น
"""
def get_talent_text(df_data):
    talent_series = get_talent_series(df_data)
    def map_data(row):
        talent = str(talent_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if talent == '00':
            # ถ้า occup_type เท่ากับ '0' ตอบกลับเป็นค่า Which skill can most help you to get employed?
            mapped_value = row['Which skill can most help you to get employed?'].strip()
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)


# รอ map ข้อมูล position
def get_position_type_series(df_data):
    mapping_position = {
        "QA": "315290",  # ผู้ตรวจสอบด้านความปลอดภัย สุขภาพ และคุณภาพผลิตภัณฑ์อื่น ๆ (กรณี QA ทั่วไป)
        "Tax consultant": "241130",  # ผู้ตรวจสอบภาษี
        "ESL Consultant": "235990",  # ผู้ประกอบวิชาชีพด้านการสอนอื่น ๆ ที่มิได้จัดประเภทไว้ในที่อื่น (กรณีปรึกษาการสอนภาษา)
        "Strategic Planner": "241990",  # ผู้ประกอบวิชาชีพทางธุรกิจ ที่มิได้จัดประเภทไว้ในที่อื่น
        "Case Team Assistant": "343120",  # เลขานุการฝ่ายบริหาร (งานผู้ช่วยในทีมที่เน้นงานสนับสนุน/เอกสาร)
        "Sale representative": "341520",  # ตัวแทนขายผลิตภัณฑ์
        "Foriegn Trade officer": "413120",  # ผู้นำเข้าหรือส่งออกสินค้า
        "Real Estate Agent, Teacher": "341320",  # นายหน้าซื้อขายอสังหาริมทรัพย์ (กรณีต้องเลือกหนึ่งเดียว)
        "Expatriate Officer": "343990",  # ผู้ปฏิบัติงานด้านบริการงานทั่วไป ซึ่งมิได้จัดประเภทไว้ในที่อื่น
        "Content Creator": "245190",  # นักประพันธ์ นักหนังสือพิมพ์ และนักเขียนอื่น ๆ
        "Marketing Assistant": "241960",  # นักการตลาด ; เจ้าหน้าที่การตลาด ; เจ้าหน้าที่ส่งเสริมการขาย
        "Marketing Manager and Editorial Assistant": "123330",  # ผู้จัดการฝ่ายการตลาด (กรณีให้โฟกัสตำแหน่งหลักเป็นงานบริหาร)
        "Admin & HR Assistant": "419020",  # เจ้าหน้าที่ฝ่ายบุคคล (รวมงานธุรการ/บุคคล)
        "Package Operations Specialist, Seller Packages": "413190",  # เจ้าหน้าที่คลังสินค้า/งานแพ็กอื่น ๆ
        "Content Producer (Corporate Partnership - Beauty)": "245190", 
        "Movie Acquisition": "241990",  # จัดอยู่ในกลุ่มงานธุรกิจ-การเจรจาซื้อขายลิขสิทธิ์
        "International Coordinator": "343990",
        "Sales and Marketing for  family business, Project director, and assistance of curators for Thailand Biennale Phuket": "241960",
        "Operation coordinators": "343990",
        "Media Planner": "241920",  # นักโฆษณา ; ผู้สร้างสรรค์งานโฆษณา (วางแผนสื่อ)
        "Investment Analyst": "241990",
        "Manager": "123130",  # ผู้จัดการฝ่ายบริหารทั่วไป (จับเป็นผู้จัดการในภาพรวม)
        "QA Engineer": "214925",  # วิศวกรคุณภาพ ; วิศวกรควบคุมคุณภาพ
        "Associate Equity Analyst": "241990",
        "-": "X11030",  # ผู้ไม่แจ้งชื่ออาชีพ
        "General Administration Officer": "419010",  # เสมียนพนักงานทั่วไป, พนักงานธุรการ
        "Marketing": "241960",
        "Marketing staff": "241960",
        "Import Export Coordinator": "413120",
        "Admin": "419010",
        "Associate Consultant": "241990",
        "CEO and COO": "121030",  # ผู้บริหารระดับสูงของหน่วยงานเอกชน
        "General manager": "123130",
        "Junior Office Assistant": "419010",
        "Client Service Assistant - Private Wealth Management": "419010",
        "Junior Internal Audit Officer": "241140",  # ผู้ตรวจสอบภายใน
        "Social media and content creator": "245190",
        "Director Assistant": "343120",
        "Linguist (Previously Marketing Project Manager)": "244430",  # นักภาษาศาสตร์
        "Business Owner (Family Business)": "121030",
        "Junior Backend Developer": "213210",  # โปรแกรมเมอร์
        "Executive Assistant- Operations and Marketing": "343120",
        "Regional Sales Executive": "341520",
        "Stylist and designer": "347150",  # นักออกแบบเสื้อผ้า, ผลิตภัณฑ์สิ่งทอสิ่งถัก
        "AE": "241960",  # (มักหมายถึง Account Executive ในงานการตลาด/โฆษณา)
        "Ae": "241960",  # (มักหมายถึง Account Executive ในงานการตลาด/โฆษณา)
        "General Document Controlle": "419010",  # (งานเอกสาร)
        "Project Manager": "123990",  # ผู้จัดการฝ่ายอื่น ๆ (งานบริหารโครงการ)
        "Content Moderator": "245190",
        "Finance ERP Consultant": "241990",
        "Finance and Accounting Analysts": "241110",  # นักบัญชีทั่วไป
        "Associate Software Engineer": "213160",  # วิศวกรซอฟต์แวร์
        "Marketing Executives": "241960",
        "Content Strategist": "241990", 
        "Assistant": "419010",  # เลขานุการ/ผู้ช่วยงานทั่วไป
        "Senior Translator": "244440",  # นักแปล
        "Cabin crew": "511120",  # พนักงานต้อนรับบนเครื่องบิน
        "Cabin Crew": "511120",  # พนักงานต้อนรับบนเครื่องบิน
        "BD&KOL specialist": "241960", 
        "Market Research Analyst": "241950",  # นักวิจัยตลาด
        "Application Developer": "213210",
        "Marketing planning and strategy": "241960",
        "Software Engineer": "213160",
        "software engineer": "213160",
        "F2F Fundraiser": "241990",
        "Marketing Trainee": "241960",
        "Production assistant": "343990",
        "Marketing & Partnerships": "241960",
        "Consultant": "241990",
        "Property Consultant": "341320",
        "Customer Care Coordinator": "422290",  # พนักงานต้อนรับ และพนักงานบริการข้อมูลข่าวสารอื่น ๆ
        "Consulting Associate": "241990",
        "Assistant Project Manager": "343990",
        "Sales coordinator": "341520",
        "Executive Analyst, Customer Success": "241990",
        "Junior Sampling Technician": "311990",  # ช่างเทคนิควิทยาศาสตร์กายภาพและวิศวกรรมศาสตร์ที่มิได้จัดประเภท
        "Digital Marketing Assistant": "241960",
        "UX": "347190",  # นักออกแบบซึ่งมิได้จัดประเภทไว้ในที่อื่น (ออกแบบ UX)
        "Cybersecurity Operations Analyst": "213150",  # ผู้เชี่ยวชาญด้านความปลอดภัยของไอที
        "Spa receptionist": "422210",  # พนักงานต้อนรับทั่วไป
        "Biomedical Researcher": "221190",  # นักชีววิทยาและนักวิทยาศาสตร์ที่เกี่ยวข้องอื่น ๆ
        "Associate - Workforce Transformation": "241990",
        "Creative content": "245190",
        "Sale and Marketing": "241960",
        "Media master": "241920",
        "Communication and Marketing": "241960",
        "Assistant General Manager": "123130",
        "Boardgame designer/Video Editor": "347190",
        "Executive": "123130",
        "Business Owner": "121030",
        "Human Resource Officer": "419020",
        "Homes Operation Coordinator": "343990",
        "Guest service agent": "422210",
        "Guest Service Agent": "422210",
        "Japanese Assistant": "244420",  # ล่าม
        "Trust and Safety Associate": "343990",
        "Sales representative": "341520",
        "sales and marketing executive": "241960",
        "Commercial Flagship Store Manager for Power Tools - Singapore Market": "123130",
        "Software Engineer": "213160",
        "Marketing Manager": "123330",
        "Accounting team member": "241110",
        "Export manager assistance": "413120",
        "Chef de partie": "512230",  # พ่อครัว ; ผู้ปรุงอาหาร
        "Marketing & Project Coordinator": "241960",
        "Ceo": "121030",
        "CEO": "121030",
        "Aide to municipal level of political party": "114190",  # เจ้าหน้าที่บริหารขององค์กรพรรคการเมืองอื่น ๆ
        "General Manager": "123130",
        "Senior Analyst, Seller Operation Service": "241990",
        "Web Designer": "213220",  # เว็บมาสเตอร์ (นักออกแบบเว็บไซด์)
        "Marketing officer": "241960",
        "Content moderator-Japanese Language": "245190",
        "Product Development & Analysis": "241990",
        "Business Support Project": "241990",
        "Owner and manager": "121030",
        "BOD": "121010",  # ประธานกรรมการ (เทียบได้กับบอร์ด)
        "Product Operation Administrator": "343990",
        "Finance and accounting officer": "241110",
        "Executive recruitment consultant": "241990",
        "freelance": "X11020",  # ผู้แจ้งชื่ออาชีพไม่ชัดเจน
        "R&D Director": "123720",  # ผู้จัดการฝ่ายวิจัยและพัฒนา
        "Ballet Teacher": "235990",  # ผู้ประกอบวิชาชีพด้านการสอนอื่น ๆ
        "Assistant of CEO": "343120",
        "Business Executive": "123130",
        "Category management initiatives": "241990",
        "PA": "343120",  # Personal Assistant
        "Advisory Associate": "241990",
        "Travel Coordinator": "422190",  # พนักงานท่องเที่ยวและผู้ปฏิบัติงานที่เกี่ยวข้อง
        "Managing Director": "121030",
        "Research Assistant Internship": "343990",
        "Management trainee": "343990",
        "Strategic Project Management Specialist": "241990",
        "Data Engineer": "213160",
        "Sales Finance": "241990",
        "Export Document Officer": "413120",
        "Lifestyle Concierge": "422290",
        "Graphic Design Foreman": "347130",
        "Executive Creative Designer": "347130",
        "Teacher": "232010",  # ครู อาจารย์ระดับมัธยมศึกษาทั่วไป (กรณีไม่ระบุระดับแน่ชัด มักใช้กลุ่ม 23xx)
        "Coordinator, Catering & Events": "343990",
        "Management Analyst": "241990",
        "key account": "241960",
        "Technology Graduate": "X11020",
        "Academic Information System Administrator": "213990",  # ผู้ประกอบวิชาชีพด้านคอมพิวเตอร์ฯ อื่น ๆ
        "Senior Marketing": "241960",
        "Editor": "245120",  # บรรณาธิการหนังสือพิมพ์ (หรือบรรณาธิการทั่วไป)
        "ASEAN Supply and Logistics, Logistics Representative": "413390",  # ผู้ขนส่งสินค้าอื่น ๆ (งานโลจิสติกส์)
        "ผู้ช่วยผู้รับใบอนุญาต": "343120",
        "Business Analyst": "241990",
        "Business analyst": "241990",
        "Data analyst": "241990",
        "HR Coordinator": "419020",
        "Teacher assistant": "333020",  # ครูผู้ช่วย (การศึกษาพิเศษ) *กรณีไม่มีโค้ดอื่นครอบคลุม
        "Product designer": "347120",  # นักออกแบบผลิตภัณฑ์อุตสาหกรรมและพาณิชยกรรม
        "Operation Assistance": "343990",
        "Artistic Director/Creative Production Assistant": "245550",  # ผู้กำกับศิลปกรรม (ใกล้เคียงงานสร้างสรรค์)
        "IT (QA Engineer)": "214925",
        "Digital Marketing": "241960",
        "sales manager": "123320",  # ผู้จัดการฝ่ายขาย
        "Agent": "341520",
        "Event Co-ordinator": "343990",
        "Academic Administration": "343990",
        "Academic administration": "343990",
        "receptionist": "422210",
        "Human Resources": "419020",
        "Marketing (Import - export)": "241960",
        "Employee": "X11020",
        "Loyalty & Online CRM Department Manager": "123330",  # ผู้จัดการฝ่ายการตลาด
        "Mathematics Tutor": "232010",
        "PSA": "X11020",
        "English Teacher & Content Creator": "232010",
        "Purchasing Manager": "123520",  # ผู้จัดการฝ่ายจัดซื้อและวัสดุ
        "Quality assurance engineer": "214925",
        "Educator": "232010",
        "Assistant Sales and Marketing Manager": "123320",
        "International E-commerce Executive": "241960",
        "Global Ecommerce - Serach Ops": "241990",
        "Digital Marketing manager": "123330",
        "Corporate Affair Officer": "241930",  # เจ้าหน้าที่ประชาสัมพันธ์
        "Reservation Sales Agent": "422290",
        "Beauty Advisor": "522020",  # พนักงานขายของหน้าร้าน / พนักงานขายสินค้า
        "Kols and Influencer Specialist": "241960",
        "UX UI Designer": "347190",
        "Artist": "245290",  # ช่างผู้ทำงานศิลปะอื่น ๆ
        "Procurement": "341610",  # ผู้จัดซื้อทั่วไป
        "Brand Assistant": "241960",
        "Content Moderator": "245190",
        "Content moderator": "245190",
        "Financial advisory analyst": "241990",
        "RM supporter": "241990",
        "Assistant to Tourism, Culture and Press Section": "343990",
        "Stylish assistant": "347150",
        "Event  Coordinator": "343990",
        "Research Assistant": "343990",
        "Career Advisor / HR Consultant": "241990",
        "Assistant": "419010",
        "Marketing Executive": "241960",
        "Marketing executive": "241960",
        "Founder": "121030",
        "Product Operations Analyst": "241990",
        "Brand & Growth Associate": "241960",
        "Tutoring teacher": "232010",
        "Research and Development": "241990",
        "UXUI Designer": "347190",
        "Management Trainee": "343990",
        "Inventory Controller": "413140",  # เจ้าหน้าที่คลังพัสดุ
        "Margin Management Analyst": "241990",
        "Content creator": "245190",
        "Sales executive": "241960",
        "Software Developer": "213210",
        "Programme Officer (Writer)": "245190",
        "Property Consultant": "341320",
        "Property consultant": "341320",
        "Corporate Finance and Treasury": "241110",
        "Senior Client Relations Manager": "123130",
        "Data Scientist": "213990",
        "Nutrition Advisor": "322320",  # ที่ปรึกษาด้านการควบคุมอาหาร/นักโภชนาการ
        "E-commerce Executive": "241960",
        "Owner": "121030",
        "Website manager and graphic assistant": "213220",
        "Procurement contracts administrator": "341610",
        "Business Investment Associate": "241990",
        "Revenue management": "241990",
        "Revenue Management": "241990",
        "Client Solutions Analyst (Private Equity)": "241990",
        "Product management": "241990",
        "Graphic design": "347130",
        "Learning Coordinator": "343990",
        "Data scientists": "213990",
        "MD": "121030",
        "Community Associate": "343990",
        "Visual Merchandiser": "347190",
        "AAd Operation & Performance Marketing Analyst": "241990",
        "Export CX": "413120",
        "Investor Relations": "241990",
        "Digital Marketing": "241960",
        "Manager": "123130",
        "Business Development Executive": "241990",
        "Dog Fitness Trainee": "X11020",
        "Ceo Assistant": "343120",
        "Developer": "213210",
        "Tutor": "232010",
        "Direct sales operation": "241960",
        "Ux designer": "347190",
        "Volumetric Accountant": "241110",
        "QC staff": "315290",
        "Software Engineer ": "213160",
        "software engineer ": "213160",
        "CEO & Founder": "121030",
        "MTPE": "244440",  # (Machine Translation Post-Editor) จัดเป็นนักแปล
        "Consultant executive": "241990",
        "Program officer": "343990",
        "Marketing/ Project Manager": "123330",
        "Management Associate": "343990",
        "Directing Manager": "123130",
        "Finance administrator": "241110",
        "Administration/ Staff/ Event Coordinator": "343990",
        "Production Trainee": "X11020",
        "Analyst": "241990",
        "Model,": "521020",  # นายแบบ นางแบบ
        "Tourist guide": "511310",  # มัคคุเทศก์
        "Learning & Development Coordinator": "343990",
        "Assistant Purchasing Manager": "123520",
        "Financial Markets officer": "241990",
        "Assistant to family": "419010",
        "Personal Assistant": "343120",
        "Sale coordinator": "341520",
        "Management Trainee - Sales & Operation": "343990",
        "Event Officer": "343990",
        "Hotel Reception": "422220",  # พนักงานต้อนรับ (โรงแรม)
        "Head of marketing": "123330",
        "Sales Coordinator": "341520",
        "Managing Partner": "121030",
        "Production staff": "932190",  # แรงงานด้านการประกอบอื่น ๆ
        "Risk Manager": "123130",
        "Creative Production": "245190",
        "Freelance English tutor": "232010",
        "Thai Language Review": "245190",
        "Product development executive": "241990",
        "Sales executives": "241960",
        "HR": "419020",
        "PMO": "343990",
        "Project Management": "343990",
        "Content creator, freelance graphic designer": "245190",
        "Assistant Fund Manager": "241990",
        "quality assurance": "315290",
        "Project Manager": "123990",
        "Associate": "241990",
        "Live streamer": "245190",
        "Reservation Agent": "422290",
        "Mt": "343990",  # (ถ้าหมายถึง Management Trainee)
        "System engineer": "214930",  # วิศวกรคอมพิวเตอร์
        "Software Tester": "213990", 
        "Sales Associates": "341520",
        "Accountant": "241110",
        "Livestream Operator": "245190",
        "R&D": "241990",
        "Tech consult": "241990",
        "Investment Banking Advisor": "241990",
        "Client Service Assistant": "419010",
        "Relationship officer": "241990",
        "Business analyse": "241990",
        "Assistance Sound engineer": "313190",
        "CFO": "121030",
        "Business operation coordinator": "343990",
        "Co-poducer": "343990",
        "Liquidity Associate": "241990",
        "Owner & CEO": "121030",
        "Assiantant Manager": "123130",
        "Programmer": "213210",
        "Club Lounge Agent": "422210",
        "Account Executive": "241960",
        "Marketing Executive": "241960",
        "Tax consultant": "241130",
        "UMC (management candidate)": "X11020",
        "Freelance": "X11020",
        "Relationship Management": "241990",
        "Partnership": "241990",
        "Investment consultant": "241990",
        "Sales assistant": "341520",
        "Designer": "347190",
        "Vm": "347190",
        "Seller": "522020",  # พนักงานขายของหน้าร้าน
        "Business owners": "121030",
        "Business owner": "121030",
        ".": "X11020",
        "Editorial coordinator": "343990",
        "Business development": "241990",
        "Human Resources Officer": "419020",
        "Performance Marketing": "241960",
        "Co": "X11020",
        "Marketing Specialist": "241960",
        "Administration Staff": "419010",
        "AMD": "X11020",
        "Greeter": "422210",
        "Import": "413120",
        "Executive Assistant": "343120",
        "Purchaser": "341610",
        "Protocol Officer": "343990",
        "No": "X11030",
        "BD": "241990",
        "Writer": "245110",  # นักประพันธ์
        "Demand planningAssociate": "241990",
        "Assistant of member of parliament": "343990",  # ไม่มีโค้ดเฉพาะผู้ช่วย ส.ส.
        "Account executive": "241960",
        "Brand Associate": "241960",
        "Partner executive": "241990",
        "Data & Informative Marketing": "241960",
        "Product Op": "241990",
        "Managing director": "121030",
        "Associate consultant HR executive search": "241990",
        "Product Operation Analyst": "241990",
        "Project Officer": "343990",
        "Sales": "341520",
        "Product Marketing Officer": "241960",
        "Biddable executive": "241960",
        "English Teacher": "232010",
        "Family Business": "121030",
        "Sales Executive": "241960",
        "Influencer Strategic Planner": "241990",
        "Caseworker": "X11020",
        "law enforcement officer": "516220",  # เจ้าหน้าที่ตำรวจ (เทียบงานบังคับใช้กฎหมาย)
        "Sales and Marketing Assosiate": "241960",
        "Humanitarian Officer/Security Officer": "516990",  # ผู้ให้บริการด้านการป้องกันภัยอื่น ๆ 
        "COO": "121030",
        "Junior Marketing Consultant": "241990",
        "Assistance Manager": "123130",
        "Business administration": "241990",
        "Wms Associate": "413140",  # เจ้าหน้าที่คลังพัสดุ (Warehouse Management System)
        "Interpreters": "244420",  # ล่าม
        "HR Specialist (Management Trainee)": "419020",
        "General": "X11020",
        "Care Supervisor": "516990",
        "Receptionist": "422210",
        "Project occordinator": "343990",
        "MMOS staff": "X11020",
        "Marketing Analysts": "241960",
        "Account manager": "123130",
        "Sale officer assistant": "341520",
        "International Manager": "123130",
        "Marketing associate": "241960",
        "Real Estate": "341320",
        "Senior Leadership Team Supporter and Communication Officer / Translator": "244440",
        "Communication Assistant (Part-time)": "343990",
        "Onboarding Experience Coordinator": "343990",
        "Merchandiser": "343990",
        "Business Analyst": "241990",
        "Marketing Planning and strategy analyst": "241960",
        "Managing assistant": "343120",
        "Production manager and Artist relation": "123990",
        "Digital campaign specialist": "241960",
        "News Reporters and Translators": "245126",  # ผู้สื่อข่าวหนังสือพิมพ์ (สำหรับ Reporter), (งานแปลใกล้เคียง)
        "Channel manager": "123990",
        "Coordinator Marcom": "343990",
        "Manager Assitance": "343120",
        "เจ้าหน้าที่แผนกการตลาด": "241960",
        "Affiliate Influencer Management": "241990",
        "Assistant Manager": "123130",
        "Tour Guide": "511310",
        "personal concierge": "422290",
        "Graphic designer": "000128",
        "Graphic Designer": "000128",
        "graphic designer": "000128",
    }

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
                mapped_value = mapping_position.get(str(row['Position']).strip())

        return mapped_value

    return df_data.apply(map_data, axis=1)
    

""" ระบุชื่อบริษัทที่ทำงาน (google form ให้กรอกข้อมูลเอง) column => Organization name
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่นักศึกษากรอกข้อมูลกลับมา
"""
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
            mapped_value = row['Organization name'].strip()

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" จับคู่ประเภทกิจการ (จาก google form มีตัวเลือกให้เลือก) column => Industry
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่จับคู่ได้กลับมา
    การจับคู่คือ ถ้าตรงกับตัวเลือกที่กำหนดใน google form ให้ส่งค่ากลับมา โดยไม่มีค่าเริ่มต้น หรือค่าอื่นๆ เพื่อกรอกข้อมูลเพิ่มเติม
"""
def get_work_type_series(df_data):
    mapping_work_type = {
        'Agriculture / Forestry / Fisheries': 'A',
        'Mining': 'B',
        'Production': 'C',
        'Power & Energy / Oil & Gas / Heating, Ventilation & Air Conditioning': 'D',
        'Water Supply / Wastewater Treatment / Waste Management / Related Activities': 'E',
        'Construction': 'F',
        'Motor Vehicles Retail and Whole Sale / Auto Repair': 'G',
        'Logistics and Warehouse': 'H',
        'Hospitality / Catering': 'I',
        'Information and Communication': 'J',
        'Financial Services/Insurance': 'K',
        'Real Estate': 'L',
        'Professional / Science / Academic': 'M',
        'Management Consultancy & Business Support Service': 'N',
        'Civil Services (Government, Armed Forces) / Social Security': 'O',
        'Education': 'P',
        'Healthcare / Charity / Non-Profit Organization': 'Q',
        'Art / Entertainment / Recreation': 'R',
        'General Business Services': 'S',
        'Small Family Owned Business': 'T',
        'International Organization / International Association': 'U'
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
            mapped_value = mapping_work_type.get(row['Industry'].strip())

        return mapped_value

    return df_data.apply(map_data, axis=1)


# รอ map ข้อมูลที่อยู่ของที่ทำงาน
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


""" ระบุชื่อ ซอย ของที่อยู่ที่ทำงาน (google form ให้กรอกข้อมูลเอง) column => Soi/Alley of your workplace
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่นักศึกษากรอกข้อมูลกลับมา
"""
def get_work_address_soi_text(df_data):
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
            # mapped_value = row['Soi/Alley of your workplace']
            mapped_value = row['QN_WORK_SOI']

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" ระบุชื่อ ถนน ของที่อยู่ที่ทำงาน (google form ให้กรอกข้อมูลเอง) column => Road of your workplace
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่นักศึกษากรอกข้อมูลกลับมา
"""
def get_work_address_street_text(df_data):
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
            # mapped_value = row['Road of your workplace']
            mapped_value = row['QN_WORK_STREET']

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" ระบุชื่อ ตำบล หรือ แขวง ของที่อยู่ที่ทำงาน (google form ให้กรอกข้อมูลเอง) column => Sub-district of your workplace
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่นักศึกษากรอกข้อมูลกลับมา
"""
def get_work_address_tambon_text(df_data):
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
            # mapped_value = row['Sub-district of your workplace']
            mapped_value = row['QN_WORK_TAMBON']

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" ระบุชื่อ อำเภอ หรือ เขต ของที่อยู่ที่ทำงาน (google form ให้กรอกข้อมูลเอง) column => Sub-district of your workplace
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่นักศึกษากรอกข้อมูลกลับมา
"""
def get_work_address_district(df_data):
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
            mapped_value = row['Sub-district of your workplace']

        return mapped_value

    return df_data.apply(map_data, axis=1)



""" ระบุชื่อ อำเภอ หรือ เขต ของที่อยู่ที่ทำงาน (google form ให้กรอกข้อมูลเอง) column => District of your workplace
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่นักศึกษากรอกข้อมูลกลับมา
"""
def get_work_address_district(df_data):
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
            mapped_value = row['District of your workplace']

        return mapped_value

    return df_data.apply(map_data, axis=1)
    

""" ระบุชื่อ จัวหวัด ของที่อยู่ที่ทำงาน (google form ให้กรอกข้อมูลเอง) column => Province of your workplace
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่นักศึกษากรอกข้อมูลกลับมา
"""
def get_work_address_province(df_data):
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
            mapped_value = row['Province of your workplace']

        return mapped_value

    return df_data.apply(map_data, axis=1)

def get_work_address_country_series(df_data):
    address_country = {
        "thailand": "TH",
        "Thailand": "TH",
        "ไทย": "TH",
        "Bangkok": "TH",
        "japan": "JP",
        "south korea": "KR",
        "myanmar": "MM",
        "qatar": "QA",
        "Qatar": "QA",
        "-": "no data",
        "no data": "no data"
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
            # mapped_value = address_country.get(row['Country of your workplace'].strip())
            mapped_value = row['QN_WORK_COUNTRY_ID']

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_work_address_zipcode_text(df_data):
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
            # mapped_value = row['Zip code of your workplace']
            mapped_value = row['QN_WORK_ZIPCODE']

        return mapped_value

    return df_data.apply(map_data, axis=1)


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
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่นักศึกษากรอกข้อมูล
            mapped_value = row['Tel of your workplace']

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_work_fax_text(df_data):
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
            mapped_value = row['Fax of your workplace']

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" ระบุชื่อ email ที่ทำงาน (google form ให้กรอกข้อมูลเอง) column => Email of your workplace
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่นักศึกษากรอกข้อมูลกลับมา
"""
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
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่นักศึกษากรอกข้อมูล
            mapped_value = row['Email of your workplace']
            # if pd.isna(row['Email of your workplace']) or row['Email of your workplace'] == '-':
            #     mapped_value = 'no data'

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" ระบุชื่อเงื่อนเดือนที่ได้รับ (google form ให้กรอกข้อมูลเอง) column => Monthly salary or earned income
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่นักศึกษากรอกข้อมูลกลับมา
"""
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
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่นักศึกษากรอกข้อมูล
            mapped_value = int(row['Monthly salary or earned income'])

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" จับคู่ความพอใจต่องานที่ทำ (จาก google form มีตัวเลือกให้เลือก) column => Are you satisfied with your work?
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่จับคู่ได้กลับมา
    การจับคู่คือ ถ้าตรงกับตัวเลือกที่กำหนดใน google form ให้ส่งค่ากลับมา แต่ถ้าไม่ใช่ให้ส่ง 00 เท่านั้น
"""
def get_satisfy_type_series(df_data):
    mapping_work_satisfy = {
        'Yes': '01',
        'No (Undesirable working system)': '02',
        'No (Undesirable co-worker)': '03',
        'No (Not match with your qualification/ability)': '04',
        'No (Little payment)': '05',
        'No (No stability)': '06',
        'No (No opportunity for promotion)': '07'
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
            mapped_value = mapping_work_satisfy.get(row['Are you satisfied with your work?'].strip(), '00')

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" จับคู่ความพอใจต่องานที่ทำ เพิ่มเติม (จาก google form มีตัวเลือกให้เลือก) column => Are you satisfied with your work?
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_satisfy_type_series เป็น 00 ต้องส่งค่าที่นักศึกษากรอกกลับมา แต่ถ้านอกเหนือให้เป็นค่าว่างเท่านั้น
"""
def get_satisfy_text(df_data):
    satisfy_type_series = get_satisfy_type_series(df_data)
    def map_data(row):
        satisfy_type = str(satisfy_type_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if satisfy_type == '00':
            # ถ้า occup_type เท่ากับ '00' Are you satisfied with your work?
            mapped_value = row['Are you satisfied with your work?']
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)


""" จับคู่ระยะเวลาในการหางานทำ (จาก google form มีตัวเลือกให้เลือก) column => After you graduated, how long did it take you to get a job?
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่จับคู่ได้กลับมา
    การจับคู่คือ ถ้าตรงกับตัวเลือกที่กำหนดใน google form ให้ส่งค่ากลับมา โดยไม่มีค่าเริ่มต้น หรือค่าอื่นๆ เพื่อกรอกข้อมูลเพิ่มเติม
"""
def get_time_find_work_series(df_data):
    mapping_time_findwork = {
        'getting a job immediately': '01',
        '1 - 2 months': '02',
        '3 - 6 months': '03',
        '7 - 9 months': '04',
        '10 - 12 months': '05',
        'Over 1 year': '06',
        'An old job (have been working there even before or during the university study)': '07'
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
            mapped_value = mapping_time_findwork.get(row['After you graduated, how long did it take you to get a job?'].strip())

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" จับคู่งานที่ทำตรงกับที่สำเร็จการศึกษา (จาก google form มีตัวเลือกให้เลือก) column => Have you worked in the field that you graduated?
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่จับคู่ได้กลับมา
    การจับคู่คือ ถ้าตรงกับตัวเลือกที่กำหนดใน google form ให้ส่งค่ากลับมา โดยไม่มีค่าเริ่มต้น หรือค่าอื่นๆ เพื่อกรอกข้อมูลเพิ่มเติม
"""
def get_match_education_series(df_data):
    mapping_time_findwork = {
        'Yes': '1',
        'No': '2'
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
            mapped_value = mapping_time_findwork.get(row['Have you worked in the field that you graduated?'].strip())

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" จับคู่การนำความรู้ที่เรียนมาประยุกต์ใช้กับการทำงาน (จาก google form มีตัวเลือกให้เลือก) column => How can you apply your knowledge to your work?
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่จับคู่ได้กลับมา
    การจับคู่คือ ถ้าตรงกับตัวเลือกที่กำหนดใน google form ให้ส่งค่ากลับมา โดยไม่มีค่าเริ่มต้น หรือค่าอื่นๆ เพื่อกรอกข้อมูลเพิ่มเติม
"""
def get_apply_education_series(df_data):
    mapping_apply_edu = {
        'To a very great extent': '01',
        'To a great extent': '02',
        'To a moderate extent': '03',
        'A little': '04',
        'Very little': '05'
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
            mapped_value = mapping_apply_edu.get(row['How can you apply your knowledge to your work?'].strip())

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" จับคู่เหตุผลที่ยังไม่ทำงาน (จาก google form มีตัวเลือกให้เลือก) column => If you are unemployed, please specify the most significant reasons:
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่จับคู่ได้กลับมา
    การจับคู่คือ ถ้าตรงกับตัวเลือกที่กำหนดใน google form ให้ส่งค่ากลับมา แต่ถ้าไม่ใช่ให้ส่ง 0 เท่านั้น
"""
def get_cause_nowork_series(df_data):
    mapping_cause_nowork = {
        'Don’t want to work now': '1',
        'Waiting for the application’s result': '2',
        'Could not find a job': '3',
        'Willing to be a freelancer': '4'
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_cause_nowork.get(row['If you are unemployed, please specify the most significant reasons:'].strip(),'0')
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" จับคู่เหตุผลที่ยังไม่ทำงาน เพิ่มเติม (จาก google form มีตัวเลือกให้เลือก) column => If you are unemployed, please specify the most significant reasons:
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_cause_nowork_series เป็น 0 ต้องส่งค่าที่นักศึกษากรอกกลับมา แต่ถ้านอกเหนือให้เป็นค่าว่างเท่านั้น
"""
def get_cause_nowork_text(df_data):
    cause_nowork_series = get_cause_nowork_series(df_data)
    def map_data(row):
        cause_nowork = str(cause_nowork_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if cause_nowork == '0':
            # ถ้า occup_type เท่ากับ '0' If you are unemployed, please specify the most significant reasons:
            mapped_value = row['If you are unemployed, please specify the most significant reasons:'].strip()
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)


""" จับคู่ปัญหาในการหางานทำ (จาก google form มีตัวเลือกให้เลือก) column => Do you have any problem in getting a job?
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_work_status_series เป็น 3 หรือ 4 ต้องส่งค่ากลับเป็นว่าง แต่ถ้าไม่ใช่ ให้ส่งค่าที่จับคู่ได้กลับมา
    การจับคู่คือ ถ้าตรงกับตัวเลือกที่กำหนดใน google form ให้ส่งค่ากลับมา แต่ถ้าไม่ใช่ให้ส่ง 0 เท่านั้น
"""
def get_problem_find_work_series(df_data):
    mapping_prob_findwork = {
        'No': '01',
        'Yes (Lack information on job availability)': '02',
        'Yes (Could not find a desired job)': '03',
        'Yes(Don’t want to take an examination)': '04',
        'Yes (Lack personal support)': '05',
        'Yes (Lack personal or financial guarantors)': '06',
        'Yes (Rejected by an organization)': '07',
        'Yes (Little salary)': '08',
        'Yes (Could not pass an examination)': '09',
        'Yes (Health issues)': '10',
        'Yes (Lack of foreign language skill)': '11',
        'Yes (Lack of computer skill)': '12',
        'Yes (Lack of experience)': '13',
        'Yes (GPA does not meet the requirement)': '14'
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_prob_findwork.get(row['Do you have any problem in getting a job?'].strip(),'00')
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)


""" จับคู่ปัญหาในการหางานทำ เพิ่มเติม (จาก google form มีตัวเลือกให้เลือก) column => Do you have any problem in getting a job?
    เงื่อนไขคือ ถ้าสถานะการทำงาน get_problem_find_work_series เป็น 00 ต้องส่งค่าที่นักศึกษากรอกกลับมา แต่ถ้านอกเหนือให้เป็นค่าว่างเท่านั้น
"""
def get_problem_find_work_text(df_data):
    problem_find_work_series = get_problem_find_work_series(df_data)
    def map_data(row):
        problem_find_work = str(problem_find_work_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if problem_find_work == '00':
            # ถ้า occup_type เท่ากับ '00' Do you have any problem in getting a job?
            mapped_value = row['Do you have any problem in getting a job?'].strip()
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)
    

def get_workneed_series(df_data):
    mapping_workneed = {
        "Thailand": "01",
        "Any country but want to live in a developed city": "02",
        "Japan": "02",
        "Australia, New Zealand, Japan": "02",
        "Canada, Netherland, and England": "02",
        "Australia": "02",
        "Singapore": "02",
        "Depends": "no data",
        "Any countries": "02",
        "Either Thailand or Overseas in countries such as Singapore or Hong Kong": "01",
        "China": "02",
        "Maybe USA but atleast some country where I can get by with speaking English only": "02",
        "USA": "02",
        "New working environment": "no data",
        "England": "02",
        "Both Thailand and overseas": "01",
        ".": "no data",
        "Germany, Japan": "02",
        "Both": "01",
        "Oversea (USA)": "02",
        "New Zealand": "02",
        "Uk": "02",
        "No preference": "no data",
        "Canada": "02"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_workneed.get(row['Do you prefer to work in Thailand or oversea?  If you prefer to work oversea, please specify the country.'].strip())
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_work_country_series(df_data):
    mapping_workneed = {
        "Thailand": "TH",
        "Any country but want to live in a developed city": "no data",
        "Japan": "JP",
        "Australia, New Zealand, Japan": "AU",  # เลือกประเทศแรกคือ Australia
        "Canada, Netherland, and England": "CA",  # เลือกประเทศแรกคือ Canada
        "Australia": "AU",
        "Singapore": "SG",
        "Depends": "no data",
        "Australia": "AU",
        "Any countries": "no data",
        "Either Thailand or Overseas in countries such as Singapore or Hong Kong": "TH",  # ทั้งสอง => เลือก TH
        "China": "CN",
        "Maybe USA but atleast some country where I can get by with speaking English only": "US",
        "USA": "US",
        "New working environment": "no data",
        "England": "GB",  # England mapped to United Kingdom (GB)
        "Both Thailand and overseas": "TH",  # ทั้งสอง => เลือก TH
        ".": "no data",
        "Germany, Japan": "DE",  # เลือกประเทศแรกคือ Germany
        "Both": "TH",  # ทั้งสอง => เลือก TH
        "Oversea (USA)": "US",
        "New Zealand": "NZ",
        "Uk": "GB",
        "No preference": "no data",
        "Canada": "CA"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status == '3':
            # ถ้า work_status เท่ากับ '3' ตอบกลับเป็นค่าที่ map ข้อมูลได้ 
            mapped_value = mapping_workneed.get(row['Do you prefer to work in Thailand or oversea?  If you prefer to work oversea, please specify the country.'].strip())
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)


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


def get_require_education_series(df_data):
    mapping_required_education = {
        "NOT planning to study": "2",
        "Planning to study": "1",
        "Currently studying": "1"
    }
    
    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน == 2 || 4
    work_status_series = get_work_status_series(df_data)
    
    def map_data(row):
        work_status = str(work_status_series.loc[row.name])
        if work_status in ['2', '4']:
            mapped_value = ''
        else:
            if pd.isna(row['Further Study Plan']) or str(row['Further Study Plan']).strip() == "":
                if pd.isna(row['What level you want to further your study?']) or str(row['What level you want to further your study?']).strip() == "":
                    mapped_value = "no data"
                else:
                    mapped_value = "1"
            else:
                mapped_value = mapping_required_education.get(str(row['Further Study Plan']).strip(), '')
            
        return mapped_value

    return df_data.apply(map_data, axis=1)



def get_level_education_series(df_data):
    mapping_level_education = {
        "Graduate diploma": "50",   # ประกาศนียบัตรบัณฑิต
        "Graduate diploma": "50",
        "Medical degree": "40", # ปริญญาตรี
        "Master's degree": "60", # ปริญญาโท
        "a certificate/specialization (which offers higher rate of salary than a doctor's degree.)": "90", # ประกาศนียบัตรหรือหลักสูตรเฉพาะ (ที่บรรจุในอัตราเงินเดือนสูงกว่าปริญญาเอก)
        "a certificate/specialization (which offers higher rate of salary than a doctor’s degree.)": "90", # ประกาศนียบัตรหรือหลักสูตรเฉพาะ (ที่บรรจุในอัตราเงินเดือนสูงกว่าปริญญาเอก)
        "Bachelor's degree": "40", # ปริญญาตรี
        "Doctoral degree": "80", # ปริญญาเอก
        "a higher graduate diploma": "70", # ประกาศนียบัตรบัณฑิตชั้นสูง
        "Not sure yet": "no data",
        "Both masters and certificates (I've always been a certificate chaser lol)": "60",
        "Not sure": "no data",
        "Language": "30" ,  # ประกาศนียบัตรวิชาชีพชั้นสูง (ในกรณีที่เป็นหลักสูตรหรือประกาศนียบัตรด้านภาษา)
        "MD (doctor of medicine)": "80" # MD ถือเป็นปริญญาเอกในด้านการแพทย์
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
            if pd.isna(row['What level you want to further your study?']) or str(row['What level you want to further your study?']).strip() == "":
                mapped_value = "no data"
            else:
                mapped_value = mapping_level_education.get(str(row['What level you want to further your study?']).strip())
        else:
            if required_education == '1':
                # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
                if pd.isna(row['What level you want to further your study?']) or str(row['What level you want to further your study?']).strip() == "":
                    mapped_value = "no data"
                else:
                    mapped_value = mapping_level_education.get(str(row['What level you want to further your study?']).strip())
            else:
                mapped_value = ''
            # ถ้า work_status ไม่เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            # mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_program_education_series(df_data):
    mapping_program_education = {
        "Same field of study": "1",
        "Different field of study": "2"
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
            mapped_value = mapping_program_education.get(str(row['What field you want to further your study?']).strip())
        else:
            if required_education == '1':
                # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
                mapped_value = mapping_program_education.get(str(row['What field you want to further your study?']).strip())
            else:
                mapped_value = ''
            # ถ้า work_status ไม่เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            # mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_program_education_id_series(df_data):
    mapping_program_education = {
        # --------------------------------------------------------
        # หมวดระบุเจาะจง หรือค้นพบสาขาใกล้เคียงที่สุด
        # --------------------------------------------------------
        "Patisserie": "005106",  # FOOD AND CATERING
        "Medicine": "001565",  # แพทยศาสตร์
        "Management": "000024",  # การจัดการ
        "Governance": "000166",  # การปกครอง
        "MEd": "000302",  # EDUCATION (Master of Education)
        "Cyber management": "000000",  # ไม่พบ "Cyber" โดยตรง
        "MBA/ Business Analytics": "000063",  # BUSINESS DATA ANALYSIS (เลือกใกล้เคียง BA)
        "Biological for doing shrimp farm": "000324",  # การเพาะเลี้ยงสัตว์น้ำ
        "-": "000000",  # ไม่มี / ไม่ระบุ
        "Marketing": "000101",  # การตลาด
        "Languages": "000000",  # ไม่ระบุภาษาใด
        "Masters in Marketing": "000101",  # การตลาด
        "Global marketing": "000101",  # การตลาด
        "Thai language": "000787",  # ภาษาไทย
        "MBA": "000050",  # BUSINESS ADMINISTRATION
        "Masters in Management": "000024",  # การจัดการ
        "Management / Business": "000013",  # BUSINESS (ตามตัวอย่าง business=000013)
        "Global event management": "000232",  # CONVENTION AND EVENT MANAGEMENT
        "Media": "000300",  # การสื่อสารมวลชน
        "Alternative Investments & Risk management": "000000",  
        "International relations": "000223",  # การระหว่างประเทศ
        "Business": "000013",  # BUSINESS
        "Medicine": "001565",  # แพทยศาสตร์
        "Logistics": "000026",  # การจัดการการขนส่งและโลจิสติกส์
        "International Relations": "000223",  # การระหว่างประเทศ
        "Medicine field": "001565",  # แพทยศาสตร์
        "Finance": "000318",  # การเงิน
        "Big data management": "007777",  # DATA SCIENCE AND ARTIFICIAL INTELLIGENCE (ใกล้เคียง)
        "Not sure yet": "000000",
        "Supply chain and logistics": "000026",  # การจัดการการขนส่งและโลจิสติกส์
        "Marketing, Management": "000027",  # การจัดการการตลาด (เลือกกลาง ๆ)
        "Business Administration/ Manager": "000050",  # BUSINESS ADMINISTRATION
        "Marketing": "000101",  # การตลาด
        "something related with UX UI and 3D model": "003359",  # 3D ANIMATION/DIGITAL EFFECTS
        "Chinese language/business": "000730",  # ภาษาจีน
        "Management, Events Management, Marketing": "000232",  # CONVENTION AND EVENT MANAGEMENT (เลือกเน้น events)
        "Public Administration": "000835",  # รัฐประศาสนศาสตร์
        "public administration": "000835",  # รัฐประศาสนศาสตร์
        "Data analysts": "000063",  # BUSINESS DATA ANALYSIS
        "Tourism&hospitality management": "000030",  # การจัดการการท่องเที่ยวและการโรงแรม
        "Computer Science": "000167",  # COMPUTER SCIENCE
        "Business or Psychology": "000000",
        "Business Analytics": "000063",  # BUSINESS DATA ANALYSIS
        "Biological sciences": "000938",  # วิทยาศาสตร์ชีวภาพ
        "Master": "000000",
        "Psychology": "000395",  # จิตวิทยา
        "psychology": "000395",  # จิตวิทยา
        "Business and trade": "000522",  # ธุรกิจ
        "Master of Science": "000000",
        "Business related": "000013",  # BUSINESS
        "IT/ Psychology": "000000",
        "Language": "000000",
        "language": "000000",
        "Management": "000024",  # การจัดการ
        "Sustainability": "000219",  # การพัฒนาอย่างยั่งยืน
        "Arts": "001104",  # ศิลปะ
        "digital design": "000128",  # COMMUNICATION DESIGN (ใกล้เคียงงานออกแบบดิจิทัล)
        "Cybersecurity": "000000",
        "Marketing/ BBA": "000050",  # BUSINESS ADMINISTRATION
        "Bioinformatics": "000442",  # ชีวสารสนเทศและชีววิทยาระบบ
        "MBE": "000000",
        "Marketing field": "000101",  # การตลาด
        "Not specify yet": "000000",
        "Haven’t decided": "000000",
        "To be decided": "000000",
        "Business Economics": "000544",  # FINANCIAL ECONOMICS (ใกล้เคียง)
        "Business and Management": "000013",  # BUSINESS
        "Mycology": "003593",  # MEDICAL MYCOLOGY
        "Medical doctor": "001565",  # แพทยศาสตร์
        "Engineering": "000375",  # ENGINEERING
        "Either Finance or Cinematic Art": "000000",
        "Psychology": "000395",  # จิตวิทยา
        "Event management": "000232",  # CONVENTION AND EVENT MANAGEMENT
        "Haven't decided yet": "000000",
        "Hospitality": "000343",  # การโรงแรม
        "Food Science and Technology": "000583",  # FOOD SCIENCE AND TECHNOLOGY
        "Entrepreneurship": "000323",  # การเป็นผู้ประกอบการ
        "IT": "000381",  # คอมพิวเตอร์และเทคโนโลยีสารสนเทศ
        "Culinary Arts": "005106",  # FOOD AND CATERING (ใกล้เคียงสุด)
        "IR or digital marketing": "000000",
        "Counseling Psychology": "000234",  # COUNSELING PSYCHOLOGY
        "UX/UI": "003359",  # 3D ANIMATION/DIGITAL EFFECTS (เลือกเป็นหมวด 3D / design)
        "data for business and marketing": "000063",  # BUSINESS DATA ANALYSIS
        "Children illustration/ childhood education-development": "000289",  # EARLY CHILDHOOD EDUCATION
        "Food science": "000583",  # FOOD SCIENCE AND TECHNOLOGY
        "Commercial real estate": "000529",  # ธุรกิจอสังหาริมทรัพย์
        "Analytics": "000063",  # BUSINESS DATA ANALYSIS
        "Marketing/Finance": "000000",
        "Data Analytic": "000063",  # BUSINESS DATA ANALYSIS
        "media and communicate": "000300",  # การสื่อสารมวลชน
        "Bioinformatics": "000442",  # ชีวสารสนเทศและชีววิทยาระบบ
        "Digital Marketing": "000101",  # การตลาด
        "Entrepreneur / digital marketing": "000323",  # การเป็นผู้ประกอบการ
        "Business/marketing": "000013",  # BUSINESS
        "Business, finance, banking": "000110",  # การธนาคารและการเงิน
        "Finance and Legal": "000000",
        "Art, Data analyze": "000000",
        "Politics": "000325",  # การเมืองการปกครอง
        "Doctor of Medicine": "001565",  # แพทยศาสตร์
        "go blow hospitality business management": "000030",  # การจัดการการท่องเที่ยวและการโรงแรม
        "MBA": "000050",  # BUSINESS ADMINISTRATION
        "Mba": "000050",  # BUSINESS ADMINISTRATION
        "Early childhood education/child psychology": "000289",  # EARLY CHILDHOOD EDUCATION
        "Environment": "000083",  # การจัดการสิ่งแวดล้อม
        "Food Science and Business": "000583",  # FOOD SCIENCE AND TECHNOLOGY (ผสมด้านธุรกิจ)
        "Human Resource Management": "000053",  # การจัดการทรัพยากรมนุษย์
        "Industrial Design": "000313",  # การออกแบบอุตสาหกรรม
        "Chinese Language": "000730",  # ภาษาจีน
        "Design": "000305",  # การออกแบบ
        "Nutrition": "001251",  # อาหารและโภชนาการ
        "International Law and International Relations": "000000",
        "Data science": "007777",  # DATA SCIENCE AND ARTIFICIAL INTELLIGENCE
        "Data Science": "007777",  # DATA SCIENCE AND ARTIFICIAL INTELLIGENCE
        "Food Innovation, Nutrition and Health": "000583",
        "Philosophy": "000630",  # ปรัชญา
        "Accounts": "000878",  # วิชาชีพการบัญชี
        "Microbiology and Immunology": "000420",  # จุลชีววิทยา (รวมด้านภูมิคุ้มกัน)
        "Human-Computer Interaction": "000000",
        "Criminology": "001238",  # อาชญาวิทยา การบริหารงานยุติธรรมและสังคม
        "Business": "000013",
        "Business Management": "000093",  # BUSINESS MANAGEMENT
        "Business management": "000093",  # BUSINESS MANAGEMENT
        "School management": "000000",
        "Fashion, Event Organizer": "000000",
        "Finance and accounting": "000000",
        "MSc Management": "000024",
        "IR": "000223",  # การระหว่างประเทศ
        "Art and design": "000305",  # การออกแบบ
        "Education": "000302",  # EDUCATION
        "3d": "003359",  # 3D ANIMATION/DIGITAL EFFECTS
        "Accounting and Finance": "000000",
        "Education": "000302",
        "Dramaturgy": "000287",  # DRAMA
        "Master of Business Administration (Marketing)": "000050", 
        "Anatomy": "000017",  # กายวิภาคศาสตร์
        "Law": "000001",  # กฎหมาย
        "law": "000001",  # กฎหมาย
        "Chinese language": "000730",  # ภาษาจีน
        "Business Administration or Art Design": "000050",  # BUSINESS ADMINISTRATION (สุ่มเลือก)
        "Cosmetics or fashion": "000000",
        "Economics and Finance": "000544",  # FINANCIAL ECONOMICS
        "Teaching": "000278",  # การสอน
        "Theoretical Computer Science": "000000",
        "pastry": "005106",  # FOOD AND CATERING
        "BBA": "000050",  # BUSINESS ADMINISTRATION
        "UX UI": "003359", 
        "Dentistry": "000514",  # ทันตแพทยศาสตร์
        "MBA - marketing": "000050",
        "Account, Law, Food Safety": "000000",
        ".": "000000",
        "Biomedical Sciences": "000448",  # ชีวเวชศาสตร์
        "Technology": "000964",  # วิทยาศาสตร์และเทคโนโลยี
        "Food science related field": "000583", 
        "Business Administration": "000050",
        "Forensic Sciences, Mortuary Sciences, Education": "000000",
        "Master of Business Administration": "000050",
        "Maketing": "000101",
        "Data science or information management": "007777",
        "Finance or Marketing": "000000",
        "UX Researcher": "003359",
        "None": "000000",
        "Business Management": "000093",
        "Business management": "000093",
        "Bioengineering": "003875",  # BIOENGINEERING
        "New media design": "000128",
        "Data Analyst": "000063",
        "MA in International Education": "000302",  # EDUCATION
        "International Development": "000281",  # DEVELOPMENT ADMINISTRATION
        "computer science, statistic or engineering": "000173",  # COMPUTER SCIENCE-STATISTICS
        "Applied linguistics, Master of Arts": "000748",  # ภาษาศาสตร์ประยุกต์
        "English literature in visual culture": "000848",  # วรรณคดีอังกฤษ
        "MBA, Economics": "000050",
        "International Business": "000527",  # ธุรกิจระหว่างประเทศ
        "Culinary Art and Kitchen Management": "005106", 
        "Environmental Management": "000083",  # การจัดการสิ่งแวดล้อม
        "AI Marketing": "000000",
        "not yet decided": "000000",
        "Quantum Technology": "008119",  # QUANTUM SCIENCE AND TECHNOLOGY
        "Engineering field": "000375",
        "Innovation": "000156",  # การบริหารเทคโนโลยี (เลือกใกล้เคียงสุด)
        "Engineering": "000375",
        "Real Estate/ Entrepreneurship": "000529",  # ธุรกิจอสังหาริมทรัพย์
        "Music": "000470",  # ดนตรี
        "Digital marketing": "000101", 
        "Finance": "000318",
        "Biodesign in medicine": "000000",
        "Entrepreneur": "000323",
        "Neuroscience": "000627",  # ประสาทวิทยาศาสตร์
        "Culinary / Tech": "000000",
        "Strategic studies": "000000",
        "Chinese for business purpose": "000730",
        "Logistics, Supply Chain Management": "000026",
        "Computer Science - Machine Learning": "000167",
        "Bussiness": "000013",
        "Drama or finance": "000000",
        "Art and design, Illustration, language (Japanese)": "000000",
        "Strategy": "000000",
        "Cybersecurity": "000000",
        "International business": "000527",
        "Design for Art Direction": "000305",
        "Logistics and supply chain management": "000026",
        "Marketing, MBA": "000050",
        "marketing": "000050",
        "Molecular Biology": "000432",  # ชีววิทยาของเซลล์และโมเลกุล
        "Information Technology": "001423",  # เทคโนโลยีสารสนเทศ
        "Food Production": "000000",
        "Pharmaceutics": "000486",  # เภสัชกรรม (ใกล้เคียง)
        "Social entrepreneurship": "000323",
        "Revenue": "000000",
        "Communication Design": "000128",
        "Master of Management": "000024",
        "Gastronomy": "005106",
        "Theoretical Chemistry": "001293",  # เคมีฟิสิกัล (เลือกเป็นเคมีเชิงทฤษฎี)
        "Chinese": "000730",
        "Branding marketing": "000101",
        "MM": "000000",
        "Biotechnology": "001379",  # เทคโนโลยีชีวภาพ
        "Tourism and hospitality": "000030",
        "Hospitality and Management": "000000",
        "Marketing/Business": "000013",
        "Management/ Marketing": "000000",
        "Film making": "000728",  # ภาพยนตร์
        "Biological research": "000938",
        "MF": "000000",
        "Food science innovation": "000583",
        "Strategic communication management": "000000",
        "Data sci": "007777",
        "human nutrition": "001251",
        "Jewelry field": "001237",  # อัญมณีและเครื่องประดับ
        "Managements": "000024",
        "System architect": "000000",
        "Entrepreneurship": "000323",
        "Illustration": "000128",
        "Cs": "000167",
        "Investment banking": "000110",
        "idk": "000000",
        "Sound engineer": "000000",
        "Microbiology and immunology": "000420",
        "Astrophysics": "000000",
        "Do not know yet": "000000",
        "Bussiness Administration": "000050",
        "Software Engineering": "000997",
        "Communication": "000125",
        "Msc finance": "000318",
        "Finance, econ": "000000",
        "Doctor of medicine": "001565",
        "Computer science": "000167",
        "Fashion Design": "000536",  # FASHION DESIGN
        "Medical": "001565",
        "hospitality": "000343",
        "Maybe MBA": "000050",
        "Business Analyst/ Entrepreneur": "000323",
        "Culture and Languages": "000000",
        "Hospitality/ management": "000343",
        "Economic": "000284",  # DEVELOPMENT ECONOMICS (เลือกใกล้เคียง)
        "economic": "000284",
        "Art": "001104",
        "Branding": "000101",
        "Business Analyst": "000063",  # BUSINESS DATA ANALYSIS
        "I’m not sure yet": "000000",
        "AI and Machine Letning": "007777",
        "Thai traditional medicine": "001568",
        "Mk": "000101",  # การตลาด
        "Science": "000904",  # วิทยาศาสตร์
        "It might be psychological or educational": "000000",
        "Human development": "000684",  # พัฒนาการมนุษย์
        "Sustain": "000219",  # การพัฒนาอย่างยั่งยืน
        "Media and Communication": "000125",
        "BE": "000000",
        "General Management": "000024",
        "Finance/Accounting": "000000",
        "Artificial Intelligence": "007777",
        "supply chain": "000026",
        "logistic": "000026",
        "Unsure": "000000",
        "Cosmetic science": "000000", 
        "International Relations and Global Affairs": "008055",  # INTERNATIONAL RELATIONS AND GLOBAL AFFAIRS
        "Business study": "000013",
        "international relations and global affairs": "008055",
        "Media production": "000300",
        "Psychology / Finance": "000000",
        "Graphic designer": "000128",
        "International Development Studies": "000281",
        "IR and Law": "000000",
        "Anti-aging": "000000",
        "Technology and design": "000305",
        "Entrepreneurship management": "000323",
        "Gender equality": "000000",
        "Business or something similar to international relations but not in the politics area.": "000000",
        "paychology": "000395",  # พิมพ์ผิด ก็เทียบ psychology
        "Human Resources": "000053",
        "Fashion": "000536",

        # --------------------------------------------------------
        # หากมีการซ้ำ / หรือเจอคำใกล้เคียงซ้ำด้านบน ให้ยึดตาม mapping ก่อนหน้า
        # --------------------------------------------------------
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


def get_problem_education_series(df_data):
    mapping_problem_education = {
        "No": "01",  # ไม่มีปัญหา
        "Yes (Lack of financial support)": "05",  # ขาดแคลนเงินทุน
        "Yes (Insufficient institution information)": "02",  # ข้อมูลสถานที่ศึกษาต่อไม่เพียงพอ
        "Yes (Insufficient required knowledge)": "04",  # ขาดความรู้พื้นฐานในการศึกษาต่อ
        "-": "00",  # อื่นๆให้ระบุ
        "Yes (Lack of academic qualifications)": "03",  # คุณสมบัติในการสมัครเรียน
        "All of above": "00",  # อื่นๆให้ระบุ
        "My passion": "00",  # อื่นๆให้ระบุ
        "lack of self-confidence ;—;": "00",  # อื่นๆให้ระบุ
        "Seek for scholarship": "00",  # อื่นๆให้ระบุ
        "Yes (lack of financial support and insufficient institution info)": "05",  # ขาดแคลนเงินทุน และ ข้อมูลสถานที่ศึกษาต่อไม่เพียงพอ
        "Lack of time and anchor of responsibility": "00",  # อื่นๆให้ระบุ
        "I want to try working first before committing": "00",  # อื่นๆให้ระบุ
        "Lack of time": "00",  # อื่นๆให้ระบุ
        "Lack work experience": "00",  # อื่นๆให้ระบุ
        "yes, i haven't given it much thought and not enough money to pay for it yet.": "05",  # ขาดแคลนเงินทุน
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
            mapped_value = mapping_problem_education.get(str(row['Do you have any problem in furthering your study?']).strip())
        else:
            if required_education == '1':
                # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
                mapped_value = mapping_problem_education.get(str(row['Do you have any problem in furthering your study?']).strip())
            else:
                mapped_value = ''
            # ถ้า work_status ไม่เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            # mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_problem_education_text(df_data):
    
    # เรียกใช้ฟังก์ชัน get_problem_education_series เพื่อรับ Series ของสถานะการทำงาน
    problem_education_series = get_problem_education_series(df_data)
    def map_data(row):
        value = str(problem_education_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if value == '00':
            # ถ้า cause_education_series เท่ากับ '00' ตอบกลับเป็นค่า Do you have any problem in furthering your study?
            mapped_value = str(row['Do you have any problem in furthering your study?']).strip()
        else:
            # ถ้า cause_education_series เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)

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


def get_cause_education_series(df_data):
    mapping_cause_education = {
        "my own desire": "4",  # เป็นความต้องการของตนเอง
        "parent’s desire": "1",  # เป็นความต้องการของบิดา/มารดา หรือผู้ปกครอง
        "career requirement": "2",  # งานที่ต้องการต้องใช้วุฒิสูงกว่า ปริญญาตรี
        "scholarship acquirement": "3",  # ได้รับทุนศึกษาต่อ
        "I want to grow, but more slowly and with some learned experience this time, instead of forcing my way to a management position as I have done..": "4",  # เป็นความต้องการของตนเอง
        "Aim to create a ground-breaking startup that creates a new industry.": "4",  # เป็นความต้องการของตนเอง
        "Higher paid job": "4",  # เป็นความต้องการของตนเอง
        "-": "0",  # อื่นๆให้ระบุ
        "Convenience of being close to home": "0",  # อื่นๆให้ระบุ
        "My own and parents’": "4",  # เป็นความต้องการของตนเอง
        "Not studying": "0",  # อื่นๆให้ระบุ
        "in order to learn new things that can help me get a better job to aid me in having a stable income in the future.": "4",  # เป็นความต้องการของตนเอง
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
            mapped_value = mapping_cause_education.get((str(row['What are the reasons for furthering your study?']).strip()))
        else:
            if required_education == '1':
                # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
                mapped_value = mapping_cause_education.get((str(row['What are the reasons for furthering your study?']).strip()))
            else:
                mapped_value = ''
            # ถ้า work_status ไม่เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            # mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)


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
        # สมมุติว่าในแต่ละแถวข้อมูลอยู่ในคอลัมน์ 'What courses at Mahidol University should be promoted to help contribute to your career?'
        raw_data = str(row['What courses at Mahidol University should be promoted to help contribute to your career?'])
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

