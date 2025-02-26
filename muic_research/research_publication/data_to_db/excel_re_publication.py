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
engine = create_engine(f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('RESEARCH_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")
#engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('RESEARCH_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

# read data from excel file.
data = pd.read_excel('../../../data/muic_research/Publication_Data/Publications_20240521_clean_data.xlsx')
df = pd.DataFrame(data)

# rename DataFrame column to match database schema.
df = df.rename(columns={
    'rank': 'rank',
    'group_rank': 'group_rank',
    'description': 'description',
    'WoS_with_JIF-P90': 'wos_with_jif_p90',
    'WoS_with_JIF': 'wos_with_jif',
    'WoS_SC': 'wos_sc',
    'WoS_SS': 'wos_ss',
    'WoS_AH': 'wos_ah',
    'WoS_ES': 'wos_es',
    'Scopus_SJR-10': 'scopus_sjr_10',
    'Scopus_Q1': 'scopus_q1',
    'Scopus_Q2': 'scopus_q2',
    'Scopus_Q3': 'scopus_q3',
    'Scopus_Q4': 'scopus_q4',
    'Scopus_No_Q': 'scopus_no_q',
    'ERIC': 'eric',
    'MathSciNet': 'math_sci_net',
    'Pubmed': 'pubmed',
    'JSTOR': 'jstor',
    'Project_Muse': 'project_muse',
    'Other_Inter.Databases': 'other_inter',
    'TCI_Group1': 'tci_group1',
    'TCI_Group2': 'tci_group2',
    'National_Journal': 'national_journal',
    'division': 'division',
    'id': 'id',
    'product_code': 'product_code',
    'firstname': 'firstname',
    'lastname': 'lastname',
    'title': 'title',
    'publication_month': 'publication_month',
    'publication_year': 'publication_year',
    'publication_calendar_year': 'publication_calendar_year',
    'publication_budget_year': 'publication_budget_year',
    'effective_date': 'effective_date',
    'national_international': 'national_international',
    'sdg': 'sdg'
})

# Convert date format if a date column exists (example column name: 'date').
if 'effective_date' in df.columns:
    df['effective_date'] = pd.to_datetime(df['effective_date'], format='%d-%m-%Y').dt.strftime('%Y-%m-%d')
    
print("Dataframe Preview:")
print(df.head())
# try to insert data to database.
try:
    # insert data to database appending new rows.
    result = df.to_sql(os.getenv('PUBLICATION_TABLE'), engine, schema=os.getenv('SCHEMA_DEFAULT'), index=False, chunksize=1000, if_exists='append')
    
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
    
