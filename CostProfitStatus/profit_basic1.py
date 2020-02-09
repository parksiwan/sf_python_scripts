import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from pandas.tseries.offsets import MonthEnd

app = dash.Dash()

#customer_list = pd.Series()

#product_list = pd.Series()
df = pd.read_excel('sample_profit.xlsx')
#features = df.columns
customer_list = df['Customer'].unique()
a_customer = pd.Series(['All'])
customer_list = np.concatenate((customer_list, a_customer))

product_list = df['Code'].unique()
a_product = pd.Series(['All'])
product_list = np.concatenate((product_list, a_product))

app.layout = html.Div([html.Div([dcc.Dropdown(id='customer',
                                              options=[{'label':i, 'value':i} for i in customer_list],
                                              #value='All')
                                              value='Mikazuki Parramatta')
                      ], style={'width':'48%', 'display':'inline-block'}),
                      html.Div([dcc.Dropdown(id='product',
                                             options=[{'label':i, 'value':i} for i in product_list],
                                             value='shallot')
                      ], style={'width':'48%', 'display':'inline-block'}),
                      html.Div([dcc.Graph(id='cost-graphic')], style={'width':'48%', 'display':'inline-block'}),
                      html.Div([dcc.Graph(id='qty-graphic')], style={'width':'48%', 'display':'inline-block'}),
                      html.Div([dcc.Graph(id='total-cost-graphic')], style={'width':'48%', 'display':'inline-block'}),
                      html.Div([dcc.Graph(id='total-qty-graphic')], style={'width':'48%', 'display':'inline-block'}),
             ], style={'padding':10})


@app.callback(Output('total-qty-graphic', 'figure'),
              [Input('customer', 'value'),Input('product', 'value')])
def update_qty_graph(customer_name, product_name):
    trace = []
    layout = []
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    df4 = pd.DataFrame()
    print(customer_name)
    print(product_name)
    if customer_name == 'All' and product_name != 'All':
        #print(df['Date'])
        #df['Date'] = pd.to_datetime(df['Date'], format="%Y%m") + MonthEnd(1)
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%m/%Y')
        #print(df['Date'])
        df['CostAmount'] = df['Cost'] * df['QTY']
        df['PriceAmount'] = df['Price'] * df['QTY']
        df['Profit'] = df['PriceAmount'] - df['CostAmount']
        df2 = df[df['Code'] == product_name]
        df3 = df2.groupby(['Customer', 'Date']).agg('sum')
        df3 = df3.reset_index()
        for i in df['Customer'].unique():
            df4 = df3[df3['Customer'] == i]
            df4 = df4.reset_index()
            trace.append(go.Scatter(x=df4['Date'],
                                    y=df4['QTY'].values.tolist(),
                                    text=i,
                                    mode='markers+lines',
                                    marker={'size':7,
                                           'opacity':0.5,
                                           'line':{'width':0.2, 'color':'blue'}}))
        layout = go.Layout(title=product_name,
                           xaxis={'title':'Date', 'tickformat':'%Y-%m-%d'},
                           yaxis={'title':'QTY', 'type': 'category'},
                           hovermode='closest')
    elif customer_name != 'All' and product_name == 'All':
        pass
    elif customer_name == 'All' and product_name == 'All':
        pass
    else:
        pass
    return {'data':trace,
            'layout':layout }


@app.callback(Output('total-cost-graphic', 'figure'),
              [Input('customer', 'value'),Input('product', 'value')])
def update_cost_graph(customer_name, product_name):
    trace = []
    layout = []
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    df4 = pd.DataFrame()
    if customer_name == 'All' and product_name != 'All':
        #df['Date'] = pd.to_datetime(df['Date'], format="%Y%m") + MonthEnd(1)
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%m/%Y')
        df['CostAmount'] = df['Cost'] * df['QTY']
        df['PriceAmount'] = df['Price'] * df['QTY']
        df['Profit'] = df['PriceAmount'] - df['CostAmount']
        df2 = df[df['Code'] == product_name]
        df3 = df2.groupby(['Customer', 'Date']).agg('sum')
        df3 = df3.reset_index()
        #print(df3)
        for i in df['Customer'].unique():
            df4 = df3[df3['Customer'] == i]
            df4 = df4.reset_index()
            trace.append(go.Bar(x=df4['Date'],
                                y=df4['PriceAmount'],
                                name=i, marker={'color': '#FFD700'}))
        layout = go.Layout(title='All Customers',
                           xaxis={'title':'Date', 'tickformat':'%Y-%m'},
                           yaxis={'title':'Profit over Cost'})
    elif customer_name != 'All' and product_name == 'All':
        pass
    elif customer_name == 'All' and product_name == 'All':
        pass
    else:
        pass
    return {'data':trace,
            'layout':layout }

if __name__ == '__main__':
    app.run_server()
