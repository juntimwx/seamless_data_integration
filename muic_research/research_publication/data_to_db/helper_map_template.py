import re
import pandas as pd

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

def get_parse_database_data(df_data):
    # รายชื่อคอลัมน์ใหม่ที่ต้องการสร้าง
    new_columns = [
        "WoS_with_JIF-P90", "WoS_with_JIF", "WoS_SC", "WoS_SS", "WoS_AH", "WoS_ES",
        "Scopus_SJR-10", "Scopus_Q1", "Scopus_Q2", "Scopus_Q3", "Scopus_Q4", "Scopus_No_Q",
        "ERIC", "MathSciNet", "Pubmed", "JSTOR", "Project_Muse", "Other_Inter.Databases",
        "TCI_Group1", "TCI_Group2", "National_Journal"
    ]
    
    # ฟังก์ชันแปลง string ในแต่ละแถว
    def parse_database(db_str):
        result = {col: 0 for col in new_columns}
        if pd.isnull(db_str):
            return result
        
        parts = db_str.split(',')
        for part in parts:
            part = part.strip()
            # --- ตรวจสอบข้อมูล WoS ---
            if "WoS" in part:
                if "(SC)" in part:
                    result["WoS_SC"] = 1
                if "(SS)" in part:
                    result["WoS_SS"] = 1
                if "(AH)" in part:
                    result["WoS_AH"] = 1
                if "(ES)" in part:
                    result["WoS_ES"] = 1

                # ตรวจสอบค่า JIF-P (เช่น (JIF-P84.4))
                match = re.search(r'JIF-P([\d\.]+)', part)
                if match:
                    try:
                        jif_value = float(match.group(1))
                        if jif_value >= 90:
                            result["WoS_with_JIF-P90"] = 1
                        else:
                            result["WoS_with_JIF"] = 1
                    except ValueError:
                        pass

            # --- ตรวจสอบข้อมูล Scopus ---
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

            # --- ตรวจสอบข้อมูล TCI ---
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

    # คำนวณ parsed data จากคอลัมน์ "Database (WoS, Scopus, TCI)"
    parsed_data = df_data["Database (WoS, Scopus, TCI)"].apply(parse_database)
    parsed_df = pd.DataFrame(parsed_data.tolist(), index=df_data.index)
    
    # เพื่อลดปัญหา column ซ้ำ ให้ลบคอลัมน์ใน new_columns ที่อาจมีอยู่แล้วใน df_data
    df_clean = df_data.drop(columns=new_columns, errors='ignore')
    df_result = pd.concat([df_clean, parsed_df], axis=1)
    return df_result
