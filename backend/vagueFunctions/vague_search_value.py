import skfuzzy as fuzz
import numpy as np

class VagueSearchValue():

  def __init__(self, es):
        self.es = es


  def compute_vague_value(self, allDocs, fieldName,weight,values):
    allValues = []
    for doc in allDocs['hits']['hits']:
      if (doc['_source'][fieldName]) :
          allValues.append(float(doc['_source'][fieldName]))

    allValues = np.sort((np.array(allValues)))
    # print("allPrices: ", allPrices)
    print(fieldName)
    print(values)
    result = []
    for value in values :
        if fieldName == "processorCount":
          lowerSupport = float(value) - 3
          upperSupport = (float(value) + 3)
        elif fieldName == "ram":
          lowerSupport, upperSupport = self.lower_upper_ram(value)
        else:
          lowerSupport = float(value) - ((float(value) - allValues[0]) / 2)
          upperSupport = float(value) + ((allValues[-1] - float(value)) / 2)
          print(lowerSupport)
          print(upperSupport)
        trimf = fuzz.trimf(allValues, [lowerSupport, float(value), upperSupport])

        body = {
          "query": {
            "range": {
              fieldName: {
                "gte": lowerSupport,  # elastic search gte operator = greater than or equals
                "lte": upperSupport  # elastic search lte operator = less than or equals
              }
            }
          }
        }

        # size in range queries should be as many as possible, because when the difference upperSupport and lowerSupport is big, we can lose some products
        # (whose price actually between the minPrice and maxPrice) because we just want to get the first 100 element
        res = self.es.search(index="amazon", body=body, size=10000)

        for hit in res['hits']['hits']:
          result.append([hit['_source']['asin'],  # hit['_source']['price'],
                        weight * fuzz.interp_membership(allValues, trimf, float(hit['_source'][fieldName]))])

    result = np.array(result, dtype=object)
    result = result[np.argsort(-result[:, 1])]
    # just return the first 100 element(i think 1000 is just too many, but we can change it later)


    result = list(map(tuple, result))
    # print(result)
    return result

  def lower_upper_ram(self, value):
    lowerSupport = 0.0
    upperSupport = 128.1
    if value == 2:
      lowerSupport = 0.0
      upperSupport = 5
    elif value == 4:
      lowerSupport = 1
      upperSupport = 7
    elif value == 6:
      lowerSupport = 3
      upperSupport = 9
    elif value == 8:
      lowerSupport = 5
      upperSupport = 13
    elif value == 12:
      lowerSupport = 7
      upperSupport = 17
    elif value == 16:
      lowerSupport = 11
      upperSupport = 25
    elif value == 24:
      lowerSupport = 15
      upperSupport = 33
    elif value == 32:
      lowerSupport = 23
      upperSupport = 129
    return lowerSupport, upperSupport
