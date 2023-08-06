from datetime import datetime
from getpass import getpass
import boto3
import pandas as pd
import os
import json

default_pond_list = ['SPW9', 'SPW11', 'SPW13']

aws_configuration = {
 'default_index_values': ['PondID'],
 'environmental_metadata_hash_keys': ['LocationID'],
 'environmental_metadata_range_keys': ['Timestamp'],
 'environmental_metadata_table': 'weather',
 'hash_keys': ['PondID'],
 'metadata_hash_keys': ['ExperimentID'],
 'metadata_table': 'experiment_meta',
 'range_keys': ['Timestamp'],
 'region_name': 'us-west-2',
 'tables': ['ysi', 'miprobe', 'weather', 'lab_samples', 'harvest', 'spectra']}


# Creates a config folder for the labprobe project
def init_folders():
    global config_location
    '''Initialize configuration and data logging folders.'''
    config_location = os.path.join(os.path.expanduser('~'), '.config', 'labprobe',)
    if not os.path.exists(config_location):
        print("Creating" + str(os.path.expanduser('~')) + "/.config/labprobe/ directory.")
        os.makedirs(config_location)
    else:
        print("Found aws configuration folder at: " + str(config_location))



def init_dynamo_config(config_dict=aws_configuration, file_name="azcati.json"):
    global aws_configuration
    global dynamodb

    aws_configuration = config_dict
    tables = aws_configuration['tables']
    default_index_values = aws_configuration['default_index_values']

    aws_configuration['aws_access_key_id'] = getpass('Enter AWS Access Key ID: ')
    aws_configuration['aws_secret_access_key'] = getpass('Enter AWS Secret Access Key: ')

    dynamodb = boto3.resource('dynamodb', 
                              region_name = aws_configuration['region_name'], 
                              aws_access_key_id = aws_configuration['aws_access_key_id'], 
                              aws_secret_access_key = aws_configuration['aws_secret_access_key'])
    with open(os.path.join(config_location, file_name), 'w') as config:
            config.write(json.dumps(aws_configuration, indent=4))
    return


def query_table(key, name, start, end, table_name, time_column):
    Key = boto3.dynamodb.conditions.Key
    table = dynamodb.Table(table_name)
    data = []
    response = table.query(KeyConditionExpression=Key(key).eq(name) & Key(time_column).between(start, end))
    for i in response[u'Items']:
        data.append(i)
    return data


def get_pond_data(ponds_list=default_pond_list, start_date="2020-01-01 00:00:00", end_date='now', datasets=aws_configuration['tables']):
    data_dict = {}
    table_list = datasets

    if end_date == 'now':
        end_date = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    if 'weather' in datasets:
        # Multi-thread this part
        table_list.remove('weather')
        data = query_table(key="LocationID", name='fieldsite', start=start_date, end=end_date, table_name='weather', time_column='Timestamp')
        data_dict['weather'] = pd.DataFrame(data)

    for dataset in table_list:
        data_dict[dataset] = pd.DataFrame()
        # Multi-thread this part.
        for pond in ponds_list:
            # Multi-thread this part.
            data = query_table(key="PondID", name=pond, start=start_date, end=end_date, table_name=dataset, time_column='Timestamp')
            data_dict[dataset] = pd.concat([data_dict[dataset], pd.DataFrame(data)], ignore_index=True)
    data_dict['ponds'] = ponds_list
    return data_dict