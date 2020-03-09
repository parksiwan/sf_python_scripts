from openpyxl import load_workbook
import numpy as np
import pandas as pd


df_orderform = pd.read_excel('orderform.xlsx')
df_sf = pd.read_excel('SF.xlsx')
df_sf_local = pd.read_excel('SF_local.xlsx')

found_code = False    
df_result_sf = pd.DataFrame()
df_result_sf_local = pd.DataFrame()

for row_orderform in df_orderform.itertuples():   
    #print(row_orderform[2])
    temp_sf = df_sf[df_sf['code'].str.upper() == row_orderform[2]]
    if len(temp_sf) > 0:
        #temp_code['orderform_price'] = sheet_orderform.cell(row_orderform, 4).value
        df_result_sf = pd.concat([df_result_sf, temp_sf], ignore_index=True)
    else:
        temp_sf_local = df_sf_local[df_sf_local['code'].str.upper() == row_orderform[2]]
        if len(temp_sf_local) > 0:
            df_result_sf_local = pd.concat([df_result_sf_local, temp_sf_local], ignore_index=True)    
        
print(df_result_sf)
df_result_sf.to_excel('sf_code_price.xlsx', sheet_name='sheet1')
df_result_sf_local.to_excel('sf_code_local_price.xlsx', sheet_name='sheet1')
