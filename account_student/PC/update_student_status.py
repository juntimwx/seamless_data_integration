import pandas as pd
from datetime import datetime

# อ่านไฟล์ Excel
data = pd.read_excel("../../data/account_student/PC/all_pc_student_update_20250225.xlsx")
# data = pd.read_excel("../../data/account_student/PC/all_mp_student_update_20250225.xlsx")
data_current = pd.read_excel("../../data/account_student/PC/pc_current_q1_2025.xlsx") 
data_postpone = pd.read_excel("../../data/account_student/PC/pc_postpone_q1_2025.xlsx") 

df = pd.DataFrame(data)
df_current = pd.DataFrame(data_current)
df_postpone = pd.DataFrame(data_postpone)

def update_status_func(row):
    # สมมุติว่า 'std_id' คือคอลัมน์ที่ใช้เป็นรหัสนักเรียนในทั้งสอง DataFrame
    if row['std_id'] in df_current['std_id'].values:
        return 'กำลังศึกษา'
    
    if row['std_id'] in df_postpone['std_id'].values:
        return 'รักษาสภาพ'
    
    # ตรวจสอบเงื่อนไขอื่น ๆ
    if row['study_status'] == 'P':
        return 'จบการศึกษา'
    elif row['student_pc_status'] == 'RS':
        return 'ลาออก'
    elif row['student_pc_status'] == 'LE':
        return 'พ้นสภาพ'
    # elif row['student_pc_status'] == 'PP':
    #     return 'รักษาสภาพ'
    # เงื่อนไขสำหรับ 'RE' ถูกคอมเมนต์ไว้ หากต้องการใช้งานสามารถยกเลิกคอมเมนต์ได้
    # elif row['student_pc_status'] == 'RE':
    #     if row['study_status'] == 'R':
    #         return 'ลงเรียนใหม่'
    #     elif row['study_status'] == 'N':
    #         return 'กำลังศึกษา'
    else:
        return "จบการศึกษา"

df['update_status'] = df.apply(update_status_func, axis=1)
print(df.head(5))

# บันทึกไฟล์ Excel ใหม่
df.to_excel(f'~/Downloads/draft_update_status_student_account_pc_{datetime.today().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx')
# df.to_excel(f'~/Downloads/draft_update_status_student_account_mp_{datetime.today().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx')
