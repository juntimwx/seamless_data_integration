# for read data
import pandas as pd

# for connect engine database
from sqlalchemy import create_engine
from urllib.parse import quote

# for get variable from .env file
# pip install python-dotenv
from dotenv import load_dotenv
import os

# load value from file .env
load_dotenv()

# for dash and config layout application
from dash import Dash, dcc, html, Input, Output

# for plot graph
import plotly.express as px

# สร้าง connection engine สำหรับฐานข้อมูล
connect_db = create_engine(
    f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('FINANCE_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)

# read data from sql
df = pd.DataFrame(pd.read_sql(f'''SELECT * FROM erp_2023_clean ORDER BY year, month_sort''', connect_db))

print(df.head())

