import skfuzzy as fuzz
import numpy as np

class VagueHardDrive():
    def __init__(self, es):
        self.es = es

    def computeVagueHardDrive(self, allDocs,  weight, minValue, maxValue, counter):

      allHardDrives = []
      for doc in allDocs['hits']['hits']:
            if doc['_source']["hddSize"]and doc['_source']['hddSize'] != 0:
                allHardDrives.append(int(doc['_source']['hddSize']))
            if doc['_source']['ssdSize'] and doc['_source']['ssdSize'] != 0:
                allHardDrives.append(int(doc['_source']['ssdSize']))

      allHardDrives = np.sort((np.array(allHardDrives)))

      if maxValue is None :
          maxValue = allHardDrives[-1]
      if minValue is None:
          minValue = allHardDrives[0]

      interval = float(maxValue) - float(minValue)
      trapezoid_wing_size = (interval / counter) * (1 / counter)
      lowerSupport = float(minValue) - trapezoid_wing_size
      upperSupport = float(maxValue) + trapezoid_wing_size
      vagueFunction = fuzz.trapmf(allHardDrives, [lowerSupport, float(minValue), float(maxValue), upperSupport])

      body = {
          "query": {
              "bool": {
                  "should": [
                      {"range": {
                          "hddSize": {
                            "gte": lowerSupport,
                            "lte": upperSupport
                          }
                      }},
                      {"range": {
                          "ssdSize": {
                            "gte": lowerSupport,
                            "lte": upperSupport
                          }
                      }}
                  ]
              }
          },
        "size" : 10000
      }
      res = self.es.search(index="amazon", body=body)

      result = []
      for hit in res['hits']['hits']:
          # in case there is two types, we should take the one with the higher score
          if hit['_source']['hddSize'] and hit['_source']['ssdSize']:
              if hit['_source']['hddSize'] != 0 and hit['_source']['ssdSize'] != 0:
                  result.append([hit['_source']['asin'],  # hit['_source']['hardDrive'],
                                 weight * max(fuzz.interp_membership(allHardDrives, vagueFunction, float(hit['_source']['hddSize'])),fuzz.interp_membership(allHardDrives, vagueFunction, float(hit['_source']['ssdSize'])))])
                  continue

          # laptop has only hdd Drive
          elif hit['_source']['hddSize'] and hit['_source']['hddSize'] != 0:
              result.append([hit['_source']['asin'],# hit['_source']['hardDrive'],
                         weight * fuzz.interp_membership(allHardDrives, vagueFunction, float(hit['_source']['hddSize']))])

          # laptop has only ssd Drive
          elif hit['_source']['ssdSize'] and hit['_source']['ssdSize'] != 0:
              result.append([hit['_source']['asin'],# hit['_source']['hardDrive'],
                         weight * fuzz.interp_membership(allHardDrives, vagueFunction, float(hit['_source']['ssdSize']))])


      result = np.array(result, dtype=object)
      result = result[np.argsort(-result[:, 1])]
      result = list(map(tuple, result)) # turn list of list pairs into list of tuple pairs containting (ASIN, score) pairs
      return result


    def computeVagueHardDrive_multiple(self, allDocs, weight, interval_list, counter):
      allHardDrives = []
      for doc in allDocs['hits']['hits']:
        if doc['_source']["hddSize"] and doc['_source']['hddSize'] != 0:
          allHardDrives.append(int(doc['_source']['hddSize']))
        if doc['_source']['ssdSize'] and doc['_source']['ssdSize'] != 0:
          allHardDrives.append(int(doc['_source']['ssdSize']))

      allHardDrives = np.sort((np.array(allHardDrives)))
      query = []
      fuzzy_logic_results = []

      for i in range(len(interval_list)):

        if 'minValue' in interval_list[i]:
          minValue = interval_list[i]['minValue']
        else:
          minValue = allHardDrives[0]

        if 'maxValue' in interval_list[i]:
          maxValue = interval_list[i]['maxValue']
        else:
          maxValue = allHardDrives[-1]

        interval = float(maxValue) - float(minValue)
        trapezoid_wing_size = (interval / counter) * (1 / counter)
        lowerSupport = float(minValue) - trapezoid_wing_size
        if minValue == 0:
          lowerSupport = 0
        upperSupport = float(maxValue) + trapezoid_wing_size
        vagueFunction = fuzz.trapmf(allHardDrives, [lowerSupport, float(minValue), float(maxValue), upperSupport])

        fuzzy_logic_results.append(vagueFunction)

        query.append({"range": {'hddSize': {"gte": lowerSupport, "lte": upperSupport}}}, )
        query.append({"range": {'ssdSize': {"gte": lowerSupport, "lte": upperSupport}}}, )

      body = {
        "query": {
          "bool": {
            "should": query
          }
        },
        "sort": {"price": {"order": "asc"}}

      }

      res = self.es.search(index="amazon", body=body, size=10000)

      result = []
      scores = []
      for hit in res['hits']['hits']:

        # in case there is two types, we should take the one with the higher score
        if hit['_source']['hddSize'] and hit['_source']['ssdSize']:
          if hit['_source']['hddSize'] != 0 and hit['_source']['ssdSize'] != 0:
            scores.append(weight * max(
                             fuzz.interp_membership(allHardDrives, vagueFunction, float(hit['_source']['hddSize'])),
                             fuzz.interp_membership(allHardDrives, vagueFunction, float(hit['_source']['ssdSize']))))


        # laptop has only hdd Drive
        elif hit['_source']['hddSize'] and hit['_source']['hddSize'] != 0:
          scores.append(weight * fuzz.interp_membership(allHardDrives, vagueFunction,
                                                         float(hit['_source']['hddSize'])))

        # laptop has only ssd Drive
        elif hit['_source']['ssdSize'] and hit['_source']['ssdSize'] != 0:
          scores.append(weight * fuzz.interp_membership(allHardDrives, vagueFunction,
                                                         float(hit['_source']['ssdSize'])))

        if len(scores) > 0:
          max_score = scores[0]
          for i in range(len(scores) - 1):
            if scores[i] < scores[i + 1]:
              max_score = scores[i + 1]
          result.append([hit['_source']['asin'], weight * max_score])

      result = np.array(result, dtype=object)
      result = result[np.argsort(-result[:, 1])]
      result = list(map(tuple, result))
      return result


    def computeVagueHardDrive_alternative(self,allDocs, clean_data, harddrive_searcher, res_search):
      # Special case to handle hardDriveSize, length is >1 if it has values other than weight
      #if 'hardDriveSize' in clean_data and len(clean_data["hardDriveSize"]) > 1:
      hd_size_weight = clean_data["range"]['hardDriveSize']["weight"]

      # print("computeVagueHardDrive_alternative function ", clean_data["range"]["hardDriveSize"])
      if "range" in clean_data["range"]["hardDriveSize"]:

        # if len(clean_data["range"]["hardDriveSize"]["range"]) == 1:

          for range in clean_data["range"]["hardDriveSize"]["range"]:
              if "minValue" in range and "maxValue" in range:
                min_value = range["minValue"]
                max_value = range["maxValue"]
                if "counter" in range:
                  res_search.append(
                    harddrive_searcher.computeVagueHardDrive(allDocs, hd_size_weight, min_value, max_value, range["counter"]))
                else:
                  res_search.append(harddrive_searcher.computeVagueHardDrive(allDocs,  hd_size_weight, min_value, max_value, 1)) # Discrete value needed not a range
          return res_search
        # else:
        #   res_search.append(harddrive_searcher.computeVagueHardDrive_multiple(allDocs, hd_size_weight,clean_data["range"]["hardDriveSize"]["range"], 1 ))
        #   return res_search
