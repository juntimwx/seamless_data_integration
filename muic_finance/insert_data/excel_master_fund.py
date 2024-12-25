import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

engine = create_engine(f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('FINANCE_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")
#engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('FINANCE_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

data = pd.read_excel('../../data/muic_finance/master/Master_FUND_18112022.xlsx')

df = pd.DataFrame(data, columns=['Fund_Id', 'Fund_Description'])

df = df.rename(columns={
    'Fund_Id' : 'fund_id',
    'Fund_Description' : 'fund_description',
})

print(df)

df.to_sql('master_funds', engine, index=False, chunksize=500, if_exists='append')  #replace
print("insert data successfully")