import json
import time
import webbrowser

import folium
import requests
from confluent_kafka import Consumer

from news.news_api.configs.config_kafka import KAFKA_BROKER, CURRENT_TOPIC
from news.news_api.configs.config_open_cage import OPEN_CAGE_API_KEY

consumer = Consumer({'bootstrap.servers': KAFKA_BROKER,
                     'group.id': 'terrorism',
                     'auto.offset.reset': 'earliest'
                     })

consumer.subscribe([CURRENT_TOPIC])

# def classify_message(location):
#     geocoding_api = requests.Session()
#     geocoding_api.headers['Authorization'] = f'Bearer {OPEN_CAGE_API_KEY}'
#
#     response = geocoding_api.get(f'https://api.opencage.com/geocode/v1/json/', params={'q': location, 'key': OPEN_CAGE_API_KEY})
#     if response.status_code == 200:
#         location_data = response.json()
#         latitude = location_data['results'][0]['geometry']['lat']
#         longitude = location_data['results'][0]['geometry']['lng']
#         print(f"Location: {location} -> Latitude: {latitude}, Longitude: {longitude}")
#     else:
#         print(f"Error geocoding {location}: {response.text}")

def plot_map(data):
    print("Plotting data on map...")
    map_object = folium.Map(location=[0, 0], zoom_start=2)
    events = []

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        location = data.get("location")
        classification = data.get("classification")

        if location:
            latitude = location.get("latitude")
            longitude = location.get("longitude")
            description = location.get("description")

            if latitude and longitude:
                events.append({
                    "latitude": latitude,
                    "longitude": longitude,
                    "description": description,
                    "classification": classification
                })

            if len(events) == 20:
                for event in events:
                    folium.Marker(
                        location=[event["latitude"], event["longitude"]],
                        popup=f"{event['classification']}: {event['description']}",
                        icon=folium.Icon(color="red" if event["classification"] == "Past terrorism event" else "blue")
                    ).add_to(map_object)

                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"news_map_{timestamp}.html"
                map_object.save(filename)
                print(f"Map updated and saved to '{filename}'")
                webbrowser.open(filename)  # Open the map in the default browser
                events.clear()



def main():
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue

        try:
            data = json.loads(msg.value().decode('utf-8'))
            plot_map(data)
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == '__main__':
    main()