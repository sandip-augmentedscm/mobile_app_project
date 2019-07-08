import numpy as np
import pandas as pd
from numpy import nan
import pymysql
from sqlalchemy import exc, create_engine
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/sales_db',\
                       echo=False)
import time
from statistics import mean, stdev
from datetime import timedelta
import warnings
warnings.simplefilter(action='ignore')

from calculate_skewness import *
from table_territory_master import create_territory_master
from table_salesperson_master import create_salesperson_master
from table_customer_master import create_customer_master
from table_sku_master import create_sku_master
from table_customer_sku_details import create_customer_sku_details
from table_territory_wise_details import create_territory_wise_details
from table_customer_wise_details import create_customer_wise_details
from table_sku_wise_details import create_sku_wise_details


input_df = pd.read_excel('csv_files\\Bellary SD Sales.xlsx')

# Date today
current_date = pd.Timestamp('2018-05-18')

# Filter the data from AUG 1, 2017 to current_date
input_df = input_df[input_df['Bill Date'] >= pd.Timestamp('2017-08-01')]
input_df = input_df[input_df['Bill Date'] <= current_date]

# Create 'territory_master' table
territory_master_df = create_territory_master(input_df)
territory_master_df.fillna('NA').to_csv('csv_files\\territory_master.csv', index=False)

# Create 'salesperson_master' table
salesperson_master_df = create_salesperson_master(territory_master_df)
salesperson_master_df.fillna('NA').to_csv('csv_files\\salesperson_master.csv', index=False)

# Create 'customer_master' table
customer_master_df = create_customer_master(input_df, territory_master_df)
customer_master_df.fillna('NA').to_csv('csv_files\\customer_master.csv', index=False)

# Create 'sku_master' table
sku_master_df = create_sku_master(input_df)
sku_master_df.fillna('NA').to_csv('csv_files\\sku_master.csv', index=False)

# Create 'customer_sku_details' table
customer_sku_details_df = create_customer_sku_details(input_df, customer_master_df, sku_master_df)
customer_sku_details_df.fillna('NA').to_csv('csv_files\\customer_sku_details.csv', index=False)

# Create 'territory_wise_details' table
territory_wise_details_df = create_territory_wise_details(input_df, territory_master_df)
territory_wise_details_df.replace([np.inf, -np.inf], np.nan, inplace=True)
territory_wise_details_df.fillna('NA').to_csv('csv_files\\territory_wise_details.csv', index=False)

# Create 'customer_wise_details' table
customer_wise_details_df = create_customer_wise_details(input_df, customer_master_df)
customer_wise_details_df.replace([np.inf, -np.inf], np.nan, inplace=True)
customer_wise_details_df.fillna('NA').to_csv('csv_files\\customer_wise_details.csv', index=False)

# Create 'sku_wise_details' table
sku_wise_details_df = create_sku_wise_details(input_df, sku_master_df)
sku_wise_details_df.replace([np.inf, -np.inf], np.nan, inplace=True)
sku_wise_details_df.fillna('NA').to_csv('csv_files\\sku_wise_details.csv', index=False)


# Save data in mysql database
option = 'append'
# How to behave if the table already exists.
# 'fail': Raise a ValueError.
# 'replace': Drop the table before inserting new values.
# 'append': Insert new values to the existing table.

def update_database(table_name, unique_key, df, option):
    query1 = 'SELECT * FROM {}'.format(table_name)
    table_copy_df = pd.read_sql(query1, con=engine)
    
    cond = table_copy_df[unique_key].isin(df[unique_key]) == True
    df.drop(df[cond].index, inplace = True)
    
    df.to_sql(name=table_name, con=engine, if_exists=option, index=False)
    
start = time.clock()
update_database('salesperson_master', ['salesperson_ID', 'salesperson_name'],\
                salesperson_master_df, option)
update_database('territory_master', ['territory_ID', 'salesperson_ID'],\
                territory_master_df, option)
update_database('customer_master', ['customer_ID', 'customer_code'],\
                customer_master_df, option)
update_database('sku_master', ['sku_ID', 'sku_code'], sku_master_df, option)
update_database('customer_sku_details', ['customer_ID', 'sku_ID', 'period'],\
                customer_sku_details_df, option)
update_database('territory_wise_details', ['territory_ID', 'period'],\
                territory_wise_details_df, option)
update_database('customer_wise_details', ['customer_ID', 'period'],\
                customer_wise_details_df, option)
update_database('sku_wise_details', ['sku_ID', 'period'],\
                sku_wise_details_df, option)
end = time.clock()

print('database updating time = ', end - start)