import os
from dataclasses import asdict
from typing import Optional

from itemadapter import ItemAdapter
from motor import motor_asyncio
from pymongo import ASCENDING, IndexModel, MongoClient

from . import items


def _get_mongo_uri() -> str:
    with open(os.environ.get("DRAGON_TALON_DB_USERNAME_FILE"), "rt") as fs:
        username = fs.read().strip()
    with open(os.environ.get("DRAGON_TALON_DB_PASSWORD_FILE"), "rt") as fs:
        password = fs.read().strip()
    return f"mongodb://{username}:{password}@mongodb:27000"


class MongoPipeline:
    def __init__(self):
        self._mongo_uri = _get_mongo_uri()
        self._dbname = "scrapy"
        self._colname: Optional[str] = None
        self._motor_cli: Optional[motor_asyncio.AsyncIOMotorClient] = None
        self._motor_col = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        if spider.name == "xiaoqu":
            self._colname = "xiaoqu"
            cli = MongoClient(self._mongo_uri, tz_aware=True)
            db = cli.get_database(self._dbname)
            col = db.get_collection(self._colname)
            index1 = IndexModel([("xiaoqu_id", ASCENDING)], unique=True)
            index2 = IndexModel([("district", ASCENDING), ("area", ASCENDING)])
            col.create_indexes([index1, index2])
        else:
            raise RuntimeError("unknown spider {repr(spider)}")

        self._motor_cli = motor_asyncio.AsyncIOMotorClient(self._mongo_uri, tz_aware=True)
        db = self._motor_cli.get_database(self._dbname)
        self._motor_col = db.get_collection(self._colname)

    def close_spider(self, spider):
        pass

    async def process_item(self, item, spider):
        record_to_insert = asdict(item)
        # self._motor_col
        print(record_to_insert)
        # if isinstance(item, items.XiaoquItem):
        #     return await self._process_xiaoqu_item(item)
        pass
