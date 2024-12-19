import math
from datetime import datetime
import pandas as pd






def insert_to_neo4j(tx, data):
    if pd.isna(data['region']):
        data['region'] = "Unknown"
    if pd.isna(data['country']):
        data['country'] = "Unknown"

    # Filter out None/null values from arrays and convert to strings
    attack = [str(x) for x in data['attack'] if x is not None]
    target = [str(x) for x in data['target'] if x is not None]

    with tx.session() as session:
        query = """
        MERGE (g:Group {name: $group})
        MERGE (r:Region {name: $region})
        MERGE (c:Country {name: $country})
        MERGE (l:City {name: $city, longitude: $longitude, latitude: $latitude})
        MERGE (c)-[:PART_OF]->(r)
        MERGE (l)-[:IN_COUNTRY]->(c)
        MERGE (g)-[:ATTACKED {
            event_id: $event_id,
            date: $date, 
            target: $target, 
            attack: $attack
        }]->(l)
        """

        session.run(query, {
            'group': data['group'],
            'attack': attack,  # Using filtered array
            'region': data['region'],
            'country': data['country'],
            'city': data['city'],
            'target': target,  # Using filtered array
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'event_id': data['event_id'],
            'date': data['date']
        })
        print("One data inserted")

def create_db_in_neo4j(tx, data):
    longitude = 0 if (pd.isna(data['longitude']) or math.isnan(data['longitude'])) else data['longitude']
    latitude = 0 if (pd.isna(data['latitude']) or math.isnan(data['latitude'])) else data['latitude']

    gname = [data['gname'], data.get('gname1'), data.get('gname2')]
    attack_type = [x for x in [data['attacktype1_txt'], data.get('attacktype2_txt'), data.get('attacktype3_txt')] if x is not None and pd.notna(x)]
    target_type = [x for x in [data['targtype1_txt'], data.get('targtype2_txt')] if x is not None and pd.notna(x)]

    for i in gname:
        if i is None or pd.isna(i):
            continue
        else:
            insert_to_neo4j(tx, {
                'event_id': data['eventid'],
                'group': i,
                'attack': attack_type,
                'region': data['region_txt'],
                'country': data['country_txt'],
                'city': data['city'],
                'target': target_type,
                'latitude': latitude,
                'longitude': longitude,
                'date': datetime(data['iyear'], data['imonth'] if 1 <= data['imonth'] <= 12 else 1, 1)
            })
    print("The neo4j database has been created")