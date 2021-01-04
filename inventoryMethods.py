import pprint
from datetime import datetime
from copy import deepcopy

def totalQuantity(pricingArray):
    quantityCount = 0
    for unit in pricingArray:
        quantityCount += unit["Quantity"]
    return quantityCount

def totalUnitBasis(costDictionary):
    basis = 0
    for key in sorted(costDictionary.keys()):
        if key == "Quantity" or key == "SKU":
            pass
        else:
            basis += costDictionary[key]
    return basis

def averageCost(pricingArray):
    allCosts = []
    totalUnits = 0
    for unit in pricingArray:
        indCost = totalUnitBasis(unit)
        totalUnits += unit["Quantity"]
        allCosts.append(indCost * unit["Quantity"])
    totalCost = 0
    for eachCost in allCosts:
        totalCost += eachCost
    if totalUnits == 0:
        return None
    else:
        return totalCost/totalUnits

def profitOrLoss(saleDictionary):
    MOIC = averageCost(saleDictionary["Sale"]) + averageCost(saleDictionary["Cost"]) # Addition because average costs are negative
    try:
        return saleDictionary["Sale"][0]["Quantity"] * MOIC # Items are sold at one price, can use average unit price
    except TypeError:
        return 0

def transactionSort(transactions):
    for dated, transact in transactions.items():
        newList = []
        buyTrack = 0
        tradeTrack = 0
        for trans in transact:
            if trans["Type"] == "BUY":
                newList.insert(0, trans)
                buyTrack += 1
            elif trans["Type"] == "TRADE":
                newList.insert(buyTrack + tradeTrack, trans)
                tradeTrack += 1
            elif trans["Type"] == "SELL":
                newList.append(trans)
        transactions[dated] = newList

def processTrade(tradeDictionary, inventory, orderBoolean, sales): # Needs adjustment for cash
    realBasis = 0
    realPrices = []
    costIndex = 0
    for tradesOut in tradeDictionary["Out"]:
        # Look in inventory for item
        removeCount = 0

        for inv in inventory[int(tradesOut["SKU"])]:
            if orderBoolean:
                orderBoolean = False # Filler action - should search inventory for items to move to sales
            else:
                while removeCount < tradesOut["Quantity"]:
                    # Move items from inventory to temporary trade array
                    realPrices.append(deepcopy(inv)) # Require deep copy to not overwrite inventory quantity
                    realPrices[costIndex]["Quantity"] = min(inv["Quantity"], tradesOut["Quantity"])
                    costIndex += 1

                    # Remove traded items from inventory
                    incrementalRemoved = min(inv["Quantity"], tradesOut["Quantity"] - removeCount)
                    removeCount += incrementalRemoved
                    if incrementalRemoved >= inv["Quantity"]:
                        inventory[int(tradesOut["SKU"])].pop(0)
                        if inventory[int(tradesOut["SKU"])] == []:
                            inventory.pop(int(tradesOut["SKU"]), None) # Clear dead items from inventory - "Active Inventory"
                    else:
                        inv["Quantity"] -= tradesOut["Quantity"] #- removeCount # Is this necessary

    # Calculate the pass-through cost of incoming trades
    realTotalBasis = {}
    for priceCombo in realPrices:
        for priceDates in sorted(priceCombo.keys()):
            if priceDates == "Quantity" or priceDates == "SKU":
                pass
            else:
                try:
                    realTotalBasis[priceDates] += ( priceCombo[priceDates] * priceCombo["Quantity"] )
                except:
                    realTotalBasis[priceDates] = ( priceCombo[priceDates] * priceCombo["Quantity"] )

    # Nominal basis required to calculate pro-rata share of incoming trade basis
    # Will require a cash adjustment
    nominalBasis = 0
    for tradesIn in tradeDictionary["In"]:
        nominalBasis += tradesIn["Price"] * tradesIn["Quantity"]

    for tradesIn in tradeDictionary["In"]:
        tempInput = {}
        tempInput["Quantity"] = tradesIn["Quantity"]

        for priceDates in realTotalBasis.keys():
            try:
                tempInput[priceDates] += (tradesIn["Price"] / nominalBasis * deepcopy(realTotalBasis[priceDates]))
            except:
                tempInput[priceDates] = (tradesIn["Price"] / nominalBasis * deepcopy(realTotalBasis[priceDates]))

        # Incoming trades are added to inventory
        try:
            inventory[int(tradesIn["SKU"])].append(tempInput)
        except:
            inventory[int(tradesIn["SKU"])] = [tempInput]

