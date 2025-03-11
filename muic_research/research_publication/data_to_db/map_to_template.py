import pandas as pd
import helper_map_template as map_template_helper
from datetime import datetime

def main():
    # โหลดข้อมูลจาก Excel
    data = pd.read_excel('../../../data/muic_research/Publication_Data/Publications_20240521_clean_map_template.xlsx')
    df_data = pd.DataFrame(data)
    
    # ประมวลผลฐานข้อมูล เพียงครั้งเดียว
    parsed_db = map_template_helper.get_parse_database_data(df_data)
    
    # สร้าง DataFrame สำหรับ template
    df_template = pd.DataFrame()
    df_template['rank'] = map_template_helper.get_rank(df_data)
    df_template['group_rank'] = map_template_helper.get_group_rank(df_data)
    df_template['description'] = df_data['Description']
    
    # ใช้ชื่อ column ที่ถูกต้อง จาก parsed_db
    df_template['WoS_with_JIF-P90'] = parsed_db['WoS_with_JIF-P90']
    df_template['WoS_with_JIF']   = parsed_db['WoS_with_JIF']
    df_template['WoS_SC']         = parsed_db['WoS_SC']
    df_template['WoS_SS']         = parsed_db['WoS_SS']
    df_template['WoS_AH']         = parsed_db['WoS_AH']
    df_template['WoS_ES']         = parsed_db['WoS_ES']
    df_template['Scopus_SJR-10']  = parsed_db['Scopus_SJR-10']
    df_template['Scopus_Q1']      = parsed_db['Scopus_Q1']
    df_template['Scopus_Q2']      = parsed_db['Scopus_Q2']
    df_template['Scopus_Q3']      = parsed_db['Scopus_Q3']
    df_template['Scopus_Q4']      = parsed_db['Scopus_Q4']
    df_template['Scopus_No_Q']    = parsed_db['Scopus_No_Q']
    df_template['ERIC']           = parsed_db['ERIC']
    df_template['MathSciNet']     = parsed_db['MathSciNet']
    df_template['Pubmed']         = parsed_db['Pubmed']
    df_template['JSTOR']          = parsed_db['JSTOR']
    df_template['Project_Muse']   = parsed_db['Project_Muse']
    df_template['Other_Inter.Databases'] = parsed_db['Other_Inter.Databases']
    df_template['TCI_Group1']     = parsed_db['TCI_Group1']
    df_template['TCI_Group2']     = parsed_db['TCI_Group2']
    df_template['National_Journal'] = parsed_db['National_Journal']
    
    # คอลัมน์อื่น ๆ จาก df_data
    df_template['division'] = df_data['Division']
    df_template['id'] = df_data['id']
    df_template['product_code'] = df_data['Product Code']
    df_template['firstname'] = df_data['Firstname']
    df_template['lastname'] = df_data['Lastname']
    df_template['title'] = df_data['Title']
    df_template['publication_month'] = df_data['Month']
    df_template['publication_year'] = map_template_helper.get_clean_year(df_data)
    df_template['publication_calendar_year'] = map_template_helper.get_clean_year(df_data)
    df_template['publication_budget_year'] = map_template_helper.get_clean_budget_year(df_data)
    df_template['effective_date'] = map_template_helper.get_format_effective_date(df_data)
    df_template['national_international'] = df_data['Other Classification ("A"-Excellent, International-Very Good, National-Good)']
    df_template['sdg'] = df_data['sdg']
    
    print(df_template.head(5))
    
    output_filename = f"~/Downloads/draft_publications_template_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    df_template.to_excel(output_filename, index=False)
    print(f"Saved output to {output_filename}")

if __name__ == '__main__':
    main()
