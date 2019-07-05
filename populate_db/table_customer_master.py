import pandas as pd
from numpy import nan
import warnings
warnings.simplefilter(action='ignore')

from table_territory_master import create_territory_master

def create_customer_master(input_df, territory_master_df):
    
    customer_df = input_df[['Customer Name',' Customer Code','Ship to City','Territory Sales Manger']]
    customer_df.rename(columns={'Customer Name':'customer_name'}, inplace=True)
    customer_df.rename(columns={' Customer Code':'customer_code'}, inplace=True)
    customer_df.rename(columns={'Territory Sales Manger':'territory_name'}, inplace=True)
    customer_df.rename(columns={'Ship to City':'City'}, inplace=True)
    
    customer_df['City'] = customer_df['City'].str.upper()
    customer_df['territory_name'] = customer_df['territory_name'].str.upper()
    
    customer_df.drop_duplicates(keep = 'first', inplace = True)
    
    customer_df[['Address','PIN_code','mobile_number']]= pd.DataFrame([[nan,nan,nan]])

    def territory_name_to_id(name):
        return territory_master_df.loc[territory_master_df['territory_name']==name,'territory_ID'].values[0]

    customer_df['territory_ID'] = customer_df['territory_name'].apply(lambda x: territory_name_to_id(x))
                                        
                                          
    customer_df.drop(columns=['territory_name'], inplace=True) 
    customer_df['customer_ID'] = list(range(1, len(customer_df)+1))
    
    cols = ['customer_ID', 'territory_ID','customer_name', 'customer_code',\
            'Address','City','PIN_code','mobile_number']
    customer_df = customer_df[cols]
    customer_df.reset_index(drop=True, inplace=True)
    
    return customer_df
    
    
if __name__ == '__main__':
    
    input_df = pd.read_excel('csv_files\\Bellary SD Sales.xlsx')

    # Date today
    current_date = pd.Timestamp('2018-02-15')

    # Filter the data from AUG 1, 2017 to current_date
    input_df = input_df[input_df['Bill Date'] >= pd.Timestamp('2017-08-01')]
    input_df = input_df[input_df['Bill Date'] <= current_date]
    
    territory_master_df = create_territory_master(input_df)
    customer_master_df = create_customer_master(input_df, territory_master_df)
    
    #save table in csv
    customer_master_df.fillna('NA').to_csv('csv_files\\customer_master.csv', index=False)
