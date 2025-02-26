import pandas as pd
import math
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

import xmlrpc.client as xmlrpclib

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

# connect to server
server = xmlrpclib.Server(os.getenv('URL_API'))
auth_token = os.getenv('AUTH_TOKEN')

# สร้าง connection ไปยังฐานข้อมูล SKY
sky_engine = create_engine(
    f"mssql+pyodbc://{os.getenv('SKY_USERNAME')}:{quote(os.getenv('SKY_PASSWORD'))}@{os.getenv('SKY_HOST')}/{os.getenv('SKY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)

connect_db_printer = create_engine(
    f"postgresql+psycopg2://{quote_plus(os.getenv('PRINTER_USERNAME'))}:"
    f"{quote_plus(os.getenv('PRINTER_PASSWORD'))}@"
    f"{os.getenv('PRINTER_HOST')}/"
    f"{os.getenv('PAPERCUT_DATABASE')}"
)

# ดึงข้อมูลสถานะนักศึกษา
query_student_status = '''
    SELECT
        std.code,
        std.FirstNameEn,
        std.LastNameEn,
        std.IsActive,
        CASE
            WHEN std.StudentStatus = 's'   THEN 'Student'
            WHEN std.StudentStatus = 'la'  THEN 'Student Leave of absence'
            WHEN std.StudentStatus = 'ex'  THEN 'Student Exchange'
            ELSE 'Unknown'
        END AS student_status,
        major.Division
    FROM student.Students std
    LEFT JOIN dbo.StagingStudent stagingStudent ON std.Code = stagingStudent.studentCode
    LEFT JOIN dbo.ALLMajor major ON SUBSTRING(stagingStudent.programCode,1,4) = major.Major
    WHERE std.IsActive = 1
        AND std.StudentStatus IN ('s','la','ex')
        AND std.code < 9000000
        AND major.Division != 'OAA'
'''

df_student_status = pd.read_sql(query_student_status, con=sky_engine)

# ดึงข้อมูล balance printer 
user_printer_db = pd.read_sql('''
    select usr.user_name as code,
        account.balance as balance_add_drop_period
    from tbl_user usr
    left join (
        select * from tbl_account  where deleted = 'N'
    ) account on usr.user_name = account.account_name
    where usr.deleted = 'N'
    --disabled_printing = 'N' and 
    --usr.department = 'Student'
    order by usr.department,usr.office
''',connect_db_printer)

# แปลงคอลัมน์ code เป็น string และตัดช่องว่างหัวท้าย
df_student_status['code'] = df_student_status['code'].astype(str).str.strip()

df_student_status.rename(columns={'FirstNameEn':'first_name_en','LastNameEn':'last_name_en','IsActive':'is_active'},inplace=True)

print("===== df_student_status sample =====")
print(df_student_status.head(10))
print(df_student_status.info())

# อ่านข้อมูลจำนวน balance ในเทอมจาก Excel
data_student_balance_in_term = pd.read_excel(
    '../../data/muic_printing/credit_interm/2-2024/registration_result_amount_term_2_2024_2025-01-17.xlsx',
    skiprows=1  # ปรับตามโครงสร้างไฟล์จริง
)

# สร้าง DataFrame เฉพาะคอลัมน์ที่ต้องการ
df_student_balance_in_term = pd.DataFrame(
    data_student_balance_in_term,
    columns=['Division', 'Code', 'Status', 'Credit']
)

# เปลี่ยนชื่อคอลัมน์ Code -> code
df_student_balance_in_term.rename(columns={'Code': 'code','Division':'division','Status':'status','Credit':'register_credit'}
                                , inplace=True)

# แปลง code เป็น string และตัดช่องว่างหัวท้าย
df_student_balance_in_term['code'] = df_student_balance_in_term['code'].astype(str).str.strip()

print("===== df_student_balance_in_term sample =====")
print(df_student_balance_in_term.head(10))
print(df_student_balance_in_term.info())

# อ่านข้อมูลจาก CSV สำหรับ transaction_balance
data_transaction_balance = pd.read_csv(
    '../../data/muic_printing/credit_interm/2-2024/transaction_credit.csv',
    skiprows=2,
    encoding='latin-1' 
)

df_transaction_balance = pd.DataFrame(
    data_transaction_balance,
    columns=['Username','Balance']
)

# เปลี่ยนชื่อ Username -> code
df_transaction_balance.rename(columns={'Username': 'code','Balance':'balance_printer_old'}, inplace=True)

# แปลง code เป็น string และตัดช่องว่างหัวท้าย
df_transaction_balance['code'] = df_transaction_balance['code'].astype(str).str.strip()

print("===== df_transaction_balance sample =====")
print(df_transaction_balance.head(10))
print(df_transaction_balance.info())

balance_current_student = pd.DataFrame(user_printer_db)
# วิธีที่ 1: ใช้การ merge ทีละขั้น
df_merge_data = pd.merge(
    pd.merge(
        pd.merge(df_student_status, df_student_balance_in_term, on='code', how='left'),
        df_transaction_balance,
        on='code',
        how='left'
    ),
    balance_current_student,
    on='code',
    how='left'
)

print("===== df_merge_data sample =====")
print(df_merge_data.head(10))
print(df_merge_data.info())

# บันทึกผลลัพธ์ลงไฟล์ Excel
output_path = "~/Downloads/test.xlsx"
df_merge_data.to_excel(output_path, index=False)
print(f"Data merged and saved to: {output_path}")


# calculate balance printer
def calculate_balance_by_term(student_status, credit_regis, balance_printer_old, balance_current_student):
    if student_status == 'Student':
        new_balance = credit_regis * 36 if not pd.isna(credit_regis) else 0
        half_old_balance = balance_printer_old / 2 if not pd.isna(balance_printer_old) else 0
        reduce_balance_add_drop_period = 200 - balance_current_student if not pd.isna(balance_current_student) else 0
        
        complete_balance = new_balance + half_old_balance - reduce_balance_add_drop_period
        if pd.isna(credit_regis):
            complete_balance = balance_current_student

        # ปรับลดหรือคงเพดานสูงสุด 800
        if complete_balance > 800:
            complete_balance = 800
    else:
        complete_balance = 100

    # ปัดเศษขึ้นก่อนคืนค่า
    complete_balance = math.ceil(complete_balance)

    return complete_balance

# เพิ่มฟังก์ชันเรียก API สำหรับข้อมูลเพิ่มเติม
def get_user_department(code):
    try:
        department = server.api.getUserProperty(auth_token, code, 'department')
    except Exception as e:
        print(f"Error fetching department for code {code}: {e}")
        department = None
    return department

def get_user_office(code):
    try:
        department = server.api.getUserProperty(auth_token, code, 'office')
    except Exception as e:
        print(f"Error fetching office for code {code}: {e}")
        department = None
    return department


# เพิ่มข้อมูลที่คำนวณใหม่เข้าใน DataFrame
df_merge_data['calculated_balance'] = df_merge_data.apply(
    lambda row: calculate_balance_by_term(
        row['student_status'],
        row['register_credit'],
        row['balance_printer_old'],
        row['balance_add_drop_period']
    ), axis=1
)

# เพิ่มข้อมูล department จาก API ลงใน DataFrame
df_merge_data['department'] = df_merge_data['code'].apply(get_user_department)
df_merge_data['office'] = df_merge_data['code'].apply(get_user_office)
df_merge_data['update_department'] = df_merge_data['student_status']

# บันทึก DataFrame ที่อัปเดตแล้วออกเป็นไฟล์ Excel
output_path = "~/Downloads/updated_test_v5.xlsx"
df_merge_data.to_excel(output_path, index=False)
print(f"Updated data saved to: {output_path}")

def set_user_property(df):
    skipped_logs = []  # เก็บรายการที่ถูกข้าม
    success_logs = []  # เก็บรายการที่อัปเดตสำเร็จ
    failed_updates = []  # เก็บรายการที่อัปเดตไม่สำเร็จ

    for idx, row in df.iterrows():
        code = row['code']
        department = row['department']
        update_department = row['update_department']
        balance_before = row['balance_add_drop_period']
        balance = row['calculated_balance']

        # ตรวจสอบว่า department ว่างหรือไม่
        if pd.isna(department) or str(department).strip() == "":
            log_message = f"Skipping code {code}: department is empty or NaN"
            print(log_message)
            skipped_logs.append({'code': code, 'reason': log_message})
            continue

        # ข้ามแถวถ้า department ตรงกับ update_department และ balance เท่ากัน
        if department == update_department and balance_before == balance:
            log_message = f"Skipping code {code}: department and balance are up-to-date"
            print(log_message)
            skipped_logs.append({'code': code, 'reason': log_message})
            continue

        # อัปเดต balance
        try:
            if balance_before != balance:
                server.api.setUserProperty(auth_token, code, 'balance', str(balance))
                log_message = f"Successfully updated balance for code {code} from {balance_before} to {balance}"
                print(log_message)
                success_logs.append({'codec': code, 'action': log_message})
        except Exception as e:
            log_message = f"Error updating balance for code {code}: {e}"
            print(log_message)
            failed_updates.append({'code': code, 'balance_before': balance_before, 'balance': balance, 'error': str(e)})

        # อัปเดต department
        try:
            if department != update_department:
                server.api.setUserProperty(auth_token, code, 'department', update_department)
                log_message = f"Successfully updated department for code {code} from {department} to {update_department}"
                print(log_message)
                success_logs.append({'code': code, 'action': log_message})
        except Exception as e:
            log_message = f"Error updating department for code {code}: {e}"
            print(log_message)
            failed_updates.append({'code': code, 'department': department, 'update_department': update_department, 'error': str(e)})

    # แปลง skipped_logs และ success_logs เป็น DataFrame และบันทึก
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

    # แปลง failed_updates เป็น DataFrame และบันทึกถ้ามีข้อผิดพลาด
    if failed_updates:
        failed_df = pd.DataFrame(failed_updates)
        failed_output_path = "~/Downloads/failed_updates.xlsx"
        failed_df.to_excel(failed_output_path, index=False)
        print(f"Failed updates saved to: {failed_output_path}")

    print("Logging completed.")

# เรียกใช้ฟังก์ชัน
set_user_property(df_merge_data)

