import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from urllib.parse import quote
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('PRINTING_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")
connect_db_printer = create_engine(
    f"postgresql+psycopg2://{quote_plus(os.getenv('PRINTER_USERNAME'))}:"
    f"{quote_plus(os.getenv('PRINTER_PASSWORD'))}@"
    f"{os.getenv('PRINTER_HOST')}/"
    f"{os.getenv('PAPERCUT_DATABASE')}"
)

data = pd.read_sql('''
select user_name username
    ,full_name
    ,email
    ,department
    ,office
from tbl_user
where deleted = 'N'
order by user_name
''',connect_db_printer)

df = pd.DataFrame(data)

print(df)
df.to_sql('master_users', engine, index=False, chunksize=500, if_exists='append')  #replace