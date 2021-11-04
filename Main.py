from pymongo import ASCENDING, MongoClient
import time
import requests
import json
import datetime
import sys
import pytz
import threading
import copy
from flask import Flask, request
import os

PRODUCTION = os.getenv('TP_PROD')

if PRODUCTION is not None and PRODUCTION == "true":
    print("RUNNING IN PRODUCTION MODE!!")
else:
    print("Running in dev mode cause environment variable \"TP_PROD=true\" was not set...")
    PRODUCTION = None

tpIndex = -89999

app = Flask(__name__)

DAY_ZERO = "2021-10-28"
mongoPort = 27018
mongoHost = "192.168.1.50"
databaseName = "TP"
collectionNameTickers = f"tickers"
collectionNameDailyProgress = f"daily"
collectionNameTransactions = f"transactions"
collectionNameFunds = f"funds"
URLTickerCurrentValue = "http://192.168.1.50:5000/tradingpal/getTickerValue"
URLTickers = "http://192.168.1.50:5000/tradingpal/getAllStocks"
URLTransactions = "http://127.0.0.1:5000/tradingpal/getFirstChangeLogItem"

globCollectionTransactions = None
globCollectionDaily = None
globCollectionFunds = None

class Main():

    def __init__(self):
        self.lastFetchedTickerHash = 0
        self.transactionsConnectionOk = False
        self.tickersConnectionOk = False

    def init(self):
        global globCollectionTransactions
        global globCollectionDaily
        global globCollectionFunds

        self.DB, self.COLLECTION, self.MONGO_CLIENT = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameTickers)
        self.DBTrans, self.COLLECTIONTrans, self.MONGO_CLIENT_TRANS = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameTransactions)
        self.DBDaily, self.COLLECTIONDaily, self.MONGO_CLIENT_DAILY = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameDailyProgress)
        self.DBFunds, self.COLLECTIONFunds, self.MONGO_CLIENT_FUNDS = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameFunds)
        globCollectionTransactions = self.COLLECTIONTrans
        globCollectionDaily = self.COLLECTIONDaily
        globCollectionFunds = self.COLLECTIONFunds
        self._testMongoConnection(self.MONGO_CLIENT)
        self.fixIndex()

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
        self.DB[collectionNameFunds].create_index([('day', ASCENDING)], unique=True)

        self.DB[collectionNameTransactions].create_index([('date', ASCENDING)])

        self.DB[collectionNameTickers].create_index([('tickerName', ASCENDING)])
        self.DB[collectionNameTickers].create_index([('dateUTC', ASCENDING)])
        self.DB[collectionNameTickers].create_index(name='tickerDate', keys=[('tickerName', ASCENDING), ('dateUTC', ASCENDING)])
        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Done (creating index)")

    def fetchTransactions(self):

        if PRODUCTION is None:
            return None

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
            if PRODUCTION is not None:
                print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Writing transactions to mongo: {transactionsData}")
                self.COLLECTIONTrans.insert(transactionsData)
                self.updateFundsToMongo(transactionsData['purchaseValueSek'])
        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to insert transactions to mongo. {ex}")

    def updateFundsToMongo(self, purchaseValueSek):

        try:
            if purchaseValueSek != 0:
                print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Updating funds to mongo {purchaseValueSek}")

            fromMongo = None
            for a in range(365):
                fromMongo = self.COLLECTIONFunds.find_one({"day": getDayAsStringDaysBack(a)})
                if fromMongo is not None:
                    break

            fundsSekFromMongo = 0
            putinSekFromMongo = 0
            yieldFromMongo = 0

            if fromMongo is None:
                print("Initializing funds collection in mongo...")
            else:
                fundsSekFromMongo = fromMongo['fundsSek']
                putinSekFromMongo = fromMongo['putinSek']
                yieldFromMongo = fromMongo['yield']

            if PRODUCTION is not None:
                self.COLLECTIONFunds.update_one(
                    {"day": getDayAsStringDaysBack(0)},
                    {"$set":
                        {
                            "fundsSek": fundsSekFromMongo - purchaseValueSek,
                            "putinSek": putinSekFromMongo,
                            "yield": yieldFromMongo
                        }
                    }, upsert=True)

        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to update funds in mongo. {ex}")

    def writeDailyProgressToMongo(self, tickerData):

        if tickerData is None or 'list' not in tickerData:
            return

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Writing daily progress to mongo")

        for nextTicker in (tickerData)['list']:
            try:
                if PRODUCTION is not None:
                    self.COLLECTIONDaily.update_one(
                        {
                            "day": str(datetime.datetime.now(pytz.timezone('Europe/Stockholm')).date()),
                            "ticker": nextTicker['tickerName']
                        },
                        { "$set":
                              {
                                  "count": nextTicker['currentStock']['count'],
                                  "singleStockPriceSek": nextTicker['singleStockPriceSek'],
                                  "name": nextTicker['currentStock']['name'],
                                  "currency": nextTicker['currancy']
                              }
                        }, upsert=True)

            except Exception as ex:
                print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to upsert progress to mongo. {ex}")

    def writeTickersToMongo(self, tickerData):

        if tickerData is None:
            return

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Writing tickers to mongo")
        allElementsForMongo = []

        try:

            for nextTicker in copy.deepcopy(tickerData['list']):
                del(nextTicker['currentStock'])
                nextTicker['dateUTC'] = datetime.datetime.strptime(tickerData['updatedUtc'], '%Y-%m-%d %H:%M:%S.%f%z')
                allElementsForMongo.append(nextTicker)

            if PRODUCTION is not None:
                self.COLLECTION.insert_many(allElementsForMongo)
        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to insert tickers to mongo. {ex}")

    def mainLoop(self):

        global tpIndex
        lastHour = -1
        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Starting...")
        sys.stdout.flush()

        while True:
            self.writeTransactionsToMongo(self.fetchTransactions())
            tickers = self.fetchTickers()
            self.writeTickersToMongo(tickers)
            self.writeDailyProgressToMongo(tickers)

            if datetime.datetime.now().hour != lastHour:
                lastHour = datetime.datetime.now().hour
                self.updateFundsToMongo(0)  # purchase of 0 sek has no impact in Db, but will copy records from yesterday to today
                tpIndex = calcTpIndexSince(DAY_ZERO)

            sys.stdout.flush()
            time.sleep(60)

def getDayAsStringDaysBack(daysback):
    day = datetime.datetime.now(tz=pytz.timezone('Europe/Stockholm')) - datetime.timedelta(days=daysback)
    return  f"{day.year}-{day.month:02}-{day.day:02}"

def getQueryStartEndFullDays(daysback):

    queryDay = datetime.datetime.now(tz=pytz.timezone('Europe/Stockholm')) - datetime.timedelta(days=daysback)
    queryStart = queryDay.replace(hour=0, minute=0, second=0, microsecond=0)
    queryEnd = queryStart + datetime.timedelta(1)
    return queryStart, queryEnd

def getFinancialDiffBetween(startTickersIn, startFunds, endTickersIn, endFunds, onlyCountActiveStocks = True):

    totStartValue = 0
    totEndValue = 0
    startTickers = {}
    for startticker in startTickersIn:
        startTickers[startticker["ticker"]] = startticker

    for endTicker in endTickersIn:
        endTickerName = endTicker['ticker']
        startVal = 0

        if endTickerName not in startTickers:
            if onlyCountActiveStocks:
                continue
        else:
            startVal = startTickers[endTickerName]['count'] * startTickers[endTickerName]['singleStockPriceSek']

        totStartValue += startVal
        totEndValue += endTicker['count'] * endTicker['singleStockPriceSek']

    totStartValue += (startFunds['fundsSek'] if startFunds is not None else 0) - (startFunds['putinSek'] if startFunds is not None else 0)
    totEndValue += (endFunds['fundsSek'] if endFunds is not None else 0) - (endFunds['putinSek'] if endFunds is not None else 0)

    if totStartValue == 0:
        return -99999.9
    else:
        return ((totEndValue / totStartValue) - 1) * 100

def getDevelopmentSinceDate(startDate):
    try:
        stocksAtStart, fundsAtStart = fetchDailyDataFromMongoByDate(startDate)
        stocksToday, fundsToday = fetchDailyDataFromMongo(0, allowCrawlingBack=False)
        stocksYesterday, fundsYesterday = fetchDailyDataFromMongo(1, allowCrawlingBack=True)
        if (len(stocksToday) >= len(stocksYesterday)) and fundsToday is not None:
            stocksNow = stocksToday
            fundsNow = fundsToday
        else:
            stocksNow = stocksYesterday
            fundsNow = fundsYesterday

        return getFinancialDiffBetween(stocksAtStart, fundsAtStart, stocksNow, fundsNow, onlyCountActiveStocks=False)
    except Exception as ex:
        return -88888.8

def getHistoricDevelopment(daysback):
    try:
        stocksDaysBack, fundsDaysBack = fetchDailyDataFromMongo(daysback)
        stocksToday, fundsToday = fetchDailyDataFromMongo(0)

        return getFinancialDiffBetween(stocksDaysBack, fundsDaysBack, stocksToday, fundsToday )
    except Exception as ex:
        return -88888.8

def fetchFundsFromMongo(dayAsString):
    global globCollectionFunds

    try:
        fromMongo = globCollectionFunds.find_one({"day": dayAsString})

        if fromMongo is None:
            print("Funds not found in DB.")

        return fromMongo

    except Exception as ex:
        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Exception when fetching funds from mongo {ex}")
        return None

def fetchDailyDataFromMongoByDate(dayAsString):

    global globCollectionDaily

    hits = globCollectionDaily.find({"day": dayAsString})
    retData = []

    for hit in hits:
        retData.append(hit)

    if len(retData) > 0:
        return retData, fetchFundsFromMongo(dayAsString)


def fetchDailyDataFromMongo(daysback, allowCrawlingBack = True):

    global globCollectionDaily

    for a in range(5 if allowCrawlingBack else 1):
        dayBackToCheck = daysback + a
        dayAsString = getDayAsStringDaysBack(dayBackToCheck)
        hits = globCollectionDaily.find({"day": dayAsString})
        retData = []

        for hit in hits:
            retData.append(hit)

        if len(retData) > 0:
            return retData, fetchFundsFromMongo(dayAsString)

    return [], None

def addCurrentStockValueToStocks(stocks):

    if stocks is None or len(stocks) == 0:
        return

    try:
        for stock in stocks:
            if 'currency' not in stock or 'ticker' not in stock:
                continue

            URL = f"{URLTickerCurrentValue}?currency={stock['currency']}&ticker={stock['ticker']}"
            retData = requests.get(URL)

            if retData.status_code != 200:
                print(f"Failed to get ticker: {URL}")
                continue

            tickerData = json.loads(retData.content)
            stock['priceInSekNow'] = tickerData['price_in_sek']

    except Exception as ex:
        print(f"Error in addCurrentStockValueToStocks(): {ex}")



def calcTpIndexSince(date):
    try:
        startStocks, startFunds = fetchDailyDataFromMongoByDate(date)
        todayStocks, todayFunds = fetchDailyDataFromMongo(1, allowCrawlingBack=True)
        addCurrentStockValueToStocks(startStocks)

        totStartStockValueTodaysCourse = 0
        for stock in startStocks:
            if 'priceInSekNow' not in stock or 'count' not in stock:
                print(f"(a) warn. TpIndex, start stocks could not be looked up in todays value {stock}")
                continue
            totStartStockValueTodaysCourse += stock['priceInSekNow'] * stock['count']

        totTodayStockValue = 0
        for stock in todayStocks:
            if 'singleStockPriceSek' not in stock or 'count' not in stock:
                print(f"(b) warn. Mal formatted entry from mongo {stock}")
                continue
            totTodayStockValue += stock['singleStockPriceSek'] * stock['count']

        totTodayStockValue += todayFunds['fundsSek'] - todayFunds['putinSek'] - todayFunds['yield']
        totStartStockValueTodaysCourse += startFunds['fundsSek'] - startFunds['putinSek'] - startFunds['yield']

        if totStartStockValueTodaysCourse == 0:
            return -99999.9
        else:
            return ((totTodayStockValue / totStartStockValueTodaysCourse) - 1) * 100
    except Exception as ex:
        print(f"Exception in calcTpIndexSince {ex}")
        return -77777


@app.route("/tradingpalstorage/getTpIndex", methods=['GET'])
def getTpIndex():
    global tpIndex
    return {"retval": tpIndex}

@app.route("/tradingpalstorage/getDevelopmentSinceStart", methods=['GET'])
def getDevelopmentSinceStart():
    return {"retval": getDevelopmentSinceDate(DAY_ZERO)}

@app.route("/tradingpalstorage/getDevelopmentSinceDaysBack", methods=['GET'])
def getDevelopmentSinceDaysBack():
    return {"retval": getHistoricDevelopment(int(request.args.get("daysback")))}

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
    main.init()
    threading.Thread(target=main.mainLoop).start()
    app.run(host='0.0.0.0', port=5001)
