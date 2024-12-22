import pandas as pd

from repositores.mongo import get_raw_data_casualties
from services.maps import plot_casualties, plot_top_groups_on_map_, plot_avg_change_per_region


def get_location():
    raw_data = get_raw_data_casualties()

    df = pd.DataFrame(raw_data)
    df['region'] = df['location'].apply(lambda x: x['area'])
    df['latitude'] = df['location'].apply(lambda x: x.get('latitude', None))
    df['longitude'] = df['location'].apply(lambda x: x.get('longitude', None))

    return df

def get_data_by_(by, returned):
    df = get_location()

    df['injured'] = df['casualties'].apply(lambda x: x['injured'])
    df['killed'] = df['casualties'].apply(lambda x: x['killed'])



    df_exploded = df.explode(by)

    df_exploded['lethality_score'] = df_exploded['injured'] + (df_exploded['killed'] * 2)
    df_exploded['event_count'] = df_exploded[by].count()

    if returned == "sum":
        result = df_exploded.groupby(by)['lethality_score'].sum().reset_index().sort_values(by='lethality_score', ascending=False)
    elif returned == "avg":
        result =df_exploded.groupby(by)['lethality_score'].mean().reset_index()
    else:
        return None

    return result



#ex 1 1
def analyze_attack_types(top_n=None):

    result = get_data_by_('attack_types','sum')
    print(result)
    if top_n:
        result = result.head(top_n)

    return result


#ex1 2 map work
def deadliest_average_by_region(top_n=None):
    df =get_location()

    # Extract relevant fields

    df['year'] = pd.to_datetime(df['date']).dt.year

    # Calculate total casualties for each event
    df['casualties'] = df['casualties'].apply(lambda x: x['injured'] + (x['killed'] * 2))

    avg_casualties = df.groupby('region').agg(
        avg_casualties=('casualties', 'mean'),
        total_casualties=('casualties', 'sum'),
        latitude=('latitude', 'first'),
        longitude=('longitude', 'first')
    ).reset_index()

    if top_n:
        avg_casualties = avg_casualties.sort_values(by='avg_casualties', ascending=False).head(top_n)

    print(avg_casualties)

    # Plot on map
    plot_casualties(avg_casualties)

    return avg_casualties

    return result


#ex1 3
def five_grops():
    result = get_data_by_('terrorists_attack_group','sum')
    result  = result[result['terrorists_attack_group']!= 'Unknown']
    result = result.head(5)
    print(result)
    return result


#ex1 6 map work
def fix_coordinates(group):
    valid_coords = group.dropna(subset=['latitude', 'longitude']).iloc[0] if not group.dropna(subset=['latitude', 'longitude']).empty else None
    if valid_coords is not None:
        group['latitude'] = group['latitude'].fillna(valid_coords['latitude'])
        group['longitude'] = group['longitude'].fillna(valid_coords['longitude'])
    return group

def change_number_attacks(top_n=None):
    df = get_location()
    df['year'] = pd.to_datetime(df['date']).dt.year

    attacks_per_year = df.groupby(['region', 'year', 'latitude', 'longitude']).size().reset_index(name='attack_count')
    attacks_per_year['percent_change'] = attacks_per_year.groupby('region')['attack_count'].pct_change()  * 10

    attacks_per_year = attacks_per_year.groupby('region', group_keys=False).apply(fix_coordinates).reset_index(drop=True)

    avg_casualties = attacks_per_year.groupby('region', as_index=False).agg(
        change_attack=('attack_count', 'mean'),
        latitude=('latitude', 'first'),
        longitude=('longitude', 'first')
    )

    if top_n:
        avg_casualties = avg_casualties.sort_values(by='change_attack', ascending=False).head(top_n)

    plot_avg_change_per_region(attacks_per_year)
    print(avg_casualties)
    return avg_casualties



#ex1 8 map work
def sum_by_grops(region=None, top_n=None, latitude=None, longitude=None):
    df = get_location()
    df['terrorists_attack_group'] = df['terrorists_attack_group'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

    df = df[df['terrorists_attack_group'] != 'Unknown']

    if region:
        df = df[df['region'] == region]

    avg_casualties = df.groupby(['terrorists_attack_group', 'region']).agg(
        event_count=('terrorists_attack_group', 'count'),
        latitude=('latitude', 'first'),
        longitude=('longitude', 'first')
    ).reset_index()

    grouped_counts = avg_casualties.sort_values(by=['event_count', 'terrorists_attack_group'], ascending=False)

    if latitude is not None and longitude is not None:
        avg_casualties = avg_casualties[
            (avg_casualties['latitude'] == latitude) & (avg_casualties['longitude'] == longitude)
        ]

    if top_n:
        avg_casualties = avg_casualties.groupby('region').apply(lambda x: x.head(top_n)).reset_index(drop=True)

    highlighted_groups = avg_casualties.groupby('region').apply(lambda x: x.nlargest(1, 'event_count')).reset_index(drop=True)
    plot_top_groups_on_map_(highlighted_groups, top_n)

    print(grouped_counts)
    return grouped_counts





#ex2 1 map
def groups_common_goals(country=None, region=None):
    df = get_location()

    df['group_name'] = df['terrorists_attack_group']
    df['target_types'] = df['target_types']
    df = df[df['group_name'] != 'Unknown']


    df = df.explode('target_types') if 'target_types' in df.columns else df
    df = df.explode('group_name') if 'group_name' in df.columns else df

    if region:
        filtered_data = df[(df['region'] == region) & (df['target_types'].notnull()) & (df['group_name'].notnull())]
    else:
        filtered_data = df[(df['target_types'].notnull()) & (df['group_name'].notnull())]

    grouped = filtered_data.groupby(['region', 'target_types', 'group_name']).size().reset_index()
    common_targets = grouped.groupby(['region', 'group_name']).filter(lambda x: len(x) > 1)

    print(common_targets)
    return common_targets


#ex2 3
def groups_participated_those_attacks():
    raw_data = get_raw_data_casualties()
    df = pd.DataFrame(raw_data)

    if 'terrorists_attack_group' in df.columns:
        df = df.explode('terrorists_attack_group')

    df = df[df['terrorists_attack_group'].notnull() & (df['terrorists_attack_group'] != 'Unknown')]

    group_counts = df['terrorists_attack_group'].value_counts()

    significant_groups = group_counts[group_counts > 1].reset_index()
    significant_groups.columns = ['terrorists_attack_group', 'attack_count']

    print(significant_groups)
    return significant_groups






five_grops()
analyze_attack_types()
groups_participated_those_attacks()



deadliest_average_by_region()
change_number_attacks()
sum_by_grops()
groups_common_goals()

