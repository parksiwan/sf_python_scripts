from django.shortcuts import render
#from .models import Inventory
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import xlrd 
import os
import platform
import datetime
import glob
import pandas as pd
import numpy as np
from django.http import HttpResponse


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


def generate_packing_list():    
    df_result = read_excel_for_packing_list()    
    #print (df_result)
    #df_result['unit'] = df_result['unit'].replace(np.nan, 'No Stock')
    #df_result['min_stock'] = df_result['min_stock'].replace(np.nan, 'No MIN stock')

    if platform.system() == 'Linux':
        os.chdir('/home/siwanpark/ExcelData/')
    else:
        os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット")

    excel_result = 'TF_PackingList' + str(datetime.date.today()) + '.xlsx'
    df_result.to_excel(excel_result)

    #return render(request, 'inventory/daily_stock.html', {'df_result': df_result} )


def read_excel_for_packing_list():
    if platform.system() == 'Linux':
        os.chdir('/home/siwanpark/ExcelData/TFPackingList/')
    else:
        os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\SF_Misc")             
    
    stock_pickup_file = glob.glob('Alex*.xls*')    
    stock_pickup_df = pd.DataFrame()
    
    stock_pickup_df = data_frame_from_pickup_list(stock_pickup_file[0])  #generate data frame          
    stock_pickup_df = stock_pickup_df[(stock_pickup_df['pmemo'].str.upper()).str.contains('TF')]
    
    #retail_status_file_name = retail_status_file[0].split('.')[0]
    if platform.system() == 'Linux':
        os.chdir('/home/siwanpark/ExcelData/TFPackingList/')
    else:
        os.chdir(r"\\192.168.20.50\AlexServer\SD共有\ボタニーパレット\SF_Misc")                 

    po_file = glob.glob('*po*.xls*')   
    po_df = pd.DataFrame()    
    
    po_df = data_frame_from_purchase_order(po_file[0]) 
    
    outer_joined_df = stock_pickup_df.merge(po_df, on='code', how='outer')    
    result_df = outer_joined_df[['code', 'Inward', 'ITEM1', 'ITEM2', 'description', 'unit', 'pickup', 'pmemo', 'bbd', 'po_unit', 'po_qty','po_prod_name' ]]
    #left_joined_df['NewBalance'] = left_joined_df['NewBalance'].fillna(0)
    
    return result_df


def data_frame_from_purchase_order(file_path):    
    loc = (file_path)     
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0)     
    
    po_list = []
    i = 1
    #inward_date = '2020-02-01'
    #bbd_date = '2020-01-01'
    while sheet.cell(i, 0).value != 'end':                                                                           
        po_data = {'code' : sheet.cell(i, 1).value, 'po_prod_name': sheet.cell(i, 3).value, 'po_qty': sheet.cell(i, 5).value, 'po_unit' : sheet.cell(i, 6).value }                        
        po_list.append(po_data)
        i += 1
    result = pd.DataFrame(po_list)    
        
    return result


def data_frame_from_pickup_list(file_path):    
    loc = (file_path)     
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0)     
    #update_date = sheet.cell_value(1, 9).split(':')[1]
    
    #update_date = update_date.strip()
   
    #for i in range(3, sheet.nrows):  
    stock_list = []
    i = 4
    #inward_date = '2020-02-01'
    #bbd_date = '2020-01-01'
    while sheet.cell(i, 1).value != 'end':    
        # Convert excel date cell to python date              
        if sheet.cell(i, 5).ctype == 3 or sheet.cell(i, 5).ctype == 2:
            inward_date = convert_excel_date(wb, sheet.cell(i, 5).value).date()
        elif sheet.cell(i, 5).ctype == 0:
            inward_date = datetime.datetime.strptime('01/01/2020', "%d/%m/%Y").date()
        elif sheet.cell(i, 5).ctype == 1:
            inward_date = datetime.datetime.strptime('01/01/2020', "%d/%m/%Y").date()
        else:
            inward_date = datetime.datetime.strptime('01/01/2020', "%d/%m/%Y").date()
        
        # Convert excel date to python date       
        #print('{} | {} | {}'.format(type(inward_date), sheet.cell(i, 18).value, sheet.cell(i, 18).ctype))
        if sheet.cell(i, 18).ctype == 3 or sheet.cell(i, 18).ctype == 2:               
            bbd_date = convert_excel_date(wb, sheet.cell(i, 18).value).date()            
        elif sheet.cell(i, 18).ctype == 0:
            bbd_date = inward_date
        elif sheet.cell(i, 18).ctype == 1:
            if sheet.cell(i, 18).value == '-':
                bbd_date = datetime.datetime.strptime('31/12/2099', "%d/%m/%Y").date()
            elif sheet.cell(i, 18).value == 'Check BBD':                
                one_year = datetime.timedelta(weeks=52)      
                bbd_date = inward_date + one_year
            else:                    
                one_year = datetime.timedelta(weeks=52)      
                bbd_date = inward_date + one_year       
                                                       
        
        stock_data = {'code' : sheet.cell(i, 4).value, 'Inward' : inward_date, 'ITEM1' : sheet.cell(i, 9).value, 'ITEM2' : sheet.cell(i, 10).value , 
                      'description' : sheet.cell(i, 11).value, 'unit': sheet.cell(i, 13).value, 'pickup' : sheet.cell(i, 14).value, 
                      'pmemo' : sheet.cell(i, 17).value, 'bbd' : bbd_date }                        
        stock_list.append(stock_data)
        i += 1
    result = pd.DataFrame(stock_list)    
        
    return result


if __name__ == "__main__":
    generate_packing_list()    