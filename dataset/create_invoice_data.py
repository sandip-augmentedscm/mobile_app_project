import os
import simpy
import random
import numpy as np
import pandas as pd
from datetime import date, timedelta
##import matplotlib.pylab as plt

parameter_df = pd.read_csv('dataset\\parameters.csv')

def daysinperiod(date_val):
    month_num = date_val.month
    return {
        1 : 31,
        2 : 28, 
        3 : 31,
        4 : 30,
        5 : 31,
        6 : 30,
        7 : 31,
        8 : 31,
        9 : 30,
        10 : 31,
        11 : 30,
        12 : 31
    }[month_num]

def datetosubperiod(date_val):
    subperiod_start_list = {
        28 : [1, 8, 15, 22],
        29 : [1, 8, 15, 22],
        30 : [1, 8, 15, 23],
        31 : [1, 8, 16, 24]
    }
    
    num_days = daysinperiod(date_val)
    
    if date_val.day < subperiod_start_list[num_days][1]:
        return 'subperiod_1'
    elif date_val.day < subperiod_start_list[num_days][2]:
        return 'subperiod_2'
    elif date_val.day < subperiod_start_list[num_days][3]:
        return 'subperiod_3'
    else:
        return 'subperiod_4'


def create_invoice_data(**kargs):
    
    start_date = pd.Timestamp(kargs['start_date'])
    num_customers = kargs['num_customers']
    num_skus = kargs['num_skus']
    num_territories = kargs['num_territories']
    num_years = kargs['num_years']
    avg_purchase_int = kargs['avg_purchase_interval']
    customer_list, sku_list = [], []
    customer_email, customer_ph_no = [], []
    territory_salesperson_list = []
    for j in range(num_customers):
        if j < 9:
            customer_list.append('customer_0'+str(j+1))
            customer_email.append('customer_0'+str(j+1)+'@xyz.com')
        else:
            customer_list.append('customer_'+str(j+1))
            customer_email.append('customer_'+str(j+1)+'@xyz.com')
        customer_ph_no.append(random.randint(9000000000, 9999999999))
        
    customer_entity_list = zip(customer_list, customer_email, customer_ph_no)
    
    for j in range(num_skus):
        if j < 9:
            sku_list.append('sku_0'+str(j+1))
        else:
            sku_list.append('sku_'+str(j+1))
            
    for j in range(num_territories):
        if j < 9:
            territory_salesperson_list.append(['territory_0'+str(j+1), 'salesperson_0'+str(j+1)])
        else:
            territory_salesperson_list.append(['territory_0'+str(j+1), 'salesperson_0'+str(j+1)])

    avg_min = kargs['min_avg_quantity_subperiod1']
    avg_max = kargs['max_avg_quantity_subperiod1']
    avg_quantity_df1 = pd.DataFrame(list(np.random.randint(avg_min, avg_max, size=(num_customers, num_skus))),\
                                        columns=sku_list, index=customer_list)
    avg_min = kargs['min_avg_quantity_subperiod2']
    avg_max = kargs['max_avg_quantity_subperiod2']
    avg_quantity_df2 = pd.DataFrame(list(np.random.randint(avg_min, avg_max, size=(num_customers, num_skus))),\
                                        columns=sku_list, index=customer_list)
    avg_min = kargs['min_avg_quantity_subperiod3']
    avg_max = kargs['max_avg_quantity_subperiod3']
    avg_quantity_df3 = pd.DataFrame(list(np.random.randint(avg_min, avg_max, size=(num_customers, num_skus))),\
                                        columns=sku_list, index=customer_list)
    avg_min = kargs['min_avg_quantity_subperiod4']
    avg_max = kargs['max_avg_quantity_subperiod4']
    avg_quantity_df4 = pd.DataFrame(list(np.random.randint(avg_min, avg_max, size=(num_customers, num_skus))),\
                                        columns=sku_list, index=customer_list)

    result_dict = {'date' : [], 'customer_name' : [],
                   'customer_email_id' : [], 'customer_ph_no' : [],
                   'sku' : [], 'territory' : [],
                   'salesperson' : [], 'quantity' : []}
    
    class customer:
        def __init__(self, env, customer_entity):
            self.env = env
            self.name = customer_entity[0]
            self.email = customer_entity[1]
            self.ph_no = customer_entity[2]
            self.avg_purchase_interval = avg_purchase_int
            self.territory_salesperson = random.choice(territory_salesperson_list)
            env.process(self.generate_interarrival())

        def generate_interarrival(self):
            while True:
                self.sku = random.choice(sku_list)
                yield self.env.timeout(np.random.exponential(self.avg_purchase_interval))
                date_val = start_date + timedelta(round(env.now))
                result_dict['date'].append(date_val)
                result_dict['customer_name'].append(self.name)
                result_dict['customer_email_id'].append(self.email)
                result_dict['customer_ph_no'].append(self.ph_no)
                result_dict['sku'].append(self.sku)
                result_dict['territory'].append(self.territory_salesperson[0])
                result_dict['salesperson'].append(self.territory_salesperson[1])
                quantity = self.generate_quantity(self.name, self.sku, datetosubperiod(date_val))
                result_dict['quantity'].append(round(quantity))
                
        def generate_quantity(self, customer_name, sku_name, subperiod_name):
            if subperiod_name == 'subperiod_1':
                mu = avg_quantity_df1.loc[customer_name, sku_name] 
            elif subperiod_name == 'subperiod_2':
                mu = avg_quantity_df2.loc[customer_name, sku_name]
            elif subperiod_name == 'subperiod_3':
                mu = avg_quantity_df3.loc[customer_name, sku_name]
            else:
                mu = avg_quantity_df4.loc[customer_name, sku_name]

            sigma = 10
            return np.random.normal(mu, sigma)

    env = simpy.Environment()
    for customer_entity in customer_entity_list:
        customer(env, customer_entity)
    env.run(until = 365*num_years-1)

    result_df = pd.DataFrame(result_dict)
    result_df.set_index('date', inplace=True) 
    return result_df


for j in range(len(parameter_df)):
    parameter_row = parameter_df.iloc[j,:]
    
    if not os.path.exists(parameter_row['path']):
        os.mkdir(parameter_row['path'])
        
    result_df = create_invoice_data(start_date = parameter_row['start_date'],
                                    num_customers = parameter_row['num_customers'],
                                    num_skus = parameter_row['num_skus'],
                                    num_years = parameter_row['num_years'],
                                    num_territories = parameter_row['num_territories'],
                                    min_avg_quantity_subperiod1 = parameter_row['min_avg_quantity_subperiod1'],
                                    max_avg_quantity_subperiod1 = parameter_row['max_avg_quantity_subperiod1'],
                                    min_avg_quantity_subperiod2 = parameter_row['min_avg_quantity_subperiod2'],
                                    max_avg_quantity_subperiod2 = parameter_row['max_avg_quantity_subperiod2'],
                                    min_avg_quantity_subperiod3 = parameter_row['min_avg_quantity_subperiod3'],
                                    max_avg_quantity_subperiod3 = parameter_row['max_avg_quantity_subperiod3'],
                                    min_avg_quantity_subperiod4 = parameter_row['min_avg_quantity_subperiod4'],
                                    max_avg_quantity_subperiod4 = parameter_row['max_avg_quantity_subperiod4'],
                                    avg_purchase_interval = parameter_row['avg_days_between_purchase']
                                    )
    result_df.to_csv(parameter_row['path']+'\\invoice.csv')
    with open(parameter_row['path']+'\\data_logic.txt', 'w') as f:
        f.write(parameter_row['description'])