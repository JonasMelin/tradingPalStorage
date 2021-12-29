import time, requests, json, datetime, sys, pytz, copy, DbAccess

DAY_ZERO = "2021-10-28"
URLTickerCurrentValue = "http://192.168.1.50:5000/tradingpal/getTickerValue"
URLTickers = "http://192.168.1.50:5000/tradingpal/getAllStocks"
URLTransactions = "http://127.0.0.1:5000/tradingpal/getFirstChangeLogItem"
URLFunds = "http://192.168.1.50:5002/tradingpalavanza/getfunds"
URLTaxes = "http://192.168.1.50:5002/tradingpalavanza/gettax"
URLYield = "http://192.168.1.50:5002/tradingpalavanza/getyield"
URLRegisterNewStock = "http://127.0.0.1:5000/tradingpal/registerNewStock"

FUND_THRESH_INVEST_IN_NEW_STOCKS_SEK = 500

class MetricHandler():

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def __init__(self):
        self.switchAndTransactionMetrics = {"correctSwitched": -1,
                "incorrectSwitched": -1,
                "correctLastTransaction": -1,
                "incorrectLastTransaction": -1,
                "ignored": -1}

        self.tpIndexByMonth = []
        self.tpIndex = -89999
        self.tpIndexTrend = 0
        self.tpIndexLast = 0
        self.developmentSinceDateLast = -89999
        self.developmentSinceLastTrend = 0
        self.developmentSinceDaysBack = {}
        self.lastFetchedTickerHash = 0
        self.transactionsConnectionOk = False
        self.tickersConnectionOk = False
        self.dbAccess = None

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def init(self):
        self.dbAccess = DbAccess.DbAccess()
        self.dbAccess.init()
        return self

    # ##############################################################################################################
    # Tested!
    # ##############################################################################################################
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

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
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

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def writeTransactionsToMongo(self, transactionsData: dict):

        if transactionsData is None or len(transactionsData) == 0:
            return

        try:
            transactionsData['date'] = datetime.datetime.strptime(transactionsData['date'], '%Y-%m-%d %H:%M:%S.%f%z')
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Writing transactions to mongo: {transactionsData}")
            self.dbAccess.insert_one(transactionsData, DbAccess.Collection.Transactions)
            self.updateFundsToMongo(transactionsData['purchaseValueSek'])
        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to insert transactions to mongo. {ex}")

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def updateFundsToMongo(self, purchaseValueSek: int):

        try:
            if purchaseValueSek != 0:
                print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Updating funds to mongo {purchaseValueSek}")

            fromMongo = self.dbAccess.find_one_sort_by(("day", -1), DbAccess.Collection.Funds)

            fundsSekFromMongo = 0
            putinSekFromMongo = 0
            yieldFromMongo = 0
            yieldTaxFromMongo = 0
            tpIndex = self.tpIndex if self.tpIndex > -1000 else 0.0

            if fromMongo is None:
                print("Initializing funds collection in mongo...")
            else:
                fundsSekFromMongo = fromMongo['fundsSek'] if 'fundsSek' in fromMongo else 0
                putinSekFromMongo = fromMongo['putinSek'] if 'putinSek' in fromMongo else 0
                yieldFromMongo = fromMongo['yield'] if 'yield' in fromMongo else 0
                yieldTaxFromMongo = fromMongo['yieldTax'] if 'yieldTax' in fromMongo else 0
                if 'tpIndex' in fromMongo:
                    tpIndex = self.tpIndex if self.tpIndex > -1000 else fromMongo['tpIndex']

            yieldFromMongo += self.getNewYieldFromAvanza()
            yieldTaxFromMongo += self.getNewTaxFromAvanza()
            fundsFromAvanza = requests.get(URLFunds)

            if fundsFromAvanza.status_code == 200 and fundsFromAvanza.content is not None:
                fundsSek = int(json.loads(fundsFromAvanza.content)['funds'])
            else:
                print("Failed to fetch funds from tradingpalAvanza. Calculating manually...")
                fundsSek = fundsSekFromMongo - purchaseValueSek

            self.dbAccess.update_one(
                {"day": self.getDayAsStringDaysBackFromToday(0)},
                {"$set":
                    {
                        "fundsSek": fundsSek,
                        "putinSek": putinSekFromMongo,
                        "yield": yieldFromMongo,
                        "yieldTax": yieldTaxFromMongo,
                        "tpIndex": tpIndex
                    }
                },
                DbAccess.Collection.Funds)

        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to update funds in mongo. {ex}")

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def checkInvestNewStocks(self):

        try:
            fromMongo = self.dbAccess.find_one_sort_by(("day", -1), DbAccess.Collection.Funds)

            if fromMongo is None or 'fundsSek' not in fromMongo or fromMongo['fundsSek'] < FUND_THRESH_INVEST_IN_NEW_STOCKS_SEK:
                return

            nextNewStock = self.dbAccess.find_one_sort_by(("prio", 1), DbAccess.Collection.NewStocks)

            _id = nextNewStock['_id']
            del(nextNewStock['_id'])

            if nextNewStock is None or "ticker" not in nextNewStock:
                print(f"Warning: No new stocks found to buy in collection {DbAccess.Collection.NewStocks}")
                return

            retData = requests.post(URLRegisterNewStock, json=nextNewStock)

            if retData.status_code != 200:
                print(f"Failed to register new stock: {nextNewStock}, {retData.content}")
                return

            self.dbAccess.delete_by_id(_id, DbAccess.Collection.NewStocks)
        except Exception as ex:
            print(f"Exception during checkInvestNewStocks: {ex}")



    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getNewYieldFromAvanza(self):
        newYield = 0
        rawYieldFromAvanza = requests.get(URLYield)

        if rawYieldFromAvanza.status_code != 200 or rawYieldFromAvanza.content is None:
            print("Problems getting yield from avanzaHAndler...")
            return 0

        jsonLoadedRawYield = json.loads(rawYieldFromAvanza.content)

        if "yields" not in jsonLoadedRawYield or len(jsonLoadedRawYield['yields']) == 0:
            return 0

        for nextYield in jsonLoadedRawYield['yields']:

            try:
                self.dbAccess.insert_one(nextYield, DbAccess.Collection.Yields)
                newYield += nextYield['amount']
            except Exception:
                # Will throw upon duplicate key errors, i.e. each yield only counted once ever...
                pass

        return int(newYield)

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getNewTaxFromAvanza(self):
        newTax = 0
        rawTaxFromAvanza = requests.get(URLTaxes)

        if rawTaxFromAvanza.status_code != 200 or rawTaxFromAvanza.content is None:
            print("Problems getting taxes from avanzaHAndler...")
            return 0

        jsonLoadedRawTax = json.loads(rawTaxFromAvanza.content)

        if "taxes" not in jsonLoadedRawTax or len(jsonLoadedRawTax['taxes']) == 0:
            return 0

        for nextTax in jsonLoadedRawTax['taxes']:

            try:
                self.dbAccess.insert_one(nextTax, DbAccess.Collection.Tax)
                newTax += nextTax['amount']
            except Exception:
                # Will throw upon duplicate key errors, i.e. each tax only counted once ever...
                pass

        return -int(newTax)


    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def writeDailyProgressToMongo(self, tickerData: dict):

        if tickerData is None or 'list' not in tickerData:
            return

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Writing daily progress to mongo")

        for nextTicker in (tickerData)['list']:
            try:
                self.dbAccess.update_one(
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
                    },
                    DbAccess.Collection.DailyProgress)

            except Exception as ex:
                print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to upsert progress to mongo. {ex}")

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def writeTickersToMongo(self, tickerData: dict):

        if tickerData is None:
            return

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Writing tickers to mongo")
        allElementsForMongo = []

        try:

            for nextTicker in copy.deepcopy(tickerData['list']):
                del(nextTicker['currentStock'])
                nextTicker['dateUTC'] = datetime.datetime.strptime(tickerData['updatedUtc'], '%Y-%m-%d %H:%M:%S.%f%z')
                allElementsForMongo.append(nextTicker)

            self.dbAccess.insert_many(allElementsForMongo, DbAccess.Collection.Tickers)
        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Failed to insert tickers to mongo. {ex}")

    # ##############################################################################################################
    #
    # ##############################################################################################################
    def getTodayAsString(self):
        return self.getDateAsStringDaysBack(datetime.datetime.now(tz=pytz.timezone('Europe/Stockholm')), 0)

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getDayAsStringDaysBackFromToday(self, daysback: int):
        return self.getDateAsStringDaysBack(datetime.datetime.now(tz=pytz.timezone('Europe/Stockholm')), daysback)

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getDateAsStringDaysBack(self, date: datetime, daysback: int):
        day = date - datetime.timedelta(days=daysback)
        return self.getDateAsString(day)

    # ##############################################################################################################
    # 
    # ##############################################################################################################
    def getDateAsString(self, date: datetime):
        return f"{date.year}-{date.month:02}-{date.day:02}"

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def dayStringToDatetime(self, stringDate):
        return datetime.datetime.strptime(stringDate, '%Y-%m-%d')

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getQueryStartEndFullDays(self, daysback: int):

        queryDay = datetime.datetime.now(tz=pytz.timezone('Europe/Stockholm')) - datetime.timedelta(days=daysback)
        queryStart = queryDay.replace(hour=0, minute=0, second=0, microsecond=0)
        queryEnd = queryStart + datetime.timedelta(1)
        return queryStart, queryEnd

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getFinancialDiffBetween(self, startTickersIn, startFunds, endTickersIn, endFunds, onlyCountActiveStocks = True):

        if startTickersIn is None or startFunds is None or endTickersIn is None or endFunds is None:
            return -888888.8

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
            if 'priceInSekNow' in endTicker:
                totEndValue += endTicker['count'] * endTicker['priceInSekNow']
            else:
                totEndValue += endTicker['count'] * endTicker['singleStockPriceSek']

        totStartValue += (startFunds['fundsSek'] if startFunds is not None else 0) - (startFunds['putinSek'] if startFunds is not None else 0)
        totEndValue += (endFunds['fundsSek'] if endFunds is not None else 0) - (endFunds['putinSek'] if endFunds is not None else 0)

        if totStartValue == 0:
            return -99999.9
        else:
            return ((totEndValue / totStartValue) - 1) * 100

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getDevelopmentSinceDate(self, startDate):

        try:
            stocksAtStart, fundsAtStart = self.fetchDailyDataFromMongoByDate(startDate)
            stocksMostRecent, fundsMostResent = self.fetchDailyDataMostRecent(self.getTodayAsString())
            self.addCurrentStockValueToStocks(stocksMostRecent)

            return self.getFinancialDiffBetween(stocksAtStart, fundsAtStart, stocksMostRecent, fundsMostResent, onlyCountActiveStocks=False)
        except Exception as ex:
            return -88888.8

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getHistoricDevelopment(self, daysback):

        try:
            stocksDaysBack, fundsDaysBack = self.fetchDailyDataFromMongo(daysback, allowCrawlingBack=True)
            stocksToday, fundsToday = self.fetchDailyDataFromMongo(0)
            self.addCurrentStockValueToStocks(stocksToday)

            return self.getFinancialDiffBetween(stocksDaysBack, fundsDaysBack, stocksToday, fundsToday, onlyCountActiveStocks=False)
        except Exception as ex:
            return -88888.8

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def fetchFundsFromMongo(self, dayAsString):

        try:
            fromMongo = self.dbAccess.find_one({"day": dayAsString}, DbAccess.Collection.Funds)

            if fromMongo is None:
                print("Funds not found in DB.")

            return fromMongo

        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Exception when fetching funds from mongo {ex}")
            return None

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def fetchDailyDataFromMongoByDate(self, dayAsString, allowCrawlingBack = False):

        for a in range(15 if allowCrawlingBack else 1):
            nextDateToCheck = self.getDateAsStringDaysBack(self.dayStringToDatetime(dayAsString), a)
            hits = self.dbAccess.find({"day": nextDateToCheck}, DbAccess.Collection.DailyProgress)
            retData = []

            for hit in hits:
                retData.append(hit)

            if len(retData) > 0:
                return retData, self.fetchFundsFromMongo(dayAsString)

        return None, None



    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def fetchDailyDataMostRecent(self, dayAsString: str):

        MAX_DAYS_BACK = 5

        retData = {}
        latestFunds = None

        for a in range(MAX_DAYS_BACK):
            dayBackToCheck = MAX_DAYS_BACK - a - 1
            dayToCheck = self.getDateAsStringDaysBack(self.dayStringToDatetime(dayAsString), dayBackToCheck)
            hits = self.dbAccess.find({"day": dayToCheck}, DbAccess.Collection.DailyProgress)


            for hit in hits:
                retData[hit['ticker']] = hit

            if len(retData) > 0:
                latestFunds = self.fetchFundsFromMongo(dayAsString)

        return list(retData.values()), latestFunds

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def fetchDailyDataFromMongo(self, daysback, allowCrawlingBack = True):

        for a in range(5 if allowCrawlingBack else 1):
            dayBackToCheck = daysback + a
            dayAsString = self.getDayAsStringDaysBackFromToday(dayBackToCheck)
            hits = self.dbAccess.find({"day": dayAsString}, DbAccess.Collection.DailyProgress)
            retData = []

            for hit in hits:
                retData.append(hit)

            if len(retData) > 0:
                return retData, self.fetchFundsFromMongo(dayAsString)

        return [], None

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
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

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def calcTpIndexSince(self, startDate: str, endDate: str, sampleSingleStartDate = True, sampleSingleEndDate = True):

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} calcTpIndexFrom {startDate} to {endDate}")

        if startDate is None or endDate is None:
            return 0.0, -999889

        try:
            if sampleSingleStartDate:
                startStocks, startFunds = self.fetchDailyDataFromMongoByDate(dayAsString=startDate, allowCrawlingBack=True)
            else:
                startStocks, startFunds = self.fetchDailyDataMostRecent(dayAsString=startDate)

            if sampleSingleEndDate:
                todayStocks, todayFunds = self.fetchDailyDataFromMongoByDate(dayAsString=endDate, allowCrawlingBack=True)
            else:
                todayStocks, todayFunds = self.fetchDailyDataMostRecent(dayAsString=endDate)

            self.addCurrentStockValueToStocks(startStocks)
            self.addCurrentStockValueToStocks(todayStocks)

            totStartStockValueTodaysCourse = 0
            for stock in startStocks:
                if 'priceInSekNow' not in stock or 'count' not in stock:
                    print(f"(a) warn. TpIndex, start stocks could not be looked up in todays value {stock}")
                    return 0.0, -1
                totStartStockValueTodaysCourse += stock['priceInSekNow'] * stock['count']

            totTodayStockValue = 0
            for stock in todayStocks:
                if 'singleStockPriceSek' not in stock or 'count' not in stock:
                    print(f"(b) warn. Mal formatted entry from mongo {stock}")
                    return 0.0, -1
                totTodayStockValue += stock['priceInSekNow'] * stock['count']

            totTodayStockValue += todayFunds['fundsSek'] - todayFunds['putinSek'] - todayFunds['yield'] + todayFunds['yieldTax']
            totStartStockValueTodaysCourse += startFunds['fundsSek'] - startFunds['putinSek'] - startFunds['yield'] + startFunds['yieldTax']

            if totStartStockValueTodaysCourse == 0:
                return 0.0, -99999.9
            else:
                return ((totTodayStockValue / totStartStockValueTodaysCourse) - 1) * 100, 0
        except Exception as ex:
            print(f"Exception in calcTpIndexSince {ex}")
            return 0.0, -77777

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def getTpIndexByMonth(self):
        return self.tpIndexByMonth

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getTpIndexWithTrend(self):

        if self.tpIndex > self.tpIndexLast:
            self.tpIndexTrend = 1
        elif self.tpIndex < self.tpIndexLast:
            self.tpIndexTrend = -1

        self.tpIndexLast = self.tpIndex

        return self.tpIndex, self.tpIndexTrend

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
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

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getDevelopmentSinceStartWithTrend(self):

        newRetVal = self.getDevelopmentSinceDate(DAY_ZERO)

        if newRetVal > self.developmentSinceDateLast:
            self.developmentSinceLastTrend = 1
        elif newRetVal < self.developmentSinceDateLast:
            self.developmentSinceLastTrend = -1

        self.developmentSinceDateLast = newRetVal

        return newRetVal, self.developmentSinceLastTrend

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getTransactionsLastDays(self, daysback):

        retval = []

        if daysback is None or daysback < 0:
            return retval

        try:
            queryStart, queryEnd = self.getQueryStartEndFullDays(daysback)
            hits = self.dbAccess.find({"date": {"$gte": queryStart, "$lte": queryEnd}}, DbAccess.Collection.Transactions)

            for hit in hits:
                del (hit['_id'])
                hit['date'] = str(hit['date'])
                retval.append(hit)

            return retval

        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))}. getTransactionsLastDays: Could not fetch data from mongo, {ex}")
            return retval

    # ##############################################################################################################
    # Tested
    # ##############################################################################################################
    def getStatsLastDays(self, daysback):

        if daysback is None or daysback < 0:
            return -99999, -99999

        try:
            _, queryEnd = self.getQueryStartEndFullDays(0)
            queryStart, _ = self.getQueryStartEndFullDays(daysback)

            hits = self.dbAccess.find({"date": {"$gte": queryStart, "$lte": queryEnd}}, DbAccess.Collection.Transactions)

            sold = 0
            bought = 0
            for hit in hits:
                if hit['tradedByBot']:
                    bought += hit['purchaseValueSek'] if hit['purchaseValueSek'] > 0 else 0
                    sold += -hit['purchaseValueSek'] if hit['purchaseValueSek'] < 0 else 0

            return sold, bought
        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))}. getTurnoverLastDays: Could not fetch data from mongo, {ex}")
            return None

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def getTpIndexesByMonth(self):
        DAY_STEPPING = 30

        sampleSingleEndDate = True
        today = self.dayStringToDatetime(self.getTodayAsString())
        startDate = self.dayStringToDatetime(DAY_ZERO)
        endDate = self.dayStringToDatetime(DAY_ZERO) + datetime.timedelta(days=DAY_STEPPING)
        monthlyResult = []
        totDays = 0

        while True:

            if self.getDateAsString(endDate) >= self.getDateAsString(today):
                endDate = today
                sampleSingleEndDate = False # Today, then sample stocks from last updated

            delta = (endDate - startDate).days

            if delta < 1:
                break

            tpIndex = self.calcTpIndexSince(self.getDateAsString(startDate), self.getDateAsString(endDate), sampleSingleStartDate=True, sampleSingleEndDate=sampleSingleEndDate)[0]
            monthlyResult.append({"tpIMonth": tpIndex, "deltaDays": delta, "dayStepping": DAY_STEPPING, "startDate": startDate, "endDate": endDate})
            totDays += delta

            endDate = endDate + datetime.timedelta(days=DAY_STEPPING)
            startDate = startDate + datetime.timedelta(days=DAY_STEPPING)

        tpIndexSummed = self.sumUpMonthlyTpIndexes(monthlyResult)

        return {
            "monthlyResult": monthlyResult, "descrMonthlyResult": "Calculated tpIndexes for every month since DAY_ZERO",
            "tpIndexSummed": tpIndexSummed,  "descrTpIndexSummed": "Summing up the total tpIndex from DAY_ZERO until TODAY, based on per month calculations",
            "tpIndexByYear": self.getTpIndexByYearSinceStart(tpIndexSummed, totDays),  "descrTpIndexByYear": "Extrapolate the tpIndexSummed to a one year basis"
        }

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def sumUpMonthlyTpIndexes(self, monthlyResult: list):

        K = 100
        index = K

        for result in monthlyResult:
            weightedIndex = result["tpIMonth"] * (result["deltaDays"] / result["dayStepping"])
            index = index * ((weightedIndex / 100) + 1)

        return index - K

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def getTpIndexByYearSinceStart(self, tpIndexSummed, totDays):

        partOfMonth = totDays / (365 / 12)
        interestPerMonth = tpIndexSummed / partOfMonth

        n = 12
        return (((1 + (interestPerMonth / 100)) ** n) - 1) * 100

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def getSwitchAndTransactionMetrics(self):
        return self.switchAndTransactionMetrics

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def calculateSwitchAndTransactionMetrics(self, tickers):

        correctSwitched = 0
        incorrectSwitched = 0
        ignored = 0
        correctLastTransaction = 0
        incorrectLastTransaction = 0

        if tickers is None:
            return None

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Calculating switchAndTransactionMetrcis")

        try:

            if tickers is None or 'list' not in tickers or len(tickers['list']) == 0:
                return None

            for ticker in tickers['list']:

                if ticker['currentStock']['boughtAt'] is not None:
                    # BoughtAt means we want it to rise
                    if ticker['priceOrigCurrancy'] >= ticker['currentStock']['switchedAt']:
                        correctSwitched += 1
                    else:
                        incorrectSwitched += 1

                    if ticker['priceOrigCurrancy'] >= ticker['currentStock']['boughtAt']:
                        correctLastTransaction += 1
                    else:
                        incorrectLastTransaction += 1
                elif ticker['currentStock']['soldAt'] is not None:
                    # soldAt means we want it to fall
                    if ticker['priceOrigCurrancy'] <= ticker['currentStock']['switchedAt']:
                        correctSwitched += 1
                    else:
                        incorrectSwitched += 1

                    if ticker['priceOrigCurrancy'] <= ticker['currentStock']['soldAt']:
                        correctLastTransaction += 1
                    else:
                        incorrectLastTransaction += 1
                else:
                    ignored += 1

        except Exception as ex:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))}. Could not calculate tpProperSwitchedIndex: {ex}")
            return None

        self.switchAndTransactionMetrics = \
            {
                "correctSwitched": correctSwitched,
                "incorrectSwitched": incorrectSwitched,
                "correctLastTransaction": correctLastTransaction,
                "incorrectLastTransaction": incorrectLastTransaction,
                "ignored": ignored
            }


    # ##############################################################################################################
    # ...
    # ##############################################################################################################
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
            self.calculateSwitchAndTransactionMetrics(tickers)
            #self.checkInvestNewStocks()
            if tickers is not None:
                self.tpIndex, retCode = self.calcTpIndexSince(DAY_ZERO, self.getTodayAsString(), sampleSingleStartDate=True, sampleSingleEndDate=False)

            if datetime.datetime.now().hour != lastHour:
                self.tpIndexByMonth = self.getTpIndexesByMonth()
                lastHour = datetime.datetime.now().hour
                self.updateFundsToMongo(0)  # purchase of 0 sek has no impact in Db, but will copy records from yesterday to today

            sys.stdout.flush()
            time.sleep(60)

if __name__ == "__main__":
    m = MetricHandler().init()

    retval = m.calculateSwitchAndTransactionMetrics(m.fetchTickers())
    print(retval)
    exit(0)
    #tp = m.calcTpIndexSince("2021-10-28", m.getTodayAsString())
    tpindexes = m.getTpIndexesByMonth()
    print(tpindexes)

    exit(0)


    retVal1 = m.calcTpIndexSince("2021-10-28", m.getDayAsStringDaysBackFromToday(0))
    retVal2 = m.calcTpIndexSince("2021-11-28", m.getDayAsStringDaysBackFromToday(0))

    print(f"{retVal1} {retVal2}")
