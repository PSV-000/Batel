import json
import pprint
from inventoryMethods import *
import numpy
import pandas
from datetime import datetime

# Table of Contents (Methods)
    # getUnitMOIC
    # getMOIC
    # getUnitXIRR
    # getXIRR

def getUnitMOIC(saleDictionary, dollarOrPercent):
    # Money on Invested Capital ($) = Total Sold - Total Bought
    # Money on Invested Capital (%) = (Total Sold - Total Bought) / Total Bought
    # Positive MOIC indicates operations have yielded above breakeven point
    if dollarOrPercent != "$" and dollarOrPercent != "%":
        return None
    MOIC = 0
    totalBasis = 0
    avgSale = averageCost(saleDictionary["Sale"])
    avgCost = averageCost(saleDictionary["Cost"])
    MOIC += (avgSale - avgCost) * totalQuantity(saleDictionary["Cost"])
    totalBasis += avgCost * totalQuantity(saleDictionary["Cost"])

    if dollarOrPercent == "$":
        return MOIC
    elif dollarOrPercent == "%":
        return MOIC / -totalBasis

def getMOIC(allTransactionSales, dollarOrPercent):
    if dollarOrPercent != "$" and dollarOrPercent != "%":
        return None
    MOIC = 0
    totalBasis = 0

    if type(allTransactionSales) is list: # MOIC for sales only
        for salesTransaction in allTransactionSales:
            avgSale = averageCost(salesTransaction["Sale"])
            avgCost = averageCost(salesTransaction["Cost"])
            MOIC += (avgSale - avgCost) * totalQuantity(salesTransaction["Cost"])
            totalBasis += avgCost * totalQuantity(salesTransaction["Cost"])
    elif type(allTransactionSales) is dict: # MOIC for all transactions
        for dated, transactions in allTransactionSales.items():
            for transaction in transactions:
                try:
                    MOIC += (transaction["Price"] * transaction["Quantity"])
                    if (transaction["Price"] * transaction["Quantity"]) < 0:
                        totalBasis += (transaction["Price"] * transaction["Quantity"])
                except (TypeError, KeyError):
                    if transaction["Type"] == "TRADE":
                        for tradeIn in transaction["In"]:
                            if tradeIn["SKU"] == cashConstant:
                                MOIC += (tradeIn["Price"] * tradeIn["Quantity"])
                        for tradeOut in transaction["Out"]:
                            if tradeOut["SKU"] == cashConstant:
                                MOIC += (tradeOut["Price"] * tradeOut["Quantity"]) # Price is already negative
                                totalBasis += (tradeOut["Price"] * tradeOut["Quantity"])
                    else:
                        pass
    if dollarOrPercent == "$":
        return MOIC
    elif dollarOrPercent == "%":
        return MOIC / -totalBasis

def getUnitXIRR(transactionInput, guess = 0.05):
    # Internal Rate of Return = expected annual rate of growth of investment
    # XIRR calculates IRR for nonperiodic cash flows
    # Unit IRR main purpose is to process individual sales

    if type(transactionInput) is dict:
        cashFlows = joinPrice(arrayPriceDates(transactionInput["Cost"]), arrayPriceDates(transactionInput["Sale"]))
    else:
        return None

    # Pandas Dataframe supports IRR calculation
    amountsPandas = []
    datesPandas = []
    for dateEntry in sorted(cashFlows.keys()):
        datesPandas.append(datetime.strptime(dateEntry, "%Y/%m/%d"))
        amountsPandas.append(cashFlows[dateEntry])

    date_column = "dates"
    amount_column = "amounts"
    inputPandas = {
        date_column: pandas.Series(datesPandas),
        amount_column: pandas.Series(amountsPandas)
        }
    salesPandas = pandas.DataFrame(inputPandas)
    salesPandas = salesPandas.sort_values(by=date_column).reset_index(drop=True)

    amounts = salesPandas[amount_column].values
    dates = salesPandas[date_column].values

    years = numpy.array(dates - dates[0], dtype='timedelta64[D]').astype(int) / 365

    step = 0.05
    epsilon = 0.0001
    limit = 1000
    residual = 1

    # Test for direction of cashflows
    disc_val_1 = numpy.sum(amounts / ((1 + guess) ** years))
    disc_val_2 = numpy.sum(amounts / ((1.05 + guess) ** years))
    mul = 1 if disc_val_2 < disc_val_1 else -1

    # Calculate XIRR
    for i in range(limit):
        prev_residual = residual
        residual = numpy.sum(amounts / ((1 + guess) ** years))
        if abs(residual) > epsilon:
            if numpy.sign(residual) != numpy.sign(prev_residual):
                step /= 2
            guess = guess + step * numpy.sign(residual) * mul
        else:
            return guess  # Expressed as a decimal

def getXIRR(transactionInput, guess = 0.05):
    # Non-Unit IRR main purpose is to process portfolios
    cashFlows = {}

    if type(transactionInput) is list: # Intended for sales array
        # Strip sales array into dictionary of {Date: Cash Flow}
        for resolution in transactionInput:
            for cost in resolution["Cost"]:
                for date, flow in cost.items():
                    if date not in nonPriceKeys:
                        try:
                            cashFlows[date] += flow
                        except KeyError:
                            cashFlows[date] = flow
            for sale in resolution["Sale"]:
                for date, flow in sale.items():
                    if date not in nonPriceKeys:
                        try:
                            cashFlows[date] += flow
                        except KeyError:
                            cashFlows[date] = flow

    elif type(transactionInput) is dict: # Intended for transaction dictionary
        # Strip transactional cash movement into a dictionary of {Date: Cash Flow}
        for resolutionDates, resolutionAmounts in transactionInput.items():
            netCashMovement = 0
            for resolutions in resolutionAmounts:
                if resolutions["Type"] == "BUY" or resolutions["Type"] == "SELL":
                    netCashMovement += resolutions["Price"] * resolutions["Quantity"]
                elif resolutions["Type"] == "TRADE":
                    for tradeIn in resolutions["In"]:
                        if tradeIn["SKU"] == cashConstant:
                            netCashMovement += tradeIn["Price"] * tradeIn["Quantity"]
                    for tradeOut in resolutions["Out"]:
                        if tradeOut["SKU"] == cashConstant:
                            netCashMovement += tradeOut["Price"] * tradeOut["Quantity"]
            try:
                cashFlows[resolutionDates] += netCashMovement
            except KeyError:
                cashFlows[resolutionDates] = netCashMovement

    # Pandas Dataframe supports IRR calculation
    amountsPandas = []
    datesPandas = []
    for dateEntry in sorted(cashFlows.keys()):
        datesPandas.append(datetime.strptime(dateEntry, "%Y/%m/%d"))
        amountsPandas.append(cashFlows[dateEntry])

    date_column = "dates"
    amount_column = "amounts"
    inputPandas = {
        date_column: pandas.Series(datesPandas),
        amount_column: pandas.Series(amountsPandas)
        }
    salesPandas = pandas.DataFrame(inputPandas)
    salesPandas = salesPandas.sort_values(by=date_column).reset_index(drop=True)

    amounts = salesPandas[amount_column].values
    dates = salesPandas[date_column].values

    years = numpy.array(dates-dates[0], dtype='timedelta64[D]').astype(int)/365

    step = 0.05
    epsilon = 0.0001
    limit = 1000
    residual = 1

    # Test for direction of cashflows
    disc_val_1 = numpy.sum(amounts/((1+guess)**years))
    disc_val_2 = numpy.sum(amounts/((1.05+guess)**years))
    mul = 1 if disc_val_2 < disc_val_1 else -1

    # Calculate IRR
    for i in range(limit):
        prev_residual = residual
        residual = numpy.sum(amounts/((1+guess)**years))
        if abs(residual) > epsilon:
            if numpy.sign(residual) != numpy.sign(prev_residual):
                step /= 2
            guess = guess + step * numpy.sign(residual) * mul
        else:
            return guess # Expressed as a decimal

# Testing methods
sales = json.load(open("sales.txt"))
print("SALES MOIC")
print(getMOIC(sales, "$"))
print(getMOIC(sales, "%"))
print("SALES IRR")
print(getXIRR(sales))

trans = json.load(open("transactions.txt"))
print("TRANSACTIONS MOIC")
print(getMOIC(trans, "$"))
print(getMOIC(trans, "%"))
print("TRANSACTIONS IRR")
print(getXIRR(trans))

for sale in sales:
    print(sale["SKU"])
    print("Unit MOIC")
    print(getUnitMOIC(sale, "$"))
    print(getUnitMOIC(sale, "%"))
    print("Unit IRR")
    print(getUnitXIRR(sale))
