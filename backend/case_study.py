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

@app.route('/api/sample', methods=['GET'])
def getSample():
  allDocs = es.search(index="amazon", body={
      "match": {
        "avgRating": 5
      }
    },
    "size": 10
  })


  helper()
  outputProducts = Backend_Helper.refineResult(allDocs)
  return jsonify(outputProducts)

def helper():
  query = '{"query": {"bool": {"must":[{"range": {"price": {"lte": 400,"gte": 200}}},{"range":{"avgRating": {"gte" :4.0}}},{"term": {"brandName": {"value": "hp"}}}]}}}'
  allDocs = es.search(index="amazon", body=query,size=1000)
  outputProducts = Backend_Helper.refineResult(allDocs)
  result = []
  for x in outputProducts:
      relevance = 1
      if (x['hddSize'] and x['hddSize'] >= 256 and x['hddSize'] <= 512) or (x['ssdSize'] and x['ssdSize'] >= 256 and x['ssdSize'] <= 512):
          relevance = relevance + 2
      if x['screenSize'] >= 13 and x['screenSize'] <= 14:
          relevance = relevance + 3
      if x['ram'] == 16 :
          relevance = relevance + 4
      result.append((x['asin'], relevance))

  print(len(result))
  one = 0
  three = 0
  four = 0
  five = 0
  six = 0
  eight = 0
  nine = 0
  seven = 0
  for (x,v) in result:
    if v == 1:
      one = one +1
    elif v == 3:
      three = three + 1
    elif v == 4:
      four = four +1
    elif v == 5:
      five = five +1
    elif v == 6:
      six = six +1
    elif v == 7:
      seven = seven + 1
    elif v == 8:
      eight = eight+1
    elif v == 9:
      nine = nine +1
    print('(' , x , ',' , v , ')')

  print ("Laptops with score 1 :" , one)
  print ("Laptops with score 3 :" , three)
  print ("Laptops with score 4 :" , four)
  print ("Laptops with score 5 :" , five)
  print ("Laptops with score 6 :" , six)
  print("Laptops with score 7 :", seven)
  print ("Laptops with score 8 :" , eight)
  print ("Laptops with score 9 :" , nine)



if __name__ == "__main__":
    app.run(port=5001, debug=True)
