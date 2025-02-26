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
        usr.office as office,
        usr.disabled_printing
    from tbl_user usr
    left join (
        select * from tbl_account  where deleted = 'N'
    ) account on usr.user_name = account.account_name
    where usr.deleted = 'N'
    and disabled_printing = 'Y'  
    --and usr.department = 'Student'
    order by usr.department,usr.office
''', connect_db_printer)

df = pd.DataFrame(user_printer_db)

# สร้างรายการใหม่ที่เก็บผลลัพธ์
output_data = []

# Loop เพื่อคำนวณ group และบันทึกในรูปแบบใหม่
# สร้างรายการใหม่ที่เก็บ log
skipped_logs = []  # เก็บรายการที่ถูกข้าม
success_logs = []  # เก็บรายการที่อัปเดตสำเร็จ
failed_updates = []  # เก็บรายการที่อัปเดตไม่สำเร็จ

# Loop เพื่อคำนวณและอัปเดตข้อมูล
for idx, row in df.iterrows():
    code = row['code']  # ใช้ code เป็น Column2
    disabled_printing = row['disabled_printing']

    # ตรวจสอบว่า user ถูกปิดการพิมพ์หรือไม่
    if disabled_printing != 'Y':
        log_message = f"Skipping code {code}: printing is not disabled."
        print(log_message)
        skipped_logs.append({'code': code, 'reason': log_message})
        continue

    # อัปเดต balance เป็น 0
    try:
        server.api.setUserProperty(auth_token, code, 'balance', "0")
        log_message = f"User {code} is disabled. Setting balance to 0."
        print(log_message)
        success_logs.append({'code': code, 'action': log_message})
    except Exception as e:
        log_message = f"Error updating balance for code {code}: {e}"
        print(log_message)
        failed_updates.append({'code': code, 'balance': '0', 'error': str(e)})

# แปลง log และบันทึกเป็นไฟล์
if skipped_logs:
    skipped_df = pd.DataFrame(skipped_logs)
    skipped_output_path = "~/Downloads/skipped_logs.xlsx"
    skipped_df.to_excel(skipped_output_path, index=False)
    print(f"Skipped logs saved to: {skipped_output_path}")

if success_logs:
    success_df = pd.DataFrame(success_logs)
    success_output_path = "~/Downloads/success_logs.xlsx"
    success_df.to_excel(success_output_path, index=False)
    print(f"Success logs saved to: {success_output_path}")

if failed_updates:
    failed_df = pd.DataFrame(failed_updates)
    failed_output_path = "~/Downloads/failed_updates.xlsx"
    failed_df.to_excel(failed_output_path, index=False)
    print(f"Failed updates saved to: {failed_output_path}")

print("Logging completed.")

