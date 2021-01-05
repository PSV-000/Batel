import json
import pprint
from datetime import datetime
from inventoryMethods import *
from collections import deque
from copy import deepcopy

transactions = json.load(open("transactions.txt"))
inventory = {}
sales = []
totalSales = {} # No use yet, but required to total return metrics

specified_order = False # This is a filler, for the transactionReader

# Accounting rules, tentatively prefer FIFO as base case
FIFO = True
LIFO = not FIFO

# Inventory creation - parse through all transactions
for key in sorted(transactions.keys()): # Sorted keys matter here because inventory creation follows strict sequence
    #convertDate = datetime.strptime(key, "%Y/%m/%d")
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

                # Cost detail for sales array
                tempDetailSKU = {}
                tempDetailSKU["Cost"] = []

                while removeCount < transaction["Quantity"]:
                    # Move items from inventory to sales array
                    tempDetailSKU["Cost"].append(deepcopy(inventory[transaction["SKU"]][0]))
                    tempDetailSKU["Cost"][costIndex]["Quantity"] = min(inventory[transaction["SKU"]][0]["Quantity"], transaction["Quantity"])
                    costIndex += 1

                    # Remove sold items from inventory
                    incrementalRemoved = min(inventory[transaction["SKU"]][0]["Quantity"], transaction["Quantity"] - removeCount)
                    removeCount += incrementalRemoved
                    if incrementalRemoved >= inventory[transaction["SKU"]][0]["Quantity"]:
                        inventory[transaction["SKU"]].pop(0)
                        if inventory[transaction["SKU"]] == []:
                            inventory.pop(transaction["SKU"], None) # Clear dead items from inventory - "Active Inventory"
                    else:
                        inventory[transaction["SKU"]][0]["Quantity"] -= incrementalRemoved

                # Sales detail for sales array
                tempSaleDetail = {}
                tempSaleDetail[key] = transaction["Price"]
                tempSaleDetail["Quantity"] = transaction["Quantity"]
                tempDetailSKU["Sale"] = [tempSaleDetail]
                tempDetailSKU["SKU"] = transaction["SKU"]
                sales.append(tempDetailSKU)

            # Add subtype/subcategory for presale
        elif transaction["Type"] == "TRADE":
            processTrade(transaction, inventory, specified_order, sales)
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

'''avgCost = []
for sku, prices in inventory.items():
    avgCost.append(averageCost(prices))
print("Inventory Average Cost=====================================")
pprint.pprint(avgCost)'''

# MOIC functions properly
piFin = []
piFinCount = 0
saleCount = 0
for salesDetail in sales:
    piFin.append(profitOrLoss(salesDetail))
    piFinCount += profitOrLoss(salesDetail)
    saleCount += 1
print("Sales Plus (MOIC)=====================================")
pprint.pprint(piFin)
print(piFinCount)
print(saleCount)