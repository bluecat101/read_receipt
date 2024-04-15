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
import csv # To save csv file

CSV_PATH_NAME     = "output.csv"  # To save receipt infomation
ITEMDB_PATH_NAME  = "item_db.py"  # To reference item infomation and write for new it
STOREDB_PATH_NAME = "store_db.py" # To reference store name infomation and write for new it

class RecordReceipt:
  """ 
  ## Description
    This class is to save data such as item on receipts.
    If there are new item, store name and category name, save them too

  ## Attributes:
    item_DB()         : Item already registered such as milk, potato, beef etc...
    category_DB()     : Category name already registered such as dairy products, vegetable, meat etc...
    store_DB()        : Store name already registered
    store(str)        : Purchace store name
    tax(str)          : Infomation of tax extarnal or internal tax
    all_item()        : Got Data from receipt such as item, price, amount, discount etc...
    new_category_en() : New category name in English not item name
    
  """
  item_DB     = iDB.item_DB     # Read item
  category_DB = iDB.category_DB # Read category name
  store_DB    = sDB.store_DB    # Read store name

  def __init__(self,store, tax, all_item, new_category_en):
    """
    ## Description:
      This method is constructor and save data.
    ## Args:
      `store (str)       `: Purchace store name
      `tax (str)         `: Infomation of tax extarnal or internal tax
      `all_item (str[][])`: Got Data from receipt such as item, price, amount, discount etc...
      `new_category_en ()`: New category name in English not item name
    """
    self.store           = store            # Instance argument
    self.tax             = tax              # Instance argument
    self.all_item        = all_item         # Instance argument
    self.new_category_en = new_category_en  # Instance argument
    self.write_file() # Record for CSV file
    self.add_DB()     # Update DataBase
    

  def write_file(self):
    """
    ## Description:
      To write item data for CSV file
    """
    f = open(CSV_PATH_NAME, mode='a') # Open file
    writer = csv.writer(f)
    for line_item in self.all_item:
      writer.writerow(line_item.values()) # Write item
    f.close()
    print("write for csv file") # Notify me that it was saved successfully

  def add_DB(self):
    """
    ## Description:
      Add new item, category name and store name
    """
    for line_item in self.all_item:
      if not(line_item["registered_name"] in line_item["item"]): # whether line_item is special_name
        iDB.special_name[line_item["item"]] = [line_item["registered_name"],str(line_item["category"])]
      if not(line_item["category"] in self.item_DB): # Whether it is new category (= No infomation for DataBase)
        # Add new key for item_DB
        # Make list to include items related to that category
        # value(type) of item_DB is not str but list so set list.
        self.item_DB[line_item["category"]] = []                                              
        self.item_DB[line_item["category"]].append(line_item["registered_name"])              # Add item for new key as value
        self.category_DB[line_item["category"]] = self.new_category_en[line_item["category"]] # Add new key and English value name for category
      elif not(line_item["registered_name"] in self.item_DB[line_item["category"]]):          # Not new category but it is new item
        self.item_DB[line_item["category"]].append(line_item["registered_name"])              # Add item for new key as value
    
    replace_content= "" # Make sentence to overwrite for file

    for key,val in self.item_DB.items(): # Write category name and content of it
      replace_content += self.category_DB[key] + " = " +str(val)+'\n'
    replace_content += "special_name = " +str(iDB.special_name)+'\n'

    ### make item_DB and category_DB argument ###
    replace_content+= "item_DB = {"
    for key in self.category_DB:
      replace_content += "'" + key + "': " + self.category_DB[key] +", "
    replace_content=replace_content[:-2] # delete space and comma
    replace_content += '}\n'
    replace_content += "category_DB = " + str(self.category_DB) + '\n'

    # Overwrite for item_DB.py
    with open(ITEMDB_PATH_NAME,"w") as f:
      f.write(replace_content)
    # Update tax infomation in storeDB.py if tax is internal 
    if self.tax == "内税" and not(self.store in sDB.internal_tax):
      sDB.internal_tax.append(self.store)
    if not(self.store in self.store_DB): # Whether new store name or not
      self.store_DB.append(self.store)
      sDB.keyword[self.store] = ""
    # Get contents in store_db.py as sentence
    with open(STOREDB_PATH_NAME) as file:
      contents = file.readlines()
    # Update store name, keyword and internal tax
    contents[1] = "store_DB = " + str(self.store_DB) + '\n'
    contents[2] = "keyword = " + str(sDB.keyword) + '\n'
    contents[3] = "internal_tax = " + str(sDB.internal_tax) + '\n'
    # Overwrite
    with open(STOREDB_PATH_NAME, mode="w") as file:
      file.writelines("".join(contents))