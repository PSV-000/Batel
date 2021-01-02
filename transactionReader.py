import json
import pprint
import csv
from datetime import datetime

skuDictionary = json.load(open("skuDictionary.txt"))
skuDictionaryReverse = json.load(open("skuDictionaryReverse.txt"))

sampleSet = {} # Sample transaction dictionary
count = 0

with open("sample_transactions.csv", newline = '') as sample:
    reader = csv.DictReader(sample)
    for row in reader:
        temp = {}
        new_date = row["Date"].strip()

        # Need to reformat to show year as YY instead of YYYY for datetime to properly read
        convertDate = datetime.strptime(new_date[:len(new_date)-2], "%m/%d/%y")

        # Need to reformat datetime object as a string to use as a key for dictionary
        reformatted = convertDate.strftime("%d/%m/%Y")
        temp["Type"] = row["Type"].strip()

        # Transaction type determines sign of price
        if temp["Type"] == "BUY":
            temp["Price"] = -abs(float(row["Price"].strip()))
        elif temp["Type"] == "SELL":
            temp["Price"] = abs(float(row["Price"].strip()))
        else:
            temp["Price"] = None # For trade and errors

        # No fractional shares of cards allowed, for quantity
        temp["Quantity"] = int(row["Quantity"].strip())
        temp["Name"] = row["Card Name"].strip()

        # SKU pull
        for cards, prints in skuDictionary.items():
            if temp["Name"] == cards:
                for sets, variants in prints.items():
                    if row["Set Name"].strip() == sets:
                        for editions, conditions in variants.items():
                            if int(row["Edition"].strip()) == int(editions):
                                for condition, sku in conditions.items():
                                    if int(row["Condition"].strip()) == int(condition):
                                        temp["SKU"] = sku
                                        count += 1
                                        break
                                    else:
                                        pass
                            else:
                                pass
                    else:
                        pass
            else:
                pass

        # Add to sample transaction dictionary
        try:
            sampleSet[reformatted].append(temp)
        except:
            sampleSet[reformatted] = [temp]

pprint.pprint(sampleSet)
print(count)

# Sample return metrics
MOIC = 0
for date, transactions in sampleSet.items():
    for transaction in transactions:
        MOIC += ( transaction["Price"] * transaction["Quantity"] )
print(MOIC)

json.dump(sampleSet, open("sample.txt", 'w'))