import os

import pymongo
from itemadapter import ItemAdapter


def _get_mongo_uri() -> str:
    with open(os.environ.get("DRAGON_TALON_DB_USERNAME_FILE"), "rt") as fs:
        username = fs.readline()
    with open(os.environ.get("DRAGON_TALON_DB_PASSWORD_FILE"), "rt") as fs:
        password = fs.readline()
    return f"mongodb://{username}:{password}@mongodb:27000"


class MongoPipeline:

    collection_name = "scrapy_items"

    def __init__(self, mongo_uri, mongo_db):
        self._mongo_uri = _get_mongo_uri()
        self._db = "scrapy"

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items"),
        )


    def open_spider(self, spider):
        # self.client = pymongo.MongoClient(self.mongo_uri)
        # self.db = self.client[self.mongo_db]
        pass

    def close_spider(self, spider):
        # self.client.close()
        pass

    async def process_item(self, item, spider):
        # print(item)
        # self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item
