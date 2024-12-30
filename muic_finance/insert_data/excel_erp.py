import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote
from dotenv import load_dotenv
import os

# load variable form .env file.
load_dotenv()

# create connection engin for database SQL Server.
engine = create_engine(f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('FINANCE_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")
#engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('FINANCE_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

# read data from excel file.
# data = pd.read_excel('../../data/muic_finance/data/ERP_2023_20240507.xlsx')
data = pd.read_excel('../../data/muic_finance/data/ERP_2022_20230703_FINAL.xlsx')
df = pd.DataFrame(data,columns=['Year','Trimester','Day','Month','DocNo','DocDate','FundsCtr','CostCtr_ID',
                                'CostCentralize','IO_Goods','IO_Work','IO_Activity','IO_Project','Order_Description',
                                'HROT','GL_ID','GL_Description','Amount','Details','MU_Strategy','IC_Strategy'])

# rename DataFrame column to match database schema.
df = df.rename(columns={
    'Year' : 'year',
    'Trimester' : 'trimester',
    'Day' : 'day',
    'Month' : 'month',
    'DocNo' : 'doc_no',
    'DocDate' : 'doc_date',
    'FundsCtr' : 'funds_center',
    'CostCtr_ID' : 'cost_center_id',
    'CostCentralize' : 'cost_centralize',
    'IO_Goods' : 'io_good_id',
    'IO_Work' : 'io_work_id',
    'IO_Activity' : 'io_activity_id',
    'IO_Project' : 'io_project_id',
    'Order_Description' : 'order_description',
    'HROT' : 'hrot',
    'GL_ID' : 'general_ledger_id',
    'GL_Description' : 'general_ledger_description',
    'Amount' : 'amount',
    'Details' : 'detail',
    'MU_Strategy' : 'mu_strategy_id',
    'IC_Strategy' : 'ic_strategy_id',
})

# Convert date format if a date column exists (example column name: 'date').
if 'doc_date' in df.columns:
    df['doc_date'] = pd.to_datetime(df['doc_date'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')

print("Dataframe Preview:")
print(df.head())
# try to insert data to database.
try:
    # insert data to database appending new rows.
    # result = df.to_sql(os.getenv('ERP_2023'), engine, schema=os.getenv('SCHEMA_DEFAULT'), index=False, chunksize=1000, if_exists='append')
    result = df.to_sql(os.getenv('ERP_2022'), engine, schema=os.getenv('SCHEMA_DEFAULT'), index=False, chunksize=1000, if_exists='append')
    
    # display a message when data inserted successfully and show number of row inserted to database.
    print(f"Data inserted successfully. Number of rows inserted: {len(df)}")
    
# handle error such as connection or SQL command issues.
except SQLAlchemyError as e:
    # display a message when data insertion fails.
    print("Failed to insert data into the database.")
    print(f"Error: {e}")
    exit()
except Exception as e:
    # display a message when data insertion fails.
    print("An unexpected error occurred.")
    print(f"Error: {e}")
    
