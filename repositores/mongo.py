
from databases.mongodb.config import collection


# Retrieving the data from Mongo
def get_raw_data_casualties():
    raw_data = list(collection.find({}, {
        'date':1,
        'target_types':1,
        'terrorists_attack_group':1,
        'attack_types': 1,
        'casualties': 1,
        'location': 1,
        'event_id': 1
    }))
    return raw_data

