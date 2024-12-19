from datetime import datetime

from databases.mongodb.config import collection, db


def insert_data_to_mongodb(data_list):
    queries = [
        {
            "event_id": data['eventid'],
            "date": datetime(data['iyear'], data['imonth'] if 1 <= data['imonth'] <= 12 else 1,1),
            "location": {
                "city": data['city'],
                "latitude": data['latitude'],
                "longitude": data['longitude'],
                "area": data['region_txt'],
                "country": data['country_txt']
            },
            "casualties": {
                "injured": data.get('nwound',0),
                "killed": data.get('nkill',0)
            },
            "terrorists_attack_group": list(filter(None, [data['gname'], data.get('gname1'), data.get('gname2')])),
            "attack_types": list(filter(None, [data['attacktype1_txt'], data.get('attacktype2_txt'), data.get('attacktype3_txt')])),
            "target_types": list(filter(None, [data['targtype1_txt'], data.get('targtype2_txt')]))
        }
        for data in data_list
    ]
    if queries:
        result = collection.insert_many(queries)
        print(f"inserted 50 rows")
        return result.inserted_ids
    else:
        return []

