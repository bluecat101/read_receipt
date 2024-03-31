################################################
# ------------------ README ------------------ #
# do character recognition with Google Coloud  #
# read receipt and analyse                     #
# get name, genre, price, descount and quantity#
#                                              #
################################################

import sys # to happend error for terminal
import io  # to open file
import os  # to get receipt image path from receipt image name
import regex as re # to check whether content in receipt is item, date, store name, and so on.
from pykakasi import kakasi # to convert item name for other character type(平仮名(hiragana),片仮名(katakana))
import mojimoji # to convert item name for other character type(半角カナ(hankakukana))
from google.cloud import vision # to do character recognition for receipt
import datetime as dt # to change date type from year, month and date.
import item_db as iDB # to access item DataBase
import store_db as sDB # to access Store name DataBase


class ReadReceipt:
  """ 
  ## Description
  
  This Class is to read and analyse receipt. 
  After analyse, can get item data, purchase date, purchase store.
  Item data including item name, price, quantity and dicount.
  If read receipt the class must be used. 

  ## Attributes:
    `item_list (dictionary[])`: Store item data line by line 
    ex) [{'item': read item text(str), 
        'registed_name': general item name(str),
        'genre': genre(str),
        'amount': item amount(int),
        'discount': discount amount },
    ]
    `date (str) `: Store purchase date. If can't identify it, store empty characters
    `store (str)`: Store purchase store name. If can't identify it, store empty characters
    `special_discount (str[][])`: Store special discount data like coupon and member discount.
      ex) [[read discount text(str), 
            items eligible for discount(str), 
            discount amount(int)], 
      ]

  """
  def __init__(self,receipt_name,exec_type = "production"):
    """ 
    ## Description
      Set class argument, get full text in receipt and analyse it

    ## Args:
      `receipt_name (str)`: Name of receipt image to use
      `exec_type (str)`: Type of execution
    """
    # Class argument
    self.item_list = []
    self.date = ""
    self.store = ""
    self.special_discount = []
    # Init full_text. if not exec_type is production, cause error no full_text argument
    full_text = ""
    # If exec_type is not production, analysed text is already prepared
    if exec_type == "production":
      # Get receipt path from receipt_name
      image_path =os.path.abspath(receipt_name)
      # Get full text in receipt. format is JSON
      full_text = self.readReceipt(image_path)
      
    # Analyse receipt to get item, purchase store etc...
    self.analyse(exec_type,full_text)
  
  def readReceipt(self,image_path):
    """ 
    ## Description
      Detects text from receipt image using Google Vision
  
    ## Args:
      `image_path` : Path of receipt image
    ## Returns:
      `full_text` (str): Full text in receipt. format is JSON and be included position(x,y) of text
    """
    # Get full text in receipt through Google Vision
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    # Get text
    full_text = response.text_annotations
    # Whether read receipt
    if full_text==[]:
      # Cause error can't read receipt and can't get text
      print("ERROR can not read",sys.stderr)
      exit(1)
    return full_text


  def analyse(self, exec_type,full_text):
    """
    ## Discription
      This method is to analyse receipt content to get some data such as item name, item detail, purchase date, purchase store and etc...
      If get some data, store class argument(self.item_list, self.date and etc...)


    ## Args:
      `exec_type (str)`: Type of execution
      `full_text (str)`: Full text in receipt. format is JSON and be included position(x,y) of text
    
    """
    if exec_type == "production":
      # First element in full_text is full text and its position. this dosen't need for analyse. Because
      # we need text and its position word by word.
      del full_text[0]
      # Disassembe content for each line and save it for line_texts
      line_texts = self.combine(full_text)
      # Sort line_texts by position from top to bottom
      line_texts = sorted(line_texts, reverse=False, key=lambda x: x[2])
    else:
      # TEST_DATA that sample receipt data
      line_texts = [['aaa', 1303, 244, 34.0, 0], ['aaa', 1353, 417, 23.333333333333332, 4], ['レジ06002023/12/24(日)11:55', 1293, 673, 24.666666666666668, 11], ['6369:180310600:002494296', 1354, 716, 22.0, 17], ['AEON会員:********68499401', 1333, 757, 22.666666666666668, 22], ['LBPチョコ596%', 1343, 845, 18.666666666666668, 27], ['(2個X298)', 1302, 874, 20.666666666666668, 31], ['LBPストロベリ298X', 1341, 928, 19.333333333333332, 37], ['ビオ砂糖脂肪O198X', 1315, 970, 24.0, 39], ['トマト350X', 1346, 1010, 18.666666666666668, 43], ['バナナ200%', 1348, 1052, 19.333333333333332, 29], ['はくさい78%', 1374, 1093, 19.333333333333332, 30], ['れんこん320%', 1377, 1133, 18.666666666666668, 44], ['(2個X160)', 1295, 1164, 21.333333333333332, 45], ['柿の種チョコ1,900X', 1273, 1215, 20.0, 51], ['(19個X単100)', 1290, 1248, 22.0, 55], ['ほうれん草50%', 1408, 1298, 21.333333333333332, 62], ['ピーナッツ218X', 1408, 1338, 19.333333333333332, 63], ['きゅうり432*', 1369, 1380, 18.666666666666668, 64], ['(9個X単48)', 1293, 1411, 21.333333333333332, 70], ['なめこ(GE有機)50%', 1335, 1463, 22.666666666666668, 77], ['小松菜88X', 1304, 1503, 20.666666666666668, 82], ['BPもっちり仕込み8138X', 1296, 1543, 21.333333333333332, 84], ['割引20%-28', 1299, 1585, 20.0, 88], ['雪印北海道バター378X', 1306, 1625, 23.333333333333332, 92], ['エキストラバージンオリ698X', 1399, 1667, 20.666666666666668, 95], ['TVたまご496X', 1323, 1708, 16.666666666666668, 98], ['(2個X248)', 1282, 1739, 20.0, 118], ['BP成分無調整牛乳1L356', 1291, 1784, 22.666666666666668, 124], ['(2個X178)', 1279, 1816, 21.333333333333332, 131], ['キリ10P498X', 1290, 1864, 16.666666666666668, 137], ['おじゃがまる654*', 1260, 1905, 18.666666666666668, 103], ['(3個X単218)', 1274, 1936, 21.333333333333332, 111], ['割引30%-198', 1286, 1985, 20.0, 106], ['絹厚揚げ196X', 1252, 2027, 20.666666666666668, 108], ['(2個X単98)', 1272, 2059, 22.0, 139], ['割引20%-40', 1282, 2109, 22.666666666666668, 146], ['がんもセット476X', 1284, 2149, 20.666666666666668, 148], ['(2個X単238)', 1266, 2184, 22.0, 153], ['割引30%-144', 1280, 2234, 22.666666666666668, 160], ['BP油揚げ98X', 1275, 2278, 22.666666666666668, 151], ['割引20%-20', 1278, 2321, 22.666666666666668, 175], ['国産大豆の田舎がんも356X', 1276, 2363, 23.333333333333332, 179], ['(2個X単178)', 1258, 2396, 23.333333333333332, 185], ['割引50%-178', 1272, 2449, 22.0, 192], ['ブロッコリー296X', 1410, 2492, 22.0, 162], ['(2個X148)', 1256, 2528, 22.666666666666668, 165], ['肉いおでん150X', 1236, 2579, 21.333333333333332, 169], ['昭和贅沢餃子338X', 1269, 2622, 22.666666666666668, 172], ['割引50%-169', 1267, 2663, 20.666666666666668, 163], ['大根60%', 1236, 2705, 20.0, 195], ['グリーンオーク160X', 1340, 2746, 20.666666666666668, 197], ['(2個X単80)', 1254, 2778, 22.666666666666668, 199], ['もやし20X', 1303, 2829, 19.333333333333332, 194], ['小計¥9,369', 1236, 2912, 25.333333333333332, 223], ['クーポンはちべえトマト¥100', 1336, 2954, 21.333333333333332, 225], ['クーポンオリーブオイル¥200', 1337, 2997, 24.0, 228], ['クーポンダノンビオ¥30', 1335, 3039, 24.0, 231], ['外税8%対象額¥9,039', 1248, 3080, 24.0, 233], ['外税8%4723', 1251, 3123, 22.666666666666668, 239], ['合計¥9,762', 1305, 3204, 22.666666666666668, 210], ['AEONPay¥9,762', 1266, 3246, 20.0, 211], ['お釣り40', 1228, 3287, 18.666666666666668, 213], ['お買上商品数:67', 1351, 3328, 23.333333333333332, 282], ['※印は軽減税率8%対象商品', 1226, 3366, 23.333333333333332, 288]]
    
    
    # If not found date, you can't get data. So in secound time, you don't mind date and get all data.
    # if self.search_texts(line_texts,status= "first"):
    #   self.search_texts(line_texts,status= "secound")
      self.search_texts(line_texts)

    
  def search_texts(self,line_texts):
    """
    ## Discription
      This method extracts the purchase date, purchase store, item and item-related data such as price, amount etc... from line_texts.
      If the date is not found, this method can't determine where item stert, so read all data from top to bottom.
      
    ## Args:
      `line_texts (str[][])`: Include text line by line
      `status (str)`: Type is "first" or "secound". If the date is not found, this method is called again and the status argument is "secound"

    # Returns:
        # `_ (bool)`: Whether date is found. In first time it is called, if date is not found, it returns False and is called again to set the date to "sample" as a dummy.
    """
    # Whether line_texts[] has price
    # line_texts[] is included about item, discount,total price etc....
    # So some line_texts[] is not for item. Then has_item_price is false.
    has_item_price = True
    # End reading line_texts. If find "小計(subtotal)", the flag is True 
    isFinish = False
    
    # Search line_texts to find item
    for text in line_texts:
      # Use dictionary type for each line.
      item_info={"item": text[0],"registed_name": "---","genre": "---","price":-1,"amount":0,"discount":0}
      # Get purchase store, if it is not found yet
      if self.store == "":
        self.find_store(text[0])
      # Get purchase date, if it is not found yet
      if self.date=="":
        # Date type is yyyy/mm/dd
        result_date = re.search('(20[0-9]{2})(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0])
        if result_date:
          self.date = str(dt.date(int(result_date.group(1)),int(result_date.group(3)),int(result_date.group(5))))
          # Delete item_list before date
          self.item_list.clear()
          continue

        # Date type is mm/dd/yyyy
        result_date = re.search('(日)([1-3][0-9]|[1-9])(月)(1[0-2]|0[1-9]|[1-9])(年)(20[0-9]{2})',text[0])
        if result_date:
          self.date = str(dt.date(int(result_date.group(6)),int(result_date.group(4)),int(result_date.group(2))))
          # Delete item_list before date
          self.item_list.clear()
          continue
      
      # Check text[0] is keyword of starting point for its item
      # If keyword is ""(empty characters), keyword in text[0] is always true, so keyword is necessary
      if self.store != "" and sDB.keyword[self.store] != "" and sDB.keyword[self.store] in text[0]: # whether store keyword is included for text
        # Delete item_list before date
        self.item_list.clear()
        continue
      
      # Find total then finish search
      if "合計" in text[0]:
        break

      # Sometime, discount exist after "小計"(subtotal)
      if isFinish: # After find "小計"(subtotal)
        # Find discount
        if "クーポン" in text[0]:
          # get price
          result_discount= re.search('[0-9]+$',text[0])
          if result_discount:
            # Get discount price
            self.special_discount.append([text[0][:result_discount.start()-1],int(result_discount.group())])
      else: # Before find "小計"(subtotal)
        if "小計" in text[0]: # quit to read item in receipt
          isFinish = True
          continue
        elif re.search('(割引|値引|クーポン)',text[0]): # Find discount line
          if text[0][-1] == '%': # Last character is '%' then calcurate discount price from item price
            text[0]=text[0][:-1] # Delete "%"
            price = re.search('[0-9]+$',text[0]) # Get discount rate
            # Add discount to previous item. Calcurate discount price because price is discount rate
            if(price):
              self.item_list[-1]["discount"] = int(self.item_list[-1]["price"]*(1-(int(price.group())/100))) 
          else: # Last character is not "%"
            price = re.search('[0-9]+$',text[0]) # Get discount price
            # Add discount to previous item
            if(price):
              self.item_list[-1]["discount"] = int(price.group())
        elif re.search('[0-9]+個',text[0]): # text line is not discount and it is related quantity
          try:
            if has_item_price: # Previous line is related item and it was purchased multiple items
              ## 注意お店によって、計算式が違う
              ## 一列に(1つあたりの金額)*(個数)=(合計)がある場合のみ
              ## 1つの値段があって次の行に合計がある場合には不可
              self.item_list[-1]["amount"]=re.search('([0-9]+)個',text[0]).group()[:-1] # get quantity
              self.item_list[-1]["price"]=int((self.item_list[-1]["price"])/int(self.item_list[-1]["amount"])) # add price per one item
            else: # don't have item yet but find quantity
              print("can't find item",sys.stderr)
          except TypeError:
            print("TypeError in finding quantity",sys.stderr)
          except AttributeError:
            print("AttributeError in finding quantity",sys.stderr)
        else: # find item name
          item_info = self.findItem(text[0],item_info) # whether item is register for DB
          # if text[0] == "", item_info is False
          if not(item_info):
            continue
          has_item_price = (item_info["price"] != "") # use has_item_price to search amount
          self.item_list.append(item_info)
    # if date is not found, return false and search secound time 
    # if status == "first":
    #   if self.date == "": self.date = "sample"
    #   # if self.store == "": self.store = "sample"
    # if status == "secound":
    #   if self.date == "sample": self.date = ""
      # if self.store == "sample": self.store = ""
    # print(status,self.date,self.store,self.item_list) 
    # return self.item_list == []
  def find_store(self,text):
    """ find Store name form DataBase """
    for storeName in sDB.storeDB: 
      if storeName in text: # whether store name is included for text
        self.store=storeName
        return True
    return False

  def findItem(self,text,item_info):
    # change data for each store
    text = sDB.setting(self.store,text)
    item_info["item"] = text
    if text == "":
      return False
    # print(text)
    kks = kakasi()
    # get boarder line between item and price
    price = re.search("([0-9]+).?$",text)
    # devide item and price
    if price:
      text = text[:price.start()]
      item_info["item"] = text
      price = int(price.group(1))
      item_info["price"] = int(price)
      item_info["amount"] = 1

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
            item_info["item"] = text
            if any(map(lambda key: text in key, iDB.special_name.keys())):
              for key in iDB.special_name.keys():
                if text in key:
                  registed_name = iDB.special_name[key][0]
                  genre = iDB.special_name[key][1]
                  break
            else:
              registed_name = dbItem
              genre = itemGenre
            # set registed_name and genre
            item_info["registed_name"] = registed_name
            item_info["genre"] = genre
            return item_info
          itemTypeStatus -= 1 # change type
          if itemTypeStatus ==3:
            itemConvert = kks.convert(itemConvert)[0]['hira'] # change type of word for Hiragana
          elif itemTypeStatus ==2:
            itemConvert = kks.convert(itemConvert)[0]['kana'] # change type of word for Katakana
          elif itemTypeStatus ==1:
            itemConvert=mojimoji.zen_to_han(itemConvert) # change type of word for Half Katakana
    return item_info 

  def combine(self,full_text):
    """ search each text in full_text. Get and Combine word. Return words by each line. 2nd argument is all text infomation in receipt. """
    def addNewLine(text):
      """ 1st argument is one line text infomation. """
      data_array=[] # store word info
      data_array.append(text.description) # stored one word
      data_array.append(text.bounding_poly.vertices[1].x) # get word position about x
      data_array.append(text.bounding_poly.vertices[1].y) # get word position about y
      data_array.append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3) # save range that is need to combine other words
      data_array.append(full_text.index(text)) # save index to sort
      return data_array

    lineInfo=[]
    for text in full_text:
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
    return self.item_list
  def getDate(self):
    return self.date
  def getStore(self):
    return self.store


