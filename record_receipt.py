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

CSV_PATH_NAME = "output.csv"      # save receipt infomation 
ITEMDB_PATH_NAME = "item_db.py"   # reference item infomation and write for new it
STOREDB_PATH_NAME = "store_db.py" # reference store name infomation and write for new it

class RecordReceipt:
  itemDB = iDB.itemDB         # read item from DataBase
  categoryDB = iDB.categoryDB # read category name from DataBase
  storeDB=sDB.storeDB         # read store name from DataBase

  def __init__(self,allItem,newCategoryEn,date,store):
    self.allItem = allItem              # to instance argument
    self.newCategoryEn = newCategoryEn  # to instance argument
    self.date = date                    # to instance argument
    self.store = store                  # to instance argument
    self.writeFile()                    # record for CSV file
    self.addDB()                        # update DataBase

  def writeFile(self):
    """ record receipt for csv file """
    f = open(CSV_PATH_NAME, mode='a') 
    writer = csv.writer(f)                  # to write with csv format
    # writer.writerow([self.date,self.store]) # write date and store name
    for lineItem in self.allItem:
      lineItem.insert(0,self.date)
      lineItem.insert(0,self.store)
      writer.writerow(lineItem) # write item
    f.close()
    print("write for csv file")

  def addDB(self):
    """ update DataBase(item_db, store_db) """
    # print(self.itemDB)
    # print("----")
    # print(self.categoryDB)
    # print("----")
    for lineItem in self.allItem:
      # print(lineItem) 
      if not(lineItem[4] in self.itemDB): # whether it is new category (no infomation for DataBase)
        self.itemDB[lineItem[4]] = [] # add new key for itemDB
        self.itemDB[lineItem[4]].append(lineItem[3]) # add item for new key as value
        self.categoryDB[lineItem[4]] = self.newCategoryEn[lineItem[4]] # add new key and English value name for category
      elif not(lineItem[3] in self.itemDB[lineItem[4]]): # not new category but it is new item
        self.itemDB[lineItem[4]].append(lineItem[3]) # add item for new key as value

    replaceContent= "" # make sentence to write

    for key,val in self.itemDB.items(): # write category name and content of it
      replaceContent += self.categoryDB[key] + " = " +str(val)+'\n'

    ### make itemDB and categoryDB argument ###
    replaceContent+= "itemDB = {"
    for key in self.categoryDB:
      replaceContent += "'" + key + "': " + self.categoryDB[key] +", "
    replaceContent=replaceContent[:-2] # delete space and comma
    replaceContent += '}\n'
    replaceContent += "categoryDB = " + str(self.categoryDB) + '\n'

    with open(ITEMDB_PATH_NAME,"w") as f: # write for item_DB.py
      f.write(replaceContent)
    
    if not(self.store in self.storeDB): # Whether new store name or not
      self.storeDB.append(self.store)
      with open(STOREDB_PATH_NAME,"w") as f:  # write for item_DB.py
        f.write("storeDB = " + str(self.storeDB))

