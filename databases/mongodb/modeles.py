import math
import uuid
from datetime import datetime

import bson
import pandas as pd
from networkx.algorithms.operators.binary import union
from pandas import DataFrame

from databases.mongodb.config import collection





def insert_data_to_mongodb(data_list):
    queries = [
        {
            "event_id": data['eventid'],
            "date": datetime(data['iyear'], data['imonth'] if 1 <= data['imonth'] <= 12 else 1,1),
            "location": {
                "city": data['city'],
                "latitude": 0 if (pd.isna(data['latitude']) or math.isnan(data['latitude'])) else data['latitude'],
                "longitude": 0 if (pd.isna(data['longitude']) or math.isnan(data['longitude'])) else data['longitude'],
                "area": data['region_txt'],
                "country": data['country_txt']
            },
            "casualties": {
                "injured": data.get('nwound',0),
                "killed": data.get('nkill',0)
            },
            "terrorists_attack_group": list(filter(None, [data['gname'], data.get('gname1'), data.get('gname2')])),
            "attack_types": list(filter(None, [data['attacktype1_txt'], data.get('attacktype2_txt'), data.get('attacktype3_txt')])),
            "target_types": list(filter(None, [data['targtype1_txt'], data.get('targtype2_txt')])),
            "description":data['addnotes'],
            "sum_terroristic":data['nperps']

        }
        for data in data_list
    ]
    if queries:
        result = collection.insert_many(queries)
        print(f"inserted 50 rows")
        return result.inserted_ids
    else:
        return []

def create_index(collection):
    """
    Create indexes for the imported columns to improve query performance.
    """
    collection.create_index([('date', 1)])
    collection.create_index([('location.country', 1)])
    collection.create_index([('location.region', 1)])
    collection.create_index([('location.city', 1)])
    collection.create_index([('attack.attack_code', 1)])
    collection.create_index([('target.target_code', 1)])
    collection.create_index([('group_name', 1)])
    collection.create_index([('kill', 1)])
    collection.create_index([('injured', 1)])


def is_country(country_name):
    raw_data = list(collection.find(
        {'location.country': country_name},
        {'location.latitude': 1, 'location.longitude': 1,'location.area':1, '_id': 0}  # Fetch only necessary fields
    ))
    if raw_data:
        df = pd.DataFrame(raw_data)
        df['latitude'] = df['location'].apply(
            lambda x: float(x['latitude']) if x.get('latitude') is not None and not pd.isna(x['latitude']) else None)
        df['longitude'] = df['location'].apply(
            lambda x: float(x['longitude']) if x.get('longitude') is not None and not pd.isna(x['longitude']) else None)
        df['area'] = df['location'].apply(
            lambda x: str(x['area']) if x.get('longitude') is not None and not pd.isna(x['area']) else None)

        df = df.dropna(subset=['latitude', 'longitude'])

        if not df.empty:
            return df['latitude'].iloc[0], df['longitude'].iloc[0],df['area'].iloc[0]

    return None, None


def marge_new_data(data_list):
    queries = []
    for data in data_list:
        lat_lon = is_country(data['Country'])
        if lat_lon[0] is not None and lat_lon[1] is not None and lat_lon[2]:  # Ensure latitude and longitude are valid
            queries.append({
                "event_id": uuid.uuid4().int % (2 ** 63),
                "date": data['Date'],
                "location": {
                    "city": data.get('City'),
                    "country": data['Country'],
                    "latitude": lat_lon[0],
                    "longitude": lat_lon[1],
                    "area":lat_lon[2],
                },
                "casualties": {
                    "injured": data.get('Injuries ', 0),
                    "killed": data.get('Fatalities ', 0)
                },
                "terrorists_attack_group": data.get('Perpetrator'),
                "attack_types": data.get('Weapon'),
                "description": data.get('Description'),
            })
    if queries:
        result = collection.insert_many(queries)
        print(f"Inserted {len(queries)} rows")
        return result.inserted_ids
    else:
        print("No valid data to insert.")
        return []