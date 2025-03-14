import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote
from dotenv import load_dotenv
import os

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

# สร้าง connection ไปยังฐานข้อมูล SKY
sky_engine = create_engine(
    f"mssql+pyodbc://{os.getenv('SKY_USERNAME')}:{quote(os.getenv('SKY_PASSWORD'))}@{os.getenv('SKY_HOST')}/{os.getenv('SKY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)
engine = create_engine(f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('CLOUD_DISASTER_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

data = pd.read_sql('''
    select  std.Code student_code,
        title.NameEn as prefix,
        std.FirstNameEn first_name,
        std.LastNameEn last_name,
        case when std.Gender = 1 then 'male'
            when std.Gender = 2 then 'female'
            else 'not specified' end as gender,
        case when nationality.NameEn = 'Myanmar' then 'Burmese'
            when nationality.NameEn = 'Myanmarian' then 'Burmese'
            when nationality.NameEn = 'Other' then 'Not Specified'
            when nationality.NameEn = 'TO_CONFIRM' then 'Not Specified'
            when nationality.NameEn = 'passed_all_required_courses' then 'Not Specified'
            else nationality.NameEn end as 'nationality',
        residentType.NameEn as resident_type,
        studentFeeType.NameEn as student_fee_type,
        term.AcademicYear as academic_year,
        term.AcademicTerm as academic_term,
        admissionType.NameTh as admission_type,
        case when admissionType.Id = 1 then 'Full-time Student' /* IC + Outbound*/
            when admissionType.Id = 1 then 'Exchange Student'  /*Inbound*/
            when admissionType.Id = 1 then 'Exchange Student'  /*Inbound*/
            when admissionType.Id = 1 then 'Exchange Student'  /*Inbound*/
            when admissionType.Id = 1 then 'Full-time Student' /* PC */
            when admissionType.Id = 1 then 'Full-time Student' /* PC */
            when admissionType.Id = 1 then 'Summer'
            else 'External' end as student_type,
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
        SUBSTRING(stagingStudent.programCode,1,4) as major,
        major.NameEn as major_name,
        major.Division as division,
        major.DivisionName as division_name,
        std.IsActive as is_active
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
''',sky_engine)

df = pd.DataFrame(data)

print("Dataframe Preview:")
print(df.head())

# try to insert data to database.
try:
    # insert data to database appending new rows.
    result = df.to_sql(os.getenv('STUDENT_IC_TABLE'), engine, schema=os.getenv('SCHEMA_DEFAULT'), index=False, chunksize=500, if_exists='append')
    
    # display a message when data inserted successfully and show number of row inserted to database.
    print(f"Data inserted successfully. Number of rows inserted: {len(df)}")
    
# handle error such as connection or SQL command issues.
except SQLAlchemyError as e:
    # display a message when data insertion fails.
    print("Failed to insert data into the database.")
    print(f"Error: {e}")
except Exception as e:
    # display a message when data insertion fails.
    print("An unexpected error occurred.")
    print(f"Error: {e}")