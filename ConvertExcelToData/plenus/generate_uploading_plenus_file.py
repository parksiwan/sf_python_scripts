from dateutil.parser import parse
import xlrd 
import os
import datetime
import glob
import pandas as pd
import numpy as np


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
            #print(date_string)
            pass
    raise ValueError('no valid date format found')


def convert_excel_date(excel_book, excel_date):
    ms_bbd_date_number = excel_date
    year, month, day, hour, minute, second = xlrd.xldate_as_tuple(ms_bbd_date_number, excel_book.datemode)
    py_date = datetime.datetime(year, month, day, hour, minute, second)
    return py_date


def main():
    # Change directory
    #(filename=r"\\192.168.20.50\AlexServer\輸入共有\輸入共有フォルダー\SF Product Name & Code List(商品名確認票）\SF Product Name & Code List (商品名確認表)_for_test.xlsx", data_only=True)
    #os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Alex\Alex 2020\siwan")
    os.chdir('/home/siwanpark/ExcelData/Alex/')
    excel_files = glob.glob('*.xls*')
    print(excel_files)
    for excel_file in excel_files:
        # Give the location of the file 
        #file_path = "Alex 2019 09 AUG D12-14.xlsm"
        #print(excel_file)
        file_name = excel_file.split('.')[0]
        df, update_date = generate_data_frame(excel_file)  #generate data frame
        df1 = df.copy(deep=True)   
        generate_usage_file_to_upload(df, file_name, update_date)        
        generate_stock_file_to_upload(df1, file_name, update_date)
        #os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Alex\Alex 2020\siwan")
        os.chdir('/home/siwanpark/ExcelData/Alex/')

def generate_data_frame(file_path):    
    loc = (file_path)     
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0)     
    update_date = sheet.cell_value(1, 9).split(':')[1]
    
    update_date = update_date.strip()

    #for i in range(3, sheet.nrows):  
    stock_list = []
    i = 4
    while sheet.cell(i, 1).value != 'end':    
        # Convert excel date to python date       
        if sheet.cell(i, 5).ctype == 3:
            inward_date = convert_excel_date(wb, sheet.cell(i, 5).value)
        else:
            inward_date = sheet.cell(i, 5).value
        # Convert excel date to python date       
        if sheet.cell(i, 18).ctype == 3:            
            bbd_date = convert_excel_date(wb, sheet.cell(i, 18).value)
            #print('{} - {}'.format(sheet.cell(i, 18).ctype, py_date))
        else:
            bbd_date = sheet.cell(i, 18).value
            #print('{} - {}'.format(sheet.cell(i, 18).ctype, sheet.cell(i, 18).value))
        
        stock_data = {'code' : sheet.cell(i, 4).value, 'origin' : sheet.cell(i, 0).value, 'Inward' : inward_date, 'Movement' : sheet.cell(i, 8).value, 
                      'ITEM1' : sheet.cell(i, 9).value, 'ITEM2' : sheet.cell(i, 10).value, 'PreviousBalance' : sheet.cell(i, 12).value, 
                      'unit': sheet.cell(i, 13).value, 'pickup' : sheet.cell(i, 14).value, 'NewBalance' : sheet.cell(i, 15).value, 
                      'pmemo' : sheet.cell(i, 17).value, 'bbd' : bbd_date }                
        stock_list.append(stock_data)
        i += 1
    result = pd.DataFrame(stock_list)    
    return result, update_date


def generate_usage_file_to_upload(df, file_name, update_date):    
    #print(df)
    df['code'].replace('', np.nan, inplace=True)
    df['pickup'].replace('', np.nan, inplace=True)
    df['pmemo'].replace('', np.nan, inplace=True)   
    #df.to_csv('test1.csv')
    df.dropna(subset=['code', 'pickup', 'pmemo'], how='any', inplace=True)        
    #df.to_csv('test2.csv')
    df_preprocessed = df[['code', 'origin', 'Movement', 'ITEM1', 'ITEM2' 'unit', 'pickup', 'pmemo']]        
    df_preprocessed['update_date'] = pd.to_datetime(update_date, format='%d/%m/%Y')
    
    if ('Freezer' in file_name or 'Lucky' in file_name or 'OSP' in file_name or 'SR' in file_name or 'KKS' in file_name or 'Daily' in file_name):
        df_preprocessed['product_type'] = 'FRZ'
    else:
        df_preprocessed['product_type'] = 'DRY'                                   
    
    df_preprocessed['id'] = ''
    df_preprocessed['unit'] = df_preprocessed['unit'].str.lower()
    df_preprocessed = df_preprocessed.reset_index()
             
    df_preprocessed_usage = df_preprocessed            

    data = { 'id' : df_preprocessed_usage['id'], 'update_date' : df_preprocessed_usage['update_date'], 
                'product_type' : df_preprocessed_usage['product_type'], 'sf_code' : df_preprocessed_usage['code'], 
                'origin' : df_preprocessed['origin'], 'product_name' : df_preprocessed_usage['ITEM1'], 'product_name_jp' : df_preprocessed['ITEM2'],
                'move' : df_preprocessed_usage['Movement'], 'unit' : df_preprocessed_usage['unit'], 
                'pickup_qty' : df_preprocessed_usage['pickup'], 'memo' : df_preprocessed_usage['pmemo']}    
    df_processed = pd.DataFrame(data)       
    processed_file_name = file_name + '_processed_usage.xlsx'
    os.chdir('/home/siwanpark/ExcelData/convert_xlsm_to_csv/uploading_file')
    #os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Alex\Alex 2020\siwan\uploading_files")
    df_processed.to_excel(processed_file_name)


def generate_stock_file_to_upload(df, file_name, update_date):
    df['code'].replace('', np.nan, inplace=True)
    df['PreviousBalance'].replace('', np.nan, inplace=True)
    df['NewBalance'].replace('', np.nan, inplace=True)        
    df.dropna(subset=['code', 'PreviousBalance', 'NewBalance'], how='any', inplace=True)                                     
        
    df_preprocessed = df[['code', 'origin', 'Inward', 'ITEM1', 'ITEM2', 'unit', 'NewBalance', 'bbd']]
    df_preprocessed['NewBalance'] = df_preprocessed['NewBalance'].astype(float)
    df_preprocessed = df_preprocessed[df_preprocessed['NewBalance'] > 0.001]       

    df_preprocessed['update_date'] = pd.to_datetime(update_date, format='%d/%m/%Y')  # Windows => pd.to_datetime(update_date, format='%Y-%m-%d')
    
    if ('Freezer' in file_name or 'Lucky' in file_name or 'OSP' in file_name or 'SR' in file_name or 'KKS' in file_name or 'Daily' in file_name):
        df_preprocessed['product_type'] = 'FRZ'
    else:
        df_preprocessed['product_type'] = 'DRY'            

    # Assign location of storage
    if 'Lucky' in file_name:     
        df_preprocessed['location'] = 'LW'
    elif 'OSP' in file_name :
        df_preprocessed['location'] = 'OSP'  		           
    elif 'KKS' in file_name:
        df_preprocessed['location'] = 'KKS'  	        
    elif 'HELLMANN' in file_name:
        df_preprocessed['location'] = 'HE'  		    
    elif 'HAISON' in file_name:
        df_preprocessed['location'] = 'HS'  	
    elif 'Alex' in file_name:
        df_preprocessed['location'] = 'Alex'	    
    elif 'Daily' in file_name:
        df_preprocessed['location'] = 'Alex'	    
        
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
                'sf_code' : df_preprocessed['code'], 'origin' : df_preprocessed['origin'], 'inward' : df_preprocessed['Inward'],
                'product_name' : df_preprocessed['ITEM1'], 'product_name_jp' : df_preprocessed['ITEM2'], 'new_balance' : df_preprocessed['NewBalance'], 
                'unit' : df_preprocessed['unit'], 'bbd' : df_preprocessed['bbd'], 'location' : df_preprocessed['location']}
    df_processed = pd.DataFrame(data)    
    processed_file_name = file_name + '_processed_stock.xlsx'
    os.chdir('/home/siwanpark/ExcelData/convert_xlsm_to_csv/uploading_file')
    #os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Alex\Alex 2020\siwan\uploading_files")
    df_processed.to_excel(processed_file_name)


if __name__ == "__main__":
    main()














