import os, xlrd, datetime, glob
import pandas as pd


def convert_excel_date(excel_book, excel_date):
    ms_bbd_date_number = excel_date
    year, month, day, hour, minute, second = xlrd.xldate_as_tuple(ms_bbd_date_number, excel_book.datemode)
    py_date = datetime.datetime(year, month, day, hour, minute, second)
    return py_date


def read_excels_and_aggregate():
    aggregated_df = pd.DataFrame()
    os.chdir('/home/siwanpark/ExcelData/sushi_train/ST')
    excel_files = glob.glob('*.xls*')    
    for excel_file in excel_files:        
        df = generate_data_frame_and_insert_to_db(excel_file)  #generate data frame   
        aggregated_df = pd.concat([aggregated_df, df], ignore_index=True)     

    aggregated_excel = 'SushiTrainPL_' + str(datetime.date.today()) + '.xlsx'
    aggregated_df.to_excel(aggregated_excel)            


def generate_data_frame_and_insert_to_db(file_path):    
    loc = (file_path)     
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0)     
    #dispatch_date = sheet.cell_value(6, 9)    
    #dispatch_date = update_date.strip()
    # Convert excel date to python date       
    if sheet.cell(6, 9).ctype == 3:
        dispatch_date = convert_excel_date(wb, sheet.cell(6, 9).value).date()
    else:
        dispatch_date = sheet.cell(6, 9).value
    
    shipment_info = sheet.cell_value(7, 9)
    
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
    #print(file_path)  
    pl_list = []
    i = 15
    print(file_path)
    while sheet.cell(i, 4).value != 'TOTAL':                                    
        if sheet.cell(i, 2).value != '' and sheet.cell(i, 5).value != '':  # when actual data is foundinsert_excel_to_db()
            if sheet.cell(i, 7).ctype == 3:
                arrival_date = convert_excel_date(wb, sheet.cell(i, 7).value).date()                
            else:                
                if sheet.cell(i, 7).value == '':
                    arrival_date = None                    
                else:
                    arrival_date = '2099-12-31'                        

            
            pl_data = {'dispatch_date': dispatch_date, 'product_type': product_type, 'customer' : customer, 'sf_code' : sheet.cell(i, 2).value, 
                      'product_name': sheet.cell(i, 3).value, 'qty': sheet.cell(i, 5).value, 'unit' : sheet.cell(i, 6).value, 'arrival_date' : arrival_date }                     
            pl_list.append(pl_data)
        i += 1
    
    result_df = pd.DataFrame(pl_list)
    return result_df

if __name__ == "__main__":
    read_excels_and_aggregate()