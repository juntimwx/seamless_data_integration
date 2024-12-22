import pandas as pd
import plotly.graph_objects as go

# สร้างตัวอย่างข้อมูลยอดขาย
data = {
    'ปี': [2022, 2022, 2022, 2023, 2023, 2023],
    'เดือน': ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'มกราคม', 'กุมภาพันธ์', 'มีนาคม'],
    'ยอดขาย': [1200.50, 1500.75, 1300.25, 1400.60, 1600.80, 1550.45]
}

# ลำดับเดือนที่ถูกต้อง
month_order = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
               'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']

# แปลงข้อมูลเป็น DataFrame
df = pd.DataFrame(data)

# ตั้งค่าคอลัมน์ "เดือน" ให้เป็นประเภท Categorical พร้อมระบุลำดับ
df['เดือน'] = pd.Categorical(df['เดือน'], categories=month_order, ordered=True)

# Pivot ข้อมูลให้เป็นรูปแบบยอดขายต่อเดือนในแต่ละปี
df_pivot = df.pivot(index='เดือน', columns='ปี', values='ยอดขาย')

# สร้างกราฟเส้นเปรียบเทียบ
fig = go.Figure()

# เพิ่มเส้นข้อมูลสำหรับแต่ละปี
for year in df_pivot.columns:
    fig.add_trace(go.Scatter(
        x=df_pivot.index,  # เดือน
        y=df_pivot[year],  # ยอดขาย
        mode='lines+markers',
        name=str(year)
    ))

# เพิ่มการตั้งค่ากราฟ
fig.update_layout(
    title='ยอดขายต่อเดือนในแต่ละปี',
    xaxis_title='เดือน',
    yaxis_title='ยอดขาย (บาท)',
    legend_title='ปี',
    xaxis=dict(categoryorder='array', categoryarray=month_order),  # เรียงเดือนตามลำดับ
)

# แสดงกราฟ
fig.show()
