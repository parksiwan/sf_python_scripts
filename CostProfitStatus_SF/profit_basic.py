import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
from pandas.tseries.offsets import MonthEnd
from datetime import datetime, date, timedelta

app = dash.Dash()

colors = {'Hanamaruya': 'red',
          'Mikazuki Parramatta': 'lightgreen',
          'Good': 'orange',
          'Great': 'darkgreen'}

product_colors = {'shallot': 'red',
                  'KONO06': 'lightgreen',
                  'TF79': 'orange',
                  'TFS01': 'darkgreen',
                  'SDA201': 'blue',
                  'SFA102': 'lightblue',
                  'TF90': 'grey'}


#colors = ['#7FDBFF', '#FFD700', '#281234']
db_conn = pg.connect("host='localhost' dbname=sfstock user=siwan password='psw1101714'")
cursor = db_conn.cursor()
select_query = "select * from sales_sales"
df = pd.read_sql_query(select_query, con=db_conn)


#df = pd.read_excel('sample_profit.xlsx')

customer_list = df['customer'].unique()
a_customer = pd.Series(['All'])
customer_list = np.concatenate((customer_list, a_customer))

product_list = df['product_code'].unique()
a_product = pd.Series(['All'])
product_list = np.concatenate((product_list, a_product))print(year_slider[1])

def read_db_to_dataframe(customer_name, product_code, conn):
    if customer_name == 'All' and product_code != 'All':
        select_sql = ("select * from sales_sales where product_code = '{}' ").format(product_code)
    elif customer_name != 'All' and product_code == 'All':
        select_sql = ("select * from sales_sales where customer = '{}' ").format(customer_name)
    elif customer_name == 'All' and product_code == 'All':
        select_sql = "select * from sales_sales"
    else:
        select_sql = ("select * from sales_sales where customer = '{}' and product_code = '{}' ").format(customer_name, product_code)
    return pd.read_sql_query(select_sql, con=conn)

def generate_table(dataframe):
    cols = dataframe.columns
    dataframe['sales_date'] = pd.to_datetime(dataframe['sales_date']).dt.date
    dataframe = dataframe.round(2)
    dataframe['CostAmount'] = '$' + dataframe['CostAmount'].astype(str)
    dataframe['PriceAmount'] = '$' + dataframe['PriceAmount'].astype(str)
    dataframe['Profit'] = '$' + dataframe['Profit'].astype(str)
    dataframe['ProfitRatio'] = dataframe['ProfitRatio'].astype(str) + "%"
    return html.Table(
        # Header
        [html.Tr([html.Th(col, style={'border':'solid thin', 'fontSize':'4'}) for col in dataframe.columns])] +
        # Body
        [html.Tr([html.Td(dataframe.iloc[i][c], style={'border':'solid thin'}) for c in cols]) for i in range(len(dataframe))]
    )

app.layout = html.Div([html.H1('Sales Dashboard'),
                      html.Div([html.H3('Select Customer:', style={'paddingRight':'30px'}),
                                dcc.Dropdown(id='customer',
                                             options=[{'label':i, 'value':i} for i in customer_list],
                                              #value='All')
                                             value='Mikazuki Parramatta')
                      ], style={'width':'32%', 'display':'inline-block', 'verticalAlign':'top'}),
                      html.Div([html.H3('Select Product:', style={'paddingRight':'30px'}),
                                dcc.Dropdown(id='product',
                                             options=[{'label':i, 'value':i} for i in product_list],
                                             value='shallot')
                      ], style={'width':'32%', 'display':'inline-block', 'verticalAlign':'top'}),
                      html.Div([html.H3('Select Date Range:', style={'paddingRight':'30px'}),
                                dcc.DatePickerRange(id='date-picker-range',
                                                    display_format='DD/MM/YYYY',
                                                    min_date_allowed=datetime(2019,1,1),
                                                    max_date_allowed=datetime.today(),
                                                    start_date = (datetime.today() - timedelta(days=10*365/12)).date(),
                                                    end_date = datetime.today().date(),
                                                    calendar_orientation='horizontal')
                      ], style={'width':'32%', 'display':'inline-block', 'verticalAlign':'top'}),
                      html.Div([html.H2('Sales Status'),
                                html.Div(id='sales-status')
                      ]),
                      html.Div([dcc.Graph(id='cost-graphic')], style={'width':'48%', 'display':'inline-block'}),
                      html.Div([dcc.Graph(id='qty-graphic')], style={'width':'48%', 'display':'inline-block'})
             ], style={'padding':10})


@app.callback([Output('qty-graphic', 'figure'), Output('sales-status', 'children')],
              [Input('customer', 'value'),
               Input('product', 'value'),
               Input('date-picker-range', 'start_date'),
               Input('date-picker-range', 'end_date')])
def update_qty_graph(customer_name, product_code, start_date, end_date):
    trace = []
    layout = []
    if customer_name == 'All' and product_code != 'All':  # For All customers
        #df1 = df.copy(deep=True)
        df1 = read_db_to_dataframe(customer_name, product_code, db_conn)
        df5 = pd.DataFrame()
        df1['sales_date'] = pd.to_datetime(df1['sales_date'], format="%Y-%m") + MonthEnd(1)
        df1['CostAmount'] = df1['product_cost'] * df1['sales_qty']
        df1['PriceAmount'] = df1['product_price'] * df1['sales_qty']
        df1['Profit'] = df1['PriceAmount'] - df1['CostAmount']
        #df1['ProfitRatio'] = df1['Profit'] / df1['PriceAmount'] * 100
        df2 = df1[(df1['product_code'] == product_code) & (df1['sales_date'] >= datetime.strptime(start_date, "%Y-%m-%d")) & (df1['sales_date'] <= datetime.strptime(end_date, "%Y-%m-%d"))]
        df3 = df2.groupby(['customer', 'sales_date']).agg('sum')
        df3 = df3.reset_index()

        temp_ratio = df3.Profit / df3.PriceAmount * 100
        df3['ProfitRatio'] = temp_ratio.where(df3.PriceAmount > 0, 0)

        for i in df3['customer'].unique():
            df4 = df3[df3['customer'] == i]
            df4 = df4.reset_index()

            trace.append(go.Scatter(x=df4['sales_date'],
                                    y=df4['sales_qty'],
                                    text=i,
                                    name=i,
                                    mode='markers+lines',
                                    marker={'size':7,
                                           'opacity':0.5,
                                           'line':{'width':0.2, 'color':'blue'}}))
            df4.loc['Total', 'sales_qty'] = 'SUB TOTAL'
            df4.loc['Total', 'CostAmount'] = df4['CostAmount'].sum()
            df4.loc['Total', 'PriceAmount'] = df4['PriceAmount'].sum()
            df4.loc['Total', 'Profit'] = df4['Profit'].sum()
            df4.loc['Total', 'ProfitRatio'] = df4.loc['Total', 'Profit'] / df4.loc['Total', 'PriceAmount'] * 100
            df5 = pd.concat([df5, df4], ignore_index=True)

        layout = go.Layout(title=product_code,
                           xaxis={'title':'Sales Date', 'tickformat':'%Y-%m-%d'},
                           yaxis={'title':'Sales QTY'},
                           hovermode='closest')

        df5.loc['Total', 'sales_qty'] = 'TOTAL'
        df5.loc['Total', 'CostAmount'] = df5.loc[df5['sales_qty'] == 'SUB TOTAL', 'CostAmount'].sum()
        df5.loc['Total', 'PriceAmount'] = df5.loc[df5['sales_qty'] == 'SUB TOTAL', 'PriceAmount'].sum()
        df5.loc['Total', 'Profit'] = df5.loc[df5['sales_qty'] == 'SUB TOTAL', 'Profit'].sum()
        df5.loc['Total', 'ProfitRatio'] = df5.loc['Total', 'Profit'] / df5.loc['Total', 'PriceAmount'] * 100
        df_result = df5[['customer', 'sales_date', 'sales_qty', 'CostAmount', 'PriceAmount', 'Profit', 'ProfitRatio']]
    elif customer_name != 'All' and product_code == 'All':  # For All products
        df1 = read_db_to_dataframe(customer_name, product_code, db_conn)
        #df1 = df.copy(deep=True)
        df5 = pd.DataFrame()
        df1['sales_date'] = pd.to_datetime(df1['sales_date'], format="%Y-%m") + MonthEnd(1)
        df1['CostAmount'] = df1['product_cost'] * df1['sales_qty']
        df1['PriceAmount'] = df1['product_price'] * df1['sales_qty']
        df1['Profit'] = df1['PriceAmount'] - df1['CostAmount']

        df2 = df1[(df1['customer'] == customer_name) & (df1['sales_date'] >= datetime.strptime(start_date, "%Y-%m-%d")) & (df1['sales_date'] <= datetime.strptime(end_date, "%Y-%m-%d"))]
        df3 = df2.groupby(['product_code', 'sales_date']).agg('sum')
        df3['ProfitRatio'] = df3['Profit'] / df3['PriceAmount'] * 100
        df3 = df3.reset_index()
        for i in df3['product_code'].unique():
            df4 = df3[df3['product_code'] == i]
            df4 = df4.reset_index()
            trace.append(go.Scatter(x=df4['sales_date'],
                                    y=df4['sales_qty'],
                                    text=i,
                                    name=i,
                                    mode='markers+lines',
                                    marker={'size':7,
                                           'opacity':0.5,
                                           'line':{'width':0.2, 'color':'blue'}}))
            df4.loc['Total', 'sales_qty'] = 'SUB TOTAL'
            df4.loc['Total', 'CostAmount'] = df4['CostAmount'].sum()
            df4.loc['Total', 'PriceAmount'] = df4['PriceAmount'].sum()
            df4.loc['Total', 'Profit'] = df4['Profit'].sum()
            df4.loc['Total', 'ProfitRatio'] = df4.loc['Total', 'Profit'] / df4.loc['Total', 'PriceAmount'] * 100
            df5 = pd.concat([df5, df4], ignore_index=True)

        layout = go.Layout(title='All products',
                           xaxis={'title':'Sales Date', 'tickformat':'%Y-%m-%d'},
                           yaxis={'title':'Sales QTY'},
                           hovermode='closest')

        df5.loc['Total', 'sales_qty'] = 'TOTAL'
        df5.loc['Total', 'CostAmount'] = df5.loc[df5['sales_qty'] == 'SUB TOTAL', 'CostAmount'].sum()
        df5.loc['Total', 'PriceAmount'] = df5.loc[df5['sales_qty'] == 'SUB TOTAL', 'PriceAmount'].sum()
        df5.loc['Total', 'Profit'] = df5.loc[df5['sales_qty'] == 'SUB TOTAL', 'Profit'].sum()
        df5.loc['Total', 'ProfitRatio'] = df5.loc['Total', 'Profit'] / df5.loc['Total', 'PriceAmount'] * 100
        df_result = df5[['product_code', 'sales_date', 'sales_qty', 'CostAmount', 'PriceAmount', 'Profit', 'ProfitRatio']]
    elif customer_name == 'All' and product_code == 'All':
        df1 = read_db_to_dataframe(customer_name, product_code, db_conn)
        #df1 = df.copy(deep=True)
        df5 = pd.DataFrame()
        df1['sales_date'] = pd.to_datetime(df1['sales_date'], format="%Y-%m") + MonthEnd(1)
        df1['CostAmount'] = df1['product_cost'] * df1['sales_qty']
        df1['PriceAmount'] = df1['product_price'] * df1['sales_qty']
        df1['Profit'] = df1['PriceAmount'] - df1['CostAmount']

        df2 = df1[(df1['sales_date'] >= datetime.strptime(start_date, "%Y-%m-%d")) & (df1['sales_date'] <= datetime.strptime(end_date, "%Y-%m-%d"))]
        df3 = df2.groupby(['product_code', 'sales_date']).agg('sum')
        df3['ProfitRatio'] = df3['Profit'] / df3['PriceAmount'] * 100
        df3 = df3.reset_index()
        for i in df3['product_code'].unique():
            df4 = df3[df3['product_code'] == i]
            df4 = df4.reset_index()
            trace.append(go.Scatter(x=df4['sales_date'],
                                    y=df4['sales_qty'],
                                    text=i,
                                    name=i,
                                    mode='markers+lines',
                                    marker={'size':7,
                                           'opacity':0.5,
                                           'line':{'width':0.2, 'color':'blue'}}))
            df4.loc['Total', 'sales_qty'] = 'SUB TOTAL'
            df4.loc['Total', 'CostAmount'] = df4['CostAmount'].sum()
            df4.loc['Total', 'PriceAmount'] = df4['PriceAmount'].sum()
            df4.loc['Total', 'Profit'] = df4['Profit'].sum()
            df4.loc['Total', 'ProfitRatio'] = df4.loc['Total', 'Profit'] / df4.loc['Total', 'PriceAmount'] * 100
            df5 = pd.concat([df5, df4], ignore_index=True)

        layout = go.Layout(title='All products',
                           xaxis={'title':'Sales Date', 'tickformat':'%Y-%m-%d'},
                           yaxis={'title':'Sales QTY'},
                           hovermode='closest')

        df5.loc['Total', 'sales_qty'] = 'TOTAL'
        df5.loc['Total', 'CostAmount'] = df5.loc[df5['sales_qty'] == 'SUB TOTAL', 'CostAmount'].sum()
        df5.loc['Total', 'PriceAmount'] = df5.loc[df5['sales_qty'] == 'SUB TOTAL', 'PriceAmount'].sum()
        df5.loc['Total', 'Profit'] = df5.loc[df5['sales_qty'] == 'SUB TOTAL', 'Profit'].sum()
        df5.loc['Total', 'ProfitRatio'] = df5.loc['Total', 'Profit'] / df5.loc['Total', 'PriceAmount'] * 100
        df_result = df5[['product_code', 'sales_date', 'sales_qty', 'CostAmount', 'PriceAmount', 'Profit', 'ProfitRatio']]
    else:
        df1 = read_db_to_dataframe(customer_name, product_code, db_conn)
        df5 = df1[(df1['customer'] == customer_name) & (df1['product_code'] == product_code) & (df1['sales_date'] >= datetime.strptime(start_date, "%Y-%m-%d").date()) & (df1['sales_date'] <= datetime.strptime(end_date, "%Y-%m-%d").date())]
        df5['CostAmount'] = df5['product_cost'] * df5['sales_qty']
        df5['PriceAmount'] = df5['product_price'] * df5['sales_qty']
        df5['Profit'] = df5['PriceAmount'] - df5['CostAmount']

        temp_ratio = df5.Profit / df5.PriceAmount * 100
        df5['ProfitRatio'] = temp_ratio.where(df5.PriceAmount > 0, 0)

        df5.loc['Total', 'product_name'] = 'TOTAL'
        df5.loc['Total', 'CostAmount'] = df5['CostAmount'].sum()
        df5.loc['Total', 'PriceAmount'] = df5['PriceAmount'].sum()
        df5.loc['Total', 'Profit'] = df5['Profit'].sum()
        df5.loc['Total', 'ProfitRatio'] = 0 if df5.loc['Total', 'Profit'] == 0 else df5.loc['Total', 'Profit'] / df5.loc['Total', 'PriceAmount'] * 100

        trace.append(go.Scatter(x=df5['sales_date'],
                                y=df5['sales_qty'],
                                text=df5['customer'],
                                mode='markers+lines',
                                marker={'size':7,
                                       'opacity':0.5,
                                       'line':{'width':0.2, 'color':'white'}}))
        layout = go.Layout(title=product_code,
                           xaxis={'title':'Sales Date'},
                           yaxis={'title':'Sales QTY'},
                           hovermode='closest')
        df_result = df5[['customer', 'sales_date', 'product_code', 'product_name', 'product_unit', 'sales_qty', 'product_cost', 'product_price', 'CostAmount', 'PriceAmount', 'Profit', 'ProfitRatio']]
    return {'data':trace, 'layout':layout }, generate_table(df_result)


@app.callback(Output('cost-graphic', 'figure'),
              [Input('customer', 'value'),
               Input('product', 'value'),
               Input('date-picker-range', 'start_date'),
               Input('date-picker-range', 'end_date')])
def update_cost_graph(customer_name, product_code, start_date, end_date):
    trace = []
    layout = []
    selected = ''
    if customer_name == 'All' and product_code != 'All':  # For All customers
        df1 = read_db_to_dataframe(customer_name, product_code, db_conn)
        #df1 = df.copy(deep=True)
        df1['sales_date'] = pd.to_datetime(df1['sales_date'], format="%Y-%m") + MonthEnd(1)
        df1['CostAmount'] = df1['product_cost'] * df1['sales_qty']
        df1['PriceAmount'] = df1['product_price'] * df1['sales_qty']
        df1['Profit'] = df1['PriceAmount'] - df1['CostAmount']
        df2 = df1[(df1['product_code'] == product_code) & (df1['sales_date'] >= datetime.strptime(start_date, "%Y-%m-%d")) & (df1['sales_date'] <= datetime.strptime(end_date, "%Y-%m-%d"))]
        print(df2['customer'])
        df3 = df2.groupby(['product_code','customer', 'sales_date']).agg('sum')
        df3 = df3.reset_index()
        print('===')
        print(df3)
        print(df3['customer'])
        for i in df3['customer'].unique():
            df4 = df3[df3['customer'] == i]
            df4 = df4.reset_index()
            trace.append(go.Bar(x=df4['sales_date'], y=df4['PriceAmount'],
                                name=i, marker={'color': colors[i]}))
        layout = go.Layout(title='All Customers',
                           xaxis={'title':'Sales Date', 'tickformat':'%Y-%m'},
                           yaxis={'title':'Sales'})
    elif customer_name != 'All' and product_code == 'All':  # For All products
        df1 = read_db_to_dataframe(customer_name, product_code, db_conn)
        #df1 = df.copy(deep=True)
        df1['sales_date'] = pd.to_datetime(df1['sales_date'], format="%Y-%m") + MonthEnd(1)
        df1['CostAmount'] = df1['product_cost'] * df1['sales_qty']
        df1['PriceAmount'] = df1['product_price'] * df1['sales_qty']
        df1['Profit'] = df1['PriceAmount'] - df1['CostAmount']
        df2 = df1[(df1['customer'] == customer_name) & (df1['sales_date'] >= datetime.strptime(start_date, "%Y-%m-%d")) & (df1['sales_date'] <= datetime.strptime(end_date, "%Y-%m-%d"))]
        df3 = df2.groupby(['customer', 'product_code', 'sales_date']).agg('sum')
        df3 = df3.reset_index()
        for i in df3['product_code'].unique():
            df4 = df3[df3['product_code'] == i]
            df4 = df4.reset_index()
            trace.append(go.Bar(x=df4['sales_date'], y=df4['PriceAmount'],
                                name=i, marker={'color': product_colors[i]}))
        layout = go.Layout(title=customer_name,
                           xaxis={'title':'Sales Date', 'tickformat':'%Y-%m'},
                           yaxis={'title':'Sales'})
    elif customer_name == 'All' and product_code == 'All':
        df1 = read_db_to_dataframe(customer_name, product_code, db_conn)
        #df1 = df.copy(deep=True)
        df1['sales_date'] = pd.to_datetime(df1['sales_date'], format="%Y-%m") + MonthEnd(1)
        df1['CostAmount'] = df1['product_cost'] * df1['sales_qty']
        df1['PriceAmount'] = df1['product_price'] * df1['sales_qty']
        df1['Profit'] = df1['PriceAmount'] - df1['CostAmount']
        df2 = df1[(df1['sales_date'] >= datetime.strptime(start_date, "%Y-%m-%d")) & (df1['sales_date'] <= datetime.strptime(end_date, "%Y-%m-%d"))]
        df3 = df2.groupby(['product_code', 'sales_date']).agg('sum')
        df3 = df3.reset_index()
        for i in df3['product_code'].unique():
            df4 = df3[df3['product_code'] == i]
            df4 = df4.reset_index()
            trace.append(go.Bar(x=df4['sales_date'], y=df4['PriceAmount'],
                                name=i, marker={'color': product_colors[i]}))
        layout = go.Layout(title='All Customers',
                           xaxis={'title':'Sales Date', 'tickformat':'%Y-%m'},
                           yaxis={'title':'Sales'})
    else:
        df1 = read_db_to_dataframe(customer_name, product_code, db_conn)
        df5 = df1[(df1['customer'] == customer_name) & (df1['product_code'] == product_code) & (df1['sales_date'] >= datetime.strptime(start_date, "%Y-%m-%d").date()) & (df['sales_date'] <= datetime.strptime(end_date, "%Y-%m-%d").date())]
        df5['CostAmount'] = df5['product_cost'] * df5['sales_qty']
        df5['PriceAmount'] = df5['product_price'] * df5['sales_qty']
        df5['Profit'] = df5['PriceAmount'] - df5['CostAmount']
        trace1 = go.Bar(x=df5['sales_date'], y=df5['PriceAmount'],
                        name='Price', marker={'color': '#FFD700'})
        trace2 = go.Bar(x=df5['sales_date'], y=df5['CostAmount'],
                        name='Cost', marker={'color': '#9EA0A1'})
        trace3 = go.Bar(x=df5['sales_date'], y=df5['Profit'],
                        name='Profit', marker={'color': '#CD7F32'})
        trace = [trace1, trace2, trace3]
        layout = go.Layout(title=customer_name,
                           xaxis={'title':'Sales Date'},
                           yaxis={'title':'Profit over Cost'},
                           barmode='stack')
    return {'data':trace, 'layout':layout }

if __name__ == '__main__':
    app.run_server()
