class SortByPrice:

  def calculateIndex_tillSameScore(self,liste):
    index = 0
    for i in range(1,len(liste)):
      if liste[i]['vaguenessScore'] == liste[i-1]['vaguenessScore']:
        index += 1
      else:
        break
    return index

  #-------------------------------------------------------------
  #Sorts the list by price, + keeping the vagnuess score sorting
  def sort_by_price(self,liste):
    sorted_list = list()
    #--------------------------------------------------------------
    #Sorts the list sliced by calculatedIndex_tillSameScore--------
    #Sorted part cut off from list, which will be further processed
    while (len(liste) > 0):
      sorted_list = sorted_list + sorted(liste[:self.calculateIndex_tillSameScore(liste)+1], key=lambda k: k['price'])
      liste = liste[self.calculateIndex_tillSameScore(liste)+1:]
    return sorted_list



