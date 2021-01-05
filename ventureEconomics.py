import json
import pprint
from inventoryMethods import *

transactionDictionary = json.load(open("transactions.txt"))
pprint.pprint(transactionDictionary)

# Money on Invested Capital = Total Bought - Total Sold
# Positive MOIC indicates operations have yielded above breakeven point
# Consider making this a method file instead of a script
MOIC = 0
for dated, transactions in transactionDictionary.items():
    for transaction in transactions:
        try:
            MOIC += (transaction["Price"] * transaction["Quantity"])
        except (TypeError, KeyError):
            if transaction["Type"] == "TRADE":
                for tradeIn in transaction["In"]:
                    if tradeIn["SKU"] == cashConstant:
                        MOIC += (tradeIn["Price"] * tradeIn["Quantity"])
                for tradeOut in transaction["Out"]:
                    if tradeOut["SKU"] == cashConstant:
                        MOIC += (tradeOut["Price"] * tradeOut["Quantity"]) # Price is already negative in transactions
            else:
                pass
print(MOIC)