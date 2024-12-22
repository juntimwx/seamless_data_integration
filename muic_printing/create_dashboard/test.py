# for read data
import pandas as pd

# for connect engine database
from sqlalchemy import create_engine
from urllib.parse import quote

# for get variable from .env file
# pip install python-dotenv
from dotenv import load_dotenv
import os

# load value from file .env
load_dotenv()

# for dash and config layout application
from dash import Dash, dcc, html, Input, Output

# for plot graph
import plotly.express as px

# สร้าง connection engine สำหรับฐานข้อมูล
connect_db = create_engine(
    f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('PRINTING_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)

# read data from sql
df = pd.DataFrame(pd.read_sql('''SELECT * FROM Printing_Cleaning ORDER BY Year, Num_Month''', connect_db))

# เติมค่าขาดหายด้วย 0 และจัดกลุ่มข้อมูล
all_months = pd.DataFrame({
    'Year': sorted(df['Year'].unique().tolist() * 12),
    'Num_Month': list(range(1, 13)) * len(df['Year'].unique())
})
df_full = all_months.merge(df, on=['Year', 'Num_Month'], how='left').fillna(0)

# ตรวจสอบและแปลงคอลัมน์ที่ควรเป็นตัวเลข
numeric_columns = ['Total Printed Pages', 'Color Pages', 'Grayscale Pages', 'ColorPage_Cost', 'Grayscale_Cost', 'Total Printed Cost']
df_full[numeric_columns] = df_full[numeric_columns].apply(pd.to_numeric, errors='coerce')

# ตรวจสอบว่ามี Job Type ในข้อมูล
if 'Job Type' not in df_full.columns:
    raise ValueError("The dataset must contain a 'Job Type' column.")

# สร้างกลุ่มข้อมูลรวมตาม Job Type
df_job_grouped = df_full.groupby('Job Type')[numeric_columns].sum().reset_index()

# รวมข้อมูลที่ซ้ำกัน (ถ้ามี)
df_full_grouped = df_full.groupby(['Year', 'Num_Month'], as_index=False)[numeric_columns].sum()

# เพิ่มชื่อเดือนสำหรับการแสดงผล
month_order = [
    'October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September'
]
df_full_grouped['Month'] = df_full_grouped['Num_Month'].apply(lambda x: month_order[x - 1])

# สร้างแอป Dash พร้อมเพิ่ม external_stylesheets
app = Dash(
    __name__,
    external_stylesheets=[
        "https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css",  # Tailwind CSS
        "https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@100..900&display=swap"  # Noto Sans Thai
    ]
)

# Layout ของแอปพลิเคชัน
app.layout = html.Div(
    className="bg-gray-100 font-sans",
    children=[
        html.Div(
            className="m-8",  # เพิ่ม Padding ด้วย Tailwind CSS
            style={"fontFamily": "'Noto Sans Thai', sans-serif"},  # ใช้ฟอนต์จาก Google Fonts
            children=[
                html.H1(
                    "Printer Usage Dashboard",
                    className="text-3xl font-bold text-center mb-6"
                ),

                # Dropdown เพื่อเลือกประเภทข้อมูลที่จะดู
                html.Label(
                    "Select Metric:",
                    className="block text-lg font-medium mb-2",
                    style={"fontFamily": "'Noto Sans Thai', sans-serif"}  # กำหนดฟอนต์เฉพาะจุด
                ),
                dcc.Dropdown(
                    id='metric-dropdown',
                    options=[{'label': col, 'value': col} for col in numeric_columns],
                    value='Total Printed Pages',  # Default value
                    className="block w-full rounded-lg shadow-sm"
                ),

                # กราฟเส้นสำหรับการใช้งาน Printer ต่อเดือน
                html.Div(
                    children=[
                        html.H2(
                            "Printer Usage Over Time",
                            className="text-2xl font-semibold mt-6 mb-4"
                        ),
                        dcc.Graph(
                            id='line-chart',
                            className="rounded-lg shadow bg-white p-4"
                        )
                    ],
                    className="mt-6"
                ),

                # กราฟ Donut
                html.Div(
                    children=[
                        html.H2(
                            "Distribution of Selected Metric by Job Type",
                            className="text-2xl font-semibold mt-6 mb-4"
                        ),
                        dcc.Graph(
                            id='donut-chart',
                            className="rounded-lg shadow bg-white p-4"
                        )
                    ],
                    className="mt-6"
                ),
            ]
        )
    ]
)

# Callback สำหรับอัปเดตกราฟตามข้อมูลที่เลือก
@app.callback(
    [Output('line-chart', 'figure'),
     Output('donut-chart', 'figure')],
    Input('metric-dropdown', 'value')
)
def update_charts(selected_metric):
    # Line Chart
    line_fig = px.line(
        df_full_grouped,
        x='Month',
        y=selected_metric,
        color='Year',
        title=f"{selected_metric} by Month",
        template="plotly_white",
        category_orders={'Month': month_order},
        line_shape='linear'
    )
    line_fig.update_layout(
        xaxis_title="Month",
        yaxis_title=selected_metric,
        yaxis_tickformat=",.0f",
        modebar_remove=["zoom", "pan", "select", "lasso", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d", "hoverCompareCartesian", "hoverClosestCartesian"],
        modebar_add=["toImage"]
    )

    # กรองข้อมูลสำหรับ Donut Chart
    filtered_df = df_job_grouped[df_job_grouped[selected_metric] > 0]  # กรองเฉพาะค่ามากกว่า 0
    filtered_df = filtered_df.nlargest(2, selected_metric)  # เลือก 2 ประเภทที่มีค่ามากที่สุด

    # ตรวจสอบว่ามีข้อมูลเพียงพอสำหรับการแสดงผล
    if filtered_df.empty or len(filtered_df) < 2:
        donut_fig = px.pie(
            title="Not enough data for selected metric.",
            hole=0.4
        )
    else:
        # Donut Chart (Job Type Distribution)
        donut_fig = px.pie(
            filtered_df,
            values=selected_metric,
            names='Job Type',
            title=f"Top 2 Job Types by {selected_metric}",
            hole=0.4,
            template="plotly_white"
        )
        donut_fig.update_traces(
            textinfo='percent+label',
            showlegend=True
        )

    # กำหนด Toolbar ให้มีเฉพาะปุ่ม Download PNG
    donut_fig.update_layout(
        modebar_remove=["zoom", "pan", "select", "lasso", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d", "hoverCompareCartesian", "hoverClosestCartesian"],
        modebar_add=["toImage"]
    )

    return line_fig, donut_fig

# รันเซิร์ฟเวอร์
if __name__ == '__main__':
    app.run_server(debug=True)
