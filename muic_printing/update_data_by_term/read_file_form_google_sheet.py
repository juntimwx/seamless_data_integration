import requests
import pandas as pd
from dotenv import load_dotenv
import os

import xmlrpc.client as xmlrpclib

load_dotenv()

# connect to server
server = xmlrpclib.Server(os.getenv('URL_API'))
auth_token = os.getenv('AUTH_TOKEN')

# URL ของ Web App (ใส่ token สำหรับการตรวจสอบสิทธิ์)
api_url = fr"https://script.google.com/macros/s/{os.getenv('token_url')}/exec?token={os.getenv('AUTH_TOKEN')}"

# ดึงข้อมูลจาก Google Apps Script
response = requests.get(api_url)

if response.status_code == 200:
    data = response.json()
    # แปลงข้อมูลเป็น DataFrame
    df = pd.DataFrame(data)
    print(df.head())

    for index, row in df.iterrows():
        print(row['employee_id'])
        print("User: %s %s" % (row['employee_id'], server.api.getUserProperty(auth_token, row['employee_id'], 'full-name')))
        # server.api.getUserProperty(auth_token, row['employee_id'], 'email')
        server.api.setUserProperty(auth_token, row['employee_id'], 'email', row['email_ac_th'])