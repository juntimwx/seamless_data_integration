import pandas as pd
from helpers.function import extract_year_range,thai_date_to_iso,extract_start_time_range,extract_end_time_range
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os

data = pd.read_excel(r'../data/muic_student_disciplinary/Template_StudentDisciplinary_v.2024.05.20_SA.xlsx')

# โหลดค่าจากไฟล์ .env
load_dotenv()

engine = create_engine(f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('STUDENT_DISCIPLINARY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")
# engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('STUDENT_DISCIPLINARY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

df = pd.DataFrame(data, columns= 
               ['Academic Year', 'Term', 'Date', 'Time', 'Student ID', 'Gender','Firstname', 'Surname', 'Major', 'Code', 'Subject', 'Lecturer name','Type_of_Issue', 
                'Type(Other)', 'Type_of_Exam ', 'No. of regulation','Level_of_Issue', 'Level_of_Punishment', 'Details', 'Location','Educational sanctions', 
                'Disciplimary sanctions', 'Appeal (Yes/No)','Result of Appeal', 'Remark'])

df = df.rename(columns={
    'Academic Year': 'academic_year',
    'Term': 'term',
    'Date': 'disciplinary_date',
    'Time': 'disciplinary_time',
    'Student ID': 'student_id',
    'Gender': 'gender',
    'Firstname': 'first_name',
    'Surname': 'last_name',
    'Major': 'major',
    'Code': 'subject_code',
    'Subject': 'subject_name',
    'Lecturer name': 'lecturer_name',
    'Type_of_Issue': 'type_of_issue',
    'Type(Other)': 'type_other',
    'Type_of_Exam ': 'type_of_exam',
    'No. of regulation': 'regulation_number',
    'Level_of_Issue': 'issue_level',
    'Level_of_Punishment': 'punishment_level',
    'Details': 'details',
    'Location': 'location',
    'Educational sanctions': 'educational_sanctions',
    'Disciplimary sanctions': 'disciplinary_sanctions',
    'Appeal (Yes/No)': 'appeal',
    'Result of Appeal': 'appeal_result',
    'Remark': 'remark'
})

# ลบช่องว่างหน้าหลังของทุกคอลัมน์
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

df['academic_year'] = df['academic_year'].apply(extract_year_range)
df['disciplinary_date'] = df['disciplinary_date'].apply(thai_date_to_iso)
df['disciplinary_time_start'] = df['disciplinary_time'].apply(extract_start_time_range)
df['disciplinary_time_end'] = df['disciplinary_time'].apply(extract_end_time_range)

df['issue_level'] = df['issue_level'].str.split('(').str[0].str.strip()

# ลบคอลัมน์ 'disciplinary_time' หลังจากแยกเวลาแล้ว
df = df.drop('disciplinary_time', axis=1)

print("Dataframe Preview:")
print(df.head())

# try to insert data to database.
try:
    # insert data to database appending new rows.
    result = df.to_sql(os.getenv('SA_DISCIPLINARY_TABLE'), engine, schema=os.getenv('SCHEMA_DEFAULT'), index=False,
                       chunksize=500, if_exists='append')

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