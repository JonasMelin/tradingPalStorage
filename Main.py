from pymongo import ASCENDING, MongoClient
import time
import requests
import json
import datetime
import sys

mongoPort = 27018
mongoHost = "127.0.0.1"
databaseName = "TP"
collectionName = f"tickers"
URL = "http://127.0.0.1:5000/tradingpal/getAllStocks"

class Main():
    def __init__(self):
        self.DB, self.COLLECTION, self.MONGO_CLIENT = self._connectDb(
            mongoHost, mongoPort, databaseName, collectionName)
        self._testMongoConnection(self.MONGO_CLIENT)
        self.lastFetchedTickerHash = 0
        self.fixIndex()

    def _connectDb(self, mongoHost, mongoPort, databaseName, collectionName):

        dbConnection = MongoClient(host=mongoHost, port=mongoPort)
        db = dbConnection[databaseName]
        collection = db[collectionName]
        return db, collection, dbConnection

    def _testMongoConnection(self, dbConnection):

        try:
            print(f"{datetime.datetime.utcnow()} Mongo connection OK! Version: {dbConnection.server_info()['version']}")
        except Exception as ex:
            raise ValueError(f"{datetime.datetime.utcnow()} Mongo connection FAILED! (B)  {ex}")

    def fixIndex(self):

        print(f"{datetime.datetime.utcnow()} Creating index")
        self.DB[collectionName].create_index([('tickerName', ASCENDING)])
        self.DB[collectionName].create_index([('dateUTC', ASCENDING)])
        self.DB[collectionName].create_index(name='tickerDate', keys=[('tickerName', ASCENDING), ('dateUTC', ASCENDING)])
        print(f"{datetime.datetime.utcnow()} Done (creating index)")

    def fetchTickers(self):

        try:
            retData = requests.get(URL)
            if retData.status_code != 200:
                print(f"{datetime.datetime.utcnow()} Failed to fetch stocks... retrying")
                sys.stdout.flush()
                time.sleep(60)

            dataAsJson = json.loads(retData.content)
            newHash = hash(str(dataAsJson["list"]))


            if self.lastFetchedTickerHash == newHash:
                return None
            else:
                self.lastFetchedTickerHash = newHash
                return dataAsJson

        except Exception as ex:
            print(f"{datetime.datetime.utcnow()} Failed to fetch tickers: {ex}")
            return None

    def writeToMongo(self, tickerData):

        if tickerData is None:
            return

        print(f"{datetime.datetime.utcnow()} Writing data to mongo")
        allElementsForMongo = []

        try:

            for nextTicker in tickerData['list']:
                del(nextTicker['currentStock'])
                nextTicker['dateUTC'] = datetime.datetime.strptime(tickerData['updatedUtc'], '%Y-%m-%d %H:%M:%S.%f')
                allElementsForMongo.append(nextTicker)

            self.COLLECTION.insert_many(allElementsForMongo)
        except Exception as ex:
            print(f"{datetime.datetime.utcnow()} Failed to insert to mongo. ")


    def mainLoop(self):

        print("Starting...")
        sys.stdout.flush()

        while True:
            tickerData = self.fetchTickers()
            self.writeToMongo(tickerData)
            sys.stdout.flush()
            time.sleep(10)



if __name__ == "__main__":
    Main().mainLoop()
