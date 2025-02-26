import requests
import pandas as pd
from dotenv import load_dotenv
import os
import xmlrpc.client as xmlrpclib
import datetime

load_dotenv()

# เชื่อมต่อ server
server = xmlrpclib.Server(os.getenv('URL_API'))
auth_token = os.getenv('AUTH_TOKEN')

# URL สำหรับดึงข้อมูล
api_url = f"https://script.google.com/macros/s/{os.getenv('token_url')}/exec?token={os.getenv('AUTH_TOKEN')}"
# URL สำหรับอัปเดต (POST) กลับไปที่ Google Sheet
post_url = f"https://script.google.com/macros/s/{os.getenv('token_url')}/exec?token={os.getenv('AUTH_TOKEN')}"

# 1) ดึงข้อมูลจาก Google Apps Script (GET)
response = requests.get(api_url)

# print(server.api.getUserProperty(auth_token, "23000004", 'disabled-print'))

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    print(df.head())
    
    for index, row in df.iterrows():
        # ตรวจสอบว่า user มีอยู่หรือยัง
        user_exists = server.api.isUserExists(auth_token, row['employee_id'])
        print(user_exists)

        if not user_exists:
            # ถ้าไม่มี user ให้สร้าง user ใหม่
            server.api.addNewInternalUser(
                auth_token,
                row['employee_id'],
                row['password_for_printing'],
                row['full_name'],
                row['email_ac_th'],
                '',
                ''
            )
            if row['type'] == 'Lecturer Parttime':
                balance = "100"
            else:
                balance = "1"

            server.api.setUserProperties(auth_token, row['employee_id'], [
                ['balance', balance],
                ['department', row['type']],
                ['office', row['office']],
                ['secondary-card-number', row['password_for_printing']],
                ['notes', f'Created by Juntima {datetime.date.today()}']
            ])

            # 2) เมื่อสร้าง User เสร็จแล้ว ให้อัปเดตสถานะกลับไปที่ Google Sheet
            # โดยส่ง employee_id และ status (หรือข้อความใด ๆ ตามต้องการ)
            update_data = {
                "employee_id": row["employee_id"],
                "status": f"Created {datetime.date.today()}"  # หรือระบุเป็น "ดำเนินการแล้ว" ตามต้องการ
            }
            update_response = requests.post(post_url, data=update_data)

            if update_response.status_code == 200:
                print(f"Update status for {row['employee_id']} success.")
            else:
                print(f"Update status for {row['employee_id']} failed: {update_response.text}")

        else:
            # ถ้ามีอยู่แล้ว จะแค่พิมพ์หรือทำอย่างอื่นก็ได้
            print(
                f"ผู้ใช้งาน: {row['employee_id']} "
                f"{server.api.getUserProperty(auth_token, row['employee_id'], 'full-name')} "
                "มีอยู่แล้ว"
            )
