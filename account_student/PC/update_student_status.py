import pandas as pd
from datetime import datetime

# data = pd.read_excel("../../data/account_student/PC/all_pc_student_update_20250225.xlsx")
data = pd.read_excel("../../data/account_student/PC/all_mp_student_update_20250225.xlsx")

df = pd.DataFrame(data)


def update_status_func(row):
    # ถ้าสถานะการศึกษาเป็น P หรือ Pass หมายถึงจบการศึกษา
    if row['study_status'] == 'P':
        return 'จบการศึกษา'
    elif row['student_pc_status'] == 'RS':
        return 'ลาออก'
    elif row['student_pc_status'] == 'LE':
        return 'พ้นสภาพ'
    elif row['student_pc_status'] == 'PP':
        return 'รักษาสภาพ'
    elif row['student_pc_status'] == 'RE':
        if row['study_status'] == 'R':
            return 'ลงเรียนใหม่'
        elif row['study_status'] == 'N':
            return 'กำลังศึกษา'
    else:
        return row.get('student_pc_status', None)
    
df['update_status'] = df.apply(update_status_func, axis=1)
print(df.head(5))

# df.to_excel(f'~/Downloads/draft_update_status_student_account_pc_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx')
df.to_excel(f'~/Downloads/draft_update_status_student_account_mp_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx')