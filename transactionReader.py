import json
import pprint
import csv
from datetime import datetime
from inventoryMethods import *

skuDictionary = json.load(open("skuDictionary.txt"))
skuDictionaryReverse = json.load(open("skuDictionaryReverse.txt")) # Unnecessary for this segment

sampleSet = {} # Sample transaction dictionary
sampleTrades = [] # Temporary storage of trades
uniqueTrades = []

with open("sample_transactions.csv", newline = '') as sample:
    reader = csv.DictReader(sample)
    for row in reader:
        temp = {}
        new_date = row["Date"].strip()

        # Reformat datetime object as a string to use as a key for dictionary, year first to properly sort
        reverseDate = datetime.strptime(new_date, "%m/%d/%Y")
        reformattedDate = reverseDate.strftime("%Y/%m/%d")

        # Temporarily set aside trade information
        if row["Type"].strip() == "TRADEIN" or row["Type"].strip() == "TRADEOUT":
            if row["Trade ID"].strip() not in uniqueTrades:
                uniqueTrades.append(row["Trade ID"].strip())
            tradeStore = [row["Trade ID"].strip(), row["Type"].strip(), reformattedDate, row["Price"].strip(), row["Quantity"].strip(), row["Card Name"].strip()]

            # SKU pull - Trades
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
            temp["Price"] = None # For trade and errors

        # No fractional shares of cards allowed, for quantity
        temp["Quantity"] = int(row["Quantity"].strip())
        temp["Name"] = row["Card Name"].strip()

        # SKU pull - Buy/Sell
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

        # Add to sample transaction dictionary
        try:
            sampleSet[reformattedDate].append(temp)
        except:
            sampleSet[reformattedDate] = [temp]

# Append trade information
for unique in uniqueTrades:
    tempTradesIn = []
    tempTradesOut = []
    tempSemi = {}
    tradeDate = ""
    for trade in sampleTrades:
        if trade[0] == unique:
            tradeDate = trade[2]
            if trade[1] == "TRADEIN": # Need to edit these for cash
                tempSet = {}
                tempSet["Price"] = float(trade[3])
                tempSet["Quantity"] = int(trade[4])
                tempSet["Name"] = trade[5]
                tempSet["SKU"] = trade[6]
                tempTradesIn.append(tempSet)
            elif trade[1] == "TRADEOUT":
                tempSet = {}
                tempSet["Price"] = float(trade[3])
                tempSet["Quantity"] = int(trade[4])
                tempSet["Name"] = trade[5]
                tempSet["SKU"] = trade[6]
                tempTradesOut.append(tempSet)
    tempSemi["Type"] = "TRADE"
    tempSemi["In"] = tempTradesIn
    tempSemi["Out"] = tempTradesOut
    try:
        sampleSet[tradeDate].append(tempSemi)
    except:
        sampleSet[tradeDate] = [tempSemi]

# Sequence as (1) Buy, (2) Trade, (3) Sell
# Consider building trade sequencing logic (e.g. push failed trades to the end of trade queue)
transactionSort(sampleSet)

pprint.pprint(sampleSet)

# Sample return metrics
MOIC = 0
for date, transactions in sampleSet.items():
    for transaction in transactions:
        try:
            MOIC += ( transaction["Price"] * transaction["Quantity"] )
        except (TypeError, KeyError):
            pass
print(MOIC)

json.dump(sampleSet, open("sample_transactions.txt", 'w'))