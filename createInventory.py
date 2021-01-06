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
    for transaction in transactions[key]:
        if transaction["Type"] == "BUY":
            # Add item to inventory
            basis = {key: transaction["Price"], "Quantity": transaction["Quantity"]}
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
                tempDetailSKU = {"Cost": []}

                while removeCount < transaction["Quantity"]:
                    # Move items from inventory to sales array
                    inventoryClone = deepcopy(inventory[transaction["SKU"]][0])
                    tempDetailSKU["Cost"].append(inventoryClone)
                    incrementalRemoved = min(inventoryClone["Quantity"], transaction["Quantity"] - removeCount)
                    tempDetailSKU["Cost"][costIndex]["Quantity"] = deepcopy(incrementalRemoved)
                    costIndex += 1

                    # Remove sold items from inventory
                    removeCount += incrementalRemoved
                    if incrementalRemoved >= inventory[transaction["SKU"]][0]["Quantity"]:
                        inventory[transaction["SKU"]].pop(0)
                        if inventory[transaction["SKU"]] == []:
                            inventory.pop(transaction["SKU"], None) # Maintain "Active Inventory"
                    else:
                        inventory[transaction["SKU"]][0]["Quantity"] -= incrementalRemoved # Reduce inventory quantity

                # Sale detail for sales array
                tempSaleDetail = {
                    key: transaction["Price"],
                    "Quantity": transaction["Quantity"]
                    }
                tempDetailSKU["Sale"] = [tempSaleDetail]
                tempDetailSKU["SKU"] = transaction["SKU"]
                sales.append(tempDetailSKU)

            # Add subtype/subcategory for presale, or create separate - presales do not work with IRR calculations
        elif transaction["Type"] == "TRADE":
            processTrade(transaction, inventory, specified_order, sales)
        else:
            print("Not a valid transaction")

# Testing
print("Transactions=====================================")
pprint.pprint(transactions)
print("Inventory=====================================")
pprint.pprint(inventory)
print("Sales=====================================")
pprint.pprint(sales)

json.dump(inventory, open("inventory.txt", 'w'))
json.dump(sales, open("sales.txt", 'w'))
