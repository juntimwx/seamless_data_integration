import pandas as pd
from helpers.function import extract_year_range,thai_date_to_iso

from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os

data = pd.read_excel(r'D:\Seamless data integration\analysis_resources\muic_student_disciplinary\datasets\Template_StudentDisciplinary_v.2024.05.20_OAA.xlsx')

# โหลดค่าจากไฟล์ .env
load_dotenv()

engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('STUDENT_DISCIPLINARY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

df = pd.DataFrame(data, columns= 
               ['Academic Year', 'Term', 'Date', 'Time', 'Student ID', 'Gender','Firstname', 'Surname', 'Major', 'Code', 'Subject', 'Lecturer name','Type_of_Issue', 
                'Type(Other)', 'Type_of_Exam ', 'No. of regulation','Level_of_Issue', 'Level_of_Punishment', 'Details', 'Location','Educational sanctions', 
                'Disciplimary sanctions', 'Appeal (Yes/No)','Result of Appeal', 'Remark'])

df = df.rename(columns={
    'Academic Year': 'academic_year',
    'Term': 'term',
    'Date': 'date',
    'Time': 'time',
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


df['academic_year'] = df['academic_year'].apply(extract_year_range)
df['date'] = df['date'].apply(thai_date_to_iso)


print(df)


df.to_sql("oaa_student_disciplinary", engine, index=False, chunksize=500, if_exists='append')