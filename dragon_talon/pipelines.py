import asyncio
import os
import queue
import threading
import time
from collections import defaultdict
from dataclasses import asdict
from typing import Optional

import pymongo
from loguru import logger
from pymongo import ASCENDING, IndexModel

from . import items


def _get_mongo_uri() -> str:
    with open(os.environ.get("DRAGON_TALON_DB_USERNAME_FILE"), "rt") as fs:
        username = fs.read().strip()
    with open(os.environ.get("DRAGON_TALON_DB_PASSWORD_FILE"), "rt") as fs:
        password = fs.read().strip()
    return f"mongodb://{username}:{password}@mongodb:27017"


class MongoPipeline:
    _QUEUE_SENTINEL = None

    def __init__(self, spider_name: str):
        self._mongo_uri = _get_mongo_uri()
        self._spider_name = spider_name

        self._mongo_cli = pymongo.MongoClient(self._mongo_uri, tz_aware=True)
        self._db_inst = self._mongo_cli.get_database("scrapy")

        self._init_collections(spider_name)
        self._item_queue = queue.Queue(maxsize=1000)
        self._consume_thread = threading.Thread(target=self._consume_items, daemon=True)

    def _init_collections(self, spider_name: str):
        if spider_name == "xiaoqu":
            xiaoqu_info_col = self._db_inst.get_collection(items.XiaoquInfo.item_name)
            index1 = IndexModel([("xiaoqu_id", ASCENDING)], unique=True)
            index2 = IndexModel([("district", ASCENDING), ("area", ASCENDING)])
            xiaoqu_info_col.create_indexes([index1, index2])

            xiaoqu_daily_stats_col = self._db_inst.get_collection(items.XiaoquDailyStats.item_name)
            index1 = IndexModel([("date_", ASCENDING), ("xiaoqu_id", ASCENDING)], unique=True)
            xiaoqu_daily_stats_col.create_indexes([index1])
        else:
            raise RuntimeError(f"unexpected spider name {self._spider_name}")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider.name)

    def open_spider(self, spider):
        self._consume_thread.start()

    def close_spider(self, spider):
        self._item_queue.put(self._QUEUE_SENTINEL)
        self._consume_thread.join()

    def process_item(self, item, spider):
        self._item_queue.put(item)

    def _consume_items(self):
        while True:
            try:
                self._consume_all_items_in_queue()
            except StopIteration:
                break
            time.sleep(5)

    def _consume_all_items_in_queue(self):
        find_sentinel = False
        col2items = defaultdict(list)
        while not self._item_queue.empty():
            item = self._item_queue.get_nowait()
            if item == self._QUEUE_SENTINEL:
                find_sentinel = True
                break
            col2items[item.item_name].append(asdict(item))
        for colname, items2insert in col2items.items():
            collection = self._db_inst.get_collection(colname)
            try:
                collection.insert_many(
                    items2insert, ordered=False, bypass_document_validation=True
                )
            except pymongo.errors.BulkWriteError as exc:
                # ignore duplicate exception
                exc_list = [error for error in exc.details["writeErrors"] if error["code"] != 11000]
                if exc_list:
                    logger.error(f"col {colname}: insertion error {exc_list}")
                inserted = len(items2insert) - len(exc_list)
                logger.info(f"col {colname}: {inserted} items inserted")
            else:
                logger.info(f"col {colname}: {len(items2insert)} items inserted")
        if find_sentinel:
            raise StopIteration
