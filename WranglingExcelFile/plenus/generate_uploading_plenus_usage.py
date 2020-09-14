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
    #os.chdir('/home/siwanpark/ExcelData/plenus/')
    excel_files = glob.glob('*.xls*')
    print(excel_files)
    for excel_file in excel_files:                
        generate_data_frame(excel_file)  #generate data frame        
        os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Siwan\StockFiles\working_place")        
        #os.chdir('/home/siwanpark/ExcelData/plenus')


def generate_data_frame(file_path):    
    loc = (file_path)     
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0)     
    
    file_name = file_path.split('.')[0]
    product_type = (file_path.split('.')[0]).split('_')[-1]  # file_path = 'plenus_dry.xlsx'
    unit = 'ctn'
        
    usage_list = []    
    
    previous_code = sheet.cell(1, 0).value        
    sf_code = previous_code.split('/')[0]
    sf_code = sf_code.strip()
    plenus_code = previous_code.split('/')[1]
    plenus_code = plenus_code.strip()
    product_name = sheet.cell(1, 1).value    
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
        else:
            previous_code = sheet.cell(i, 0).value
            sf_code = previous_code.split('/')[0]
            sf_code = sf_code.strip()
            plenus_code = previous_code.split('/')[1]
            plenus_code = plenus_code.strip()
            product_name = sheet.cell(i, 1).value    
            description = sheet.cell(i, 2).value   
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
                   
        i += 1
        
    df_usage = pd.DataFrame(usage_list)            
    usage_file_name = file_name + '_processed_usage.xlsx'
    #os.chdir('/home/siwanpark/ExcelData/plenus')
    os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Siwan\StockFiles\working_place\uploading_files")    
    df_usage.to_excel(usage_file_name)
    

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


if __name__ == "__main__":
    main()














