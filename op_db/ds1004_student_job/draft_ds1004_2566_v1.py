import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os
import helpers_2566_v1, helpers_add_column
from datetime import datetime

data = pd.read_excel('../../data/op_db/data/ds1004_student_job/MUIC Graduate Employment Survey of Academic Year 2023.xlsx')
df_data = pd.DataFrame(data)

df_data.rename(columns={'Position ': 'Position','Industry ':'Industry'}, inplace=True)


df = pd.DataFrame()

# โหลดค่าจากไฟล์ .env
load_dotenv()

engine = create_engine(f"mssql+pyodbc://{os.getenv('SKY_USERNAME')}:{quote(os.getenv('SKY_PASSWORD'))}@{os.getenv('SKY_HOST')}/{os.getenv('SKY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

data_sql = pd.read_sql('''
    select 
        Code
        --,Gender
        ,case when Gender = 1 then 'male'
            when Gender = 2 then 'female'
            else 'not specified' end as Gender
        ,CitizenNumber
        ,Passport 
    from student.Students
''', engine)
df_sql = pd.DataFrame(data_sql)

df['CITIZEN_ID'] = helpers_2566_v1.get_citizen_id_series(df_data, df_sql)
df['UNIV_ID'] = '00600'
df['STD_ID'] = df_data['Student ID-Final']
df['QN_WORK_STATUS'] = helpers_2566_v1.get_work_status_series(df_data)
df['QN_MILITARY_STATUS'] = helpers_2566_v1.get_military_status_series(df_data, df_sql)
df['QN_ORDINATE_STATUS'] = helpers_2566_v1.get_ordinate_status_series(df_data)
df['QN_OCCUP_TYPE'] = helpers_2566_v1.get_occup_type_series(df_data)
df['QN_OCCUP_TYPE_TXT'] = helpers_2566_v1.get_occup_type_text(df_data)
df['QN_TALENT_ID'] = helpers_2566_v1.get_talent_series(df_data)
df['QN_TALENT_TXT'] = helpers_2566_v1.get_talent_text(df_data)
# df['QN_POS_ID'] = helpers_2566_v1.get_position_type_series(df_data)
df['QN_WORK_NAME'] = helpers_2566_v1.get_work_name_text(df_data)
df['QN_WORKTYPE_ID'] = helpers_2566_v1.get_work_type_series(df_data)
# df['QN_WORK_ADD'] = helpers_2566_v1.get_work_address_name_text(df_data)
# df['QN_WORK_MOO'] = helpers_2566_v1.get_work_address_moo_text(df_data)
# df['QN_WORK_BUILDING'] = helpers_2566_v1.get_work_address_building_text(df_data)
df['QN_WORK_SOI'] = helpers_2566_v1.get_work_address_soi_text(df_data)
df['QN_WORK_STREET'] = helpers_2566_v1.get_work_address_street_text(df_data)
df['QN_WORK_TAMBON'] = helpers_2566_v1.get_work_address_tambon_text(df_data)
df['district'] = helpers_2566_v1.get_work_address_district(df_data)
df['province'] = helpers_2566_v1.get_work_address_province(df_data)
df['QN_WORK_COUNTRY_ID'] = helpers_2566_v1.get_work_address_country_series(df_data)
df['QN_WORK_ZIPCODE'] = helpers_2566_v1.get_work_address_zipcode_text(df_data)
df['QN_WORK_TEL'] = helpers_2566_v1.get_work_tel_text(df_data)
df['QN_WORK_FAX'] = helpers_2566_v1.get_work_fax_text(df_data)
df['QN_WORK_EMAIL'] = helpers_2566_v1.get_work_email_text(df_data)
df['QN_SALARY'] = helpers_2566_v1.get_work_salary_text(df_data)
df['QN_WORK_SATISFY'] = helpers_2566_v1.get_satisfy_type_series(df_data)
df['QN_WORK_SATISFY_TXT'] = helpers_2566_v1.get_satisfy_text(df_data)
df['QN_TIME_FINDWORK'] = helpers_2566_v1.get_time_find_work_series(df_data)
df['QN_MATCH_EDU'] = helpers_2566_v1.get_match_education_series(df_data)
df['QN_APPLY_EDU'] = helpers_2566_v1.get_apply_education_series(df_data)
df['QN_CAUSE_NOWORK'] = helpers_2566_v1.get_cause_nowork_series(df_data)
df['QN_CAUSE_NOWORK_TXT'] = helpers_2566_v1.get_cause_nowork_text(df_data)
df['QN_PROB_FINDWORK'] = helpers_2566_v1.get_problem_find_work_series(df_data)
df['QN_PROB_FINDWORK_TXT'] = helpers_2566_v1.get_problem_find_work_text(df_data)

df['QN_WORKNEED_ID'] = helpers_2566_v1.get_workneed_series(df_data)
df['QN_WORKNEED_COUNTRY_ID'] = helpers_2566_v1.get_work_country_series(df_data)
df['QN_WORKNEED_POSITION'] = helpers_2566_v1.get_work_position_series(df_data)
df['QN_SKILL_DEVELOPMENT'] = helpers_2566_v1.get_skill_development_text(df_data)
df['QN_DISCLOSURE_AGREEMENT_ID'] = helpers_2566_v1.get_disclosure_agreement_text(df_data)
df['QN_REQUIRE_EDU'] = helpers_2566_v1.get_require_education_series(df_data)
df['QN_LEVEL_EDU'] = helpers_2566_v1.get_level_education_series(df_data)
df['QN_PROGRAM_EDU'] = helpers_2566_v1.get_program_education_series(df_data)
# df['QN_PROGRAM_EDU_ID'] = helpers_v3.get_program_education_id_series(df_data)
df['QN_TYPE_UNIV'] = helpers_2566_v1.get_type_university_series(df_data)
df['QN_CAUSE_EDU'] = helpers_2566_v1.get_cause_education_series(df_data)
df['QN_CAUSE_EDU_TXT'] = helpers_2566_v1.get_cause_education_text(df_data)
# df['QN_PROB_EDU'] = helpers_v3.get_problem_education_series(df_data)
# df['QN_PROB_EDU_TXT'] = helpers_v3.get_problem_education_text(df_data)
df['QN_ADDPROGRAM1'] = helpers_2566_v1.get_parse_program_data(df_data)['QN_ADDPROGRAM1']
df['QN_ADDPROGRAM2'] = helpers_2566_v1.get_parse_program_data(df_data)['QN_ADDPROGRAM2']
df['QN_ADDPROGRAM3'] = helpers_2566_v1.get_parse_program_data(df_data)['QN_ADDPROGRAM3']
df['QN_ADDPROGRAM4'] = helpers_2566_v1.get_parse_program_data(df_data)['QN_ADDPROGRAM4']
df['QN_ADDPROGRAM5'] = helpers_2566_v1.get_parse_program_data(df_data)['QN_ADDPROGRAM5']
df['QN_ADDPROGRAM6'] = helpers_2566_v1.get_parse_program_data(df_data)['QN_ADDPROGRAM6']
df['QN_ADDPROGRAM7'] = helpers_2566_v1.get_parse_program_data(df_data)['QN_ADDPROGRAM7']
df['QN_ADDPROGRAM8'] = helpers_2566_v1.get_parse_program_data(df_data)['QN_ADDPROGRAM8']
df['QN_ADDPROGRAM9'] = helpers_2566_v1.get_parse_program_data(df_data)['QN_ADDPROGRAM9']
df['QN_ADDPROGRAM7_TXT'] = helpers_2566_v1.get_parse_program_data(df_data)['QN_ADDPROGRAM7_TXT']
df['QN_COMMENT_PROGRAM'] = df_data['Suggestions regarding course and field of study (optional)']
df['QN_COMMENT_LEARN'] = df_data['Suggestions regarding teaching (optional)']
df['QN_COMMENT_ACTIVITY'] = df_data['Suggestions regarding student development activities (optional)']

df['QY_YEAR'] = '2567'

# ใช้ list comprehension
df = df[['QY_YEAR'] + [col for col in df.columns if col != 'QY_YEAR']]

print(df.head(15))

df.to_excel(f'~/Downloads/draft_ds1004_2566_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx')