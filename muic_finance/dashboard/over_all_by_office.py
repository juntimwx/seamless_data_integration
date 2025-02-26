# for read data
import pandas as pd

# for connect engine database
from sqlalchemy import create_engine
from urllib.parse import quote

# for get variable from .env file
from dotenv import load_dotenv
import os

# load value from file .env
load_dotenv()

# for dash and config layout application
import dash
from dash import dcc, html, dash_table
from dash.dash_table.Format import Format, Scheme

# for plot graph
import plotly.express as px

# helper
from helper import abbreviate_number, get_trimester

# Import dash-bootstrap-components
import dash_bootstrap_components as dbc

# Import necessary libraries for callbacks
from dash.dependencies import Input, Output, State

# สร้าง connection engine สำหรับฐานข้อมูล
connect_db = create_engine(
    f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('FINANCE_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)

# read data from sql
df = pd.DataFrame(pd.read_sql(
    fr'''
    SELECT * 
    FROM {os.getenv('ERP_VIEW')} 
    WHERE cost_center_description = '{os.getenv('SSO_STAFF_OFFICE')}'
    ORDER BY year, month_sort
    ''', 
    connect_db
))

# สร้าง dash app ด้วย Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Athiti:wght@200;300;400;500;600;700&display=swap"]
)

# name month and order month
month_order = [
    'October', 'November', 'December', 'January', 'February', 'March', 
    'April', 'May', 'June', 'July', 'August', 'September'
]
month_mapping = {m: i for i, m in enumerate(month_order, start=1)}

# สร้างคอลัมน์ช่วยเหลือ
df['month_name'] = df['month'].apply(lambda x: pd.to_datetime(str(x), format='%m').strftime('%B'))
df['custom_month_sort'] = df['month_name'].map(month_mapping)

# get trimester
df['trimester'] = df['month'].apply(get_trimester)

# สร้าง list สำหรับแต่ละ filter (เพื่อใช้เป็น default ใน checklist)
years = sorted(df['year'].unique())
trimesters = sorted(df['trimester'].unique())
months = sorted(df['month_name'].unique(), key=lambda x: month_mapping[x])
cost_centralizes = sorted(df['CostCentralize'].unique())

# ----------------------------------------
# ฟังก์ชันสร้าง Dropdown สำหรับ Filter โดยใช้ dbc.DropdownMenu
# ----------------------------------------
def create_filter_dropdown(label_text, options, default_values, checklist_id):
    """
    สร้างโครงสร้าง Dropdown + Checklist โดยใช้ dbc.DropdownMenu
    """
    return dbc.DropdownMenu(
        label=label_text,
        children=[
            dbc.Checklist(
                options=[{'label': str(opt), 'value': str(opt)} for opt in options],
                value=[str(v) for v in default_values],
                id=checklist_id,
                inline=False,
                switch=False,
                style={"maxHeight": "150px", "overflowY": "auto", "padding": "0.5rem"}
            )
        ],
        nav=True,
        in_navbar=False,
        toggle_style={"color": "white", "backgroundColor": "#0d9488", "borderRadius": "0.5rem", "padding": "0.5rem 1rem"},
        className="me-2",
        direction="down",
        menu_variant="light"  # สามารถเปลี่ยนเป็น dark หากต้องการ
    )

# ----------------------------------------
# ส่วนประกอบตาราง
# ----------------------------------------
table_gl_figure = dash_table.DataTable(
    id='table_gl',
    columns=[
        {"name": "No.", "id": "rank"},
        {"name": "GL ID", "id": "general_ledger_id"},
        {"name": "GL Description", "id": "general_ledger_description"},
        {
            "name": "Amount",
            "id": "amount",
            "type": "numeric",
            "format": Format(group=",", precision=2, scheme=Scheme.fixed)
        }
    ],
    data=[],
    sort_action='native',
    sort_mode='multi',
    page_size=50,
    style_header={
        'background_color': '#0d9488',
        'font_weight': '600',
        'text_align': 'center',
        'color': 'white',
        'font_family': 'Athiti',
        'font_size': '14px'
    },
    style_cell={
        'text_align': 'left',
        'padding': '8px',
        'font_family': 'Athiti',
        'font_size': '14px',
        'border': '1px solid #ddd'
    },
    style_data_conditional=[
        {
            'if': {'column_id': 'amount'},
            'textAlign': 'right'
        },
        {
            'if': {'column_id': 'rank'},
            'textAlign': 'center'
        },
        {
            'if': {'row_index': 'odd'},
            'background_color': '#F9F9F9'
        },
        {
            'if': {'row_index': 'even'},
            'background_color': 'white'
        },
        {
            'if': {'state': 'active'},
            'background_color': '#D3E4F1',
            'border': '1px solid #4A90E2'
        },
        {
            'if': {'state': 'selected'},
            'background_color': '#AED6F1',
            'border': '1px solid #4A90E2'
        },
    ],
    style_table={
        'minWidth': '100%',
        'height': '900px',  # เพิ่มความสูงให้เท่ากับ 2 กราฟ และรวมพื้นว่าง
        'overflowY': 'auto',
        'overflowX': 'auto',
        'border': 'none',  # ลบกรอบพื้นหลัง
    },
    style_as_list_view=False,
)

table_group_figure = dash_table.DataTable(
    id='table_group',
    columns=[
        {"name": "No.", "id": "rank"},
        {"name": "Group ID", "id": "group_id"},
        {"name": "Group Description", "id": "group_description"},
        {
            "name": "Amount",
            "id": "amount",
            "type": "numeric",
            "format": Format(group=",", precision=2, scheme=Scheme.fixed)
        }
    ],
    data=[],
    sort_action='native',
    sort_mode='multi',
    page_size=50,
    style_header={
        'background_color': '#0d9488',
        'font_weight': '600',
        'text_align': 'center',
        'color': 'white',
        'font_family': 'Athiti',
        'font_size': '14px'
    },
    style_cell={
        'text_align': 'left',
        'padding': '8px',
        'font_family': 'Athiti',
        'font_size': '14px',
        'border': '1px solid #ddd'
    },
    style_data_conditional=[
        {
            'if': {'column_id': 'amount'},
            'textAlign': 'right'
        },
        {
            'if': {'column_id': 'rank'},
            'textAlign': 'center'
        },
        {
            'if': {'row_index': 'odd'},
            'background_color': '#F9F9F9'
        },
        {
            'if': {'row_index': 'even'},
            'background_color': 'white'
        },
        {
            'if': {'state': 'active'},
            'background_color': '#D3E4F1',
            'border': '1px solid #4A90E2'
        },
        {
            'if': {'state': 'selected'},
            'background_color': '#AED6F1',
            'border': '1px solid #4A90E2'
        },
    ],
    style_table={
        'minWidth': '100%',
        'height': '400px',  # ความสูงปกติของตารางที่สอง
        'overflowY': 'auto',
        'overflowX': 'auto',
        'border': 'none',  # ลบกรอบพื้นหลัง
    },
    style_as_list_view=False,
)

# initial empty chart
line_chart = {}
bar_chart = {}
donut_chart = {}

# ----------------------------------------
# Layout ของแอป โดยใช้ dbc.DropdownMenu และจัดวางตารางและกราฟ
# ----------------------------------------
app.layout = dbc.Container(
    fluid=True,
    className="p-4 bg-light",
    children=[
        html.H1(
            "ERP 2023",
            className="text-center mb-4",
            style={"fontFamily": "Athiti"}
        ),

        # ส่วนปุ่ม Dropdown + Checklist สำหรับ 4 filters โดยใช้ dbc.DropdownMenu
        dbc.Row(
            className="justify-content-end mb-4",
            children=[
                dbc.Col(
                    width="auto",
                    children=create_filter_dropdown(
                        label_text="Year",
                        options=years,
                        default_values=years,
                        checklist_id="year_checkbox"
                    )
                ),
                dbc.Col(
                    width="auto",
                    children=create_filter_dropdown(
                        label_text="Trimester",
                        options=trimesters,
                        default_values=trimesters,
                        checklist_id="trimester_checkbox"
                    )
                ),
                dbc.Col(
                    width="auto",
                    children=create_filter_dropdown(
                        label_text="Month",
                        options=months,
                        default_values=months,
                        checklist_id="month_checkbox"
                    )
                ),
                dbc.Col(
                    width="auto",
                    children=create_filter_dropdown(
                        label_text="Cost Centralize",
                        options=cost_centralizes,
                        default_values=cost_centralizes,
                        checklist_id="cost_checkbox"
                    )
                ),
            ]
        ),

        # จัดวางตารางและกราฟ
        dbc.Row(
            children=[
                # คอลัมน์ด้านซ้าย: ตาราง 2 แถว โดยตารางแรกมีความสูง 900px
                dbc.Col(
                    md=6,
                    children=[
                        dbc.Row(
                            className="mb-4",
                            children=[
                                dbc.Col(
                                    width=12,
                                    children=table_gl_figure  # ตำแหน่งตารางแรก
                                )
                            ]
                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    width=12,
                                    children=table_group_figure  # ตำแหน่งตารางที่สอง
                                )
                            ]
                        )
                    ]
                ),

                # คอลัมน์ด้านขวา: กราฟ 3 แถว โดยแต่ละกราฟมีความสูง 400px
                dbc.Col(
                    md=6,
                    children=[
                        dbc.Row(
                            className="mb-4",
                            children=[
                                dbc.Col(
                                    width=12,
                                    children=dbc.Card(
                                        dbc.CardBody(
                                            children=[
                                                dcc.Graph(
                                                    id='line_chart',
                                                    figure=line_chart,
                                                    style={"height": "400px"},  # กำหนดความสูงของกราฟ
                                                    config={
                                                        'modeBarButtonsToRemove': [
                                                            'zoom2d',
                                                            'pan2d',
                                                            'select2d',
                                                            'lasso2d',
                                                            'zoomIn2d',
                                                            'zoomOut2d',
                                                            'autoScale2d',
                                                            'resetScale2d',
                                                            'hoverClosestCartesian',
                                                            'hoverCompareCartesian',
                                                            'toggleSpikelines'
                                                        ],
                                                        'displaylogo': False
                                                    }
                                                )
                                            ]
                                        ),
                                        className="h-100"
                                    )
                                )
                            ]
                        ),
                        dbc.Row(
                            className="mb-4",
                            children=[
                                dbc.Col(
                                    width=12,
                                    children=dbc.Card(
                                        dbc.CardBody(
                                            children=[
                                                dcc.Graph(
                                                    id='bar_chart',
                                                    figure=bar_chart,
                                                    style={"height": "400px"},  # กำหนดความสูงของกราฟ
                                                    config={
                                                        'modeBarButtonsToRemove': [
                                                            'zoom2d',
                                                            'pan2d',
                                                            'select2d',
                                                            'lasso2d',
                                                            'zoomIn2d',
                                                            'zoomOut2d',
                                                            'autoScale2d',
                                                            'resetScale2d',
                                                            'hoverClosestCartesian',
                                                            'hoverCompareCartesian',
                                                            'toggleSpikelines'
                                                        ],
                                                        'displaylogo': False
                                                    }
                                                )
                                            ]
                                        ),
                                        className="h-100"
                                    )
                                )
                            ]
                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    width=12,
                                    children=dbc.Card(
                                        dbc.CardBody(
                                            children=[
                                                dcc.Graph(
                                                    id='pie_chart',
                                                    figure=donut_chart,
                                                    style={"height": "400px"},  # กำหนดความสูงของกราฟ
                                                    config={
                                                        'modeBarButtonsToRemove': [
                                                            'zoom2d',
                                                            'pan2d',
                                                            'select2d',
                                                            'lasso2d',
                                                            'zoomIn2d',
                                                            'zoomOut2d',
                                                            'autoScale2d',
                                                            'resetScale2d',
                                                            'hoverClosestCartesian',
                                                            'hoverCompareCartesian',
                                                            'toggleSpikelines'
                                                        ],
                                                        'displaylogo': False
                                                    }
                                                )
                                            ]
                                        ),
                                        className="h-100"
                                    )
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# ----------------------------------------
# Callback หลัก: กรองข้อมูล + อัปเดตตาราง/กราฟ
# ----------------------------------------
@app.callback(
    [
        Output('table_gl','data'),
        Output('table_group','data'),
        Output('line_chart','figure'),
        Output('bar_chart','figure'),
        Output('pie_chart','figure')
    ],
    [
        Input('year_checkbox', 'value'),
        Input('trimester_checkbox', 'value'),
        Input('month_checkbox', 'value'),
        Input('cost_checkbox', 'value')
    ]
)
def update_visuals(selected_years, selected_trimesters, selected_months, selected_cost_centralize):
    # ถ้าไม่มีการเลือกหรือเลือกว่าง, ให้ fallback กลับไปค่าทั้งหมด
    if not selected_years:
        selected_years = years
    if not selected_trimesters:
        selected_trimesters = trimesters
    if not selected_months:
        selected_months = months
    if not selected_cost_centralize:
        selected_cost_centralize = cost_centralizes

    # แปลง year เป็น int ถ้าจำเป็น
    selected_years = [int(y) for y in selected_years]

    # filter df
    filtered_df = df[
        (df['year'].isin(selected_years)) &
        (df['trimester'].isin(selected_trimesters)) &
        (df['month_name'].isin(selected_months)) &
        (df['CostCentralize'].isin(selected_cost_centralize))
    ]

    # --------------------------
    # สร้าง data สำหรับ table GL
    # --------------------------
    filtered_df_gl = (
        filtered_df.groupby(
            ['general_ledger_id','general_ledger_description'],
            as_index=False
        )
        .agg({'amount': 'sum'})
        .sort_values('amount', ascending=False)
    )
    filtered_df_gl['amount'] = filtered_df_gl['amount'].astype(float)
    filtered_df_gl['rank'] = range(1, len(filtered_df_gl) + 1)
    table_gl_data = filtered_df_gl.to_dict('records')

    # --------------------------
    # สร้าง data สำหรับ table Group
    # --------------------------
    filtered_df_group = (
        filtered_df.groupby(
            ['group_id','group_description'],
            as_index=False
        )
        .agg({'amount': 'sum'})
        .sort_values('amount', ascending=False)
    )
    filtered_df_group['amount'] = filtered_df_group['amount'].astype(float)
    filtered_df_group['rank'] = range(1, len(filtered_df_group) + 1)
    table_group_data = filtered_df_group.to_dict('records')

    # --------------------------
    # Line Chart
    # --------------------------
    df_month_amount_filtered = (
        filtered_df.groupby(['month_name','custom_month_sort','year'], as_index=False)
        .agg({'amount':'sum'})
        .sort_values('custom_month_sort', ascending=True)
    )

    line_chart_filtered = px.line(
        df_month_amount_filtered,
        x='custom_month_sort',
        y='amount',
        color='year',
        labels={
            'custom_month_sort': 'Month',
            'amount': 'Total Amount',
            'year': 'Year'
        },
        title='Cost by Month',
        category_orders={
            'custom_month_sort': sorted(month_mapping.values()),
            'year': sorted(filtered_df['year'].unique())
        },
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='ggplot2',
        markers=True,
        line_shape='spline'
    ).update_xaxes(
        tickmode='array',
        tickvals=list(month_mapping.values()),
        ticktext=month_order,
        title_font=dict(size=15, family='Athiti', color='black')
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.5,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        legend=dict(
            title='Year',
            title_font=dict(size=14, family='Athiti', color='black'),
            font=dict(size=13, family='Athiti', color='black'),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        title=dict(font=dict(size=20, family='Athiti', color='black'))
    )

    # --------------------------
    # Bar Chart
    # --------------------------
    df_office_amount_filtered = (
        filtered_df.groupby(['cost_center_description','year'], as_index=False)
        .agg({'amount':'sum'})
        .sort_values('amount', ascending=False)
    )
    # 1) รวมยอดตาม cost_center
    df_office_total = (
        df_office_amount_filtered.groupby('cost_center_description', as_index=False)
        .agg({'amount': 'sum'})
        .sort_values('amount', ascending=False)
    )
    # 2) เลือก Top 15
    df_top_offices_filtered = df_office_total.head(15)
    # 3) filter เฉพาะ Top 15
    df_filtered_office_filtered = df_office_amount_filtered[
        df_office_amount_filtered['cost_center_description'].isin(df_top_offices_filtered['cost_center_description'])
    ]
    bar_chart_filtered = px.histogram(
        df_filtered_office_filtered,
        x='cost_center_description',
        y='amount',
        color='year',
        barmode='group',
        labels={
            'cost_center_description': 'Office',
            'amount': 'Total Amount',
            'year': 'Year'
        },
        title='Cost by Office',
        template='ggplot2',
        text_auto='.2s',
        color_discrete_sequence=px.colors.qualitative.Pastel
    ).update_traces(
        textangle=360,
        textposition='outside'
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.5,
        xaxis=dict(
            title='Office',
            tickangle=-45,
            title_font=dict(size=14, family='Athiti', color='black'),
            tickfont=dict(size=14, family='Athiti', color='black')
        ),
        yaxis=dict(
            title='Amount',
            title_font=dict(size=14, family='Athiti', color='black'),
            tickfont=dict(size=10, family='Athiti', color='black'),
            showgrid=True,
            gridcolor='lightgray'
        ),
        legend=dict(
            title='Year',
            title_font=dict(size=14, family='Athiti', color='black'),
            font=dict(size=12, family='Athiti', color='black'),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        title=dict(font=dict(size=20, family='Athiti', color='black'))
    )

    # --------------------------
    # Donut Chart
    # --------------------------
    df_cost_center_filtered = (
        filtered_df.groupby(['CostCentralize'], as_index=False)
        .agg({'amount': 'sum'})
        .sort_values('amount', ascending=False)
    )
    total_amount_filtered = filtered_df['amount'].sum()
    short_total_amount_filtered = abbreviate_number(total_amount_filtered)

    donut_chart_filtered = px.pie(
        df_cost_center_filtered,
        names='CostCentralize',
        values='amount',
        hole=0.4,
        labels={
            'CostCentralize': 'Cost Centralize',
            'amount': 'Total Amount'
        },
        title='Cost Centralize',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='ggplot2'
    ).update_traces(
        textposition='inside',
        textinfo='percent+label'
    ).update_layout(
        title=dict(font=dict(size=20, family='Athiti', color='black'), x=0.5),
        legend=dict(
            title='Cost Centralize',
            title_font=dict(size=14, family='Athiti', color='black'),
            font=dict(size=12, family='Athiti', color='black'),
        ),
        annotations=[
            dict(
                text=short_total_amount_filtered,
                x=0.5,
                y=0.5,
                font=dict(size=20, family='Athiti', color='black'),
                showarrow=False
            )
        ]
    )

    return (
        table_gl_data,
        table_group_data,
        line_chart_filtered,
        bar_chart_filtered,
        donut_chart_filtered
    )

# run server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        dev_tools_ui=False,  # ปิด UI แสดง Dev Tools
    )
