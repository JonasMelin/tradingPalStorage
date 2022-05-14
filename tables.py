import math

def getCourtage(ticker, value):
    
    value = math.fabs(value)

    if ".OL" in ticker:
        return ST_converter(value)
    if ".ST" in ticker:
        return ST_converter(value)
    if ".DE" in ticker:
        return US_converter(value)
    if ".HE" in ticker:
        return US_converter(value)
    if ".CO" in ticker:
        return ST_converter(value)
    if ".TO" in ticker:
        return US_converter(value)
    if "." not in ticker:
        return US_converter(value)

    print(f"warning: Could not look up courtage for ticker {ticker}")
    return US_converter(value)

def US_converter(value):
    if value < 400:
        return 10

    return 15

def ST_converter(value):
    if value < 500:
        return 1
    if value < 900:
        return 2
    if value < 1200:
        return 3
    if value < 1700:
        return 4
    if value < 1900:
        return 5
    if value < 2100:
        return 6
    if value < 2700:
        return 7
    if value < 3600:
        return 9

    return 13


if __name__ == "__main__":
    print(getCourtage("ABC.ST", 10))
    print(getCourtage("ABC.ST", -1000))
    print(getCourtage("ABC.ST", 10000))