##############################################
# ----------------- README ----------------- #
# Record recipet infomation                  #
#   such as store name, date, item, price.   #
# If first store name or first item,         #
#   update DataBase(item_db.py,store_db.py). #
#                                            #
##############################################

import item_db as iDB
import store_db as sDB
import csv
# import os
CSV_PATH_NAME = "output.csv"      # save receipt infomation 
ITEMDB_PATH_NAME = "item_db.py"   # reference item infomation and write for new it
STOREDB_PATH_NAME = "store_db.py" # reference store name infomation and write for new it

class RecordReceipt:
  item_DB = iDB.item_DB         # read item from DataBase
  category_DB = iDB.category_DB # read category name from DataBase
  store_DB=sDB.store_DB         # read store name from DataBase

  def __init__(self,allItem,newCategoryEn):
    self.allItem = allItem              # to instance argument
    self.newCategoryEn = newCategoryEn  # to instance argument
    # self.date = date                    # to instance argument
    self.store = allItem[0]["store"]                  # to instance argument
    self.writeFile()                    # record for CSV file
    self.addDB()                        # update DataBase

  def writeFile(self):
    """ record receipt for csv file """
    f = open(CSV_PATH_NAME, mode='a') 
    writer = csv.writer(f)                  # to write with csv format
    # writer.writerow([self.date,self.store]) # write date and store name
    for lineItem in self.allItem:
      writer.writerow(lineItem.values()) # write item
    f.close()
    print("write for csv file")

  def addDB(self):
    """ update DataBase(item_db, store_db) """
    for lineItem in self.allItem:
      if not(lineItem["registered_name"] in lineItem["item"]): # whether lineItem is special_name
        # print(lineItem)
        iDB.special_name[lineItem["item"]] = [lineItem["registered_name"],str(lineItem["category"])]
      if not(lineItem["category"] in self.item_DB): # whether it is new category (no infomation for DataBase)
        self.item_DB[lineItem["category"]] = [] # add new key for item_DB
        self.item_DB[lineItem["category"]].append(lineItem["registered_name"]) # add item for new key as value
        self.category_DB[lineItem["category"]] = self.newCategoryEn[lineItem["category"]] # add new key and English value name for category
      elif not(lineItem["registered_name"] in self.item_DB[lineItem["category"]]): # not new category but it is new item
        self.item_DB[lineItem["category"]].append(lineItem["registered_name"]) # add item for new key as value
    
    replaceContent= "" # make sentence to write

    for key,val in self.item_DB.items(): # write category name and content of it
      replaceContent += self.category_DB[key] + " = " +str(val)+'\n'
    replaceContent += "special_name = " +str(iDB.special_name)+'\n'

    ### make item_DB and category_DB argument ###
    replaceContent+= "item_DB = {"
    for key in self.category_DB:
      replaceContent += "'" + key + "': " + self.category_DB[key] +", "
    replaceContent=replaceContent[:-2] # delete space and comma
    replaceContent += '}\n'
    replaceContent += "category_DB = " + str(self.category_DB) + '\n'

    with open(ITEMDB_PATH_NAME,"w") as f: # write for item_DB.py
      f.write(replaceContent)
    
    if not(self.store in self.store_DB): # Whether new store name or not
      self.store_DB.append(self.store)
      sDB.keyword[self.store] = ""
      with open(STOREDB_PATH_NAME) as file:
        contents = file.readlines()
      contents[1] = "store_DB = " + str(self.store_DB) + '\n'
      contents[2] = "keyword = " + str(sDB.keyword) + '\n'
      with open(STOREDB_PATH_NAME, mode="w") as file:
        # print(type(contents))
        # print(contents)
        file.writelines("".join(contents))



      # with open(STOREDB_PATH_NAME,"w") as f:  # write for item_DB.py
      #   f.write("store_DB = " + str(self.store_DB))

