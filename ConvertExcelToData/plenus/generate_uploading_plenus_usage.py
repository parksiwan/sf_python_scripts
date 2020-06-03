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
            pass
    raise ValueError('no valid date format found')


def convert_excel_date(excel_book, excel_date):
    ms_bbd_date_number = excel_date
    year, month, day, hour, minute, second = xlrd.xldate_as_tuple(ms_bbd_date_number, excel_book.datemode)
    py_date = datetime.datetime(year, month, day, hour, minute, second)
    return py_date


def main():
    # Change directory    
    os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Siwan\StockFiles\working_place")
    #os.chdir('/home/siwanpark/ExcelData/Alex/')
    excel_files = glob.glob('*.xls*')
    print(excel_files)
    for excel_file in excel_files:        
        file_name = excel_file.split('.')[0]
        df = generate_data_frame(excel_file)  #generate data frame
        #df1 = df.copy(deep=True)   
        generate_usage_file_to_upload(df, file_name, update_date)                
        os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Siwan\StockFiles\working_place")        
        #os.chdir('/home/siwanpark/ExcelData/Alex/')

def generate_data_frame(file_path):    
    loc = (file_path)     
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0)     
    
    product_type = (file_path.split('.')[0]).split('_')[-1]  # file_path = 'plenus_dry.xlsx'
    unit = 'ctn'
        
    usage_list = []    
    previous_code = sheet.cell(1, 0).value        
    sf_code = previous_code.split('/')[0]
    plenus_code = previous_code.split('/')[1]
    prodcut_name = sheet.cell(1, 1).value    
    description = sheet.cell(1, 2).value    

    # Convert excel date to python date       
    if sheet.cell(0, 3).ctype == 3:
        usage_month_1 = convert_excel_date(wb, sheet.cell(0, 3).value)
    else:
        usage_month_1 = sheet.cell(0, 3).value

    if sheet.cell(0, 5).ctype == 3:
        usage_month_2 = convert_excel_date(wb, sheet.cell(0, 5).value)
    else:
        usage_month_2 = sheet.cell(0, 5).value

    if sheet.cell(0, 7).ctype == 3:
        usage_month_3 = convert_excel_date(wb, sheet.cell(0, 7).value)
    else:
        usage_month_3 = sheet.cell(0, 7).value

    i = 1
    while sheet.cell(i, 0).value != 'end':    
        if sheet.cell(i, 0).value == previous_code or sheet.cell(i, 0).value == '':            
            if sheet.cell(i, 3).value != '':  # if 1st month usage data found
                customer, qty = extract_usage_data(sheet.cell(i, 3).value) 
                usage_data = create_usage_data(usage_month_1, product_type, customer, sf_code, plenus_code, product_name, description, qty, unit)
                usage_list.append(usage_data)                
            if sheet.cell(i, 5).value != '': # if 2nd month usage data found
                customer, qty = extract_usage_data(sheet.cell(i, 5).value) 
                usage_data = create_usage_data(usage_month_2, product_type, customer, sf_code, plenus_code, product_name, description, qty, unit)
                usage_list.append(usage_data)                
            if sheet.cell(i, 7).value != '': # if 3rd month usage data found
                customer, qty = extract_usage_data(sheet.cell(i, 7).value) 
                usage_data = create_usage_data(usage_month_3, product_type, customer, sf_code, plenus_code, product_name, description, qty, unit)
                usage_list.append(usage_data)                            
                
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
                        
        else:
            previous_code = sheet.cell(i, 0).value
            sf_code = previous_code.split('/')[0]
            plenus_code = previous_code.split('/')[1]
            prodcut_name = sheet.cell(i, 1).value    
            description = sheet.cell(i, 2).value   
            if sheet.cell(i, 3).value != '':  # if 1st month usage data found
                customer, qty = extract_usage_data(sheet.cell(i, 3).value) 
                usage_data = create_usage_data(usage_month, product_type, customer, sf_code, plenus_code, product_name, description, qty, unit)
                usage_list.append(usage_data)                
            if sheet.cell(i, 5).value != '': # if 2nd month usage data found
                customer, qty = extract_usage_data(sheet.cell(i, 5).value) 
                usage_data = create_usage_data(usage_month, product_type, customer, sf_code, plenus_code, product_name, description, qty, unit)
                usage_list.append(usage_data)                
            if sheet.cell(i, 7).value != '': # if 3rd month usage data found
                customer, qty = extract_usage_data(sheet.cell(i, 7).value) 
                usage_data = create_usage_data(usage_month, product_type, customer, sf_code, plenus_code, product_name, description, qty, unit)
                usage_list.append(usage_data)                
                   
        i += 1
    result = pd.DataFrame(stock_list)    
    return result, update_date

def extract_usage_data(input_string):    
    input_string_list = input_string.split()
    customer_list = input_string_list[:-1]
    customer = '_'.join(customer_list)
    qty_string = input_string_list[-1]
    qty = qty_string.split('(')[-1].replace(')', '')

    return customer, qty 
       

def create_usage_data(usage_month, product_type, customer, sf_code, plenus_code, product_name, description, qty, unit):
    usage_data = {'usage_month': usage_month, 'product_type': product_type, 'customer': customer, 'sf_code': sf_code, 
                  'plenus_code': plenus_code, 'product_name': product_name, 'description': description, 'qty': qty, 'unit': unit}                          
    return usage_data


def generate_usage_file_to_upload(df, file_name, update_date):    
    #print(df)
    df['code'].replace('', np.nan, inplace=True)
    df['pickup'].replace('', np.nan, inplace=True)
    df['pmemo'].replace('', np.nan, inplace=True)   
    #df.to_csv('test1.csv')
    df.dropna(subset=['code', 'pickup', 'pmemo'] update_date):    
    #print(df)
    df['code'].replace('', np.nan, inplace=True)
    df['pickup'].replace('', np.nan, inplace=Tru, how='any', inplace=True)        
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
    #os.chdir('/home/siwanpark/ExcelData/convert_xlsm_to_csv/uploading_file')
    os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Siwan\StockFiles\working_place\uploading_files")    
    df_processed.to_excel(processed_file_name)


if __name__ == "__main__":
    main()














