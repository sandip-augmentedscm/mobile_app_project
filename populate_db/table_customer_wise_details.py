import pandas as pd
import numpy as np
from numpy import nan
from statistics import mean, stdev

import warnings
warnings.simplefilter(action='ignore')

from table_territory_master import create_territory_master
from table_customer_master import create_customer_master
from calculate_skewness import *
from calculate_skewed_runrate import *

def create_customer_wise_details(input_df, customer_df):
    input_df.sort_values(by='Bill Date',inplace=True)
    today = input_df['Bill Date'].max()
    input_df['period'] = input_df['Bill Date'].apply(lambda x: DatetoPeriod(x))
    current_period = input_df.loc[(input_df['Bill Date'] == today), 'period'].values[0]

    
    customer_details_df = input_df[['Customer Name', 'Month Name', 'period',\
                                'Quantity in KG/LTR', 'Amount To Customer']]
    customer_details_df['Customer Name'] = customer_details_df['Customer Name'].str.upper()
    customer_details_df = customer_details_df.groupby(['Customer Name', 'period', 'Month Name'],\
                                            as_index=False)['Quantity in KG/LTR', 'Amount To Customer'].sum()

    customer_details_df.rename(columns={'Customer Name':'customer_name'}, inplace=True)
    customer_details_df.rename(columns={'Quantity in KG/LTR':'actual_volm'}, inplace=True)
    customer_details_df.rename(columns={'Amount To Customer':'actual_val'}, inplace=True)
    customer_details_df[['target_val', 'target_volm', 'required_rr_val','required_rr_volm', \
                        'skewed_req_rr_val', 'skewed_req_rr_volm']] = \
                        pd.DataFrame([[nan, nan, nan, nan, nan, nan]])

    customer_details_df['actual_rr_val'] = customer_details_df\
    .apply(lambda x: x.actual_val/DaysinPeriod(x.period), axis=1)

    customer_details_df['actual_rr_volm'] = customer_details_df\
    .apply(lambda x: x.actual_volm/DaysinPeriod(x.period), axis=1)

    customer_details_df[['skewed_actual_rr_val', 'skewed_actual_rr_volm']] = pd.DataFrame([[nan, nan]])

    customer_list = customer_df['customer_name'].drop_duplicates(keep = 'first').tolist()
    # customer_list = customer_details_df['customer_name'].drop_duplicates(keep = 'first').tolist()

    customer_wise_skew_result = calculate_customer_wise_skew(input_df, customer_df)
    for customer in customer_list:
        sales_val = sum(customer_wise_skew_result['current_val'][customer])
        sales_val_rate = skewed_actual_runrate(sales_val, customer_wise_skew_result['val'][customer],\
                                               current_period, today)

        sales_volm = sum(customer_wise_skew_result['current_volm'][customer])
        sales_volm_rate = skewed_actual_runrate(sales_volm, customer_wise_skew_result['volm'][customer],\
                                               current_period, today)

        customer_details_df.loc[(customer_details_df['customer_name']==customer) &\
                            (customer_details_df['period']== current_period), \
                                'skewed_actual_rr_val'] = sales_val_rate
        customer_details_df.loc[(customer_details_df['customer_name']==customer) &\
                            (customer_details_df['period']== current_period), \
                                'skewed_actual_rr_volm'] = sales_volm_rate

    def customer_name_to_id(name):
        return customer_df[customer_df['customer_name']==name]['customer_ID'].values[0]

    customer_details_df['customer_ID'] = customer_details_df['customer_name']\
                                        .apply(lambda x: customer_name_to_id(x))

    customer_details_df.drop(columns=['customer_name'], inplace=True)

    cols = ['customer_ID', 'period', 'target_val', 'target_volm', 'actual_val', 'actual_volm', \
            'actual_rr_val', 'actual_rr_volm', 'skewed_actual_rr_val', 'skewed_actual_rr_volm',\
            'required_rr_val','required_rr_volm', 'skewed_req_rr_val', 'skewed_req_rr_volm']
    customer_details_df = customer_details_df[cols]
    customer_details_df.sort_values(by=['period', 'customer_ID'], inplace=True)
    customer_details_df.reset_index(drop=True, inplace=True)

    return customer_details_df

if __name__ == '__main__':
    
    input_df = pd.read_excel('csv_files\\Bellary SD Sales.xlsx')

    # Date today
    current_date = pd.Timestamp('2018-02-15')

    # Filter the data from AUG 1, 2017 to current_date
    input_df = input_df[input_df['Bill Date'] >= pd.Timestamp('2017-08-01')]
    input_df = input_df[input_df['Bill Date'] <= current_date]
        
    territory_master_df = create_territory_master(input_df)
    customer_master_df = create_customer_master(input_df, territory_master_df)
    customer_wise_details_df = create_customer_wise_details(input_df, customer_master_df)
    
    # Replacing the 'inf' values with 'nan' values
    customer_wise_details_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # save table in csv
    customer_wise_details_df.fillna('NA').to_csv('csv_files\\customer_wise_details.csv', index=False)