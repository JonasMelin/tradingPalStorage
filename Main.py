from pymongo import ASCENDING, MongoClient
import time
import requests
import json
import datetime
import sys

mongoPort = 27018
mongoHost = "127.0.0.1"
databaseName = "TP"
collectionNameTickers = f"tickers"
collectionNameTransactions = f"transactions"
URLTickers = "http://127.0.0.1:5000/tradingpal/getAllStocks"
URLTransactions = "http://127.0.0.1:5000/tradingpal/getFirstChangeLogItem"

class Main():
    def __init__(self):
        self.DB, self.COLLECTION, self.MONGO_CLIENT = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameTickers)
        self.DBTrans, self.COLLECTIONTrans, self.MONGO_CLIENT_TRANS = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameTransactions)
        self._testMongoConnection(self.MONGO_CLIENT)
        self._testMongoConnection(self.MONGO_CLIENT_TRANS)
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
        self.DB[collectionNameTickers].create_index([('tickerName', ASCENDING)])
        self.DB[collectionNameTickers].create_index([('dateUTC', ASCENDING)])
        self.DB[collectionNameTickers].create_index(name='tickerDate', keys=[('tickerName', ASCENDING), ('dateUTC', ASCENDING)])
        print(f"{datetime.datetime.utcnow()} Done (creating index)")

    def fetchTransactions(self):
        try:
            retData = requests.get(URLTransactions)

            if retData.status_code != 200:
                print(f"{datetime.datetime.utcnow()} Failed to fetch transactions... ")
                sys.stdout.flush()
                time.sleep(60)

            return json.loads(retData.content)

        except Exception as ex:
            print(f"{datetime.datetime.utcnow()} Failed to fetch transactions: {ex}")
            return None

    def fetchTickers(self):

        try:
            retData = requests.get(URLTickers)
            if retData.status_code != 200:
                print(f"{datetime.datetime.utcnow()} Failed to fetch stocks... ")
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

    def writeTransactionsToMongo(self, transactionsData):

        if transactionsData is None or len(transactionsData) == 0:
            return

        try:
            transactionsData['date'] = datetime.datetime.strptime(transactionsData['date'], '%Y-%m-%d %H:%M:%S.%f%z')
            self.COLLECTIONTrans.insert(transactionsData)
        except Exception as ex:
            print(f"{datetime.datetime.utcnow()} Failed to insert transactions to mongo. {ex}")

    def writeTickersToMongo(self, tickerData):

        if tickerData is None:
            return

        print(f"{datetime.datetime.utcnow()} Writing data to mongo")
        allElementsForMongo = []

        try:

            for nextTicker in tickerData['list']:
                del(nextTicker['currentStock'])
                nextTicker['dateUTC'] = datetime.datetime.strptime(tickerData['updatedUtc'], '%Y-%m-%d %H:%M:%S.%f%z')
                allElementsForMongo.append(nextTicker)

            self.COLLECTION.insert_many(allElementsForMongo)
        except Exception as ex:
            print(f"{datetime.datetime.utcnow()} Failed to insert tickers to mongo. {ex}")


    def mainLoop(self):

        print("Starting...")
        sys.stdout.flush()

        while True:
            self.writeTickersToMongo(self.fetchTickers())
            self.writeTransactionsToMongo(self.fetchTransactions())
            sys.stdout.flush()
            time.sleep(10)



if __name__ == "__main__":
    Main().mainLoop()
