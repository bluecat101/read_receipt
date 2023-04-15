import sys
import io
import os
import re
import re
import regex
from pykakasi import kakasi
import mojimoji
# dairy_products=["牛乳","卵","チーズ"]
# meat=["鶏","豚","牛","ししゃも"]
# snack=["クッキー","パイ","揚げせん","チョコ","アーモンド","ケーキ","フルグラ","コーンフレーク","ポテト"]
# staple=["パン","ブレッド","うどん","ご飯","パスタ"]
# drink=["珈琲","緑茶"]
# vegetable=["じゃがいも","レタス","水菜","舞茸","榎茸","小松菜","ほうれん草","野菜","ブロッコリー","人参","ピーマン","きゅうり"]
# processed_goods=["ちくわ","納豆","西京漬","厚揚げ","かに風","ウインナー"] 
# item_db={"乳製品": dairy_products,"肉類": meat,"お菓子": snack,"主食": staple,"飲み物":drink ,"野菜":vegetable ,"加工品":processed_goods}

class Read:
  # def __init__(self):
  dairy_products=["牛乳","卵","チーズ"]
  meat=["鶏","豚","牛","ししゃも"]
  snack=["クッキー","パイ","揚げせん","チョコ","アーモンド","ケーキ","フルグラ","コーンフレーク","ポテト"]
  staple=["パン","ブレッド","うどん","ご飯","パスタ"]
  drink=["珈琲","緑茶"]
  vegetable=["じゃがいも","レタス","水菜","舞茸","榎茸","小松菜","ほうれん草","野菜","ブロッコリー","人参","ピーマン","きゅうり"]
  processed_goods=["ちくわ","納豆","西京漬","厚揚げ","かに風","ウインナー"] 
  item_db={"乳製品": dairy_products,"肉類": meat,"お菓子": snack,"主食": staple,"飲み物":drink ,"野菜":vegetable ,"加工品":processed_goods}

  def find_item(self,text):
    item_inf=[]
    self.kakasi = kakasi()
    # if item_name == "":
    for item_genre,item_value in Read.item_db.items(): ## 辞書内ループ
      for db_item in item_value:
        item_convert=db_item
        if regex.match('^\p{Script=Han}+$', item_convert):
          item_status=4
        elif re.match('[あ-ん]+', item_convert):
          item_status=3
        elif re.match('[ア-ン]+', item_convert):
          item_status=2
        elif re.match('[ｱ-ﾝ]+', item_convert):
          item_status=1
        else:
          item_status=0
        while item_status != 0:
          regular=re.escape(item_convert)  ## 正規表現オブジェクト
          if re.search(regular,text):
            ##データ加工
            if re.match('[0-9]',text):
              price=re.match('[0-9]*',text)
              text=text[price.end():]+price.group()
            try:
              item_inf.append(text[:re.search("[0-9]+.?$",text).start()])
            except:
              item_inf.append(text)
            # item_inf.append(text[:re.search("[0-9]+.?$",text).start()])
            item_inf.append(db_item)
            item_inf.append(item_genre)
            break
          item_status-=1
          if item_status ==3:
            item_convert = self.kakasi.convert(item_convert)[0]['hira']
          elif item_status ==2:
            item_convert = self.kakasi.convert(item_convert)[0]['kana']
          elif item_status ==1:
            item_convert=mojimoji.zen_to_han(item_convert)
        if item_inf!=[]:
          break
      if item_inf!=[]:
          break
    else:
      # item_inf.append(text[:re.search("[0-9]+",text).start()])
      try:
        item_inf.append(text[:re.search("[0-9]+.?$",text).start()])
      except:
        item_inf.append(text)
      item_inf.append("can't find item_db")
      item_inf.append("can't find genre")
    return item_inf

  def same_last_item(item_list_last_name,line_texts,position):
    regular=re.escape(item_list_last_name)  ## 正規表現オブジェクト
    for i,text in enumerate(line_texts):
      if(i>position-3 and i<position and re.search(regular,text[0])): 
        return True
      elif i==position:
        return False
    return False

  # def insert(self,):


  def combine(self,text,line_array):# 初めに一番後ろの値を確認する,違うなら最初から探す
    data_array=[]
    if line_array==[]:
      data_array.append(text.description)
      data_array.append(text.bounding_poly.vertices[1].x)
      data_array.append(text.bounding_poly.vertices[1].y)
      data_array.append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3)
      data_array.append(texts.index(text))
      line_array.append(data_array)
    else:
      if(text.bounding_poly.vertices[0].y >line_array[-1][2]-line_array[-1][3] and text.bounding_poly.vertices[0].y <line_array[-1][2]+line_array[-1][3]):
        if line_array[-1][1]<text.bounding_poly.vertices[1].x:
          line_array[-1][0]+=text.description
        else:
          line_array[-1][0]=text.description+line_array[-1][0]
        line_array[-1][2]=text.bounding_poly.vertices[1].y

      else:
        for line in reversed(line_array):
          if(text.bounding_poly.vertices[0].y >line[2]-line[3] and text.bounding_poly.vertices[0].y <line[2]+line[3]):
            if line[1]<text.bounding_poly.vertices[1].x:
              # line_array[-1][0]+=text.description
              line[0]+=text.description
            else:
              # line_array[-1][0]=text.description+line_array[-1][0]
              line[0]=text.description+line[0]
            # line_array[-1][2]=text.bounding_poly.vertices[2].y
            line[2]=text.bounding_poly.vertices[1].y
            break
        else:
          data_array.append(text.description)
          data_array.append(text.bounding_poly.vertices[1].x)
          data_array.append(text.bounding_poly.vertices[1].y)
          data_array.append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3)
          data_array.append(texts.index(text))
          line_array.append(data_array)
  # -----#

  def sort(self,data):
    def find_pivot(data,left,right):
      return data[int((left+right)/2)]
    def quick_sort(data,left,right):
      if left>=right:
        return 0
      pivot=find_pivot(data,left,right)
      i=left
      j=right
      while(1):
        while(data[i][2]<pivot[2]):
          i+=1
        while(data[j][2]>pivot[2]):
          j-=1
        if i>=j:
          break
        tmp=data[i]
        data[i]=data[j]
        data[j]=tmp
        i+=1
        j-=1
      quick_sort(data,left,i-1)
      quick_sort(data,j+1,right)
      return 0
    quick_sort(data,0,len(data)-1)

read=Read()
# path =os.path.abspath('sebun.jpg') 
path =os.path.abspath('ion_long.png') 
"""Detects text in the file."""
from google.cloud import vision
import io
client = vision.ImageAnnotatorClient()
with io.open(path, 'rb') as image_file:
    content = image_file.read()
image = vision.Image(content=content)
response = client.text_detection(image=image)
texts = response.text_annotations
print(texts)
date=""
if texts==[]:
  print("ERROR can not read")
  exit(1)
print("----")
del texts[0]
line_texts=[]
for text in texts:
  read.combine(text,line_texts)
#   print(line_texts)
# exit(1)

read.sort(line_texts)
for line in line_texts:
  print(line[0])




noitem=0
item_list=[]
total_inf=[]
error=[]
texts_only_num=[]
finish_flag=0
for text in line_texts:
  if date=="":
    if re.search('20[0-9]{2}(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0]): 
      date=re.search('20[0-9]{2}(/|年)(1[0-2]|0[1-9]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0]).group() ## 日付の取得
  else:
    if re.match("小計",text[0]):
      finish_flag=1
      # total_inf=["合計","金額",text]
    elif re.match("合計",text[0]):
      total_inf=["合計","金額",text]
      break
    elif re.search('割引',text[0])and finish_flag==0:
      if re.match('%',text[0][-1]):
        text[0]=text[0][:-1]
        price= re.search('[0-9]+$',text[0])
        try:
          item_list[len(item_list)-1].append(int(item_list[len(item_list)-1][-1])*(1-(int(price.group())/100))) 
        except TypeError:
          item_list[len(item_list)-1].append("can't calcurlate discount")
        except AttributeError:
          item_list[len(item_list)-1].append("can't find discount")
      else:
        price= re.search('[0-9]+$',text[0])
        item_list[len(item_list)-1].append(price.group()) if price else item_inf.append("can't find discount")
    elif re.search('[0-9]個',text[0])and finish_flag==0:
      try:
        if noitem==0:
          item_list[len(item_list)-1][4]=re.search('([0-9]+)個',text[0]).group()[:-1]
          item_list[len(item_list)-1][3]=int(int(item_list[len(item_list)-1][3])/int(item_list[len(item_list)-1][4]))
        else:
          error_inf=[]
          error_inf.append(item_list[len(item_list)-1][0])
          error_inf.append("個数")
          error.append(error_inf)
          print("error",sys.stderr)
      except TypeError:
        error_inf=[]
        error_inf.append(item_list[len(item_list)-1][0])
        error_inf.append("個数")
        error.append(error_inf)
        print("error",sys.stderr)
      except AttributeError:
        error_inf=[]
        error_inf.append(item_list[len(item_list)-1][0])
        error_inf.append("個数")
        error.append(error_inf)
        print("error",sys.stderr)
    elif finish_flag==0:
      item_inf=read.find_item(text[0])
      if item_inf !=[]:
        while re.match('(\D)',text[0][-1]):
          text[0]=text[0][:-1]
        try:
          item_inf.append(re.search('[0-9]+$',text[0]).group())
          item_inf.append(1)
          noitem=0
        except AttributeError:
          item_inf.append("can't find price")
          item_inf.append(0)
          noitem=1
        item_list.append(item_inf)
noitem=0

# for item in item_list:
#   if noitem==0 or item[0]!="can't find item":
#     print(item)
#     noitem=0
#   if(item[0]=="can't find item"):
#     noitem=1

for item in item_list:
  print(item)
print(total_inf)
print(date)