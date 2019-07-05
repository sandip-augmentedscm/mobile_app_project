import pandas as pd
import warnings
warnings.simplefilter(action='ignore')

def create_territory_master(input_df):
    
    territory_sr1 = input_df['Territory Sales Manger']
    territory_sr1 = territory_sr1.str.upper()
    territory_sr1.drop_duplicates(keep = 'first', inplace = True)
    territory_sr1 = territory_sr1.reset_index(drop = True)
    territory_sr2 = pd.Series(range(1, len(territory_sr1)+1))
    territory_df = pd.concat([territory_sr2, territory_sr1], axis=1)
    territory_df.columns = ['territory_ID','territory_name']
    
    territory_df['salesperson_ID'] = list(range(1, len(territory_df)+1))
    
    return territory_df
    
    
if __name__ == '__main__':
    
    input_df = pd.read_excel('csv_files\\Bellary SD Sales.xlsx')

    # Date today
    current_date = pd.Timestamp('2018-02-15')

    # Filter the data from AUG 1, 2017 to current_date
    input_df = input_df[input_df['Bill Date'] >= pd.Timestamp('2017-08-01')]
    input_df = input_df[input_df['Bill Date'] <= current_date]
    
    territory_master_df = create_territory_master(input_df)
    
    #save table in csv
    territory_master_df.fillna('NA').to_csv('csv_files\\territory_master.csv', index=False)