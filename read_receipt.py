################################################
# ------------------ README ------------------ #
# do character recognition with Google Coloud  #
# read receipt and analyse                     #
# get name, category, price, descount and quantity#
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
        'registered_name': general item name(str),
        'category': category(str),
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
      recognition_result = self.do_OCR(image_path)
    # Analyse receipt to get item, purchase store etc...
    line_text = self.analyse(exec_type,recognition_result)
    self.search_texts(line_text)
    # print store name read by OCR
    if self.store == "":
      print(line_text[:3])
  
  def do_OCR(self,image_path):
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
      line_text =['/EONFOODSTYLE', 'イオンフードスタイル港南台店', 'TEL045-832-1361', '領収証', '株式会社ダイエー', '登録番号T4140001005666', 'レジ0599 2024/4/20(土)15:52', '取8147青:180310599登:003787845', 'İAEON会員:********68499401', '肝挽肉 277J', '割引 20% -56', '会員様割引5% -12', '豚挽肉 445', '割引 20% -89', '会員様割引 5% -18', '大ばちまぐろ 525', '会員様割引5% -27', '生アトランティッ 645*', '割引 20% -129', '会員様割引5% -26', 'BP豆腐 156X', '(2個X単78)', '会員様割引5% -8', '餃子の皮 380', '(2個X単190)', '会員様割引5% -20', 'もやし 65J', '会員様割引5% -4', 'タマネギ 280*', '会員様割引5% -14', 'じゃが芋 280', '会員様割引5% -14', '洛市壬生菜 70', '会員様割引5% -4', 'ガーナブラックEX 200', '会員様割引5% -10', '焼えび風味スティック 196', '(2個X単98)']
      return line_text
    # First element in recognition_result is full text. Use this text to judge whether each text is same line or not.
    # First element is to use '\n'(new line code) so split with '\n' and return type of array
    full_text = recognition_result[0].description.split('\n')
    # delete first element 
    del recognition_result[0]
    # To save connected text and its infomation of coordinates.
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
      # Get first index found. If using re.search(), when "(" is search word you must escape.
      # If using removeprefix, it will not work when a space is present
      index = full_text[pointer_for_full_text].index(word.description)
      full_text[pointer_for_full_text] = full_text[pointer_for_full_text][:index]+full_text[pointer_for_full_text][index+len(word.description):]

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
    # Get only text and delete "," as it gets in the way when searching for the amount.
    line_text = [x["text"].replace(",","") for x in line_text_info]
    return line_text
    
  def search_texts(self,line_text):
    """
    ## Discription
      This method extracts the purchase date, purchase store, item and item-related data such as price, amount etc... from line_text.
      If the date is not found, this method can't determine where item stert, so read all data from top to bottom.
      
    ## Args:
      `line_text (str[])`: Include text line by line
      `status (str)`: Type is "first" or "secound". If the date is not found, this method is called again and the status argument is "secound"

    # Returns:
        # `_ (bool)`: Whether date is found. In first time it is called, if date is not found, it returns False and is called again to set the date to "sample" as a dummy.
    """

    # End reading line_text. If find "小計(subtotal)", the flag is True 
    isFinish = False
    
    # Search line_text to find item
    for text in line_text:
      # Use dictionary type for each line.
      item_info={"item": text,"registered_name": "---","category": "---","price":-1,"amount":0,"discount":0}
      # Get purchase store, if it is not found yet
      if self.store == "":
        self.find_store(text)
      # Get purchase date, if it is not found yet
      if self.date=="":
        # Date type is yyyy/mm/dd, yyyy年mm月dd
        searched_date = re.search('(20[0-9]{2})(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|0[1-9]|[1-9])',text)
        if searched_date:
          self.date = str(dt.date(int(searched_date.group(1)),int(searched_date.group(3)),int(searched_date.group(5))))
          # Delete item_list before date
          self.item_list.clear()
          continue

        # Date type is mm/dd/yyyy, 日mm月dd年yyyy
        searched_date = re.search('(日)([1-3][0-9]|0[1-9]|[1-9])(月)(1[0-2]|0[1-9]|[1-9])(年)(20[0-9]{2})',text)
        if searched_date:
          self.date = str(dt.date(int(searched_date.group(6)),int(searched_date.group(4)),int(searched_date.group(2))))
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
      if re.search("合計|(合[ ]*計)",text):
        break
      # Sometime, discount exist after "小計"(subtotal)
      if isFinish: # After find "小計"(subtotal)
        # Find discount
        if "クーポン" in text:
          # Get price
          searched_discount= re.search('[0-9]+$',text)
          if searched_discount: # Get discount price
            self.special_discount.append([text[:searched_discount.start()-1],int(searched_discount.group())])
      else: # Before find "小計"(subtotal)
        if re.search("小計|(小[ ]*計)",text): # quit to read item in receipt
          isFinish = True
          continue
        elif re.search('(割引|値引|クーポン)',text): # Find discount line
          if text[-1] == '%': # Last character is '%' then calcurate discount price from item price
            text=text[:-1] # Delete "%"
            searched_price = re.search('[0-9]+$',text) # Get discount rate
            # Add discount to previous item. Calcurate discount price because price is discount rate
            if searched_price and len(self.item_list) > 0:
              self.item_list[-1]["discount"] += int(self.item_list[-1]["price"]*(1-(int(searched_price.group())/100))) 
          else: # Last character is not "%"
            searched_price = re.search('[0-9]+$',text) # Get discount price
            # Add discount to previous item
            if searched_price and len(self.item_list) > 0:
              self.item_list[-1]["discount"] += int(searched_price.group())
        elif re.search('[0-9]+個',text): # Text line is not related discount but it is related quantity
          if len(self.item_list) != 0: # Previous line exist
            # Get quantity and set to previous line
            self.item_list[-1]["amount"] = re.search('([0-9]+)個',text).group()[:-1] 
            # Set price when item is found but price is not found
            if self.item_list[-1]["price"] == -1: 
              searched_price = re.search("([0-9]+)(?!.*g$)?$",text)
              if searched_price:
                self.item_list[-1]["price"] += int(searched_price.group(1))
            # Update price per one item
            self.item_list[-1]["price"] = int((self.item_list[-1]["price"])/int(self.item_list[-1]["amount"])) 
        elif(text != ""): # Other type may be item, so record the line
          # Whether item is registed for DB and store data for item_info
          if self.find_item(text,item_info):
            self.item_list.append(item_info)

  def find_store(self,text):
    """
    ## Discription
      Search for purchase locations registered in store DB from text and store to self.store
      
    ## Args:
      `text (str)`: each line text
    
    ## Returns:
      `bool` : text is "" or having any character
    """
    for storeName in sDB.store_DB: 
      if storeName in text: # whether store name is included for text
        self.store=storeName

  def find_item(self,text,item_info):
    """
    ## Description:
      Search for registered item in item_db.
      item in item_db is registered as Hiragara or Katakana but some receipts are written differently, so search while converting registered item names to other notation methods
    ## Args:
        text (str): For searching line text
        item_info (dict): To store searched data
    """
    # Change data by each store
    # Some receipt has characteristics such as having extra characters then delete it
    text = sDB.setting(self.store,text)
    # Don't add row when character is empty after changing the text for each store
    if text == "":
      return False
    item_info["item"] = text # Store processed text
    kks = kakasi() # Make instance to convert for HIragana and Katakana
    # Get boarder line between item and price
    searched_price = re.search("([0-9]+)(?!.*g$).?$",text)
    # Devide item and searched_price
    if searched_price:
      text = text[:searched_price.start()]
      item_info["item"] = text
      item_info["price"] = int(searched_price.group(1))
      # Leave it at one for now.
      item_info["amount"] = 1

    # Find item name from DataBase
    # Get item from DataBase and search by changing the notation method
    for item_genre,item_value in iDB.item_DB.items(): # Roop from DB
      for db_item in item_value: # Roop in each item name
        item_convert=db_item # Get DB item name to change Kanji, Hiragana, Katakana and Half Katakana.
        # Check type of item name in DB whether Kanji, Hiragana, Katakana and Half Katakana and change status.
        if re.match('^\p{Script=Han}+$', item_convert): # Kanji
          itemTypeStatus = 4
        elif re.match('[あ-ん]+', item_convert): # Hiragana
          itemTypeStatus = 3
        elif re.match('[ア-ン]+', item_convert): # Katakana
          itemTypeStatus = 2
        elif re.match('[ｱ-ﾝ]+', item_convert): # Half Katakana
          itemTypeStatus = 1
        else: # English, Other language or combination of tow character type
          itemTypeStatus=0
        while itemTypeStatus != -1:
          regular=re.escape(item_convert)  # Make regular expression object.
          if any(map(lambda key: text in key, list(iDB.special_name.keys()))): # Find text in special name
            # Find which matches
            # Save time by first using any instead of for statement
            for key in iDB.special_name.keys():
              if text in key:
                # Get registered_name and category
                registered_name = iDB.special_name[key][0]
                category = iDB.special_name[key][1]
                item_info["registered_name"] = registered_name
                item_info["category"] = category
                return True
          elif(re.search(regular,text)): # Find text
            # Get registered_name and category
            registered_name = db_item
            category = item_genre
            item_info["registered_name"] = registered_name
            item_info["category"] = category
            return True
          else:
            # Change type of the notation method
            itemTypeStatus -= 1
            if itemTypeStatus ==3:
              item_convert = kks.convert(item_convert)[0]['hira'] # Change type of word for Hiragana
            elif itemTypeStatus ==2:
              item_convert = kks.convert(item_convert)[0]['kana'] # Change type of word for Katakana
            elif itemTypeStatus ==1:
              item_convert=mojimoji.zen_to_han(item_convert) # Change type of word for Half Katakana
    return True