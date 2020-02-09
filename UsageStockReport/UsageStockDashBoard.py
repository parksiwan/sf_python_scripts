# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 19:11:33 2019

@author: siwan
"""
# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt  #import dash_table_experiments as dt
import pandas as pd
from plotly.subplots import make_subplots  #import plotly
import psycopg2 as pg
#import base64

stock_status_file = r'C:\Users\siwan\DataScience\DeadStock_R1\StockStatusReport.xlsx'

conn = pg.connect("host='localhost' dbname=sfstock user=siwan password='psw1101714'")
cursor = conn.cursor()

select_code_list_query = "(select distinct(sf_code), product_name from inventory_currentstock where end_stock_day = '2019-09-30') union (select distinct(sf_code), product_name from inventory_monthlyusage) order by sf_code"
df_code_list = pd.read_sql_query(select_code_list_query, con=conn)
#df_sf_usage = pd.read_excel(sf_usage)
df_stock_status = pd.read_excel(stock_status_file)
df_stock_code = df_code_list[['sf_code', 'product_name']]

#print(df_stock_status)

# Create our app layout
app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([
    html.Div([
        html.Div([ 
            html.H2('Stock Status'),
            dcc.Dropdown(
                id = 'xaxis-column',
                options = [{'label': i, 'value': i} for i in df_stock_code],
                value='AS01'
                    ),
           
        ]),
        html.Div([
            html.H2('WOW')    
        ]),                
    ], style={'columnCount': 2}),
    #html.Div(id='selected-indexes'),
    html.Div([
        #html.H2('Stock Status'),
        dcc.Graph(
            id='datatable-subplots'
        )
    ])
], style={'columnCount': 1, 'width': '100%'})
 
@app.callback(Output('datatable-subplots', 'figure'),
              [Input('my-datatable', 'data'),
               Input('my-datatable', 'selected_rows'),
              ])
def update_figure(rows, selected_rows):            
    selected_df = pd.DataFrame(rows).iloc[selected_rows[0]] 
            
    dff = df_stock_status[df_stock_status['Code'] == selected_df['sf_code']]
    
    #fig = make_subplots(rows=1, cols=1)
    #stock = [' ' for i in range(0, 12)]
    #stock[11] = dff.iloc[0][3]
    
    fig = {
        #'data': data,
        'data': [
                    {
                        'x': dff.columns[4:16],
                        'y': dff.iloc[0][4:16],
                        'type': 'line',
                        'name': 'monthly usage',                        
                    },
                    {
                        'x': dff.columns[4:16],
                        'y': [dff.iloc[0][17] for i in range(4, 16)],
                        'type': 'line',
                        'name': 'avg. usage',       
                        'line': {'width': 0.1, 'dash': 'dot'},
                    },    
                    {
                        'x': dff.columns[4:16],
                        'y': [dff.iloc[0][3] for i in range(4, 16)],
                        #'y': stock[0:12],
                        'type': 'line',
                        'name': 'finish stock',               
                        'line': {'width': 0.5, 'dash': 'dot'},
                    }
                ],                
        'layout': {
            'title': 'Usage over Stock -- ' + dff.iloc[0][2] + "(" + dff.iloc[0][1] + ")",
            'xaxis' : dict(
                title='Month',
                titlefont=dict(
                family='Courier New, monospace',
                size=20,
                color='#7f7f7f'
            )),
            'yaxis' : dict(
                title='QTY (ctn)',
                titlefont=dict(
                family='Helvetica, monospace',
                size=20,
                color='#7f7f7f'
            ))
        }
    }            
    return fig
    
  
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port='80', debug=True)
