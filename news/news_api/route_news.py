

import json
import time

import requests
from confluent_kafka import Producer
from news.news_api.configs.config_groq import GROQ_API_KEY, GROQ_API_URL
from news.news_api.configs.config_kafka import KAFKA_BROKER, CURRENT_TOPIC, HISTORIC_TOPIC
from news.news_api.configs.config_news import NEWS_API_URL

# Define constants
ARTICLES_PAGE = 1

response_format_groq = {
    "type": "json_schema",
    "json_schema": {
        "name": "news_classification",
        "schema": {
            "type": "object",
            "properties": {
                "classification": {
                    "type": "string",
                    "enum": [
                        "Current terrorism event",
                        "Past terrorism event",
                        "Other news event"
                    ]
                },
                "location": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "longitude": {"type": "number"},
                        "latitude": {"type": "number"}
                    },
                    "required": ["description", "longitude", "latitude"]
                }
            },
            "required": ["classification", "location"],
            "additionalProperties": False
        },
        "strict": True
    }
}

producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def fetch_news():
    try:
        response = requests.get(f"{NEWS_API_URL}{ARTICLES_PAGE}")
        response.raise_for_status()
        data = response.json()
        return data.get("articles", {}).get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

def classify_news_article(article_content):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    payload = {
        "messages": [
            {"role": "system",
             "content": "You are an assistant classifying news articles into categories and locations"},
            {"role": "user", "content": f"This is a news article: {article_content}"}
        ],
        "model": "grok-2-1212",
        "stream": False,
        "temperature": 0,
        "response_format": response_format_groq
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"Response from GROQ API: {result}")

        # Extract classification and location details
        content = result.get("choices", [])[0].get("message", {}).get("content", "")
        classification_data = json.loads(content)
        return {
            "classification": classification_data.get("classification"),
            "location": classification_data.get("location")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error classifying article: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON content: {e}")
        return None

def send_to_kafka(topic, data):
    try:
        producer.produce(topic, value=json.dumps(data).encode('utf-8'))
        producer.flush()
        print(f"Sent message to Kafka topic '{topic}': {data}")
    except Exception as e:
        print(f"Error sending message to Kafka: {e}")

def main():
    while True:
        articles = fetch_news()
        for article in articles:
            classification = classify_news_article(article)
            if classification:
                classification_type = classification.get("classification")
                location = classification.get("location")
                if classification_type == "Current terrorism event":
                    send_to_kafka(CURRENT_TOPIC, {"classification": classification_type, "location": location})
                elif classification_type == "Past terrorism event":
                    send_to_kafka(HISTORIC_TOPIC, {"classification": classification_type, "location": location})
        time.sleep(120)


if __name__ == '__main__':
    main()
