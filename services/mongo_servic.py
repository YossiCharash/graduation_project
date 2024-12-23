import pandas as pd

from repositores.mongo import get_raw_data_casualties
from services.maps import plot_casualties, plot_top_groups_on_map_, plot_avg_change_per_region, \
    plot_groups_common_goals, \
    plt_areas_common_attack_strategies_by_groups, plot_identify_areas_with_high_intergroup_activity


def get_location():
    raw_data = get_raw_data_casualties()

    df = pd.DataFrame(raw_data)
    df['region'] = df['location'].apply(lambda x: x['area'])
    df['latitude'] = df['location'].apply(lambda x: x.get('latitude', None))
    df['longitude'] = df['location'].apply(lambda x: x.get('longitude', None))

    return df

def get_data_by_(by):

    df = get_location()

    df['injured'] = df['casualties'].apply(lambda x: x['injured'])
    df['killed'] = df['casualties'].apply(lambda x: x['killed'])



    df_exploded = df.explode(by)

    df_exploded['lethality_score'] = df_exploded['injured'] + (df_exploded['killed'] * 2)
    df_exploded['event_count'] = df_exploded[by].count()

    result = df_exploded.groupby(by)['lethality_score'].sum().reset_index().sort_values(by='lethality_score', ascending=False)

    return result



#ex 1 1
def analyze_attack_types(top_n=None):
    """
    1. The deadliest attack types.
    "Deadliest" = the types with the highest
     number of casualties, killed and injured,
      where a casualty = 1 point
       and a kill is worth 2 points for the calculation.
    :param top_n:
    """
    result = get_data_by_('attack_types','sum')
    print(result)
    if top_n:
        result = result.head(top_n)

    return result


#ex1 2 map work
def deadliest_average_by_region(top_n=None):
    """
    Average number of casualties by region.
     Average percentage of casualties.
     Number of casualties according to the calculation
      from the previous question for the event by region.
    :param top_n:
    """
    df =get_location()

    df['year'] = pd.to_datetime(df['date']).dt.year
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

    plot_casualties(avg_casualties)

    return avg_casualties



#ex1 3
def five_groups_deadliest():
    """
    The five teams with the most casualties over the years
    """
    result = get_data_by_('terrorists_attack_group')
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
    """
    Percentage change in the number of attacks between years by region    :param top_n:
    """
    df = get_location()
    df['year'] = pd.to_datetime(df['date']).dt.year

    attacks_per_year = df.groupby(['region', 'year', 'latitude', 'longitude']).size().reset_index(name='attack_count')
    attacks_per_year['percent_change'] = attacks_per_year.groupby('region')['attack_count'].pct_change()  * 100

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
    """
    The most active groups in a particular area. Grouping the number of events by terrorist groups.
    :param region:
    :param top_n:
    :param latitude:
    :param longitude:
    """
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
def groups_common_goals(filter_by:str):
    """
    Identifying groups with common goals in the same area.
    """
    df = get_location()
    df['country'] = df['location'].apply(lambda x: x['country'])

    df['group_name'] = df['terrorists_attack_group']
    df['target_types'] = df['target_types']
    df = df[df['group_name'] != 'Unknown']

    df = df.explode('target_types') if 'target_types' in df.columns else df
    df = df.explode('group_name') if 'group_name' in df.columns else df

    filtered_data = df[(df['target_types'].notnull()) & (df['group_name'].notnull())]
    grouped = filtered_data.groupby([filter_by, 'target_types', 'group_name','longitude','latitude']).size().reset_index()
    common_targets = grouped.groupby([filter_by, 'group_name','longitude','latitude']).filter_by(lambda x: len(x) > 1)
    plot_groups_common_goals(common_targets,filter_by)
    return common_targets


#ex2 3
def groups_participated_those_attacks():
    """
    Locating groups that participated in those attacks
    """
    raw_data = get_raw_data_casualties()
    df = pd.DataFrame(raw_data)

    if 'terrorists_attack_group' in df.columns:
        df = df.explode('terrorists_attack_group')

    df['event_id'] = df['event_id'].astype(str)
    df['terrorists_attack_group'] = df['terrorists_attack_group'].astype(str)

    df = df[df['terrorists_attack_group'].notnull() & (df['terrorists_attack_group'] != 'Unknown')]

    event_groups = df.groupby('event_id')['terrorists_attack_group'].apply(list).reset_index()

    events_dict = event_groups.set_index('event_id')['terrorists_attack_group'].to_dict()

    print(events_dict)
    return events_dict




#ex2 14
def areas_common_attack_strategies_by_groups(filter_by):
    """
    Identifying areas with common attack strategies between groups
    """
    df = get_location()
    df['country'] = df['location'].apply(lambda x: x['country'])
    df['group_name'] = df['terrorists_attack_group'].apply(lambda x: str(x) if isinstance(x, list) else x)
    df['attack_types'] = df['attack_types'].apply(lambda x: str(x) if isinstance(x, list) else x)
    df = df[df['attack_types'] != 'Unknown']

    if filter_by not in df.columns:
        raise ValueError(f"{filter_by} column is not present in the data.")

    grouped = df.groupby(['region', 'country', 'longitude', 'latitude', 'attack_types'])['group_name'].nunique().reset_index()
    grouped = grouped.rename(columns={'group_name': 'unique_groups'})

    sorted_grouped = grouped.sort_values(by='unique_groups', ascending=False)
    top_areas = sorted_grouped.drop_duplicates(subset=['region'], keep='first').head(12)[
        ['region', 'longitude', 'latitude', 'attack_types', 'unique_groups']]

    plt_areas_common_attack_strategies_by_groups(top_areas, filter_by)

    print(top_areas)
    return top_areas

#ex2 15
def groups_similar_preferences_goals():
    """
    Identifies groups with similar preferences for attack targets.
    """
    df = get_location()
    df['group_name'] = df['terrorists_attack_group'].apply(lambda x: str(x) if isinstance(x, list) else x)
    df['target_types'] = df['target_types'].apply(lambda x: str(x) if isinstance(x, list) else x)
    filtered_data = df[df['target_types'].notnull() & df['group_name'].notnull()]
    if filtered_data.empty:
        raise ValueError("No valid data available after filtering.")
    grouped = filtered_data.groupby(['target_types', 'group_name']).size().reset_index(name='count')

    similar_groups = grouped.groupby('target_types')['group_name'].apply(list).reset_index()
    similar_groups = similar_groups[similar_groups['group_name'].apply(len) > 1]

    print(similar_groups)
    return similar_groups.to_dict(orient='records')


def identify_areas_with_high_intergroup_activity(filter_by):
    """
    Identifies areas with high intergroup activity and returns their coordinates and group count.
    """
    df = get_location()

    df['country'] = df['location'].apply(lambda x: x['country'])
    df['group_name'] = df['terrorists_attack_group'].apply(lambda x: str(x) if isinstance(x, list) else x)

    grouped = df.groupby([filter_by, 'longitude', 'latitude'])['group_name'].nunique().reset_index()
    grouped = grouped.rename(columns={'group_name': 'unique_groups_count'})

    sorted_grouped = grouped.sort_values(by='unique_groups_count', ascending=False)

    unique_areas = sorted_grouped.drop_duplicates(subset=['region'], keep='first')
    top_areas = unique_areas.head(12)[[filter_by, 'longitude', 'latitude', 'unique_groups_count']]

    plot_identify_areas_with_high_intergroup_activity(top_areas, filter_by)

    print(top_areas)
    return top_areas




