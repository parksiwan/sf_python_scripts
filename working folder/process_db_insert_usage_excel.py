# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 22:25:11 2019

@author: siwan
"""

import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
import glob

def main():
    try:
        conn = pg.connect("host='localhost' dbname=sfstock user=siwan password='psw1101714'")
        insert_cursor = conn.cursor()        
        excel_files = glob.glob('*.xlsx')
        
        for excel_file in excel_files:
            df = pd.read_excel(excel_file)
            for row_df in df.itertuples():
                
                insert_query = "insert into  inventory_usage (update_date, sf_code, pickup_qty, unit, memo, product_type, product_name) values ('"  \
                               + str(row_df[2].date()) + "','" + str(row_df[4]) + "'," + str(row_df[8]) + ",'" + str(row_df[7]) + "', '" \
                               + str(row_df[9]) + "', '" + str(row_df[3]) + "','" + str(row_df[5]) + "')"                                                    
                insert_cursor.execute(insert_query)
            print (excel_file)    
        conn.commit()                                       
    except (Exception, pg.Error) as error:
        print ("Error fetching data from db", error)
    finally:
        if (conn):
            insert_cursor.close()            
            conn.close()
    
if __name__ == "__main__":
    main()