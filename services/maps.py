import os
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

        output_path = "../maps/casualty_markers_map.html"
        casualty_map.save(output_path)

        if os.path.exists(output_path):
            print(f"Map with markers saved successfully to '{output_path}'")
        else:
            print("Failed to save the map.")
    else:
        print("No data available to plot on the map.")





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

        output_path = "../maps/avg_change_map.html"
        attack_map.save(output_path)

        if os.path.exists(output_path):
            print(f"Map saved successfully to '{output_path}'")
        else:
            print("Failed to save the map.")
    else:
        print("No data available to plot on the map.")



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

    attack_map.save("../maps/terrorist_groups_map.html")
    print("Map saved as 'terrorist_groups_map.html'")

