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
      lineTexts = sorted(lineTexts, reverse=False, key=lambda x: x[2])
      # print(lineTexts)
      for i in lineTexts:
        print(i[2])

    else:
      lineTexts = [['/EONFOODSTYLE', 1303, 244, 34.0, 0], ['TELイオンフードスタイル港南台店045-832-1361', 1353, 417, 23.333333333333332, 4], ['領収証', 1490, 491, 42.0, 100], ['株式会社ダイエー', 1672, 583, 16.0, 65], ['登録番号T4140001005666', 1472, 623, 25.333333333333332, 67], ['レジ06002023/12/24(日)11:55', 1293, 673, 24.666666666666668, 11], ['6369:180310600:002494296', 1354, 716, 22.0, 17], ['AEON会員:********68499401', 1333, 757, 22.666666666666668, 22], ['LBPチョコ596%', 1343, 845, 18.666666666666668, 27], ['(2個X298)', 1302, 874, 20.666666666666668, 31], ['LBPストロベリ298X', 1341, 928, 19.333333333333332, 37], ['ビオ砂糖脂肪O198X', 1315, 970, 24.0, 39], ['トマト350X', 1346, 1010, 18.666666666666668, 43], ['バナナ200%', 1348, 1052, 19.333333333333332, 29], ['はくさい78%', 1374, 1093, 19.333333333333332, 30], ['れんこん320%', 1377, 1133, 18.666666666666668, 44], ['(2個X160)', 1295, 1164, 21.333333333333332, 45], ['柿の種チョコ1,900X', 1273, 1215, 20.0, 51], ['(19個X単100)', 1290, 1248, 22.0, 55], ['ほうれん草50%', 1408, 1298, 21.333333333333332, 62], ['ピーナッツ218X', 1408, 1338, 19.333333333333332, 63], ['きゅうり432*', 1369, 1380, 18.666666666666668, 64], ['(9個X単48)', 1293, 1411, 21.333333333333332, 70], ['なめこ(GE有機)50%', 1335, 1463, 22.666666666666668, 77], ['小松菜88X', 1304, 1503, 20.666666666666668, 82], ['BPもっちり仕込み8138X', 1296, 1543, 21.333333333333332, 84], ['割引20%-28', 1299, 1585, 20.0, 88], ['雪印北海道バター378X', 1306, 1625, 23.333333333333332, 92], ['エキストラバージンオリ698X', 1399, 1667, 20.666666666666668, 95], ['TVたまご496X', 1323, 1708, 16.666666666666668, 98], ['(2個X248)', 1282, 1739, 20.0, 118], ['BP成分無調整牛乳1L356', 1291, 1784, 22.666666666666668, 124], ['(2個X178)', 1279, 1816, 21.333333333333332, 131], ['キリ10P498X', 1290, 1864, 16.666666666666668, 137], ['おじゃがまる654*', 1260, 1905, 18.666666666666668, 103], ['(3個X単218)', 1274, 1936, 21.333333333333332, 111], ['割引30%-198', 1286, 1985, 20.0, 106], ['絹厚揚げ196X', 1252, 2027, 20.666666666666668, 108], ['(2個X単98)', 1272, 2059, 22.0, 139], ['割引20%-40', 1282, 2109, 22.666666666666668, 146], ['がんもセット476X', 1284, 2149, 20.666666666666668, 148], ['(2個X単238)', 1266, 2184, 22.0, 153], ['割引30%-144', 1280, 2234, 22.666666666666668, 160], ['BP油揚げ98X', 1275, 2278, 22.666666666666668, 151], ['割引20%-20', 1278, 2321, 22.666666666666668, 175], ['国産大豆の田舎がんも356X', 1276, 2363, 23.333333333333332, 179], ['(2個X単178)', 1258, 2396, 23.333333333333332, 185], ['割引50%-178', 1272, 2449, 22.0, 192], ['ブロッコリー296X', 1410, 2492, 22.0, 162], ['(2個X148)', 1256, 2528, 22.666666666666668, 165], ['肉いおでん150X', 1236, 2579, 21.333333333333332, 169], ['昭和贅沢餃子338X', 1269, 2622, 22.666666666666668, 172], ['割引50%-169', 1267, 2663, 20.666666666666668, 163], ['大根60%', 1236, 2705, 20.0, 195], ['グリーンオーク160X', 1340, 2746, 20.666666666666668, 197], ['(2個X単80)', 1254, 2778, 22.666666666666668, 199], ['もやし20X', 1303, 2829, 19.333333333333332, 194], ['小計¥9,369', 1236, 2912, 25.333333333333332, 223], ['クーポンはちべえトマト¥100', 1336, 2954, 21.333333333333332, 225], ['クーポンオリーブオイル¥200', 1337, 2997, 24.0, 228], ['クーポンダノンビオ¥30', 1335, 3039, 24.0, 231], ['外税8%対象額¥9,039', 1248, 3080, 24.0, 233], ['外税8%4723', 1251, 3123, 22.666666666666668, 239], ['合計¥9,762', 1305, 3204, 22.666666666666668, 210], ['AEONPay¥9,762', 1266, 3246, 20.0, 211], ['お釣り40', 1228, 3287, 18.666666666666668, 213], ['お買上商品数:67', 1351, 3328, 23.333333333333332, 282], ['※印は軽減税率8%対象商品', 1226, 3366, 23.333333333333332, 288]]
    

    self.itemList=[]
    self.totalInf=[]
    self.specialDiscount=[]
    self.date=""
    self.store=""
    # if not found date, you can't get data so in secound time, you don't mind date
    if self.search_texts(lineTexts,status= "first"):
      self.search_texts(lineTexts,status= "secound")

    
  def search_texts(self,lineTexts,status):
    # text[0] has price
    hasPrice=True
    # read word of "小計"
    isFinish=False
    exist_target = True # don't read item until the target word exist
    # print(sDB.target)
    if self.store in sDB.target and (sDB.target[self.store] != ""): exist_target = False
    # if status == "secound":
      # make dummy not to mind date and store
      # self.date = "sample"  # dummy date
      # self.store = "sample" # dummy store
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
            # print(self.itemList,price,text[0])
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
          # if text[0] == "", itemInfo is False
          if not(itemInfo):
            continue
          hasPrice = (itemInfo["price"] != "") # use hasPrice to search amount
          self.itemList.append(itemInfo)
    # if date is not found, return false and search secound time 
    if status == "first":
      if self.date == "": self.date = "sample"
      if self.store == "": self.store = "sample"
    if status == "secound":
      if self.date == "sample": self.date = ""
      if self.store == "sample": self.store = ""
    # print(status,self.date,self.store,self.itemList) 
    return self.itemList == []
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
    itemInfo["item"] = text
    if text == "":
      return False
    # print(text)
    # get boarder line between item and price
    price = re.search("([0-9]+).?$",text)
    # devide item and price
    if price:
      text = text[:price.start()]
      itemInfo["item"] = text
      price = int(price.group(1))
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
            if any(map(lambda key: text in key, iDB.special_name.keys())):
              for key in iDB.special_name.keys():
                if text in key:
                  register_name = iDB.special_name[key][0]
                  genre = iDB.special_name[key][1]
                  break
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
  

  def getItemLine(self):
    return self.itemList
  def getTotal(self):
    return self.totalInf
  def getDate(self):
    return self.date
  def getStore(self):
    return self.store


