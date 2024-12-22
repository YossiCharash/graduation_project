import pandas as pd
from more_itertools import chunked
from pandas.core.interchange.dataframe_protocol import DataFrame

from databases.mongodb.modeles import insert_data_to_mongodb, marge_new_data
from databases.neo4j.config_neo4j import neo4j_driver
from databases.neo4j.models_neo4j import create_db_in_neo4j


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



def insert_new_csv_(path):
    df = pd.read_csv(path, encoding='latin1')
    df = df.where(pd.notnull(df), None)
    rows = df.to_dict('records')
    for batch in chunked(rows, 100):
        marge_new_data(batch)




insert_new_csv_('../data/RAND_Database_of_Worldwide_Terrorism_Incidents.csv')