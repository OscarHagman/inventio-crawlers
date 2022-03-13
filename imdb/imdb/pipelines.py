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
import boto3

load_dotenv()


class ImdbPipeline:

    def create_table(self, table_name):
        try:
            self.table = self.CLIENT.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'timestamp',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'timestamp',
                        'AttributeType': 'N'
                    }
            
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            print("Creating table")
            waiter = self.CLIENT.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print("Table created")
            
        except self.DDB_EXCEPTIONS.ResourceInUseException:
            print("Table already exists")
        except Exception as e:
            print("SOMETHING UNEXPECTED HAPPENED\n\n" + e)
    
    def connect_to_mongo(self, ENV):
        if ENV == "DEV":
            self.MONGO_URI = os.getenv("DEV_MONGO_URI")
        elif ENV == "PROD":
            self.MONGO_URI = os.getenv("PROD_MONGO_URI")
        elif ENV == "TEST":
            self.MONGO_URI = os.getenv("TEST_MONGO_URI")
        else:
            logging.warning("UNKNOWN ENVIORNMENT, TERMINATING SPIDER")
            sys.exit()

        print(">>> MONGO_URI:", self.MONGO_URI + "\n")
        self.CLIENT = pymongo.MongoClient(self.MONGO_URI)
        self.db = self.CLIENT[os.getenv("DB_NAME")]

    def open_spider(self, spider):
        ENV = os.getenv("ENV")
        print("\n>>> RUNNING IN", ENV, "ENVIRONMENT")
        # self.connect_to_mongo(ENV)

        
        self.CLIENT = boto3.client(
            "dynamodb",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        )

        self.DYNAMO_DB = boto3.resource(
            "dynamodb",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            )

        self.DDB_EXCEPTIONS = self.CLIENT.exceptions


    def close_spider(self, spider):
        # print("\n>>> CLOSING MONGO CONNECTION\n")
        # self.CLIENT.close()
        pass

    def process_item(self, item, spider):
        table_name = getattr(spider, "TABLE_NAME")
        
        self.DYNAMO_DB.Table(table_name).put_item(Item=item)
        # self.db[table_name].insert_one(item)
        return item
