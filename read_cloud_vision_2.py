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
  return item_inf
# -----#



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
# print('Texts:')
date=""
if texts==[]:
  print("ERROR can not read")
  exit(1)

del texts[0]
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
      item_inf=find_item(text.description)
      if item_inf !=[]:
        item_inf.append(text.bounding_poly.vertices[1].y)
        item_inf.append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3)
        item_list.append(item_inf)
    elif re.match('[割]',text.description):
      if len(item_list)>0:
        item_list[len(item_list)-1].append(text.bounding_poly.vertices[1].y)
        item_list[len(item_list)-1].append((text.bounding_poly.vertices[2].y-text.bounding_poly.vertices[1].y)*2/3)
      else:
        print("missing reading") # error
    if re.search("[0-9](?!.*([a-z]|%)).*$",text.description):# 金額を取得(この際、※や.が含まれる)
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

item_list.append(total_inf)
for item_inf in item_list:
  item_inf.insert(0,len(item_inf)/2-1)
  for text in texts_only_num:
    if (text.bounding_poly.vertices[0].y >item_inf[3]-item_inf[4] and text.bounding_poly.vertices[0].y <item_inf[3]+item_inf[4]) and re.search("[0-9](?!.*([a-z]|%)).*$",text.description):
      del item_inf[3:5]
      item_inf.append(re.sub(r"\D", "", text.description))
      item_inf[0]-=1
    if item_inf[0]==0:
      break
  del item_inf[0]
print(item_list)


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
