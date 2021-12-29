import arrow
import json
import pika
from typing import Dict

credentials = pika.PlainCredentials("root", "root")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange="py-homework", exchange_type="direct")

channel.queue_declare(queue="Test")
channel.queue_bind(exchange="py-homework",
                   queue="Test", routing_key="Test-key")


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

print(type(get_input_meassage))
body = get_input_meassage()
print(body)

channel.basic_publish(exchange="py-homework",
                      routing_key="Test-key", body=json.dumps(body))
print("[.] Message has send")

channel.close()
