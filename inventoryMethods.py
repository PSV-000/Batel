import pprint
from datetime import datetime

def totalQuantity(pricingArray):
    quantityCount = 0
    for unit in pricingArray:
        quantityCount += unit["Quantity"]
    return quantityCount

def totalBasis(costDictionary):
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
        indCost = totalBasis(unit)
        totalUnits += unit["Quantity"]
        allCosts.append(indCost * unit["Quantity"])
    totalCost = 0
    for eachCost in allCosts:
        totalCost += eachCost
    if totalUnits == 0:
        return None
    else:
        return totalCost/totalUnits
