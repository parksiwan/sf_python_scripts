# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 15:24:20 2019

@author: siwan
"""
from dateutil.parser import parse
from openpyxl import load_workbook
import pandas as pd
import numpy as np
import glob


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
    
def main():
    excel_files = glob.glob('*.xlsx')
    #excel_files = glob.glob('*.xls')
    for excel_file in excel_files:
        df = pd.read_excel(excel_file)
        df.dropna(subset=['code', 'pickup', 'pmemo'], inplace=True)  
        #df.dropna(subset=['sf_code'], inplace=True)  
        df_preprocessed = df[['code', 'Movement', 'ITEM1', 'unit', 'pickup', 'pmemo']]
       
        update_date = (excel_file.split('.')[0]).split('_')[1]
        df_preprocessed['update_date'] = pd.to_datetime(update_date, format='%Y-%m-%d')
        
        if ((excel_file.split('.')[0]).split('_')[0] == 'AlexFreezer') or \
           ((excel_file.split('.')[0]).split('_')[0] == 'Botany') or \
           ((excel_file.split('.')[0]).split('_')[0] == 'KKS'):
            df_preprocessed['product_type'] = 'FRZ'
        else:
            df_preprocessed['product_type'] = 'DRY'                                   
        
        df_preprocessed['id'] = ''
        df_preprocessed['unit'] = df_preprocessed['unit'].str.lower()
        df_preprocessed = df_preprocessed.reset_index()
             
        df_preprocessed_usage = df_preprocessed        
        
        data = { 'id' : df_preprocessed_usage['id'], 'update_date' : df_preprocessed_usage['update_date'], 
                 'product_type' : df_preprocessed_usage['product_type'], 'sf_code' : df_preprocessed_usage['code'], 
                 'product_name' : df_preprocessed_usage['ITEM1'], 
                  'move' : df_preprocessed_usage['Movement'], 'unit' : df_preprocessed_usage['unit'], 
                 'pickup_qty' : df_preprocessed_usage['pickup'], 'memo' : df_preprocessed_usage['pmemo']}
        
        df_processed = pd.DataFrame(data)    
        excel_file_processed = (excel_file.split('.')[0]) + '_processed_usage.xlsx'
        excel_writer = pd.ExcelWriter(excel_file_processed, engine='openpyxl')
        wb = excel_writer.book
        df_processed.to_excel(excel_writer, index=False)
        wb.save(excel_file_processed)
    
if __name__ == "__main__":
    main()
    


    
