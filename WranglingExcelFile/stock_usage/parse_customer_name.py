from dateutil.parser import parse
import xlrd
import os
import platform
import datetime
import glob
import pandas as pd
import numpy as np

'''
Add HUBX condition and file path on 3/6/2020
'''

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
    for date_format in ('%Y-%m-%d','%Y-%m-%d %H:%M:%S', '%d-%m-%Y', '%d.%m.%Y', '%Y.%m.%d', '%d.%m.%y', '%d/%m/%Y', '%d/%m/%Y %H:%M:%S'):
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
    if platform.system() == 'Linux':
        os.chdir('/home/siwanpark/ExcelData/')
    else:
        os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Siwan\StockFiles\working_place")    

    excel_files = glob.glob('*.xls*')
    print(excel_files)
    for excel_file in excel_files:        
        file_name = excel_file.split('.')[0]
        generate_data_frame(excel_file, file_name)  #generate data frame        
        #generate_excel_file(df, file_name)
        
        if platform.system() == 'Linux':
            os.chdir('/home/siwanpark/ExcelData/')
        else:
            os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Siwan\StockFiles\working_place")


def generate_data_frame(file_path, file_name):
    loc = (file_path)
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)    
    
    usage_list = []
    customer_name_set = set()
    i = 1
    while sheet.cell(i, 0).value != 'end':       
        update_date = sheet.cell(i, 1).value
        '''
        if sheet.cell(i, 1).ctype == 3 or sheet.cell(i, 1).ctype == 2:
            update_date = convert_excel_date(wb, sheet.cell(i, 1).value).date()
        elif sheet.cell(i, 1).ctype == 0:
            update_date = datetime.datetime.strptime('01/01/2020', "%d/%m/%Y").date()
        elif sheet.cell(i, 1).ctype == 1:
            update_date = datetime.datetime.strptime('01/01/2020', "%d/%m/%Y").date()
        else:
            update_date = datetime.datetime.strptime('01/01/2020', "%d/%m/%Y").date()
        '''
        
        customer_temp_name = parse_pickup_memo(sheet.cell(i, 7).value)
        customer_name_set.add(customer_temp_name.upper())  # add customer name to set
        #if len(memo_list) >= 2:
        usage_data = {'id' : sheet.cell(i, 0).value, 'update_date' : update_date, 'product_type' : sheet.cell(i, 2).value, 
                      'sf_code' : sheet.cell(i, 3).value, 'product_name' : sheet.cell(i, 4).value, 'pickup_qty' : sheet.cell(i, 5).value, 
                      'unit' : sheet.cell(i, 6).value, 'split' : '', 'split_qty' : '', 'memo' : sheet.cell(i, 7).value, 'location': sheet.cell(i, 8).value, 
                      'origin' : sheet.cell(i, 9).value, 'product_name_jp' : sheet.cell(i, 10).value, 'cust_name' : customer_temp_name.upper() }
        usage_list.append(usage_data)
        #else:
        #    for usage_count in range(len(memo_list)):
        #        if memo_list[usage_count] != ' ':
        #            pickup_qty = parse_pickup_qty(memo_list[usage_count])
        #            #print(pickup_qty)
        #            usage_data = {'id' : sheet.cell(i, 0).value, 'update_date' : update_date, 'product_type' : sheet.cell(i, 2).value, 
        #                    'sf_code' : sheet.cell(i, 3).value, 'product_name' : sheet.cell(i, 4).value, 'pickup_qty' : sheet.cell(i, 5).value, 
        #                    'unit' : sheet.cell(i, 6).value, 'split' : '*', 'split_qty' : pickup_qty, 'memo' : memo_list[usage_count], 'origin': sheet.cell(i, 8).value, 
        #                    'product_name_jp' : sheet.cell(i, 9).value }
        #            usage_list.append(usage_data)

        i += 1

    result = pd.DataFrame(usage_list)
    processed_file_name = file_name + '_processed_customer.xlsx'
    result.to_excel(processed_file_name)

    # generates excel of SET for customer name
    customer_name_list = list(customer_name_set)
    customer_name_df = pd.DataFrame(customer_name_list)
    customer_name_df.to_excel('customer_name_set.xlsx')

    #return result

'''
def parse_pickup_qty(pickup_string):    
    print(pickup_string)
    
    pickup_qty = pickup_string.split('-')[1]
    #print('{} - {}'.format(pickup_string, pickup_qty))
    if pickup_qty.strip().isdigit() == True:
        return float(pickup_qty)
    else:
        return 0
'''    


def parse_pickup_memo(memo_string):
    memo_list = memo_string.split('-')
    memo_list[0] = memo_list[0].strip()  # remove leading and trailing spaces
    customer_string = memo_list[0].split(' ')
    if customer_string[0].upper() == 'FOR':
        return customer_string[1]
    else:
        return memo_list[0]


if __name__ == "__main__":
    main()
