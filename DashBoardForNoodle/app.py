# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import random
import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import psycopg2 as pg
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import calendar

# Multi-dropdown options. Read static values from controls.py
from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create controls
county_options = [
    {"label": str(COUNTIES[county]), "value": str(county)} for county in COUNTIES
]

well_status_options = [
    {"label": str(WELL_STATUSES[well_status]), "value": str(well_status)}
    for well_status in WELL_STATUSES
]

well_type_options = [
    {"label": str(WELL_TYPES[well_type]), "value": str(well_type)}
    for well_type in WELL_TYPES
]

def generate_color_list(number_of_colors):
    color_list = []
    for _ in range(number_of_colors):
        rgb = ''
        for _ in 'RGB': 
            i = random.randrange(0, 2**8) 
            rgb += i.to_bytes(1, "big").hex() 
        rgb = "#" + rgb
        color_list.append(rgb)
    return color_list 


# Load data from DB
db_conn = pg.connect("host='localhost' dbname=sfstock user=siwan password='psw1101714'")
cursor = db_conn.cursor()
select_query = "select * from inventory_noodleusage"
df = pd.read_sql_query(select_query, con=db_conn)
df['sf_code'] = df['sf_code'].str.strip()  # remove blank space 

df_code_list = pd.DataFrame(df['sf_code'].unique())
df_code_list.columns = ['sf_code']
df_code_list['simple_name'] = ''
for i in range(len(df_code_list)):
    df_code_list.iat[i, 1] = (df[df['sf_code'] == df_code_list.iat[i, 0]].head(1)).iat[0, 4]  

# Create code & code name dictionary
code_product_options = [
    {"label": code_product[2], "value": code_product[1].strip()} for code_product in df_code_list.itertuples()
]

# customer_list need to be generated upon request
df_customer_list = pd.DataFrame(df['customer'].unique())
df_customer_list.columns = ['customer']
color_list = generate_color_list(len(df_customer_list))
customer_color = {}
for i in range(len(df_customer_list)):
    customer_color[df_customer_list.iat[i, 0]] = color_list[i]    

# Create customer & color dictionary
customer_options = [
    {"label": key, "value": key } for key in customer_color
]
customer_options.insert(0, {"label": "ALL", "value": "ALL"})


# Create global chart template
layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=30, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    font=dict(
        family="Courier New, monospace",
        fontweight="bold",
        color="#111111"
    )
    #mapbox=dict(
    #    accesstoken=mapbox_access_token,
    #    style="light",
    #    center=dict(lon=-78.05, lat=42.54),
    #    zoom=7,
    #),
)

# Create app layout#print(c_month)
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        html.Div(id="output-clientside"),      
        html.Div(
            [                
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(
                                    "Noodle",
                                    style={"margin-bottom": "0px", "margin-top":"0px"},
                                ),
                                html.H5(
                                    "Dispatch Overview", style={"margin-top": "10px"}
                                ),
                            ]
                        )
                    ],
                    className="twelve column",
                    id="title",
                ),               
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [html.P("TODAY :  ", className="summary-label"), html.P(id="current_day", className="summary-result")],
                                            id="div1",                                            
                                            className="flex-display",
                                        ),
                                        html.Div(
                                            [html.P("This Week Dispatch :  ", className="summary-label"), html.P(id="this_week_dispatch", className="summary-result")],
                                            id="div2",                                            
                                            className="flex-display",
                                        ),
                                        html.Div(
                                            [html.P("Last Week Dispatch :  ", className="summary-label"), html.P(id="last_week_dispatch", className="summary-result")],
                                            id="div4",
                                            className="flex-display",
                                        ),
                                        html.Div(
                                            [html.P("This Month Dispatch :  ", className="summary-label"), html.P(id="this_month_dispatch", className="summary-result")],
                                            id="div3",
                                            className="flex-display",
                                        ),                                        
                                        html.Div(
                                            [html.P("Last Month Dispatch :  ", className="summary-label"), html.P(id="last_month_dispatch", className="summary-result")],
                                            id="div5",
                                            className="flex-display",
                                        ),
                                    ],
                                    className="mini_container",                                    
                                ),                                
                            ]                                                     
                        ),
                        html.P(
                            "Filter by Date :",
                            className="summary-label control_label",
                        ),
                        dcc.RangeSlider(
                            id="year_slider",
                            min=2017,
                            max=2020,
                            step=1,
                            marks={
                                2017: '2017',
                                2020: '2020'
                            },
                            value=[2017, 2020],
                            className="dcc_control",
                        ),
                        html.P("Filter by Products:", className="summary-label control_label"),                        
                        dcc.Dropdown(
                            id="product_code",
                            options=code_product_options,
                            #multi=True,
                            value="KONO01",  # changed on 11/6
                            className="dcc_control",
                        ),                                                           
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [                        
                        html.Div(
                            [dcc.Graph(id="count_graph")],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display"
        ),
        
        html.Div(
            [   
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="dispatch_customer_graph")],
                            className="pretty_container",
                        ),
                    ],
                    className="twelve columns",
                ),                                                                 
            ],
            className="row flex-display",
        ),  

        html.Div(
            [                                 
                html.Div(
                
                    [dcc.Graph(id="dispatch_customer_pie_graph")],
                    className="pretty_container four columns",
                ),   

                html.Div(
                    [                        
                        html.P("Select Customer: ", className="control_label"), 
                        dcc.Dropdown(
                            id='noodle_customer',                            
                            options=customer_options,
                            value='ALL'
                        ),
                    ],
                    className="two columns",
                ),
                html.Div(
                    [dcc.Graph(id="yearly_comparison_graph")],
                    className="pretty_container six columns",
                ),              

            ],
            className="row flex-display",
        ),                
                
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Helper functions
def filter_dataframe(df, product_code, year_slider):    
    if year_slider[0] == year_slider[1]:
        dff = df[
            (df["sf_code"] == product_code)
            & (df["update_date"] >= dt.datetime(year_slider[0], 1, 1).date())
            & (df["update_date"] <= dt.datetime(year_slider[1], 12, 31).date())
        ]
        return dff
    else:
        dff = df[
            (df["sf_code"] == product_code)
            & (df["update_date"] >= dt.datetime(year_slider[0], 1, 1).date())
            & (df["update_date"] <= dt.datetime(year_slider[1], 12, 31).date())
        ]
        return dff


@app.callback(
    [Output('current_day', 'children'), Output('this_week_dispatch', 'children'), Output('this_month_dispatch', 'children'), 
     Output('last_week_dispatch', 'children'), Output('last_month_dispatch', 'children')],
    [
        Input("product_code", "value"),        
        Input("year_slider", "value"),
    ],
)
def generate_summary(product_code, year_slider):    
    dff = filter_dataframe(df, product_code, [year_slider[0], year_slider[1]])
    temp_df = dff[["update_date", "qty"]]                   
    #today = datetime.date.today()
    today = dt.date(2020, 10, 5)

    distance_to_sunday = (today.weekday() + 1) % 7  
    this_sunday = today - dt.timedelta(distance_to_sunday)
    last_sunday = today - dt.timedelta(distance_to_sunday + 7)   

    df_previous_week = temp_df[temp_df['update_date'] == last_sunday]
    df_current_week = temp_df[temp_df['update_date'] == this_sunday]
    this_week_dispatch = str("{:.2f}".format(df_current_week['qty'].sum())) 
    last_week_dispatch = str("{:.2f}".format(df_previous_week['qty'].sum())) 

    # To get current and next month
    current_month = today
    previous_month = current_month + relativedelta(months=-1)
    next_month = current_month + relativedelta(months=1)

    first_day_current_month = current_month.replace(day=1) 
    first_day_previous_month = previous_month.replace(day=1)
    first_day_next_month = next_month.replace(day=1)

    p_month = first_day_previous_month
    c_month = first_day_current_month
    n_month = first_day_next_month
    
    df_current_month = temp_df[(temp_df['update_date'] >= c_month) & (temp_df['update_date'] < n_month)]
    df_previous_month = temp_df[(temp_df['update_date'] >= p_month) & (temp_df['update_date'] < c_month)]
    this_month_dispatch = str("{:.2f}".format(df_current_month['qty'].sum())) 
    last_month_dispatch = str("{:.2f}".format(df_previous_month['qty'].sum())) 
        
    current_day = today.strftime("%d/%m/%Y") 
    #date_range = str(start_date) + ' ~ ' + str(end_date)    
    return current_day, this_week_dispatch, this_month_dispatch, last_week_dispatch, last_month_dispatch


# Selectors -> count graph
@app.callback(
    Output("count_graph", "figure"),
    [
        Input("product_code", "value"),        
        Input("year_slider", "value"),
    ],
)
def dispatch_total_qty(product_code, year_slider):
    layout_count = copy.deepcopy(layout)

    dff = filter_dataframe(df, product_code, [2017, 2020])
    temp_df = dff[["update_date", "sf_code", "qty"]]
    grouped_df = temp_df.groupby(['update_date', 'sf_code']).agg('sum')
    reindex_df = grouped_df.reset_index()    
    
    colors = []    
    for i in list(reindex_df['update_date'].unique()):    
        if i.year >= int(year_slider[0]) and i.year <= int(year_slider[1]):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")    

    data = [     
        dict(                           
            type="bar",
            x=reindex_df['update_date'],
            y=reindex_df["qty"],                        
            name="All Wells",
            marker=dict(color=colors),
        ),
    ]

    layout_count["title"] = "Total Dispatch QTY"
    layout_count["xaxis"] = dict(title='Time')
    layout_count["yaxis"] = dict(title='QTY (ctn)')
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True
    
    figure = dict(data=data, layout=layout_count)
    return figure


@app.callback(
    Output("dispatch_customer_graph", "figure"),
    [
        Input("product_code", "value"),        
        Input("year_slider", "value"),    
    ],
)
def dispatch_per_customers(product_code, year_slider):
    layout_individual = copy.deepcopy(layout)

    dff = filter_dataframe(df, product_code, [year_slider[0], year_slider[1]])
    temp_df = dff[["customer", "update_date", "sf_code", "qty"]]    
    grouped_df = temp_df.groupby(['customer', 'update_date']).agg('sum')    
    reindex_df = grouped_df.reset_index()
    
    data = []
    for customer in df_customer_list['customer'].unique():
        customer_df = reindex_df[reindex_df['customer'] == customer]
        customer_df = customer_df.reset_index()            
        data.append(
            dict(
                ype="scatter",
                mode="lines+markers",
                name=customer,
                x=customer_df['update_date'],
                y=customer_df['qty'],
                line=dict(shape="spline", smoothing=2, width=1, color=customer_color[customer]),
                marker=dict(symbol="diamond-open"),
            )
        )   

    layout_individual["title"] = 'Dispatch QTY per customer (Line)'
    layout_individual["xaxis"] = dict(title='Time')
    layout_individual["yaxis"] = dict(title='QTY (ctn)')

    figure = dict(data=data, layout=layout_individual)
    return figure


@app.callback(
    Output("dispatch_customer_pie_graph", "figure"),
    [
        Input("product_code", "value"),        
        Input("year_slider", "value"),    
    ],
)
def dispatch_per_customers_pie_graph(product_code, year_slider):    
    dff = filter_dataframe(df, product_code, [year_slider[0], year_slider[1]])
    temp_df = dff[["customer", "update_date", "sf_code", "qty"]]    
    grouped_df = temp_df.groupby(['customer', 'update_date']).agg('sum')    
    reindex_df = grouped_df.reset_index()

    fig = px.pie(reindex_df, values='qty', names='customer', title='Dispatch QTY per customer (Pie)')        
    figure = fig
    return figure


@app.callback(
    Output("yearly_comparison_graph", "figure"),
    [    
        Input("product_code", "value"),   
        Input("noodle_customer", "value")
    ]
)
def comparison_graph_by_year(product_code, noodle_customer):
    layout_yearly_graph = copy.deepcopy(layout)

    dff = filter_dataframe(df, product_code, [2017, 2020])
    temp_df = dff[["customer", "update_date", "sf_code", "unit", "qty"]]    
    temp_df['update_date'] = pd.to_datetime(temp_df['update_date']) 
    #year_df = temp_df['dispatch_date'].dt.year  # to check if year's data exists
    # error handling when no data in dataframe
    #print(temp_df)
    if noodle_customer == 'ALL':  # total                                
        layout_yearly_graph["title"] = 'Yearly Comparison of Dispatch QTY'        
    else: 
        temp_df = temp_df[temp_df['customer'] == noodle_customer]        
        layout_yearly_graph["title"] = 'Yearly Comparison (' + noodle_customer + ')'            
        #print(noodle_customer)

    if len(temp_df) > 0:
        year_df = temp_df['update_date'].dt.year  # to check if year's data exists        
        grouped_df = temp_df.groupby([temp_df.update_date.dt.month,temp_df.update_date.dt.year]).agg(sum).unstack()
        #grouped_df = temp_df.groupby(['dispatch_date']).agg('sum')    
        reindex_df = grouped_df.reset_index()          
        col_list = ['update_date']        
        if 2019 in year_df.unique():
            col_list.append('2019')
        if 2020 in year_df.unique():
            col_list.append('2020')

        #reindex_df.columns = ['dispatch_month', '2017','2018','2019','2020']
        reindex_df.columns = col_list        
        if '2019' in reindex_df.columns:
            df_2019 = reindex_df[['update_date', '2019']]
        else:
            df_2019 = pd.DataFrame(columns=['update_date', '2019'])
        if '2020' in reindex_df.columns:
            df_2020 = reindex_df[['update_date', '2020']]
        else:
            df_2020 = pd.DataFrame(columns=['update_date', '2020'])
        

        data = [                    
            dict(
                type="scatter",
                mode="lines+markers",
                name="2019",
                x=df_2019['update_date'].apply(lambda x: calendar.month_abbr[x]),            
                y=df_2019['2019'],                     
                line=dict(shape="spline", smoothing=2, width=1, color="#8bc34a"),
                marker=dict(symbol="diamond-open"),
            ),   
            dict(
                type="scatter",
                mode="lines+markers",
                name="2020",
                x=df_2020['update_date'].apply(lambda x: calendar.month_abbr[x]),            
                y=df_2020['2020'],                   
                line=dict(shape="spline", smoothing=2, width=1, color="#ff5722"),
                marker=dict(symbol="diamond-open"),
            ),             
        ]    

        layout_yearly_graph["xaxis"] = dict(title='Month')
        layout_yearly_graph["yaxis"] = dict(title='QTY (ctn)')
    
        figure = dict(data=data, layout=layout_yearly_graph)
        return figure                      
    figure = dict(data=None, layout=None)
    return figure


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8051, debug=True)
