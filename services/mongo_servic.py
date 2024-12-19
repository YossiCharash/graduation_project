import pandas as pd
from databases.mongodb.config import collection
from repositores.mongo import get_raw_data_casualties


def analyze_attack_types(top_n=None):

    raw_data = get_raw_data_casualties(collection)

    df = pd.DataFrame(raw_data)

    df['injured'] = df['casualties'].apply(lambda x: x['injured'])
    df['killed'] = df['casualties'].apply(lambda x: x['killed'])

    df_exploded = df.explode('attack_types')

    analysis = df_exploded.groupby('attack_types').agg({
        'injured': 'sum',
        'killed': 'sum',
        'attack_types': 'count'
    }).rename(columns={
        'injured': 'total_injured',
        'killed': 'total_killed',
        'attack_types': 'attack_count'
    })

    analysis['lethality_score'] = analysis['total_injured'] + (analysis['total_killed'] * 2)

    result = analysis.sort_values('lethality_score', ascending=False)

    if top_n:
        result = result.head(top_n)

    return result


