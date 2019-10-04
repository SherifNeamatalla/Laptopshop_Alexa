import collections
import os
from collections import Counter

from addMatchedInformation.add_Matched_Information import ColorInformation
from binaryFunctions import binary_search, binary_search_text
from helper import Backend_Helper
from main import es
from sortByPriceSameVagunessScore.sort_by_price_same_vaguness_score import SortByPrice
from vagueFunctions import vague_search_range, vague_search_harddrive, vague_search_value, vague_search_price, \
  alexa_functions
import all_docs_search as dao
from vagueFunctions.vague_search_price import VagueSearchPrice
import pickle


allDocs_path = './allDocs.obj'

def do_query(data):



  with open(allDocs_path, 'rb') as input:
    allDocs = pickle.load(input)

  data = Backend_Helper.clean_frontend_json(data)

  #create binary clean data if weighting is equal to 5
  binary_clean_data = {}
  clean_data = {}
  alexa_clean_data = {}
  output_binary = list()
  #bool_search_default = False #If no weighting = 5 for any value, do not caculate boolean search below

  for field in data.keys():
    if data[field]['weight'] == 5:
      #bool_search_default = True
      binary_clean_data[field] = data[field] #weigth doesn't matter for boolean search
    elif data[field]["weight"] == 6: #This is for alexa_search, will be used at the end
      alexa_clean_data[field] = data[field]
      pass
    else:
      clean_data[field] = data[field]

  #Compute boolean/binary search for items with weighting = 5
  bin_obj = binary_search.BinarySearch()
  alexa_searcher = alexa_functions.AlexaSearch(es)

  if len(binary_clean_data) > 0:
      query = bin_obj.createBinarySearchQuery(binary_clean_data)
      res = es.search(index="amazon", body=query)
      output_binary = Backend_Helper.refineResult(res)



  if len(alexa_clean_data) > 0 :

  #Add alexa search results to output_binary, same mechanism and logic for both.
      alexa_result = get_alexa_search_result(allDocs, alexa_clean_data, alexa_searcher)
      output_binary += alexa_result

  res_search = list()

  # field_value_dict has the form:
  # {'binary' : { 'brandName': ['acer', 'hp'], 'weight':1}, ...}, 'vague' : {....},
  field_value_dict = extract_fields_and_values(clean_data)


  #Get total cumulative weight weight_sum (for example for all attributes weights were 7) and dividue each score by this weight_sum
  #For normalization
  weight_sum = 0
  for field_type in field_value_dict.keys():
    for field_name in field_value_dict[field_type]:
      field_weight = field_value_dict[field_type][field_name]["weight"]
      if field_weight != 5: ##Shouldn't happen though because they have already been removed from clean_data
        weight_sum += field_weight

  # --------------------------------------------------------------------#
  # Objects for each class to use the vague searching functions


  ######################################################################## NEW #########################################
  #Function call in ColorInformation to extract searched values.
  #function extractKeyValuePairs() will do that.
  c_i_helper = ColorInformation()
  price_searcher = vague_search_price.VagueSearchPrice(es)
  ######################################################################## NEW #########################################


  range_searcher = vague_search_range.VagueSearchRange(es)

  binary_searcher = binary_search_text.BinarySearchText(es)

  harddrive_searcher = vague_search_harddrive.VagueHardDrive(es)

  value_searcher = vague_search_value.VagueSearchValue(es)
  # --------------------------------------------------------------------#
  # # Special case to handle hardDriveSize, length is >1 if it has values other than weight
  if 'hardDriveSize' in clean_data and len(clean_data["hardDriveSize"]) > 1:
    # res_search += vague_search_harddrive.computeVagueHardDrive_alternative(allDocs, clean_data,
    #                                                                                       harddrive_searcher,
    #                                                                                       res_search)
    res_search = harddrive_searcher.computeVagueHardDrive_alternative(allDocs, field_value_dict,
                                                                           harddrive_searcher,
                                                                           res_search)
  #  --------------------------------------------------------------------#
  # Special case to handle price
  if 'price' in clean_data and len(clean_data["price"]) > 1:
    ##NEW##########
    #res_search += vague_search_price.VagueSearchPrice.computeVaguePrice_alternative(allDocs, clean_data, price_searcher, res_search, searchedValues)
    res_search = price_searcher.computeVaguePrice_alternative(allDocs, field_value_dict, price_searcher, res_search)

  # --------------------------------------------------------------------#
  # Gets scores for all other attributes
  res_search += call_responsible_methods(allDocs, field_value_dict, range_searcher, binary_searcher, value_searcher,
                                         alexa_searcher)




  # --------------------------------------------------------------------#
  resList = [dict(x) for x in res_search]

  # Counter objects count the occurrences of objects in the list...
  count_dict = Counter()
  for tmp in resList:
    count_dict += Counter(tmp)

  result = dict(count_dict)
  sortedDict = collections.OrderedDict(sorted(result.items(), key=lambda x: x[1], reverse=True))
  asinKeys = list(result.keys())

  # call the search function
  outputProducts = getElementsByAsin(asinKeys) #calls helper class method refineResuls


  # Compare outputProducts and output_binary to select only items that also occur in boolean search
  outputProducts, output_binary = filter_from_boolean(outputProducts, output_binary)



  # add a vagueness score to the returned objects and normalize
  for item in outputProducts:
    # Normalize the scores so that for each score x,  0< x <=1
    item['vaguenessScore'] = result[item['asin']]/weight_sum


  outputProducts = sorted(outputProducts, key=lambda x: x["vaguenessScore"], reverse=True)

  for item in output_binary: #binary search results that did not meet other vague requirements
    item['vaguenessScore'] = None

  # concatenate with products with weighting 5 ***
  outputProducts = outputProducts + output_binary
  # products with same vagueness score should be listed according to price descending
  s_p = SortByPrice()


  # #DELETE all products with vagueness_score = 0
  outputProducts_vaguenessGreaterZero = list()

  for laptop in outputProducts:
    if laptop["vaguenessScore"] != 0:
      outputProducts_vaguenessGreaterZero.append(laptop)
  outputProducts_vaguenessGreaterZero = s_p.sort_by_price(outputProducts_vaguenessGreaterZero)

  #outputProducts_vaguenessGreaterZero , output_binary = filter_from_boolean(outputProducts_vaguenessGreaterZero, output_binary)

  #outputProducts_vaguenessGreaterZero = outputProducts_vaguenessGreaterZero[:1000]

  c_i_helper.add_matched_information(data,outputProducts_vaguenessGreaterZero,allDocs)

  #Needed in frontend

  outputProducts_vaguenessGreaterZero_with_original_query = [outputProducts_vaguenessGreaterZero,data]

  return outputProducts_vaguenessGreaterZero_with_original_query


def get_vague_result(res_search):
  resList = [dict(x) for x in res_search]
  # Counter objects count the occurrences of objects in the list...
  count_dict = Counter()
  for tmp in resList:
    count_dict += Counter(tmp)
  result = dict(count_dict)
  #sortedDict = collections.OrderedDict(sorted(result.items(), key=lambda x: x[1], reverse=True))
  asinKeys = list(result.keys())
  # call the search function
  outputProducts = getElementsByAsin(asinKeys)  # calls helper class method refineResuls
  return outputProducts, result


def get_cumulative_weight(field_value_dict):
  cum_weight = 0
  for field_type in field_value_dict.keys():
    for field_name in field_value_dict[field_type]:
      field_weight = field_value_dict[field_type][field_name]["weight"]
      if field_weight != 5:  ##Shouldn't happen though because they have already been removed from clean_data
        cum_weight += field_weight
  # print("cum_weight: ", cum_weight)
  return cum_weight


def get_vague_and_binary_lists(clean_data1):
  # create binary clean data if weighting is equal to 5
  binary_clean_data = {}
  clean_data = {}
  # bool_search_default = False #If no weighting = 5 for any value, do not caculate boolean search below
  for field in clean_data1.keys():
    if clean_data1[field]['weight'] == 5:
      # bool_search_default = True
      binary_clean_data[field] = clean_data1[field]  # weigth doesn't matter for boolean search
    else:
      clean_data[field] = clean_data1[field]
      # binary_clean data has to also contain the empty/meaningless fields  because this is the format needed for BinarySearch() method
      # This doesn't matter though because weight has no meaning for boolean search and is not used in the calculation for the result set
      binary_clean_data[field] = {'weight': 1}
  # print("print binary_clean_data: ", binary_clean_data)
  # print("print clean_data: ", clean_data)
  # Compute boolean/binary search for items with weighting = 5
  bin_obj = binary_search.BinarySearch()
  query = bin_obj.createBinarySearchQuery(binary_clean_data)
  res = es.search(index="amazon", body=query)
  output_binary = Backend_Helper.refineResult(res)
  return clean_data, output_binary


def filter_from_boolean(outputProducts, output_binary):

  if len(output_binary) == 0:
      return outputProducts,output_binary


  intersection = get_list_intersection(outputProducts,output_binary);

  return intersection, output_binary

def get_list_intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def callAttributeMethod(attributeName, attributeValue, attributeWeight, allDocs):
  methodName = "computeVague" + attributeName[0].upper() + attributeName[1:]
  className = "vague_search_" + attributeName

  eval(className + "." + methodName)


def extract_fields_and_values(fieldNameToValueDict):
  result = dict(dict())
  result["binary"] = {}
  result["vague"] = {}
  result["range"] = {}
  result["alexa"] = {}

  for fieldName in fieldNameToValueDict:

    if not fieldNameToValueDict[fieldName]:
      continue
    # normal match
    # Ranged terms, example : ram : { minRam : 2,maxRam : 4}
    # If that's the case, then search for minRam and maxRam in fieldNameToValueDict, get them and add range to the query
    value_field_name = fieldName + "Value"
    range_field_name = fieldName+"Range"
    min_field_name = "minValue"
    max_field_name = "maxValue"
    if range_field_name in fieldNameToValueDict[fieldName]:
      result["range"].update({fieldName: {"range" : fieldNameToValueDict[fieldName][range_field_name]
          , "weight": fieldNameToValueDict[fieldName]["weight"]}})
    # --------------------------------------------------------------------------------------------------------------------------------#
    # In case of multiple values for the same field, example : ram : [2,4,6], ram is either 2, 4 or 6.
    elif value_field_name in fieldNameToValueDict[fieldName]:
      if type(fieldNameToValueDict[fieldName][value_field_name]) is list and len(fieldNameToValueDict[fieldName][value_field_name]) > 0:
        if type(fieldNameToValueDict[fieldName][value_field_name][0]) is str:
          fieldNameToValueDict[fieldName][value_field_name] = [x.lower() for x in
                                                               fieldNameToValueDict[fieldName][value_field_name]]
          result["binary"].update({fieldName: {"value": fieldNameToValueDict[fieldName][value_field_name],
                                               "weight": fieldNameToValueDict[fieldName]["weight"]}})
        # --------------------------------------------------------------------------------------------------------------------------------#
        elif type(fieldNameToValueDict[fieldName][value_field_name][0]) is int or type(
          fieldNameToValueDict[fieldName][value_field_name][0]) is float:
          result["vague"].update({fieldName: {"value": fieldNameToValueDict[fieldName][value_field_name],
                                              "weight": fieldNameToValueDict[fieldName]["weight"]}})
      # --------------------------------------------------------------------------------------------------------------------------------#
      # A normal string match as brandName or hardDriveType
      else:
        # Example : match "{ hardDriveType :{"value": "ssd"}}"
        result["binary"].update({fieldName: {"value": [fieldNameToValueDict[fieldName][value_field_name]],
                                             "weight": fieldNameToValueDict[fieldName]["weight"]}})
      # --------------------------------------------------------------------------------------------------------------------------------#
      # A Query coming from alexa, with only more or less
    elif type(fieldNameToValueDict[fieldName]) is dict and ("intent" in fieldNameToValueDict[fieldName]):
      # Extract name of field, and set the name of min and max values to minField and maxField, example : minRam and maxRam.
      # Extract the values of minField and maxField from the JSON coming from the front end
      result["alexa"].update({fieldName: {"intent": fieldNameToValueDict[fieldName]["intent"],
                                          "value": fieldNameToValueDict[fieldName]["value"],
                                          "weight": fieldNameToValueDict[fieldName]["weight"]}})
  return result



def call_responsible_methods(allDocs, field_value_dict, range_searcher, binary_searcher, value_searcher,
                             alexa_searcher):
  res_search = list()
  # --------------------------------------------------------------------#
  # Extracts each field and its value and weight to the dict
  for field_type in field_value_dict.keys():
    for field_name in field_value_dict[field_type]:
      if field_name != "price" and field_name != "hardDriveSize":
        field_weight = field_value_dict[field_type][field_name]["weight"]
        # Values for binary key in the dict, these will be searched in the binary_searcher
        if field_type is "binary":
          field_value = field_value_dict[field_type][field_name]["value"]
          res_search.append(binary_searcher.compute_binary_text(field_name, field_weight, field_value))

        # --------------------------------------------------------------------#


          """ The range key is the key used for Facets with an interval. For example: weight, screen size, processor size, etc."""
        elif field_type is "range":

          """The length of field_value_dict is the length of the interval range for a field (For example, for weight).
            If it has length ==1, then only one interval for this field has been entered by user.  The function continues
            with default implementation of vague function and membership function calculations."""
          if len(field_value_dict[field_type][field_name]["range"]) ==1:
            for range in field_value_dict[field_type][field_name]["range"] :
                if "minValue" in range and "maxValue" in range:
                  min_value = range["minValue"]
                  max_value = range["maxValue"]
                  if "counter" in range:
                    counter = range["counter"]
                    res_search.append(
                    range_searcher.compute_vague_range(allDocs, field_name, field_weight, min_value, max_value, counter))
                  else:
                    res_search.append(range_searcher.compute_vague_range(allDocs, field_name, field_weight, min_value, max_value, 1))

                # elif "minValue" in range:
                #   min_value = range["minValue"]
                #   res_search.append(range_searcher.compute_vague_range(allDocs, field_name, field_weight, min_value, None))
                #
                # elif "maxValue" in field_value_dict[field_type][field_name]:
                #   max_value = range["maxValue"]
                #   res_search.append(range_searcher.compute_vague_range(allDocs, field_name, field_weight, None, max_value))

          else:# Price range consists of at least two non-consecutive intervals
            res_search.append(range_searcher.compute_vague_range_mult_intervals(allDocs, field_name, field_weight,
                                                              field_value_dict[field_type][field_name]["range"]))
        # --------------------------------------------------------------------#
        # Values for binary key in the dict, these will be searched in the value_searcher
        elif field_type is "vague":
          field_value = field_value_dict[field_type][field_name]["value"]
          res_search.append(value_searcher.compute_vague_value(allDocs, field_name, field_weight, field_value))
        # --------------------------------------------------------------------#
        # Values for alexa

  return res_search



def getElementsByAsin(asinKeys):
  result = es.search(index="amazon", body={
                                              "query": {
                                                  "terms": {
                                                        "asin.keyword": asinKeys
                                                  }

                                              }, "size":7000

                                            })

  return Backend_Helper.refineResult(result)


def get_all_documents():

  if os.path.exists('./allDocs.obj'):
    # print("allDocs exists")
    if os.path.getsize(allDocs_path)>0:
      with open(allDocs_path, "rb") as f:
        unpickler = pickle.Unpickler(f)
        allDocs = unpickler.load()
  else:
    allDocs = dao.search_for_all_docs()
    with open(allDocs_path, 'wb') as output:
      pickle.dump(allDocs, output, pickle.HIGHEST_PROTOCOL)

  #return allDocs


# def get_all_documents():
#   allDocs = es.search(index="amazon", body={
#     "size": 10000,
#     "query": {
#       "match_all": {}
#     }
#   })
#   return allDocs

def get_alexa_search_result(allDocs, field_value_dict, alexa_searcher):
    res_search = list()
    for field_name in field_value_dict:
      field_value = field_value_dict[field_name]["value"]
      field_intent = field_value_dict[field_name]["intent"]
      res_search.append(alexa_searcher.compute_boolean_value(field_name, 6, field_value, field_intent))

    resList = [dict(x) for x in res_search]

    # Counter objects count the occurrences of objects in the list...
    count_dict = Counter()
    for tmp in resList:
      count_dict += Counter(tmp)

    result = dict(count_dict)
    asinKeys = list(result.keys())

    # call the search function
    outputProducts = getElementsByAsin(asinKeys)
    return outputProducts

def get_test_documents():
   some_docs = dao.search_for_some_docs()
   return some_docs
