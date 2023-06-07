import item_db as db
import csv
import re

CSV_PATH_NAME = "output.csv"
ITEMDB_PATH_NAME = "item_db.py"

class RecordReceipt:
  itemDB = db.itemDB
  categoryDB = db.categoryDB
  def __init__(self,allItem,newCategoryEn,date,store):
    self.allItem=allItem
    self.newCategoryEn=newCategoryEn
    self.date=date
    self.store=store
    self.writeFile()
    self.addDB()

  def writeFile(self):
    f = open(CSV_PATH_NAME, mode='a')
    writer = csv.writer(f)
    writer.writerow([self.date,self.store])

    for lineItem in self.allItem:
      writer.writerow(lineItem)
    f.close()
    print("write for csv file")



  def addDB(self):
    newCategory={}
    for lineItem in self.allItem:
      if not(lineItem[2] in self.itemDB):
        self.itemDB[lineItem[2]] = []# 追加する
        self.itemDB[lineItem[2]].append(lineItem[1])

        newCategory[lineItem[2]] = []# 追加する
      elif not(lineItem[1] in self.itemDB[lineItem[2]]):
        self.itemDB[lineItem[2]].append(lineItem[1])

    for key in newCategory:
      newCategory[key]=self.itemDB[key]
    replaceContent=""

    for key,val in self.itemDB.items():
      if key in newCategory:
        replaceContent += self.newCategoryEn[key] +" = "+str(val)+'\n'
      else:
        replaceContent += self.categoryDB[key] + " = " +str(val)+'\n'

    for key,value in self.newCategoryEn.items():
      self.categoryDB[key]=value 
    
    replaceContent+= "itemDB = {"
    for key in self.categoryDB:
      replaceContent += "'" + key + "': " + self.categoryDB[key] +", "
    replaceContent=replaceContent[:-2]
    replaceContent += '}\n'
    replaceContent += "categoryDB = " + str(self.categoryDB) + '\n'
    with open(ITEMDB_PATH_NAME,"w") as f:
      f.write(replaceContent)


""""""
if __name__=="__main__":
  items=[
        ['2', '牛乳', '乳製品', '4', '7', '0', '28']
        ,['2', 'newItem', '乳製品', '4', '7', '0', '28']
        ,['fff', 'newItem', '新しい', '4', '5', '6', '14']
        ,['fff', 'newItem', '新しい', '4', '5', '6', '14']
        ,['fff', 'newItem2', '新しい', '4', '5', '6', '14']
        ]
  # newCategoryEn={"新しい": "newcategory"}
  newCategoryEn={}
  app=RecordReceipt(items,newCategoryEn)
