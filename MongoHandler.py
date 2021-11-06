from pymongo import ASCENDING, MongoClient
import time, requests, json, datetime, sys, pytz, copy, os

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

class MongoHandler():

    def __init__(self):
        self.tpIndex = -89999
        self.tpIndexTrend = 0
        self.tpIndexLast = 0
        self.developmentSinceDateLast = -89999
        self.developmentSinceLastTrend = 0
        self.developmentSinceDaysBack = {}
        self.lastFetchedTickerHash = 0
        self.transactionsConnectionOk = False
        self.tickersConnectionOk = False

    def init(self):

        self.PRODUCTION = os.getenv('TP_PROD')

        if self.PRODUCTION is not None and self.PRODUCTION == "true":
            print("RUNNING IN PRODUCTION MODE!!")
        else:
            print("Running in dev mode cause environment variable \"TP_PROD=true\" was not set...")
            self.PRODUCTION = None


        self.DB, self.COLLECTION, self.MONGO_CLIENT = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameTickers)
        self.DBTrans, self.COLLECTIONTrans, self.MONGO_CLIENT_TRANS = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameTransactions)
        self.DBDaily, self.COLLECTIONDaily, self.MONGO_CLIENT_DAILY = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameDailyProgress)
        self.DBFunds, self.COLLECTIONFunds, self.MONGO_CLIENT_FUNDS = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameFunds)
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

        if self.PRODUCTION is None:
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
            if self.PRODUCTION is not None:
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
                fromMongo = self.COLLECTIONFunds.find_one({"day": self.getDayAsStringDaysBack(a)})
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

            if self.PRODUCTION is not None:
                self.COLLECTIONFunds.update_one(
                    {"day": self.getDayAsStringDaysBack(0)},
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
                if self.PRODUCTION is not None:
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

            if self.PRODUCTION is not None:
                self.COLLECTION.insert_many(allElementsForMongo)
        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to insert tickers to mongo. {ex}")

    def getDayAsStringDaysBack(self, daysback):

        day = datetime.datetime.now(tz=pytz.timezone('Europe/Stockholm')) - datetime.timedelta(days=daysback)
        return  f"{day.year}-{day.month:02}-{day.day:02}"

    def getQueryStartEndFullDays(self, daysback):

        queryDay = datetime.datetime.now(tz=pytz.timezone('Europe/Stockholm')) - datetime.timedelta(days=daysback)
        queryStart = queryDay.replace(hour=0, minute=0, second=0, microsecond=0)
        queryEnd = queryStart + datetime.timedelta(1)
        return queryStart, queryEnd

    def getFinancialDiffBetween(self, startTickersIn, startFunds, endTickersIn, endFunds, onlyCountActiveStocks = True):

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

    def getDevelopmentSinceDate(self, startDate):

        try:
            stocksAtStart, fundsAtStart = self.fetchDailyDataFromMongoByDate(startDate)
            stocksToday, fundsToday = self.fetchDailyDataFromMongo(0, allowCrawlingBack=False)
            stocksYesterday, fundsYesterday = self.fetchDailyDataFromMongo(1, allowCrawlingBack=True)
            if (len(stocksToday) >= len(stocksYesterday)) and fundsToday is not None:
                stocksNow = stocksToday
                fundsNow = fundsToday
            else:
                stocksNow = stocksYesterday
                fundsNow = fundsYesterday

            return self.getFinancialDiffBetween(stocksAtStart, fundsAtStart, stocksNow, fundsNow, onlyCountActiveStocks=False)
        except Exception as ex:
            return -88888.8

    def getHistoricDevelopment(self, daysback):

        try:
            stocksDaysBack, fundsDaysBack = self.fetchDailyDataFromMongo(daysback)
            stocksToday, fundsToday = self.fetchDailyDataFromMongo(0)

            return self.getFinancialDiffBetween(stocksDaysBack, fundsDaysBack, stocksToday, fundsToday )
        except Exception as ex:
            return -88888.8

    def fetchFundsFromMongo(self, dayAsString):

        try:
            fromMongo = self.COLLECTIONFunds.find_one({"day": dayAsString})

            if fromMongo is None:
                print("Funds not found in DB.")

            return fromMongo

        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Exception when fetching funds from mongo {ex}")
            return None

    def fetchDailyDataFromMongoByDate(self, dayAsString):

        hits = self.COLLECTIONDaily.find({"day": dayAsString})
        retData = []

        for hit in hits:
            retData.append(hit)

        if len(retData) > 0:
            return retData, self.fetchFundsFromMongo(dayAsString)


    def fetchDailyDataMostRecent(self):

        MAX_DAYS_BACK = 5

        retData = {}
        latestFunds = None

        for a in range(MAX_DAYS_BACK):
            dayBackToCheck = MAX_DAYS_BACK - a - 1
            dayAsString = self.getDayAsStringDaysBack(dayBackToCheck)
            hits = self.COLLECTIONDaily.find({"day": dayAsString})


            for hit in hits:
                retData[hit['ticker']] = hit

            if len(retData) > 0:
                latestFunds = self.fetchFundsFromMongo(dayAsString)

        return list(retData.values()), latestFunds


    def fetchDailyDataFromMongo(self, daysback, allowCrawlingBack = True):

        for a in range(5 if allowCrawlingBack else 1):
            dayBackToCheck = daysback + a
            dayAsString = self.getDayAsStringDaysBack(dayBackToCheck)
            hits = self.COLLECTIONDaily.find({"day": dayAsString})
            retData = []

            for hit in hits:
                retData.append(hit)

            if len(retData) > 0:
                return retData, self.fetchFundsFromMongo(dayAsString)

        return [], None

    def addCurrentStockValueToStocks(self, stocks):

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

    def calcTpIndexSince(self, date):

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} calcTpIndexSince...")

        if date is None:
            return -999889

        try:
            startStocks, startFunds = self.fetchDailyDataFromMongoByDate(date)
            todayStocks, todayFunds = self.fetchDailyDataMostRecent()
            self.addCurrentStockValueToStocks(startStocks)

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

    def getTpIndexWithTrend(self):

        if self.tpIndex > self.tpIndexLast:
            self.tpIndexTrend = 1
        elif self.tpIndex < self.tpIndexLast:
            self.tpIndexTrend = -1

        self.tpIndexLast = self.tpIndex

        return self.tpIndex, self.tpIndexTrend

    def getDevelopmentWithTrend(self, daysback):

        if daysback is None or daysback < 0:
            return -1, 0

        if daysback not in self.developmentSinceDaysBack:
            self.developmentSinceDaysBack[daysback] = {"lastRetVal": -89999, "trend": 0}

        newRetVal = self.getHistoricDevelopment(daysback)
        historicalData = self.developmentSinceDaysBack[daysback]

        if newRetVal > historicalData["lastRetVal"]:
            historicalData["trend"] = 1
        elif newRetVal < historicalData["lastRetVal"]:
            historicalData["trend"] = -1

        historicalData["lastRetVal"] = newRetVal

        return newRetVal, historicalData["trend"]

    def getDevelopmentSinceStartWithTrend(self):

        newRetVal = self.getDevelopmentSinceDate(DAY_ZERO)

        if newRetVal > self.developmentSinceDateLast:
            self.developmentSinceLastTrend = 1
        elif newRetVal < self.developmentSinceDateLast:
            self.developmentSinceLastTrend = -1

        self.developmentSinceDateLast = newRetVal

        return newRetVal, self.developmentSinceLastTrend

    def getTransactionsLastDays(self, daysback):

        retval = []

        if daysback is None or daysback < 0:
            return retval

        try:
            queryStart, queryEnd = self.getQueryStartEndFullDays(daysback)
            hits = self.COLLECTIONTrans.find({"date": {"$gte": queryStart, "$lte": queryEnd}})

            for hit in hits:
                del (hit['_id'])
                hit['date'] = str(hit['date'])
                retval.append(hit)

            return retval

        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))}. getTransactionsLastDays: Could not fetch data from mongo, {ex}")
            return retval

    def getStatsLastDays(self, daysback):

        if daysback is None or daysback < 0:
            return -99999, -99999

        try:
            _, queryEnd = self.getQueryStartEndFullDays(0)
            queryStart, _ = self.getQueryStartEndFullDays(daysback)

            hits = self.COLLECTIONTrans.find({"date": {"$gte": queryStart, "$lte": queryEnd}})

            sold = 0
            bought = 0
            for hit in hits:
                bought += hit['purchaseValueSek'] if hit['purchaseValueSek'] > 0 else 0
                sold += -hit['purchaseValueSek'] if hit['purchaseValueSek'] < 0 else 0

            return sold, bought
        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))}. getTurnoverLastDays: Could not fetch data from mongo, {ex}")
            return None

    def mainLoop(self):

        lastHour = -1
        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Starting...")
        sys.stdout.flush()

        while True:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Running...")
            self.writeTransactionsToMongo(self.fetchTransactions())
            tickers = self.fetchTickers()
            self.writeTickersToMongo(tickers)
            self.writeDailyProgressToMongo(tickers)

            if datetime.datetime.now().hour != lastHour:
                lastHour = datetime.datetime.now().hour
                self.updateFundsToMongo(0)  # purchase of 0 sek has no impact in Db, but will copy records from yesterday to today
                self.tpIndex = self.calcTpIndexSince(DAY_ZERO)

            sys.stdout.flush()
            time.sleep(60)