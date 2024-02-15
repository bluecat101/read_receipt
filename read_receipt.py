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
  def __init__(self,receiptName,test = False):
    self.kakasi = kakasi()
    
    self.test = test
    if not(test):
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
    if not(self.test):
      """ Disassemble content for each line. """
      del self.textsInfo[0]
      lineTexts = self.combine(self.textsInfo) # disassembe content for each line and save it for lineTexts
      # for i in lineTexts:
      #   print(i)
      self.sort(lineTexts) # sort from top to bottom because sometimes disassembling is mistake order.
      """
      """
    else:
      lineTexts = [['英', 2988, 104, 0.6666666666666666, 150], ['SEVENCIOLINGS', 1097, 201, 18.0, 17], ['数', 2989, 207, 0.6666666666666666, 151], ['日(日31月12年2023番号登録者事業:電話9-1市横浜県神奈川横浜セブン-イレブン小雀町店戸塚区小雀町111045-851-7119レジ#217020001093092)21:23青229', 1673, 1083, 132.66666666666666, 0], ['領収書', 1442, 1277, 64.66666666666667, 41], ['7Pアーﾙグレイ無糖600ml*100', 953, 1496, 59.333333333333336, 44], ['7Pハジメリョクチャシズオカ600', 957, 1576, 58.0, 50], ['@100x2*200', 1470, 1693, 45.333333333333336, 56], ['7プレミアムむぎ茶600ml*100', 909, 1792, 54.0, 59], ['塩むすび*100', 963, 1890, 53.333333333333336, 64], ['小計(税抜8%)¥500', 956, 2090, 60.0, 66], ['消費税等(8%)¥40', 1148, 2188, 58.666666666666664, 74], ['合計¥540', 1940, 2305, 48.0, 93], ['(税率8%対象¥540)', 955, 2376, 60.0, 96], ['(内消費税等8%¥40)', 957, 2477, 60.666666666666664, 101], ['商品券支払¥1.000', 1047, 2568, 60.0, 108], ['商品券残高¥460', 1048, 2672, 57.333333333333336, 113], ['¥460', 1936, 2767, 46.666666666666664, 119], ['お買上明細は上記のとおりです。', 957, 2860, 59.333333333333336, 121], ['お', 957, 2869, 47.333333333333336, 118], ['[*]マークは軽減税率対象です。', 907, 2954, 62.666666666666664, 130], ['伝票番号231-231-206-5874', 955, 3045, 56.666666666666664, 140]]
    

    hasPrice=True
    self.itemList=[]
    self.totalInf=[]
    self.specialDiscount=[]
    self.date=""
    self.store=""
    isFinish=False
    is_find_target = True
    # print(lineTexts)
    for text in lineTexts:
      if self.date=="": # until find date in receipt (store name must be exsisted above date)
        if self.store=="": # find store name 
          if self.findStore(text[0]) and (sDB.target[self.store] != ""):
            is_find_target = False
        if re.search('20[0-9]{2}(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0]): 
          result=re.search('(20[0-9]{2})(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0])
          self.date = str(dt.date(int(result.group(1)),int(result.group(3)),int(result.group(5))))
        if  re.search('(日)([1-3][0-9]|[1-9])(月)(1[0-2]|0[1-9]|[1-9])(年)(20[0-9]{2})',text[0]):
          result=re.search('(日)([1-3][0-9]|[1-9])(月)(1[0-2]|0[1-9]|[1-9])(年)(20[0-9]{2})',text[0])
          self.date = str(dt.date(int(result.group(6)),int(result.group(4)),int(result.group(2))))
      elif not(is_find_target):
        if re.search(re.escape(sDB.target[self.store]),text[0]): # whether store target is included for text
          is_find_target = True
        # print("is_find_target:",is_find_target)
      else: # After find self.date
        if re.match("小計",text[0]): # quit to read item in receipt
          isFinish = True
          # self.totalInf=["合計","金額",text]
        elif re.search("合計",text[0]): # get total price and exit roop
          self.totalInf = ["合計","金額",text]
          break
        elif re.search('(クーポン)',text[0]) and isFinish: # find discount
          search= re.search('[0-9]+$',text[0]) # get price
          self.specialDiscount.append([text[0][:search.start()-1],int(search.group())])
          # tmp = text[0][:price()]
        elif re.search('(割引|値引|クーポン)',text[0]) and not(isFinish): # find discount 
          # print()
          # print("yes") if re.search('[割引|値引|クーポン]',text[0]) else print("no")
          if re.match('%',text[0][-1]): # whether last character is "%" in word
            text[0]=text[0][:-1] # delete "%"
            price= re.search('[0-9]+$',text[0]) # get price
            try:
              # calcurate discount price because noe price is  "%"
              self.itemList[len(self.itemList)-1].append(int(self.itemList[len(self.itemList)-1][-1])*(1-(int(price.group())/100))) 
            except TypeError: # can't find price with number
              self.itemList[len(self.itemList)-1].append("---") # can't calcurlate discount
            except AttributeError: # can't get discount
              self.itemList[len(self.itemList)-1].append("---") # can't find discount
          else: # last character is not "%"
            price= re.search('[0-9]+$',text[0])
            # print(text)
            self.itemList[len(self.itemList)-1].append(price.group()) if price else itemInfo.append("---") # store discount price or not find it then put "can't find discount"
        elif re.search('[0-9]個',text[0])and not(isFinish): # word is not discount and it is quantity
          try:
            if hasPrice: # have item and need to get quantity
              self.itemList[len(self.itemList)-1][4]=re.search('([0-9]+)個',text[0]).group()[:-1] # get quantity
              self.itemList[len(self.itemList)-1][3]=int(int(self.itemList[len(self.itemList)-1][3])/int(self.itemList[len(self.itemList)-1][4])) # add price per one item
            else: # don't have item yet but find quantity
              print("can't find item",sys.stderr)
          except TypeError:
            print("TypeError in finding quantity",sys.stderr)
          except AttributeError:
            print("AttributeError in finding quantity",sys.stderr)
        elif not(isFinish): # find item name
          itemInfo=self.findItem(text[0]) # get itemInfo
          if itemInfo !=[]: # match word in DataBase
            while text[0] != "" and re.match('(\D)',text[0][-1]): # delete last charator if it is string
              text[0]=text[0][:-1]
            try:
              itemInfo.append(re.search('[0-9]+$',text[0]).group()) # get price
              itemInfo.append(1) # number of item
              hasPrice = True # find item flag
            except AttributeError: # can't get price
              itemInfo.append("---")
              itemInfo.append(0)
              hasPrice=False
            self.itemList.append(itemInfo)

  def findStore(self,text):
    """ find Store name form DataBase """
    for storeName in sDB.storeDB: 
      if re.search(re.escape(storeName),text): # whether store name is included for text
        self.store=storeName
        return True
    return False

  def findItem(self,text):
    text = sDB.setting(self.store,text)
    """ find item name from DataBase. 2nd argument is word maybe it become item name. """
    itemInfo=[]
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
            if re.match('[0-9]',text): # if first character is number
              price=re.match('[0-9]*',text) # get price from first character
              text=text[price.end():]+price.group() # change the order 
            try:
              itemInfo.append(text[:re.search("[0-9]+.?$",text).start()]) # append text from first to previous
            except:
              itemInfo.append(text)
            if text in iDB.special_name.keys():
              itemInfo.append(iDB.special_name[text][0])
              itemInfo.append(iDB.special_name[text][1])
            else:
              itemInfo.append(dbItem)
              itemInfo.append(itemGenre)
            break
          itemTypeStatus -= 1 # change type
          if itemTypeStatus ==3:
            itemConvert = self.kakasi.convert(itemConvert)[0]['hira'] # change type of word for Hiragana
          elif itemTypeStatus ==2:
            itemConvert = self.kakasi.convert(itemConvert)[0]['kana'] # change type of word for Katakana
          elif itemTypeStatus ==1:
            itemConvert=mojimoji.zen_to_han(itemConvert) # change type of word for Half Katakana
        if itemInfo!=[]: # find name from DataBase
          break
      if itemInfo!=[]: # find name from DataBase
          break
    else: # can't find name from DataBase
      try: # get item name
        itemInfo.append(text[:re.search("[0-9]+.?$",text).start()])
      except:
        itemInfo.append(text)
      itemInfo.append("---") # can't find itemDB
      itemInfo.append("---") # can't find genre
    return itemInfo # itemInfo[0]: item name, itemInfo[1]: item DB name, itemInfo[2]: genre
  # def familyMart(self,lineTexts):

    

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

