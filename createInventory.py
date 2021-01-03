import json
import pprint
from datetime import datetime
from inventoryMethods import *
from collections import deque

transactions = json.load(open("sample_transactions.txt"))
inventory = {}
sales = []
totalSales = {} # Can't think of how this is used yet

specified_order = False # This is a filler, for the transactionReader
FIFO = True
LIFO = not FIFO

for key in sorted(transactions.keys()):
    convertDate = datetime.strptime(key, "%Y/%m/%d")
    #print(convertDate)
    for transaction in transactions[key]:
        if transaction["Type"] == "BUY":
            # Add item to inventory
            basis = {}
            basis[key] = transaction["Price"]
            basis["Quantity"] = transaction["Quantity"]
            try:
                if FIFO:
                    inventory[transaction["SKU"]].append(basis)
                elif LIFO:
                    inventory[transaction["SKU"]].insert(0, basis)
            except KeyError:
                inventory[transaction["SKU"]] = [basis]
        elif transaction["Type"] == "SELL":
            # Remove item from inventory
            if specified_order:
                specified_order = False # Filler action - should search inventory for items to move to sales
            else:
                costIndex = 0
                removeCount = 0
                tempDetailSKU = {}
                tempDetailSKU["Cost"] = []

                while removeCount < transaction["Quantity"]:
                    # Move items from inventory to sales array
                    tempDetailSKU["Cost"].append(inventory[transaction["SKU"]][0])
                    tempDetailSKU["Cost"][costIndex]["Quantity"] = min(inventory[transaction["SKU"]][0]["Quantity"], transaction["Quantity"])
                    costIndex += 1

                    # Remove sold items from inventory
                    incrementalRemoved = min(inventory[transaction["SKU"]][0]["Quantity"], transaction["Quantity"] - removeCount)
                    removeCount += incrementalRemoved
                    if incrementalRemoved >= inventory[transaction["SKU"]][0]["Quantity"]:
                        inventory[transaction["SKU"]].pop(0)
                    else:
                        inventory[transaction["SKU"]][0]["Quantity"] -= transaction["Quantity"]

                # Sale detail for sales array
                tempSaleDetail = {}
                tempSaleDetail[key] = transaction["Price"]
                tempSaleDetail["Quantity"] = transaction["Quantity"]
                tempDetailSKU["Sale"] = [tempSaleDetail]
                tempDetailSKU["SKU"] = transaction["SKU"]
                sales.append(tempDetailSKU)

            # Add subtype for presale
        elif transaction["Type"] == "TRADE":
            # Do trade things
            # Add subtype for cash-in/cash-out/neutral/cash-out-sale
            print("TRADE")
        else:
            print("Not a valid transaction")

print("Transactions=====================================")
pprint.pprint(transactions)
print("Inventory=====================================")
pprint.pprint(inventory)
print("Sales=====================================")
pprint.pprint(sales)
json.dump(inventory, open("sample_inventory.txt", 'w'))
json.dump(sales, open("sample_sales.txt", 'w'))

avgCost = []
for sku, prices in inventory.items():
    avgCost.append(averageCost(prices))
print("Inventory Average Cost=====================================")
pprint.pprint(avgCost)

# MOIC functions properly
piFin = []
piFinCount = 0
for salesDetail in sales:
    piFin.append(salesDetail["Sale"][0]["Quantity"] * (averageCost(salesDetail["Sale"]) + averageCost(salesDetail["Cost"])))
    piFinCount += salesDetail["Sale"][0]["Quantity"] * (averageCost(salesDetail["Sale"]) + averageCost(salesDetail["Cost"]))
print("Sales Plus (MOIC)=====================================")
pprint.pprint(piFin)
print(piFinCount)