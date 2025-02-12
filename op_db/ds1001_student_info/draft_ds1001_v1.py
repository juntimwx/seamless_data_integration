import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os
from datetime import datetime

# ------------------------------------------
# 1) โหลดค่าจากไฟล์ .env และเชื่อมต่อ SQL
# ------------------------------------------
load_dotenv()

# สร้าง Engine เพื่อเชื่อมต่อฐานข้อมูล
engine = create_engine(
    f"mssql+pyodbc://{os.getenv('SKY_USERNAME')}:{quote(os.getenv('SKY_PASSWORD'))}"
    f"@{os.getenv('SKY_HOST')}/{os.getenv('SKY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)

# ------------------------------------------
# 2) อ่านข้อมูลจาก Excel
# ------------------------------------------
excel_path = "../../data/op_db/ds1001_student_info/ds1001_from_p-phon.xlsx"
df_data = pd.read_excel(excel_path)

print("Columns in df_data:", df_data.columns)

# ------------------------------------------
# 3) ปรับ type ของ STD_ID ให้ตรงกัน และทำการ Merge
# ------------------------------------------
# df_sql['STD_ID'] = df_sql['STD_ID'].astype(int)
df_data['STD_ID'] = df_data['STD_ID'].astype(str)

std_ids_str = ','.join(map(str, df_data['STD_ID'].tolist()))
# ดึงข้อมูลจาก SQL
query = f'''
    SELECT DISTINCT
        '2567' AS ACADEMIC_YEAR,
        '2' AS SEMESTER,
        '00600' AS UNIV_ID,
        CASE 
            WHEN CitizenNumber IS NOT NULL AND CitizenNumber <> '' THEN CitizenNumber
            ELSE Passport
        END AS CITIZEN_ID,
        std.Code AS STD_ID,
        CASE 
            WHEN std.TitleId = '12' THEN '004'
            WHEN std.TitleId = '14' THEN '003'
        END AS PREFIX_NAME_ID,
        std.FirstNameTh AS STD_FNAME,
        std.MidNameTh AS STD_MNAME,
        std.LastNameTh AS STD_LNAME,
        UPPER(LEFT(std.FirstNameEn, 1)) + LOWER(SUBSTRING(std.FirstNameEn, 2, LEN(std.FirstNameEn))) AS STD_FNAME_EN,
        UPPER(LEFT(std.MidNameEn, 1)) + LOWER(SUBSTRING(std.MidNameEn, 2, LEN(std.MidNameEn))) AS STD_MNAME_EN,
        UPPER(LEFT(std.LastNameEn, 1)) + LOWER(SUBSTRING(std.LastNameEn, 2, LEN(std.LastNameEn))) AS STD_LNAME_EN,
        std.Gender AS GENDER_ID,
        CONVERT(varchar(10), DATEADD(YEAR, 543, std.BirthDate), 23) AS BIRTHDAY_TH,
        '' AS SUB_DISTRICT_ID,
        CASE 
            WHEN nationality.NameEn = 'Thai' THEN 'TH'
            WHEN nationality.NameEn = 'Indian' THEN 'IN'
            WHEN nationality.NameEn = 'Myanmar' THEN 'MM'
            WHEN nationality.NameEn = 'American' THEN 'US'
            WHEN nationality.NameEn = 'Bangladeshi' THEN 'BD'
            WHEN nationality.NameEn = 'Nepalese' THEN 'NP'
            WHEN nationality.NameEn = 'Singaporean' THEN 'SG'
            WHEN nationality.NameEn = 'Polish' THEN 'PL'
            WHEN nationality.NameEn = 'Chinese' THEN 'CN'
            WHEN nationality.NameEn = 'Russian' THEN 'RU'
            WHEN nationality.NameEn = 'Bhutanese' THEN 'BT'
            WHEN nationality.NameEn = 'Taiwanese' THEN 'TW'
            WHEN nationality.NameEn = 'Sudanese' THEN 'SD'
            WHEN nationality.NameEn = 'Korean' THEN 'KR'
            WHEN nationality.NameEn = 'Canadian' THEN 'CA'
            WHEN nationality.NameEn = 'Malaysian' THEN 'MY'
            WHEN nationality.NameEn = 'Japanese' THEN 'JP'
            WHEN nationality.NameEn = 'Cambodian' THEN 'KH'
            WHEN nationality.NameEn = 'Spanish' THEN 'ES'
            WHEN nationality.NameEn = 'South Korean' THEN 'KP'
            WHEN nationality.NameEn = 'British' THEN 'GB'
            WHEN nationality.NameEn = 'Filipino' THEN 'FI'
            WHEN nationality.NameEn = 'Belgian' THEN 'BE'
            WHEN nationality.NameEn = 'German' THEN 'DE'
            WHEN nationality.NameEn = 'French' THEN 'FR'
            WHEN nationality.NameEn = 'Zimbabwean' THEN 'ZW'
            WHEN nationality.NameEn = 'Myanmarian' THEN 'MM'
            WHEN nationality.NameEn = 'Swedish' THEN 'SE'
            WHEN nationality.NameEn = 'Emirati' THEN 'AE'
            WHEN nationality.NameEn = 'Norwegian' THEN 'NO'
            WHEN nationality.NameEn = 'Dutch' THEN 'NL'
            WHEN nationality.NameEn = 'Italian' THEN 'IT'
            WHEN nationality.NameEn = 'Latvian' THEN 'LV'
            WHEN nationality.NameEn = 'Indonesian' THEN 'ID'
            WHEN nationality.NameEn = 'Gabonese' THEN 'GA'
            WHEN nationality.NameEn = 'Swiss' THEN 'CH'
            WHEN nationality.NameEn = 'New Zeland' THEN 'NZ'
            WHEN nationality.NameEn = 'Guinean' THEN 'GN'
            WHEN nationality.NameEn = 'Maldivian' THEN 'MV'
            WHEN nationality.NameEn = 'Danish' THEN 'DK'
            WHEN nationality.NameEn = 'Bruneian' THEN 'BN'
            WHEN nationality.NameEn = 'Australian' THEN 'AU'
            WHEN nationality.NameEn = 'Turkish' THEN 'TR'
            WHEN nationality.NameEn = 'Pakistani' THEN 'PK'
            WHEN nationality.NameEn = 'Malagasy' THEN 'MG'
            WHEN nationality.NameEn = 'Vietnamese' THEN 'VN'
            WHEN nationality.NameEn = 'Austrian' THEN 'AT'
            WHEN nationality.NameEn = 'Salvadoran' THEN 'SV'
            WHEN nationality.NameEn = 'Nigerian' THEN 'NG'
            WHEN nationality.NameEn = 'Moroccan' THEN 'MA'
            WHEN nationality.NameEn = 'Beninese' THEN 'BJ'
            WHEN nationality.NameEn = 'Zambian' THEN 'ZM'
            WHEN nationality.NameEn = 'Philippines' THEN 'PH'
            WHEN nationality.NameEn = 'South African' THEN 'ZA'
            WHEN nationality.NameEn = 'Ukrainian' THEN 'UA'
            WHEN nationality.NameEn = 'Israeli' THEN 'IL'
            WHEN nationality.NameEn = 'Irish' THEN 'IE'
            WHEN nationality.NameEn = 'Laotian' THEN 'LA'
            ELSE nationality.NameEn
        END AS NATIONALITY_ID,
        term.AcademicYear + 543 AS ADMIT_YEAR,
        '00137' AS FAC_ID,
        major_code,
        case when major_code = 'ICIR' then '25290061100177' --หลักสูตรศิลปศาสตรบัณฑิต สาขาวิชาความสัมพันธ์ระหว่างประเทศและกิจการทั่วโลก (หลักสูตรนานาชาติ)
            when major_code = 'ICBI' then '25520061103841' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์ชีวภาพ (หลักสูตรนานาชาติ) มหาวิทยาลัยมหิดล
            when major_code = 'ICBE' then '25500061102072' --หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาเศรษฐศาสตร์ธุรกิจ (หลักสูตรนานาชาติ)  
            when major_code = 'ICMF' then '25450061100862' --หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาการเงิน (หลักสูตรนานาชาติ) 
            when major_code = 'ICMI' then '25450061100783' --หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาธุรกิจระหว่างประเทศ (หลักสูตรนานาชาติ)
            when major_code = 'ICMK' then '25450061100772' --หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาการตลาด(หลักสูตรนานาชาติ)
            when major_code = 'ICCU' then '25570061103047' --หลักสูตรศิลปศาสตรบัณฑิต สาขาวิชาวัฒนธรรมนานาชาติศึกษาและภาษา (หลักสูตรนานาชาติ)
            when major_code = 'ICCS' then '25450061100895' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาการคอมพิวเตอร์ (หลักสูตรนานาชาติ)
            when major_code = 'ICMC' then '25580061100607' --หลักสูตรนิเทศศาสตรบัณฑิต สาขาวิชาสื่อและการสื่อสาร (หลักสูตรนานาชาติ)
            when major_code = 'ICAM' then '25520061103896' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาคณิตศาสตร์ประยุกต์ (หลักสูตรนานาชาติ)
            when major_code = 'ICCI' then '25510061100363' --หลักสูตรวิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์ (หลักสูตรนานาชาติ)
            when major_code = 'ICTB' then '25510061103636' --หลักสูตรการจัดการบัณฑิต สาขาวิชาผู้ประกอบการด้านธุรกิจการเดินทางและธุรกิจบริการ (หลักสูตรนานาชาติ)
            when major_code = 'ICCD' then '25520061100735' --หลักสูตรศิลปกรรมศาสตรบัณฑิต สาขาวิชาการออกแบบนิเทศศิลป์ (หลักสูตรนานาชาติ) มหาวิทยาลัยมหิดล
            when major_code = 'ICCT' then '25630064005206' --หลักสูตรศิลปศาสตรและวิทยาศาสตรบัณฑิต สาขาวิชาเทคโนโลยีสร้างสรรค์ (หลักสูตรนานาชาติ)
            when major_code = 'ICPY' then '25520061103828' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาฟิสิกส์ (หลักสูตรนานาชาติ)
            when major_code = 'ICCH' then '25500061102421' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาเคมี (หลักสูตรนานาชาติ)
            when major_code = 'ICFS' then '25350061100163' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์และเทคโนโลยีการอาหาร (หลักสูตรนานาชาติ)
            when major_code = 'ICTH' then '25661924002001' --หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาการจัดการการท่องเที่ยวและบริการนานาชาติ (หลักสูตรนานาชาติ)
            when major_code = 'ICIH' then '25510061103636' --หลักสูตรการจัดการบัณฑิต สาขาวิชาการจัดการการบริการนานาชาติ (หลักสูตรนานาชาติ) มหาวิทยาลัยมหิดล
	end CURR_ID,
        '1' AS STUDY_TYPE_ID,
        '1' AS STUDY_TIME_ID,
        '1' AS STUDY_REG_ID,
        '1' AS CLASS,
        '0' AS GRAD_STATUS_ID,
        CASE 
            WHEN std.StudentStatus = 's' THEN '1'
            WHEN std.StudentStatus = 'la' THEN '2'
            WHEN std.StudentStatus = 'dm' THEN '3'
            WHEN std.StudentStatus = 'rs' THEN '4'
            ELSE std.StudentStatus 
        END AS STD_STATUS_ID,
        CASE 
            WHEN std.StudentStatus = 'rs' THEN N'ลาออก'
            ELSE '-' 
        END AS TERMINATE_STUDY_CAUSE,
        CASE 
            WHEN gpa IS NULL THEN '0.00'
            ELSE gpa 
        END AS GPA,
        CASE 
            WHEN gpax IS NULL THEN '0.00'
            ELSE gpax 
        END AS GPAX,
        CASE 
            WHEN term_credit.total_regis_credits IS NULL THEN 0
            ELSE term_credit.total_regis_credits
        END AS NUM_CREDIT,
        CASE 
            WHEN total_credit.total_regis_credits IS NULL THEN 0
            ELSE total_credit.total_regis_credits
        END AS ACC_CREDIT,
        '0' AS DEFORM_ID,
        '0' AS FUND_STATUS_ID,
        '-' AS FUND_NAME,
        '-' AS TALENT_ID,
        CASE 
            WHEN std.Passport IS NULL THEN '-'
            WHEN std.Passport = '' THEN '-'
            ELSE std.Passport
        END AS PASSPORT_NUMBER,
        '-' AS PASSPORT_STARTDATE,
        '-' AS PASSPORT_ENDDATE,
        '1' AS DEGREE_NUM
    FROM student.Students std
    JOIN student.StudentAddresses stdAddress ON std.Id = stdAddress.StudentId
    JOIN master.Titles title ON std.TitleId = title.Id
    JOIN master.Nationalities nationality ON std.NationalityId = nationality.Id
    JOIN student.AdmissionInformations admissionInfo ON admissionInfo.StudentId = std.Id
    JOIN master.AdmissionTypes admissionType ON admissionType.Id = admissionInfo.AdmissionTypeId
    JOIN dbo.Terms term ON term.Id = admissionInfo.AdmissionTermId
    JOIN dbo.StagingStudent stagingStudent ON std.Code = stagingStudent.studentCode
    JOIN (
        SELECT
            curriculum.AbbreviationEn AS major_code,
            curriculum.NameEn AS major_name,
            faculty.ShortNameEn AS short_division_name,
            faculty.NameEn AS division_name
        FROM curriculum.Curriculums curriculum
        LEFT JOIN master.Faculties faculty ON faculty.Id = curriculum.FacultyId
    ) major ON SUBSTRING(stagingStudent.programCode, 1, 4) = major.major_code
    OUTER APPLY (
        SELECT 
            StudentId,
            AVG(
                CASE 
                    WHEN registrationCourse.GradeName = 'A'  THEN 4.00
                    WHEN registrationCourse.GradeName = 'B'  THEN 3.00
                    WHEN registrationCourse.GradeName = 'B+' THEN 3.50
                    WHEN registrationCourse.GradeName = 'C'  THEN 2.00
                    WHEN registrationCourse.GradeName = 'C+' THEN 2.50
                    WHEN registrationCourse.GradeName = 'D'  THEN 1.00
                    WHEN registrationCourse.GradeName = 'D+' THEN 1.50
                    WHEN registrationCourse.GradeName = 'F'  THEN 0.00
                END
            ) AS gpa
        FROM registration.RegistrationCourses registrationCourse
        WHERE registrationCourse.TermId = '151'
            AND registrationCourse.GradeName NOT IN ('AU', 'I', 'S', 'T', 'U', 'W', 'X', 't', 'O')
            AND registrationCourse.StudentId = std.Id
        GROUP BY StudentId
    ) gpa
    OUTER APPLY (
        SELECT 
            StudentId,
            AVG(
                CASE 
                    WHEN registrationCourse.GradeName = 'A'  THEN 4.00
                    WHEN registrationCourse.GradeName = 'B'  THEN 3.00
                    WHEN registrationCourse.GradeName = 'B+' THEN 3.50
                    WHEN registrationCourse.GradeName = 'C'  THEN 2.00
                    WHEN registrationCourse.GradeName = 'C+' THEN 2.50
                    WHEN registrationCourse.GradeName = 'D'  THEN 1.00
                    WHEN registrationCourse.GradeName = 'D+' THEN 1.50
                    WHEN registrationCourse.GradeName = 'F'  THEN 0.00
                END
            ) AS gpax
        FROM registration.RegistrationCourses registrationCourse
        WHERE registrationCourse.GradeName NOT IN ('AU', 'I', 'S', 'T', 'U', 'W', 'X', 't', 'O')
            AND registrationCourse.StudentId = std.Id
        GROUP BY StudentId
    ) gpax
    OUTER APPLY (
        SELECT SUM(c.RegistrationCredit) AS total_regis_credits
        FROM registration.RegistrationCourses rc
        JOIN dbo.Courses c ON c.id = rc.CourseId
        JOIN dbo.Terms t ON t.Id = rc.TermId
        WHERE rc.Status <> 'd'
            AND t.AcademicYear = '2024'
            AND t.AcademicTerm = '2'
            AND std.Id = rc.StudentId
    ) term_credit
    OUTER APPLY (
        SELECT SUM(c.RegistrationCredit) AS total_regis_credits
        FROM registration.RegistrationCourses rc
        JOIN dbo.Courses c ON c.id = rc.CourseId
        JOIN dbo.Terms t ON t.Id = rc.TermId
        WHERE rc.Status <> 'd'
            AND std.Id = rc.StudentId
    ) total_credit
    WHERE 
        --std.Code >= '6080037'
        --AND std.Code < '9000000'
        std.Code in ({std_ids_str})
        AND std.StudentStatus IN ('s', 'la', 'ex', 'np', 'rs', 'dm')
        AND admissionType.NameEn NOT IN ('Exchange inbound','Visiting direct application','Visiting agency')
    ORDER BY std.Code
'''
df_sql = pd.read_sql(query, engine)

print(df_sql)

pos_sub = df_sql.columns.get_loc('SUB_DISTRICT_ID')
df_sql = df_sql.drop(columns="SUB_DISTRICT_ID")

df_merged = pd.merge(
    df_sql, 
    df_data[['STD_ID', 'SUB_DISTRICT_ID','ACC_CREDIT']],  # เลือกเฉพาะคอลัมน์ที่จำเป็น
    on='STD_ID', 
    how='left'  # กำหนดรูปแบบการ join
)
col_sub = df_merged.pop('SUB_DISTRICT_ID')  # เอาคอลัมน์ออกมาก่อน
df_merged.insert(pos_sub, 'SUB_DISTRICT_ID', col_sub)

# ถ้าต้องการ fill ค่า NaN หลัง merge:
# df_merged['SUB_DISTRICT_ID'] = df_merged['SUB_DISTRICT_ID'].fillna('-')

# ------------------------------------------
# 4) Export ออกเป็นไฟล์ Excel
# ------------------------------------------
output_filename = os.path.expanduser(
    f"~/Downloads/draft_ds1001_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
)
df_merged.to_excel(output_filename, index=False)
print(f"Data exported to {output_filename}")