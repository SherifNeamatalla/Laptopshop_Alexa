import numpy as np

class AlexaSearch :
    def __init__(self, es):
          self.es = es

    def compute_boolean_value(self,field_name,field_weight,field_value,field_intent):

        es_intent = "gt" if field_intent == "more" else "lt"


        body = {
          "query":{
            "bool":{
                "must":{
                    "range": {
                        field_name: {
                            es_intent : field_value
                 # elastic search lte operator = less than or equals
              }
            }
          }
        }
       }
      }

        # size in range queries should be as many as possible, because when the difference upperSupport and lowerSupport is big, we can lose some products
        # (whose price actually between the minPrice and maxPrice) because we just want to get the first 100 element
        res = self.es.search(index="amazon", body=body, size=10000)

        result = []
        for hit in res['hits']['hits']:
          result.append([hit['_source']['asin'],  # hit['_source']['price'],
                        field_weight])


        result = np.array(result, dtype=object)
        result = result[np.argsort(-result[:, 1])]
        # just return the first 100 element(i think 1000 is just too many, but we can change it later)
        result = result[:100]
        result = list(map(tuple, result))
        return result
