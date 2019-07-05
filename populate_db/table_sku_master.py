import pandas as pd
from numpy import nan
import warnings
warnings.simplefilter(action='ignore')

def create_sku_master(input_df):
    
    sku_df = input_df[['Item Name', 'Item ID', 'Pack MRP']]
    sku_df.rename(columns={'Item Name':'sku_name'}, inplace=True)
    sku_df.rename(columns={'Item ID':'sku_code'}, inplace=True)
    sku_df.rename(columns={'Pack MRP':'customer_price'}, inplace=True)
    
    sku_df['sku_name'] = sku_df['sku_name'].str.upper()
    
    sku_df.drop_duplicates(keep = 'first', inplace = True)
    
    def sku_to_product(name):
        return input_df.loc[input_df['Item Name'].str.upper() == name, 'Product Group'].values[0]
    
    sku_df['product_name'] = sku_df['sku_name'].apply(lambda x: sku_to_product(x))

    sku_df[['description','Launch Date','list_price','conv_factor_val_to_volm']]=\
    pd.DataFrame([[nan, nan, nan, nan]])
    
    sku_df['sku_ID'] = list(range(1, len(sku_df)+1))
    cols = ['sku_ID','sku_name', 'sku_code', 'product_name', 'description', 'Launch Date',\
            'list_price', 'customer_price','conv_factor_val_to_volm']
    sku_df = sku_df[cols]
    sku_df.reset_index(drop=True, inplace=True)
    
    return sku_df
    
    
if __name__ == '__main__':
    
    input_df = pd.read_excel('csv_files\\Bellary SD Sales.xlsx')

    # Date today
    current_date = pd.Timestamp('2018-02-15')

    # Filter the data from AUG 1, 2017 to current_date
    input_df = input_df[input_df['Bill Date'] >= pd.Timestamp('2017-08-01')]
    input_df = input_df[input_df['Bill Date'] <= current_date]
    
    sku_master_df = create_sku_master(input_df)
    
    #save table in csv
    sku_master_df.fillna('NA').to_csv('csv_files\\sku_master.csv', index=False)