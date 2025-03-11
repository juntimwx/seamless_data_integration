import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote
from dotenv import load_dotenv
import os

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

# สร้าง connection engine สำหรับ SQL Server
engine = create_engine(
    f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}"
    f"@{os.getenv('LOCAL_HOST')}/{os.getenv('RESEARCH_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)
# engine สำรอง (commented out)
# engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('RESEARCH_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

def extract_sdg_values(db_str: any) -> dict:
    """
    ประมวลผลข้อมูลจากคอลัมน์ 'sdg' โดยแยกหมายเลขหลัก (ก่อนจุด)
    เช่น "1.4" จะได้หมายเลขหลักเป็น 1, "8.3" จะได้หมายเลขหลักเป็น 8 เป็นต้น
    จากนั้นจะตั้งค่า 1 ให้กับ sdg ที่ตรงกัน (sdg1, sdg8, …)
    """
    sdg_columns = [f"sdg{i}" for i in range(1, 18)]
    result = {col: 0 for col in sdg_columns}
    
    if pd.isnull(db_str):
        return result

    # แปลงให้เป็นสตริงหากไม่ใช่
    if not isinstance(db_str, str):
        db_str = str(db_str)

    parts = db_str.split(',')
    for part in parts:
        part = part.strip()  # ตัดช่องว่างออก
        if '.' in part:
            main_value = part.split('.')[0]
        else:
            main_value = part

        try:
            main_num = int(main_value)
        except ValueError:
            continue  # ข้ามหากไม่สามารถแปลงเป็นตัวเลขได้

        if 1 <= main_num <= 17:
            result[f'sdg{main_num}'] = 1
    return result

def main():
    # อ่านข้อมูลจากไฟล์ Excel
    data = pd.read_excel('../../../data/muic_research/Publication_Data/Publications_20240521_clean_data.xlsx')
    df = pd.DataFrame(data)

    # เปลี่ยนชื่อคอลัมน์ให้ตรงกับ schema ของฐานข้อมูล
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

    # เปลี่ยนรูปแบบวันที่ในคอลัมน์ effective_date (ถ้ามี)
    if 'effective_date' in df.columns:
        df['effective_date'] = pd.to_datetime(df['effective_date'], format='%d-%m-%Y').dt.strftime('%Y-%m-%d')

    # ประมวลผลคอลัมน์ 'sdg' โดยใช้ extract_sdg_values แล้วสร้างคอลัมน์ใหม่สำหรับแต่ละ sdg
    sdg_df = df['sdg'].apply(lambda x: pd.Series(extract_sdg_values(x)))
    df = pd.concat([df, sdg_df], axis=1)
    # หากไม่ต้องการคอลัมน์ 'sdg' ต้นฉบับก็สามารถลบทิ้งได้
    # df.drop('sdg', axis=1, inplace=True)

    print("Dataframe Preview:")
    print(df.head())

    output_filename = f"~/Downloads/draft_extract_sdg_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    df.to_excel(output_filename, index=False)
    print(f"Saved output to {output_filename}")

if __name__ == '__main__':
    main()
