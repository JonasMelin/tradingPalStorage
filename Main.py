from pymongo import ASCENDING, MongoClient
import time
import requests
import json
import datetime
import sys
import pytz
import threading
from flask import Flask, request

app = Flask(__name__)

mongoPort = 27018
mongoHost = "192.168.1.50"
databaseName = "TP"
collectionNameTickers = f"tickers"
collectionNameDailyProgress = f"daily"
collectionNameTransactions = f"transactions"
URLTickers = "http://192.168.1.50:5000/tradingpal/getAllStocks"
URLTransactions = "http://192.168.1.50:5000/tradingpal/getFirstChangeLogItem"

globCollectionTransactions = None

class Main():
    def __init__(self):
        global globCollectionTransactions
        self.DB, self.COLLECTION, self.MONGO_CLIENT = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameTickers)
        self.DBTrans, self.COLLECTIONTrans, self.MONGO_CLIENT_TRANS = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameTransactions)
        self.DBDaily, self.COLLECTIONDaily, self.MONGO_CLIENT_DAILY = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameDailyProgress)
        globCollectionTransactions = self.COLLECTIONTrans
        self._testMongoConnection(self.MONGO_CLIENT)
        self._testMongoConnection(self.MONGO_CLIENT_TRANS)
        self._testMongoConnection(self.MONGO_CLIENT_DAILY)
        self.lastFetchedTickerHash = 0
        self.fixIndex()
        self.transactionsConnectionOk = False
        self.tickersConnectionOk = False

    def _connectDb(self, mongoHost, mongoPort, databaseName, collectionName):

        dbConnection = MongoClient(host=mongoHost, port=mongoPort)
        db = dbConnection[databaseName]
        collection = db[collectionName]
        return db, collection, dbConnection

    def _testMongoConnection(self, dbConnection):

        try:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Mongo connection OK! Version: {dbConnection.server_info()['version']}")
        except Exception as ex:
            raise ValueError(f"{datetime.datetime.utcnow()} Mongo connection FAILED! (B)  {ex}")

    def fixIndex(self):

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Creating index")

        self.DB[collectionNameDailyProgress].create_index([('day', ASCENDING), ('ticker', ASCENDING)], unique=True)

        self.DB[collectionNameTransactions].create_index([('date', ASCENDING)])

        self.DB[collectionNameTickers].create_index([('tickerName', ASCENDING)])
        self.DB[collectionNameTickers].create_index([('dateUTC', ASCENDING)])
        self.DB[collectionNameTickers].create_index(name='tickerDate', keys=[('tickerName', ASCENDING), ('dateUTC', ASCENDING)])
        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Done (creating index)")

    def fetchTransactions(self):
        try:
            retData = requests.get(URLTransactions)

            if retData.status_code != 200:
                print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to fetch transactions... ")
                sys.stdout.flush()
                time.sleep(60)

            if not self.transactionsConnectionOk:
                print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Connection to tradingpal to fetch transactions OK")
                self.transactionsConnectionOk = True

            return json.loads(retData.content)

        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to fetch transactions: {ex}")
            return None

    def fetchTickers(self):

        try:
            retData = requests.get(URLTickers)
            if retData.status_code != 200:
                print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to fetch stocks... ")
                sys.stdout.flush()
                time.sleep(60)

            if not self.tickersConnectionOk:
                print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Connection to tradingpal to fetch tickers OK")
                self.tickersConnectionOk = True

            dataAsJson = json.loads(retData.content)
            newHash = hash(str(dataAsJson["list"]))


            if self.lastFetchedTickerHash == newHash:
                return None
            else:
                self.lastFetchedTickerHash = newHash
                return dataAsJson

        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to fetch tickers: {ex}")
            return None

    def writeTransactionsToMongo(self, transactionsData):

        if transactionsData is None or len(transactionsData) == 0:
            return

        try:
            transactionsData['date'] = datetime.datetime.strptime(transactionsData['date'], '%Y-%m-%d %H:%M:%S.%f%z')
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Writing transactions to mongo: {transactionsData}")
            self.COLLECTIONTrans.insert(transactionsData)
        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to insert transactions to mongo. {ex}")

    def writeDailyProgressToMongo(self, tickerData):

        if tickerData is None or 'list' not in tickerData:
            return

        for nextTicker in (tickerData)['list']:
            try:
                if not nextTicker['marketOpen']:
                    continue

                entry = {
                    "ticker": nextTicker['tickerName'],
                    "name": nextTicker['currentStock']['name'],
                    "day": str(datetime.datetime.now(pytz.timezone('Europe/Stockholm')).date()),
                    "count": nextTicker['currentStock']['count'],
                    "singleStockPriceSek": nextTicker['singleStockPriceSek']
                }
                self.COLLECTIONDaily.update_one(
                    {"day": entry["day"], "ticker": entry['ticker']},
                    { "$set":
                          {
                              "count": entry["count"],
                              "singleStockPriceSek": entry["singleStockPriceSek"],
                              "name": entry["name"]
                          }
                    }, upsert=True)

            except Exception as ex:
                pass

    def writeTickersToMongo(self, tickerData):

        if tickerData is None:
            return

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Writing tickers to mongo")
        allElementsForMongo = []

        try:

            for nextTicker in tickerData['list']:
                del(nextTicker['currentStock'])
                nextTicker['dateUTC'] = datetime.datetime.strptime(tickerData['updatedUtc'], '%Y-%m-%d %H:%M:%S.%f%z')
                allElementsForMongo.append(nextTicker)

            self.COLLECTION.insert_many(allElementsForMongo)
        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to insert tickers to mongo. {ex}")

    def mainLoop(self):

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Starting...")
        sys.stdout.flush()

        while True:
            tickers = self.fetchTickers()
            self.writeTickersToMongo(tickers)
            self.writeDailyProgressToMongo(tickers)
            self.writeTransactionsToMongo(self.fetchTransactions())
            sys.stdout.flush()
            time.sleep(60)

def getQueryStartEndFullDays(daysback):

    queryDay = datetime.datetime.now(tz=pytz.timezone('Europe/Stockholm')) - datetime.timedelta(days=daysback)
    queryStart = queryDay.replace(hour=0, minute=0, second=0, microsecond=0)
    queryEnd = queryStart + datetime.timedelta(1)
    return queryStart, queryEnd

@app.route("/tradingpalstorage/getTransactionsLastDays", methods=['GET'])
def getTransactionsLastDays():
    global globCollectionTransactions

    try:
        daysback = int(request.args.get("daysback"))
        queryStart, queryEnd = getQueryStartEndFullDays(daysback)
        hits = globCollectionTransactions.find({"date": {"$gte": queryStart, "$lte": queryEnd}})

        retval = []
        for hit in hits:
            del(hit['_id'])
            hit['date'] = str(hit['date'])
            retval.append(hit)

        return {"retval": retval}
    except Exception as ex:
        errorMsg = (f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))}. getTransactionsLastDays: Could not fetch data from mongo, {ex}")
        print(errorMsg)
        return errorMsg

@app.route("/tradingpalstorage/getTurnoverLastDays", methods=['GET'])
def getStatsLastDays():
    global globCollectionTransactions

    try:
        daysback = int(request.args.get("daysback"))
        _, queryEnd = getQueryStartEndFullDays(0)
        queryStart, _ = getQueryStartEndFullDays(daysback)

        hits = globCollectionTransactions.find({"date": {"$gte": queryStart, "$lte": queryEnd}})

        sold = 0
        bought = 0
        for hit in hits:
            bought += hit['purchaseValueSek'] if hit['purchaseValueSek'] > 0 else 0
            sold += -hit['purchaseValueSek'] if hit['purchaseValueSek'] < 0 else 0

        return {
            "retval": {
                "soldForSek": sold,
                "boughtForSek": bought
            }
        }
    except Exception as ex:
        errorMsg = (f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))}. getTurnoverLastDays: Could not fetch data from mongo, {ex}")
        print(errorMsg)
        return errorMsg

if __name__ == "__main__":

    main = Main()
    threading.Thread(target=main.mainLoop).start()
    app.run(host='0.0.0.0', port=5001)
