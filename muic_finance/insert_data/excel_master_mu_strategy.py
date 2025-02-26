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
data = pd.read_excel('../../data/muic_finance/master/Master_MU_Strategy_2023.05.31.xlsx')
df = pd.DataFrame(data)

# rename DataFrame column to match database schema.
df = df.rename(columns={
    'ID_MUST' : 'id',
    'Year_start' : 'year_start',
    'Year_end' : 'year_end',
    'Name' : 'name',
    'Description' : 'description',
    'status' : 'status'
})

print("Dataframe Preview:")
print(df.head())

# try to insert data to database.
try:
    # insert data to database appending new rows.
    result = df.to_sql(os.getenv('MU_STRATEGY_TABLE'), engine, schema=os.getenv('SCHEMA_MASTER'), index=False, chunksize=500, if_exists='append')
    
    # display a message when data inserted successfully and show number of row inserted to database.
    print(f"Data inserted successfully. Number of rows inserted: {len(df)}")
    
# handle error such as connection or SQL command issues.
except SQLAlchemyError as e:
    # display a message when data insertion fails.
    print("Failed to insert data into the database.")
    print(f"Error: {e}")
except Exception as e:
    # display a message when data insertion fails.
    print("An unexpected error occurred.")
    print(f"Error: {e}")
