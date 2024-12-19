import pandas as pd
from pandas import DataFrame

from databases.mongodb.config import collection
from repositores.mongo import get_raw_data_casualties

def get_data_by_(by, returned):
    raw_data = get_raw_data_casualties()

    df = pd.DataFrame(raw_data)

    df['injured'] = df['casualties'].apply(lambda x: x['injured'])
    df['killed'] = df['casualties'].apply(lambda x: x['killed'])
    df['region'] = df['location'].apply(lambda x: x['area'])


    df_exploded = df.explode(by)

    df_exploded['lethality_score'] = df_exploded['injured'] + (df_exploded['killed'] * 2)
    df_exploded['event_count'] = df_exploded[by].count()
    analysis_sum = df_exploded.groupby(by)['lethality_score'].sum().reset_index()
    analysis_avg = df_exploded.groupby(by)['lethality_score'].mean().reset_index()

    if returned == "sum":
        return analysis_sum
    elif returned == "avg":
        return analysis_avg
    else:
        return None




def analyze_attack_types(top_n=None):

    result = get_data_by_('attack_types','sum')
    print(result)
    if top_n:
        result = result.head(top_n)

    return result

def deadliest_average_by_region(top=None):

    result = get_data_by_("region",'avg')

    print(result)

    return result
