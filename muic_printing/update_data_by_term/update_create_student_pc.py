import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

# for printer
import xmlrpc.client as xmlrpclib

# โหลดค่าจากไฟล์ .env
load_dotenv()

connect_db_printer = create_engine(
    f"postgresql+psycopg2://{quote_plus(os.getenv('PRINTER_USERNAME'))}:"
    f"{quote_plus(os.getenv('PRINTER_PASSWORD'))}@"
    f"{os.getenv('PRINTER_HOST')}/"
    f"{os.getenv('PAPERCUT_DATABASE')}"
)

user_printer_db = pd.read_sql('''
    select usr.user_name,
        usr.full_name,
        account.balance,
        usr.email,
        usr.department,
        usr.office,
        usr.card_number,
        usr.card_number2,
        usr.disabled_printing,
        usr.home_directory,
        usr.notes
    from tbl_user usr
    left join (
        select * from tbl_account  where deleted = 'N'
    ) account on usr.user_name = account.account_name
    where usr.deleted = 'N'
    --disabled_printing = 'N' and 
    --usr.department = 'Student'
    order by usr.department,usr.office
''',connect_db_printer)

print(user_printer_db.head())

connect_db_sky = create_engine(f"mssql+pyodbc://{os.getenv('SKY_USERNAME')}:{quote(os.getenv('SKY_PASSWORD'))}@{os.getenv('SKY_HOST')}/{os.getenv('SKY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

student_status_studying = pd.read_sql('''
    select  std.Code student_code,
            std.FirstNameEn first_name,
            std.LastNameEn last_name,
            case when std.StudentStatus = 'prc'	then 'passed_all_required_course'
                when std.StudentStatus = 'pa'	then 'passed_away'
                when std.StudentStatus = 'rs'	then 'resign'
                when std.StudentStatus = 'dm'	then 'dismissed'
                when std.StudentStatus = 's'	then 'studying'
                when std.StudentStatus = 'la'	then 'leave_of_absence'
                when std.StudentStatus = 'ex'	then 'exchange'
                when std.StudentStatus = 'g'	then 'graduated'
                when std.StudentStatus = 'np'	then 'no_report'
                when std.StudentStatus = 'd'	then 'deleted'
                when std.StudentStatus = 'b'	then 'blacklist'
                when std.StudentStatus = 'tr'	then 'transferred_to_other_university'
                when std.StudentStatus = 're'	then 'reenter'
                when std.StudentStatus = 'ra'	then 're_admission'
                else 'Unknown' end as student_status,
            case when std.StudentStatus = 'prc'	then 'Inactive'
                when std.StudentStatus = 'pa'	then 'Inactive'
                when std.StudentStatus = 'rs'	then 'Inactive'
                when std.StudentStatus = 'dm'	then 'Inactive'
                when std.StudentStatus = 's'	then 'Active'
                when std.StudentStatus = 'la'	then 'Active'
                when std.StudentStatus = 'ex'	then 'Active'
                when std.StudentStatus = 'g'	then 'Inactive'
                when std.StudentStatus = 'np'	then 'Inactive'
                when std.StudentStatus = 'd'	then 'Inactive'
                when std.StudentStatus = 'b'	then 'Inactive'
                when std.StudentStatus = 'tr'	then 'Inactive'
                --when std.StudentStatus = 're'	then 'reenter'
                --when std.StudentStatus = 'ra'	then 're_admission'
                else 'Unknown' end as student_status_2,
            major.Division as division
    from student.Students std
    left join master.Titles title on std.TitleId = title.Id
    left join master.Nationalities nationality on std.NationalityId = nationality.Id
    left join master.ResidentTypes residentType on std.ResidentTypeId = residentType.Id
    left join master.StudentFeeTypes studentFeeType on std.StudentFeeTypeId = studentFeeType.Id
    left join student.AdmissionInformations admissionInfo on std.Id = admissionInfo.StudentId
    left join dbo.Terms term on admissionInfo.AdmissionTermId = term.Id
    left join master.AdmissionTypes admissionType on admissionInfo.AdmissionTermId = admissionType.Id
    left join dbo.StagingStudent stagingStudent on std.Code = stagingStudent.studentCode
    left join dbo.ALLMajor major on SUBSTRING(stagingStudent.programCode,1,4) = major.Major
    where std.StudentStatus = 's'
''',connect_db_sky)

print(student_status_studying.head())


# ใช้ merge เพื่อรวมข้อมูล
merged_data = pd.merge(
    student_status_studying,                  # DataFrame แรก
    user_printer_db,          # DataFrame ที่สอง
    left_on="student_code",              # คีย์ของ DataFrame แรก
    right_on="user_name",          # คีย์ของ DataFrame ที่สอง
    how="left"                        # ประเภทการเชื่อม (left join)
)

# ตรวจสอบผลลัพธ์
print(merged_data.head())

# หากต้องการ export ออกมาเป็นไฟล์ Excel
merged_data.to_excel("~/Downloads/merged_data.xlsx", index=False)

# connect to server
server = xmlrpclib.Server(os.getenv('URL_API'))
auth_token = os.get('AUTH_TOKEN')
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          