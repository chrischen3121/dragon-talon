import os
from typing import Optional

from itemadapter import ItemAdapter
from pymongo import ASCENDING, IndexModel, MongoClient

from . import items


def _get_mongo_uri() -> str:
    with open(os.environ.get("DRAGON_TALON_DB_USERNAME_FILE"), "rt") as fs:
        username = fs.read().strip()
    with open(os.environ.get("DRAGON_TALON_DB_PASSWORD_FILE"), "rt") as fs:
        password = fs.read().strip()
    return f"mongodb://{username}:{password}@mongodb:27000"


class MongoPipeline:

    collection_name = "scrapy_items"
    # TODO: items to different collections

    def __init__(self):
        self._mongo_uri = _get_mongo_uri()
        self._dbname = "scrapy"
        self._colname: Optional[str] = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        if spider.name == "xiaoqu":
            self._colname = "xiaoqu"
            cli = MongoClient(self._mongo_uri, tz_aware=True)
            db = cli.get_database(self._dbname)
            col = db.get_collection("self._colname")
            # index1 = IndexModel([("xiaoqu_id", ASCENDING), unique=True])
            # col.create_indexes([index1])
        # TODO: create motor cli

    def close_spider(self, spider):
        # self.client.close()
        pass

    async def process_item(self, item, spider):
        # if isinstance(item, items.XiaoquItem):
        #     return await self._process_xiaoqu_item(item)
        # self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        pass

    async def _process_xiaoqu_item(self, item):
        pass
