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
    # Init recognition_result. if not exec_type is production, cause error no recognition_result argument
    recognition_result = ""
    # If exec_type is not production, analysed text is already prepared
    if exec_type == "production":
      # Get receipt path from receipt_name
      image_path =os.path.abspath(receipt_name)
      # Get text and coordinates of it from receipt. format is like JSON
      recognition_result = self.do_character_recogition(image_path)
      
    # Analyse receipt to get item, purchase store etc...
    line_text = self.analyse(exec_type,recognition_result)
    self.search_texts(line_text)
  
  def do_character_recogition(self,image_path):
    """ 
    ## Description
      Detects text from receipt image using Google Vision
  
    ## Args:
      `image_path` : Path of receipt image
    ## Returns:
      `recognition_result (str)`: Full text and coordinates for each word in receipt. format is JSON and be included position(x,y) of text
    """
    # Get full text in receipt through Google Vision
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    # Get text
    recognition_result = response.text_annotations
    # Whether read receipt
    if recognition_result==[]:
      # Cause error can't read receipt and can't get text
      print("ERROR can not read",sys.stderr)
      exit(1)
    return recognition_result


  def analyse(self, exec_type, recognition_result):
    """
    ## Discription:
      To restore sentences based on the results of character recognition.
      Character recognition may not be possible on each line because there are too many spaces or some characters are unreadable.
      Therefore, we restore each line based on the coordinates of each word.

    ## Args:
      `exec_type (str)`: Type of execution
      `recognition_result (str)`: Full text in receipt. Format is like JSON and be included position(x,y) of text
    
    ## Returns:
      `line_text (str[])`: Text of each restored line from receipt.
    """
    def add_height_border(analysed_text):
      """
      ## Discription:
        Add height area for top and bottom borders because, to determine whether tow words are in the same line.
        Ranges to be on the same line is the word heights plus half of it.
      ## Args:
        analysed_text (disc["text":,"vertices":]): Data is added top and bottom borders
      """
      # get half the height
      height_rigion = (analysed_text["vertices"][2]["y"] - analysed_text["vertices"][1]["y"])*1/2
      # add top and bottom borders to analysed_text
      analysed_text["top_border"] = analysed_text["vertices"][1]["y"] - height_rigion
      analysed_text["bottom_border"] = analysed_text["vertices"][2]["y"] + height_rigion
  
    def concat_text(first,second):
      """
      ## Discription:
        This method is to connects argument of first and argument of second in order.
        If the connecting parts are numbers, add a space to easily judge.

      ## Args:
        first (str): first text
        second (str): last text

      Returns:
          connected text: Pattern is (first + second) or (first +" "+ second)
      """
      if first == "" or second == "": # To avoid IndexError
        return first + second
      elif first[-1].isdecimal() and second[0].isdecimal(): # add a space
        return first + " " + second
      else: # not need a space
        return first + second
      
    def update_coordinates(updated_data ,update_data, position):
      """
      ## Description:
        This method is to update coordinates when find and connect text on the same line
      ## Args:
          `updated_data (dict)`: Updated dict 
          `update_data (dict,google.cloud.vision_v1.types.image_annotator.EntityAnnotation)`: Update dict or Google data
          If update data first time from result of OCR, the type is Google data.
          `position (int)`: Where you update, 0, 1, 2 or 3.
      """
      # Update coordinates of x and y
      if type(update_data) is dict: # Type is dict
        updated_data["vertices"][position]["x"] = update_data["vertices"][position]["x"]
        updated_data["vertices"][position]["y"] = update_data["vertices"][position]["y"]
      else: # Type is google.cloud.vision_v1.types.image_annotator.EntityAnnotation
        updated_data["vertices"][position]["x"] = update_data.bounding_poly.vertices[position].x
        updated_data["vertices"][position]["y"] = update_data.bounding_poly.vertices[position].y
        
        
      
    if "develop" in exec_type: # don't analyse
      # TEST_DATA that sample receipt data
      line_text = ['そうてつローゼン', '港南台店TEL:045(832)1211', '相鉄ローゼン株式会社', '本社住所:横浜市西区北幸2-9-14', '登録番号:T9020001037881', '*********', '毎度ご来店ありがとうございます', '今月は休まず営業いたします', '**************', '2024年1月27日(土)16:14', '*202005ほうれん草', '¥98 2個 ¥196', '*202004大根', '¥98 2個 ¥196', '*202001なす袋入', '¥198 2個 ¥396', '*101001コウジミリ750g', '¥158 2個 ¥316', '外税8.0% ¥88', '税込小計8点 \\1,192', 'ガチャクーポン1枚 -\\50', '合計', '(税込8.0%対象額 ¥1,142', '¥1,142)', '8.0%消費税等 ¥84', '税額計 ¥84', '*」は軽減税率対象商品です', 'ホット \\1,142', '\\1,142', '顧客コード*********0617', 'カード発行会社ラクテンカード 00056', '****8624I', '会員番号************8624', 'お取扱日2024-01-27 16:14:04', '真番号 取引内容', '410421833 お買上', '取扱区分 承認番号', '(110)00761523', '分割回数処理通番合計額(TOTAL)', '1221 ¥1,142', 'A0000000031010 ATC000d00IC', 'ALVISACREDIT', '加盟店', '相鉄ローゼン港南台店', 'TEL:045-832-1211', '★今月ランクレギュラー', '<<ポイント情報>>', '1,104円', 'ポイント対象金額 1,104円)', '(うち3倍対象', '前回累計ポイント 3,283A', '剪圖 上ポイント 15点', '3,298点', '累計ポイント', '2,172円', '今月買上金額累計', '鍵', '来月ラングレギュラー', '今月あと17828円お買上げで', 'ブロンズにランクUP', '来月5日に50Pプレゼント', 'キャッシャ:鈴木啓', 'R4104-#1221']
      return line_text
    # First element in recognition_result is full text. Use this text to judge whether each text is same line or not.
    # First element is to use '\n'(new line code) so split with '\n' and return type of array
    full_text = recognition_result[0].description.split('\n')
    # delete first element 
    del recognition_result[0]
    # To save connected text and its infomation of coordinates
    # To connect text on each line, do 2 step.
    # STEP1: connect text from full_text data. If full_text show tow word is same line, connect them
    # STEP2: connect text from word of coordinates. 
    # So the argument name is ver1 and after two step, name is "line_text_info"
    line_text_info_ver1 = []
    # [STEP1]
    # Point to where it is looking in full_text
    pointer_for_full_text = 0
    # Initialize to save line_text_info_ver1
    # vertices[0] is left top, vertices[1] is right top, vertices[2] is right bottom, vertices[3] is left bottom
    one_line = {"text": "","vertices":[{"x":-1,"y":-1},{"x":-1,"y":-1},{"x":-1,"y":-1},{"x":-1,"y":-1}]}
    for word in recognition_result:
      # Until get some word in full_text 
      # Coordinates in recognition_result are absolute in full_text order, so you can search in order.
      while len(full_text) > pointer_for_full_text and not(word.description in full_text[pointer_for_full_text]):
        if one_line["text"] != "": # Find text data
          line_text_info_ver1.append(one_line)
          # Reset one_line to save line_text_info_ver1
          one_line = {"text": "","vertices":[{"x":-1,"y":-1},{"x":-1,"y":-1},{"x":-1,"y":-1},{"x":-1,"y":-1}]}
        # Move pointer to point next
        pointer_for_full_text += 1
        # Finish to search
        if len(full_text) <= pointer_for_full_text:
         break
      # Delete found word to avoid duplicates
      full_text[pointer_for_full_text] = full_text[pointer_for_full_text].lstrip(word.description)
      if one_line["text"] == "": # First new line word and is not connection of words
        update_coordinates(one_line, word, 0) # Update left top coordinates
        update_coordinates(one_line, word, 3) # Update left bottom coordinates
      update_coordinates(one_line, word, 1)   # Update right top coordinates
      update_coordinates(one_line, word, 2)   # Update right bottom coordinates
      # Connects text
      one_line["text"] = concat_text(one_line["text"],word.description)
    
    # [STEP2]
    add_height_border(line_text_info_ver1[0])
    # This is line_text_info_ver2 and to save connected text and its infomation of coordinates
    line_text_info = []
    # Add first text for line_text_info
    line_text_info.append(line_text_info_ver1[0])
    # Search matches in the same row
    for one_line in line_text_info_ver1[1:]:
      # Search from lines already found in STEP2
      # Basically, it is likely to be the same line as the last registered line.
      for one_line_text_info in reversed(line_text_info):
        # Whether it is within the height range.
        # Basically found word is connected after the registered text, so compare part of right top and right bottom
        if one_line["vertices"][1]["y"] > one_line_text_info["top_border"] and one_line["vertices"][2]["y"] < one_line_text_info["bottom_border"]:
          if one_line_text_info["vertices"][1]["x"] < one_line["vertices"][0]["x"]: # Connects after the registered text
            # Connect text
            one_line_text_info["text"] += " " + one_line["text"]
            update_coordinates(one_line_text_info, one_line,1) # Update right top coordinates
            update_coordinates(one_line_text_info, one_line,2) # Update right bottom coordinates
            break
          elif one_line_text_info["vertices"][0]["x"] > one_line["vertices"][1]["x"]: # Connects before the registered text
            # Connect text
            one_line_text_info["text"] = one_line["text"] + " " +one_line_text_info["text"]
            update_coordinates(one_line_text_info ,one_line,0) # Update left top coordinates
            update_coordinates(one_line_text_info ,one_line,3) # Update left bottom coordinates
            break
      else:
        # If don't find text in same line, register one_line
        add_height_border(one_line)
        line_text_info.append(one_line)
    # Sort by y coordinate because OCR is not arranged in the order of y coordinate (because it considers x coordinate)
    # Since the x coordinate is taken into account, if you sort before this timing, the number of joins on the left will increase.
    line_text_info = sorted(line_text_info, reverse=False, key=lambda x: x["vertices"][0]["y"])
    # Get only text 
    line_text = [x["text"] for x in line_text_info]
    return line_text
    
  def search_texts(self,line_text):
    """
    ## Discription
      This method extracts the purchase date, purchase store, item and item-related data such as price, amount etc... from line_text.
      If the date is not found, this method can't determine where item stert, so read all data from top to bottom.
      
    ## Args:
      `line_text (str[][])`: Include text line by line
      `status (str)`: Type is "first" or "secound". If the date is not found, this method is called again and the status argument is "secound"

    # Returns:
        # `_ (bool)`: Whether date is found. In first time it is called, if date is not found, it returns False and is called again to set the date to "sample" as a dummy.
    """
    # Whether line_text[] has price
    # line_text[] is included about item, discount,total price etc....
    # So some line_text[] is not for item. Then has_item_price is false.
    has_item_price = True
    # End reading line_text. If find "小計(subtotal)", the flag is True 
    isFinish = False
    
    # Search line_text to find item
    for text in line_text:
      # Use dictionary type for each line.
      item_info={"item": text,"registed_name": "---","genre": "---","price":-1,"amount":0,"discount":0}
      # Get purchase store, if it is not found yet
      if self.store == "":
        self.find_store(text)
      # Get purchase date, if it is not found yet
      if self.date=="":
        # Date type is yyyy/mm/dd
        result_date = re.search('(20[0-9]{2})(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|[1-9])',text)
        if result_date:
          self.date = str(dt.date(int(result_date.group(1)),int(result_date.group(3)),int(result_date.group(5))))
          # Delete item_list before date
          self.item_list.clear()
          continue

        # Date type is mm/dd/yyyy
        result_date = re.search('(日)([1-3][0-9]|[1-9])(月)(1[0-2]|0[1-9]|[1-9])(年)(20[0-9]{2})',text)
        if result_date:
          self.date = str(dt.date(int(result_date.group(6)),int(result_date.group(4)),int(result_date.group(2))))
          # Delete item_list before date
          self.item_list.clear()
          continue
      
      # Check text is keyword of starting point for its item
      # If keyword is ""(empty characters), keyword in text is always true, so keyword is necessary
      if self.store != "" and sDB.keyword[self.store] != "" and sDB.keyword[self.store] in text: # whether store keyword is included for text
        # Delete item_list before date
        self.item_list.clear()
        continue
      
      # Find total then finish search
      if "合計" in text:
        break

      # Sometime, discount exist after "小計"(subtotal)
      if isFinish: # After find "小計"(subtotal)
        # Find discount
        if "クーポン" in text:
          # get price
          result_discount= re.search('[0-9]+$',text)
          if result_discount:
            # Get discount price
            self.special_discount.append([text[:result_discount.start()-1],int(result_discount.group())])
      else: # Before find "小計"(subtotal)
        if "小計" in text: # quit to read item in receipt
          isFinish = True
          continue
        elif re.search('(割引|値引|クーポン)',text): # Find discount line
          if text[-1] == '%': # Last character is '%' then calcurate discount price from item price
            text=text[:-1] # Delete "%"
            price = re.search('[0-9]+$',text) # Get discount rate
            # Add discount to previous item. Calcurate discount price because price is discount rate
            if(price):
              self.item_list[-1]["discount"] = int(self.item_list[-1]["price"]*(1-(int(price.group())/100))) 
          else: # Last character is not "%"
            price = re.search('[0-9]+$',text) # Get discount price
            # Add discount to previous item
            if(price):
              self.item_list[-1]["discount"] = int(price.group())
        elif re.search('[0-9]+個',text): # text line is not discount and it is related quantity
          try:
            if has_item_price: # Previous line is related item and it was purchased multiple items
              ## 注意お店によって、計算式が違う
              ## 一列に(1つあたりの金額)*(個数)=(合計)がある場合のみ
              ## 1つの値段があって次の行に合計がある場合には不可
              # print(line_text)
              # print("===========")
              # print(self.item_list)
              # print("===========")
              # print(text)
              self.item_list[-1]["amount"]=re.search('([0-9]+)個',text).group()[:-1] # get quantity
              self.item_list[-1]["price"]=int((self.item_list[-1]["price"])/int(self.item_list[-1]["amount"])) # add price per one item
            else: # don't have item yet but find quantity
              print("can't find item",sys.stderr)
          except TypeError:
            print("TypeError in finding quantity",sys.stderr)
          except AttributeError:
            print("AttributeError in finding quantity",sys.stderr)
        else: # find item name
          item_info = self.findItem(text,item_info) # whether item is register for DB
          # if text == "", item_info is False
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

  # def combine(self,full_text):
  #   """ search each text in full_text. Get and Combine word. Return words by each line. 2nd argument is all text infomation in receipt. """
  #   def addNewLine(text):
  #     """ 1st argument is one line text infomation. """
  #     data_array=[] # store word info
  #     data_array.append(text.description) # stored one word
  #     data_array.append(text.bounding_poly.vertices[1].x) # get word position about x
  #     data_array.append(text.bounding_poly.vertices[1].y) # get word position about y
  #     data_array.append(text.bounding_poly.vertices[2].y) # get word position about y
  #     data_array.append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3) # save range that is need to combine other words
  #     # data_array.append(full_text.index(text)) # save index to sort
  #     return data_array

  #   lineInfo=[]
  #   for text in full_text:
  #     if lineInfo==[]: # first roop
  #       lineInfo.append(addNewLine(text)) # save for lineInfo array
  #     else: # secound time onwards roop 
  #       if(text.bounding_poly.vertices[0].y >lineInfo[-1][2]-lineInfo[-1][4] and text.bounding_poly.vertices[0].y <lineInfo[-1][3]+lineInfo[-1][4]):
  #         """ Whethrer this text is included preve word's range """
  #         if lineInfo[-1][1]<text.bounding_poly.vertices[1].x: # Whther position of this text is after prev word.
  #           lineInfo[-1][0]+=text.description # connect prev word and this word
  #         else:
  #           lineInfo[-1][0]=text.description+lineInfo[-1][0] # connect prev word and this word
  #         lineInfo[-1][2]=text.bounding_poly.vertices[1].y # update position y
  #       else:
  #         for line in reversed(lineInfo): # search word form last word
  #           if(text.bounding_poly.vertices[0].y >line[2]-line[4] and text.bounding_poly.vertices[0].y <line[3]+line[4]):
  #             """ Whethrer this text is included preve word's range """
  #             if line[1]<text.bounding_poly.vertices[1].x: # Whther position of this text is after prev word.
  #               line[0]+=text.description # connect prev word and this word
  #             else:
  #               line[0]=text.description+line[0] # connect prev word and this word
  #             line[2]=text.bounding_poly.vertices[1].y # update position y
  #             break
  #         else: # can't find some position word in lineInfo
  #           lineInfo.append(addNewLine(text)) # save for lineInfo array
  #   return lineInfo
  

  def getItemLine(self):
    return self.item_list
  def getDate(self):
    return self.date
  def getStore(self):
    return self.store

