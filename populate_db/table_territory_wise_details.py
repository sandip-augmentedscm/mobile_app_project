import pandas as pd
import numpy as np
from numpy import nan
from statistics import mean, stdev

import warnings
warnings.simplefilter(action='ignore')

from table_territory_master import create_territory_master
from calculate_skewness import *
from calculate_skewed_runrate import *

def create_territory_wise_details(input_df, territory_df):
    input_df.sort_values(by='Bill Date',inplace=True)
    today = input_df['Bill Date'].max()
    input_df['period'] = input_df['Bill Date'].apply(lambda x: DatetoPeriod(x))
    current_period = input_df.loc[(input_df['Bill Date'] == today), 'period'].values[0]

    
    territory_details_df = input_df[['Territory Sales Manger', 'Month Name', 'period',\
                                'Quantity in KG/LTR', 'Amount To Customer']]
    territory_details_df['Territory Sales Manger'] = territory_details_df['Territory Sales Manger'].str.upper()
    territory_details_df = territory_details_df.groupby(['Territory Sales Manger', 'period', 'Month Name'],\
                                            as_index=False)['Quantity in KG/LTR', 'Amount To Customer'].sum()

    territory_details_df.rename(columns={'Territory Sales Manger':'territory_name'}, inplace=True)
    territory_details_df.rename(columns={'Quantity in KG/LTR':'actual_volm'}, inplace=True)
    territory_details_df.rename(columns={'Amount To Customer':'actual_val'}, inplace=True)
    territory_details_df[['target_val', 'target_volm', 'required_rr_val','required_rr_volm', \
                        'skewed_req_rr_val', 'skewed_req_rr_volm']] = \
                        pd.DataFrame([[nan, nan, nan, nan, nan, nan]])

    territory_details_df['actual_rr_val'] = territory_details_df\
    .apply(lambda x: x.actual_val/DaysinPeriod(x.period), axis=1)

    territory_details_df['actual_rr_volm'] = territory_details_df\
    .apply(lambda x: x.actual_volm/DaysinPeriod(x.period), axis=1)

    territory_details_df[['skewed_actual_rr_val', 'skewed_actual_rr_volm']] = pd.DataFrame([[nan, nan]])

    territory_list = territory_df['territory_name'].drop_duplicates(keep = 'first').tolist()

    territory_wise_skew_result = calculate_territory_wise_skew(input_df, territory_df)
    for territory in territory_list:
        sales_val = sum(territory_wise_skew_result['current_val'][territory])
        sales_val_rate = skewed_actual_runrate(sales_val, territory_wise_skew_result['val'][territory],\
                                               current_period, today)
        
        sales_volm = sum(territory_wise_skew_result['current_volm'][territory])
        sales_volm_rate = skewed_actual_runrate(sales_volm, territory_wise_skew_result['volm'][territory],\
                                               current_period, today)

        territory_details_df.loc[(territory_details_df['territory_name']==territory) &\
                            (territory_details_df['period']== current_period), \
                                'skewed_actual_rr_val'] = sales_val_rate
        territory_details_df.loc[(territory_details_df['territory_name']==territory) &\
                            (territory_details_df['period']== current_period), \
                                'skewed_actual_rr_volm'] = sales_volm_rate

    def territory_name_to_id(name):
        return territory_df[territory_df['territory_name']==name]['territory_ID'].values[0]

    territory_details_df['territory_ID'] = territory_details_df['territory_name']\
                                        .apply(lambda x: territory_name_to_id(x))

    territory_details_df.drop(columns=['territory_name'], inplace=True)

    cols = ['territory_ID', 'period', 'target_val', 'target_volm', 'actual_val', 'actual_volm', \
            'actual_rr_val', 'actual_rr_volm', 'skewed_actual_rr_val', 'skewed_actual_rr_volm',\
            'required_rr_val','required_rr_volm', 'skewed_req_rr_val', 'skewed_req_rr_volm']
    territory_details_df = territory_details_df[cols]
    territory_details_df.sort_values(by=['period', 'territory_ID'], inplace=True)
    territory_details_df.reset_index(drop=True, inplace=True)

    return territory_details_df

    
if __name__ == '__main__':
    
    input_df = pd.read_excel('csv_files\\Bellary SD Sales.xlsx')

    # Date today
    current_date = pd.Timestamp('2018-02-15')

    # Filter the data from AUG 1, 2017 to current_date
    input_df = input_df[input_df['Bill Date'] >= pd.Timestamp('2017-08-01')]
    input_df = input_df[input_df['Bill Date'] <= current_date]
        
    territory_master_df = create_territory_master(input_df)
    territory_wise_details_df = create_territory_wise_details(input_df, territory_master_df)
    
    # Replacing the 'inf' values with 'nan' values
    territory_wise_details_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # save table in csv
    territory_wise_details_df.fillna('NA').to_csv('csv_files\\territory_wise_details.csv', index=False)