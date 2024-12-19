import pandas as pd
from pandas import DataFrame

from databases.mongodb.config import collection
from repositores.mongo import get_raw_data_casualties, get_raw_data_location

def get_data_by_(by):
    raw_data = get_raw_data_casualties()

    df = pd.DataFrame(raw_data)

    df['injured'] = df['casualties'].apply(lambda x: x['injured'])
    df['killed'] = df['casualties'].apply(lambda x: x['killed'])
    df['region'] = df['location'].apply(lambda x: x['area'])


    df_exploded = df.explode(by)

    analysis = df_exploded.groupby(by).agg({
        'injured': 'sum',
        'killed': 'sum',
        'attack_types': 'count',
        f'{by}':'first'
    }).rename(columns={
        'injured': 'total_injured',
        'killed': 'total_killed',
        'attack_types': 'attack_count',
        f'{by}':f'{by}'
    })

    analysis['lethality_score'] = analysis['total_injured'] + (analysis['total_killed'] * 2)

    result = analysis.sort_values('lethality_score', ascending=False)
    # highest_lethality = result[['lethality_score', f'{by}']].iloc[0]

    return result




def analyze_attack_types(top_n=None):

    result = get_data_by_('attack_types')

    if top_n:
        result = result.head(top_n)

    return result




def deadliest_average_by_region(top=None):

    result = get_data_by_("region")

    if top:
        result = result.head(top)

    return result
