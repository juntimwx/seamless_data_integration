import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('PRINTING_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")


file_name = 'print_summary_by_user_Jan_2025'
data = pd.read_csv(fr'../data/muic_printing/{file_name}.csv',
                   skiprows=2)

df = pd.DataFrame(data, columns= 
               ['Username', 'Full Name', 'Department', 'Office', 'Primary Card Number',
       'Color Pages', 'Grayscale Pages', 'Duplex Pages', 'Simplex Pages',
       'Total Printed Pages', 'Jobs', 'Avg. Pages', 'Cost', 'Avg. Cost'])

# เปลี่ยนชื่อคอลัมน์ให้เป็นไปตามมาตรฐานที่ต้องการ
# df.rename(columns={
#     'Username' : 'username',
#     'Full Name' : 'full_name',
#     'Department' : 'department',
#     'Office' : 'office',
#     'Primary Card Number' : 'primary_card_number',
#     'Color Pages' : 'color_pages',
#     'Grayscale Pages' : 'grayscale_pages',
#     'Duplex Pages' : 'duplex_pages',
#     'Simplex Pages' : 'simplex_pages',
#     'Total Printed Pages' : 'total_printed_pages',
#     'Jobs' : 'jobs',
#     'Avg. Pages' : 'average_pages',
#     'Cost' : 'cost',
#     'Avg. Cost' : 'average_cost'
# }, inplace=True)

# df['date_version'] = '2024-10-31'

print(df)
df.to_sql('print_summary_by_user_Jan_2025', engine, index=False, chunksize=500, if_exists='append')  #replace