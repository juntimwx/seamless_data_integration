import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

df = pd.DataFrame()

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
# 6780921

df['ACADEMIC_YEAR'] = '2567'
df['SEMESTER'] = '2'
df['UNIV_ID'] = '00600'
# df['CITIZEN_ID'] = 


# ใช้ list comprehension
df = df[['ACADEMIC_YEAR'] + [col for col in df.columns if col != 'ACADEMIC_YEAR']]


print(df)

