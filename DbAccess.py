import os, datetime, pytz, enum
from pymongo import ASCENDING, MongoClient

mongoPort = 27018
mongoHost = "192.168.1.50"
databaseName = "TP"
collectionNameTickers = f"tickers"
collectionNameDailyProgress = f"daily"
collectionNameTransactions = f"transactions"
collectionNameFunds = f"funds"
collectionNameYield = f"yield"
collectionNameTax = f"tax"
collectionNameNewStocks = f"newStocksQueue"

class Collection(enum.Enum):
   Tickers = collectionNameTickers
   DailyProgress = collectionNameDailyProgress
   Transactions = collectionNameTransactions
   Funds = collectionNameFunds
   Yields = collectionNameYield
   Tax = collectionNameTax
   NewStocks = collectionNameNewStocks

# ##############################################################################################################
# ...
# ##############################################################################################################
class DbAccess():

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def __init__(self):
        self.DBRead = None
        self.DBWrite = None

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def init(self):

        global databaseName

        self.DBRead, _, MONGO_CLIENT_Read = self._connectDb(mongoHost, mongoPort, databaseName, collectionNameTickers)
        self._testMongoConnection(MONGO_CLIENT_Read)

        self.PRODUCTION = os.getenv('TP_PROD')

        if self.PRODUCTION is not None and self.PRODUCTION == "true":
            print("RUNNING IN PRODUCTION MODE!!")
            self.DBWrite = self.DBRead
        else:
            print("Writing data to test DB cause environment variable \"TP_PROD=true\" was not set...")
            self.DBWrite, _, MONGO_CLIENT_Write = self._connectDb(mongoHost, mongoPort, databaseName + "_test", collectionNameTickers)
            self._testMongoConnection(MONGO_CLIENT_Write)

        self.fixIndex()

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def _connectDb(self, mongoHost, mongoPort, databaseName, collectionName):

        dbConnection = MongoClient(host=mongoHost, port=mongoPort)
        db = dbConnection[databaseName]
        collection = db[collectionName]
        return db, collection, dbConnection

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def _testMongoConnection(self, dbConnection):

        try:
            print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Mongo connection OK! Version: {dbConnection.server_info()['version']}")
        except Exception as ex:
            raise ValueError(f"{datetime.datetime.utcnow()} Mongo connection FAILED! (B)  {ex}")

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def fixIndex(self):

        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Creating index")

        self.DBWrite[Collection.DailyProgress.value].create_index([('day', ASCENDING), ('ticker', ASCENDING)], unique=True)
        self.DBWrite[Collection.Funds.value].create_index([('day', ASCENDING)], unique=True)

        self.DBWrite[Collection.Yields.value].create_index([('id', ASCENDING)], unique=True)
        self.DBWrite[Collection.Tax.value].create_index([('id', ASCENDING)], unique=True)

        self.DBWrite[Collection.NewStocks.value].create_index([('prio', ASCENDING)])

        self.DBWrite[Collection.Transactions.value].create_index([('date', ASCENDING)])

        self.DBWrite[Collection.Tickers.value].create_index([('tickerName', ASCENDING)])
        self.DBWrite[Collection.Tickers.value].create_index([('dateUTC', ASCENDING)])
        self.DBWrite[Collection.Tickers.value].create_index(name='tickerDate', keys=[('tickerName', ASCENDING), ('dateUTC', ASCENDING)])
        print(f"{datetime.datetime.now(pytz.timezone('Europe/Stockholm'))} Done (creating index)")

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def insert_one(self, data: dict, collection: Collection):
        self.DBWrite[collection.value].insert_one(data)

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def insert_many(self, data: list, collection: Collection):
        if data is not None and len(data) > 0:
            self.DBWrite[collection.value].insert_many(data)

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def update_one(self, query: dict, data: dict, collection: Collection):
        self.DBWrite[collection.value].update_one(query, data, upsert=True)

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def find_one(self, query, collection: Collection):
        return self.DBRead[collection.value].find_one(query)

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def find_one_sort_by(self, sort: tuple, collection: Collection):
        try:
            return self.DBRead[collection.value].find().sort([sort]).next()
        except Exception as ex:
            return None

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def find_sort_by(self, sort: tuple, collection: Collection):
        try:
            return self.DBRead[collection.value].find().sort([sort])
        except Exception as ex:
            return None

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def find(self, query, collection: Collection):
        return self.DBRead[collection.value].find(query)

    # ##############################################################################################################
    # ...
    # ##############################################################################################################
    def delete_by_id(self, _id, collection: Collection):
        self.DBWrite[collection.value].delete_one({"_id": _id})

# ##############################################################################################################
# ...
# ##############################################################################################################
if __name__ == "__main__":
    db = DbAccess()
    db.init()
    db.insert_one({"day": 92, "ticker": "adsf"}, Collection.DailyProgress)
    db.insert_one({"day": 92, "ticker": "adsf"}, Collection.Tickers)