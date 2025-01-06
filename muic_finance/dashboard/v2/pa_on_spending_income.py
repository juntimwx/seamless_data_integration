# for read data
import pandas as pd

# for connect engine database
from sqlalchemy import create_engine
from urllib.parse import quote

# for get variable from .env file
from dotenv import load_dotenv
import os

# load value from file .env
load_dotenv()

# สร้าง connection engine สำหรับฐานข้อมูล
connect_db = create_engine(
    f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('FINANCE_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)

# read data from sql
df = pd.DataFrame(pd.read_sql(
    fr'''
    SELECT * 
    FROM {os.getenv('ERP_VIEW')} 
    WHERE cost_center_description = '{os.getenv('SSO_STAFF_OFFICE')}'
    ORDER BY year, month_sort
    ''',
    connect_db
))

print(df.head())

