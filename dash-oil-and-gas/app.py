# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
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
        # empty Div to trigger javascript file for graph resizing
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
                                            [html.H6(id="well_text"), html.P("No. of Wells")],
                                            id="wells",
                                            className="mini_container",
                                        ),
                                        html.Div(
                                            [html.H6(id="gasText"), html.P("Gas")],
                                            id="gas",
                                            className="mini_container",
                                        ),
                                    ],
                                    className="row container-display",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [html.H6(id="oilText"), html.P("Oil")],
                                            id="oil",
                                            className="mini_container",
                                        ),
                                        html.Div(
                                            [html.H6(id="waterText"), html.P("Water")],
                                            id="water",
                                            className="mini_container",
                                        ),
                                    ],
                                    className="row container-display",
                                ),
                            ],                            
                        ),
                        html.P(
                            "Filter by dispatch date (or select range in histogram):",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="year_slider",
                            min=2015,
                            max=2025,
                            value=[2016, 2024],
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
                    [dcc.Graph(id="main_graph")],
                    className="pretty_container five columns",
                ),            
                html.Div(
                    [dcc.Graph(id="individual_graph")],
                    className="pretty_container seven columns",
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
    dff = df[
        (df["sf_code"] == well_statuses)
        & (df["dispatch_date"] > dt.datetime(year_slider[0], 1, 1).date())
        & (df["dispatch_date"] < dt.datetime(year_slider[1], 1, 1).date())
    ]
    return dff


# Selectors -> count graph
@app.callback(
    Output("count_graph", "figure"),
    [
        Input("well_statuses", "value"),        
        Input("year_slider", "value"),
    ],
)
def make_count_figure(well_statuses, year_slider):

    layout_count = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, [2015, 2025])
    f = dff[["dispatch_date", "sf_code", "qty"]]
    g = f.groupby(['dispatch_date', 'sf_code']).agg('sum')
    h = g.reset_index()
    #g.index = g["dispatch_date"]    
    #g = g.resample("A").count()
    
    colors = []
    for i in list(h['dispatch_date'].unique()):
    #for i in range(2017, 2040):        
        if i.year >= int(year_slider[0]) and i.year < int(year_slider[1]):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")    
    data = [
        
        #dict(
        #    type="scatter",
        #    mode="markers",
        #    x=g.index,
        #    y=g["API_WellNo"] / 2,
        #    name="All Wells",
        #    opacity=0,
        #    hoverinfo="skip",
        #),
        
        dict(
            type="bar",
            x=h['dispatch_date'],
            y=h["qty"],
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


# Main graph -> individual graph
@app.callback(
    Output("individual_graph", "figure"),
    [
        Input("well_statuses", "value"),        
        Input("year_slider", "value"),
    ],
)
#@app.callback(Output("individual_graph", "figure"), [Input("main_graph", "hoverData")])
def make_individual_figure(well_statuses, year_slider):
#def make_individual_figure(main_graph_hover):

    layout_individual = copy.deepcopy(layout)

    if main_graph_hover is None:
        main_graph_hover = {
            "points": [
                {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
            ]
        }

    chosen = [point["customdata"] for point in main_graph_hover["points"]]
    index, gas, oil, water = produce_individual(chosen[0])

    if index is None:
        annotation = dict(
            text="No data available",
            x=0.5,
            y=0.5,
            align="center",
            showarrow=False,
            xref="paper",
            yref="paper",
        )
        layout_individual["annotations"] = [annotation]
        data = []
    else:
        data = [
            dict(
                type="scatter",
                mode="lines+markers",
                name="STNSW",
                x=index,
                y=gas,
                line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
                marker=dict(symbol="diamond-open"),
            ),
            dict(
                type="scatter",
                mode="lines+markers",
                name="STQLD",
                x=index,
                y=oil,
                line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
                marker=dict(symbol="diamond-open"),
            ),
            dict(
                type="scatter",
                mode="lines+markers",
                name="STADL",
                x=index,
                y=water,
                line=dict(shape="spline", smoothing=2, width=1, color="#92d8d8"),
                marker=dict(symbol="diamond-open"),
            ),
        ]
        layout_individual["title"] = dataset[chosen[0]]["Well_Name"]

    figure = dict(data=data, layout=layout_individual)
    return figure


# Main
if __name__ == "__main__":
    app.run_server(debug=True)
