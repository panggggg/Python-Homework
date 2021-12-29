import json
import pika
import redis

from Config.development import config
from database.mongodb import Mongo

mongo_config = config["mongodb_config"]
mongodb = Mongo(
    host=mongo_config["host"],
    port=mongo_config["port"],
    username=mongo_config["username"],
    password=mongo_config["password"],
    auth_db=mongo_config["auth_db"],
    db=mongo_config["database"],
    collection=mongo_config["collection"]
)
mongodb._connect()
print(f"[ Connected to MongoDB ]")

redis_config = config["redis_config"]
redis_connect = redis.Redis(host=redis_config["host"], port=redis_config["port"], password=redis_config["password"])
print(f"[ Connected to Redis ]")

credentials = pika.PlainCredentials("root", "root")
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange="py-homework", exchange_type="direct")

def callback(ch, method, properties, body):
    message = json.loads(body)
    title = message.get("title")
    print("Receive message: ")
    print(f"""
            Title: {message.get("title")}
            pageCount:{message.get("pageCount")}
            Authors: {message.get("authors")}
            Categories: {message.get("categories")}
        """)
    print("Save to redis", redis_connect.set(title, title))
    mongodb.save_to_mongo(message)
    print("Successfully saved!")
    channel.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue="Test", on_message_callback=callback)
print("[*] Waitting for data")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
