from datetime import datetime

from pymongo import MongoClient


class MongoUtil:
    def __init__(self, host, port,  db_name):
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]

    def addTime(self, dictData):
        dictData['autoCreateTime'] = datetime.now()

    def insertCollection(self, collection, dictData):
        self.addTime(dictData)
        collection = self.db[collection]
        return collection.insert_one(dictData)

    def upsert(self, collection, dictData, filter):
        self.addTime(dictData)
        collection = self.db[collection]
        return collection.replace_one(filter, dictData, True)

    def query(self, collection, filter, sort=None):
        collection = self.db[collection]
        if sort:
            sort = list(sort.items())
        return collection.find(filter=filter, sort=sort)

    def find_one(self, collection, filter):
        collection = self.db[collection]
        sort = list({
                        '_id': -1
                    }.items())
        return collection.find_one(filter=filter, sort=sort)
