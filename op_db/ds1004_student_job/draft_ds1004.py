import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os
from helpers.ds1004_student_job import (get_citizen_id_series,get_work_status_series,get_military_status_series,get_ordinate_status_series,get_occupation_type_series,get_occupation_text,get_talent_id_series,
                                        get_talent_text,get_position_series,get_work_name,get_industry_series,get_address_data,get_work_country_series,get_work_zipcode,get_work_tel,get_work_fax,get_work_email,get_work_salary,
                                        get_work_satisfy_series,get_satisfaction_text,get_time_findwork_series,get_match_edu_series,get_apply_edu_series,get_cause_nowork_with_details,get_cause_nowork_with_details_text,
                                        get_prob_findwork_series,get_prob_findwork_text,get_workneed_series,get_workneed_country_series,get_workneed_position_series,get_skill_development_series,get_disclosure_agreement,
                                        get_required_edu_series,get_level_edu_series,get_field_study_series,get_program_study_id_series,get_type_univ_series,get_cause_edu_series,get_cause_edu_text,get_prob_edu_series,get_prob_edu_text)

data = pd.read_excel(fr'../datasets/ds1004_student_job/MUIC Graduate Employment Survey of Academic Year 2023.xlsx')
df_data = pd.DataFrame(data)
df = pd.DataFrame()
# print(df_data.columns)

# โหลดค่าจากไฟล์ .env
load_dotenv()

engine = create_engine(f"mssql+pyodbc://{os.getenv('SKY_USERNAME')}:{quote(os.getenv('SKY_PASSWORD'))}@{os.getenv('SKY_HOST')}/{os.getenv('SKY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

data_sql = pd.read_sql('select Code,CitizenNumber,Passport from student.Students', engine)
df_sql = pd.DataFrame(data_sql)

df['STD_ID'] = df_data['Student ID-Final']

df['QN_WORK_STATUS'] = get_work_status_series(df_data)
df['QN_MILITARY_STATUS'] = get_military_status_series(df_data)
df['QN_ORDINATE_STATUS'] = get_ordinate_status_series(df_data)
df['QN_OCCUP_TYPE'] = get_occupation_type_series(df_data)
df['QN_OCCUP_TYPE_TXT'] = get_occupation_text(df_data)
df['QN_TALENT_ID'] = get_talent_id_series(df_data)
df['QN_TALENT_TXT'] = get_talent_text(df_data)
df['QN_POS_ID'] = get_position_series(df_data)
df['QN_WORK_NAME'] = get_work_name(df_data)
df['QN_WORKTYPE_ID'] = get_industry_series(df_data)

# สำหรับช้อมูลที่อยู่ที่ทำงาน
mapped_df = get_address_data(df_data)
df = pd.concat([df, mapped_df], axis=1)

df['QN_WORK_COUNTRY_ID'] = get_work_country_series(df_data)
df['QN_WORK_ZIPCODE'] = get_work_zipcode(df_data)
df['QN_WORK_TEL'] = get_work_tel(df_data)
df['QN_WORK_FAX'] = get_work_fax(df_data)
df['QN_WORK_EMAIL'] = get_work_email(df_data)
df['QN_SALARY'] = get_work_salary(df_data)
df['QN_WORK_SATISFY'] = get_work_satisfy_series(df_data)
df['QN_WORK_SATISFY_TXT'] = get_satisfaction_text(df_data)
df['QN_TIME_FINDWORK'] = get_time_findwork_series(df_data)
df['QN_MATCH_EDU'] = get_match_edu_series(df_data)
df['QN_APPLY_EDU'] = get_apply_edu_series(df_data)
df['QN_CAUSE_NOWORK'] = get_cause_nowork_with_details(df_data)
df['QN_CAUSE_NOWORK_TXT'] = get_cause_nowork_with_details_text(df_data)
df['QN_PROB_FINDWORK'] = get_prob_findwork_series(df_data)
df['QN_PROB_FINDWORK_TXT'] = get_prob_findwork_text(df_data)
df['QN_WORKNEED_ID'] = get_workneed_series(df_data)
df['QN_WORKNEED_COUNTRY_ID'] = get_workneed_country_series(df_data)
df['QN_WORKNEED_POSITION'] = get_workneed_position_series(df_data)
df['QN_SKILL_DEVELOPMENT'] = get_skill_development_series(df_data)
df['QN_DISCLOSURE_AGREEMENT_ID'] = get_disclosure_agreement(df_data)
df['QN_REQUIRE_EDU'] = get_required_edu_series(df_data)
df['QN_LEVEL_EDU'] = get_level_edu_series(df_data)
df['QN_PROGRAM_EDU'] = get_field_study_series(df_data)
df['QN_PROGRAM_EDU_ID'] = get_program_study_id_series(df_data)
df['QN_TYPE_UNIV'] = get_type_univ_series(df_data)
df['QN_CAUSE_EDU'] = get_cause_edu_series(df_data)
df['QN_CAUSE_EDU_TXT'] = get_cause_edu_text(df_data)
df['QN_PROB_EDU'] = get_prob_edu_series(df_data)
df['QN_PROB_EDU_TXT'] = get_prob_edu_text(df_data)
df['QN_ADDPROGRAM1'] = ''
df['QN_ADDPROGRAM2'] = ''
df['QN_ADDPROGRAM3'] = ''
df['QN_ADDPROGRAM4'] = ''
df['QN_ADDPROGRAM5'] = ''
df['QN_ADDPROGRAM6'] = ''
df['QN_ADDPROGRAM7'] = ''
df['QN_ADDPROGRAM8'] = ''
df['QN_ADDPROGRAM9'] = ''
df['QN_ADDPROGRAM7_TXT'] = ''
df['QN_COMMENT_PROGRAM'] = df_data['Suggestions regarding course and field of study (optional)']
df['QN_COMMENT_LEARN'] = df_data['Suggestions regarding teaching (optional)']
df['QN_COMMENT_ACTIVITY'] = df_data['Suggestions regarding student development activities (optional)']
df['QN_DATE_UPDATE'] = ''

# เรียกใช้ฟังก์ชันจาก helper
df['CITIZEN_ID'] = get_citizen_id_series(df_data, df_sql)

df['QY_YEAR'] = '2567'
df['UNIV_ID'] = '00600'

column_order = [
    'QY_YEAR', 'CITIZEN_ID', 'UNIV_ID', 'STD_ID', 'QN_WORK_STATUS',
    'QN_MILITARY_STATUS', 'QN_ORDINATE_STATUS', 'QN_OCCUP_TYPE',
    'QN_OCCUP_TYPE_TXT', 'QN_TALENT_ID', 'QN_TALENT_TXT', 'QN_POS_ID',
    'QN_WORK_NAME', 'QN_WORKTYPE_ID', 'QN_WORK_ADD', 'QN_WORK_MOO',
    'QN_WORK_BUILDING', 'QN_WORK_SOI', 'QN_WORK_STREET', 'QN_WORK_TAMBON',
    'QN_WORK_COUNTRY_ID', 'QN_WORK_ZIPCODE', 'QN_WORK_TEL', 'QN_WORK_FAX',
    'QN_WORK_EMAIL', 'QN_SALARY', 'QN_WORK_SATISFY', 'QN_WORK_SATISFY_TXT',
    'QN_TIME_FINDWORK', 'QN_MATCH_EDU', 'QN_APPLY_EDU', 'QN_CAUSE_NOWORK',
    'QN_CAUSE_NOWORK_TXT', 'QN_PROB_FINDWORK', 'QN_PROB_FINDWORK_TXT',
    'QN_WORKNEED_ID', 'QN_WORKNEED_COUNTRY_ID', 'QN_WORKNEED_POSITION',
    'QN_SKILL_DEVELOPMENT', 'QN_DISCLOSURE_AGREEMENT_ID', 'QN_REQUIRE_EDU',
    'QN_LEVEL_EDU', 'QN_PROGRAM_EDU', 'QN_PROGRAM_EDU_ID', 'QN_TYPE_UNIV',
    'QN_CAUSE_EDU', 'QN_CAUSE_EDU_TXT', 'QN_PROB_EDU', 'QN_PROB_EDU_TXT',
    'QN_ADDPROGRAM1', 'QN_ADDPROGRAM2', 'QN_ADDPROGRAM3', 'QN_ADDPROGRAM4',
    'QN_ADDPROGRAM5', 'QN_ADDPROGRAM6', 'QN_ADDPROGRAM7', 'QN_ADDPROGRAM8',
    'QN_ADDPROGRAM9', 'QN_ADDPROGRAM7_TXT', 'QN_COMMENT_PROGRAM',
    'QN_COMMENT_LEARN', 'QN_COMMENT_ACTIVITY', 'QN_DATE_UPDATE'
]

df = df[column_order]
print(df.head())
# Save to Excel
file_path = 'output_v1.xlsx'
df.to_excel(file_path, index=False)

print(f"Data saved to {file_path}")