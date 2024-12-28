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
from dash import Dash, dcc, html, Input, Output,dash_table
from dash.dash_table.Format import Format, Scheme


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

# df_gl['amount'] = df_gl['amount'].map('{:,.2f}'.format)
df_gl['amount'] = df_gl['amount'].astype(float)

# create column rank
df_gl['rank'] = range(1, len(df_gl) + 1)
total_rows = len(df_gl)


print(df_gl.tail())  # ตรวจสอบท้ายตาราง

# create dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css",  # Tailwind CSS
        "https://fonts.googleapis.com/css2?family=Athiti:wght@200;300;400;500;600;700&display=swap"  # Athiti
    ]
)

# create table 
table_figure =  dash_table.DataTable(
    columns=[
        {"name":"No.","id":"rank"},
        {"name":"GL ID","id":"general_ledger_id"},
        {"name":"GL Description","id":"general_ledger_description"},
        {
            "name": "Amount",
            "id": "amount",
            "type": "numeric",
            "format": Format(
                group=",",        # เพิ่มการคั่นหลักพันด้วยจุลภาค
                precision=2,      # จำนวนทศนิยม 2 ตำแหน่ง
                scheme=Scheme.fixed
            )
        }
    ],
    data=df_gl.to_dict('records'),
    # filter_action='native',
    sort_action='native',
    sort_mode='multi',
    page_size=50,
    style_header={
        'backgroundColor': 'lightblue',
        'fontWeight': 'bold',
        'textAlign': 'center'
    },
    style_cell={
        'textAlign': 'left',
        'padding': '5px',
        'font_size': '12px'
    },
    style_data_conditional=[
        {
            'if': {'column_id': 'amount'},
            'textAlign': 'right'
        }
    ],
    style_as_list_view=True,
    style_table={
        'minWidth': '100%',
        'maxHeight': '600px',
        'overflowY': 'auto',
        'overflowX': 'auto',
    }
)


# create app layout
app.layout = html.Div(
    className="container mx-2 p-6 bg-slate-200",
    children=[
        html.H1(
            "ERP 2023",
            className="text-4xl font-semibold mb-8 text-center text-gray-800"
        ),
        html.Div(
            className="bg-white rounded p-3",
            children=[
                table_figure
            ]
            
        )
    ]
)

# run server
if __name__ == '__main__':
    app.run_server(debug=True)

