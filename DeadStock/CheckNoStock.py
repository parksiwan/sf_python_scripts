
# coding: utf-8
# In[10]:

from openpyxl import load_workbook
import numpy as np
import pandas as pd

alex_frozen_list = 'Alex_Freezer.xlsx'
alex_dry_list = 'Alex_Dry.xlsx'
daily_frozen_list = 'Daily.xlsx' 
input_order_form = 'LM_order_sheet.xlsx'

df_alex_frozen = pd.read_excel(alex_frozen_list)
df_alex_dry = pd.read_excel(alex_dry_list)
df_daily = pd.read_excel(daily_frozen_list)
df_LM_order_form =pd.read_excel(input_order_form)

df_alex_frozen.dropna(subset=['Code'], inplace=True)  #Drop the rows where at least one element is missing.
df_alex_dry.dropna(subset=['Code'], inplace=True)  #Drop the rows where at least one element is missing.
df_daily.dropna(subset=['Code'], inplace=True)
df_LM_order_form.dropna(subset=['SF Code'], inplace=True)

df_simplified_alex_frozen = df_alex_frozen[['Code', 'New Balance']]
df_simplified_alex_dry = df_alex_dry[['Code', 'New Balance']]
df_simplified_daily = df_daily[['Code', 'New Balance']]
df_simplified_LM_order_form = df_LM_order_form[['SF Code', 'Order QTY']]

#grouped_stock = pd.concat([df_simplified_alex_frozen, df_simplified_daily]) 
grouped_stock = pd.concat([df_simplified_alex_frozen,df_simplified_alex_dry, df_simplified_daily]) 
#grouped_stock = df_simplified_alex_dry
grouped_stock = (grouped_stock.groupby('Code')).agg(['sum']).reset_index()              

"""
for row_order_form in df_simplified_LM_order_form.itertuples():    
    print (row_order_form[1])
    idx = grouped_stock.index[grouped_stock['Code'] == row_order_form[1]]    
    #print (idx)
    if idx is not None:        
        #print(grouped_stock.iloc[idx]['New Balance'])
        if grouped_stock.iloc[idx]['New Balance'] is not None:            
            print(grouped_stock.iloc[idx]['New Balance'])
        pass
        #print (idx)
        #if grouped_stock.loc[grouped_stock['Code'] == row_order_form[1]] is not None:     
        #print (grouped_stock.iloc[idx, 0],'---', grouped_stock.iloc[idx, 1])
    else:
        df_simplified_LM_order_form.at[row_order_form.Index, 'Order QTY'] = -1
        print ('&&')
"""        
    
found_code = False    
for row_order_form in df_simplified_LM_order_form.itertuples():    
    for row_stock in grouped_stock.itertuples():
        if row_order_form[1] == row_stock[1]:
            found_code = True
            if row_stock[2] <= 0:
                df_simplified_LM_order_form.at[row_order_form.Index, 'Order QTY'] = -1                                
        else:
            pass
    
    if found_code is False:
        df_simplified_LM_order_form.at[row_order_form.Index, 'Order QTY'] = -1
        
    found_code = False

df_simplified_LM_order_form.to_excel('Stock_info.xlsx', sheet_name='sheet1')

#grouped_stock.to_csv(r'C:\Users\siwan\DataScience\STOCK_result.csv')

#b = d_to.sum()
#b['date'] = '31/3/2019'
#b.to_csv('Alex_to_result.csv')






