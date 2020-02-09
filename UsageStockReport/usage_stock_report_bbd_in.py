# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 22:13:56 2019
Read monthly usage / current stock and generate stock status report
@author: siwan
"""

from openpyxl import load_workbook
import xlsxwriter
import numpy as np
import pandas as pd
import datetime

minus_to_blank = lambda x : '-' if x < 0 else x
#def change_color(val):
#    if val > 0:
#        return 'background-color: red'

def main():
    # Files to be read
    sf_current_stock = 'sf_current_stock_bbd_in.csv'
    sf_monthly_usage = 'sf_monthly_usage.csv'
    sf_code_list = 'sf_code_list.csv'

    # Read csv files into data frame
    df_sf_current_stock = pd.read_csv(sf_current_stock)
    df_sf_monthly_usage = pd.read_csv(sf_monthly_usage)
    df_sf_code_list = pd.read_csv(sf_code_list)

    result = pd.DataFrame()
    result['sf_code'] = ''           # sf code
    result['product_type'] = ''      # product type

    result['product_name'] = ''      # product name
    result['m1'] = 0                 # Month 1
    result['m2'] = 0                 # Month 2
    result['m3'] = 0                 # Month 3
    result['m4'] = 0                 # Month 4
    result['m5'] = 0                 # Month 5
    result['m6'] = 0                 # Month 6
    result['m7'] = 0                 # Month 7
    result['m8'] = 0                 # Month 8
    result['m9'] = 0                 # Month 9
    result['m10'] = 0                # Month 10
    result['m11'] = 0                # Month 11
    result['m12'] = 0                # Month 12
    result['occurrence'] = 0         # count = occurrence
    result['ave_usage'] = 0          # average usage (sum of m / count of m)
    result['total_stock_qty'] = 0    # total stock qty

    result['current_stock_qty'] = 0  # current stock qty
    result['bbd'] = ''               # bbd
    result['month_diff'] = 0         # month difference
    result['general_usage'] = 0      # month_diff x average usage
    result['actual_usage'] = 0       # actual usage
    result['total_actual_usage'] = 0 # total_actual usage
    result['stock_waste'] = 0        # stock waste (over stock)
    result['stock_lasting'] = 0      # lasting stock
    result['low_stock'] = ''         # low stock alarm (total actual stock < average usage)

    data_list = []
    #ave_usage = 0
    for row_code in df_sf_code_list.itertuples():
        ave_usage = 0
        # read usage info
        df_usage_of_code = df_sf_monthly_usage[df_sf_monthly_usage['sf_code'] == row_code[1]]
        if len(df_usage_of_code) > 0:
            occurrence = 0
            m = [-1 for x in range(12)]  # initializing by '-1'
            #df_usage_of_code = df_usage_of_code.reset_index()
            #print((df_usage_of_code.iloc[0, 1]))
            temp_index = datetime.datetime.strptime(df_usage_of_code.iloc[0, 1], "%d/%m/%Y")
            #print(df_usage_of_code)
            #print(temp_index.month)
            for i in range(temp_index.month - 1, 12):  # assign 0 to usage month initially => Need to improve
                m[i] = 0
                occurrence += 1

            usage_sub_total = 0
            for row_usage_of_code in df_usage_of_code.itertuples():
                month_index = datetime.datetime.strptime(row_usage_of_code[2], "%d/%m/%Y")

                m[month_index.month - 1] = row_usage_of_code[3]
                usage_sub_total += row_usage_of_code[3]
                
            ave_usage = 0 if len(df_usage_of_code) == 0 else float(usage_sub_total / occurrence)
            data = { 'sf_code': row_code[1], 'product_type': row_code[2], 'product_name': row_code[3], 'm1': minus_to_blank(m[0]),
                     'm2': minus_to_blank(m[1]), 'm3': minus_to_blank(m[2]), 'm4': minus_to_blank(m[3]), 'm5': minus_to_blank(m[4]),
                     'm6': minus_to_blank(m[5]), 'm7': minus_to_blank(m[6]),
                     'm8': minus_to_blank(m[7]), 'm9': minus_to_blank(m[8]), 'm10': minus_to_blank(m[9]),
                     'm11': minus_to_blank(m[10]), 'm12': minus_to_blank(m[11]),
                     'occurrence': occurrence, 'ave_usage': ave_usage,
                     'total_stock_qty': 0, 'current_stock_qty': 0, 'bbd': '', 'month_diff': 0,
                     'general_usage': 0, 'actual_usage': 0, 'total_actual_usage': 0, 'stock_waste': 0,
                     'stock_lasting': 0, 'low_stock': '' }

        else:
            data = { 'sf_code': row_code[1], 'product_type': row_code[2], 'product_name': row_code[3], 'm1': '',
                     'm2': '', 'm3': '', 'm4': '', 'm5': '', 'm6': '', 'm7': '',
                     'm8': '', 'm9': '', 'm10': '', 'm11': '', 'm12': '',
                     'occurrence': '', 'ave_usage': '',
                     'total_stock_qty': 0, 'current_stock_qty': 0, 'bbd': '', 'month_diff': 0,
                     'general_usage': 0, 'actual_usage': 0, 'total_actual_usage': 0, 'stock_waste': 0,
                     'stock_lasting': 0, 'low_stock': '' }
        data_list.append(data)
        first_line_index = len(data_list)

        # read stock info
        df_stock_of_code = df_sf_current_stock[df_sf_current_stock['sf_code'] == row_code[1]]
        #print(row_code[1])
        #current_date = pd.to_datetime(df_stock_of_code.iat[0, 1])
        if len(df_stock_of_code) > 0:
            current_date = datetime.datetime.strptime(df_stock_of_code.iat[0, 1], "%d/%m/%Y")
            #print(current_date)
            temp_data_list = []
            total_current_stock = 0
            previous_date = current_date
            for row_stock_of_code in df_stock_of_code.itertuples():
                temp_current_stock_qty = row_stock_of_code[4]             # 0
                #temp_bbd = pd.to_datetime(row_stock_of_code[6])           # 1
                temp_bbd = datetime.datetime.strptime(row_stock_of_code[6], "%d/%m/%Y")                
                temp_month_diff = temp_bbd - previous_date
                #temp_month_diff = temp_month_diff / np.timedelta64(1,'M') # 2
                temp_month_diff = temp_month_diff.total_seconds() / (3600 * 24 * 30) # 2
                temp_general_usage = ave_usage * temp_month_diff          # 3
                temp_actual_usage = temp_current_stock_qty                # 4
                temp_stock_waste = 0.0                                    # 5
                temp_stock_lasting = 0                                    # 6
                temp_low_stock = 0                                        # 7
                total_current_stock += temp_current_stock_qty                

                temp_data = { 'current_stock_qty': temp_current_stock_qty, 'bbd': temp_bbd,
                              'month_diff': temp_month_diff, 'general_usage': temp_general_usage,
                              'actual_usage': temp_actual_usage, 'stock_waste': temp_stock_waste,
                              'stock_lasting': temp_stock_lasting, 'low_stock': temp_low_stock }
                temp_data_list.append(temp_data)
                previous_date = temp_bbd
            temp_stock_of_code = pd.DataFrame(temp_data_list)
            
            # calculate actual usage
            for i in range(len(temp_stock_of_code)):                
                if temp_stock_of_code.iat[i, 4] < temp_stock_of_code.iat[i, 3]:  # actual_usage < general_usage
                    for j in range(i + 1, len(temp_stock_of_code)):
                        general_minus_actual = temp_stock_of_code.iat[i, 3] - temp_stock_of_code.iat[i, 4]
                        if temp_stock_of_code.iat[j, 4] > general_minus_actual:
                            temp_stock_of_code.iat[i, 4] += general_minus_actual
                            temp_stock_of_code.iat[j, 4] -= general_minus_actual
                            break
                        else:
                            temp_stock_of_code.iat[i, 4] += temp_stock_of_code.iat[j, 4]
                            temp_stock_of_code.iat[j, 4] = 0

            # calculate stock waste & stock lasting & low stock status
            total_actual_usage = 0
            for i in range(len(temp_stock_of_code)):                
                if temp_stock_of_code.iat[i, 4] > temp_stock_of_code.iat[i, 3]:  # actual_usage > general_usage
                    temp_stock_of_code.iat[i, 5] = float(temp_stock_of_code.iat[i, 4] - temp_stock_of_code.iat[i, 3])
                    temp_stock_of_code.iat[i, 4] -= temp_stock_of_code.iat[i, 5]
                total_actual_usage += temp_stock_of_code.iloc[i, 4]

            # calculate stock lasting
            stock_lasting = 'Dead Stock' if ave_usage == 0 else float(total_actual_usage / ave_usage)

            if (total_actual_usage < ave_usage):
                low_stock = 'low stock alarm'
            else:
                low_stock = ''

            # append processed stock info to list
            # if first stock line, should be updated on the first line otherwise appended
            data_list[first_line_index - 1]['total_stock_qty'] = total_current_stock
            data_list[first_line_index - 1]['current_stock_qty'] = temp_stock_of_code.iat[0, 0]
            data_list[first_line_index - 1]['bbd'] = temp_stock_of_code.iat[0, 1].date()
            data_list[first_line_index - 1]['month_diff'] = temp_stock_of_code.iat[0, 2]
            data_list[first_line_index - 1]['general_usage'] = temp_stock_of_code.iat[0, 3]
            data_list[first_line_index - 1]['actual_usage'] = temp_stock_of_code.iat[0, 4]
            data_list[first_line_index - 1]['total_actual_usage'] = total_actual_usage
            data_list[first_line_index - 1]['stock_waste'] = temp_stock_of_code.iat[0, 5]
            data_list[first_line_index - 1]['stock_lasting'] = stock_lasting
            data_list[first_line_index - 1]['low_stock'] = low_stock
            if len(temp_stock_of_code) > 1:
                for i in range(1, len(temp_stock_of_code)):
                    data = { 'sf_code': row_code[1], 'product_type': row_code[2], 'product_name': row_code[3], 'm1': '',
                             'm2': '', 'm3': '', 'm4': '', 'm5': '', 'm6': '', 'm7': '',
                             'm8': '', 'm9': '', 'm10': '', 'm11': '', 'm12': '',
                             'occurrence': '', 'ave_usage': '', 'total_stock_qty': '',
                             'current_stock_qty': temp_stock_of_code.iat[i, 0], 'bbd': temp_stock_of_code.iat[i, 1].date(),
                             'month_diff': temp_stock_of_code.iat[i, 2], 'general_usage': temp_stock_of_code.iat[i, 3],
                             'actual_usage': temp_stock_of_code.iat[i, 4], 'total_actual_usage': '', 'stock_waste': temp_stock_of_code.iat[i, 5],
                             'stock_lasting': '', 'low_stock': '' }
                    data_list.append(data)
        else:
            data_list[first_line_index - 1]['sf_code'] = row_code[1]
            data_list[first_line_index - 1]['product_type'] = row_code[2]
            data_list[first_line_index - 1]['product_name'] = row_code[3]
            
            data_list[first_line_index - 1]['total_stock_qty'] = ''
            data_list[first_line_index - 1]['current_stock_qty'] = ''
            data_list[first_line_index - 1]['bbd'] = ''
            data_list[first_line_index - 1]['month_diff'] = ''
            data_list[first_line_index - 1]['general_usage'] = ''
            data_list[first_line_index - 1]['actual_usage'] = ''
            data_list[first_line_index - 1]['total_actual_usage'] = ''
            data_list[first_line_index - 1]['stock_waste'] = ''
            data_list[first_line_index - 1]['stock_lasting'] = ''
            data_list[first_line_index - 1]['low_stock'] = ''

    result = pd.DataFrame(data_list)    

    writer = pd.ExcelWriter('sf_usage_stock_report_bbd_in.xlsx', engine='xlsxwriter')
    result.to_excel(writer, index=False, sheet_name='usage_stock')
    workbook = writer.book
    worksheet = writer.sheets['usage_stock']
    #format1_column = workbook.add_format({'bg_color' : '#FFC7CE', 'font_color' : '#9C0006'})
    #format2_column = workbook.add_format({'bg_color' : '#C6EFCE', 'font_color' : '#9C0006'})

    #worksheet.conditional_format('Y1:Y3000', {'type':'cell','criteria':'>', 'value': 0,'format': format1_column })
    #worksheet.conditional_format('A2:Q3000', {'type':'formula','criteria':'=AND($A2<>"",$Q2="")','format': format2_column })
    writer.save()


if __name__ == '__main__':
    main()
