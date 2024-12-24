import json

import folium
import requests
from anyio import sleep
from confluent_kafka import Consumer
from scipy.optimize import bracket

from news.news_api.configs.config_kafka import KAFKA_BROKER, HISTORIC_TOPIC

consumer = Consumer({'bootstrap.servers': KAFKA_BROKER,
                     'group.id': 'terrorism',
                     'auto.offset.reset': 'earliest'
                     })

consumer.subscribe([HISTORIC_TOPIC])

def plot_map():
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

        data = json.loads(msg.value().decode('utf-8'))
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

                map_object.save("news_map.html")
                print("Map updated and saved to 'news_map.html'")
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