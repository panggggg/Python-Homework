import arrow
import json
import pika
import redis
from typing import Dict, Union

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
    message["created_at"] = str(arrow.utcnow())
    message["updated_at"] = str(arrow.utcnow())

    return message

def setup_message(message: Dict) -> str:
    message = {}
    message["title"] = message_dict.get("title")
    message["pageCount"] = message_dict.get("pageCount")
    message["authors"] = message_dict.get("authors")
    message["categories"] = message_dict.get("categories")
 
    return str(message)

def get_message_from_redis(key: str) -> Union[bytes, None]:
    get_from_redis = redis_connect.get(key)
    return get_from_redis

body = get_input_meassage()
message = json.dumps(body) #str -> dict
message_dict = json.loads(message) #dict -> str

get_title = message_dict.get("title")
key = get_title.replace(" ", "")
message_for_check = setup_message(message_dict)
redis_message = get_message_from_redis(key)

if redis_message is not None:
    if message_for_check == redis_message.decode("utf-8"):
        print("[X] This message was sent")
else:
    channel.basic_publish(exchange="py-homework",
                    routing_key="Test-key", body=json.dumps(body))
    print("[.] Message has send")
channel.close()
