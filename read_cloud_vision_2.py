# class read:
import sys
import io
import os
import re


dairy_products=["牛乳","卵","チーズ"]
meat=["鶏","豚","牛","ししゃも"]
snack=["クッキー","パイ","揚げせん","チョコ","アーモンド","ケーキ","フルグラ","コーンフレーク","ポテト"]
staple=["パン","ブレッド","うどん","ご飯","パスタ"]
drink=["珈琲","緑茶"]
vegetable=["じゃがいも","レタス","水菜","舞茸","榎茸","小松菜","ほうれん草","野菜","ブロッコリー","人参","ピーマン","きゅうり"]
processed_goods=["ちくわ","納豆","西京漬","厚揚げ","かに風","ウインナー"] 
item_db={"乳製品": dairy_products,"肉類": meat,"お菓子": snack,"主食": staple,"飲み物":drink ,"野菜":vegetable ,"加工品":processed_goods}

def find_item(text):
  import re
  import regex
  from pykakasi import kakasi
  import mojimoji

  kakasi = kakasi()
  item_inf=[]

  # if item_name == "":
  for item_genre,item_value in item_db.items(): ## 辞書内ループ
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
        # print("item_status",item_status,"[]",item_convert)
        regular=re.escape(item_convert)  ## 正規表現オブジェクト
        if re.search(regular,text):
          ##データ加工
          if re.match('[0-9]',text):
            price=re.match('[0-9]*',text)
            text=text[price.end():]+price.group()
          # print(re.search("[0-9]+",text))
          # print(text)
          # print(re.search("[0-9]+",text).start())
          # exit(1)
          # if(re.search("[0-9]+",text).start())>0:
          item_inf.append(text[:re.search("[0-9]+",text).start()])
          item_inf.append(db_item)
          item_inf.append(item_genre)
          # item_genre=k ## 商品のジャンルを確定する
          # item_name=item ## 商品の名前を確定する
          break
          # item_status=1
        item_status-=1
        if item_status ==3:
          item_convert = kakasi.convert(item_convert)[0]['hira']
        elif item_status ==2:
          item_convert = kakasi.convert(item_convert)[0]['kana']
        elif item_status ==1:
          item_convert=mojimoji.zen_to_han(item_convert)
      if item_inf!=[]:
        break
    if item_inf!=[]:
        break
  if item_inf==[]:
    item_inf.append("can't find item")
    item_inf.append("can't find item_db")
    item_inf.append("can't find genre")

  return item_inf

# def same_last_item():
def same_last_item(item_list_last_name,line_texts,position):
  regular=re.escape(item_list_last_name)  ## 正規表現オブジェクト
  for i,text in enumerate(line_texts):
    if(i>position-3 and i<position and re.search(regular,text[0])): 
      return True
    elif i==position:
      return False
  return False
# 
# -----#
def combine(text,line_array):# 初めに一番後ろの値を確認する,違うなら最初から探す
  data_array=[]
  if line_array==[]:
    data_array.append(text.description)
    data_array.append(text.bounding_poly.vertices[1].y)
    data_array.append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3)
    data_array.append(texts.index(text))
    line_array.append(data_array)
  else:
    if(text.bounding_poly.vertices[0].y >line_array[-1][1]-line_array[-1][2] and text.bounding_poly.vertices[0].y <line_array[-1][1]+line_array[-1][2]):
      line_array[-1][0]+=text.description
    else:
      for line in reversed(line_array):
        if(text.bounding_poly.vertices[0].y >line[1]-line[2] and text.bounding_poly.vertices[0].y <line[1]+line[2]):
          line[0]+=text.description
          break
      else:
        data_array.append(text.description)
        data_array.append(text.bounding_poly.vertices[1].y)
        data_array.append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3)
        data_array.append(texts.index(text))
        line_array.append(data_array)
# -----#



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
  combine(text,line_texts)

for line in line_texts:
  print(line[0])

noitem=0
item_list=[]
total_inf=[]
error=[]
texts_only_num=[]
for text in line_texts:
  if date=="":
    if re.search('20[0-9]{2}(/|年)(1[0-2]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0]): 
      date=re.search('20[0-9]{2}(/|年)(1[0-2]|[1-9])(/|月)([1-3][0-9]|[1-9])',text[0]).group() ## 日付の取得
  else:
    if re.match("合計",text[0]):
      total_inf=["合計","金額",text]
    elif re.search('割引',text[0]):
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
    elif re.search('[0-9]個',text[0]):
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
    else:
      item_inf=find_item(text[0])
      if item_inf !=[]:
        if re.match('(\D)',text[0][-1]):
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
for item in item_list:
  if noitem==0 or item[0]!="can't find item":
    print(item)
    noitem=0
  if(item[0]=="can't find item"):
    noitem=1
  

"""
item_list=[]
total_inf=[]
texts_only_num=[]
for text in texts:
  if date=="":
    if re.search('20[0-9]{2}(/|年)(1[0-2]|[1-9])(/|月)([1-3][0-9]|[1-9])',text.description): 
      date=re.search('20[0-9]{2}(/|年)(1[0-2]|[1-9])(/|月)([1-3][0-9]|[1-9])',text.description).group() ## 日付の取得
  else:
    if re.search('([^0-9a-zA-Z]{2,})',text.description):
      if text.description == "合計":
        total_inf=["合計","金額",text.bounding_poly.vertices[1].y,(text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3]
      elif re.match('[割]',text.description):
        if len(item_list)>0:
          item_list[len(item_list)-1].append("割引")
          item_list[len(item_list)-1].append(text.bounding_poly.vertices[1].y)
          item_list[len(item_list)-1].append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3)
        else:
          print("missing reading") # error
      else:
        item_inf=find_item(text.description)
        if item_inf !=[]:
          item_inf.append("商品")
          item_inf.append(text.bounding_poly.vertices[1].y)
          item_inf.append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3)
          item_list.append(item_inf)
    if re.search("[0-9](?!.*([a-z])).*$",text.description):# 数字のみのリストを作る
      texts_only_num.append(text)

      # delete_index.append(texts.index(text))
      # print("delete",text.description,"index",texts.index(text))
  # elif date!="" and re.search('.',text.description):
# print("len",len(delete_index))
# for i in reversed(delete_index):
#   print("i",i)
#   del texts[i]
# for text in texts:
  
# del texts[:date_index]
# print("------------")
# print(texts_only_num)
# for text in texts_only_num:
#   print(text.description)
      # print("item_inf",item_inf)
    # print("texts.index(text)",texts.index(text))
  # print('\n"{}"'.format(text.description))
    # vertices = (['({},{})'.format(vertex.x, vertex.y)
    #             for vertex in text.bounding_poly.vertices])
    # print('bounds: {}'.format(','.join(vertices)))

# -----#
print(item_list)
# exit(1)
# item_list.append(total_inf)
for item_inf in item_list:
  item_inf.insert(0,len(item_inf)/3-1)
  
  for text in texts_only_num:
    if (text.bounding_poly.vertices[0].y >item_inf[5]-item_inf[6] and text.bounding_poly.vertices[0].y <item_inf[5]+item_inf[6]) and re.search("[0-9](?!.*([a-z])).*$",text.description):
      # print("----")
      # print(text)
      # print(item_list)
      # exit(1)
      if(item_inf[4]=="割引"):
        max_discount=text
        for i,discount in enumerate(texts_only_num):
          if i> texts_only_num.index(text) and max_discount.bounding_poly.vertices[1].x<discount.bounding_poly.vertices[1].x and(discount.bounding_poly.vertices[0].y >item_inf[5]-item_inf[6] and discount.bounding_poly.vertices[0].y <item_inf[5]+item_inf[6]) and re.search("[0-9](?!.*([a-z])).*$",discount.description):
            # print(i,discount)
            max_discount=discount
        # print(max_discount)
        # exit(1)
        text=max_discount
      print("----")
      print(text)
      # print(item_list)

      print(texts_only_num[texts_only_num.index(text)+1])
      # exit(1)
      # if(text.deescription=="割引" or text.deescription=="割"):
      # if (texts_only_num[texts_only_num.index(text)+1].bounding_poly.vertices[0].y >item_inf[3]-item_inf[4] and texts_only_num[texts_only_num.index(text)+1].bounding_poly.vertices[0].y <item_inf[3]+item_inf[4]) and re.match('%',texts_only_num[texts_only_num.index(text)+1].description):
        # print(text)
        # print(texts_only_num[texts_only_num.index(text)+1])
        # continue
        
        
        #文字列の追加（商品名：価格：割引）
        #　割引があったらfor文(現在値からで)でmax_xをゲットする。
        # 現在値からできないならif文で飛ばすかも(速度見る)
        
        
        #データを変更する必要がありそう
        # 一列で見るようにデータを変更する。
        #一番後ろが数字になるまで加工する
        #その後、一番後ろの値を取得する。->金額



      del item_inf[4:7]
      item_inf.append(re.sub(r"\D", "", text.description))
      item_inf[0]-=1
    if item_inf[0]==0:
      break
  del item_inf[0]

for i in item_list:
  print(i)
"""

"""
textsの中身は自在に操れる。
リストのように扱える。
以下のコードは全て予定通りに実行された。
print("-------")

print(texts[0])# OK
test=[]
for i,text in enumerate(texts):
  test.append(text)
print(test)
print(test[0].description)
for i,text in enumerate(texts):
  if i<50:
     del test[i] 

print("test",test)
"""
  