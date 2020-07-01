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
    #os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Siwan\StockFiles\working_place")
    os.chdir('/home/siwanpark/ExcelData/plenus/')
    excel_files = glob.glob('*.xls*')
    print(excel_files)
    for excel_file in excel_files:
        generate_data_frame(excel_file)  #generate data frame
        #os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Siwan\StockFiles\working_place")
        os.chdir('/home/siwanpark/ExcelData/plenus/')


def generate_data_frame(file_path):
    loc = (file_path)
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)

    file_name = file_path.split('.')[0]
    product_type = (file_path.split('.')[0]).split('_')[2]  # file_path = 'plenus_dry.xlsx'
    unit = 'ctn'

    stock_list = []
    stock_base_date = datetime.datetime.today().date()
    previous_code = sheet.cell(1, 0).value
    sf_code = previous_code.split('/')[0]
    plenus_code = previous_code.split('/')[1]
    product_name = sheet.cell(1, 1).value
    description = sheet.cell(1, 2).value

    i = 1
    while sheet.cell(i, 0).value != 'end':
        if sheet.cell(i, 0).value == previous_code or sheet.cell(i, 0).value == '':
            if sheet.cell(i, 9).value != '': # if stock data found
                bbd, qty = extract_stock_data(sheet.cell(i, 9).value)
                stock_data = create_stock_data(stock_base_date, product_type, sf_code, plenus_code, product_name, description, qty, unit, bbd)
                stock_list.append(stock_data)
        else:
            previous_code = sheet.cell(i, 0).value
            sf_code = previous_code.split('/')[0]
            plenus_code = previous_code.split('/')[1]
            product_name = sheet.cell(i, 1).value
            description = sheet.cell(i, 2).value
            if sheet.cell(i, 9).value != '': # if stock data found
                bbd, qty = extract_stock_data(sheet.cell(i, 9).value)
                stock_data = create_stock_data(stock_base_date, product_type, sf_code, plenus_code, product_name, description, qty, unit, bbd)
                stock_list.append(stock_data)

        i += 1

    df_usage = pd.DataFrame(stock_list)
    stock_file_name = file_name + '_processed_stock.xlsx'
    os.chdir('/home/siwanpark/ExcelData/plenus')
    #os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\Siwan\StockFiles\working_place\uploading_files")
    df_usage.to_excel(stock_file_name)


def extract_stock_data(input_string):
    input_list = input_string.split()
    stock_qty = input_list[0]
    temp_string = input_list[1]
    bbd = temp_string.split(':')[1]
    stock_bbd = datetime.datetime.strptime(bbd, "%d/%m/%Y")
    #print(type(stock_bbd))

    return stock_bbd, stock_qty


def create_stock_data(stock_base_date, product_type, sf_code, plenus_code, product_name, description, qty, unit, bbd):
    stock_data = {'stock_base_date': stock_base_date, 'product_type': product_type, 'sf_code': sf_code, 'plenus_code': plenus_code,
                  'product_name': product_name, 'description': description, 'qty': qty, 'unit': unit, 'bbd': bbd}
    return stock_data


if __name__ == "__main__":
    main()
