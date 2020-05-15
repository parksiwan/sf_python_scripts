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

# Load data
'''
df = pd.read_csv(DATA_PATH.joinpath("wellspublic.csv"), low_memory=False)
df["Date_Well_Completed"] = pd.to_datetime(df["Date_Well_Completed"])
df = df[df["Date_Well_Completed"] > dt.datetime(1960, 1, 1)]

trim = df[["API_WellNo", "Well_Type", "Well_Name"]]
trim.index = trim["API_WellNo"]
dataset = trim.to_dict(orient="index")

points = pickle.load(open(DATA_PATH.joinpath("points.pkl"), "rb"))
'''

# Load data from DB
db_conn = pg.connect("host='localhost' dbname=sfstock user=siwan password='psw1101714'")
cursor = db_conn.cursor()
select_query = "select * from sushi_train_packinglist"
df = pd.read_sql_query(select_query, con=db_conn)
df_code_list = pd.DataFrame(df['sf_code'].unique())
df_code_list.columns = ['sf_code']
df_code_list['product_name'] = ''
for i in range(len(df_code_list)):
    df_code_list.iat[i, 1] = (df[df['sf_code'] == df_code_list.iat[i, 0]].head(1)).iat[0, 5]

code_product_options = [
    {"label": code_product[2], "value": code_product[1]} for code_product in df_code_list.itertuples()
]


# Create global chart template
#mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
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
                                    "Sushi Train",
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
                                            [html.H6(id="well_text"), html.P(id="total_dispatch")],
                                            id="div1",                                            
                                            #className="mini_container",
                                        ),
                                        html.Div(
                                            [html.H6(id="gasText"), html.P(id="date_range")],
                                            id="div2",
                                            #className="mini_container",
                                        ),
                                        html.Div(
                                            [html.H6(id="oilText"), html.P(id="avg_dispatch_week")],
                                            id="div3",
                                            #className="mini_container",
                                        ),
                                        html.Div(
                                            [html.H6(id="waterText"), html.P(id="avg_dispatch_month")],
                                            id="div4",
                                            #className="mini_container",
                                        ),
                                    ],
                                    className="mini_container",                                    
                                ),                                
                            ]                                                     
                        ),
                        html.P(
                            "Filter by dispatch date (or select range in histogram):",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="year_slider",
                            min=2016,
                            max=2021,
                            step=1,
                            marks={
                                2016: '2016',
                                2021: '2021'
                            },
                            value=[2016, 2021],
                            className="dcc_control",
                        ),
                        html.P("Filter by products:", className="control_label"),                        
                        dcc.Dropdown(
                            id="well_statuses",
                            options=code_product_options,
                            #multi=True,
                            value='KYJ32',
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
                    [dcc.Graph(id="stocking_time_graph")],
                    className="pretty_container five columns",
                ),            
                html.Div(
                    [dcc.Graph(id="dispatch_customer_graph")],
                    className="pretty_container seven columns",
                ),                                  
            ],
            className="row flex-display",
        ),
        
        #html.Div(
        #    [
        #        dcc.RadioItems(
        #           id='xaxis-type',
        #            options=[
        #                        {"label": "Total", "value": "all"},
        #                        {"label": "Branch", "value": "one"},                              
        #                    ],
        #            value='all',
        #            labelStyle={'display': 'inline-block'}
        #        ),    
        #        dcc.Dropdown(
        #            id='yaxis-column',
        #            options=[
        #                        {"label": "STNSW", "value": "stnsw"},
        #                        {"label": "STQLD", "value": "stqld"},                              
        #                        {"label": "STADL", "value": "stadl"},                              
        #                    ],    dcc.RadioItems(                       
        #            value='STNSW'
        #        ),
        #    ],                        
        #),
        
        html.Div(
            [   
                html.Div(
                    [
                        html.P("Graph Mode: ", className="control_label"),  
                        dcc.RadioItems(
                            id='xaxis-type',
                            options=[
                                        {"label": "Total", "value": "all"},
                                        {"label": "Branch", "value": "one"},                              
                                    ],
                            value='all',
                            labelStyle={'display': 'inline-block'}
                        ),  
                        html.P("Select Branch: ", className="control_label"), 
                        dcc.Dropdown(
                            id='yaxis-column',
                            options=[
                                        {"label": "STNSW", "value": "stnsw"},
                                        {"label": "STQLD", "value": "stqld"},                              
                                        {"label": "STADL", "value": "stadl"},                              
                                    ],
                            value='STNSW'
                        ),
                    ],
                    className="two columns",
                ),
                html.Div(
                    [dcc.Graph(id="yearly_comparison_graph")],
                    className="pretty_container ten columns",
                ),                                        
            ],
            className="row flex-display",
        ),  
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Helper functions
def filter_dataframe(df, well_statuses, year_slider):    
    if year_slider[0] == year_slider[1]:
        dff = df[
            (df["sf_code"] == well_statuses)
            & (df["dispatch_date"] >= dt.datetime(year_slider[0], 1, 1).date())
            & (df["dispatch_date"] <= dt.datetime(year_slider[1], 12, 31).date())
        ]
        return dff
    else:
        dff = df[
            (df["sf_code"] == well_statuses)
            & (df["dispatch_date"] > dt.datetime(year_slider[0], 1, 1).date())
            & (df["dispatch_date"] < dt.datetime(year_slider[1], 1, 1).date())
        ]
        return dff


@app.callback(
    [Output('total_dispatch', 'children'), Output('date_range', 'children'), 
     Output('avg_dispatch_week', 'children'), Output('avg_dispatch_month', 'children')],
    [
        Input("well_statuses", "value"),        
        Input("year_slider", "value"),
    ],
)
def generate_summary(well_statuses, year_slider):    

    dff = filter_dataframe(df, well_statuses, [year_slider[0], year_slider[1]])
    temp_df = dff[["dispatch_date", "qty"]]
    total_dispatch_qty = temp_df['qty'].sum()
    start_date = temp_df['dispatch_date'].min()
    end_date = temp_df['dispatch_date'].max()

    delta_dates = end_date - start_date
    
    #diff_days = delta_dates / np.timedelta64(1,'D')
    diff_days = delta_dates.total_seconds() / (3600 * 24) # 2


    #grouped_df = temp_df.groupby(['dispatch_date', 'sf_code']).agg('sum')
    #reindex_df = grouped_df.reset_index()               

    total_dispatch = "Total Dispatch : " + str(total_dispatch_qty)
    date_range = "Date Range : " + str(start_date) + ' ~ ' + str(end_date)
    avg_dispatch_week = "AVG Dispatch per Week : " + str("{:.2f}".format(total_dispatch_qty * 7 / diff_days))
    avg_dispatch_month = "AVG Dispatch per Month : " + str("{:.2f}".format(total_dispatch_qty * 30 / diff_days))
    return total_dispatch, date_range, avg_dispatch_week, avg_dispatch_month


# Selectors -> count graph
@app.callback(
    Output("count_graph", "figure"),
    [
        Input("well_statuses", "value"),        
        Input("year_slider", "value"),
    ],
)
def dispatch_total_qty(well_statuses, year_slider):
    layout_count = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, [2015, 2025])
    temp_df = dff[["dispatch_date", "sf_code", "qty"]]
    grouped_df = temp_df.groupby(['dispatch_date', 'sf_code']).agg('sum')
    reindex_df = grouped_df.reset_index()    
    
    colors = []    
    for i in list(reindex_df['dispatch_date'].unique()):    
        if i.year >= int(year_slider[0]) and i.year < int(year_slider[1]):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")    

    data = [     
        dict(                           
            type="bar",
            x=reindex_df['dispatch_date'],
            y=reindex_df["qty"],
            name="All Wells",
            marker=dict(color=colors),
        ),
    ]

    layout_count["title"] = "Dispatched QTY"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True
    
    figure = dict(data=data, layout=layout_count)
    return figure


@app.callback(
    Output("dispatch_customer_graph", "figure"),
    [
        Input("well_statuses", "value"),        
        Input("year_slider", "value"),    
    ],
)
def dispatch_per_customers(well_statuses, year_slider):
    layout_individual = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, [year_slider[0], year_slider[1]])
    temp_df = dff[["customer", "dispatch_date", "sf_code", "qty"]]    
    grouped_df = temp_df.groupby(['customer', 'dispatch_date']).agg('sum')    
    reindex_df = grouped_df.reset_index()
    
    stadl_df = reindex_df[reindex_df['customer'] == 'STADL']
    stnsw_df = reindex_df[reindex_df['customer'] == 'STNSW']
    stqld_df = reindex_df[reindex_df['customer'] == 'STQLD']
    stadl_df = stadl_df.reset_index()
    stnsw_df = stnsw_df.reset_index()
    stqld_df = stqld_df.reset_index()
    
    data = [        
        dict(
            type="scatter",
            mode="lines+markers",
            name="STNSW",
            x=stnsw_df['dispatch_date'],
            y=stnsw_df['qty'],
            line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
            marker=dict(symbol="diamond-open"),
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="STQLD",
            x=stqld_df['dispatch_date'],
            y=stqld_df['qty'],            
            line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
            marker=dict(symbol="diamond-open"),
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="STADL",
            x=stadl_df['dispatch_date'],
            y=stadl_df['qty'],                        
            line=dict(shape="spline", smoothing=2, width=1, color="#92d8d8"),
            marker=dict(symbol="diamond-open"),
        ),        
    ]
    layout_individual["title"] = 'Dispatched QTY per Customers'

    figure = dict(data=data, layout=layout_individual)
    return figure

@app.callback(
    Output("stocking_time_graph", "figure"),
    [
        Input("well_statuses", "value"),        
        Input("year_slider", "value"),    
    ],
)
def time_between_inward_dispatch(well_statuses, year_slider):
    layout_individual = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, [year_slider[0], year_slider[1]])
    temp_df = dff[["customer", "dispatch_date", "sf_code", "qty", "arrival_date"]]   
    temp_df['queuing_days'] = temp_df['dispatch_date'] - temp_df['arrival_date'] 
    temp_df['queuing_days'] = temp_df['queuing_days'] / np.timedelta64(1,'D')

    grouped_df = temp_df.groupby(['queuing_days']).agg('sum')    
    reindex_df = grouped_df.reset_index()    
    
    data = [     
        dict(                           
            type="bar",
            x=reindex_df['queuing_days'],
            y=reindex_df['qty'],
            name="All Wells",
            marker=dict(color="#59C3C3"),
        ),
    ]

    layout_individual["title"] = 'Queuing Time'
    

    figure = dict(data=data, layout=layout_individual)
    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
