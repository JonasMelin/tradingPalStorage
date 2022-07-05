from MetricHandler import MetricHandler
from flask import Flask, request, Response
import threading
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
metricHandler = MetricHandler()

@app.route("/tradingpalstorage/getTpIndex", methods=['GET'])
def getTpIndex():

    tpIndex, tpIndexTrend = metricHandler.getTpIndexWithTrend()
    tpIndexByMonth = metricHandler.getTpIndexByMonth()

    return {
        "retval": tpIndex, "trend": tpIndexTrend, "descrRetval": "TP index calculated from DAY_ZERO until TODAY in one single calculation",
        "tpIndexByMonth": tpIndexByMonth
    }

@app.route("/tradingpalstorage/getSuperscore2", methods=['GET'])
def getSuperscore2():

    gainList, gainValue = metricHandler.getSuperScore2()

    return {
        "retval": gainList,
        "gainValue": gainValue,
    }

@app.route("/tradingpalstorage/getDevelopmentSinceStart", methods=['GET'])
def getDevelopmentSinceStart():

    dev, trend = metricHandler.getDevelopmentSinceStartWithTrend()
    return {"retval": dev, "trend": trend}

@app.route("/tradingpalstorage/getDevelopmentSinceDaysBack", methods=['GET'])
def getDevelopmentSinceDaysBack():

    daysback = request.args.get("daysback")
    if daysback is None:
        return "missing param daysback"

    dev, trend = metricHandler.getDevelopmentWithTrend(int(daysback))
    return {"retval": dev, "trend": trend}

@app.route("/tradingpalstorage/getTransactionsLastDays", methods=['GET'])
def getTransactionsLastDays():

    daysback = request.args.get("daysback")
    if daysback is None:
        return "missing param daysback"

    return {"retval": metricHandler.getTransactionsLastDays(int(daysback))}

@app.route("/tradingpalstorage/getTurnoverLastDays", methods=['GET'])
def getStatsLastDays():

    daysback = request.args.get("daysback")
    if daysback is None:
        return "missing param daysback"

    sold, bought = metricHandler.getStatsLastDays(int(daysback))

    return {
        "retval": {
            "soldForSek": sold,
            "boughtForSek": bought
        }
    }

@app.route("/tradingpalstorage/getDailyMetrics", methods=['GET'])
def getDailyMetrics():

    return {
        "retval": metricHandler.getDailyMetrics()
    }

@app.route("/tradingpalstorage/addPutinSekToMongo", methods=['GET'])
def addPutinSekToMongo():

    additionalPutinSek = request.args.get('additionalPutinSek')

    if additionalPutinSek is None:
        return Response("Please provied variable additionalPutinSek, i.e \"http://localhost:5001/tradingpalstorage/addPutinSekToMongo?additionalPutinSek=2000\" ", status=400)

    try:
        additionalPutinSek = int(additionalPutinSek)
    except Exception as ex:
        return Response("Provied variable is not an int", status=400)

    print(f"Adding putin sek to mongo: {additionalPutinSek}")
    metricHandler.updateFundsToMongo(purchaseValueSek=0, additionalPutinSek=additionalPutinSek)
    
    return Response(f"Added {additionalPutinSek} to mongo", status=200)


if __name__ == "__main__":

    metricHandler.init()
    threading.Thread(target=metricHandler.mainLoop).start()
    app.run(host='0.0.0.0', port=5001)