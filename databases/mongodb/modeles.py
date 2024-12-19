import math
from datetime import datetime
import pandas as pd

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

