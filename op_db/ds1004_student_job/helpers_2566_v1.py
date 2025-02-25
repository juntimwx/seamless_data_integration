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
            mapped_value = row['Soi/Alley of your workplace']

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
            mapped_value = row['Road of your workplace']

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
            mapped_value = row['Sub-district of your workplace']

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
            mapped_value = address_country.get(row['Country of your workplace'].strip())

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
            mapped_value = row['Zip code of your workplace']

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
        "Australia ": "AU",
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

        # "yes": "1",
        # "no": "2"
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
            mapped_value = mapping_required_education.get(str(row['Further Study Plan']).strip())

        return mapped_value

    return df_data.apply(map_data, axis=1)


def get_level_education_series(df_data):
    mapping_level_education = {
        "Graduate diploma": "50",   # ประกาศนียบัตรบัณฑิต
        "Master's degree": "60", # ปริญญาโท
        "Doctoral degree": "80", # ปริญญาเอก
        "a higher graduate diploma": "70", # ประกาศนียบัตรบัณฑิตชั้นสูง
        "a certificate/specialization (which offers higher rate of salary than a doctor’s degree.)": "90", # ประกาศนียบัตรหรือหลักสูตรเฉพาะ (ที่บรรจุในอัตราเงินเดือนสูงกว่าปริญญาเอก)
        "Master's degree": "60", # ปริญญาโท
        "Bachelor's degree": "40", # ปริญญาตรี
        "Not sure yet": "no data",
        "Not sure": "no data",
        "Language": "30" ,  # ประกาศนียบัตรวิชาชีพชั้นสูง (ในกรณีที่เป็นหลักสูตรหรือประกาศนียบัตรด้านภาษา)
        "Both masters and certificates (I've always been a certificate chaser lol)": "60",
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
            mapped_value = mapping_level_education.get(str(row['What level you want to further your study?']).strip())
        else:
            if required_education == '1':
                # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้
                mapped_value = mapping_level_education.get(str(row['What level you want to further your study?']).strip())
            else:
                mapped_value = ''
            # ถ้า work_status ไม่เท่ากับ '2' หรือ '4' ตอบกลับเป็นค่าว่าง
            # mapped_value = ''

        return mapped_value

    return df_data.apply(map_data, axis=1)


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

