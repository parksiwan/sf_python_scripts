
# coding: utf-8
# In[10]:

from openpyxl import load_workbook
import numpy as np
import pandas as pd

code_origin_list = 'CodeOriginList.xlsx'
stock_list = 'StockList.xlsx'

df_code_origin_list = pd.read_excel(code_origin_list)
df_stock_list =pd.read_excel(stock_list)
df_stock_list['origin'] = ''

df_code_origin_list.dropna(subset=['code'], inplace=True)  #Drop the rows where at least one element is missing.
#df_stock_list.dropna(subset=['code'], inplace=True)

found_code = False    
product_origin = ''
for row_stock in df_stock_list.itertuples():   
   
    if pd.isna(row_stock[1]) is False:        
        for row_code_origin in df_code_origin_list.itertuples():
            if row_stock[1] == row_code_origin[1]:
                found_code = True
                product_origin = row_code_origin[2]
            else:
                pass
    else:        
        found_code = True
        product_origin = ''
    
    if found_code is False:
        #print (df_stock_list.at[row_stock.Index, 'origin'])
        df_stock_list.at[row_stock.Index, 'origin'] = 'AUS'
    else:
        df_stock_list.at[row_stock.Index, 'origin'] = product_origin 
        
    found_code = False
    product_origin = ''

df_stock_list.to_excel('StockOriginList.xlsx', sheet_name='sheet1')
