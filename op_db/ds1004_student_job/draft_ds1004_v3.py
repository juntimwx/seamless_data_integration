import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os
import helpers_v3

data = pd.read_excel('../../data/op_db/data/ds1004_student_job/Final_ภาวะมีงานทำปี 2565_2025-02-03.xlsx')
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

df['CITIZEN_ID'] = helpers_v3.get_citizen_id_series(df_data, df_sql)
df['UNIV_ID'] = '00600'
df['STD_ID'] = df_data['Student ID']
df['QN_WORK_STATUS'] = helpers_v3.get_work_status_series(df_data)
df['QN_MILITARY_STATUS'] = helpers_v3.get_military_status_series(df_data, df_sql)
df['QN_ORDINATE_STATUS'] = helpers_v3.get_ordinate_status_series(df_data)
df['QN_OCCUP_TYPE'] = helpers_v3.get_occup_type_seties(df_data)
df['QN_OCCUP_TYPE_TXT'] = helpers_v3.get_occup_type_text(df_data)
df['QN_TALENT_ID'] = helpers_v3.get_talent_series(df_data)
df['QN_TALENT_TXT'] = helpers_v3.get_talent_text(df_data)
df['QN_POS_ID'] = helpers_v3.get_position_type_series(df_data)
df['QN_WORK_NAME'] = helpers_v3.get_work_name_text(df_data)
df['QN_WORKTYPE_ID'] = helpers_v3.get_work_type_series(df_data)
df['QN_WORK_ADD'] = helpers_v3.get_work_address_text(df_data)
df['QN_WORK_MOO'] = helpers_v3.get_work_address_moo_text(df_data)
df['QN_WORK_BUILDING'] = helpers_v3.get_work_address_building_info(df_data)
df['QN_WORK_SOI'] = helpers_v3.get_work_address_soi(df_data)
df['QN_WORK_STREET'] = helpers_v3.get_work_address_road_info(df_data)
df['QN_WORK_TAMBON'] = helpers_v3.get_work_address_subdistrict(df_data)
df['QN_WORK_COUNTRY_ID'] = helpers_v3.get_work_address_country(df_data)
df['QN_WORK_ZIPCODE'] = helpers_v3.get_work_address_postal_code(df_data)
df['QN_WORK_TEL'] = helpers_v3.get_work_tel_text(df_data)
df['QN_WORK_FAX'] = ''
df['QN_WORK_EMAIL'] = helpers_v3.get_work_email_text(df_data)
df['QN_SALARY'] = helpers_v3.get_work_salary_text(df_data)
df['QN_WORK_SATISFY'] = helpers_v3.get_satisfy_type_series(df_data)
df['QN_WORK_SATISFY_TXT'] = helpers_v3.get_satisfy_text(df_data)
df['QN_TIME_FINDWORK'] = helpers_v3.get_time_find_work_series(df_data)
df['QN_MATCH_EDU'] = helpers_v3.get_match_education_series(df_data)
df['QN_APPLY_EDU'] = helpers_v3.get_apply_education_series(df_data)
df['QN_CAUSE_NOWORK'] = helpers_v3.get_cause_nowork_series(df_data)
df['QN_CAUSE_NOWORK_TXT'] = helpers_v3.get_cause_nowork_text(df_data)
df['QN_PROB_FINDWORK'] = helpers_v3.get_problem_find_work_series(df_data)
df['QN_PROB_FINDWORK_TXT'] = helpers_v3.get_problem_find_work_text(df_data)
df['QN_WORKNEED_ID'] = helpers_v3.get_work_series(df_data)
df['QN_WORKNEED_COUNTRY_ID'] = helpers_v3.get_work_series(df_data)
df['QN_WORKNEED_POSITION'] = helpers_v3.get_work_country_series(df_data)
df['QN_SKILL_DEVELOPMENT'] = helpers_v3.get_skill_development_text(df_data)
df['QN_DISCLOSURE_AGREEMENT_ID'] = helpers_v3.get_disclosure_agreement_text(df_data)
df['QN_REQUIRE_EDU'] = helpers_v3.get_require_education_series(df_data)
df['QN_LEVEL_EDU'] = helpers_v3.get_level_education_series(df_data)
df['QN_PROGRAM_EDU'] = helpers_v3.get_program_education_series(df_data)
df['QN_PROGRAM_EDU_ID'] = helpers_v3.get_program_education_id_series(df_data)
df['QN_TYPE_UNIV'] = helpers_v3.get_type_university_series(df_data)
df['QN_CAUSE_EDU'] = helpers_v3.get_cause_education_series(df_data)
df['QN_CAUSE_EDU_TXT'] = helpers_v3.get_cause_education_text(df_data)
df['QN_PROB_EDU'] =helpers_v3.get_problem_education_series(df_data)
df['QN_PROB_EDU_TXT'] = helpers_v3.get_problem_education_text(df_data)
# df['QN_ADDPROGRAM1']
# df['QN_ADDPROGRAM2']
# df['QN_ADDPROGRAM3']
# df['QN_ADDPROGRAM4']
# df['QN_ADDPROGRAM5']
# df['QN_ADDPROGRAM6']
# df['QN_ADDPROGRAM7']
# df['QN_ADDPROGRAM8']
# df['QN_ADDPROGRAM9']
# df['QN_ADDPROGRAM7_TXT']
df['QN_COMMENT_PROGRAM'] = df_data['Suggestions regarding course and field of study (optional)']
df['QN_COMMENT_LEARN'] = df_data['Suggestions regarding teaching (optional)']
df['QN_COMMENT_ACTIVITY'] = df_data['Suggestions regarding student development activities (optional)']
# df['QN_DATE_UPDATE']

df['QY_YEAR'] = '2567'

print(df.head(5))

df.to_excel('~/Downloads/draft_ds1004.xlsx')