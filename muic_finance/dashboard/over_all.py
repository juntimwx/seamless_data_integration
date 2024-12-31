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
import dash
from dash import dcc, html, dash_table
from dash.dash_table.Format import Format, Scheme

# for plot graph
import plotly.express as px

# helper
from helper import abbreviate_number, get_trimester

# สร้าง connection engine สำหรับฐานข้อมูล
connect_db = create_engine(
    f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('FINANCE_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)

# read data from sql
df = pd.DataFrame(pd.read_sql(fr'''SELECT * FROM {os.getenv('ERP_VIEW')} ORDER BY year, month_sort''', connect_db))

# create dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css",  # Tailwind CSS
        "https://fonts.googleapis.com/css2?family=Athiti:wght@200;300;400;500;600;700&display=swap"  # Athiti
    ]
)

# name month and order month
month_order = [
    'October', 'November', 'December', 'January', 'February', 'March', 
    'April', 'May', 'June', 'July', 'August', 'September'
]
month_mapping = {month: index for index, month in enumerate(month_order, start=1)}

# map month with month sort when %m = month month integer such as 1 2 3 ... and %B month name such as January February ...
df['month_name'] = df['month'].apply(lambda x: pd.to_datetime(str(x), format='%m').strftime('%B'))
df['custom_month_sort'] = df['month_name'].map(month_mapping)

# create unique options for each dropdown
# get trimester
df['trimester'] = df['month'].apply(get_trimester)
years = sorted(df['year'].unique())
trimesters = sorted(df['trimester'].unique())
months = sorted(df['month_name'].unique(), key=lambda x:month_mapping[x])
cost_centralizes = sorted(df['CostCentralize'].unique())

# define the filter
filters = html.Div(
    className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6",
    children=[
        # year dropdown
        html.Div(
            children=[
                html.Label("Year",className="block text-black"),
                dcc.Dropdown(
                    id='filter_year',
                    options=[{'label': year, 'value': year} for year in years],
                    value=years,
                    multi=True,
                    placeholder="Select Year"
                )
            ]
        ),
        # trimester dropdown
        html.Div(
            children=[
                html.Label("Trimester",className="block text-black"),
                dcc.Dropdown(
                    id='filter_trimester',
                    options=[{'label': trimester, 'value': trimester} for trimester in trimesters],
                    value=trimesters,
                    multi=True,
                    placeholder="Select Trimester"
                )
            ]
        ),
        # month dropdown
        html.Div(
            children=[
                html.Label("Month",className="block text-black"),
                dcc.Dropdown(
                    id='filter_month',
                    options=[{'label': month, 'value': month} for month in months],
                    value=months,
                    multi=True,
                    placeholder="Select Month"
                )
            ]
        ),
        # const centralize dropdown
        html.Div(
            children=[
                html.Label("Cost centralize",className="block text-black"),
                dcc.Dropdown(
                    id='filter_cost_centralize',
                    options=[{'label': cost_centralize, 'value': cost_centralize} for cost_centralize in cost_centralizes],
                    value=cost_centralizes,
                    multi=True,
                    placeholder="Select Cost centralize"
                )
            ]
        )
    ]
)

# create table 
# initial table_gl setup (to be updated via callback)
table_gl_figure =  dash_table.DataTable(
    id='table_gl',
    columns=[
        {"name":"No.","id":"rank"},
        {"name":"GL ID","id":"general_ledger_id"},
        {"name":"GL Description","id":"general_ledger_description"},
        {"name": "Amount","id": "amount","type": "numeric","format": Format(    
                group=",",        # เพิ่มการคั่นหลักพันด้วยจุลภาค    
                precision=2,      # จำนวนทศนิยม 2 ตำแหน่ง    
                scheme=Scheme.fixed
            )
        }
    ],
    data=[], # initial empty
    sort_action='native',
    sort_mode='multi',
    page_size=50,
    style_header={
        'background_color': '#0d9488',
        'font_weight': '600',
        'text_align': 'center',
        'color': 'white',
        'font_family':'Athiti',
        'font_size':'14px'
    },
    style_cell={
        'text_align': 'left',
        'padding': '8px',
        'font_family':'Athiti',
        'font_size':'14px',
        'border':'1px solid #ddd'
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
            'border':'1px solid #4A90E2'
        },
        {
            'if': {'state': 'selected'},
            'background_color': '#AED6F1',
            'border':'1px solid #4A90E2'
        },
    ],
    style_table={
        'minWidth': '100%',
        'height': '900px',  # กำหนดความสูงคงที่สำหรับตาราง Group
        'overflowY': 'auto',   # เปิดการเลื่อนแนวตั้ง
        'overflowX': 'auto',
        'border': '1px solid #ddd',  # เพิ่มขอบรอบตาราง
        'borderRadius': '5px'  # มุมมนของขอบตาราง
    },
    style_as_list_view=False,
)

table_group_figure = dash_table.DataTable(
    id='table_group',
    columns=[
        {"name":"No.","id":"rank"},
        {"name":"Group ID","id":"group_id"},
        {"name":"Group Description","id":"group_description"},
        {"name":"Amount","id":"amount","type":"numeric","format":Format(
                group=",",        # เพิ่มการคั่นหลักพันด้วยจุลภาค
                precision=2,      # จำนวนทศนิยม 2 ตำแหน่ง
                scheme=Scheme.fixed
            )
        }
    ],
    data=[], # initial empty
    sort_action='native',
    sort_mode='multi',
    page_size=50,
    style_header={
        'background_color': '#0d9488',
        'font_weight': '600',
        'text_align': 'center',
        'color': 'white',
        'font_family':'Athiti',
        'font_size':'14px'
    },
    style_cell={
        'text_align': 'left',
        'padding': '8px',
        'font_family':'Athiti',
        'font_size':'14px',
        'border':'1px solid #ddd'
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
            'border':'1px solid #4A90E2'
        },
        {
            'if': {'state': 'selected'},
            'background_color': '#AED6F1',
            'border':'1px solid #4A90E2'
        },
    ],
    style_table={
        'min_width': '100%',
        'max_height': '450px',  # กำหนดความสูงคงที่สำหรับตาราง Group
        'overflowY': 'auto',   # เปิดการเลื่อนแนวตั้ง
        'overflowX': 'auto',
        'border': '1px solid #ddd',  # เพิ่มขอบรอบตาราง
        'borderRadius': '5px'  # มุมมนของขอบตาราง
    },
    style_as_list_view=False,
)

# initial empty chart (to be updated via callback)
line_chart = {}
bar_chart = {}
donut_chart = {}

# create app layout
app.layout = html.Div(
    className="w-full mx-2 p-6 bg-slate-200",
    children=[
        html.H1(
            "ERP 2023",
            className="text-4xl font-normal mb-8 text-center text-gray-800"
        ),
        # filter => dropdown layout
        filters,
        # display table and chart
        html.Div(
            className="grid grid-cols-1 md:grid-cols-2 gap-4",
            children=[
                html.Div(
                    className="flex flex-col gap-4",
                    children=[
                        html.Div(
                            className="bg-white rounded p-2",
                            children=[
                                table_gl_figure
                            ]
                        ),
                        html.Div(
                            className="bg-white rounded p-2",
                            children=[
                                table_group_figure
                            ]
                        ),
                    ]
                ),
                html.Div(
                    className="flex flex-col gap-4",
                    children=[
                        html.Div(
                            className="bg-white rounded p-2",
                            children=[
                                dcc.Graph(
                                    id='line_chart',
                                    figure=line_chart,
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
                        html.Div(
                            className="bg-white rounded p-2",
                            children=[
                                dcc.Graph(
                                    id='bar_chart',
                                    figure=bar_chart,
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
                        html.Div(
                            className="bg-white rounded p-2",
                            children=[
                                dcc.Graph(
                                    id='pie_chart',
                                    figure=donut_chart,
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
                        )
                    ]
                )
            ]
            
        )
    ]
)

# callback to update table and graphs based on filters
from dash.dependencies import Input, Output

@app.callback(
    [
        Output('table_gl','data'),
        Output('table_group','data'),
        Output('line_chart','figure'),
        Output('bar_chart','figure'),
        Output('pie_chart','figure')
    ],
    [
        Input('filter_year', 'value'),
        Input('filter_trimester', 'value'),
        Input('filter_month', 'value'),
        Input('filter_cost_centralize', 'value')
    ]
)

def update_visuals(selected_years, selected_trimesters,selected_months, selected_cost_centralize):
    # handle cases where no filter is selected
    if not selected_years:
        selected_years = years
    if not selected_trimesters:
        selected_trimesters = trimesters
    if not selected_months:
        selected_months = months
    if not selected_cost_centralize:
        selected_cost_centralize = cost_centralizes
    
    # filter the dataframe based on selections
    filtered_df = df[
        (df['year'].isin(selected_years)) &
        (df['trimester'].isin(selected_trimesters)) &
        (df['month_name'].isin(selected_months)) &
        (df['CostCentralize'].isin(selected_cost_centralize))
    ]

    
    # update gl table
    filtered_df_gl = (
        filtered_df.groupby(
            ['general_ledger_id','general_ledger_description'],
            as_index=False
        )
        .aggregate({'amount': 'sum'})
        .sort_values('amount', ascending=False)
    )
    filtered_df_gl['amount'] = filtered_df_gl['amount'].astype(float)
    filtered_df_gl['rank'] = range(1, len(filtered_df_gl) + 1)
    
    table_gl_data = filtered_df_gl.to_dict('records')
    
    # update group table
    filtered_df_group = (
        filtered_df.groupby(
            ['group_id','group_description'],
            as_index=False
        )
        .aggregate({'amount': 'sum'})
        .sort_values('amount', ascending=False)
    )
    filtered_df_group['amount'] = filtered_df_group['amount'].astype(float)
    filtered_df_group['rank'] = range(1, len(filtered_df_group) + 1)
    
    table_group_data = filtered_df_group.to_dict('records')
    
    # update line chart
    df_month_amount_filtered = (
        filtered_df.groupby(
        ['month_name','custom_month_sort','year'],
        as_index=False
    )
    .aggregate({'amount': 'sum'})
    .sort_values('custom_month_sort', ascending=False)
    )

    # line chart
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
        title='Cost by month',
        category_orders={
            'custom_month_sort': list(month_mapping.values()),
            'year':sorted(filtered_df['year'].unique())
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
            x=0.1,
            # bgcolor='rgba(0,0,0,0)',
            # bordercolor='lightgray',
            # borderwidth=1
        ),
        title=dict(
            font=dict(size=20, family='Athiti', color='black'),
        )
    )
    
    # update bar chart
    df_office_amount_filtered = (
        filtered_df.groupby(
            ['cost_center_description','year'],
            as_index=False
        )
        .aggregate({'amount': 'sum'})
        .sort_values('amount', ascending=False)
    )

    # 1. calculate total per office
    df_office_total = (
        df_office_amount_filtered.groupby(
            'cost_center_description'
            , as_index=False
        )
        .aggregate({'amount': 'sum'})
        .sort_values('amount', ascending=False)
    )

    # 2. select top 15 office
    df_top_offices_filtered = df_office_total.head(15)

    # 3. filter data for Top offices
    df_filtered_office_filtered = df_office_amount_filtered[
        df_office_amount_filtered['cost_center_description'].isin(df_top_offices_filtered['cost_center_description'])
    ]

    # create bar chart
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
        text_auto='.2s',  # แสดงตัวเลขบนแท่ง
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
            # bgcolor='rgba(0,0,0,0)',
            # bordercolor='lightgray',
            # borderwidth=1
        ),
        title=dict(
            font=dict(size=20, family='Athiti', color='black'),
        )
    )
    
    # update donut chart
    df_cost_center_filtered = (
        filtered_df.groupby(
            ['CostCentralize'],
            as_index=False,
        )
        .aggregate({'amount': 'sum'})
        .sort_values('amount', ascending=False)
    )
    total_amount_filtered = filtered_df['amount'].sum()
    short_total_amount_filtered = abbreviate_number(total_amount_filtered)
    
    donut_chart_filtered = px.pie(
        df_cost_center_filtered,
        names='CostCentralize',
        values='amount',
        hole=0.4,  # กำหนดขนาดของรูกลาง (0.4 หมายถึง 40% ของรัศมี)
        labels={
            'CostCentralize' : 'Cost Centralize',
            'amount': 'Total Amount',
        },
        title='Cost Centralize',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='ggplot2'
    ).update_traces(
        textposition='inside',
        textinfo='percent+label'
    ).update_layout(
        title=dict(
            font=dict(size=20, family='Athiti', color='black'),
            x=0.5
        ),
        legend=dict(
            title='Cost Centralize',
            title_font=dict(size=14, family='Athiti', color='black'),
            font=dict(size=12, family='Athiti', color='black'),
            # bgcolor='rgba(0,0,0,0)',
            # bordercolor='lightgray',
            # borderwidth=1
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
    return table_gl_data, table_group_data, line_chart_filtered, bar_chart_filtered, donut_chart_filtered

# run server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        dev_tools_ui=False,  # ปิด UI แสดง Dev Tools
        # dev_tools_props_check=True,
        # dev_tools_silence_routes_logging=True
    )

