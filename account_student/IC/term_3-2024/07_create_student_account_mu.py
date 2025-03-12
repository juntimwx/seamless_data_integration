import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote
from dotenv import load_dotenv
import os

# load variable form .env file.
load_dotenv()

# สร้าง connection ไปยังฐานข้อมูล SKY
sky_engine = create_engine(f"mssql+pyodbc://{os.getenv('SKY_USERNAME')}:{quote(os.getenv('SKY_PASSWORD'))}@{os.getenv('SKY_HOST')}/{os.getenv('SKY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")
student_data = pd.read_sql('''
    select
        case when std.TitleId = '17' then '002' --17 นาง
            when std.TitleId in ('12','26','30') or (std.TitleId = '44' and std.Code in ('4880635','5380028')) then '003' -- 12,26,30 นางสาว 44 ไม่ระบุ
            when std.TitleId in ('14','18') then '001' --14,18 นาย
            else 'Not Specified'
        end as 'รหัสคำนำหน้าชื่อ'
        ,case when std.TitleId = '17' then 'Mrs.' --17 นาง
            when std.TitleId in ('12','26','30') or (std.TitleId = '44' and std.Code in ('4880635','5380028')) then 'Ms.' -- 12,26,30 นางสาว 44 ไม่ระบุ
            when std.TitleId in ('14','18') then 'Mr.' --14,18 นาย
            else 'Not Specified'
        end as 'คำนำหน้าชื่อ'
        ,upper(trim(std.FirstNameEn)) as 'ชื่อ(ภาษาไทย)'
        ,upper(trim(std.MidNameEn)) as 'ชื่อกลาง(ภาษาไทย)'
        ,upper(trim(std.LastNameEn)) as 'สกุล(ภาษาไทย)'
        ,upper(trim(std.FirstNameEn)) as 'ชื่อ(ภาษาอังกฤษ)'
        ,upper(trim(std.MidNameEn)) as 'ชื่อกลาง(ภาษาอังกฤษ)'
        ,upper(trim(std.LastNameEn)) as 'สกุล(ภาษาอังกฤษ)'
        ,case when std.Gender = 1 then 'M'
            when std.Gender = 2 or std.Code in ('4880635','5380028') then 'F'
            else 'Not Specified'
        end as 'เพศ'
        ,std.CitizenNumber as 'เลขประจำตัวประชาชน'
        ,std.Passport as 'เลขหนังสือเดินทาง'
        ,format(switchoffset(convert(datetimeoffset, std.BirthDate), '+07:00'),N'dd/MM/yyyy','th-TH') as 'วันเดือนปีเกิด'
        ,std.Code as 'รหัสนักศึกษา'
        ,'IC' as 'รหัสคณะ'
        ,curriculum.AbbreviationEn as 'รหัสหลักสูตร'
        ,curriculumVersion.NameEn
        ,'-' as 'รหัสสาขา'
        ,'0' as 'กลุ่ม'
        ,'B' as 'ระดับการศึกษา'
        ,case when curriculum.AbbreviationEn in ('DTDS','PYPY') then 'take a course with IC'
            when std.StudentStatus = 'prc' then 'passed_all_required_courses'
            when std.StudentStatus = 'pa' then 'passed_away'
            when std.StudentStatus = 'rs' then 'resigned'
            when std.StudentStatus = 'dm' then 'dismissed'
            when std.StudentStatus = 's' then 'studying'
            when std.StudentStatus = 'la' then 'leave_of_absence'
            when std.StudentStatus = 'ex' then 'exchange'
            when std.StudentStatus = 'g' then 'graduated'
            when std.StudentStatus = 'g1' then 'graduated_with_first_class_honors'
            when std.StudentStatus = 'g2' then 'graduated_with_second_class_honors'
            when std.StudentStatus = 'np' then 'no_report'
            when std.StudentStatus = 'd' then 'deleted'
            when std.StudentStatus = 'b' then 'blacklist'
            when std.StudentStatus = 'tr' then 'transferred_to_other_university'
            when std.StudentStatus = 're' then 'reenter'
            when std.StudentStatus = 'ra' then 're_admission'
            else 'Others'
        end as 'สถานภาพนักศึกษา'
    from student.Students std
    left join student.CurriculumInformations curriculumInfo on curriculumInfo.StudentId = std.Id
    inner join curriculum.CurriculumVersions curriculumVersion on curriculumVersion.Id = curriculumInfo.CurriculumVersionId
    inner join curriculum.Curriculums curriculum on curriculum.Id = curriculumVersion.CurriculumId
    where curriculumInfo.IsActive = '1' and (left(std.Code,2) > '49' and left(std.Code,2) < '99')
    order by std.Code
''',sky_engine)

df = pd.DataFrame(student_data)

data_engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('OP2_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

print("Dataframe Preview:")
print(df.head())

# try to insert data to database.
try:
    # insert data to database appending new rows.
    result = df.to_sql(os.getenv('CREATE_ACCOUNT_STUDENT_IC'), data_engine, schema=os.getenv('SCHEMA_DEFAULT'), index=False, chunksize=500, if_exists='replace')
    
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