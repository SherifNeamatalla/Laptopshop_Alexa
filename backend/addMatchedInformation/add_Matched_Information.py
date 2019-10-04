from vagueFunctions.vague_search_price import VagueSearchPrice
# from backend.vagueFunctions.vague_search_price import VagueSearchPrice
import numpy as np

#Changed vague_search_price to access vagnuess-scores

class ColorInformation:


  #extract searched key value pair
  #return as a dictionary---------
  #------------------------------#
  def add_matched_information(self,query,laptops,allDocs):
    all_values_dict = dict()
    for laptop in laptops:
        result = dict()
        if (laptops.index(laptop) == 0) :
            self.fill_all_values_dict(all_values_dict,laptop,allDocs)

        for field in laptop :
            if laptop[field] is not None :
                if (field == "hddSize" or field == "ssdSize") and( laptop[field] >0) :
                    if "hardDriveSize" in query :
                      if len(query["hardDriveSize"]["hardDriveSizeRange"]) == 1:
                        color_value = self.get_ranged_field_color(laptop[field],query["hardDriveSize"]["hardDriveSizeRange"],all_values_dict,field)
                        result.update({field:color_value})

                      else:# There are multiple non-consecutive intervals
                        colors = []
                        for interval_range in query["hardDriveSize"]["hardDriveSizeRange"]:
                          color_value = self.get_ranged_field_color(laptop[field], [interval_range], all_values_dict, field)
                          colors.append(color_value)
                        if "green" in colors:
                          result.update({field: 'green'})
                        elif "yellow" in colors:
                          result.update({field: 'yellow'})
                        else:
                          result.update({field: color_value})

                elif field in query :
                    field_range_name = field+"Range"
                    field_value_name = field+"Value"

                    if field_range_name in query[field] :
                      if len(query[field][field_range_name])==1 :
                        color_value = self.get_ranged_field_color(laptop[field],query[field][field_range_name],all_values_dict,field)
                        result.update({field:color_value})
                      else: # There are multiple non-consecutive intervals
                        colors =[]
                        for interval_range in query[field][field_range_name]:
                          color_value = self.get_ranged_field_color(laptop[field], [interval_range], all_values_dict, field)
                          colors.append(color_value)
                        if "green" in colors:
                          result.update({field:'green'})
                        elif "yellow" in colors:
                          result.update({field:'yellow'})
                        else:
                          result.update({field: color_value})


                    elif field_value_name in query[field]:
                      if len(query[field][field_value_name]) > 0 and type(query[field][field_value_name][0]) is str :
                          color_value = self.get_text_value_field_color(laptop[field],query[field][field_value_name],allDocs,field)
                          result.update({field:color_value})
                      else :
                          color_value = self.get_discrete_value_field_color(laptop[field],query[field][field_value_name],all_values_dict,field)
                          result.update({field:color_value})
        laptop.update({"matched":result})

  def get_text_value_field_color(self,laptop_value,query_values,allDocs,field_name):

      for value in query_values :

          if value.lower() == laptop_value.lower() :
              return "green"

      return "red"

  def get_discrete_value_field_color(self,laptop_value,query_values,all_values_dict,field_name):

      for value in query_values :
          if value == laptop_value :
              return "green"
      #==========================Yellow=========================#


      allValues = np.sort((np.array(all_values_dict[field_name])))
      ############################
      #COLOR VALUE
      for value in query_values :

        if field_name == "processorCount":
          lowerSupport = float(value) - 3
          upperSupport = float(value) + 3
        elif field_name == "ram":
          lowerSupport, upperSupport = self.lower_upper_ram(value)
        else:
          lowerSupport = float(value) - ((float(value) - allValues[0]) / 2)
          upperSupport = float(value) + ((allValues[-1] - float(value)) / 2)

        if float(laptop_value) >= lowerSupport and float(laptop_value) <= upperSupport :
            return "yellow"

      return "red"

  def get_ranged_field_color(self,laptop_value,query_values,all_values_dict,field_name):

      for value in query_values :

          if "minValue" in value and "maxValue" in value :
              if float(laptop_value) >= value["minValue"] and float(laptop_value) <=value["maxValue"]:
                  return "green"
              maxValue = value["maxValue"]
              minValue = value["minValue"]

          elif "minValue" in value  :

              if float(laptop_value) >= value["minValue"]:
                  return "green"
              maxValue = None
              minValue = value["minValue"]

          elif "maxValue" in value  :

              if float(laptop_value) <= value["maxValue"]:
                  return "green"
              maxValue = value["maxValue"]
              minValue = None

      #==========================Yellow=========================#


      allValues = np.sort((np.array(all_values_dict[field_name])))
      for value in query_values :
          if maxValue is None :
              maxValue = allValues[-1]
          if minValue is None:
              minValue = allValues[0]


          if 'counter' in query_values[0]:
            interval = float(maxValue) - float(minValue)
            trapezoid_wing_size = (interval / query_values[0]['counter']) * (1 / query_values[0]['counter'])
            lowerSupport = float(minValue) - trapezoid_wing_size
            upperSupport = float(maxValue) + trapezoid_wing_size
          else:
            lowerSupport = float(minValue) - (float(maxValue) - float(minValue))
            upperSupport = float(maxValue) + float(maxValue) - float(minValue)

          if minValue == 0:
            lowerSupport = 0

          if float(laptop_value) >= lowerSupport and float(laptop_value) <= upperSupport :
              return "yellow"
      return "red"

  def prozessDataBinary(self,searchedValues):
    self.threshholdPrice = self.prozessThreshholdPrice(searchedValues)

    for laptop in self.products:

      # initial value for minValue, maxValue. May change later
      if 'minValue' in searchedValues:
        self.matched['price'] = 'green'
      if 'maxValue' in searchedValues:
        self.matched['price'] = 'green'


      '''for key in searchedValues:
      #special case for price field, containing 3 infos instead of 2-------------------------------------#
        if key   == 'minValue':
          self.prozessColorAttributePrice(searchedValues,laptop)
          #self.prozessColorAttributeByVaguenessScore(laptop)
        elif key == 'maxValue':
          self.prozessColorAttributePrice(searchedValues,laptop)
          #self.prozessColorAttributeByVaguenessScore(laptop)
      #--------------------------------------------------------------------------------------------------#

        else: #all other attributes
        # --------------------------------------------------------------------------------------------------#
        # Strings needs to be converted to lowercase-------------------------------------------------------#
          try:
            if ((laptop[key[:-5]] is not None)and not laptop[key[:-5]].lower() == searchedValues[key].lower()):
              self.matched[key[:-5]] = 'red'
            else:
              self.matched[key[:-5]] = 'green'
        #--------------------------------------------------------------------------------------------------#

        #Numbers cant be converted, so except for control flow if lower() - function fails-----------------#
          except:
            if ((laptop[key[:-5]] is not None) and not laptop[key[:-5]] == searchedValues[key]):
              self.matched[key[:-5]] = 'red'
            else:
             self.matched[key[:-5]] = "green"'''
        #---------------------------------------------------------------------------------------------------#


      #Sort the created matched dict ----------------------------------------#
      matchedSortedKeys = sorted(self.matched.keys())
      matchedSorted = {}
      for key in matchedSortedKeys:
        matchedSorted[key] = self.matched[key]
      laptop["matched"] = matchedSorted
      self.matched = {}
      #----------------------------------------------------------------------#


  #Calculation of threshhold--------------------#
  #---------------------------------------------#
  def prozessThreshholdPrice(self,searchedValues):
    threshhold = 0
    try:
      threshhold = (float(searchedValues['maxValue']) - float(searchedValues['minValue']))
    except:
      threshhold = 50
    if threshhold > 50:
      threshhold = 50
    #print(threshhold)
    return threshhold


  #Price can be green, yellow or red, depending on the threshhold-----------------#
  #-------------------------------------------------------------------------------#
  # def prozessColorAttributePrice(self,searchedValues,laptop_value):
  #   print("in prozessColorAttributePrice function")
  #   threshholdPrice = self.prozessThreshholdPrice(searchedValues)
  #   try:
  #     if (laptop_value >= float(searchedValues['minValue'])-threshholdPrice):
  #       if (float(laptop_value) < float(searchedValues["minValue"])):
  #         return 'yellow'
  #     else:
  #       return 'red'
  #   except:
  #     pass
  #   try:
  #     if (laptop_value <= float(searchedValues['maxValue'])+threshholdPrice):
  #       if (float(laptop_value) > float(searchedValues["maxValue"])):
  #         return 'yellow'
  #     else:
  #       return 'red'
  #   except:
  #     pass


  def prozessColorAttributeByVaguenessScore(self,laptop):
    laptopName = laptop["asin"]
    score = 0
    for tupel in self.price_scores:
      if laptopName == tupel[0]:
        score = tupel[1]
    if score < 1:
      self.matched['price'] = 'yellow'
    if score < 0.985:
      self.matched['price'] = 'red'

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
  def fill_all_values_dict(self,all_values_dict,laptop,allDocs):

      for field_name in laptop:
          allValues = []

          for doc in allDocs['hits']['hits']:
            if (field_name in doc['_source']) :
                try:
                    allValues.append(float(doc['_source'][field_name]))
                except :
                    pass

          allValues = np.sort((np.array(allValues)))
          all_values_dict.update({field_name : allValues})
