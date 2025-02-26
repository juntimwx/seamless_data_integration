import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('SMART_EDU_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

data = pd.read_excel('./datasets/smart-edu-student-id-67-t2-24-25.xls')
df = pd.DataFrame(data)

df = df.rename(columns={
    'คำนำหน้าชื่อ' : 'prefix_id',
    'ชื่อ(ภาษาไทย)' : 'firstname_th',
    'ชื่อกลาง(ภาษาไทย)' : 'middle_name_th',
    'สกุล(ภาษาไทย)' : 'lastname_th',
    'ชื่อ(ภาษาอังกฤษ)' : 'firstname_en',
    'ชื่อกลาง(ภาษาอังกฤษ)' : 'middle_name_en',
    'สกุล(ภาษาอังกฤษ)' : 'lastname_en',
    'เพศ' : 'gender',
    'เลขประจำตัวประชาชน' : 'citizen_id',
    'วันเดือนปีเกิด' : 'birthday',
    'รหัสนักศึกษา(กรณีกำหนดมาโดยคณะ)' : 'student_id',
    'รหัสคณะ' : 'faculty_id',
    'รหัสหลักสูตร' : 'curriculum_id',
    'รหัสสาขา' : 'major_id',
    'กลุ่ม' : 'group',
    'ระดับการศึกษา' : 'degree_level',
    'สถานะการศึกษา' : 'education_status',
    'สัญชาติ' : 'nationality',
    'Admission Type' : 'admission_type',
    'Remark' : 'remark',
})

df['birthday'] = df['birthday'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y").strftime("%Y-%m-%d"))


df = df.drop('No.', axis=1)
print(df.head())
df.to_sql('student_info', engine, index=False, chunksize=500, if_exists='append')  #replace
