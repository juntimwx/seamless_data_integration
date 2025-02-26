import pandas as pd
import re

# รหัสบัตรประชาชน
def get_citizen_id_series(df_data, df_sql):
    # แปลงชนิดข้อมูลของคอลัมน์ 'Student ID-Final' เป็นสตริง
    student_ids = df_data['Student ID-Final'].astype(str)

    # สร้าง Dictionary สำหรับ 'CitizenNumber' โดยใช้ 'Code' เป็น Key
    citizen_dict = df_sql.set_index('Code')['CitizenNumber'].to_dict()

    # สร้าง Dictionary สำหรับ 'Passport' โดยใช้ 'Code' เป็น Key
    passport_dict = df_sql.set_index('Code')['Passport'].to_dict()

    # ฟังก์ชันสำหรับดึงค่า 'CitizenNumber' หรือ 'Passport' ตามเงื่อนไข
    def get_citizen_or_passport(student_id):
        citizen_number = citizen_dict.get(student_id, None)
        if pd.isna(citizen_number) or citizen_number == '':
            return passport_dict.get(student_id, '')
        else:
            return citizen_number

    # สร้าง Series ใหม่สำหรับ 'CITIZEN_ID'
    citizen_id_series = student_ids.apply(get_citizen_or_passport)

    return citizen_id_series

# รหัสสถานะการทำงาน
def get_work_status_series(df_data):
    work_status_mapping = {
        'Unemployed before graduation and employed after graduation': '1',
        'Employed and currently pursuing a higher degree': '2',
        'Unemployed': '3',
        'Currently pursuing a higher degree': '4',
        'Employed in the same field before and after graduation': '5',
        'Employed before and change the field work after graduation': '6',
        'Employed before graduation and promoted after graduation in the same field': '7',
    }

    def map_work_status(row):
        return work_status_mapping.get(row['Currently Employed Status'], '')

    work_status_series = df_data.apply(map_work_status, axis=1)
    return work_status_series

# รหัสสถานะการเกณฑ์ทหาร  เงื่อนไข ถ้าเป็นผู้หญิงใส่ -
def get_military_status_series(df_data):
    mapping = {
        'Taken a draft deferment period or Exempted from military service or Conscripted - อยู่ในช่วงผ่อนผันเกณฑ์ทหาร หรือได้รับการยกเว้น หรือผ่านการเกณฑ์ทหารแล้ว': '0'
    }

    def map_military_status(row):
        if row['Prefix'] == 'Mr.':
            return mapping.get(row['Military Status (Male only) -  สถานะการเกณฑ์ทหาร(เฉพาะเพศชาย)'], '1')
        else:
            return '-'

    military_status_series = df_data.apply(map_military_status, axis=1)
    return military_status_series

# รหัสสถานะการเป็นนักบวช
def get_ordinate_status_series(df_data):
    # สร้างฟังก์ชันสำหรับแมปค่า
    def map_ordinate_status(text):
        if pd.isna(text):
            return ''
        elif 'ไม่ได้เป็นนักบวช' in text:
            return '1'
        elif 'อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา น้อยกว่า 3 เดือน' in text:
            return '2'
        elif 'อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา 4 เดือน - 1 ปี' in text:
            return '3'
        elif 'อยู่ในระหว่างการเป็นนักบวช ระยะเวลาถึงกำหนดลาสิกขา มากกว่า 1 ปี' in text:
            return '4'
        else:
            return '5'  # หรือค่าที่คุณต้องการสำหรับกรณีอื่น ๆ

    # ใช้ฟังก์ชันกับคอลัมน์ 'Being Ordained as a Priest Status - สถานะการเป็นนักบวช'
    ordinate_status_series = df_data['Being Ordained as a Priest Status -  สถานะการเป็นนักบวช'].apply(map_ordinate_status)

    return ordinate_status_series

# รหัสประเภทงานที่ทำ เงื่อนไข ถ้ารหัสสถานะการทำงานเป็น 3 หรือ 4 จะต้องเป็นค่าว่างเท่านั้น
def get_occupation_type_series(df_data):
    occupation_mapping = {
        'Account manager': '03',
        'AXONS': '03',
        'Cabin Crew': '03',
        'Civil Servant/Employee in a government organization': '01',
        'Consultant': '03',
        'Design Freelancer': '04',
        'Employee in a Tech company': '03',
        'Employee in an ecommerce company': '03',
        'Employee in an international organization': '05',
        'Employee in an international school': '05',
        'Employee in an thai organization': '03',
        'English Tutor': '03',
        'Event organizer': '03',
        'Freelance': '04',
        'Freelance ': '04',
        'Freelancer in film production industry': '04',
        'Graphic designer': '03',
        'have 1 owned business, hired by family, hired part time by singaporean company, hired full time by BOI company': '00',
        'Model': '03',
        'Music industry': '03',
        'no': '00',
        'None': '00',
        'Political career': '01',
        'Production of vaccine': '02',
        'Real Estate Agent': '03',
        'School': '03',
        'Staff in Embassy': '05',
        'Staff in School': '03',
        'Staff in the beauty retail industry': '03',
        'Staff/Employee in a private company': '03',
        'Staff/Employee in a public company': '02',
        'Staff/Employee in a State-Enterprise Agency': '02',
        'Startup': '03',
        'Store Design and Business Development': '03',
        'teacher': '03',
        'Tech': '03',
        'Tutor': '03',
        'Unemployed': '00',
        'Writer': '03',
        'Your own business/family business': '04',
    }

    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)

    def map_occupation_type(row):
        work_status = str(work_status_series.loc[row.name])
        occupation = row['Type of Job']

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น 00 เพื่อกรอกข้อมูลเพิ่มเติม
            mapped_value = occupation_mapping.get(occupation, '00')

        return mapped_value

    occupation_type_series = df_data.apply(map_occupation_type, axis=1)
    return occupation_type_series

# ประเภทงานที่ทำ ระบุข้อความเพิ่มเติม เงื่อนไข ถ้ารหัสประเภทงานที่ทำ ไม่เท่ากับ 0 หรือเป็นค่าว่าง จะต้องเป็นค่าว่างเท่านั้น
def get_occupation_text(df_data):
    # เรียกใช้ฟังก์ชัน get_occupation_type_series เพื่อรับ Series ของรหัสประเภทงานที่ทำ
    occupation_type_series = get_occupation_type_series(df_data)
    # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
    mapped_value = df_data['Type of Job'].where(occupation_type_series == '00', other='')

    return mapped_value

# รหัสความสามารถพิเศษ เงื่อนไข ถ้ารหัสสถานะการทำงานเป็น 3 หรือ 4 จะต้องเป็นค่าว่างเท่านั้น
def get_talent_id_series(df_data):
    talent_mapping = {
        'Art': '04',
        'Business': '00',
        'Business management': '00',
        'Business skills': '00',
        'Business skills learned during the time in MUIC': '00',
        'Coding': '02',
        'Communication': '00',
        'Communication skills': '00',
        'Communication skills, Critical Thinking skills, Analytical skills, Microsoft Excel skills': '00',
        'Computer literacy': '02',
        'Connection': '00',
        'Creative': '00',
        'Critical Thinking': '00',
        'Critical thinking': '00',
        'Critical thinking skills': '00',
        'Digital Marketing': '00',
        'Digital Marketing skill': '00',
        'English and hospitality skills': '01',
        'Everything in real world': '00',
        'Excel': '02',
        'experience of sales and listening skills': '00',
        'Extra curriculum activities': '03',
        'Finance': '00',
        'Finance & Accounting skills': '00',
        'Financial': '00',
        'Foreign Languages': '01',
        'Global Awareness': '00',
        'Internship': '00',
        'Management': '00',
        'Management Skills': '00',
        'Marketing': '00',
        'marketing and excel skills': '02',
        'Mindset': '00',
        'Negotiation skill': '00',
        'Own a business': '00',
        'Producing Music': '06',
        'Programming': '02',
        'Related knowledge from BBA courses': '00',
        'Sales and marketing': '00',
        'Service minded': '00',
        'Socialism': '00',
        'Sport': '05',
        'Talents and work experiences': '00',
        'Teaching': '00',
        'The ability to do deep work and discipline.': '00',
        'The skills I learned in my major': '00',
        'Traditional dance/Music': '06',
        'Understanding of human minds/thought process': '00',
    }

    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)

    def map_talent_id(row):
        work_status = str(work_status_series.loc[row.name])
        talent = row['Which skill can most help you to get employed?']

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น 00 เพื่อกรอกข้อมูลเพิ่มเติม
            mapped_value = talent_mapping.get(talent, '00')

        return mapped_value

    talent_id_series = df_data.apply(map_talent_id, axis=1)
    return talent_id_series

# ความสามารถพิเศษ ระบุข้อความเพิ่มเติม เงื่อนไข ถ้ารหัสความสามารถพิเศษ ไม่เท่ากับ 0 หรือ เป็นค่าว่าง จะต้องเป็นค่าว่างเท่านั้น
def get_talent_text(df_data):
    # เรียกใช้ฟังก์ชัน get_talent_id_series เพื่อรับ Series ของรหัสความสามารถพิเศษ
    talent_type_series = get_talent_id_series(df_data)
    # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
    mapped_value = df_data['Which skill can most help you to get employed?'].where(talent_type_series == '00', other='')

    return mapped_value

# รหัสตำแหน่งงาน เงื่อนไข ถ้ารหัสสถานะการทำงานเป็น 3 หรือ 4 จะต้องเป็นค่าว่างเท่านั้น
def get_position_series(df_data):
    job_mapping = {
        'Tax consultant': '241160',
        'ESL Consultant': '233010',
        'Strategic Planner': '241310',
        'Case Team Assistant': '343220',
        'Sale representative': '341520',
        'Foriegn Trade officer': '342230',
        'Real Estate Agent, Teacher': '341320',
        'Expatriate Officer': '332020',
        'Content Creator': '245190',
        'Marketing Assistant': '241930',
        'Marketing Manager and Editorial Assistant': '123120',
        'Admin & HR Assistant': '419010',
        'Package Operations Specialist, Seller Packages': '413190',
        'Content Producer (Corporate Partnership - Beauty)': '245190',
        'Movie Acquisition': '245550',
        'International Coordinator': '332020',
        'Sales and Marketing for  family business, Project director, and assistance of curators for Thailand Biennale Phuket': '341520',
        'Operation coordinators': '413190',
        'Media Planner': '343120',
        'Investment Analyst': '241130',
        'Manager': '121110',
        'QA Engineer': '214920',
        'Associate Equity Analyst': '241130',
        'General Administration Officer': '411190',
        'Marketing': '241320',
        'Marketing staff': '241320',
        'Import Export Coordinator': '342230',
        'Admin': '419010',
        'Associate Consultant': '241160',
        'CEO and COO': '121110',
        'General manager': '121110',
        'Junior Office Assistant': '419010',
        'Client Service Assistant - Private Wealth Management': '421130',
        'Junior Internal Audit Officer': '241150',
        'Social media and content creator': '245190',
        'Director Assistant': '343120',
        'Linguist (Previously Marketing Project Manager)': '264340',
        'Business Owner (Family Business)': '131120',
        'Junior Backend Developer': '251230',
        'Executive Assistant- Operations and Marketing': '343120',
        'Regional Sales Executive': '123310',
        'Stylist and designer': '347140',
        'AE': '241320',
        'General Document Controlle': '419010',
        'Project Manager': '131120',
        'Content Moderator': '411190',
        'Finance ERP Consultant': '241160',
        'Finance and Accounting Analysts': '241110',
        'Associate Software Engineer': '251230',
        'Marketing Executives ': '123120',
        'Content Strategist': '245190',
        'Assistant ': '343120',
        'Senior Translator': '264310',
        'Cabin crew': '511120',
        'BD&KOL specialist': '241320',
        'Market Research Analyst': '241310',
        'Application Developer': '251230',
        'Marketing planning and strategy': '241310',
        'Software Engineer': '251230',
        'F2F Fundraiser': '511390',
        'Marketing Trainee ': '241320',
        'Production assistant': '343190',
        'Marketing & Partnerships': '241320',
        'Consultant ': '241160',
        'Property Consultant': '341320',
        'Customer Care Coordinator ': '422190',
        'Consulting Associate': '241160',
        'Assistant Project Manager': '131120',
        'Sales coordinator': '341520',
        'Executive Analyst, Customer Success': '241310',
        'Junior Sampling Technician': '313990',
        'Digital Marketing Assistant': '241930',
        'UX ': '251230',
        'Cybersecurity Operations Analyst': '251130',
        'Spa receptionist': '422220',
        'Biomedical Researcher': '213190',
        'Associate - Workforce Transformation ': '241110',
        'Creative content': '245190',
        'Sale and Marketing': '341520',
        'Media master': '245550',
        'Communication and Marketing': '241320',
        'Assistant General Manager ': '121110',
        'Boardgame designer/Video Editor': '347190',
        'Executive ': '241110',
        'Business Owner': '131120',
        'Human Resource Officer': '419020',
        'Homes Operation Coordinator': '413190',
        'Guest service agent': '422220',
        'Japanese Assistant': '343120',
        'Trust and Safety Associate': '516930',
        'Sales representative': '341520',
        'sales and marketing executive': '341520',
        'Graphic designer ': '347135',
        'Commercial Flagship Store Manager for Power Tools - Singapore Market': '123120',
        'Software Engineer ': '251230',
        'Marketing Manager': '123120',
        'Accounting team member': '241110',
        'Export manager assistance': '342230',
        'Chef de partie': '512220',
        'Marketing & Project Coordinator ': '241320',
        'Ceo': '121110',
        'Aide to municipal level of political party': '111010',
        'General Manager': '121110',
        'Senior Analyst, Seller Operation Service': '241310',
        'Web Designer': '251230',
        'Marketing officer': '241320',
        'Content moderator-Japanese Language': '411190',
        'Product Development & Analysis': '214910',
        'Business Support Project': '131120',
        'Owner and manager': '131120',
        'BOD': '121110',
        'Product Operation Administrator': '419010',
        'Finance and accounting officer': '241110',
        'Executive recruitment consultant ': '241160',
        'freelance': '245190',
        'R&D Director': '122110',
        'Ballet Teacher': '235420',
        'Assistant of CEO': '343120',
        'Business Executive': '241110',
        'Category management initiatives': '241320',
        'PA': '343120',
        'Advisory Associate': '241160',
        'Travel Coordinator': '422190',
        'Managing Director': '121110',
        'Research Assistant Internship': '211220',
        'Management trainee': '241110',
        'Strategic Project Management Specialist': '241310',
        'Data Engineer': '251230',
        'Sales Finance': '241110',
        'Export Document Officer': '342230',
        'Lifestyle Concierge': '422220',
        'Graphic Design Foreman': '347135',
        'Executive Creative Designer': '347190',
        'Teacher': '233010',
        'Coordinator, Catering & Events': '512320',
        'Management Analyst': '241310',
        'key account': '123310',
        'Technology Graduate': '251230',
        'Academic Information System Administrator': '251230',
        'Senior Marketing': '123120',
        'Editor': '245130',
        'ASEAN Supply and Logistics, Logistics Representative ': '413190',
        'ผู้ช่วยผู้รับใบอนุญาต': '233010',
        'Graphic Designer': '347135',
        'Business Analyst': '241310',
        'Data analyst': '212010',
        'HR Coordinator': '419020',
        'Teacher assistant ': '333020',
        'Product designer': '347190',
        'Operation Assistance': '413190',
        'Artistic Director/Creative Production Assistant': '245550',
        'IT (QA Engineer)': '214920',
        'Digital Marketing': '241320',
        'sales manager': '123310',
        'Agent': '341320',
        'Event Co-ordinator': '512320',
        'Academic Administration ': '411190',
        'receptionist': '422220',
        'Human Resources ': '419020',
        'Marketing (Import - export)': '241320',
        'Employee': '411190',
        'Loyalty & Online CRM Department Manager': '123120',
        'Mathematics Tutor ': '233010',
        'PSA': '411190',
        'English Teacher & Content Creator': '233010',
        'Purchasing Manager\t': '123130',
        'Quality assurance engineer': '214920',
        'Educator': '233010',
        'Assistant Sales and Marketing Manager ': '123310',
        'International E-commerce Executive': '241320',
        'Global Ecommerce - Serach Ops': '241320',
        'Digital Marketing manager': '123120',
        'Corporate Affair Officer': '241320',
        'Reservation Sales Agent': '422220',
        'Beauty Advisor': '522020',
        'Kols and Influencer Specialist': '241320',
        'UX UI Designer': '251230',
        'Artist': '347190',
        'Procurement': '123130',
        'Brand Assistant': '241930',
        'Content Moderator ': '411190',
        'Financial advisory analyst': '241130',
        'RM supporter': '241110',
        'Assistant to Tourism, Culture and Press Section': '343120',
        'Stylish assistant ': '343120',
        'Event  Coordinator': '512320',
        'Research Assistant': '211220',
        'Career Advisor / HR Consultant': '241160',
        'Assistant': '343120',
        'Marketing Executive ': '123120',
        'Founder': '131120',
        'Product Operations Analyst': '241310',
        'Brand & Growth Associate ': '241320',
        'Tutoring teacher': '233010',
        'Research and Development ': '122110',
        'UXUI Designer': '251230',
        'Management Trainee ': '241110',
        'Inventory Controller': '413140',
        'Margin Management Analyst': '241130',
        'Content creator': '245190',
        'Sales executive ': '341520',
        'Software Developer': '251230',
        'Programme Officer (Writer)': '245190',
        'Property Consultant ': '341320',
        'Corporate Finance and Treasury': '241110',
        'Senior Client Relations Manager ': '121110',
        'Data Scientist': '212010',
        'Nutrition Advisor': '322320',
        'E-commerce Executive': '241320',
        'Owner': '131120',
        'Website manager and graphic assistant': '251230',
        'Procurement contracts administrator ': '123130',
        'Business Investment Associate ': '241160',
        'Revenue management ': '241110',
        'Client Solutions Analyst (Private Equity)': '241130',
        'Product management': '123120',
        'Graphic design': '347135',
        'Learning Coordinator': '333020',
        'Data scientists ': '212010',
        'MD': '121110',
        'Community Associate': '343190',
        'Visual Merchandiser': '347135',
        'AAd Operation & Performance Marketing Analyst': '241310',
        'Export CX': '342230',
        'Investor Relations ': '241110',
        'Digital Marketing ': '241320',
        'Manager ': '121110',
        'Business Development Executive': '241320',
        'Dog Fitness Trainee': '612940',
        'Ceo Assistant': '343120',
        'Developer': '251230',
        'Tutor': '233010',
        'Direct sales operation': '341520',
        'Ux designer': '251230',
        'Volumetric Accountant': '241110',
        'QC staff': '311970',
        'Software Engineer  ': '251230',
        'CEO & Founder': '121110',
        'Consultant executive ': '241160',
        'Program officer': '241310',
        'Marketing/ Project Manager': '241320',
        'Management Associate': '241110',
        'Directing Manager': '121110',
        'Finance administrator': '241110',
        'Administration/ Staff/ Event Coordinator': '419010',
        'Production Trainee': '343190',
        'Analyst': '241310',
        'Model, ': '521020',
        'Tourist guide': '511310',
        'Learning & Development Coordinator ': '333020',
        'Assistant Purchasing Manager': '123130',
        'Financial Markets officer': '241110',
        'Assistant to family ': '343120',
        'Personal Assistant': '343120',
        'Sale coordinator ': '341520',
        'Management Trainee - Sales & Operation': '341520',
        'Event Officer': '512320',
        'Hotel Reception ': '422220',
        'Head of marketing ': '123120',
        'Sales Coordinator ': '341520',
        'Managing Partner': '121110',
        'Production staff': '343190',
        'Risk Manager': '121110',
        'Creative Production': '245190',
        'Freelance English tutor': '233010',
        'Thai Language Review': '264310',
        'Product development executive ': '214910',
        'Sales executives ': '123310',
        'HR': '419020',
        'PMO': '131120',
        'Project Management': '131120',
        'Content creator, freelance graphic designer': '245190',
        'Assistant Fund Manager': '241110',
        'quality assurance': '214920',
        'Project Manager ': '131120',
        'Associate ': '241110',
        'Live streamer': '245190',
        'Reservation Agent': '422220',
        'Mt': '241110',
        'System engineer': '214420',
        'Software Tester': '251230',
        'Sales Associates ': '341520',
        'Accountant': '241110',
        'Livestream Operator': '245190',
        'R&D': '122110',
        'Tech consult': '251120',
        'Investment Banking Advisor': '241160',
        'Client Service Assistant': '421130',
        'Relationship officer ': '241110',
        'Business analyse': '241310',
        'Assistance Sound engineer ': '313160',
        'CFO': '121110',
        'Business operation coordinator ': '413190',
        'Co-poducer': '245550',
        'Liquidity Associate': '241110',
        'Owner & CEO': '121110',
        'Assiantant Manager': '343120',
        'Programmer': '251230',
        'Club Lounge Agent': '422220',
        'Account Executive': '341520',
        'Marketing Executive': '123120',
        'Tax consultant': '241160',
        'UMC (management candidate)': '121110',
        'Freelance ': '245190',
        'Relationship Management': '241110',
        'Partnership': '241320',
        'Investment consultant ': '241160',
        'Sales assistant ': '341520',
        'Designer': '347135',
        'Vm': '347135',
        'Seller': '341520',
        'Business owners ': '131120',
        '.': '411190',
        'Editorial coordinator ': '245130',
        'Business development': '241320',
        'Human Resources Officer': '419020',
        'Performance Marketing': '241320',
        'Co': '241320',
        'Marketing Specialist': '241320',
        'Administration Staff': '419010',
        'AMD': '241110',
        'Greeter': '422220',
        'Import': '342230',
        'Executive Assistant ': '343120',
        'Purchaser': '123130',
        'Protocol Officer': '243290',
        'No': '411190',
        'BD': '241320',
        'Writer': '245190',
        'Demand planningAssociate': '241310',
        'Assistant of member of parliament ': '111010',
        'Account executive ': '241320',
        'Brand Associate': '241320',
        'Partner executive': '241320',
        'Data & Informative Marketing': '241310',
        'Product Op': '241320',
        'Managing director ': '121110',
        'Associate consultant HR executive search ': '241160',
        'Product Operation Analyst': '241310',
        'Project Officer': '131120',
        'Sales': '341520',
        'Product Marketing Officer': '241320',
        'Biddable executive ': '241320',
        'English Teacher': '233010',
        'Family Business': '131120',
        'Sales Executive': '341520',
        'Influencer Strategic Planner': '241310',
        'Caseworker': '241160',
        'law enforcement officer': '516220',
        'Sales and Marketing Assosiate': '341520',
        'Humanitarian Officer/Security Officer': '516220',
        'COO': '121110',
        'Junior Marketing Consultant': '241320',
        'Assistance Manager': '343120',
        'Business administration ': '241110',
        'Wms Associate': '413140',
        'Interpreters': '264320',
        'HR Specialist (Management Trainee)': '419020',
        'General': '121110',
        'Care Supervisor': '515120',
        'Receptionist ': '422220',
        'Project occordinator': '131120',
        'MMOS staff': '411190',
        'Marketing Analysts': '241310',
        'Account manager ': '241110',
        'Sale officer assistant': '341520',
        'International Manager': '121110',
        'Marketing associate ': '241320',
        'Real Estate': '341320',
        'Senior Leadership Team Supporter and Communication Officer / Translator': '343120',
        'Communication Assistant (Part-time)': '343120',
        'Onboarding Experience Coordinator ': '241320',
        'Merchandiser': '341520',
        'Marketing Planning and strategy analyst': '241310',
        'Managing assistant ': '343120',
        'Production manager and Artist relation': '131120',
        'Digital campaign specialist': '241320',
        'News Reporters and Translators': '264210',
        'Channel manager': '123310',
        'Coordinator Marcom': '241320',
        'Manager Assitance': '343120',
        'เจ้าหน้าที่แผนกการตลาด': '241320',
        'Affiliate Influencer Management ': '241320',
        'Assistant Manager': '343120',
        'Tour Guide': '511310',
        'personal concierge ': '422220',
    }

    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)

    def map_position_status(row):
        work_status = str(work_status_series.loc[row.name])
        position = row['Position ']

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น 00 เพื่อกรอกข้อมูลเพิ่มเติม
            mapped_value = job_mapping.get(position, '00')

    position_status_series = df_data.apply(map_position_status, axis=1)
    return position_status_series

# ชื่อหน่วยงาน เงื่อนไข ถ้ารหัสสถานะการทำงานเป็น 3 หรือ 4 จะต้องเป็นค่าว่างเท่านั้น
def get_work_name(df_data):
    # Retrieve the Series of work statuses
    work_status_series = get_work_status_series(df_data)

    def check_work_name(row):
        # Get the work status for the current row
        work_status = str(work_status_series.loc[row.name])

        # Get the organization name, defaulting to empty string if missing
        work_name = row.get('Organization name', '')

        # Apply the specified condition
        if work_status in ['3', '4']:
            # If work_status is '3' or '4', return empty string
            mapped_value = ''
        else:
            # Otherwise, return the original organization name
            mapped_value = work_name
        return mapped_value

    # Apply the function to each row in the DataFrame
    work_name_series = df_data.apply(check_work_name, axis=1)
    return work_name_series


# รหัสประเภทกิจการ เงื่อนไข ถ้ารหัสสถานะการทำงานเป็น 3 หรือ 4 จะต้องเป็นค่าว่างเท่านั้น
def get_industry_series(df_data):
    industry_mapping = {
        'Agriculture / Forestry / Fisheries': 'A',
        'Art / Entertainment / Recreation': 'R',
        'Civil Services (Government, Armed Forces) / Social Security': 'O',
        'Construction': 'F',
        'Education': 'P',
        'Financial Services/Insurance': 'K',
        'General Business Services': 'N',
        'Healthcare / Charity / Non-Profit Organization': 'Q',
        'Hospitality / Catering': 'I',
        'Information and Communication': 'J',
        'International Organization / International Association': 'U',
        'Logistics and Warehouse': 'H',
        'Management Consultancy & Business Support Service': 'M',
        'Mining': 'B',
        'Motor Vehicles Retail and Whole Sale / Auto Repair': 'G',
        'Power & Energy / Oil & Gas / Heating, Ventilation & Air Conditioning': 'D',
        'Production': 'C',
        'Professional / Science / Academic': 'M',
        'Real Estate': 'L',
        'Small Family Owned Business': 'T',
        'Water Supply / Wastewater Treatment / Waste Management / Related Activities': 'E',
    }

    # เรียกใช้ฟังก์ชัน get_work_status_series เพื่อรับ Series ของสถานะการทำงาน
    work_status_series = get_work_status_series(df_data)

    def map_industry_status(row):
        work_status = str(work_status_series.loc[row.name])
        position = row['Industry ']

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if work_status in ['3', '4']:
            # ถ้า work_status เท่ากับ '3' หรือ '4' ตอบกลับเป็นค่าว่าง
            mapped_value = ''
        else:
            # ถ้า work_status เป็นค่าอื่นๆ ตอบกลับเป็นค่าที่ map ข้อมูลได้ หากไม่พบให้ส่งเป็น ''
            mapped_value = industry_mapping.get(position, '')

        return mapped_value

    industry_status_series = df_data.apply(map_industry_status, axis=1)
    return industry_status_series


def get_address_data(df_data):
    # Initialize target columns with empty strings
    df_data['QN_WORK_ADD'] = ''
    df_data['QN_WORK_MOO'] = ''
    df_data['QN_WORK_BUILDING'] = ''
    df_data['QN_WORK_SOI'] = ''
    df_data['QN_WORK_STREET'] = ''
    df_data['QN_WORK_TAMBON'] = ''

    # Iterate over each row to extract and map data
    for index, row in df_data.iterrows():
        # Address Number
        df_data.at[index, 'QN_WORK_ADD'] = extract_address_number(row['Address no of your workplace'])

        # Moo/Village Number
        df_data.at[index, 'QN_WORK_MOO'] = extract_moo_number(row)

        # Building Name
        df_data.at[index, 'QN_WORK_BUILDING'] = extract_building_name(row)

        # Soi/Alley
        df_data.at[index, 'QN_WORK_SOI'] = row['Soi/Alley of your workplace']

        # Street/Road
        df_data.at[index, 'QN_WORK_STREET'] = row['Road of your workplace']

        # Sub-district/Tambon
        df_data.at[index, 'QN_WORK_TAMBON'] = row['Sub-district of your workplace']

    return df_data[
        ['QN_WORK_ADD', 'QN_WORK_MOO', 'QN_WORK_BUILDING', 'QN_WORK_SOI', 'QN_WORK_STREET', 'QN_WORK_TAMBON']]


def extract_address_number(address):
    if pd.isnull(address):
        return ''
    # Use regex to extract the first number sequence from the address
    match = re.match(r'^\s*(\d+[\w/-]*)', str(address))
    if match:
        return match.group(1)
    else:
        return ''


def extract_moo_number(row):
    # Check all columns for 'Moo' or 'หมู่' and extract the number
    moo_number = ''
    for col in ['Address no of your workplace', 'Soi/Alley of your workplace', 'Road of your workplace']:
        if pd.isnull(row[col]):
            continue
        text = str(row[col])
        # Search for 'Moo' followed by a number
        match = re.search(r'\bMoo\.?\s*(\d+)', text, re.IGNORECASE)
        if not match:
            # Search for 'หมู่' followed by a number (Thai word for Moo)
            match = re.search(r'หมู่\s*(\d+)', text)
        if match:
            moo_number = match.group(1)
            break
    return moo_number


def extract_building_name(row):
    building_name = ''
    for col in ['Address no of your workplace', 'Soi/Alley of your workplace']:
        if pd.isnull(row[col]):
            continue
        text = str(row[col])
        # Check for keywords indicating a building name
        if any(keyword in text.lower() for keyword in ['building', 'tower', 'อาคาร', 'คอนโด', 'โรงงาน']):
            building_name = text
            break
    return building_name


def get_work_zipcode(df_data):
    # Retrieve the Series of work statuses
    work_status_series = get_work_status_series(df_data)

    def check_work_zipcode_work(row):
        # Get the work status for the current row
        work_status = str(work_status_series.loc[row.name])

        # Get the Zip code of your workplace, defaulting to empty string if missing
        work_zipcode_work = row.get('Zip code of your workplace', '')

        # Apply the specified condition
        if work_status in ['3', '4']:
            # If work_status is '3' or '4', return empty string
            mapped_value = ''
        else:
            # Otherwise, return the original organization name
            mapped_value = work_zipcode_work
        return mapped_value

    # Apply the function to each row in the DataFrame
    work_zipcode_work_series = df_data.apply(check_work_zipcode_work, axis=1)
    return work_zipcode_work_series


def get_work_country_series(df_data):
    country_mapping = {
        'Thailand': 'TH',
        'ไทย': 'TH',
        'Bangkok': 'TH',
        'Bkk': 'TH',
        'ประเทศไทย': 'TH',
        'thailand': 'TH',
        'Thai': 'TH',
        'thailand ': 'TH',
        'Thailand ': 'TH',
        'Thailand  ': 'TH',
        'Thai land': 'TH',
        'Thailand\n': 'TH',
        'Cambodia': 'KH',
        'Singapore': 'SG',
        'Qatar': 'QA',
        'Australia': 'AU',
        'China': 'CN',
        'India': 'IN',
        'United Kingdom': 'GB',
        'UK': 'GB',
        'USA': 'US',
        'United States': 'US',
        'Saudi Arabia': 'SA',
        'Mauritania': 'MR',
        'Cambodia\n': 'KH',
        'Singapore\n': 'SG',
        'China\n': 'CN',
        'India\n': 'IN',
        'Bangkok\n': 'TH',
        'Work from home': '',
        'Depends on filming site': '',
        'Idk': '',
        'No': '',
        '-': '',
        '.': '',
        'No\n': '',
        'No ': '',
        'No  ': '',
        'No\n\n': '',
        'No\n\n\n': '',
        'No (Not match with your qualification/ability)': '',
        'Not matching with the life style': '',
        'Still not sure, currently on probation': '',
        'Cant say much only 3 days pass': '',
        'Still waiting to start': '',
        'Need more money': '',
        'I signed an NDA': '',
        'Work from home\n': '',
        # เพิ่มเติมตามความจำเป็น
    }

    def map_country_code(row):
        response = str(row['Country of your workplace']).strip()
        return country_mapping.get(response, '')

    country_code_series = df_data.apply(map_country_code, axis=1)
    return country_code_series


def get_work_tel(df_data):
    # Retrieve the Series of work statuses
    work_status_series = get_work_status_series(df_data)

    def check_work_tel(row):
        # Get the work status for the current row
        work_status = str(work_status_series.loc[row.name])

        # Get the Tel of your workplace, defaulting to empty string if missing
        work_tel = row.get('Tel of your workplace', '')

        # Apply the specified condition
        if work_status in ['3', '4']:
            # If work_status is '3' or '4', return empty string
            mapped_value = ''
        else:
            # Otherwise, return the original organization name
            mapped_value = work_tel
        return mapped_value

    # Apply the function to each row in the DataFrame
    work_tel_series = df_data.apply(check_work_tel, axis=1)
    return work_tel_series


def get_work_fax(df_data):
    # Retrieve the Series of work statuses
    work_status_series = get_work_status_series(df_data)

    def check_work_fax(row):
        # Get the work status for the current row
        work_status = str(work_status_series.loc[row.name])

        # Get the Fax of your workplace, defaulting to empty string if missing
        work_fax = row.get('Fax of your workplace', '')

        # Apply the specified condition
        if work_status in ['3', '4']:
            # If work_status is '3' or '4', return empty string
            mapped_value = ''
        else:
            # Otherwise, return the original organization name
            mapped_value = work_fax
        return mapped_value

    # Apply the function to each row in the DataFrame
    work_fax_series = df_data.apply(check_work_fax, axis=1)
    return work_fax_series


def get_work_email(df_data):
    # Retrieve the Series of work statuses
    work_status_series = get_work_status_series(df_data)

    def check_work_email(row):
        # Get the work status for the current row
        work_status = str(work_status_series.loc[row.name])

        # Get the Email of your workplace, defaulting to empty string if missing
        work_email = row.get('Email of your workplace', '')

        # Apply the specified condition
        if work_status in ['3', '4']:
            # If work_status is '3' or '4', return empty string
            mapped_value = ''
        else:
            # Otherwise, return the original organization name
            mapped_value = work_email
        return mapped_value

    # Apply the function to each row in the DataFrame
    work_email_series = df_data.apply(check_work_email, axis=1)
    return work_email_series


def get_work_salary(df_data):
    # Retrieve the Series of work statuses
    work_status_series = get_work_status_series(df_data)

    def check_work_salary(row):
        # Get the work status for the current row
        work_status = str(work_status_series.loc[row.name])

        # Get the Monthly salary or earned income, defaulting to empty string if missing
        work_salary = row.get('Monthly salary or earned income', '')

        # Apply the specified condition
        if work_status in ['3', '4']:
            # If work_status is '3' or '4', return empty string
            mapped_value = ''
        else:
            # Otherwise, return the original organization name
            mapped_value = work_salary
        return mapped_value

    # Apply the function to each row in the DataFrame
    work_salary_series = df_data.apply(check_work_salary, axis=1)
    return work_salary_series


def get_work_satisfy_series(df_data):
    mapping = {
        'Yes': '01',
        'No (Undesirable working system)': '02',
        'No (Undesirable co-worker)': '03',
        'No (Not match with your qualification/ability)': '04',
        'No (Little payment)': '05',
        'No (No stability)': '06',
        'No (No opportunity for promotion)': '07',
    }

    # Call the get_work_status_series function to get the Series of work statuses
    work_status_series = get_work_status_series(df_data)

    def map_response(row):
        # Get the work status and response, handling missing values
        work_status = str(work_status_series.loc[row.name])
        response = row.get('Are you satisfied with your work?', '')

        # Convert response to string and handle missing values
        response = str(response).strip() if pd.notna(response) else ''

        # Check if work_status is '3' or '4', return empty string if so
        if work_status in ['3', '4']:
            return ''
        else:
            # Proceed to map the response
            # Handle responses that match directly
            if response in mapping:
                return mapping[response]

            # Handle specific cases with key phrases
            elif 'Not match with your qualification' in response or 'want to change field' in response or 'career goal' in response:
                return '04'
            elif 'Little payment' in response or 'Need more money' in response:
                return '05'
            elif 'No stability' in response:
                return '06'
            elif 'No opportunity for promotion' in response or 'pursue a bigger career path' in response:
                return '07'
            elif 'Undesirable working system' in response or 'work-life balance' in response or 'workplace and environment' in response:
                return '02'
            elif 'Undesirable co-worker' in response:
                return '03'
            elif response == 'Not really':
                return '00'
            else:
                # Default to '00' for Others
                return '00'

    # Apply the function row-wise
    work_satisfy_series = df_data.apply(map_response, axis=1)
    return work_satisfy_series


def get_satisfaction_text(df_data):
    # Get the satisfaction series
    satisfaction_series = get_work_satisfy_series(df_data)
    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_satisfaction_text(row):
        work_status = str(work_status_series.loc[row.name])
        satisfaction_code = satisfaction_series.loc[row.name]

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            return ''
        elif satisfaction_code == '00':
            # Return the original response if satisfaction code is '00' (Others)
            return row['Are you satisfied with your work?']
        else:
            # Otherwise, return empty string
            return ''

    # Apply the function to each row
    mapped_value = df_data.apply(map_satisfaction_text, axis=1)
    return mapped_value


def get_time_findwork_series(df_data):
    time_mapping = {
        '1 - 2 months': '02',
        '10 - 12 months': '05',
        '3 - 6 months': '03',
        '7 - 9 months': '04',
        'an old job (have been working there even before or during the university study)': '07',
        'getting a job immediately': '01',
        'over 1 year': '06',
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_time_findwork(row):
        work_status = str(work_status_series.loc[row.name])

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            return ''
        else:
            response = row['After you graduated, how long did it take you to get a job?']
            return time_mapping.get(response, '')

    time_findwork_series = df_data.apply(map_time_findwork, axis=1)
    return time_findwork_series


def get_match_edu_series(df_data):
    mapping = {
        'yes': '1',
        'no': '2',
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_response(row):
        work_status = str(work_status_series.loc[row.name])

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            return ''
        else:
            response = row['Have you worked in the field that you graduated?']
            return mapping.get(response, '')

    match_edu_series = df_data.apply(map_response, axis=1)
    return match_edu_series


def get_apply_edu_series(df_data):
    mapping = {
        'To a very great extent': '01',
        'To a great extent': '02',
        'To a moderate extent': '03',
        'A little': '04',
        'Very little': '05',
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_response(row):
        work_status = str(work_status_series.loc[row.name])

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            return ''
        else:
            response = row['How can you apply your knowledge to your work?'].strip()
            return mapping.get(response, '')

    apply_edu_series = df_data.apply(map_response, axis=1)
    return apply_edu_series


def get_cause_nowork_with_details(df_data):
    cause_nowork = {
        "Could not find a job": 1,
        "Currently a freelancer and seeking a suitable job at the same time": 4,
        "Currently studying Chinese": 1,
        "Don’t want to work now": 1,
        "Family business": 1,
        "Freelancer": 4,
        "Giving CFA exam in November": 1,
        "Gonna make my own business. I'm currently in the process of learning many things before open.": 4,
        "I work for my own manufacturer but I don’t have legitimate org. info yet": 4,
        "Just coming back from work and travel": 1,
        "Learn family business": 1,
        "Looking for different-field jobs": 3,
        "My boss is very busy to assign my tasks": 0,
        "Planning on pursuing a Master’s Degree": 1,
        "Research and waiting for publication before pursuing higher degree": 1,
        "Seeking for specific field (supply chain & logistics) which I don’t have enough experience.": 3,
        "Starting a business": 4,
        "Studying Chinese for a year": 1,
        "Taking rest after previous job": 1,
        "Wait to pursue master degree": 1,
        "Waiting for the application’s result": 2,
        "Willing to be a freelancer": 4,
        "Work contract is finished": 0,
        "Working on personal business": 4
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_response(row):
        work_status = str(work_status_series.loc[row.name])

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            return ''
        else:
            response = row['If you are unemployed, please specify the most significant reasons:']
            return cause_nowork.get(response, '')

    match_edu_series = df_data.apply(map_response, axis=1)
    return match_edu_series


def get_cause_nowork_with_details_text(df_data):
    # Get the cause_nowork_with_details series
    cause_nowork_with_details_series = get_cause_nowork_with_details(df_data)
    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_cause_nowork_with_details_text(row):
        work_status = str(work_status_series.loc[row.name])
        cause_nowork_with_details_code = cause_nowork_with_details_series.loc[row.name]

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            return ''
        elif cause_nowork_with_details_code == '00':
            # Return the original response if cause_nowork_with_details code is '00' (Others)
            return row['If you are unemployed, please specify the most significant reasons:']
        else:
            # Otherwise, return empty string
            return ''

    # Apply the function to each row
    mapped_value = df_data.apply(map_cause_nowork_with_details_text, axis=1)
    return mapped_value


def get_prob_findwork_series(df_data):
    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    # Define the mapping dictionary for exact matches
    exact_mapping = {
        'no': '01',
        'no work to do from my boss and i wait for him because he offer a good outcome': '00',
        'work permit': '00',
        'yes - being an expat it is difficult due to not having a work visa upon completing undergraduate studies.': '00',
        'yes (could not find a desired job)': '03',
        'yes (could not pass an examination)': '09',
        'yes (health issues)': '10',
        'yes (lack information on job availability)': '02',
        'yes (lack of experience)': '13',
        'yes (lack personal or financial guarantors)': '06',
        'yes (lack personal support)': '05',
        'yes (little salary)': '08',
        'yes (rejected by an organization)': '07',
        'yes (skill issue)': '11',
        'yes mostly location of the work place is too far from home': '00',
        # Add more exact mappings if necessary
    }

    # Define keywords for partial matches (if any additional mapping needed)
    partial_mapping = {
        # Example: 'visa': '00',  # If you want to capture any response containing 'visa' as '00'
        # Add more partial mappings if necessary
    }

    work_status_series = get_work_status_series(df_data)

    def map_prob_findwork(row):
        """
        Maps a single response to the appropriate PROB_FINDWORK code.

        Parameters:
        - row (pd.Series): A row from the DataFrame.

        Returns:
        - str: The corresponding PROB_FINDWORK code.
        """
        # Retrieve the work_status for the current row
        work_status = str(work_status_series.loc[row.name])

        # If work_status is '3' or '4', set PROB_FINDWORK to '00' (Other)
        if work_status in ['3', '4']:
            return '00'

        # Retrieve and clean the response
        response = str(row['Do you have any problem in getting a job?'])

        # Check for exact match
        if response in exact_mapping:
            return exact_mapping[response]

        # Check for partial matches (if any)
        for keyword, code in partial_mapping.items():
            if keyword in response:
                return code

        # Default to '00' for Others
        return '00'

    # Apply the mapping function to each row
    prob_findwork_series = df_data.apply(map_prob_findwork, axis=1)

    return prob_findwork_series


def get_prob_findwork_text(df_data):
    # Get the prob_findwork series
    prob_findwork_series = get_prob_findwork_series(df_data)
    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_prob_findwork_text(row):
        work_status = str(work_status_series.loc[row.name])
        prob_findwork_code = prob_findwork_series.loc[row.name]

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            return ''
        elif prob_findwork_code == '00':
            # Return the original response if prob_findwork code is '00' (Others)
            return row['Do you have any problem in getting a job?']
        else:
            # Otherwise, return empty string
            return ''

    # Apply the function to each row
    mapped_value = df_data.apply(map_prob_findwork_text, axis=1)
    return mapped_value


def get_workneed_series(df_data):
    # Define the mapping dictionary for exact matches
    exact_mapping = {
        '.': '02',
        'any countries': '02',
        'any country but want to live in a developed city': '02',
        'australia': '02',
        'australia ': '02',  # To handle trailing space
        'australia, new zealand, japan': '02',
        'both': '02',
        'both thailand and overseas': '02',
        'canada': '02',
        'canada, netherland, and england': '02',
        'china': '02',
        'depends': '02',
        'either thailand or overseas in countries such as singapore or hong kong': '02',
        'england': '02',
        'germany, japan': '02',
        'japan': '02',
        'maybe usa but atleast some country where i can get by with speaking english only': '02',
        'new working environment': '02',
        'new zealand': '02',
        'no preference': '02',
        'oversea (usa)': '02',
        'singapore': '02',
        'thailand': '01',
        'uk': '02',
        'usa': '02',
        # Add more exact mappings if necessary
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_workneed(row):
        # Retrieve the work_status for the current row
        work_status = str(work_status_series.loc[row.name])

        # If work_status is '3' or '4', set WORKNEED to '02' (ทำงานต่างประเทศ)
        if work_status in ['3', '4']:
            return '02'

        # Retrieve and clean the response
        response = str(row['Do you prefer to work in Thailand or oversea?  If you prefer to work oversea, please specify the country.'])

        # Check for exact match
        if response in exact_mapping:
            return exact_mapping[response]

        # Default to '02' for Others
        return '02'

    # Apply the mapping function to each row
    workneed_series = df_data.apply(map_workneed, axis=1)

    return workneed_series


def get_workneed_country_series(df_data):
    # Define the country to code mapping based on Nationality table
    country_to_code = {
        'andorra': 'AD',
        'united arab emirates': 'AE',
        'afghanistan': 'AF',
        'antigua and barbuda': 'AG',
        'anguilla': 'AI',
        'albania': 'AL',
        'armenia': 'AM',
        'netherlands antilles': 'AN',
        'angola': 'AO',
        'antarctica': 'AQ',
        'argentina': 'AR',
        'american samoa': 'AS',
        'austria': 'AT',
        'australia': 'AU',
        'aruba': 'AW',
        'land islands': 'AX',
        'azerbaijan': 'AZ',
        'bosnia and herzegovina': 'BA',
        'barbados': 'BB',
        'bangladesh': 'BD',
        'belgium': 'BE',
        'burkina faso': 'BF',
        'bulgaria': 'BG',
        'bahrein': 'BH',
        'burundi': 'BI',
        'benin': 'BJ',
        'bermuda': 'BM',
        'brunei darussalam': 'BN',
        'bolivia': 'BO',
        'brazil': 'BR',
        'bahamas': 'BS',
        'bhutan': 'BT',
        'bouvet island': 'BV',
        'botswana': 'BW',
        'belarus': 'BY',
        'belize': 'BZ',
        'canada': 'CA',
        'cocos (keeling) islands': 'CC',
        'congo, the democratic republic of the': 'CD',
        'central african republic': 'CF',
        'congo': 'CG',
        'switzerland': 'CH',
        "côte d'ivoire": 'CI',
        'cook islands': 'CK',
        'chile': 'CL',
        'cameroon': 'CM',
        'china': 'CN',
        'colombia': 'CO',
        'costa rica': 'CR',
        'serbia and montenegro': 'CS',
        'cuba': 'CU',
        'cape verde': 'CV',
        'christmas island': 'CX',
        'cyprus': 'CY',
        'czech republic': 'CZ',
        'germany': 'DE',
        'djibouti': 'DJ',
        'denmark': 'DK',
        'dominica': 'DM',
        'dominican republic': 'DO',
        'algeria': 'DZ',
        'ecuador': 'EC',
        'estonia': 'EE',
        'egypt': 'EG',
        'western sahara': 'EH',
        'eritrea': 'ER',
        'spain': 'ES',
        'ethiopia': 'ET',
        'finland': 'FI',
        'fiji': 'FJ',
        'falkland islands (malvinas)': 'FK',
        'micronesia, federated states of': 'FM',
        'faroe islands': 'FO',
        'france': 'FR',
        'gabon': 'GA',
        'united kingdom': 'GB',
        'grenada': 'GD',
        'georgia': 'GE',
        'french guiana': 'GF',
        'ghana': 'GH',
        'gibraltar': 'GI',
        'greenland': 'GL',
        'gambia': 'GM',
        'guinea': 'GN',
        'guadeloupe': 'GP',
        'equatorial guinea': 'GQ',
        'greece': 'GR',
        'south georgia and the south sandwich islands': 'GS',
        'guatemala': 'GT',
        'guam': 'GU',
        'guinea-bissau': 'GW',
        'guyana': 'GY',
        'hong kong': 'HK',
        'heard island and mcdonald islands': 'HM',
        'honduras': 'HN',
        'croatia': 'HR',
        'haiti': 'HT',
        'hungary': 'HU',
        'indonesia': 'ID',
        'ireland': 'IE',
        'israel': 'IL',
        'india': 'IN',
        'british indian ocean territory': 'IO',
        'iraq': 'IQ',
        'iran, islamic republic of': 'IR',
        'iceland': 'IS',
        'italy': 'IT',
        'jamaica': 'JM',
        'jordan': 'JO',
        'japan': 'JP',
        'kenya': 'KE',
        'kyrgyzstan': 'KG',
        'cambodia': 'KH',
        'kiribati': 'KI',
        'comoros': 'KM',
        'saint kitts and nevis': 'KN',
        'korea, democratic people\'s republic of': 'KP',
        'korea, republic of': 'KR',
        'kuwait': 'KW',
        'cayman islands': 'KY',
        'kazakhstan': 'KZ',
        'lao people\'s democratic republic': 'LA',
        'lebanon': 'LB',
        'saint lucia': 'LC',
        'liechtenstein': 'LI',
        'sri lanka': 'LK',
        'liberia': 'LR',
        'lesotho': 'LS',
        'lithuania': 'LT',
        'luxembourg': 'LU',
        'latvia': 'LV',
        'libyan arab jamahiriya': 'LY',
        'morocco': 'MA',
        'monaco': 'MC',
        'moldova, republic of': 'MD',
        'madagascar': 'MG',
        'marshall islands': 'MH',
        'macedonia, the former yugoslav republic of': 'MK',
        'mali': 'ML',
        'myanmar': 'MM',
        'mongolia': 'MN',
        'macao': 'MO',
        'northern mariana islands': 'MP',
        'martinique': 'MQ',
        'mauritania': 'MR',
        'montserrat': 'MS',
        'malta': 'MT',
        'mauritius': 'MU',
        'maldives': 'MV',
        'malawi': 'MW',
        'mexico': 'MX',
        'malaysia': 'MY',
        'mozambique': 'MZ',
        'namibia': 'NA',
        'new caledonia': 'NC',
        'niger': 'NE',
        'norfolk island': 'NF',
        'nigeria': 'NG',
        'nicaragua': 'NI',
        'netherlands': 'NL',
        'norway': 'NO',
        'nepal': 'NP',
        'nauru': 'NR',
        'niue': 'NU',
        'new zealand': 'NZ',
        'oman': 'OM',
        'panama': 'PA',
        'peru': 'PE',
        'french polynesia': 'PF',
        'papua new guinea': 'PG',
        'philippines': 'PH',
        'pakistan': 'PK',
        'poland': 'PL',
        'saint pierre and miquelon': 'PM',
        'pitcairn': 'PN',
        'puerto rico': 'PR',
        'palestinian territory, occupied': 'PS',
        'portugal': 'PT',
        'palau': 'PW',
        'paraguay': 'PY',
        'qatar': 'QA',
        'réunion': 'RE',
        'romania': 'RO',
        'russian federation': 'RU',
        'rwanda': 'RW',
        'saudi arabia': 'SA',
        'solomon islands': 'SB',
        'seychelles': 'SC',
        'sudan': 'SD',
        'sweden': 'SE',
        'singapore': 'SG',
        'saint helena': 'SH',
        'slovenia': 'SI',
        'svalbard and jan mayen': 'SJ',
        'slovakia': 'SK',
        'sierra leone': 'SL',
        'san marino': 'SM',
        'senegal': 'SN',
        'somalia': 'SO',
        'suriname': 'SR',
        'sao tome and principe': 'ST',
        'el salvador': 'SV',
        'syria arab republic': 'SY',
        'swaziland': 'SZ',
        'turks and caicos islands': 'TC',
        'chad': 'TD',
        'french southern territories': 'TF',
        'togo': 'TG',
        'thailand': 'TH',
        'tajikistan': 'TJ',
        'tokelau': 'TK',
        'timor-leste': 'TL',
        'turkmenistan': 'TM',
        'tunisia': 'TN',
        'tonga': 'TO',
        'turkey': 'TR',
        'trinidad and tobago': 'TT',
        'tuvalu': 'TV',
        'taiwan, province of china': 'TW',
        'tanzania, united republic of': 'TZ',
        'ukraine': 'UA',
        'uganda': 'UG',
        'united states minor outlying islands': 'UM',
        'united states': 'US',
        'uruguay': 'UY',
        'uzbekistan': 'UZ',
        'vatican city state': 'VA',
        'saint vincent and the grenadines': 'VC',
        'venezuela': 'VE',
        'virgin islands, british': 'VG',
        'virgin islands, u.s.': 'VI',
        'viet nam': 'VN',
        'vanuatu': 'VU',
        'wallis and futuna': 'WF',
        'samoa': 'WS',
        'yemen': 'YE',
        'mayotte': 'YT',
        'south africa': 'ZA',
        'zimbabwe': 'ZW'
        # Add more mappings if necessary
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_response(row):
        work_status = str(work_status_series.loc[row.name])

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            return ''
        else:
            response = row['Do you prefer to work in Thailand or oversea?  If you prefer to work oversea, please specify the country.']
            return country_to_code.get(response, '')

    match_edu_series = df_data.apply(map_response, axis=1)
    return match_edu_series


def get_workneed_position_series(df_data):

    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_response(row):
        work_status = str(work_status_series.loc[row.name])

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            map_data = ''
        else:
            map_data = row['What is your preference position?']

        return map_data

    workneed_position_series = df_data.apply(map_response, axis=1)
    return workneed_position_series


def get_skill_development_series(df_data):

    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_response(row):
        work_status = str(work_status_series.loc[row.name])

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            map_data = ''
        else:
            map_data = row['What is your skills or curriculum that you want to improve?']

        return map_data

    skill_development_series = df_data.apply(map_response, axis=1)
    return skill_development_series


def get_disclosure_agreement(df_data):
    # Define the mapping for exact responses
    disclosure_agreement_mapping = {
        'i am willing to reveal the information for all employers except in insurance and direct sale industry': '3',
        # ยินยอมเปิดเผยข้อมูลยกเว้นนายจ้างประเภทขายประกัน/ขายตรง
        'i am willing to reveal the information for all employers except in workforce industry': '2',
        # ยินยอมเปิดเผยข้อมูลยกเว้นนายจ้างประเภทจ้างเหมาแรงงาน
        'i am willing to reveal the information for all employers except in workforce, insurance and direct sale industry': '4',
        # ยินยอมเปิดเผยข้อมูลยกเว้นนายจ้างประเภทจ้างเหมาแรงงาน และประเภทขายประกัน/ขายตรง
        'i am willing to reveal the information for all employers': '1',  # ยินยอมเปิดเผยข้อมูลต่อนายจ้างทุกประเภท
        'no, i am not willing to reveal any information': '0',  # ไม่ยินยอมเปิดเผยข้อมูล
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_response(row):
        work_status = str(work_status_series.loc[row.name])

        # Check work status condition
        if work_status in ['3', '4']:
            # Return empty string if work status is '3' or '4'
            return ''
        else:
            response = row['Are you willing to reveal this information for employers/organization to applying a job?']
            return disclosure_agreement_mapping.get(response, '')

    match_edu_series = df_data.apply(map_response, axis=1)
    return match_edu_series


def get_required_edu_series(df_data):
    mapping = {
        'Yes': '1',
        'No': '2',
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)

    def map_response(row):
        work_status = str(work_status_series.loc[row.name])

        # Check work status condition
        if work_status in ['2', '4']:
            # Return empty string if work status is '3' or '4'
            return ''
        else:
            response = row['Do you want to continue study?']
            return mapping.get(response, '')

    match_required_series = df_data.apply(map_response, axis=1)
    return match_required_series


def get_level_edu_series(df_data):
    # Mapping from response to LEV_ID
    education_mapping = {
        'graduate diploma': '30',  # ประกาศนียบัตรวิชาชีพชั้นสูง
        'medical degree': '50',    # MD (doctor of medicine) might correspond to ประกาศนียบัตรบัณฑิต
        "master's degree": '60',   # ปริญญาโท
        'a certificate/specialization (which offers higher rate of salary than a doctor’s degree.)': '90',  # ประกาศนียบัตรหรือหลักสูตรเฉพาะ
        "bachelor's degree": '40', # ปริญญาตรี
        'doctoral degree': '80',   # ปริญญาเอก
        'a higher graduate diploma': '70',  # ประกาศนียบัตรบัณฑิตชั้นสูง
        'both masters and certificates (i\'ve always been a certificate chaser lol)': ['60', '90'],  # Both ปริญญาโท and ประกาศนียบัตรหรือหลักสูตรเฉพาะ
        'language': '90',           # Assuming language courses fall under ประกาศนียบัตรหรือหลักสูตรเฉพาะ
        # Add more mappings as needed
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)
    required_edu_series = get_required_edu_series(df_data)


    # Function to map each response to LEV_ID
    def map_response(row):
        # Extract work status and required education columns for the row
        work_status = str(work_status_series.loc[row.name])  # Adjust column name accordingly
        required_edu = str(required_edu_series.loc[row.name])  # Adjust column name accordingly

        # Check work status condition
        if work_status in ['2', '4']:
            return ''  # Skip if work status is 2 or 4
        else:
            if required_edu == '1':
                response = row['What level you want to further your study?']
                mapped_value = education_mapping.get(response, '')
                if isinstance(mapped_value, list):
                    return ','.join(mapped_value)  # Join multiple LEV_IDs with a comma
                else:
                    return mapped_value
            else:
                return ''  # Skip if required education is not '1'

    # Apply the mapping function to each row
    match_required_series = df_data.apply(map_response, axis=1)
    return match_required_series


def get_field_study_series(df_data):
    # กำหนดพจนานุกรมสำหรับการแมปคำตอบเป็นรหัส
    field_study_mapping = {
        'same field of study': '1',       # สาขาวิชาเดิม
        'different field of study': '2',  # สาขาวิชาใหม่
    }

    work_status_series = get_work_status_series(df_data)
    required_edu_series = get_required_edu_series(df_data)

    # ฟังก์ชันสำหรับการแมปคำตอบแต่ละแถว
    def map_field_response(row):
        work_status = str(work_status_series.loc[row.name])  # Adjust column name accordingly
        required_edu = str(required_edu_series.loc[row.name])  # Adjust column name accordingly

        # ตรวจสอบเงื่อนไขสถานะการทำงาน
        if work_status in ['2', '4']:
            return ''
        else:
            if required_edu == '1':
                response = row['What field you want to further your study?']  # สมมติว่า 'Field_Response' เป็นคอลัมน์คำตอบ
                return field_study_mapping.get(response, '')
            else:
                return ''

    match_required_series = df_data.apply(map_field_response, axis=1)
    return match_required_series


def get_program_study_series(df_data):
    # ฟังก์ชันสำหรับการแมปคำตอบแต่ละแถว
    def map_field_response(row):
        # Get the work status series
        field_study_series = get_field_study_series(df_data)

        # ตรวจสอบเงื่อนไขสถานะการทำงาน
        if field_study_series == '2':
            return row['What field you want to further your study?']
        else:
            return ''

    match_required_series = df_data.apply(map_field_response, axis=1)
    return match_required_series


def get_program_study_id_series(df_data):
    # Get the work status series
    field_study_series = get_field_study_series(df_data)
    # ฟังก์ชันสำหรับการแมปคำตอบแต่ละแถว
    def map_field_response(row):
        field_study = str(field_study_series.loc[row.name])  # Adjust column name accordingly

        # ตรวจสอบเงื่อนไขสถานะการทำงาน
        if field_study == '2':
            return row['Please specify field of study.']
        else:
            return ''

    match_required_series = df_data.apply(map_field_response, axis=1)
    return match_required_series


def get_type_univ_series(df_data):
    # Mapping from response to LEV_ID
    university_mapping = {
        'public': '1',  # รัฐบาล
        'private': '2',  # เอกชน
        'overseas': '3'  # ต่างประเทศ
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)
    required_edu_series = get_required_edu_series(df_data)

    # Function to map each response to LEV_ID
    def map_response(row):

        work_status = str(work_status_series.loc[row.name])  # Adjust column name accordingly
        required_edu = str(required_edu_series.loc[row.name])  # Adjust column name accordingly
        # Check work status condition
        if work_status in ['2', '4']:
            return ''
        else:
            if required_edu == '1':
                response = row['What type of university/institute you want to further your study?']
                mapped_value = university_mapping.get(response, '')
                if isinstance(mapped_value, list):
                    return ','.join(mapped_value)  # Join multiple LEV_IDs with a comma
                else:
                    return mapped_value
            else:
                return ''

    # Apply the mapping function to each row
    match_required_series = df_data.apply(map_response, axis=1)
    return match_required_series


def get_cause_edu_series(df_data):
    # Mapping from response to LEV_ID
    reason_mapping = {
        'aim to create a ground-breaking startup that creates a new industry': '0',  # อื่นๆให้ระบุ
        'career requirement': '2',  # งานที่ต้องการต้องใช้วุฒิสูงกว่า ปริญญาตรี
        'convenience of being close to home': '0',  # อื่นๆให้ระบุ
        'higher paid job': '0',  # อื่นๆให้ระบุ
        'i want to grow, but more slowly and with some learned experience this time, instead of forcing my way to a management position as I have done..': '0',
        # อื่นๆให้ระบุ
        'in order to learn new things that can help me get a better job to aid me in having a stable income in the future.': '0',
        # อื่นๆให้ระบุ
        'my own and parents’': '1',  # Combination of parent’s desire and self-desire
        'my own desire': '4',  # เป็นความต้องการของตนเอง
        'not studying': '0',  # อื่นๆให้ระบุ
        'parent’s desire': '1',  # เป็นความต้องการของบิดา/มารดา หรือผู้ปกครอง
        'scholarship acquirement': '3'  # ได้รับทุนศึกษาต่อ
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)
    required_edu_series = get_required_edu_series(df_data)

    # Function to map each response to LEV_ID
    def map_response(row):

        work_status = str(work_status_series.loc[row.name])  # Adjust column name accordingly
        required_edu = str(required_edu_series.loc[row.name])  # Adjust column name accordingly

        # Check work status condition
        if work_status in ['2', '4']:
            return ''
        else:
            if required_edu == '1':
                response = row['What type of university/institute you want to further your study?']
                mapped_value = reason_mapping.get(response, '')
                if isinstance(mapped_value, list):
                    return ','.join(mapped_value)  # Join multiple LEV_IDs with a comma
                else:
                    return mapped_value
            else:
                return ''

    # Apply the mapping function to each row
    match_required_series = df_data.apply(map_response, axis=1)
    return match_required_series


def get_cause_edu_text(df_data):
    # Get the satisfaction series
    cause_edu_series = get_cause_edu_series(df_data)

    def map_satisfaction_text(row):
        cause_edu_code = cause_edu_series.loc[row.name]

        # Check work status condition
        if cause_edu_code == '00':
            # Return the original response if satisfaction code is '00' (Others)
            return row['What are the reasons for furthering your study?']
        else:
            # Otherwise, return empty string
            return ''

    # Apply the function to each row
    mapped_value = df_data.apply(map_satisfaction_text, axis=1)
    return mapped_value


def get_prob_edu_series(df_data):
    # Mapping from response to LEV_ID
    problem_mapping = {
        'all of above': '00',  # Combination of all possible issues and others
        'i want to try working first before committing': '00',  # อื่นๆให้ระบุ
        'lack of self-confidence ;—;': '00',  # อื่นๆให้ระบุ
        'lack of time': '00',  # อื่นๆให้ระบุ
        'lack of time and anchor of responsibility': '00',  # อื่นๆให้ระบุ
        'lack work experience': '00',  # อื่นๆให้ระบุ
        'my passion': '00',  # อื่นๆให้ระบุ
        'no': '01',  # ไม่มีปัญหา
        'seek for scholarship': '00',  # อื่นๆให้ระบุ
        'yes (insufficient institution information)': '02',  # ข้อมูลสถานที่ศึกษาต่อไม่เพียงพอ
        'yes (insufficient required knowledge)': '04',  # ขาดความรู้พื้นฐานในการศึกษาต่อ
        'yes (lack of academic qualifications)': '03',  # คุณสมบัติในการสมัครเรียน
        'yes (lack of financial support and insufficient institution info)': '05',
        # Combination of financial and institutional issues
        'yes (lack of financial support)': '05',  # ขาดแคลนเงินทุน
        'yes, i haven\'t given it much thought and not enough money to pay for it yet.': '05',
        # Financial and unspecified issues
    }

    # Get the work status series
    work_status_series = get_work_status_series(df_data)
    required_edu_series = get_required_edu_series(df_data)

    # Function to map each response to LEV_ID
    def map_response(row):

        work_status = str(work_status_series.loc[row.name])  # Adjust column name accordingly
        required_edu = str(required_edu_series.loc[row.name])  # Adjust column name accordingly

        # Check work status condition
        if work_status in ['2', '4']:
            return ''
        else:
            if required_edu == '1':
                response = row['What type of university/institute you want to further your study?']
                mapped_value = problem_mapping.get(response, '')
                if isinstance(mapped_value, list):
                    return ','.join(mapped_value)  # Join multiple LEV_IDs with a comma
                else:
                    return mapped_value
            else:
                return ''

    # Apply the mapping function to each row
    match_required_series = df_data.apply(map_response, axis=1)
    return match_required_series


def get_prob_edu_text(df_data):
    # Get the satisfaction series
    cause_edu_series = get_cause_edu_series(df_data)

    def map_satisfaction_text(row):
        cause_edu_code = cause_edu_series.loc[row.name]

        # Check work status condition
        if cause_edu_code == '00':
            # Return the original response if satisfaction code is '00' (Others)
            return row['Do you have any problem in furthering your study?']
        else:
            # Otherwise, return empty string
            return ''

    # Apply the function to each row
    mapped_value = df_data.apply(map_satisfaction_text, axis=1)
    return mapped_value

