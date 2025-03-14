import pandas as pd
import html
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote
from dotenv import load_dotenv
import os

# load variable form .env file. 
load_dotenv()

# create connection engin for database SQL Server.
# engine = create_engine(f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('OP_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")
engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('OP_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

data = pd.read_excel('../../../data/account_student/PC/default_data/all_student_pc_20250225.xlsx')
# data = pd.read_excel('../../../data/account_student/PC/default_data/all_student_mp_20250225.xlsx')
dataStudent = pd.DataFrame(data)

data_status = pd.read_excel('../../../data/account_student/PC/default_data/final_student_status.xlsx')
dataStudentStatus = pd.DataFrame(data_status)

merged_df = pd.merge(dataStudent, dataStudentStatus, on="std_id", how="left")

dataUpdate = pd.DataFrame()

dataUpdate['prefix'] = merged_df['applicant_title']
dataUpdate['name_th'] = merged_df['applicant_nameth']
dataUpdate['lastname_th'] = merged_df['applicant_snameth']
dataUpdate['name_en'] = merged_df['applicant_nameen']
dataUpdate['lastname_en'] = merged_df['applicant_snameen']
dataUpdate['citizen_number'] = merged_df['applicant_idcard']
dataUpdate['birthday'] = merged_df['applicant_dateofbirth']
dataUpdate['student_id'] = merged_df['std_id']
dataUpdate['major_id'] = merged_df['applicant_major']
dataUpdate['student_level'] = merged_df['current_level'].apply(
    lambda x: html.unescape(html.unescape(x.strip())) if isinstance(x, str) else x
)

def getStudentStatusEn(status):
    if status == 'จบการศึกษา':
        statusEn = 'graduated'
    elif status == 'ลาออก':
        statusEn = 'dismissed'
    elif status == 'พ้นสภาพ':
        statusEn = 'leave'
    elif status == 'กำลังศึกษา':
        statusEn = 'studying'
    elif status == 'รักษาสภาพ':
        statusEn = 'leave_of_absence'
    else:
        statusEn = None  # กรณีไม่ตรงกับค่าใดๆ ที่ระบุไว้
    return statusEn
    
dataUpdate['student_status'] = merged_df['student_status'].apply(getStudentStatusEn)

print("Dataframe Preview:")
print(dataUpdate.head())
# try to insert data to database.
try:
    # insert data to database appending new rows.
    result = dataUpdate.to_sql(os.getenv('PC_STUDENT_PC'), engine, schema=os.getenv('SCHEMA_DEFAULT'), index=False, chunksize=1000, if_exists='append')
    # result = dataUpdate.to_sql(os.getenv('PC_STUDENT_MP'), engine, schema=os.getenv('SCHEMA_DEFAULT'), index=False, chunksize=1000, if_exists='append')
    
    # display a message when data inserted successfully and show number of row inserted to database.
    print(f"Data inserted successfully. Number of rows inserted: {len(dataUpdate)}")
    
# handle error such as connection or SQL command issues.
except SQLAlchemyError as e:
    # display a message when data insertion fails.
    print("Failed to insert data into the database.")
    print(f"Error: {e}")
    exit()
except Exception as e:
    # display a message when data insertion fails.
    print("An unexpected error occurred.")
    print(f"Error: {e}")