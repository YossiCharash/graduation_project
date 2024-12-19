import pandas as pd
from more_itertools import chunked

from databases.mongodb.config import collection
from databases.mongodb.modeles import insert_data_to_mongodb

#
# def read_csv(path):
#
#     df = pd.read_csv(path, encoding='latin1',usecols=[
#         'eventid','iyear','imonth', 'iday','country',
#         'country_txt','region','region_txt','city',
#         'longitude','latitude','nkill','gname' , 'gname2', 'gname3'
#         ,'motive','nperps','nwound','attacktype1',
#         'attacktype1_txt','attacktype2','attacktype2_txt','attacktype3',
#          'attacktype3_txt','targtype1','targtype1_txt','targtype2'	,'targtype2_txt',
#         'propcomment','addnotes'])
#     df = df.where(pd.notnull(df), None)
#
#     rows = df.to_dict('records')
#
#     for batch in chunked(rows, 100):
#         insert_data_to_mongodb(batch)



# Retrieving the data from Mongo
def get_raw_data_casualties():
    raw_data = list(collection.find({}, {
        'attack_types': 1,
        'casualties': 1,
        'location': 1,
        'event_id': 1
    }))
    return raw_data

