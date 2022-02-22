# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter # Added by Scrapy
import logging
import pymongo
from dotenv import load_dotenv
import os
import sys

load_dotenv()


class ImdbPipeline:

    def open_spider(self, spider):
        ENV = os.getenv("ENV")
        print(">>> RUNNING IN", ENV, "ENVIRONMENT")

        if ENV == "DEV":
            self.MONGO_URI = os.getenv("DEV_MONGO_URI")
        elif ENV == "PROD":
            self.MONGO_URI = os.getenv("PROD_MONGO_URI")
        elif ENV == "TEST":
            self.MONGO_URI = os.getenv("TEST_MONGO_URI")
        else:
            logging.warning("UNKNOWN ENVIORNMENT, TERMINATING SPIDER")
            sys.exit()

        print(">>> MONGO_URI:", self.MONGO_URI)
        self.client = pymongo.MongoClient(self.MONGO_URI)
        self.db = self.client[os.getenv("DB_NAME")]


    def close_spider(self, spider):
        print(">>> CLOSING MONGO CONNECTION")
        self.client.close()

    def process_item(self, item, spider):
        collection_name = getattr(spider, "COLLECTION_NAME")
        self.db[collection_name].insert_one(item)
        return item
