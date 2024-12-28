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

# for create table
import plotly.graph_objects as graphObj

# for dash and config layout application
import dash
from dash import Dash, dcc, html, Input, Output

# for plot graph
import plotly.express as px

# สร้าง connection engine สำหรับฐานข้อมูล
connect_db = create_engine(
    f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('FINANCE_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)

# read data from sql
df = pd.DataFrame(pd.read_sql(f'''SELECT * FROM erp_2023_clean ORDER BY year, month_sort''', connect_db))

df_gl = (
    df.groupby(
        ['general_ledger_id','general_ledger_description'],
        as_index=False
    )
    .aggregate({'amount': 'sum'})
    .sort_values('amount', ascending=False)
)
print(df.head())

# create column rank
df_gl['rank'] = range(1, len(df_gl) + 1)
total_rows = len(df_gl)


print(df_gl.tail())  # ตรวจสอบท้ายตาราง

# create dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css",  # Tailwind CSS
        "https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@100..900&display=swap"  # Noto Sans Thai
    ]
)

# create table 
table_figure =  graphObj.Figure(
    data=[
        graphObj.Table(
            header=dict(
                values=['No','GL_ID','GL_Description','Amount'],
                fill_color='lightblue',
                align='center', 
                font=dict(color='black',size=14)
            ),
            cells=dict(
                values=[df_gl['rank'],df_gl['general_ledger_id'],df_gl['general_ledger_description'],df_gl['amount']],
                fill_color='white',
                align='left',
                font=dict(color='black', size=12),
                format=['', '', '', ',.2f']  # Format the 'Amount' column with commas
            )
        )
    ]
)

# create app layout
app.layout = html.Div([
    html.H1("ERP 2022-2023"),
    dcc.Graph(
        figure=table_figure,
        style={'width': '50%'}
    )
])

# run server
if __name__ == '__main__':
    app.run_server(debug=True)

