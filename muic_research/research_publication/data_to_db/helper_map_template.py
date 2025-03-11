import re
import pandas as pd
import numpy as np

def get_rank(df_data):
    valid_ranks = ['Lecturer', 'Assoc.Prof.', 'Support Staff', 'Asst.Prof.', 'Prof.', 'Asst.Lect.', 'Academic Advisor']
    
    def check_rank_value(row):
        rank = str(row['Rank']).strip()
        if rank not in valid_ranks:
            if rank in ('Asst.Prof', 'Asst. Prof.'):
                return 'Asst.Prof.'
            elif rank in ('Assoc.Prof', 'Assoc. Prof.'):
                return 'Assoc.Prof.'
            else:
                return rank
        return rank
    
    return df_data.apply(check_rank_value, axis=1)

def get_group_rank(df_data):
    def map_group_rank(row):
        rank = str(row['Rank']).strip()
        if rank == 'Academic Advisor':
            return 'Academic Advisor'
        elif rank == 'Support Staff':
            return 'Support Staff'
        else:
            return 'Lecturer'
    
    return df_data.apply(map_group_rank, axis=1)


def get_parse_database_data(df_data: pd.DataFrame) -> pd.DataFrame:
    """
    แปลงข้อมูลจากคอลัมน์ "Database (WoS, Scopus, TCI)" โดยแยกข้อมูลของฐานข้อมูล
    ต่าง ๆ ลงในคอลัมน์ใหม่ที่กำหนดไว้

    Parameters:
      df_data: pandas DataFrame ที่มีคอลัมน์ "Database (WoS, Scopus, TCI)"

    Returns:
      DataFrame ที่รวมคอลัมน์เดิมกับคอลัมน์ใหม่ที่ถูกแยกข้อมูลออกมาแล้ว
    """
    # รายชื่อคอลัมน์ใหม่ที่ต้องการสร้าง
    new_columns = [
        "WoS_with_JIF-P90", "WoS_with_JIF", "WoS_SC", "WoS_SS", "WoS_AH", "WoS_ES",
        "Scopus_SJR-10", "Scopus_Q1", "Scopus_Q2", "Scopus_Q3", "Scopus_Q4", "Scopus_No_Q",
        "ERIC", "MathSciNet", "Pubmed", "JSTOR", "Project_Muse", "Other_Inter.Databases",
        "TCI_Group1", "TCI_Group2", "National_Journal"
    ]
    
    def parse_database(db_str: str) -> dict:
        """
        แปลง string ข้อมูลฐานข้อมูลในแต่ละแถว และคืนค่าเป็น dictionary ที่มี flag
        สำหรับแต่ละคอลัมน์ที่ต้องการ
        """
        # กำหนดค่าเริ่มต้นเป็น 0 ให้กับทุกคอลัมน์
        result = {col: 0 for col in new_columns}
        
        if pd.isnull(db_str):
            return result
        
        # แยกข้อมูลแต่ละส่วนด้วยเครื่องหมายจุลภาค
        parts = db_str.split(',')
        for part in parts:
            part = part.strip()
            
            # --- ตรวจสอบข้อมูลของ WoS ---
            if "WoS" in part:
                if "(SC)" in part:
                    result["WoS_SC"] = 1
                if "(SS)" in part:
                    result["WoS_SS"] = 1
                if "(AH)" in part:
                    result["WoS_AH"] = 1
                if "(ES)" in part:
                    result["WoS_ES"] = 1

                # ตรวจสอบค่า JIF
                # ใช้ regex ที่รองรับทั้ง (JIF-Pxx) และ (JIF-xx)
                match = re.search(r'JIF-?P?([\d\.]+)', part)
                if match:
                    try:
                        jif_value = float(match.group(1))
                        if jif_value >= 90:
                            result["WoS_with_JIF-P90"] = 1
                        else:
                            result["WoS_with_JIF"] = 1
                    except ValueError:
                        pass

            # --- ตรวจสอบข้อมูลของ Scopus ---
            if "Scopus" in part:
                if "SJR-10" in part:
                    result["Scopus_SJR-10"] = 1
                if "SJR-Q1" in part:
                    result["Scopus_Q1"] = 1
                if "SJR-Q2" in part:
                    result["Scopus_Q2"] = 1
                if "SJR-Q3" in part:
                    result["Scopus_Q3"] = 1
                if "SJR-Q4" in part:
                    result["Scopus_Q4"] = 1
                if "No_Q" in part:
                    result["Scopus_No_Q"] = 1

            # --- ตรวจสอบข้อมูลของ TCI ---
            if "TCI" in part:
                if "Group1" in part:
                    result["TCI_Group1"] = 1
                if "Group2" in part:
                    result["TCI_Group2"] = 1

            # --- ตรวจสอบฐานข้อมูลอื่น ๆ ---
            if "ERIC" in part:
                result["ERIC"] = 1
            if "MathSciNet" in part:
                result["MathSciNet"] = 1
            if "Pubmed" in part:
                result["Pubmed"] = 1
            if "JSTOR" in part:
                result["JSTOR"] = 1
            if "Project_Muse" in part:
                result["Project_Muse"] = 1
            if "Other_Inter.Databases" in part:
                result["Other_Inter.Databases"] = 1
            if "National" in part and "Journal" in part:
                result["National_Journal"] = 1
        
        return result

    # ประมวลผลคอลัมน์ "Database (WoS, Scopus, TCI)" ด้วยฟังก์ชัน parse_database
    parsed_data = df_data["Database (WoS, Scopus, TCI)"].apply(parse_database)
    parsed_df = pd.DataFrame(parsed_data.tolist(), index=df_data.index)
    
    # ลบคอลัมน์ที่อาจซ้ำอยู่ใน df_data เพื่อลดปัญหาการซ้ำกันของคอลัมน์
    df_clean = df_data.drop(columns=new_columns, errors='ignore')
    df_result = pd.concat([df_clean, parsed_df], axis=1)
    
    return df_result

def get_clean_year(df_data):
    # แปลงคอลัมน์ 'Year' เป็น string แล้วลบอักขระที่ไม่ใช่ตัวเลขออก
    cleaned_year = df_data['Year'].astype(str).str.replace(r'\D', '', regex=True)
    # หากต้องการแปลงให้เป็นตัวเลข (int) ก็สามารถทำได้ดังนี้
    # cleaned_year = cleaned_year.astype(int)
    return cleaned_year


def get_clean_budget_year(df_data):
    # แปลงคอลัมน์ 'Year' ด้วย get_clean_year ซึ่งจะให้ผลเป็น string ที่มีเฉพาะตัวเลข
    year_clean_str = get_clean_year(df_data)
    # แปลงให้เป็น numeric โดยใช้ errors='coerce' เพื่อแปลงค่าที่ไม่สามารถแปลงได้เป็น NaN
    year_clean = pd.to_numeric(year_clean_str, errors='coerce')
    # แปลงคอลัมน์ 'Month' ให้เป็น numeric ด้วยเช่นกัน
    month = pd.to_numeric(df_data['Month'], errors='coerce')
    
    # ถ้า month >= 10 ให้เพิ่มปีขึ้น 1 มิฉะนั้นใช้ปีเดิม
    year_budget = np.where(month >= 10, year_clean + 1, year_clean)
    
    # แปลงผลลัพธ์เป็น pandas Series โดยใช้ Nullable Integer Type เพื่อรองรับ NaN
    return pd.Series(year_budget, index=df_data.index).astype("Int64")


def get_format_effective_date(df_data):
    def custom_format_date(val):
        # ถ้า val เป็น string และมีรูปแบบเป็น "ชื่อเดือน ปี" (เช่น "April 2023")
        if isinstance(val, str) and re.match(r'^[A-Za-z]+\s+\d{4}$', val):
            return val
        try:
            return pd.to_datetime(val).strftime('%Y-%m-%d')
        except Exception:
            return val
    
    return df_data['effective_date'].apply(custom_format_date)
