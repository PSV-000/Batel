import json
import pprint
import csv
from datetime import datetime
from inventoryMethods import *

skuDictionary = json.load(open("skuDictionary.txt")) # Provided by TCG Player

transactionDictionary = {} # Date : [ Array of BUY/TRADE/SELL transactions ]
sampleTrades = [] # Temporary storage of trades
uniqueTrades = [] # Counts batches of trades

with open("sample_transactions.csv", newline = '') as sample:
    reader = csv.DictReader(sample)
    for row in reader:
        temp = {}
        new_date = row["Date"].strip()

        # Reformat datetime object as a string for dictionary key, year comes first to properly sort ascending
        reverseDate = datetime.strptime(new_date, "%m/%d/%Y")
        reformattedDate = reverseDate.strftime("%Y/%m/%d")

        # Temporarily store trade information
        if row["Type"].strip() == "TRADEIN" or row["Type"].strip() == "TRADEOUT":
            if row["Trade ID"].strip() not in uniqueTrades:
                uniqueTrades.append(row["Trade ID"].strip())
            if row["Card Name"] == cashConstant or row["Card Name"] == "CASH":
                tradeStore = [row["Trade ID"].strip(), row["Type"].strip(), row["Price"].strip(), cashConstant, reformattedDate]
            else:
                tradeStore = [row["Trade ID"].strip(), row["Type"].strip(), reformattedDate, row["Price"].strip(), row["Quantity"].strip(), row["Card Name"].strip()]

                # SKU pull for TRADES
                for cards, prints in skuDictionary.items():
                    if row["Card Name"].strip() == cards:
                        for sets, variants in prints.items():
                            if row["Set Name"].strip() == sets:
                                for editions, conditions in variants.items():
                                    if int(row["Edition"].strip()) == int(editions):
                                        for condition, sku in conditions.items():
                                            if int(row["Condition"].strip()) == int(condition):
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
        temp["Type"] = row["Type"].strip()
        if temp["Type"] == "BUY":
            temp["Price"] = -abs(float(row["Price"].strip()))
        elif temp["Type"] == "SELL":
            temp["Price"] = abs(float(row["Price"].strip()))
        else:
            temp["Price"] = None

        # No fractional shares of cards allowed, for quantity
        temp["Quantity"] = int(row["Quantity"].strip())
        temp["Name"] = row["Card Name"].strip()

        # SKU pull for BUY/SELL
        for cards, prints in skuDictionary.items():
            if row["Card Name"].strip() == cards:
                for sets, variants in prints.items():
                    if row["Set Name"].strip() == sets:
                        for editions, conditions in variants.items():
                            if int(row["Edition"].strip()) == int(editions):
                                for condition, sku in conditions.items():
                                    if int(row["Condition"].strip()) == int(condition):
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
        except:
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
                    tempSet["Price"] = float(trade[2])
                    tempSet["Quantity"] = 1
                    tempSet["SKU"] = cashConstant
                    tempSet["Date"] = trade[4]
                else:
                    tempSet["Price"] = float(trade[3])
                    tempSet["Quantity"] = int(trade[4])
                    tempSet["Name"] = trade[5]
                    tempSet["SKU"] = trade[6]
                tempTradesIn.append(tempSet)
            elif trade[1] == "TRADEOUT":
                tempSet = {}
                if trade[3] == cashConstant:
                    tempSet["Price"] = -float(trade[2])
                    tempSet["Quantity"] = 1
                    tempSet["SKU"] = cashConstant
                    tempSet["Date"] = trade[4]
                else:
                    tempSet["Price"] = float(trade[3])
                    tempSet["Quantity"] = int(trade[4])
                    tempSet["Name"] = trade[5]
                    tempSet["SKU"] = trade[6]
                tempTradesOut.append(tempSet)
    tempSemi["Type"] = "TRADE"
    tempSemi["In"] = tempTradesIn
    tempSemi["Out"] = tempTradesOut

    try:
        transactionDictionary[tradeDate].append(tempSemi)
    except:
        transactionDictionary[tradeDate] = [tempSemi]

transactionSort(transactionDictionary) # Sorted for parse order: (1) Buy, (2) Trade, (3) Sell

json.dump(transactionDictionary, open("transactions.txt", 'w'))