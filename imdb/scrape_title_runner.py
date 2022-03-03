import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from imdb.spiders.scrape_title import ScrapeTitleSpider
from multiprocessing import Process, Queue
import pymongo
from dotenv import load_dotenv
import os
import sys
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--collection", help="MongoDB collection name to loop through")
parser.add_argument("-k", "--key", help="Collection key to get data from")
args = parser.parse_args()

load_dotenv()
# Enviornment Variables
ENV = os.getenv("ENV")
DB_NAME = os.getenv("DB_NAME")

def check_args():
    if args.collection and args.key is not None:
        print(f"ARGUMENTS:\n\nCollection: {args.collection}\nKey: {args.key}")
    else:
        print("COLLECTION:", args.collection, "\nKEY:", args.key)
        print('You have to add a collection and collection key, use the "-h" flag for more help\nTerminating runner')
        sys.exit()

def run_spider(spider, imdb_id):
    def f(q):
        try:
            settings = get_project_settings()
            configure_logging(settings)
            runner = CrawlerRunner(settings)
            deferred = runner.crawl(spider, ID=imdb_id)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result

def connect_to_db():
    print("\n>>> RUNNING IN", ENV, "ENVIRONMENT")

    if ENV == "DEV":
        MONGO_URI = os.getenv("DEV_MONGO_URI")
    elif ENV == "PROD":
        MONGO_URI = os.getenv("PROD_MONGO_URI")
    elif ENV == "TEST":
        MONGO_URI = os.getenv("TEST_MONGO_URI")
    else:
        logging.warning("UNKNOWN ENVIORNMENT, TERMINATING SPIDER RUNNER")
        sys.exit()

    print(">>> MONGO_URI:", MONGO_URI + "\n")
    return pymongo.MongoClient(MONGO_URI)

def loop_through_collection(client, db_name, collection_name, collection_key):
    db = client[db_name]
    collection = db[collection_name].find()

    try:
        for document in collection:
            run_spider(ScrapeTitleSpider, document[collection_key])

    except KeyError:
        print(f'DOCUMENT "_id:{document["_id"]}" DOES NOT HAVE THE "{collection_key}" KEY')
    except Exception as e:
        print("SOMETHING UNEXPECTED HAPPENED in loop_through_collection:\n" + e)

def main():
    check_args()
    client = connect_to_db()
    loop_through_collection(client, DB_NAME, args.collection, args.key)

if __name__ == "__main__":
    main()
