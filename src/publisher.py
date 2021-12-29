import json
import pika
import redis
from typing import Dict

from Config.development import config

credentials = pika.PlainCredentials("root", "root")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", credentials=credentials))
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

#NOTE: loads(dict -> str), dumps(str -> dict)

body = get_input_meassage()
message = json.dumps(body)
message_dict = json.loads(message)
print(str(message_dict))
get_title = message_dict.get("title")
key = get_title.replace(" ", "")

get_from_redis = redis_connect.get(key)
message_from_redis = get_from_redis.decode("utf-8")

if str(message_dict) == message_from_redis:
    print("This message was sent")
else:
    channel.basic_publish(exchange="py-homework",
                            routing_key="Test-key", body=json.dumps(body))
    print("[.] Message has send")

channel.close()
