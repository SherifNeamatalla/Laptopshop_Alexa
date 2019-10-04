import collections
from flask import Flask, jsonify, render_template, request
from elasticsearch import Elasticsearch

#from collections
#from flask_cors import CORS

#
# from vagueFunctions import vague_search_price, vague_search_harddrive,vague_search_range,vague_search_value
# from binaryFunctions import binary_search_text
# from helper import Backend_Helper
# from vagueFunctions import vague_search_price, vague_search_harddrive,vague_search_hdType

from vagueFunctions import vague_search_price, vague_search_harddrive,vague_search_range,vague_search_value,alexa_functions, vague_search_freetext
from binaryFunctions import binary_search_text, binary_search
from helper import Backend_Helper

from addMatchedInformation.add_Matched_Information import ColorInformation
from sortByPriceSameVagunessScore.sort_by_price_same_vaguness_score import SortByPrice
from vagueFunctions.vague_search_price import VagueSearchPrice
import services_b as service

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
app = Flask(__name__) #Create the flask instance, __name__ is the name of the current Python module


@app.route('/api/search/alexa', methods=['POST'])
def alexa_search():

    print('Entered end point..')
    data = request.get_json()
    intent = data["intent"]
    intent_variable = data["intentVariable"]
    intent_variable_value = data[data["intentVariable"]][data["intentVariable"]+"Value"]
    #TODO: boolean method for intentVariable
    #TODO: delete intentVariable with its Value
    data = Backend_Helper.clean_for_alexa(data)
    print('Cleaned Date..')
    allDocs = service.get_all_documents()
    print('Got all docs')

    outputProducts = service.do_query(data)

    print('Query done')

    return jsonify(outputProducts[0])


@app.route('/api/search', methods=['POST'])
def search():


    data = request.get_json()

    """The following line: set serialized object allDocs, which is a copy of the database"""
    service.get_all_documents()
    outputProducts = service.do_query(data)

    return jsonify(outputProducts)


@app.route('/api/searchText', methods=['POST'])
def searchText():
  data = request.get_json()

  query = data['searchValue']
  outputProducts =[]

  allDocs = service.get_all_documents()

  free_text_searcher =vague_search_freetext.VagueFreeText(es)
  res_search= free_text_searcher.compute_vague_freetext(allDocs, query, False) #False => not boolean search

  outputProducts = Backend_Helper.refineResult(res_search)
  for item in outputProducts: #binary search results all have a vagueness score of 1
    item['vaguenessScore'] =1 #todo: change vagueness score to reflect score

    print(outputProducts)
    return jsonify(outputProducts)


@app.route('/api/sample', methods=['GET'])
def getSample():

    allDocs = service.get_test_documents()

    outputProducts = Backend_Helper.refineResult(allDocs)
    return jsonify(outputProducts) #original from alfred

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



if __name__ == "__main__":
    app.run(port=5001, debug=True)
