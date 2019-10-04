
class VagueFreeText():
  def __init__(self, es):
        self.es = es

  def compute_vague_freetext(self, allDocs, query, isBooleanSearch):
    result = []

    operator = "or" #default not boolean
    if isBooleanSearch is True:
      operator = "and"

    #Did user specify a field?
    alist = ["brand", "price", "title"]
    fields = []

    query = query.lower()
    for field in alist:
      if field in query:
        if field is "brand":
          fields.append("brandName")
        if field is "title":
          fields.append("productTitle")
        #if field is "price":
          #fields.append(field) #do not add!  numeric fields problematic

    # #The following is a case insensitive search
    # Default: "operator": "or", "fields" : *
    body ={
            "query": {
              "multi_match" : {
                "query" :  query,
                "operator": operator,
                "fields":fields,
                "lenient": "true"
              }

              }
            }


    #todo: change score to represent normalized score from elasticsearch result
    res = self.es.search(index="amazon", body=body, size=10000)

    # # Add list including [asin, fuzzycalc] to result. Fuzzy Calculation is between 0 and 1
    # for hit in res['hits']['hits']:
    #   result.append([hit['_source']['asin'],  float(1.0)])
    #
    #
    # result = list(map(tuple, result))

    return res
