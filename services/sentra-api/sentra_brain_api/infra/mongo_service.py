from pymongo import MongoClient
from sentra_brain_api.core.config import settings

class MongoService:
    def __init__(self):
        self.client = MongoClient(settings.mongo_url)
        self.db = self.client[settings.mongo_db_name]

    def get_collection(self, name):
        return self.db[name]
