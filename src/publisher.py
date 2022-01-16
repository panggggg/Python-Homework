import json
import pika
import redis
from typing import Dict, Union

from Config.development import config

credentials = pika.PlainCredentials(config["rabbitmq_config"]["username"], config["rabbitmq_config"]["password"])
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=config["rabbitmq_config"]["host"], credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange="py-homework", exchange_type="direct")

channel.queue_declare(queue="Test")
channel.queue_bind(exchange="py-homework",
                   queue="Test", routing_key="Test-key")

redis_config = config["redis_config"]
redis_connect = redis.Redis(
    host=redis_config["host"], port=redis_config["port"], password=redis_config["password"])
print(f"[ Connected to Redis ]")


def get_input_meassage() -> Dict:
    message = {}
    print("Title: ")
    title = input()
    print("Page: ")
    pageCount = int(input())
    print("Authors: ")
    authors = input()
    print("Categories: ")
    categories = input()

    message["title"] = title
    message["pageCount"] = pageCount
    message["authors"] = authors
    message["categories"] = categories

    return message

def get_message_from_redis(key: str) -> Union[bytes, None]:
    get_from_redis = redis_connect.get(key)
    return get_from_redis

body = get_input_meassage()
message = json.dumps(body) #dumps: dict -> json str, loads: json str -> dict

get_title = body.get("title")
key = get_title.replace(" ", "")
redis_message = get_message_from_redis(key)

if redis_message is not None and str(body) == redis_message.decode("utf-8"):
    print("[X] This message has was sent")
elif redis_message is None or str(body) != redis_message.decode("utf-8"):
    channel.basic_publish(exchange="py-homework",
                    routing_key="Test-key", body=json.dumps(body))
    print("[.] Message has send")
else:
    raise Exception("Something error")
    
channel.close()
