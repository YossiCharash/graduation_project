
import json
import time

import groq
import requests
from confluent_kafka import Producer

from news.news_api.configs.config_groq import GROQ_API_KEY
from news.news_api.configs.config_kafka import KAFKA_BROKER, HISTORIC_TOPIC, CURRENT_TOPIC
from news.news_api.configs.config_news import NEWS_API_URL

ARTICLES_PAGE = 1




producer = Producer({'bootstrap.servers': KAFKA_BROKER})



def fetch_news():
    # global ARTICLES_PAGE
    # payload = {
    #     "action": "getArticles",
    #     "keyword": "terror attack",
    #     "ignoreSourceGroupUri": "paywall/paywalled_sources",
    #     "articlesPage": ARTICLES_PAGE,
    #     "articlesCount": 1,
    #     "articlesSortBy": "socialScore",
    #     "articlesSortByAsc": False,
    #     "dataType": ["news", "pr"],
    #     "forceMaxDataTimeWindow": 31,
    #     "resultType": "articles",
    #     "apiKey": API_KEY_NEWS
    # }

    response = requests.get(NEWS_API_URL)
    if response.status_code == 200:
        try:
            data = response.json()
            print(json.dumps(data['res'], indent=4))
            filter_by_category(data.get("articles", {}).get("results", []))
            return data.get("articles", {}).get("results", [])
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            return []
    else:
        print(f"Failed to fetch news: {response.status_code}")
        return []

def filter_by_category(message_text):
    groq_api = groq.GroqAPI(api_key=GROQ_API_KEY)
    response = groq_api.classify(message_text,
                                 categories=['general news', 'historic terrorist incident', 'current terrorist event'])

    for new in message_text:
        if isinstance(new, dict) and 'title' in new:
            print(f"Sent article: {new['title']} to Kafka")
            if response['category'] == 'historic terrorist incident':
                send_to_kafka(HISTORIC_TOPIC,new)
            elif response['category'] == 'current terrorist event':
                send_to_kafka(CURRENT_TOPIC,new)
        else:
            print(f"Article is not a dictionary or does not contain 'title': {new}")





def send_to_kafka(topic,data):
    try:
        producer.produce(topic, value=json.dumps(data).encode('utf-8'))
        producer.flush()
        print(f"Sent message to Kafka: {data}")
    except Exception as e:
        print(e)


def main():
    while True:
        fetch_news()
        time.sleep(120)




