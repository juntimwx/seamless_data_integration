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

def __init__(self, host="10.27.24.140", port=9191, ssl=False, verbose=False):
    self.host = host
    self.port = port
    self.ssl = ssl
    self.verbose = verbose

    if self.ssl is True:
        self.url = f"https://{self.host}:{self.port}/rpc/api/xmlrpc"
    else:
        self.url = f"http://{self.host}:{self.port}/rpc/api/xmlrpc"

    self.api = None

def addNewInternalUser(
    self,
    authToken: str,
    userName: str,
    password: str,
    fullName=None,
    email=None,
    cardId=None,
    pin=None,
):
    """
    Creates and sets up a new internal user account
        - The (unique) username and password are required at a minimum
        - Additional properties are optional and will be used if not blank. Properties may also be set after creation using `setUserProperty()` or `setUserProperties()`
    
    Parameters:
    - `Required`
        - `username` (str): A unique username. An exception is thrown if the username already exists
        - `password` (str): The user's password
    - `Optional`
        - `fullName` (str): The full name of the user
        - `email` (str): The email address of the user
        - `cardId` (str): The card/identity number of the user
        - `pin` (int): The card/id pin
        
    Returns:
    """
    return self.api.addNewInternalUser(
        authToken, userName, password, fullName, email, cardId, pin
        )

if response.status_code == 200:
    data = response.json()
    # แปลงข้อมูลเป็น DataFrame
    df = pd.DataFrame(data)
    print(df.head())

    for index, row in df.iterrows():
        print(row['employee_id'])
        print("User: %s %s" % (row['employee_id'], server.api.getUserProperty(auth_token, row['employee_id'], 'full-name')))
        # server.api.getUserProperty(auth_token, row['employee_id'], 'email')
        # server.api.setUserProperty(auth_token, row['employee_id'], 'email', row['email_ac_th'])
        # print(server.api.isUserExists(auth_token, row['employee_id']))
        # server.api.addNewInternalUser(auth_token,row['employee_id'], row['password_for_printing'], row['full_name'], row['email'])
        addNewInternalUser(auth_token,row['employee_id'], row['password_for_printing'], row['full_name'], row['email'],'','')