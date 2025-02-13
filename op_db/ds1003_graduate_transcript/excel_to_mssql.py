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
# engine = create_engine(f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('FINANCE_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")
engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('OP_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")


data = pd.read_excel('../../data/op_db/data/ds1003_graduate_transcript/ds1003_graduate_transcript_from_p-phon.xlsx')
df = pd.DataFrame(data)

print("Dataframe Preview:")
print(df.head())
# try to insert data to database.
try:
    # insert data to database appending new rows.
    result = df.to_sql(os.getenv('DS_1003'), engine, schema=os.getenv('SCHEMA_DEFAULT'), index=False, chunksize=1000, if_exists='append')
    
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
    