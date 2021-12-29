import pymongo

from models.book import CreateBook, UpdateBook

class Mongo:
    def __init__(self, host, port, username, password, auth_db, db, collection):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth_db = auth_db
        self.db = db
        self.collection = collection

    def _connect(self):
        client = pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            authSource=self.auth_db,
            authMechanism="SCRAM-SHA-1"
        )
        database = client[self.db]
        self.connection = database[self.collection]

    def save_to_mongo(self, message: CreateBook):
        return self.connection.insert_one(message)

    def update_to_mongo(self, query, message: UpdateBook):
        return self.connection.update_one()

