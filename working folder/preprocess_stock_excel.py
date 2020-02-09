# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 15:24:20 2019

@author: siwan
"""
from dateutil.parser import parse
from openpyxl import load_workbook
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
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
    
def convert_string_to_date(date_string):
    for date_format in ('%Y-%m-%d %H:%M:%S', '%d-%m-%Y', '%d.%m.%Y', '%Y.%m.%d', '%d.%m.%y', '%d/%m/%Y', '%d/%m/%Y %H:%M:%S'):
        try:
            return datetime.datetime.strptime(date_string, date_format)
        except ValueError:   
            print(date_string)
            pass
    raise ValueError('no valid date format found')
    
def main():
    excel_files = glob.glob('*.xlsx')    
    
    for excel_file in excel_files:
        df = pd.read_excel(excel_file)
        df.dropna(subset=['code', 'PreviousBalance', 'NewBalance'], how='any', inplace=True)                                     
        
        df_preprocessed = df[['code', 'Inward', 'ITEM1', 'unit', 'NewBalance', 'bbd']]
        df_preprocessed['NewBalance'] = df_preprocessed['NewBalance'].astype(float)
        df_preprocessed = df_preprocessed[df_preprocessed['NewBalance'] > 0.001]                
        
        update_date = (excel_file.split('.')[0]).split('_')[1]
        df_preprocessed['update_date'] = pd.to_datetime(update_date, format='%Y-%m-%d')
        
        if ((excel_file.split('.')[0]).split('_')[0] == 'AlexFreezer') or \
           ((excel_file.split('.')[0]).split('_')[0] == 'Botany') or \
           ((excel_file.split('.')[0]).split('_')[0] == 'KKS'):
            df_preprocessed['product_type'] = 'FRZ'
        else:
            df_preprocessed['product_type'] = 'DRY'            

    	# Assign location of storage
        if ((excel_file.split('.')[0]).split('_')[0])[:4] == 'Alex':
            df_preprocessed['location'] = 'Alex'
        elif ((excel_file.split('.')[0]).split('_')[0])[:5] == 'Lucky':     
            df_preprocessed['location'] = 'LW'
        elif ((excel_file.split('.')[0]).split('_')[0])[:3] == 'OSP':
            df_preprocessed['location'] = 'OSP'  		    
        elif ((excel_file.split('.')[0]).split('_')[0])[:2] == 'SR':
            df_preprocessed['location'] = 'SR'  		    
        elif ((excel_file.split('.')[0]).split('_')[0])[:3] == 'HAI':
            df_preprocessed['location'] = 'HS'  	        
        elif ((excel_file.split('.')[0]).split('_')[0])[:3] == 'HEL':
            df_preprocessed['location'] = 'HE'  		    
        elif ((excel_file.split('.')[0]).split('_')[0])[:3] == 'KKS':
            df_preprocessed['location'] = 'KKS'  		    
        
        df_preprocessed['id'] = ''
        df_preprocessed['unit'] = df_preprocessed['unit'].str.lower()
        df_preprocessed = df_preprocessed.reset_index()    
        
        for i in range(0, len(df_preprocessed)):
            #print(df_preprocessed.at[i, 'Code'])
            #print(is_date(str(df_preprocessed.at[i, 'Code']), True))
            if is_date(str(df_preprocessed.at[i, 'Inward'])) == False:
                df_preprocessed.at[i, 'Inward'] = pd.to_datetime('1999-01-01', format='%Y-%m-%d')
            else:
                df_preprocessed.at[i, 'Inward'] = convert_string_to_date(str(df_preprocessed.at[i, 'Inward']))
                
            if is_date(str(df_preprocessed.at[i, 'bbd'])) == True:
                df_preprocessed.at[i, 'bbd'] = convert_string_to_date(str(df_preprocessed.at[i, 'bbd']))
                            
                
            if is_date(str(df_preprocessed.at[i, 'bbd'])) == False:
                if str(df_preprocessed.at[i, 'bbd']) == '-':
                    df_preprocessed.at[i, 'bbd'] = '2099-12-31'
                    #pass
                elif str(df_preprocessed.at[i, 'bbd']) == 'Check BBD':
                    dt = datetime.datetime.strptime(str(df_preprocessed.at[i, 'Inward']), "%Y-%m-%d %H:%M:%S").date()
                    one_year = datetime.timedelta(weeks=52)                    
                    df_preprocessed.at[i, 'bbd'] = dt + one_year
                    #pass
                else:
                    dt = datetime.datetime.strptime(str(df_preprocessed.at[i, 'Inward']), "%Y-%m-%d %H:%M:%S").date()
                    one_year = datetime.timedelta(weeks=52)                    
                    df_preprocessed.at[i, 'bbd'] = dt + one_year
                              
        data = { 'id' : df_preprocessed['id'], 'update_date' : df_preprocessed['update_date'], 'product_type' : df_preprocessed['product_type'],
                 'sf_code' : df_preprocessed['code'], 'inward' : df_preprocessed['Inward'],
                 'product_name' : df_preprocessed['ITEM1'], 'new_balance' : df_preprocessed['NewBalance'], 'unit' : df_preprocessed['unit'], 
                 'bbd' : df_preprocessed['bbd'], 'location' : df_preprocessed['location']}
        
        df_processed = pd.DataFrame(data)    
        excel_file_processed = (excel_file.split('.')[0]) + '_processed_stock.xlsx'
        excel_writer = pd.ExcelWriter(excel_file_processed, engine='openpyxl')
        wb = excel_writer.book
        df_processed.to_excel(excel_writer, index=False)
        wb.save(excel_file_processed)
    
if __name__ == "__main__":
    main()
    


    
