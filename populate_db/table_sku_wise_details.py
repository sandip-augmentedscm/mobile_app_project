import pandas as pd
import numpy as np
from numpy import nan
from statistics import mean, stdev

import warnings
warnings.simplefilter(action='ignore')

from table_sku_master import create_sku_master
from calculate_skewness import *
from calculate_skewed_runrate import *

def create_sku_wise_details(input_df, sku_df):
    input_df.sort_values(by='Bill Date',inplace=True)
    today = input_df['Bill Date'].max()
    input_df['period'] = input_df['Bill Date'].apply(lambda x: DatetoPeriod(x))
    current_period = input_df.loc[(input_df['Bill Date'] == today), 'period'].values[0]

    sku_details_df = input_df[['Item Name', 'Month Name', 'period',\
                                'Quantity in KG/LTR', 'Amount To Customer']]
    sku_details_df['Item Name'] = sku_details_df['Item Name'].str.upper()
    sku_details_df = sku_details_df.groupby(['Item Name', 'period', 'Month Name'],\
                                            as_index=False)['Quantity in KG/LTR', 'Amount To Customer'].sum()

    sku_details_df.rename(columns={'Item Name':'sku_name'}, inplace=True)
    sku_details_df.rename(columns={'Quantity in KG/LTR':'actual_volm'}, inplace=True)
    sku_details_df.rename(columns={'Amount To Customer':'actual_val'}, inplace=True)
    sku_details_df[['target_val', 'target_volm', 'required_rr_val','required_rr_volm', \
                        'skewed_req_rr_val', 'skewed_req_rr_volm']] = \
                        pd.DataFrame([[nan, nan, nan, nan, nan, nan]])

    sku_details_df['actual_rr_val'] = sku_details_df\
    .apply(lambda x: x.actual_val/DaysinPeriod(x.period), axis=1)

    sku_details_df['actual_rr_volm'] = sku_details_df\
    .apply(lambda x: x.actual_volm/DaysinPeriod(x.period), axis=1)

    sku_details_df[['skewed_actual_rr_val', 'skewed_actual_rr_volm']] = pd.DataFrame([[nan, nan]])

    sku_list = sku_df['sku_name'].drop_duplicates(keep = 'first').tolist()


    sku_wise_skew_result = calculate_sku_wise_skew(input_df, sku_df)
    
    for sku in sku_list:
        sales_val = sum(sku_wise_skew_result['current_val'][sku])
        sales_val_rate = skewed_actual_runrate(sales_val, sku_wise_skew_result['val'][sku],\
                                               current_period, today)

        sales_volm = sum(sku_wise_skew_result['current_volm'][sku])
        sales_volm_rate = skewed_actual_runrate(sales_volm, sku_wise_skew_result['volm'][sku],\
                                               current_period, today)

        sku_details_df.loc[(sku_details_df['sku_name']==sku) &\
                            (sku_details_df['period']== current_period), \
                                'skewed_actual_rr_val'] = sales_val_rate
        sku_details_df.loc[(sku_details_df['sku_name']==sku) &\
                            (sku_details_df['period']== current_period), \
                                'skewed_actual_rr_volm'] = sales_volm_rate

    def sku_name_to_id(name):
        return sku_df[sku_df['sku_name']==name]['sku_ID'].values[0]

    sku_details_df['sku_ID'] = sku_details_df['sku_name']\
                                        .apply(lambda x: sku_name_to_id(x))

    sku_details_df.drop(columns=['sku_name'], inplace=True)

    cols = ['sku_ID', 'period', 'target_val', 'target_volm', 'actual_val', 'actual_volm', \
            'actual_rr_val', 'actual_rr_volm', 'skewed_actual_rr_val', 'skewed_actual_rr_volm',\
            'required_rr_val','required_rr_volm', 'skewed_req_rr_val', 'skewed_req_rr_volm']
    sku_details_df = sku_details_df[cols]
    sku_details_df.sort_values(by=['period', 'sku_ID'], inplace=True)
    sku_details_df.reset_index(drop=True, inplace=True)

    return sku_details_df

if __name__ == '__main__':
    
    input_df = pd.read_excel('csv_files\\Bellary SD Sales.xlsx')

    # Date today
    current_date = pd.Timestamp('2018-05-18')

    # Filter the data from AUG 1, 2017 to current_date
    input_df = input_df[input_df['Bill Date'] >= pd.Timestamp('2017-08-01')]
    input_df = input_df[input_df['Bill Date'] <= current_date]
        
    sku_master_df = create_sku_master(input_df)
    sku_wise_details_df = create_sku_wise_details(input_df, sku_master_df)
    
    # Replacing the 'inf' values with 'nan' values
    sku_wise_details_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # save table in csv
    sku_wise_details_df.fillna('NA').to_csv('csv_files\\sku_wise_details.csv', index=False)