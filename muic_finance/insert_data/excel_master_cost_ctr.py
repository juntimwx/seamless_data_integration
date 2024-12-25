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

data = pd.read_excel('../../data/muic_finance/master/Master_CostCtr_2024.06.05.xlsx')

df = pd.DataFrame(data)

df = df.rename(columns={
    'CostCtr_Id' : 'id',
    'CostCtr_Description' : 'description',
    'CostCtr_Eng' : 'name_en',
    'CostCtr_TH' : 'name_th',
})

print(df)
df.to_sql('master_cost_ctr', engine, index=False, chunksize=500, if_exists='append')  #replace
print("insert data successfully")