from MetricHandler import MetricHandler
from flask import Flask, request
import threading

app = Flask(__name__)
metricHandler = MetricHandler()

@app.route("/tradingpalstorage/getTpIndex", methods=['GET'])
def getTpIndex():

    tpIndex, tpIndexTrend = metricHandler.getTpIndexWithTrend()
    return {"retval": tpIndex, "trend": tpIndexTrend}

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

if __name__ == "__main__":

    metricHandler.init()
    threading.Thread(target=metricHandler.mainLoop).start()
    app.run(host='0.0.0.0', port=5001)