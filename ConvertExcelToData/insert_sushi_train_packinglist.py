from sushi_train_packing_list import STPackingList
from database import Database
import os, xlrd, datetime, glob


def convert_excel_date(excel_book, excel_date):
    ms_bbd_date_number = excel_date
    year, month, day, hour, minute, second = xlrd.xldate_as_tuple(ms_bbd_date_number, excel_book.datemode)
    py_date = datetime.datetime(year, month, day, hour, minute, second)
    return py_date


def read_excel_and_insert_to_db():
    os.chdir('/home/siwanpark/ExcelData/')
    excel_files = glob.glob('*.xls*')    
    file_number = 1 
    for excel_file in excel_files:        
        print('{} - {}'.format(excel_file, file_number))
        generate_data_frame_and_insert_to_db(excel_file)  #generate data frame        
        file_number += 1


def generate_data_frame_and_insert_to_db(file_path):    
    loc = (file_path)     
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0) 
       
    #dispatch_date = sheet.cell_value(6, 9)    
    #dispatch_date = update_date.strip()
    # Convert excel date to python date       
    if sheet.cell(6, 9).ctype == 3 or sheet.cell(6, 9).ctype == 2:
        dispatch_date = convert_excel_date(wb, sheet.cell(6, 9).value).date()
    elif sheet.cell(6, 9).ctype == 1:
        dispatch_date = datetime.datetime.strptime(sheet.cell(6, 9).value, "%d/%m/%Y")
    else:
        dispatch_date = sheet.cell(6, 9).value
    
    shipment_info = file_path
    #print(dispatch_date)
    if 'NSW' in shipment_info:
        customer = 'STNSW'
    elif 'SQ' in shipment_info:
        customer = 'STQLD'
    elif 'SA' in shipment_info:
        customer = 'STADL'
    else:
        customer = 'UNKNOWN'

    if 'DRY' in shipment_info:
        product_type = 'DRY'
    elif 'FRZ' in shipment_info:
        product_type = 'FRZ'
    else:
        product_type = 'UNKNOWN'

    #for i in range(3, sheet.nrows):    
    
    i = 15
    while sheet.cell(i, 4).value != 'TOTAL':                                    
        if sheet.cell(i, 2).value != '' and sheet.cell(i, 2).value != '-' and sheet.cell(i, 5).value != '':  # when actual data is found
            if sheet.cell(i, 7).ctype == 3 or sheet.cell(i, 7).ctype == 2:
                arrival_date = convert_excel_date(wb, sheet.cell(i, 7).value).date()       
            elif sheet.cell(i, 7).ctype == 1:
                arrival_date = datetime.datetime.strptime(sheet.cell(i, 7).value, "%d/%m/%Y")
            else:                
                if sheet.cell(i, 7).value == '' or sheet.cell(i, 7).value == '=' or sheet.cell(i, 7).value == '-':
                    arrival_date = None                    
                else:                    
                    arrival_date = dispatch_date
            
            st_packing_list = STPackingList(dispatch_date, product_type, customer, sheet.cell(i, 2).value, sheet.cell(i, 3).value, 
                                            sheet.cell(i, 5).value, sheet.cell(i, 6).value, arrival_date)
            st_packing_list.save_to_db()
            
        i += 1
    

def insert_excel_to_db():
    Database.initialise(database="sfstock", user="siwan", password="psw1101714", host="localhost")

    read_excel_and_insert_to_db()        
    #user_from_db = User.load_from_db_by_email('jose@schoolofcode.me')
    #print(user_from_db)


if __name__ == "__main__":
    insert_excel_to_db()