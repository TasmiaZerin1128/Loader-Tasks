import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
import sys


def check_if_data_available_for(start_date: datetime.date, end_date: datetime.date):
    while start_date <= end_date:
        if start_date < datetime.date(year=2016, month=1, day=1):
            raise ValueError(f"{start_date} is prior to the data publish start date of January 1st, 2016.")
        if start_date > datetime.datetime.now().date() + datetime.timedelta(days=1):
            raise ValueError(f"{start_date} is in the future. Query date is supported till today's date.")
        start_date += datetime.timedelta(days=1)


def fetch_data(start_date: datetime.date, end_date: datetime.date):
    start_date = start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    end_date = end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    data_url = f'https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type?format=json&from={start_date}&to={end_date}'
    
    data = requests.get(data_url)
    return data.json()


def save_data_to_csv(data):
    df = []
    psrTypes = ["Fossil Hard coal", "Fossil Oil", "Hydro Pumped Storage", "Biomass", "Hydro Run-of-river and poundage"]

    for each_data_block in data['data']:
        single_df = pd.json_normalize(each_data_block['data'])
        single_df['startTime'] = each_data_block['startTime']
        single_df['name'] = 'bmrs _report'
        single_df = single_df[['startTime', 'quantity', 'psrType', 'name']]
        single_df = single_df[single_df['psrType'].isin(psrTypes)]

        single_df = single_df.rename(columns={
            'quantity': 'value',
            'psrType': 'keys',
        })
        
        df.append(single_df)
    
    df = pd.concat(df)
    
    csv_file = f'first_loader_{datetime.datetime.now()}.csv'
    df.to_csv(csv_file, index=False)


def get_results(start_date: datetime.date, end_date: datetime.date):
    check_if_data_available_for(start_date, end_date)
    print(f'Start time {start_date} and end time {end_date} are valid. Fetching data.')
    data = fetch_data(start_date, end_date)
    save_data_to_csv(data)


# Get the data for the last n days
get_results(datetime.datetime.now().date() - datetime.timedelta(days=int(sys.argv[1])), datetime.datetime.now().date())