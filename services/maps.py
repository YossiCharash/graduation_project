import os

from folium.plugins import MarkerCluster
from sklearn.cluster import KMeans
import folium



def plot_casualties(df):
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        raise ValueError("Columns 'latitude' and 'longitude' are missing from the DataFrame.")

    df = df.dropna(subset=['latitude', 'longitude'])
    kmeans = KMeans(n_clusters=5, random_state=42)
    df['cluster'] = kmeans.fit_predict(df[['latitude', 'longitude']])

    if not df.empty:
        map_center = [df.iloc[0]['latitude'], df.iloc[0]['longitude']]
        casualty_map = folium.Map(location=map_center, zoom_start=5)

        colors = ['red', 'blue', 'green', 'purple', 'orange']
        for _, row in df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(
                    f"<strong>Region:</strong> {row['region']}<br>"
                    f"<strong>Avg Casualties:</strong> {row.get('avg_casualties', 'N/A'):.2f}<br>"
                    f"<strong>Total Casualties:</strong> {row.get('total_casualties', 'N/A')}<br>"
                    f"<strong>Cluster:</strong> {row['cluster']}",
                    max_width=300
                ),
                icon=folium.Icon(color=colors[row['cluster']])
            ).add_to(casualty_map)

        output_path = "../templates/casualty_markers_map.html"
        casualty_map.save(output_path)

        if os.path.exists(output_path):
            print(f"Map with markers saved successfully to '{output_path}'")
        else:
            print("Failed to save the map.")
    else:
        print("No data available to plot on the map.")
    return output_path





def plot_avg_change_per_region(df):

    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        raise ValueError("Columns 'latitude' and 'longitude' are missing from the DataFrame.")

    if 'region' not in df.columns or 'percent_change' not in df.columns:
        raise ValueError("Columns 'region' and 'percent_change' are missing from the DataFrame.")

    df = df.dropna(subset=['latitude', 'longitude'])

    if not df.empty:
        map_center = [df['latitude'].mean(), df['longitude'].mean()]
        attack_map = folium.Map(location=map_center, zoom_start=3)

        grouped = df.groupby('region').agg(
            latitude=('latitude', 'first'),
            longitude=('longitude', 'first'),
            avg_percent_change=('percent_change', 'mean')
        ).reset_index()

        for _, row in grouped.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(
                    f"<strong>Region:</strong> {row['region']}<br>"
                    f"<strong>Average Percent Change:</strong> {row['avg_percent_change']:.2f}%<br>",
                    max_width=300
                ),
                icon=folium.Icon(color='green' if row['avg_percent_change'] >= 0 else 'red')
            ).add_to(attack_map)

        output_path = "../templates/avg_change_map.html"
        attack_map.save(output_path)

        if os.path.exists(output_path):
            print(f"Map saved successfully to '{output_path}'")
        else:
            print("Failed to save the map.")
        return output_path

    else:
        print("No data available to plot on the map.")

    return None

def plot_top_groups_on_map_(df, region=None, top_n=5):
    df = df.dropna(subset=['latitude', 'longitude'])

    if not df.empty:
        map_center = [df['latitude'].mean(), df['longitude'].mean()]
        attack_map = folium.Map(location=map_center, zoom_start=6)
    regions = df['region'].unique()
    for region in regions:
        region_data = df[df['region'] == region]

        if top_n:
            region_data = region_data.nlargest(top_n, 'event_count')

        for _, row in region_data.iterrows():
            group = row['region']
            event_count = row['event_count']
            lat, lon = row['latitude'], row['longitude']
            top_groups = region_data.nlargest(top_n, 'event_count')
            top_groups_info = "<br>".join([f"{r['terrorists_attack_group']}: {r['event_count']}" for _, r in top_groups.iterrows()])
            folium.Marker(
                location=[lat, lon],
                popup=f"Region: {region}<br>Group: {group}<br>Events: {event_count}<br><br>Top Groups in Region:<br>{top_groups_info}",
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(attack_map)

    attack_map.save("../templates/terrorist_groups_map.html")
    print("Map saved as 'terrorist_groups_map.html'")

    return 'terrorist_groups_map.html'



def plot_groups_common_goals(df, filt):

    df = df.dropna(subset=['latitude', 'longitude'])

    if not df.empty:
        map_center = [df['latitude'].mean(), df['longitude'].mean()]
        attack_map = folium.Map(location=map_center, zoom_start=6)
    regions = df['region'].unique()
    for region in regions:
        region_data = df[df['region'] == region]
        for _, row in region_data.iterrows():
            region = row[filt]
            target_types = row['target_types']
            group_name = row['group_name']
            lat, lon = row['latitude'], row['longitude']
            folium.Marker(
                location=[lat, lon],
                popup=f"Region: {region}<br>Group: {group_name}<br>target_types: {target_types}<br><br>Top Groups in Region:<br>",
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(attack_map)

    attack_map.save("../maps/plot_groups_common_goals.html")
    print("Map saved as 'plot_groups_common_goals.html'")


def plt_areas_common_attack_strategies_by_groups(data,filt):
    map_center = [data['latitude'].mean(), data['longitude'].mean()]
    attack_map = folium.Map(location=map_center, zoom_start=(2))
    marker_cluster = MarkerCluster().add_to(attack_map)

    for _, row in data.iterrows():
        popup_content = (
            f"<b>Attack Type:</b> {row['attack_types']}<br>"
            f"<b>Unique Groups:</b> {row['unique_groups']}<br>"
            f"<b>Location:</b> {row[filt]}"
        )
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_content,
            icon=folium.Icon(color='blue', icon='info-sign'),
        ).add_to(marker_cluster)
        print(_)
    attack_map.save("../maps/areas_common_attack_strategies_by_groups.html")
    print("Map saved as 'areas_common_attack_strategies_by_groups_map.html'")




def plot_identify_areas_with_high_intergroup_activity(df,filter_by):
    map_center = [df['latitude'].mean(), df['longitude'].mean()]
    activity_map = folium.Map(location=map_center, zoom_start=6)
    marker_cluster = MarkerCluster().add_to(activity_map)

    for _, row in df.iterrows():
        popup_content = (
            f"<b>{filter_by.capitalize()}:</b> {row[filter_by]}<br>"
            f"<b>Unique Groups Count:</b> {row['unique_groups_count']}<br>"
        )
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_content,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)
    activity_map.save("../maps/identify_areas_with_high_intergroup_activity.html")
    print("Map saved as 'identify_areas_with_high_intergroup_activity.html'")