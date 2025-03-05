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

# for dash and config layout application
import dash
from dash import dcc, html, dash_table

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

table_gl_figure = dash_table.DataTable(
    id='table_gl',
    columns=[
        {'name': 'Section หน่วยงาน', 'id':'section'},
        {'name': 'Spending Q1', 'id': 'spending_q1'}
    ],
    style_table={
        'minWidth': '100%',
        'height': '900px',  # เพิ่มความสูงให้เท่ากับ 2 กราฟ และรวมพื้นว่าง
        'overflowY': 'auto',
        'overflowX': 'auto',
        'border': 'none',  # ลบกรอบพื้นหลัง
    },
    style_as_list_view=False
)