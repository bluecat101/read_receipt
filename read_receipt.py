################################################
# ------------------ README ------------------ #
# do character recognition with Google Coloud  #
# read receipt and alaryse                     #
# get name, genre, price, descount and qunattiy#
#                                              #
################################################

import sys
import io
import os
import regex as re
from pykakasi import kakasi
import mojimoji
from google.cloud import vision
import io
import item_db as iDB
import store_db as sDB
import datetime as dt

class ReadReceipt:
  def __init__(self,receiptName,exec_type = "production"):
    self.kakasi = kakasi()
    self.exec_type = exec_type
    if exec_type == "production":
      self.path =os.path.abspath(receiptName) # set image path
      self.readReceipt()
      self.textsInfo # to save all content in receipt
    else:
      self.analyse()
  
  def readReceipt(self):
    """ Detects text in the file. Call analyse function. """
    client = vision.ImageAnnotatorClient()
    with io.open(self.path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    self.textsInfo = response.text_annotations # save content
    if self.textsInfo==[]: # can't read receipt
      print("ERROR can not read")
      exit(1)
    else:
      self.analyse() # analyse text


  def analyse(self): 
    if self.exec_type == "production":
      """ Disassemble content for each line. """
      del self.textsInfo[0]
      lineTexts = self.combine(self.textsInfo) # disassembe content for each line and save it for lineTexts
      # for i in lineTexts:
      #   print(i)
      self.sort(lineTexts) # sort from top to bottom because sometimes disassembling is mistake order.
    else:
      lineTexts = [['英', 2988, 104, 0.6666666666666666, 150], ['SEVENCIOLINGS', 1097, 201, 18.0, 17], ['数', 2989, 207, 0.6666666666666666, 151], ['日(日31月12年2023番号登録者事業:電話9-1市横浜県神奈川横浜セブン-イレブン小雀町店戸塚区小雀町111045-851-7119レジ#217020001093092)21:23青229', 1673, 1083, 132.66666666666666, 0], ['領収書', 1442, 1277, 64.66666666666667, 41], ['塩むすび*100※', 953, 1496, 59.333333333333336, 44],['割引33', 953, 1700, 59.333333333333336, 44], ['2個X単価', 963, 1890, 53.333333333333336, 64], ['小計(税抜8%)¥500', 956, 2090, 60.0, 66], ['消費税等(8%)¥40', 1148, 2188, 58.666666666666664, 74], ['合計¥540', 1940, 2305, 48.0, 93], ['(税率8%対象¥540)', 955, 2376, 60.0, 96], ['(内消費税等8%¥40)', 957, 2477, 60.666666666666664, 101], ['商品券支払¥1.000', 1047, 2568, 60.0, 108], ['商品券残高¥460', 1048, 2672, 57.333333333333336, 113], ['¥460', 1936, 2767, 46.666666666666664, 119], ['お買上明細は上記のとおりです。', 957, 2860, 59.333333333333336, 121], ['お', 957, 2869, 47.333333333333336, 118], ['[*]マークは軽減税率対象です。', 907, 2954, 62.666666666666664, 130], ['伝票番号231-231-206-5874', 955, 3045, 56.666666666666664, 140]]
    

    self.itemList=[]
    self.totalInf=[]
    self.specialDiscount=[]
    self.date=""
    self.store=""
    # if not found date, you can't get data so in secound time, you don't mind date
    if self.search_texts(lineTexts,status= "first"):
      self.search_texts(lineTexts,status= "secound")
      self.date = ""  # reset date
      self.store = "" # reset date

    
  def search_texts(self,lineTexts,status):
    # text[0] has price
    hasPrice=True
    # read word of "小計"
    isFinish=False
    exist_target = True # don't read item until the target word exist
    if status == "secound":
      # make dummy not to mind date and store
      self.date = "sample"  # dummy date
      self.store = "sample" # dummy store
    for text in lineTexts:
      itemInfo={"item": text[0],"register_name": "---","genre": "---","price":-1,"amount":0,"discount":0}
      if self.date=="": # until find date in receipt (store name must be exsisted above date)
        if self.store=="": # find store name 
          if self.findStore(text[0]) and (sDB.target[self.store] != ""):
            exist_target = False
        if re.search('20[0-9]{2}(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0]): 
          result=re.search('(20[0-9]{2})(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0])
          self.date = str(dt.date(int(result.group(1)),int(result.group(3)),int(result.group(5))))
        if  re.search('(日)([1-3][0-9]|[1-9])(月)(1[0-2]|0[1-9]|[1-9])(年)(20[0-9]{2})',text[0]):
          result=re.search('(日)([1-3][0-9]|[1-9])(月)(1[0-2]|0[1-9]|[1-9])(年)(20[0-9]{2})',text[0])
          self.date = str(dt.date(int(result.group(6)),int(result.group(4)),int(result.group(2))))
      elif not(exist_target):
        if re.search(re.escape(sDB.target[self.store]),text[0]): # whether store target is included for text
          exist_target = True
      elif isFinish:
        if re.search('(クーポン)',text[0]): # find discount
          search= re.search('[0-9]+$',text[0]) # get price
          self.specialDiscount.append([text[0][:search.start()-1],int(search.group())])
        if re.search("合計",text[0]): # get total price and exit roop
          break
      else: # After find self.date
        if re.match("小計",text[0]): # quit to read item in receipt
          isFinish = True
        elif re.search("合計",text[0]): # get total price and exit roop
          break
        elif re.search('(割引|値引|クーポン)',text[0]): # find discount 
          if re.match('%',text[0][-1]): # whether last character is "%"
            text[0]=text[0][:-1] # delete "%"
            price= re.search('[0-9]+$',text[0]) # get price
            print(self.itemList,price,text[0])
            # calcurate discount price because noe price is  "%"
            self.itemList[-1]["discount"] = int(self.itemList[-1]["price"]*(1-(int(price.group())/100))) 
          else: # last character is not "%"
            price= re.search('[0-9]+$',text[0]) # get price
            self.itemList[-1]["discount"] = int(price.group())
            
        elif re.search('[0-9]個',text[0]): # word is not discount and it is quantity
          try:
            if hasPrice: # have item and need to get quantity
              ## 注意お店によって、計算式が違う
              ## 一列に(1つあたりの金額)*(個数)=(合計)がある場合のみ
              ## 1つの値段があって次の行に合計がある場合には不可
              self.itemList[-1]["amount"]=re.search('([0-9]+)個',text[0]).group()[:-1] # get quantity
              self.itemList[-1]["price"]=int((self.itemList[-1]["price"])/int(self.itemList[-1]["amount"])) # add price per one item
            else: # don't have item yet but find quantity
              print("can't find item",sys.stderr)
          except TypeError:
            print("TypeError in finding quantity",sys.stderr)
          except AttributeError:
            print("AttributeError in finding quantity",sys.stderr)
        else: # find item name
          itemInfo = self.findItem(text[0],itemInfo) # whether item is register for DB
          hasPrice = (itemInfo["price"] != "") # use hasPrice to search amount
          self.itemList.append(itemInfo)
    # if date is not found, return false and search secound time 
    return self.date == ""  
  def findStore(self,text):
    """ find Store name form DataBase """
    for storeName in sDB.storeDB: 
      if re.search(re.escape(storeName),text): # whether store name is included for text
        self.store=storeName
        return True
    return False

  def findItem(self,text,itemInfo):
    # change data for each store
    text = sDB.setting(self.store,text)
    # get boarder line between item and price
    price = re.search("([0-9]+).?$",text)
    # devide item and price
    if price:
      text = text[:price.start()]
      price = int(price.group())
      itemInfo["price"] = int(price)
      itemInfo["amount"] = 1

    """ find item name from DataBase. 2nd argument is word maybe it become item name. """
    for itemGenre,itemValue in iDB.itemDB.items(): # roop from DB
      for dbItem in itemValue: # roop in each item name
        itemConvert=dbItem # get DB item name to change Kanji, Hiragana, Katakana and Half Katakana.
        ### check type of item name in DB whether Kanji, Hiragana, Katakana and Half Katakana and change status. ###
        if re.match('^\p{Script=Han}+$', itemConvert): # Kanji
          itemTypeStatus = 4
        elif re.match('[あ-ん]+', itemConvert): # Hiragana
          itemTypeStatus = 3
        elif re.match('[ア-ン]+', itemConvert): # Katakana
          itemTypeStatus = 2
        elif re.match('[ｱ-ﾝ]+', itemConvert): # Half Katakana
          itemTypeStatus = 1
        else: # English, Other language or combination of tow character type
          itemTypeStatus=0
        while itemTypeStatus != -1:
          regular=re.escape(itemConvert)  # make regular expression object.
          if re.search(regular,text) or text in iDB.special_name.keys(): # if itemConvert is included in text
            itemInfo["item"] = text
            if text in iDB.special_name.keys():
              # specialnameと完全一致以外も入れる
              register_name = iDB.special_name[text][0]
              genre = iDB.special_name[text][1]
            else:
              register_name = dbItem
              genre = itemGenre
            # set register_name and genre
            itemInfo["register_name"] = register_name
            itemInfo["genre"] = genre
            return itemInfo
          itemTypeStatus -= 1 # change type
          if itemTypeStatus ==3:
            itemConvert = self.kakasi.convert(itemConvert)[0]['hira'] # change type of word for Hiragana
          elif itemTypeStatus ==2:
            itemConvert = self.kakasi.convert(itemConvert)[0]['kana'] # change type of word for Katakana
          elif itemTypeStatus ==1:
            itemConvert=mojimoji.zen_to_han(itemConvert) # change type of word for Half Katakana
    return itemInfo 

  def combine(self,textsInfo):
    """ search each text in textsInfo. Get and Combine word. Return words by each line. 2nd argument is all text infomation in reciept. """
    def addNewLine(text):
      """ 1st argument is one line text infomation. """
      data_array=[] # store word info
      data_array.append(text.description) # stored one word
      data_array.append(text.bounding_poly.vertices[1].x) # get word position about x
      data_array.append(text.bounding_poly.vertices[1].y) # get word position about y
      data_array.append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3) # save range that is need to combine other words
      data_array.append(textsInfo.index(text)) # save index to sort
      return data_array

    lineInfo=[]
    for text in textsInfo:
      if lineInfo==[]: # first roop
        lineInfo.append(addNewLine(text)) # save for lineInfo array
      else: # secound time onwards roop 
        if(text.bounding_poly.vertices[0].y >lineInfo[-1][2]-lineInfo[-1][3] and text.bounding_poly.vertices[0].y <lineInfo[-1][2]+lineInfo[-1][3]):
          """ Whethrer this text is included preve word's range """
          if lineInfo[-1][1]<text.bounding_poly.vertices[1].x: # Whther position of this text is after prev word.
            lineInfo[-1][0]+=text.description # connect prev word and this word
          else:
            lineInfo[-1][0]=text.description+lineInfo[-1][0] # connect prev word and this word
          lineInfo[-1][2]=text.bounding_poly.vertices[1].y # update position y
        else:
          for line in reversed(lineInfo): # search word form last word
            if(text.bounding_poly.vertices[0].y >line[2]-line[3] and text.bounding_poly.vertices[0].y <line[2]+line[3]):
              """ Whethrer this text is included preve word's range """
              if line[1]<text.bounding_poly.vertices[1].x: # Whther position of this text is after prev word.
                line[0]+=text.description # connect prev word and this word
              else:
                line[0]=text.description+line[0] # connect prev word and this word
              line[2]=text.bounding_poly.vertices[1].y # update position y
              break
          else: # can't find some position word in lineInfo
            lineInfo.append(addNewLine(text)) # save for lineInfo array
    return lineInfo
  

  def sort(self,data):
    """ quickSort by index as textsInfo. 2nd infomation is infomation """
    def findPivot(data,left,right): # get Pivot
      return data[int((left+right)/2)]
    
    def quickSort(data,left,right):
      if left>=right:
        return 0
      pivot=findPivot(data,left,right) # get pivot
      i=left
      j=right
      while(1):
        while(data[i][2]<pivot[2]): # find position i
          i+=1
        while(data[j][2]>pivot[2]): # find position j
          j-=1
        if i>=j:
          break
        ### swap ###
        tmp=data[i]
        data[i]=data[j]
        data[j]=tmp
        i+=1
        j-=1
      quickSort(data,left,i-1)  # recursing
      quickSort(data,j+1,right) # recursing
      return 0
    quickSort(data,0,len(data)-1) # exec when called sort()

  def getItemLine(self):
    return self.itemList
  def getTotal(self):
    return self.totalInf
  def getDate(self):
    return self.date
  def getStore(self):
    return self.store

