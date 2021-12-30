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
redis_connect = redis.Redis(
    host=redis_config["host"], port=redis_config["port"], password=redis_config["password"])
print(f"[ Connected to Redis ]")

credentials = pika.PlainCredentials("root", "root")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange="py-homework", exchange_type="direct")


def callback(ch, method, properties, body):
    message = json.loads(body)

    book_title = message.get("title")
    pageCount = message.get("pageCount")
    authors = message.get("authors")
    categories = message.get("categories")
    updated_at = message.get("updated_at")

    key = book_title.replace(" ", "")
    
    redis = {}
    redis["title"] = book_title
    redis["pageCount"] = pageCount
    redis["authors"] = authors
    redis["categories"] = categories

    print("Receive message: ")
    print(f"""
            Title: {book_title}
            pageCount:{pageCount}
            Authors: {authors}
            Categories: {categories}
        """)
    
    if redis_connect.get(key) is None:
        redis_connect.set(key, str(redis))
        mongodb.update_to_mongo({'title': book_title},{ '$set': message})
        print("Successfully saved!")
    elif redis_connect.get(key) is not None:
        redis_connect.set(key, str(redis))
        mongodb.update_to_mongo({'title': book_title},{ '$set': { 'title': book_title, 'pageCount': pageCount, 'authors': authors, 'categories': categories, 'updated_at': updated_at } })
        print("Successfully updated!")
    else:
        raise Exception("Something error")
    channel.basic_ack(delivery_tag=method.delivery_tag)
    



channel.basic_consume(queue="Test", on_message_callback=callback)
print("[*] Waitting for data")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
