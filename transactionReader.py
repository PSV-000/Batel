import json
import pprint
import csv
from datetime import datetime
from inventoryMethods import *

skuDictionary = json.load(open("skuDictionary.txt")) # Provided by TCG Player

transactionDictionary = {} # Date : [ Array of BUY/TRADE/SELL transactions ]
sampleTrades = [] # Temporary storage of trades
uniqueTrades = [] # Counts batches of trades

with open("sample_transactions.csv", newline='') as transactionInput:
    transReader = csv.DictReader(transactionInput)
    for row in transReader:
        transType = row["Type"].strip()
        transName = row["Card Name"].strip()
        transSet = row["Set Name"].strip()
        transID = row["Trade ID"].strip()
        transPrice = float(row["Price"].strip())
        transDate = row["Date"].strip()
        try:
            transQuantity = int(row["Quantity"].strip())
            transEdition = int(row["Edition"].strip())
            transCondition = int(row["Condition"].strip())
        except ValueError:
            # Processing cash-only line items
            pass

        # Reformat datetime object as a string for dictionary key, year comes first to properly sort ascending
        reverseDate = datetime.strptime(transDate, "%m/%d/%Y")
        reformattedDate = reverseDate.strftime("%Y/%m/%d")

        # Temporarily store trade information
        temp = {}
        if transType == "TRADEIN" or transType == "TRADEOUT":
            if transID not in uniqueTrades:
                uniqueTrades.append(transID)
            if transName == cashConstant or transName == "CASH":
                tradeStore = [transID, transType, transPrice, cashConstant, reformattedDate]
            else:
                tradeStore = [transID, transType, reformattedDate, transPrice, transQuantity, transName]

                # SKU pull for TRADES
                for cards, prints in skuDictionary.items():
                    if transName == cards:
                        for sets, variants in prints.items():
                            if transSet == sets:
                                for editions, conditions in variants.items():
                                    if transEdition == int(editions):
                                        for condition, sku in conditions.items():
                                            if transCondition == int(condition):
                                                tradeStore.append(sku)
                                                break
                                            else:
                                                continue
                                    else:
                                        continue
                            else:
                                continue
                    else:
                        continue
            sampleTrades.append(tradeStore)
            continue

        # Transaction type (Buy/Sell) determines sign of price
        temp["Type"] = transType
        if temp["Type"] == "BUY":
            temp["Price"] = -abs(transPrice)
        elif temp["Type"] == "SELL":
            temp["Price"] = abs(transPrice)
        else:
            temp["Price"] = None

        # No fractional shares of cards allowed, for quantity
        temp["Quantity"] = int(transQuantity)
        temp["Name"] = transName

        # SKU pull for BUY/SELL
        for cards, prints in skuDictionary.items():
            if transName == cards:
                for sets, variants in prints.items():
                    if transSet == sets:
                        for editions, conditions in variants.items():
                            if transEdition == int(editions):
                                for condition, sku in conditions.items():
                                    if transCondition == int(condition):
                                        temp["SKU"] = sku
                                        break
                                    else:
                                        continue
                            else:
                                continue
                    else:
                        continue
            else:
                continue
        try:
            transactionDictionary[reformattedDate].append(temp)
        except KeyError:
            transactionDictionary[reformattedDate] = [temp]

# Append trade information
for unique in uniqueTrades:
    tempTradesIn = []
    tempTradesOut = []
    tempSemi = {}
    tradeDate = ""
    for trade in sampleTrades:
        if trade[0] == unique:
            tradeDate = trade[2]

            # Separate incoming and outgoing trades
            if trade[1] == "TRADEIN":
                tempSet = {}
                if trade[3] == cashConstant:
                    tempSet["Price"] = trade[2]
                    tempSet["Quantity"] = 1
                    tempSet["SKU"] = cashConstant
                    tempSet["Date"] = trade[4]
                else:
                    tempSet["Price"] = trade[3]
                    tempSet["Quantity"] = trade[4]
                    tempSet["Name"] = trade[5]
                    tempSet["SKU"] = trade[6]
                tempTradesIn.append(tempSet)
            elif trade[1] == "TRADEOUT":
                tempSet = {}
                if trade[3] == cashConstant:
                    tempSet["Price"] = -trade[2]
                    tempSet["Quantity"] = 1
                    tempSet["SKU"] = cashConstant
                    tempSet["Date"] = trade[4]
                else:
                    tempSet["Price"] = trade[3]
                    tempSet["Quantity"] = trade[4]
                    tempSet["Name"] = trade[5]
                    tempSet["SKU"] = trade[6]
                tempTradesOut.append(tempSet)
    tempSemi["Type"] = "TRADE"
    tempSemi["In"] = tempTradesIn
    tempSemi["Out"] = tempTradesOut

    try:
        transactionDictionary[tradeDate].append(tempSemi)
    except KeyError:
        transactionDictionary[tradeDate] = [tempSemi]

transactionSort(transactionDictionary) # Sorted for parse order: (1) Buy, (2) Trade, (3) Sell

json.dump(transactionDictionary, open("transactions.txt", 'w'))
