# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
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

customer_color = {
    'YAYOI_Chatswood' : "#009688", 
    'YAYOI_Galeries' : "#9c27b0", 
    'YAYOI_Garden' : "#607d8b", 
    'Hottomotto' : "#ffab91",
    'YAYOI_Westfield_Sydney' : "#8bc34a", 
    'Plenus_Aus_Office' : "#3e2723", 
    'Plenus_Aus(Cash)' : "#69f0ae",
    'YAYOI_Market_City' : "#ff5722", 
    'Plenus_Central_Kitchen' : "#ff1744",
    'YAYOI_World_Square' : "#00b0ff", 
    'YAYOI_Hurstville' : "#f9a825"
}
# Load data from DB
db_conn = pg.connect("host='localhost' dbname=sfstock user=siwan password='psw1101714'")
cursor = db_conn.cursor()
select_query = "select * from inventory_noodleusage"
df = pd.read_sql_query(select_query, con=db_conn)
df['sf_code'] = df['sf_code'].str.strip()  # remove blank space 

df_customer_list = df['customer'].unique()
df_code_list = pd.DataFrame(df['sf_code'].unique())
df_code_list.columns = ['sf_code']
df_code_list['product_name'] = ''
for i in range(len(df_code_list)):
    df_code_list.iat[i, 1] = (df[df['sf_code'] == df_code_list.iat[i, 0]].head(1)).iat[0, 6]  

code_product_options = [
    {"label": code_product[2], "value": code_product[1].strip()} for code_product in df_code_list.itertuples()
]

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

# Create app layout
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
                                            [html.P("Total Dispatch :  ", className="summary-label"), html.P(id="total_dispatch", className="summary-result")],
                                            id="div1",                                            
                                            className="flex-display",
                                        ),
                                        html.Div(
                                            [html.P("Date Range :  ", className="summary-label"), html.P(id="date_range", className="summary-result")],
                                            id="div2",
                                            className="flex-display",
                                        ),
                                        html.Div(
                                            [html.P("AVG Dispatch per Week :  ", className="summary-label"), html.P(id="avg_dispatch_week", className="summary-result")],
                                            id="div3",
                                            className="flex-display",
                                        ),
                                        html.Div(
                                            [html.P("AVG Dispatch per Month :  ", className="summary-label"), html.P(id="avg_dispatch_month", className="summary-result")],
                                            id="div4",
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
                            value="PD01",  # changed on 11/6
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
            className="row flex-display",
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
                        html.P("Select Graph: ", className="control_label"), 
                        dcc.Dropdown(
                            id='plenus_branch',                            
                            options=[                                                              
                                        {"label": "ALL", "value": "ALL"},                   
                                        {"label": 'YAYOI Chatswood', "value" : 'YAYOI_Chatswood'}, 
                                        {"label": 'YAYOI Galeries', "value" : 'YAYOI_Galeries'}, 
                                        {"label": 'YAYOI Garden', "value" : 'YAYOI_Garden'}, 
                                        {"label": 'Hottomotto', "value" : 'Hottomotto'},
                                        {"label": 'YAYOI Westfield Sydney', "value" : 'YAYOI_Westfield_Sydney'}, 
                                        {"label": 'Plenus Aus Office', "value" : 'Plenus_Aus_Office'}, 
                                        {"label": 'Plenus Aus(Cash)', "value" : 'Plenus_Aus(Cash)'},
                                        {"label": 'YAYOI Market City', "value" : 'YAYOI_Market_City'}, 
                                        {"label": 'Plenus Central Kitchen', "value" : 'Plenus_Central_Kitchen'},
                                        {"label": 'YAYOI World Square', "value" : 'YAYOI_World_Square'}, 
                                        {"label": 'YAYOI Hurstville', "value" : 'YAYOI_Hurstville'}           
                                    ],
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
            & (df["usage_month"] >= dt.datetime(year_slider[0], 1, 1).date())
            & (df["usage_month"] <= dt.datetime(year_slider[1], 12, 31).date())
        ]
        return dff
    else:
        dff = df[
            (df["sf_code"] == product_code)
            & (df["usage_month"] >= dt.datetime(year_slider[0], 1, 1).date())
            & (df["usage_month"] <= dt.datetime(year_slider[1], 12, 31).date())
        ]
        return dff


@app.callback(
    [Output('total_dispatch', 'children'), Output('date_range', 'children'), 
     Output('avg_dispatch_week', 'children'), Output('avg_dispatch_month', 'children')],
    [
        Input("product_code", "value"),        
        Input("year_slider", "value"),
    ],
)
def generate_summary(product_code, year_slider):    

    dff = filter_dataframe(df, product_code, [year_slider[0], year_slider[1]])
    temp_df = dff[["usage_month", "qty"]]
    total_dispatch_qty = temp_df['qty'].sum()
    start_date = temp_df['usage_month'].min()
    end_date = temp_df['usage_month'].max()

    #delta_dates = end_date - start_date
    diff_days = (end_date - start_date).days
    
    #diff_days = delta_dates / np.timedelta64(1,'D')
    #diff_days = delta_dates.total_seconds() / (3600 * 24) # 2
    #diff_days = delta_dates.dt.seconds / (3600 * 24) # 2


    #grouped_df = temp_df.groupby(['dispatch_date', 'sf_code']).agg('sum')
    #reindex_df = grouped_df.reset_index()               

    total_dispatch = str(total_dispatch_qty)
    #total_dispatch = "Total Dispatch : " + str(total_dispatch_qty)
    date_range = str(start_date) + ' ~ ' + str(end_date)
    avg_dispatch_week = str("{:.2f}".format(total_dispatch_qty * 7 / diff_days))
    avg_dispatch_month = str("{:.2f}".format(total_dispatch_qty * 30 / diff_days))
    return total_dispatch, date_range, avg_dispatch_week, avg_dispatch_month


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
    temp_df = dff[["usage_month", "sf_code", "qty"]]
    grouped_df = temp_df.groupby(['usage_month', 'sf_code']).agg('sum')
    reindex_df = grouped_df.reset_index()    
    
    colors = []    
    for i in list(reindex_df['usage_month'].unique()):    
        if i.year >= int(year_slider[0]) and i.year <= int(year_slider[1]):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")    

    data = [     
        dict(                           
            type="bar",
            x=reindex_df['usage_month'],
            y=reindex_df["qty"],                        
            name="All Wells",
            marker=dict(color=colors),
        ),
    ]

    layout_count["title"] = "QTY dispatched in total"
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
    temp_df = dff[["customer", "usage_month", "sf_code", "qty"]]    
    grouped_df = temp_df.groupby(['customer', 'usage_month']).agg('sum')    
    reindex_df = grouped_df.reset_index()
    
    data = []
    for customer in df_customer_list:
        customer_df = reindex_df[reindex_df['customer'] == customer]
        customer_df = customer_df.reset_index()    
        data.append(
            dict(
                ype="scatter",
                mode="lines+markers",
                name=customer,
                x=customer_df['usage_month'],
                y=customer_df['qty'],
                line=dict(shape="spline", smoothing=2, width=1, color=customer_color[customer]),
                marker=dict(symbol="diamond-open"),
            )
        )   

    layout_individual["title"] = 'QTY dispatched as per branch'
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
    temp_df = dff[["customer", "usage_month", "sf_code", "qty"]]    
    grouped_df = temp_df.groupby(['customer', 'usage_month']).agg('sum')    
    reindex_df = grouped_df.reset_index()

    fig = px.pie(reindex_df, values='qty', names='customer', title='Dispatch QTY per customer')
        
    figure = fig
    return figure


@app.callback(
    Output("yearly_comparison_graph", "figure"),
    [    
        Input("product_code", "value"),   
        Input("plenus_branch", "value")
    ]
)
def comparison_graph_by_year(product_code, plenus_branch):
    layout_yearly_graph = copy.deepcopy(layout)

    dff = filter_dataframe(df, product_code, [2017, 2020])
    temp_df = dff[["customer", "usage_month", "sf_code", "unit", "qty"]]    
    temp_df['usage_month'] = pd.to_datetime(temp_df['usage_month']) 
    #year_df = temp_df['dispatch_date'].dt.year  # to check if year's data exists
    # error handling when no data in dataframe
    if plenus_branch == 'ALL':  # total                                
        layout_yearly_graph["title"] = 'Yearly Comparison in Total'        
    else: 
        temp_df = temp_df[temp_df['customer'] == plenus_branch]        
        layout_yearly_graph["title"] = 'Yearly Comparison (' + plenus_branch + ')'            

    if len(temp_df) > 0:
        year_df = temp_df['usage_month'].dt.year  # to check if year's data exists
        grouped_df = temp_df.groupby([temp_df.usage_month.dt.month,temp_df.usage_month.dt.year]).agg(sum).unstack()
        #grouped_df = temp_df.groupby(['dispatch_date']).agg('sum')    
        reindex_df = grouped_df.reset_index()          
        col_list = ['usage_month']
        if 2017 in year_df.unique():
            col_list.append('2017')
        if 2018 in year_df.unique():
            col_list.append('2018')
        if 2019 in year_df.unique():
            col_list.append('2019')
        if 2020 in year_df.unique():
            col_list.append('2020')

        #reindex_df.columns = ['dispatch_month', '2017','2018','2019','2020']
        reindex_df.columns = col_list
        if '2017' in reindex_df.columns:
            df_2017 = reindex_df[['usage_month', '2017']]
        else:
            df_2017 = pd.DataFrame(columns=['usage_month', '2017'])
        if '2018' in reindex_df.columns:
            df_2018 = reindex_df[['usage_month', '2018']]
        else:
            df_2018 = pd.DataFrame(columns=['usage_month', '2018'])
        if '2019' in reindex_df.columns:
            df_2019 = reindex_df[['usage_month', '2019']]
        else:
            df_2019 = pd.DataFrame(columns=['usage_month', '2019'])
        if '2020' in reindex_df.columns:
            df_2020 = reindex_df[['usage_month', '2020']]
        else:
            df_2020 = pd.DataFrame(columns=['usage_month', '2020'])
        

        data = [        
            dict(
                type="scatter",
                mode="lines+markers",
                name="2017",
                x=df_2017['usage_month'].apply(lambda x: calendar.month_abbr[x]),        
                y=df_2017['2017'],
                line=dict(shape="spline", smoothing=2, width=1, color="#009688"),
                marker=dict(symbol="diamond-open"),
            ),
            dict(
                type="scatter",
                mode="lines+markers",
                name="2018",
                x=df_2018['usage_month'].apply(lambda x: calendar.month_abbr[x]),            
                y=df_2018['2018'],         
                line=dict(shape="spline", smoothing=2, width=1, color="#9c27b0"),
                marker=dict(symbol="diamond-open"),
            ),
            dict(
                type="scatter",
                mode="lines+markers",
                name="2019",
                x=df_2019['usage_month'].apply(lambda x: calendar.month_abbr[x]),            
                y=df_2019['2019'],                     
                line=dict(shape="spline", smoothing=2, width=1, color="#8bc34a"),
                marker=dict(symbol="diamond-open"),
            ),   
            dict(
                type="scatter",
                mode="lines+markers",
                name="2020",
                x=df_2020['usage_month'].apply(lambda x: calendar.month_abbr[x]),            
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
