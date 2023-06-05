import item_db as db
import csv
import re
import regex

CSV_PATH_NAME = "output.csv"
ITEMDB_PATH_NAME = "item_db.py"

class RecordReceipt:
  itemDB = db.itemDB
  def __init__(self,allItem,newCategoryEn):
    self.allItem=allItem
    # self.writeFile()
    self.newCategoryEn=newCategoryEn
    # print(self.newCategoryEn)

    self.addDB()
    # if  newCategoryEn=={}:
    #   print(newCategoryEn)
    #   print(type(newCategoryEn))
    
    # if 

  def writeFile(self):
    f = open(CSV_PATH_NAME, mode='a')
    writer = csv.writer(f)
    for lineItem in self.allItem:
      writer.writerow(lineItem)
    f.close()
    print("write for csv file")



  def addDB(self):
    originCategoryNum=len(self.itemDB.keys())
    # print(originCategoryNum)
    newCategory={}
    # newCategoryEn={}
    for lineItem in self.allItem:
      if not(lineItem[2] in self.itemDB):
        self.itemDB[lineItem[2]] = []# 追加する
        self.itemDB[lineItem[2]].append(lineItem[1])

        newCategory[lineItem[2]] = []# 追加する
        # newCategory[lineItem[2]].append(lineItem[1])
      elif not(lineItem[1] in self.itemDB[lineItem[2]]):
        self.itemDB[lineItem[2]].append(lineItem[1])
    for key in newCategory:
      newCategory[key]=self.itemDB[key]

    fRead = open(ITEMDB_PATH_NAME,"r")
    lineFILE = fRead.readlines()
    currentLine=0
    replaceContent=""
    categoryList=self.itemDB.copy()
    for key,val in self.itemDB.items():
      try:
        categoryName = re.match('^.+=',lineFILE[currentLine]).group()
        categoryName=categoryName[:-2]
        # print(repr(categoryName))
      except:
        categoryName = "noname"
        # replaceContent+=lineFILE[currentLine]
      categoryList[key]=categoryName
      if not(str(val) in lineFILE[currentLine]):
        replaceContent+=categoryName+" = "+str(val)+'\n'
      else:
        replaceContent+=lineFILE[currentLine]
      currentLine+=1
      if(currentLine >= originCategoryNum):
        break

    for key in newCategory:
      categoryList[key]=self.newCategoryEn[key]

    # print(newCategory)
    # print(categoryList)

    for key,value in newCategory.items():
      # print(key)
      replaceContent += self.newCategoryEn[key] +" = "+ str(value) + '\n'
    # print(self.itemDB)
    # print(categoryList)

    replaceContent+= "itemDB = {"
    for key in self.itemDB.keys():
      replaceContent += "'" + key + "': " + categoryList[key] +", "
    replaceContent=replaceContent[:-2]
    replaceContent += '}\n'
    # print(replaceContent)
    fRead.close()
    with open(ITEMDB_PATH_NAME,"w") as f:
      f.write(replaceContent)
    # print("------")
    # print(self.itemDB)


if __name__=="__main__":
  items=[
        ['2', '牛乳', '乳製品', '4', '7', '0', '28']
        ,['2', 'newItem', '乳製品', '4', '7', '0', '28']
        ,['fff', 'newItem', '新しい', '4', '5', '6', '14']
        ,['fff', 'newItem', '新しい', '4', '5', '6', '14']
        ,['fff', 'newItem2', '新しい', '4', '5', '6', '14']
        ]
  newCategoryEn={"新しい": "newcategory"}
  app=RecordReceipt(items,newCategoryEn)
