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

class ReadReceipt:
  def __init__(self,receiptName):
    self.kakasi = kakasi()
    self.path =os.path.abspath(receiptName) # set image path
    self.readReceipt()
    self.textsInfo # to save all content in receipt
  
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
    """ Disassemble content for each line. """
    del self.textsInfo[0]
    lineTexts = self.combine(self.textsInfo) # disassembe content for each line and save it for lineTexts
  
    self.sort(lineTexts) # sort from top to bottom because sometimes disassembling is mistake order.
    
    hasPrice=True
    self.itemList=[]
    self.totalInf=[]
    self.date=""
    self.store=""
    isFinish=False
    for text in lineTexts:
      if self.date=="": # until find date in receipt (store name must be exsisted above date)
        if self.store=="": # find store name 
          self.findStore(text[0])
        if re.search('20[0-9]{2}(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0]): 
          self.date=re.search('20[0-9]{2}(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0]).group() ## get self.date
      else: # After find self.date
        if re.match("小計",text[0]): # quit to read item in receipt
          isFinish = True
          # self.totalInf=["合計","金額",text]
        elif re.match("合計",text[0]): # get total price and exit roop
          self.totalInf = ["合計","金額",text]
          break
        elif re.search('[割引|値引]',text[0]) and not(isFinish): # find discount 
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
        break

  def findItem(self,text):
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
        else: # English or Other language
          itemTypeStatus=0

        while itemTypeStatus != 0:
          regular=re.escape(itemConvert)  # make regular expression object.
          if re.search(regular,text): # if itemConvert is included in text
            if re.match('[0-9]',text): # if first character is number
              price=re.match('[0-9]*',text) # get price from first character
              text=text[price.end():]+price.group() # change the order 
            try:
              itemInfo.append(text[:re.search("[0-9]+.?$",text).start()]) # append text from first to previous
            except:
              itemInfo.append(text)
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

