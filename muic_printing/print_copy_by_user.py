import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('PRINTING_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")


file_name = 'print_copy_summary_by_user_Feb_2025'
data = pd.read_csv(fr'../data/muic_printing/{file_name}.csv',
                   encoding='ISO-8859-1', skiprows=2)

df = pd.DataFrame(data, columns=
               ['Username', 'Full Name', 'Job Type', 'Color Pages', 'Grayscale Pages',
       'Total Printed Pages', 'Cost', 'Duplex Pages', 'Simplex Pages'])

# เปลี่ยนชื่อคอลัมน์ให้เป็นไปตามมาตรฐานที่ต้องการ
# df.rename(columns={
#     'Username' : 'username',
#     'Full Name' : 'full_name',
#     'Job Type' : 'job_type',
#     'Color Pages' : 'color_pages',
#     'Grayscale Pages' : 'grayscale_pages',
#     'Total Printed Pages' : 'total_printed_pages',
#     'Cost' : 'cost',
#     'Duplex Pages' : 'duplex_pages',
#     'Simplex Pages' : 'simplex_pages',
# }, inplace=True)

# df['date_version'] = '2024-10-31'

print(df)
df.to_sql('print_copy_summary_by_user_Feb_2025', engine, index=False, chunksize=500, if_exists='append')  #replace