from flask import Flask, jsonify, render_template, request
from elasticsearch import Elasticsearch
import skfuzzy as fuzz
import numpy as np
from collections import Counter
import json
from collections import defaultdict
from helper import Backend_Helper
from binaryFunctions import binary_search


es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
app = Flask(__name__) #Create the flask instance, __name__ is the name of the current Python module


# priceDict = {}
# hdDict = {}
# productTitleDict = {}
# allDocs ={}

@app.route('/api/search', methods=['POST'])
def searchBinary():
    data = request.get_json()
    clean_data = Backend_Helper.clean_frontend_json(data)

    bin_obj = binary_search.BinarySearch();

    query = bin_obj.createBinarySearchQuery(clean_data)
    res = es.search(index="amazon", body=query)

    final_result = [Backend_Helper.refineResult(res),data]


    return jsonify(final_result)

@app.route('/api/search/alexa', methods=['POST'])
def alexa_search():

    data = request.get_json()
    intent = data["intent"]
    intent_variable = data["intentVariable"]
    intent_variable_value = data[data["intentVariable"]][data["intentVariable"]+"Value"]
    #TODO: boolean method for intentVariable
    #TODO: delete intentVariable with its Value
    del data[intent_variable][intent_variable+"Value"]

    data[intent_variable].update({"intent":intent,"value":intent_variable_value})

    data[intent_variable]["weight"] = 5

    del data["intent"]
    del data["intentVariable"]

    clean_data = Backend_Helper.clean_frontend_json(data)
    bin_obj = binary_search.BinarySearch();
    query = bin_obj.createBinarySearchQuery(clean_data)
    res = es.search(index="amazon", body=query)

    print(query)



    return jsonify(Backend_Helper.refineResult(res))

@app.route('/api/<asin>', methods =['GET'])
def getElementByAsin(asin):
    product = es.search(index='amazon', body ={
                                                "query":{
                                                    "match":{
                                                        "asin" : asin
                                                      }
                                                    },
                                                  "size":1
                                              })
    product = Backend_Helper.refineResult(product)
    return jsonify(product)


@app.route('/api/sample', methods=['GET'])
def getSample():
  allDocs = es.search(index="amazon", body={
    "query": {
      "match": {
        "avgRating": 5
      }
    },
    "size": 10
  })

  outputProducts = Backend_Helper.refineResult(allDocs)
  return jsonify(outputProducts)  # original from alfred

# def createBinarySearchQuery(fieldNameToValueDict) :
#     body = defaultdict(lambda: defaultdict(lambda : defaultdict(lambda: defaultdict(dict))))
#
#     terms = []
#     ranges = []
#     alexa = []
#     sameFieldMultpleValues = []
#     hardDriveSizeValues = []
#
#
#     boolean_ssd_and_hdd = False
#
#     if "hardDriveSize" in fieldNameToValueDict and len(fieldNameToValueDict["hardDriveSize"].keys()) > 1:
#         if "hardDriveType" not in fieldNameToValueDict or fieldNameToValueDict["hardDriveType"].lower() == "hybrid":
#             hardDriveSize_value = fieldNameToValueDict["hardDriveSize"]
#             del fieldNameToValueDict["hardDriveSize"]
#             fieldNameToValueDict.update({"ssdSize":hardDriveSize_value,"hddSize" :hardDriveSize_value})
#             boolean_ssd_and_hdd = True
#         elif fieldNameToValueDict["hardDriveType"].lower() == "ssd" :
#             hardDriveSize_value = fieldNameToValueDict["hardDriveSize"]
#             del fieldNameToValueDict["hardDriveSize"]
#             fieldNameToValueDict.update({"ssdSize":hardDriveSize_value})
#         else :
#             hardDriveSize_value = fieldNameToValueDict["hardDriveSize"]
#             del fieldNameToValueDict["hardDriveSize"]
#             fieldNameToValueDict.update({"hddSize" :hardDriveSize_value})
#
#     if boolean_ssd_and_hdd :
#         #Discrete value with ssd and hdd
#         if "hardDriveSizeValue" in fieldNameToValueDict["hddSize"] :
#             hardDriveSizeValues.append({"term" : {"ssdSize" : fieldNameToValueDict["ssdSize"]["hardDriveSizeValue"]}})
#             hardDriveSizeValues.append({"term" : {"hddSize" : fieldNameToValueDict["hddSize"]["hardDriveSizeValue"]}})
#             #ranged value with ssd and hdd
#         else :
#             if "minValue" in fieldNameToValueDict["hddSize"] and  "maxValue" in fieldNameToValueDict["hddSize"] :
#                 minValue = fieldNameToValueDict["hddSize"]["minValue"]
#                 maxValue = fieldNameToValueDict["hddSize"]["maxValue"]
#                 hardDriveSizeValues.append({"range" : {"hddSize" : {"lte" : maxValue,"gte" : minValue }}})
#                 hardDriveSizeValues.append({"range" : {"ssdSize" : {"lte" : maxValue,"gte" : minValue }}})
#
#             elif "minValue" in fieldNameToValueDict["hddSize"] :
#                 minValue = fieldNameToValueDict["hddSize"]["minValue"]
#                 hardDriveSizeValues.append({"range" : {"hddSize" : {"gte" : minValue }}})
#                 hardDriveSizeValues.append({"range" : {"ssdSize" : {"gte" : minValue }}})
#
#
#             elif "maxValue" in fieldNameToValueDict[fieldName] :
#                 maxValue = fieldNameToValueDict["hddSize"]["maxValue"]
#                 hardDriveSizeValues.append({"range" : {"hddSize" : {"lte" : maxValue}}})
#                 hardDriveSizeValues.append({"range" : {"hddSize" : {"lte" : maxValue}}})
#
#     for fieldName in fieldNameToValueDict :
#
#         if not fieldNameToValueDict[fieldName] or fieldName =="ssdSize" or fieldName == "hddSize" :
#             continue
#
#         #normal match
#         #Ranged terms, example : ram : { minRam : 2,maxRam : 4}
#         #If that's the case, then search for minRam and maxRam in fieldNameToValueDict, get them and add range to the query
#         value_field_name = fieldName+"Value"
#         if type(fieldNameToValueDict[fieldName]) is dict and ("minValue" in fieldNameToValueDict[fieldName] or "maxValue" in fieldNameToValueDict[fieldName]) :
#             #Extract name of field, and set the name of min and max values to minField and maxField, example : minRam and maxRam.
#             #minValueName = "min"+fieldName[0].upper()+fieldName[1:]
#             #maxValueName = "max"+fieldName[0].upper()+fieldName[1:]
#             if not fieldNameToValueDict[fieldName]["minValue"] or not fieldNameToValueDict[fieldName]["maxValue"]:
#                 continue
#
#             #Extract the values of minField and maxField from the JSON coming from the front end
#             if "minValue" in fieldNameToValueDict[fieldName] and  "maxValue" in fieldNameToValueDict[fieldName] :
#                 minValue = fieldNameToValueDict[fieldName]["minValue"]
#                 maxValue = fieldNameToValueDict[fieldName]["maxValue"]
#                 ranges.append({"range" : {fieldName : {"lte" : maxValue,"gte" : minValue }}})
#
#             elif "minValue" in fieldNameToValueDict[fieldName] :
#                 minValue = fieldNameToValueDict[fieldName]["minValue"]
#                 ranges.append({"range" : {fieldName : {"gte" : minValue }}})
#
#             elif "maxValue" in fieldNameToValueDict[fieldName] :
#                 maxValue = fieldNameToValueDict[fieldName]["maxValue"]
#                 ranges.append({"range" : {fieldName : {"lte" : maxValue}}})
#
#         #--------------------------------------------------------------------------------------------------------------------------------#
#         #In case of multiple values for the same field, example : ram : [2,4,6], ram is either 2, 4 or 6.
#         elif value_field_name in fieldNameToValueDict[fieldName] :
#             if type(fieldNameToValueDict[fieldName][value_field_name]) is list :
#                 if type(fieldNameToValueDict[fieldName][0]) is str :
#                     fieldNameToValueDict[fieldName] = [x.lower() for x in fieldNameToValueDict[fieldName]]
#                 sameFieldMultpleValues.append({"terms" : {fieldName :fieldNameToValueDict[fieldName] }})
#         #--------------------------------------------------------------------------------------------------------------------------------#
#         #A normal numerical match, example : ram : 8, ram is 8
#             elif type(fieldNameToValueDict[fieldName][value_field_name]) is int or type(fieldNameToValueDict[fieldName][value_field_name]) is float :
#                 terms.append({"term" : {fieldName : fieldNameToValueDict[fieldName][value_field_name]}})
#             #--------------------------------------------------------------------------------------------------------------------------------#
#             #A normal string match as brandName or hardDriveType
#             else :
#                 #Example : match "{ ram : 8}"
#                 terms.append({"term" : {fieldName : fieldNameToValueDict[fieldName][value_field_name].lower()}})
#             #--------------------------------------------------------------------------------------------------------------------------------#
#         elif type(fieldNameToValueDict[fieldName]) is dict and ("intent" in fieldNameToValueDict[fieldName]) :
#             #Extract name of field, and set the name of min and max values to minField and maxField, example : minRam and maxRam.
#             #Extract the values of minField and maxField from the JSON coming from the front end
#             field_intent = fieldNameToValueDict[fieldName]["intent"]
#             es_intent = "gt" if field_intent == "more" else "lt"
#             ranges.append({"range" : {fieldName : {es_intent : fieldNameToValueDict[fieldName]["value"]}}})
#
#
#     body["query"]["bool"]["must"] = []
#     body["query"]["bool"]["should"] = []
#     if len(hardDriveSizeValues) > 0 :
#         body["query"]["bool"]["should"].append(hardDriveSizeValues)
#     if len(terms) > 0 :
#         body["query"]["bool"]["must"].append(terms)
#     if len(ranges) > 0 :
#         body["query"]["bool"]["must"].append(ranges)
#     if len(sameFieldMultpleValues) > 0 :
#         body["query"]["bool"]["must"].append(sameFieldMultpleValues)
#
#     body.update({"size":100})
#
#     return body
#

if __name__ == "__main__":
    app.run(port=5001, debug=True)
