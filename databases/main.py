import pandas as pd
from more_itertools import chunked

from databases.mongodb.config import collection
from databases.mongodb.modeles import insert_data_to_mongodb, marge_new_data, create_index



def read_csv_(path):

    df = pd.read_csv(path, encoding='latin1',usecols=[
        'eventid','iyear','imonth', 'iday',
        'country_txt','region_txt','city',
        'longitude','latitude','nkill','gname' , 'gname2', 'gname3'
        ,'nperps','nwound','attacktype1',
        'attacktype1_txt','attacktype2','attacktype2_txt','attacktype3',
         'attacktype3_txt','targtype1','targtype1_txt','targtype2'	,'targtype2_txt',
        'propcomment','addnotes'])
    df = df.where(pd.notnull(df), None)

    rows = df.to_dict('records')

    for batch in chunked(rows, 100):
        insert_data_to_mongodb(batch)
        create_index(collection)




def insert_new_csv_(path):
    df = pd.read_csv(path, encoding='latin1')
    df = df.where(pd.notnull(df), None)
    rows = df.to_dict('records')
    for batch in chunked(rows, 100):
        marge_new_data(batch)




