from unittest.mock import patch, MagicMock
import MetricHandler, DbAccess, datetime, copy

getAllStocksRawReply = "{\n    \"list\": [\n        {\n            \"tickerName\": \"AKSO.OL\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 223,\n                \"currency\": \"NOK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Aker solutions\",\n                \"soldAt\": 25.32,\n                \"totalInvestedSek\": 921,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 24.987795000000002,\n            \"priceOrigCurrancy\": 24.5,\n            \"currancy\": \"NOK\",\n            \"trailingPE\": null,\n            \"priceToSalesTrailing12Months\": 0.440628,\n            \"trailingAnnualDividendYield\": 0.057562526,\n            \"enterpriseValue\": 15853175808\n        },\n        {\n            \"tickerName\": \"AR4.DE\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 20,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Aurelius equity\",\n                \"soldAt\": 28.18,\n                \"totalInvestedSek\": 4099,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 250.13415840000002,\n            \"priceOrigCurrancy\": 25.12,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 21.872267,\n            \"priceToSalesTrailing12Months\": 0.21603073,\n            \"trailingAnnualDividendYield\": 0.04,\n            \"enterpriseValue\": 931242304\n        },\n        {\n            \"tickerName\": \"ATEA.OL\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 33,\n                \"currency\": \"NOK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Atea\",\n                \"soldAt\": 178.8,\n                \"totalInvestedSek\": 5411,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 159.309942,\n            \"priceOrigCurrancy\": 156.2,\n            \"currancy\": \"NOK\",\n            \"trailingPE\": 23.987776,\n            \"priceToSalesTrailing12Months\": 0.42461535,\n            \"trailingAnnualDividendYield\": 0.032258064,\n            \"enterpriseValue\": 19073810432\n        },\n        {\n            \"tickerName\": \"BETS-B.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 52.8,\n                \"count\": 109,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Betsson\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 7518,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 59.7,\n            \"priceOrigCurrancy\": 59.7,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 6.9835677,\n            \"priceToSalesTrailing12Months\": 1.2415357,\n            \"trailingAnnualDividendYield\": 0.061435726,\n            \"enterpriseValue\": 8243290112\n        },\n        {\n            \"tickerName\": \"BILL.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 31,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Billerud korsn\\u00e4s\",\n                \"soldAt\": 187.95,\n                \"totalInvestedSek\": 3563,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 180.0,\n            \"priceOrigCurrancy\": 180.0,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 26.568945,\n            \"priceToSalesTrailing12Months\": 1.470081,\n            \"trailingAnnualDividendYield\": 0.023704521,\n            \"enterpriseValue\": 40872525824\n        },\n        {\n            \"tickerName\": \"BURE.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 366,\n                \"count\": 16,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Bure\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 4858,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 407.4,\n            \"priceOrigCurrancy\": 407.4,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 4.4140706,\n            \"priceToSalesTrailing12Months\": 4.1577506,\n            \"trailingAnnualDividendYield\": 0.0049407114,\n            \"enterpriseValue\": 28748040192\n        },\n        {\n            \"tickerName\": \"CAPMAN.HE\",\n            \"currentStock\": {\n                \"boughtAt\": 2.62,\n                \"count\": 216,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Capman Oyj\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 5367,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 29.52419505,\n            \"priceOrigCurrancy\": 2.965,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 14.8241205,\n            \"priceToSalesTrailing12Months\": 8.972041,\n            \"trailingAnnualDividendYield\": 0.047138046,\n            \"enterpriseValue\": 487436960\n        },\n        {\n            \"tickerName\": \"DANSKE.CO\",\n            \"currentStock\": {\n                \"boughtAt\": 105.7,\n                \"count\": 40,\n                \"currency\": \"DKK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Danske Bank\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 4886,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 146.00595449999997,\n            \"priceOrigCurrancy\": 109.05,\n            \"currancy\": \"DKK\",\n            \"trailingPE\": 9.849812,\n            \"priceToSalesTrailing12Months\": 2.028981,\n            \"trailingAnnualDividendYield\": 0.017346052,\n            \"enterpriseValue\": 1021359489024\n        },\n        {\n            \"tickerName\": \"DBK.DE\",\n            \"currentStock\": {\n                \"boughtAt\": 10.27,\n                \"count\": 55,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Deutsche bank\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 5430,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 111.16631148,\n            \"priceOrigCurrancy\": 11.164,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 13,\n            \"priceToSalesTrailing12Months\": 0.95924854,\n            \"trailingAnnualDividendYield\": 0.00992959,\n            \"enterpriseValue\": -99634839552\n        },\n        {\n            \"tickerName\": \"DNB.OL\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 25,\n                \"currency\": \"NOK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"DNB\",\n                \"soldAt\": 215.7,\n                \"totalInvestedSek\": 3255,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 208.673586,\n            \"priceOrigCurrancy\": 204.6,\n            \"currancy\": \"NOK\",\n            \"trailingPE\": 17.803894,\n            \"priceToSalesTrailing12Months\": 6.4596095,\n            \"trailingAnnualDividendYield\": 0.04398827,\n            \"enterpriseValue\": 852428980224\n        },\n        {\n            \"tickerName\": \"DPW.DE\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 9,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Deutsche Post\",\n                \"soldAt\": 59.25,\n                \"totalInvestedSek\": 1871,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 534.0244791,\n            \"priceOrigCurrancy\": 53.63,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 14.809537,\n            \"priceToSalesTrailing12Months\": 0.90466535,\n            \"trailingAnnualDividendYield\": 0.025037093,\n            \"enterpriseValue\": 80851410944\n        },\n        {\n            \"tickerName\": \"DTE.DE\",\n            \"currentStock\": {\n                \"boughtAt\": 16.208,\n                \"count\": 36,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Deutsche Telekom\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 6511,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 159.00247776,\n            \"priceOrigCurrancy\": 15.968,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 14.339891,\n            \"priceToSalesTrailing12Months\": 0.727786,\n            \"trailingAnnualDividendYield\": 0.036918532,\n            \"enterpriseValue\": 249821495296\n        },\n        {\n            \"tickerName\": \"EOAN.DE\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 50,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"E.ON\",\n                \"soldAt\": 11.33,\n                \"totalInvestedSek\": 4944,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 111.08665092000001,\n            \"priceOrigCurrancy\": 11.156,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 8.566615,\n            \"priceToSalesTrailing12Months\": 0.4547095,\n            \"trailingAnnualDividendYield\": 0.04242643,\n            \"enterpriseValue\": 64772435968\n        },\n        {\n            \"tickerName\": \"EOLU-B.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 152.2,\n                \"count\": 38,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Eolus vind\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 6554,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 159.95,\n            \"priceOrigCurrancy\": 159.95,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 23.168604,\n            \"priceToSalesTrailing12Months\": 1.8838713,\n            \"trailingAnnualDividendYield\": 0.009410289,\n            \"enterpriseValue\": 3406534912\n        },\n        {\n            \"tickerName\": \"EQNR.OL\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 23,\n                \"currency\": \"NOK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Equinor\",\n                \"soldAt\": 235.25,\n                \"totalInvestedSek\": 2908,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 224.17621800000003,\n            \"priceOrigCurrancy\": 219.8,\n            \"currancy\": \"NOK\",\n            \"trailingPE\": 30.42139,\n            \"priceToSalesTrailing12Months\": 10.063613,\n            \"trailingAnnualDividendYield\": 0.0017994294,\n            \"enterpriseValue\": 710857523200\n        },\n        {\n            \"tickerName\": \"EWRK.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 47,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"ework\",\n                \"soldAt\": 122.8,\n                \"totalInvestedSek\": 4309,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 112.6,\n            \"priceOrigCurrancy\": 112.6,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 25.429865,\n            \"priceToSalesTrailing12Months\": 0.15422595,\n            \"trailingAnnualDividendYield\": 0.040035587,\n            \"enterpriseValue\": 1900296320\n        },\n        {\n            \"tickerName\": \"G5EN.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 12,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"G5 Entertainment\",\n                \"soldAt\": 462.2,\n                \"totalInvestedSek\": 5558,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 458.6,\n            \"priceOrigCurrancy\": 458.6,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 20.735817,\n            \"priceToSalesTrailing12Months\": 2.9606996,\n            \"trailingAnnualDividendYield\": 0.013676149,\n            \"enterpriseValue\": 3757371904\n        },\n        {\n            \"tickerName\": \"HAV-B.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 222,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Havsfrun\",\n                \"soldAt\": 26,\n                \"totalInvestedSek\": 5747,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 22.45,\n            \"priceOrigCurrancy\": 22.45,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 24.02529,\n            \"priceToSalesTrailing12Months\": 17.00869,\n            \"trailingAnnualDividendYield\": 0.065789476,\n            \"enterpriseValue\": 132691432\n        },\n        {\n            \"tickerName\": \"HEI.DE\",\n            \"currentStock\": {\n                \"boughtAt\": 61.7,\n                \"count\": 10,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Heidelberg Cement\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 6734,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 655.0089546,\n            \"priceOrigCurrancy\": 65.78,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 7.3554096,\n            \"priceToSalesTrailing12Months\": 0.7013145,\n            \"trailingAnnualDividendYield\": 0.034045186,\n            \"enterpriseValue\": 21625341952\n        },\n        {\n            \"tickerName\": \"IMP-A-SDB.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 75.3,\n                \"count\": 77,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Implantica\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 7961,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 77.2,\n            \"priceOrigCurrancy\": 77.2,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": null,\n            \"priceToSalesTrailing12Months\": null,\n            \"trailingAnnualDividendYield\": null,\n            \"enterpriseValue\": 5124329984\n        },\n        {\n            \"tickerName\": \"INDU-C.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 18,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Industriv\\u00e4rlden\",\n                \"soldAt\": 326.1,\n                \"totalInvestedSek\": 4923,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 276.6,\n            \"priceOrigCurrancy\": 276.6,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 6.1063833,\n            \"priceToSalesTrailing12Months\": 6.1006427,\n            \"trailingAnnualDividendYield\": 0.022441652,\n            \"enterpriseValue\": 126542700544\n        },\n        {\n            \"tickerName\": \"INVE-B.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 27,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Investor\",\n                \"soldAt\": 214.4,\n                \"totalInvestedSek\": 3881,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 199.58,\n            \"priceOrigCurrancy\": 199.58,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 3.9642122,\n            \"priceToSalesTrailing12Months\": 3.2476802,\n            \"trailingAnnualDividendYield\": 0.017447656,\n            \"enterpriseValue\": 677161271296\n        },\n        {\n            \"tickerName\": \"KIND-SDB.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 45,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"kindred\",\n                \"soldAt\": 127.5,\n                \"totalInvestedSek\": 2674,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 119.15,\n            \"priceOrigCurrancy\": 119.15,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 92.42308,\n            \"priceToSalesTrailing12Months\": 19.856558,\n            \"trailingAnnualDividendYield\": 0.0027363186,\n            \"enterpriseValue\": 26308501504\n        },\n        {\n            \"tickerName\": \"LATO-B.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 271.7,\n                \"count\": 22,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Latour\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 4415,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 315.2,\n            \"priceOrigCurrancy\": 315.2,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 40.478653,\n            \"priceToSalesTrailing12Months\": 12.086446,\n            \"trailingAnnualDividendYield\": 0.009520787,\n            \"enterpriseValue\": 207045722112\n        },\n        {\n            \"tickerName\": \"LUND-B.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 10,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Lundbergf\\u00f6retagen\",\n                \"soldAt\": 574,\n                \"totalInvestedSek\": 4828,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 499.9,\n            \"priceOrigCurrancy\": 499.9,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 12.231348,\n            \"priceToSalesTrailing12Months\": 4.162062,\n            \"trailingAnnualDividendYield\": 0.007015434,\n            \"enterpriseValue\": 187761213440\n        },\n        {\n            \"tickerName\": \"MOWI.OL\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 23,\n                \"currency\": \"NOK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Mowi\",\n                \"soldAt\": 238.8,\n                \"totalInvestedSek\": 4325,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 252.01976100000002,\n            \"priceOrigCurrancy\": 247.1,\n            \"currancy\": \"NOK\",\n            \"trailingPE\": 26.166634,\n            \"priceToSalesTrailing12Months\": 31.87413,\n            \"trailingAnnualDividendYield\": 0.0008074284,\n            \"enterpriseValue\": 128725483520\n        },\n        {\n            \"tickerName\": \"NDA-SE.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 52,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Nordea\",\n                \"soldAt\": 110.48,\n                \"totalInvestedSek\": 3451,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 105.04,\n            \"priceOrigCurrancy\": 105.04,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 118.65604,\n            \"priceToSalesTrailing12Months\": 45.198803,\n            \"trailingAnnualDividendYield\": 0.0037142856,\n            \"enterpriseValue\": 549154095104\n        },\n        {\n            \"tickerName\": \"NOBI.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 53.9,\n                \"count\": 107,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Nobia\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 5963,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 52.95,\n            \"priceOrigCurrancy\": 52.95,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 13.718082,\n            \"priceToSalesTrailing12Months\": 0.64877063,\n            \"trailingAnnualDividendYield\": 0.037700284,\n            \"enterpriseValue\": 10951852032\n        },\n        {\n            \"tickerName\": \"ORES.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 144,\n                \"count\": 40,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"\\u00d6resund\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 6368,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 149.2,\n            \"priceOrigCurrancy\": 149.2,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 6.332431,\n            \"priceToSalesTrailing12Months\": 6.3383145,\n            \"trailingAnnualDividendYield\": 0.04054054,\n            \"enterpriseValue\": 6251074560\n        },\n        {\n            \"tickerName\": \"ORK.OL\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 66,\n                \"currency\": \"NOK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Orkla\",\n                \"soldAt\": 88.1,\n                \"totalInvestedSek\": 5402,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 82.714701,\n            \"priceOrigCurrancy\": 81.1,\n            \"currancy\": \"NOK\",\n            \"trailingPE\": 16.670937,\n            \"priceToSalesTrailing12Months\": 1.6274521,\n            \"trailingAnnualDividendYield\": 0.035256412,\n            \"enterpriseValue\": 92712501248\n        },\n        {\n            \"tickerName\": \"POOL-B.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 332,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Poolia\",\n                \"soldAt\": 17.25,\n                \"totalInvestedSek\": 3036,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 15.75,\n            \"priceOrigCurrancy\": 15.75,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 12.632008,\n            \"priceToSalesTrailing12Months\": 0.40994522,\n            \"trailingAnnualDividendYield\": 0.03858521,\n            \"enterpriseValue\": 697226176\n        },\n        {\n            \"tickerName\": \"RATO-B.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 48.88,\n                \"count\": 118,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Ratos\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 4757,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 50.0,\n            \"priceOrigCurrancy\": 50.0,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 6.8311405,\n            \"priceToSalesTrailing12Months\": 0.75970304,\n            \"trailingAnnualDividendYield\": 0.018981019,\n            \"enterpriseValue\": 20758857728\n        },\n        {\n            \"tickerName\": \"RROS.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 9.28,\n                \"count\": 620,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Rottneros\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 6419,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 10.14,\n            \"priceOrigCurrancy\": 10.14,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 21.31356,\n            \"priceToSalesTrailing12Months\": 0.6992594,\n            \"trailingAnnualDividendYield\": 0.044731606,\n            \"enterpriseValue\": 1390518784\n        },\n        {\n            \"tickerName\": \"RWE.DE\",\n            \"currentStock\": {\n                \"boughtAt\": 29.22,\n                \"count\": 19,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"RWE\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 6010,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 336.96416880000004,\n            \"priceOrigCurrancy\": 33.84,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 18.820255,\n            \"priceToSalesTrailing12Months\": 1.5572492,\n            \"trailingAnnualDividendYield\": 0.025282571,\n            \"enterpriseValue\": 17616123904\n        },\n        {\n            \"tickerName\": \"SAMPO.HE\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 12,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Sampo\",\n                \"soldAt\": 46.33,\n                \"totalInvestedSek\": 4594,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 458.54609849999997,\n            \"priceOrigCurrancy\": 46.05,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 74.05751,\n            \"priceToSalesTrailing12Months\": 2.1879935,\n            \"trailingAnnualDividendYield\": 0.03649635,\n            \"enterpriseValue\": 18430437376\n        },\n        {\n            \"tickerName\": \"SEMC.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 115,\n                \"count\": 51,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Semcon\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 5689,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 115.0,\n            \"priceOrigCurrancy\": 115.0,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 20.728394,\n            \"priceToSalesTrailing12Months\": 1.2864755,\n            \"trailingAnnualDividendYield\": 0.025510205,\n            \"enterpriseValue\": 1808689664\n        },\n        {\n            \"tickerName\": \"SKUE.OL\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 27,\n                \"currency\": \"NOK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Skue sparbank\",\n                \"soldAt\": 204.0,\n                \"totalInvestedSek\": 4143,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 208.06164,\n            \"priceOrigCurrancy\": 204.0,\n            \"currancy\": \"NOK\",\n            \"trailingPE\": 11.880597,\n            \"priceToSalesTrailing12Months\": 1.2145177,\n            \"trailingAnnualDividendYield\": 0.03,\n            \"enterpriseValue\": 1340732416\n        },\n        {\n            \"tickerName\": \"SSAB-B.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 134,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"SSAB\",\n                \"soldAt\": 42.68,\n                \"totalInvestedSek\": 4101,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 42.82,\n            \"priceOrigCurrancy\": 42.82,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 53.08658,\n            \"priceToSalesTrailing12Months\": 0.5989057,\n            \"trailingAnnualDividendYield\": 0.035663337,\n            \"enterpriseValue\": 52493946880\n        },\n        {\n            \"tickerName\": \"STE-R.ST\",\n            \"currentStock\": {\n                \"boughtAt\": 141,\n                \"count\": 41,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Stora Enso\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 4339,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 145.2,\n            \"priceOrigCurrancy\": 145.2,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 187.05128,\n            \"priceToSalesTrailing12Months\": 13.344892,\n            \"trailingAnnualDividendYield\": 0.002080444,\n            \"enterpriseValue\": 121877585920\n        },\n        {\n            \"tickerName\": \"SWED-a.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 30,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Swedbank\",\n                \"soldAt\": 187.7,\n                \"totalInvestedSek\": 3966,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 187.12,\n            \"priceOrigCurrancy\": 187.12,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 11.162765,\n            \"priceToSalesTrailing12Months\": 4.795967,\n            \"trailingAnnualDividendYield\": 0.014979339,\n            \"enterpriseValue\": 661934112768\n        },\n        {\n            \"tickerName\": \"TEL2-B.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 43,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Tele2\",\n                \"soldAt\": 133.9,\n                \"totalInvestedSek\": 4637,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 122.7,\n            \"priceOrigCurrancy\": 122.7,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 11.981049,\n            \"priceToSalesTrailing12Months\": 3.1892698,\n            \"trailingAnnualDividendYield\": 0.048328634,\n            \"enterpriseValue\": 116802437120\n        },\n        {\n            \"tickerName\": \"TELIA.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 150,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Telia\",\n                \"soldAt\": 38.47,\n                \"totalInvestedSek\": 5683,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 33.9,\n            \"priceOrigCurrancy\": 33.9,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": null,\n            \"priceToSalesTrailing12Months\": 1.5669575,\n            \"trailingAnnualDividendYield\": 0.058445353,\n            \"enterpriseValue\": 249472827392\n        },\n        {\n            \"tickerName\": \"TKA.DE\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 60,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Thyssenkrupp AG\",\n                \"soldAt\": 9.44,\n                \"totalInvestedSek\": 5200,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 89.67787542,\n            \"priceOrigCurrancy\": 9.006,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 0.53030396,\n            \"priceToSalesTrailing12Months\": 0.17572634,\n            \"trailingAnnualDividendYield\": 0.016659264,\n            \"enterpriseValue\": 2144920320\n        },\n        {\n            \"tickerName\": \"TLX.DE\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 14,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"Talanx\",\n                \"soldAt\": 40.06,\n                \"totalInvestedSek\": 4817,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 413.23915500000004,\n            \"priceOrigCurrancy\": 41.5,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": 15.699247,\n            \"priceToSalesTrailing12Months\": 0.26744467,\n            \"trailingAnnualDividendYield\": 0.036531903,\n            \"enterpriseValue\": 17143323648\n        },\n        {\n            \"tickerName\": \"TUI1.DE\",\n            \"currentStock\": {\n                \"boughtAt\": 2.595,\n                \"count\": 222,\n                \"currency\": \"EUR\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"TUI\",\n                \"soldAt\": null,\n                \"totalInvestedSek\": 7878,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 28.80725001,\n            \"priceOrigCurrancy\": 2.893,\n            \"currancy\": \"EUR\",\n            \"trailingPE\": null,\n            \"priceToSalesTrailing12Months\": 1.2262956,\n            \"trailingAnnualDividendYield\": 0.1894737,\n            \"enterpriseValue\": 9266094080\n        },\n        {\n            \"tickerName\": \"VNV.ST\",\n            \"currentStock\": {\n                \"boughtAt\": null,\n                \"count\": 43,\n                \"currency\": \"SEK\",\n                \"lockCounter\": 0,\n                \"lockKey\": -1,\n                \"name\": \"VNV Global\",\n                \"soldAt\": 131.0,\n                \"totalInvestedSek\": 4115,\n                \"tickerIsLocked\": false\n            },\n            \"singleStockPriceSek\": 127.1,\n            \"priceOrigCurrancy\": 127.1,\n            \"currancy\": \"SEK\",\n            \"trailingPE\": 43.266956,\n            \"priceToSalesTrailing12Months\": 37.782246,\n            \"trailingAnnualDividendYield\": null,\n            \"enterpriseValue\": 12645213184\n        }\n    ],\n    \"updatedUtc\": \"2021-10-29 09:47:25.314369+02:00\",\n    \"sellModeStocks\": 28,\n    \"buyModeStocks\": 18,\n    \"neutralModeStocks\": 0,\n    \"failCounter\": 0,\n    \"successCounter\": 46,\n    \"skippedCounter\": 23,\n    \"totalInvestedSek\": 224019,\n    \"totalGlobalValueSek\": 261073,\n    \"updateVersion\": 729061685,\n    \"industries\": {\n        \"Integrated Freight & Logistics\": {\n            \"totValue (SEK)\": 4806,\n            \"companies\": [\n                \"Deutsche Post\"\n            ]\n        },\n        \"Capital Markets\": {\n            \"totValue (SEK)\": 4983,\n            \"companies\": [\n                \"Havsfrun\"\n            ]\n        },\n        \"Staffing & Employment Services\": {\n            \"totValue (SEK)\": 5229,\n            \"companies\": [\n                \"Poolia\"\n            ]\n        },\n        \"Metal Fabrication\": {\n            \"totValue (SEK)\": 5380,\n            \"companies\": [\n                \"Thyssenkrupp AG\"\n            ]\n        },\n        \"Packaged Foods\": {\n            \"totValue (SEK)\": 5459,\n            \"companies\": [\n                \"Orkla\"\n            ]\n        },\n        \"Electronic Gaming & Multimedia\": {\n            \"totValue (SEK)\": 5503,\n            \"companies\": [\n                \"G5 Entertainment\"\n            ]\n        },\n        \"Furnishings, Fixtures & Appliances\": {\n            \"totValue (SEK)\": 5665,\n            \"companies\": [\n                \"Nobia\"\n            ]\n        },\n        \"Steel\": {\n            \"totValue (SEK)\": 5737,\n            \"companies\": [\n                \"SSAB\"\n            ]\n        },\n        \"Farm Products\": {\n            \"totValue (SEK)\": 5796,\n            \"companies\": [\n                \"Mowi\"\n            ]\n        },\n        \"Medical Devices\": {\n            \"totValue (SEK)\": 5944,\n            \"companies\": [\n                \"Implantica\"\n            ]\n        },\n        \"Travel Services\": {\n            \"totValue (SEK)\": 6395,\n            \"companies\": [\n                \"TUI\"\n            ]\n        },\n        \"Building Materials\": {\n            \"totValue (SEK)\": 6550,\n            \"companies\": [\n                \"Heidelberg Cement\"\n            ]\n        },\n        \"Information Technology Services\": {\n            \"totValue (SEK)\": 10549,\n            \"companies\": [\n                \"Atea\",\n                \"ework\"\n            ]\n        },\n        \"oil industry\": {\n            \"totValue (SEK)\": 10728,\n            \"companies\": [\n                \"Aker solutions\",\n                \"Equinor\"\n            ]\n        },\n        \"Insurance\\u2014Diversified\": {\n            \"totValue (SEK)\": 11287,\n            \"companies\": [\n                \"Sampo\",\n                \"Talanx\"\n            ]\n        },\n        \"Gambling\": {\n            \"totValue (SEK)\": 11868,\n            \"companies\": [\n                \"Betsson\",\n                \"kindred\"\n            ]\n        },\n        \"Engineering & Construction\": {\n            \"totValue (SEK)\": 11943,\n            \"companies\": [\n                \"Eolus vind\",\n                \"Semcon\"\n            ]\n        },\n        \"Utilities\\u2014Diversified\": {\n            \"totValue (SEK)\": 11956,\n            \"companies\": [\n                \"E.ON\",\n                \"RWE\"\n            ]\n        },\n        \"Telecom Services\": {\n            \"totValue (SEK)\": 16085,\n            \"companies\": [\n                \"Deutsche Telekom\",\n                \"Tele2\",\n                \"Telia\"\n            ]\n        },\n        \"Paper & Paper Products\": {\n            \"totValue (SEK)\": 17819,\n            \"companies\": [\n                \"Billerud korsn\\u00e4s\",\n                \"Rottneros\",\n                \"Stora Enso\"\n            ]\n        },\n        \"banking\": {\n            \"totValue (SEK)\": 33862,\n            \"companies\": [\n                \"Danske Bank\",\n                \"Deutsche bank\",\n                \"DNB\",\n                \"Nordea\",\n                \"Skue sparbank\",\n                \"Swedbank\"\n            ]\n        },\n        \"Asset Management\": {\n            \"totValue (SEK)\": 57529,\n            \"companies\": [\n                \"Aurelius equity\",\n                \"Bure\",\n                \"Capman Oyj\",\n                \"Industriv\\u00e4rlden\",\n                \"Investor\",\n                \"Latour\",\n                \"Lundbergf\\u00f6retagen\",\n                \"\\u00d6resund\",\n                \"Ratos\",\n                \"VNV Global\"\n            ]\n        }\n    }\n}"
getLastTransactionRawReply = "{\n    \"boughtAt\": 2.88,\n    \"count\": 202,\n    \"currency\": \"EUR\",\n    \"name\": \"TUI\",\n    \"soldAt\": null,\n    \"totalInvestedSek\": 7661,\n    \"purchasedStocks\": 16,\n    \"purchaseValueSek\": 457,\n    \"date\": \"2021-10-29 17:19:20.483941+02:00\",\n    \"tradedByBot\": false\n}"
getTickerCurrentValueReply = "{\n    \"price\": 25.76,\n    \"industry\": \"Oil & Gas Equipment & Services\",\n    \"employees\": 14888,\n    \"price_in_sek\": 25.893952000000002,\n    \"convertToSekRatio\": 1.0052\n}"
mongoFundsFindLatest = {'_id': '618708fa9d2a3d6e68fa052d', 'day': '2021-11-07', 'fundsSek': 14334, 'putinSek': 1, 'yield': 577, 'yieldTax': 2, 'tpIndex': 0.04}
mongoDailyProgressFindByDay = [{'_id': '617a4b21e9df121b71f9a3c8', 'day': '2021-10-28', 'ticker': 'AKSO.OL', 'count': 223, 'name': 'Aker solutions', 'singleStockPriceSek': 24.606665999999997, 'currency': 'NOK'}]
mongoTransactionsFindByDay = [{'_id': '618ad061f76a6b5902fc9712', 'boughtAt': None, 'count': 52, 'currency': 'CAD', 'name': 'Boston Pizza', 'soldAt': 15.88, 'totalInvestedSek': 4548, 'purchasedStocks': -11, 'purchaseValueSek': -1202, 'date': datetime.datetime(2021, 11, 9, 19, 47, 14, 351000), 'tradedByBot': True}]
getFundsFromAvanzaHandlerReply = "{\"funds\":5000.07}"
getYieldFromAvanzaHandlerReply = "{\"yields\":[{\"account\":{\"id\":\"9288043\",\"name\":\"Jonas KF\",\"type\":\"Kapitalforsakring\"},\"amount\":34.15,\"currency\":\"SEK\",\"description\":\"Utdelning 18 st \\u00e0 1,89 KROGER CO\",\"id\":\"2980124327ABBBPRJT465\",\"orderbook\":{\"currency\":\"USD\",\"flagCode\":\"US\",\"id\":\"3477\",\"isin\":\"US5010441013\",\"name\":\"Kroger Co\",\"type\":\"STOCK\"},\"price\":1.897667,\"sum\":34.16,\"transactionType\":\"DIVIDEND\",\"verificationDate\":\"2021-12-02\",\"volume\":18.0},{\"account\":{\"id\":\"9288043\",\"name\":\"Jonas KF\",\"type\":\"Kapitalforsakring\"},\"amount\":46.16,\"currency\":\"SEK\",\"description\":\"Utdelning 163 st \\u00e0 0,28 JAGUAR MINING INC\",\"id\":\"2976910000ABBBPRGC196\",\"orderbook\":{\"currency\":\"CAD\",\"flagCode\":\"CA\",\"id\":\"85697\",\"isin\":\"CA47009M8896\",\"name\":\"Jaguar Mining Inc\",\"type\":\"STOCK\"},\"price\":0.283241,\"sum\":46.17,\"transactionType\":\"DIVIDEND\",\"verificationDate\":\"2021-12-01\",\"volume\":163.0},{\"account\":{\"id\":\"9288043\",\"name\":\"Jonas KF\",\"type\":\"Kapitalforsakring\"},\"amount\":31.29,\"currency\":\"SEK\",\"description\":\"Utdelning 52 st \\u00e0 0,60 BOSTON PIZZA ROYALTIES INCOME FUND\",\"id\":\"2976909094ABBBPRGB8496\",\"orderbook\":{\"currency\":\"CAD\",\"flagCode\":\"CA\",\"id\":\"194368\",\"isin\":\"CA1010841015\",\"name\":\"Boston Pizza Royalties Income Fund\",\"type\":\"STOCK\"},\"price\":0.601888,\"sum\":31.3,\"transactionType\":\"DIVIDEND\",\"verificationDate\":\"2021-12-01\",\"volume\":52.0},{\"account\":{\"id\":\"9288043\",\"name\":\"Jonas KF\",\"type\":\"Kapitalforsakring\"},\"amount\":32.01,\"currency\":\"SEK\",\"description\":\"Utdelning 23 st \\u00e0 1,39 MOWI ASA\",\"id\":\"2972456949ABBBPQSM3917\",\"orderbook\":{\"currency\":\"NOK\",\"flagCode\":\"NO\",\"id\":\"52507\",\"isin\":\"NO0003054108\",\"name\":\"Mowi\",\"type\":\"STOCK\"},\"price\":1.392073,\"sum\":32.02,\"transactionType\":\"DIVIDEND\",\"verificationDate\":\"2021-11-30\",\"volume\":23.0}]}\n"
getTaxFromAvanzaHandlerReply = "{\"taxes\":[{\"account\":{\"id\":\"9288043\",\"name\":\"Jonas KF\",\"type\":\"Kapitalforsakring\"},\"amount\":-5.12,\"currency\":\"SEK\",\"description\":\"Utl\\u00e4ndsk k\\u00e4llskatt KROGER CO 15%\",\"id\":\"2980124328ABBBPRJT466\",\"orderbook\":{\"currency\":\"USD\",\"flagCode\":\"US\",\"id\":\"3477\",\"isin\":\"US5010441013\",\"name\":\"Kroger Co\",\"type\":\"STOCK\"},\"transactionType\":\"FOREIGN_TAX\",\"verificationDate\":\"2021-12-02\",\"volume\":18.0},{\"account\":{\"id\":\"9288043\",\"name\":\"Jonas KF\",\"type\":\"Kapitalforsakring\"},\"amount\":-6.92,\"currency\":\"SEK\",\"description\":\"Utl\\u00e4ndsk k\\u00e4llskatt JAGUAR MINING INC 15%\",\"id\":\"2976910001ABBBPRGC197\",\"orderbook\":{\"currency\":\"CAD\",\"flagCode\":\"CA\",\"id\":\"85697\",\"isin\":\"CA47009M8896\",\"name\":\"Jaguar Mining Inc\",\"type\":\"STOCK\"},\"transactionType\":\"FOREIGN_TAX\",\"verificationDate\":\"2021-12-01\",\"volume\":163.0},{\"account\":{\"id\":\"9288043\",\"name\":\"Jonas KF\",\"type\":\"Kapitalforsakring\"},\"amount\":-4.69,\"currency\":\"SEK\",\"description\":\"Utl\\u00e4ndsk k\\u00e4llskatt BOSTON PIZZA ROYALTIES INCOME FUND 15%\",\"id\":\"2976909095ABBBPRGB8497\",\"orderbook\":{\"currency\":\"CAD\",\"flagCode\":\"CA\",\"id\":\"194368\",\"isin\":\"CA1010841015\",\"name\":\"Boston Pizza Royalties Income Fund\",\"type\":\"STOCK\"},\"transactionType\":\"FOREIGN_TAX\",\"verificationDate\":\"2021-12-01\",\"volume\":52.0},{\"account\":{\"id\":\"9288043\",\"name\":\"Jonas KF\",\"type\":\"Kapitalforsakring\"},\"amount\":-8.0,\"currency\":\"SEK\",\"description\":\"Utl\\u00e4ndsk k\\u00e4llskatt MOWI ASA 25%\",\"id\":\"2972456950ABBBPQSM3918\",\"orderbook\":{\"currency\":\"NOK\",\"flagCode\":\"NO\",\"id\":\"52507\",\"isin\":\"NO0003054108\",\"name\":\"Mowi\",\"type\":\"STOCK\"},\"transactionType\":\"FOREIGN_TAX\",\"verificationDate\":\"2021-11-30\",\"volume\":23.0}]}\n"
mongoNextNewStockToBuy = {'_id': '61ae136ecd398008e1d9c3dc', 'ticker': 'NOKIA.HE', 'name': 'Nokia', 'prio': 10}


@patch('MetricHandler.requests')
def testGetYield(requestsMock):
    objUnderTest = MetricHandler.MetricHandler()
    requestsMock.get.return_value.status_code = 200
    requestsMock.get.return_value.content = getYieldFromAvanzaHandlerReply
    objUnderTest.dbAccess = MagicMock()

    retData = objUnderTest.getNewYieldFromAvanza()

    assert retData is not None and retData > 1.0


@patch('MetricHandler.requests')
def testGetTax(requestsMock):
    objUnderTest = MetricHandler.MetricHandler()
    requestsMock.get.return_value.status_code = 200
    requestsMock.get.return_value.content = getTaxFromAvanzaHandlerReply
    objUnderTest.dbAccess = MagicMock()

    retData = objUnderTest.getNewTaxFromAvanza()

    assert retData is not None and retData > 1.0

@patch('MetricHandler.requests')
def testFetchTickers(requestsMock):
    objUnderTest = MetricHandler.MetricHandler()
    requestsMock.get.return_value.status_code = 200
    requestsMock.get.return_value.content = getAllStocksRawReply

    requestsMock.reset_mock()
    tickers1 = objUnderTest.fetchTickers()
    requestsMock.get.assert_called_once_with(MetricHandler.URLTickers)
    assert(tickers1 is not None)
    assert type(tickers1) is dict and len(tickers1) > 0
    assert('list' in tickers1 and len(tickers1['list']) > 0) # First call you get tickers.

    requestsMock.reset_mock()
    tickers2 = objUnderTest.fetchTickers()
    requestsMock.get.assert_called_once_with(MetricHandler.URLTickers)
    assert (tickers2 is None) # no updated data hence None

    requestsMock.reset_mock()
    requestsMock.get.return_value.content = "{\"list\": []}"
    tickers2 = objUnderTest.fetchTickers()
    assert (tickers2 is not None) # updated data, hence not null any more
    assert type(tickers2) is dict and len(tickers2) > 0

    return tickers1

@patch('MetricHandler.requests')
def testFetchTransactions(requestsMock):
    objUnderTest = MetricHandler.MetricHandler()
    requestsMock.get.return_value.status_code = 200
    requestsMock.get.return_value.content = getLastTransactionRawReply

    requestsMock.reset_mock()
    transactions = objUnderTest.fetchTransactions()
    requestsMock.get.assert_called_once_with(MetricHandler.URLTransactions)
    assert(transactions is not None)
    assert type(transactions) is dict and len(transactions) > 0

    return transactions

def testWriteTransactions():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.updateFundsToMongo = MagicMock()
    objUnderTest.dbAccess = MagicMock()

    transactionData = testFetchTransactions()
    objUnderTest.writeTransactionsToMongo(transactionData)

    objUnderTest.dbAccess.insert_one.assert_called_once_with(transactionData, DbAccess.Collection.Transactions)
    objUnderTest.updateFundsToMongo.assert_called_once_with(transactionData['purchaseValueSek'])

@patch('MetricHandler.requests')
def testUpdateFundsToMongo(requestsMock):
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.dbAccess = MagicMock()
    objUnderTest.dbAccess.find_one_sort_by.return_value = mongoFundsFindLatest
    requestsMock.get.return_value.status_code = 200
    requestsMock.get.return_value.content = getFundsFromAvanzaHandlerReply

    objUnderTest.updateFundsToMongo(6)

    objUnderTest.dbAccess.find_one_sort_by.assert_called_once()
    objUnderTest.dbAccess.update_one.assert_called_once()

def testWriteDailyProgressToMongo():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.dbAccess = MagicMock()

    objUnderTest.writeDailyProgressToMongo(testFetchTickers())
    objUnderTest.dbAccess.update_one.assert_called()

def testWriteTickersToMongo():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.dbAccess = MagicMock()

    objUnderTest.writeTickersToMongo(testFetchTickers())
    objUnderTest.dbAccess.insert_many.assert_called()

def testGetDaysAsStringDaysBack():
    objUnderTest = MetricHandler.MetricHandler()

    retVal = objUnderTest.getDayAsStringDaysBackFromToday(4)
    assert retVal is not None
    assert type(retVal) is str and len(retVal) > 0

def testGetQueryStartEndFullDays():
    objUnderTest = MetricHandler.MetricHandler()

    queryStart, queryEnd = objUnderTest.getQueryStartEndFullDays(4)
    assert queryStart is not None
    assert queryEnd is not None
    assert type(queryEnd) is datetime.datetime
    assert type(queryStart) is datetime.datetime

def testGetFinancialDiffBetween():
    objUnderTest = MetricHandler.MetricHandler()
    stocksAtStart, fundsAtStart = testFetchDailyDataFromMongoByDate()
    stocksAtEnd, fundsAtEnd = testFetchDailyDataFromMongoByDate()

    retVal = objUnderTest.getFinancialDiffBetween(stocksAtStart, fundsAtStart, stocksAtEnd, fundsAtEnd)
    assert retVal is not None
    assert retVal == 0.0

def testFetchDailyDataFromMongoByDate():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.dbAccess = MagicMock()
    objUnderTest.dbAccess.find.return_value = copy.deepcopy(mongoDailyProgressFindByDay)
    objUnderTest.fetchFundsFromMongo = MagicMock()
    objUnderTest.fetchFundsFromMongo.return_value = copy.deepcopy(mongoFundsFindLatest)

    dailyData, funds = objUnderTest.fetchDailyDataFromMongoByDate(4)
    assert dailyData is not None
    assert funds is not None
    assert type(dailyData) is list and len(dailyData) > 0
    assert type(funds) is dict and len(funds) > 0

    return dailyData, funds

def testFetchFundsFromMongo():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.dbAccess = MagicMock()
    objUnderTest.dbAccess.find_one.return_value = copy.deepcopy(mongoFundsFindLatest)

    retVal = objUnderTest.fetchFundsFromMongo(4)
    assert retVal is not None
    assert type(retVal) is dict

    return retVal

def testFetchDailyDataMostRecent():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.dbAccess = MagicMock()
    objUnderTest.dbAccess.find.return_value = copy.deepcopy(mongoDailyProgressFindByDay)
    objUnderTest.fetchFundsFromMongo = MagicMock()
    objUnderTest.fetchFundsFromMongo.return_value = copy.deepcopy(testFetchFundsFromMongo())

    dailyStocks, dailyFunds = objUnderTest.fetchDailyDataMostRecent()
    assert dailyStocks is not None
    assert dailyFunds is not None

    return dailyStocks, dailyFunds

def testFetchDailyDataFromMongo():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.dbAccess = MagicMock()
    objUnderTest.dbAccess.find.return_value = copy.deepcopy(mongoDailyProgressFindByDay)
    objUnderTest.fetchFundsFromMongo = MagicMock()
    objUnderTest.fetchFundsFromMongo.return_value = copy.deepcopy(testFetchFundsFromMongo())

    dailyStocks, dailyFunds = objUnderTest.fetchDailyDataFromMongo(2, allowCrawlingBack=True)
    assert dailyStocks is not None
    assert dailyFunds is not None

    return dailyStocks, dailyFunds

@patch('MetricHandler.requests')
def testAddCurrentStockValueToStocks(requestsMock):
    objUnderTest = MetricHandler.MetricHandler()
    requestsMock.get.return_value.status_code = 200
    requestsMock.get.return_value.content = copy.deepcopy(getTickerCurrentValueReply)

    tickers, funds = testFetchDailyDataFromMongoByDate()
    assert len(tickers) == 1
    assert 'priceInSekNow' not in tickers[0]
    objUnderTest.addCurrentStockValueToStocks(tickers)

    assert len(tickers) == 1
    assert 'priceInSekNow' in tickers[0]

@patch('MetricHandler.requests')
def testCalcTpIndexSince(requestsMock):
    objUnderTest = MetricHandler.MetricHandler()
    requestsMock.get.return_value.status_code = 200
    requestsMock.get.return_value.content = getTickerCurrentValueReply
    objUnderTest.fetchDailyDataFromMongoByDate = MagicMock()
    objUnderTest.fetchDailyDataFromMongoByDate.return_value = copy.deepcopy(testFetchDailyDataFromMongoByDate())
    objUnderTest.fetchDailyDataMostRecent = MagicMock()
    objUnderTest.fetchDailyDataMostRecent.return_value = copy.deepcopy(testFetchDailyDataFromMongoByDate())

    retVal, retCode = objUnderTest.calcTpIndexSince("2021-10-28")
    assert retCode is 0
    assert retVal is not 0

    return retVal, retCode

def testGetTpIndexWithTrend():
    objUnderTest = MetricHandler.MetricHandler()

    objUnderTest.tpIndex = 7.4
    _, _ = objUnderTest.getTpIndexWithTrend()

    objUnderTest.tpIndex = 7.5
    index, trend = objUnderTest.getTpIndexWithTrend()
    assert index is 7.5 and trend is 1

    objUnderTest.tpIndex = 7.5
    index, trend = objUnderTest.getTpIndexWithTrend()
    assert index is 7.5 and trend is 1

    objUnderTest.tpIndex = 7.4
    index, trend = objUnderTest.getTpIndexWithTrend()
    assert index is 7.4 and trend is -1

    return index, trend

def testGetDevelopmentWithTrend():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.getHistoricDevelopment = MagicMock()

    objUnderTest.getHistoricDevelopment.return_value = 2.3
    _, _ = objUnderTest.getDevelopmentWithTrend(3)

    objUnderTest.getHistoricDevelopment.return_value = 2.4
    dev, trend = objUnderTest.getDevelopmentWithTrend(3)
    assert dev is 2.4 and trend is 1

    objUnderTest.getHistoricDevelopment.return_value = 1.3
    _, _ = objUnderTest.getDevelopmentWithTrend(2)

    objUnderTest.getHistoricDevelopment.return_value = 1.2
    dev, trend = objUnderTest.getDevelopmentWithTrend(2)
    assert dev is 1.2 and trend is -1

    objUnderTest.getHistoricDevelopment.return_value = 2.4
    dev, trend = objUnderTest.getDevelopmentWithTrend(3)
    assert dev is 2.4 and trend is 1

    return dev, trend

def testGetDevelopmentSinceDate():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.fetchDailyDataFromMongoByDate = MagicMock()
    objUnderTest.fetchDailyDataFromMongoByDate.return_value = copy.deepcopy(testFetchDailyDataFromMongoByDate())
    objUnderTest.fetchDailyDataMostRecent = MagicMock()
    objUnderTest.fetchDailyDataMostRecent.return_value = copy.deepcopy(testFetchDailyDataMostRecent())

    diff = objUnderTest.getDevelopmentSinceDate("2021-10-29")
    assert diff is not None

    return diff


def testGetHistoricDevelopment():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.fetchDailyDataFromMongo = MagicMock()
    objUnderTest.fetchDailyDataFromMongo.return_value = copy.deepcopy(testFetchDailyDataFromMongoByDate())
    objUnderTest.fetchDailyDataFromMongo = MagicMock()
    objUnderTest.fetchDailyDataFromMongo.return_value = copy.deepcopy(testFetchDailyDataMostRecent())

    diff = objUnderTest.getHistoricDevelopment(3)
    assert diff is not None

    return diff

def testGetDevelopmentSinceStartWithTrend():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.getDevelopmentSinceDate = MagicMock()

    objUnderTest.getDevelopmentSinceDate.return_value = 0.4
    _, _ = objUnderTest.getDevelopmentSinceStartWithTrend()
    objUnderTest.getDevelopmentSinceDate.return_value = 0.5
    dev, trend = objUnderTest.getDevelopmentSinceStartWithTrend()
    assert dev is 0.5 and trend is 1

def testGetTransactionsLastDays():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.dbAccess = MagicMock()
    objUnderTest.dbAccess.find.return_value = copy.deepcopy(mongoTransactionsFindByDay)

    retVal = objUnderTest.getTransactionsLastDays(3)
    assert retVal is not None and len(retVal) > 0

    return retVal

def testGetStatsLastDays():
    objUnderTest = MetricHandler.MetricHandler()
    objUnderTest.dbAccess = MagicMock()
    objUnderTest.dbAccess.find.return_value = mongoTransactionsFindByDay

    sold, bought = objUnderTest.getStatsLastDays(3)
    assert sold is not None and bought is not None

    return sold, bought

#########################################################################################
# Run all tests
#########################################################################################
testGetYield()
testGetTax()
testWriteTransactions()
testFetchTransactions()
testFetchTickers()
testUpdateFundsToMongo()
testWriteDailyProgressToMongo()
testWriteTickersToMongo()
testGetDaysAsStringDaysBack()
testGetQueryStartEndFullDays()
testFetchFundsFromMongo()
testFetchDailyDataFromMongoByDate()
testGetFinancialDiffBetween()
testFetchDailyDataMostRecent()
testFetchDailyDataFromMongo()
testAddCurrentStockValueToStocks()
testCalcTpIndexSince()
testGetTpIndexWithTrend()
testGetDevelopmentWithTrend()
testGetDevelopmentSinceDate()
testGetHistoricDevelopment()
testGetDevelopmentSinceStartWithTrend()
testGetTransactionsLastDays()
testGetStatsLastDays()
