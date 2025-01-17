import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

import xmlrpc.client as xmlrpclib

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

# connect to server
server = xmlrpclib.Server(os.getenv('URL_API'))
auth_token = os.getenv('AUTH_TOKEN')

connect_db_printer = create_engine(
    f"postgresql+psycopg2://{quote_plus(os.getenv('PRINTER_USERNAME'))}:"
    f"{quote_plus(os.getenv('PRINTER_PASSWORD'))}@"
    f"{os.getenv('PRINTER_HOST')}/"
    f"{os.getenv('PAPERCUT_DATABASE')}"
)

# ดึงข้อมูล balance printer 
user_printer_db = pd.read_sql('''
    select usr.user_name as code,
        account.balance as balance_add_drop_period,
        usr.department as department,
        usr.office as office
    from tbl_user usr
    left join (
        select * from tbl_account  where deleted = 'N'
    ) account on usr.user_name = account.account_name
    where usr.deleted = 'N'
    --disabled_printing = 'N' and 
    --usr.department = 'Student'
    order by usr.department,usr.office
''', connect_db_printer)

df = pd.DataFrame(user_printer_db)

# สร้างรายการใหม่ที่เก็บผลลัพธ์
output_data = []

# Loop เพื่อคำนวณ group และบันทึกในรูปแบบใหม่
for idx, row in df.iterrows():
    department = row['department']
    office = row['office']
    code = row['code']  # ใช้ code เป็น Column2

    # ข้ามแถวที่ department เป็นค่าว่าง
    if pd.isna(department) or department.strip() == "":
        continue

    # สร้างกลุ่มเริ่มต้นว่าง
    groups = []

    # กำหนดกลุ่มหลักสำหรับแต่ละ department
    if department in ('Lecturer Parttime', 'LecturerParttimePC', 'LecturerPC', 'Staff',
                      'Student Exchange', 'Student Leave of absence', 'StudentPC'):
        groups.append(department)
        if office != 'IT':
            groups.append('bw')  # อยู่ในกลุ่ม 'bw'

    else:
        groups.append(department)  # กลุ่มค่าเริ่มต้น

    # เพิ่มข้อมูลลงใน output_data สำหรับทุกกลุ่มที่อยู่
    for group in groups:
        output_data.append([group, code])

# แปลง output_data เป็น DataFrame
df_output = pd.DataFrame(output_data, columns=['Column 1', 'Column 2'])

# บันทึกเป็นไฟล์ .txt (Tab-Separated) พร้อมหัวตาราง
output_txt_path = "~/Downloads/additional-groups.txt"
df_output.to_csv(output_txt_path, sep='\t', index=False, header=True)
print(f"Data saved to: {output_txt_path}")
