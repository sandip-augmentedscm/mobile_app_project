import pandas as pd
from numpy import nan
import warnings
warnings.simplefilter(action='ignore')

from table_territory_master import create_territory_master

def create_salesperson_master(territory_master_df):
    
    salesperson_df = territory_master_df.copy()
    salesperson_df['salesperson_name'] = ['salesperson_'+str(x) for x in \
                                        salesperson_df['salesperson_ID']] 
    salesperson_df['mobile_number'] = pd.DataFrame([[nan]])

    salesperson_df.drop(columns=['territory_ID', 'territory_name'], inplace=True) 
    
    return salesperson_df
    
    
if __name__ == '__main__':
    
    input_df = pd.read_excel('csv_files\\Bellary SD Sales.xlsx')

    # Filter the data from AUG 1, 2017 to FEB 15, 2018
    input_df = input_df[input_df['Bill Date'] >= pd.Timestamp('2017-08-01')]
    input_df = input_df[input_df['Bill Date'] <= pd.Timestamp('2018-02-15')]
    
    territory_master_df = create_territory_master(input_df)
    salesperson_master_df = create_salesperson_master(territory_master_df)
    
    #save table in csv
    salesperson_master_df.fillna('NA').to_csv('csv_files\\salesperson_master.csv', index=False)