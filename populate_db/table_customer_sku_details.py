import pandas as pd
from numpy import nan
import warnings
warnings.simplefilter(action='ignore')

from table_territory_master import create_territory_master
from table_customer_master import create_customer_master
from table_sku_master import create_sku_master

def create_customer_sku_details(input_df, customer_master_df, sku_master_df):
    
    cust_sku_master_df = input_df[['Customer Name', 'Item Name', 'Month Name', \
                             'Quantity in KG/LTR', 'Amount To Customer']]
    cust_sku_master_df = cust_sku_master_df.groupby(['Month Name', 'Customer Name', 'Item Name'],as_index=False)\
    ['Quantity in KG/LTR', 'Amount To Customer'].sum()
    def monthToPeriod(month):
        return {
                'JAN' : 201801,
                'FEB' : 201802,
                'MAR' : 201803,
                'APR' : 201804,
                'MAY' : 201805,
                'JUN' : 201806,
                'JUL' : 201807,
                'AUG' : 201708,
                'SEP' : 201709, 
                'OCT' : 201710,
                'NOV' : 201711,
                'DEC' : 201712
        }[month]

    cust_sku_master_df['period'] = cust_sku_master_df['Month Name'].apply(lambda x: monthToPeriod(x))
    cust_sku_master_df.rename(columns={'Customer Name':'customer_name'}, inplace=True)
    cust_sku_master_df.rename(columns={'Item Name':'sku_name'}, inplace=True)
    cust_sku_master_df.rename(columns={'Quantity in KG/LTR':'actual_volm'}, inplace=True)
    cust_sku_master_df.rename(columns={'Amount To Customer':'actual_val'}, inplace=True)

    cust_sku_master_df['sku_name'] = cust_sku_master_df['sku_name'].str.upper()
    
    def cust_name_to_id(name):
        return customer_master_df[customer_master_df['customer_name']==name]['customer_ID'].values[0]

    def sku_name_to_id(name):
        return sku_master_df[sku_master_df['sku_name']==name]['sku_ID'].values[0]

    cust_sku_master_df['customer_ID'] = cust_sku_master_df['customer_name'].apply(lambda x: cust_name_to_id(x))
    cust_sku_master_df['sku_ID'] = cust_sku_master_df['sku_name'].apply(lambda x: sku_name_to_id(x))

    cust_sku_master_df.drop(columns=['customer_name', 'sku_name', 'Month Name'], inplace=True) 
    cust_sku_master_df[['target_val', 'target_volm']]= pd.DataFrame([[nan,nan]])

    cols = ['customer_ID', 'sku_ID', 'period','target_val', 'target_volm',\
            'actual_val', 'actual_volm']
    cust_sku_master_df = cust_sku_master_df[cols]
    cust_sku_master_df.sort_values(by=['period', 'customer_ID', 'sku_ID'], inplace=True)
    cust_sku_master_df.reset_index(drop=True, inplace=True)
    
    return cust_sku_master_df

if __name__ == '__main__':
    
    input_df = pd.read_excel('csv_files\\Bellary SD Sales.xlsx')

    # Date today
    current_date = pd.Timestamp('2018-02-15')

    # Filter the data from AUG 1, 2017 to current_date
    input_df = input_df[input_df['Bill Date'] >= pd.Timestamp('2017-08-01')]
    input_df = input_df[input_df['Bill Date'] <= current_date]
    
    territory_master_df = create_territory_master(input_df)
    customer_master_df = create_customer_master(input_df, territory_master_df)
    sku_master_df = create_sku_master(input_df)
    customer_sku_details_df = create_customer_sku_details(input_df, customer_master_df, sku_master_df)
    
    #save table in csv
    customer_sku_details_df.fillna('NA').to_csv('csv_files\\customer_sku_details.csv', index=False)