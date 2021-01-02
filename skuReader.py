import json
import pprint
import time

skuEvery = json.load(open("allCardsPidSku.txt"))

skuDictionary = {}
skuDictionaryReverse = {}

for key, value in skuEvery.items():
    for setInd in value:
        for butters in setInd[2]:
            try:
                skuDictionaryReverse[butters["skuId"]].append([key, setInd[0], butters["productId"], butters["printingId"], butters["conditionId"]])
            except:
                skuDictionaryReverse[butters["skuId"]] = [key, setInd[0], butters["productId"], butters["printingId"], butters["conditionId"]]

json.dump(skuDictionaryReverse, open("skuDictionaryReverse.txt", 'w'))

for sku, array in skuDictionaryReverse.items():
    tempBase = {}
    tempBase[array[4]] = sku # { Condition : SKU }
    tempEdit = {}
    tempEdit[array[3]] = [tempBase] # { Edition : { Condition : SKU } }
    tempSet = {}
    tempSet[array[1]] = tempEdit # { Set : { Edition : { Condition : SKU } } }

    try:
        skuDictionary[array[0]][array[1]][array[3]].append(tempBase) # Append new condition/SKU to editions
    except:
        try:
            skuDictionary[array[0]][array[1]][array[3]] = [tempBase] # Otherwise try to set first condition/SKU assignment to edition
        except:
            try:
                skuDictionary[array[0]][array[1]].append(tempEdit) # Otherwise, add entire new edition set
            except:
                try:
                    skuDictionary[array[0]][array[1]] = tempEdit
                except:
                    try:
                        skuDictionary[array[0]].append(tempSet)
                    except:
                        skuDictionary[array[0]] = tempSet

for cards, prints in skuDictionary.items():
    for sets, variants in prints.items():
        for editions, conditions in variants.items():
            temp = {}
            for item in conditions:
                for key, value in item.items():
                    temp[key] = value
            variants[editions] = temp

json.dump(skuDictionary, open("skuDictionary.txt", 'w'))