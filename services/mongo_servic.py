import pandas as pd

from repositores.mongo import get_raw_data_casualties
from services.maps import plot_attacks_on_map, plot_casualties, plot_top_groups_on_map_


def get_data_by_(by, returned):
    raw_data = get_raw_data_casualties()

    df = pd.DataFrame(raw_data)

    df['injured'] = df['casualties'].apply(lambda x: x['injured'])
    df['killed'] = df['casualties'].apply(lambda x: x['killed'])
    df['region'] = df['location'].apply(lambda x: x['area'])
    df['latitude'] = df['location'].apply(lambda x: x.get('latitude', None))
    df['longitude'] = df['location'].apply(lambda x: x.get('longitude', None))
    df['year'] = df['date'].dt.year


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




def analyze_attack_types(top_n=None):

    result = get_data_by_('attack_types','sum')
    print(result)
    if top_n:
        result = result.head(top_n)

    return result

def deadliest_average_by_region(top_n=None):
    raw_data = get_raw_data_casualties()
    df = pd.DataFrame(raw_data)

    # Extract relevant fields
    df['region'] = df['location'].apply(lambda x: x['area'])
    df['latitude'] = df['location'].apply(lambda x: x.get('latitude', None))
    df['longitude'] = df['location'].apply(lambda x: x.get('longitude', None))
    df['year'] = pd.to_datetime(df['date']).dt.year

    # Calculate total casualties for each event
    df['casualties'] = df['casualties'].apply(lambda x: x['injured'] + (x['killed'] * 2))

    # Group by region to calculate averages
    avg_casualties = df.groupby('region').agg(
        avg_casualties=('casualties', 'mean'),
        total_casualties=('casualties', 'sum'),
        latitude=('latitude', 'first'),
        longitude=('longitude', 'first')
    ).reset_index()

    # Filter top N or all
    if top_n:
        avg_casualties = avg_casualties.sort_values(by='avg_casualties', ascending=False).head(top_n)

    print(avg_casualties)

    # Plot on map
    plot_casualties(avg_casualties)

    return avg_casualties

    return result


def five_grops():
    result = get_data_by_('terrorists_attack_group','sum')
    result  = result[result['terrorists_attack_group']!= 'Unknown']
    result = result.head(5)
    print(result)
    return result


def change_number_attacks(top_n=None):
    raw_data = get_raw_data_casualties()
    df = pd.DataFrame(raw_data)

    df['region'] = df['location'].apply(lambda x: x['area'])
    df['latitude'] = df['location'].apply(lambda x: x.get('latitude', None))
    df['longitude'] = df['location'].apply(lambda x: x.get('longitude', None))
    df['year'] = pd.to_datetime(df['date']).dt.year
    attacks_per_year = df.groupby(['region', 'year', 'latitude', 'longitude']).size().reset_index(name='attack_count')
    attacks_per_year['percent_change'] = attacks_per_year.groupby('region')['attack_count'].pct_change() * 100

    avg_casualties = attacks_per_year.groupby('region').agg(
        change_attack=('attack_count', 'mean'),
        latitude=('latitude', 'first'),
        longitude=('longitude', 'first')
    ).reset_index()

    if top_n:
        avg_casualties = avg_casualties.sort_values(by='change_attack', ascending=False).head(top_n)

    plot_attacks_on_map(attacks_per_year)
    print(avg_casualties)
    return avg_casualties




def sum_by_grops(region=None, top_n=None):
    raw_data = get_raw_data_casualties()
    df = pd.DataFrame(raw_data)
    df['region'] = df['location'].apply(lambda x: x['area'])
    df['terrorists_attack_group'] = df['terrorists_attack_group'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

    df = df[df['terrorists_attack_group'] != 'Unknown']

    if region:
        df = df[df['region'] == region]

    grouped_counts = df.groupby(['terrorists_attack_group', 'region']).size()
    grouped_counts = grouped_counts.reset_index(name='event_count')
    grouped_counts = grouped_counts.sort_values(by=['event_count', 'terrorists_attack_group'], ascending=False)
    if top_n:
        grouped_counts = grouped_counts.head(top_n)
    else:
        grouped_counts = grouped_counts.head(1)

    # plot_top_groups_on_map_(grouped_counts)
    print(grouped_counts)
    return grouped_counts



def groups_common_goals(country=None, region=None):
    raw_data = get_raw_data_casualties()
    df = pd.DataFrame(raw_data)

    # Extract relevant columns
    df['region'] = df['location'].apply(lambda x: x['area'])
    df['group_name'] = df['terrorists_attack_group']
    df['target_types'] = df['target_types']
    df['latitude'] = df['location'].apply(lambda x: x.get('latitude', None))
    df['longitude'] = df['location'].apply(lambda x: x.get('longitude', None))
    df = df[df['group_name'] != 'Unknown']


    # Ensure 'target_types' and 'group_name' are not lists
    df = df.explode('target_types') if 'target_types' in df.columns else df
    df = df.explode('group_name') if 'group_name' in df.columns else df

    if region:
        filtered_data = df[(df['region'] == region) & (df['target_types'].notnull()) & (df['group_name'].notnull())]
    else:
        filtered_data = df[(df['target_types'].notnull()) & (df['group_name'].notnull())]

    # Group by region, target type, and group name
    grouped = filtered_data.groupby(['region', 'target_types', 'group_name']).size().reset_index()
    common_targets = grouped.groupby(['region', 'group_name']).filter(lambda x: len(x) > 1)

    print(common_targets)
    return common_targets

def groups_participated_those_attacks():
    raw_data = get_raw_data_casualties()
    df = pd.DataFrame(raw_data)

    # Ensure 'terrorists_attack_group' is not a list
    if 'terrorists_attack_group' in df.columns:
        df = df.explode('terrorists_attack_group')

    # Remove unknown or missing values
    df = df[df['terrorists_attack_group'].notnull() & (df['terrorists_attack_group'] != 'Unknown')]

    # Count occurrences of each group
    group_counts = df['terrorists_attack_group'].value_counts()

    # Filter groups with attack counts greater than or equal to the minimum threshold
    significant_groups = group_counts[group_counts > 1].reset_index()
    significant_groups.columns = ['terrorists_attack_group', 'attack_count']

    print(significant_groups)
    return significant_groups

    print(grouped_attacks)
    return grouped_attacks




# five_grops()
# analyze_attack_types()
groups_participated_those_attacks()

# deadliest_average_by_region()
# change_number_attacks()
# sum_by_grops('Central America & Caribbean',5)
# groups_common_goals("",'East Asia')
