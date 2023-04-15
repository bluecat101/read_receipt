import re
import regex
from pykakasi import kakasi
import mojimoji
# ----- #
s="2023/3/28"
result=re.search('20[0-9]{2}(/|年)(1[0-2]|[1-9])(/|月)([1-3][0-9]|[1-9])',s)
date=re.search('20[0-9]{2}(/|年)(1[0-2]|[1-9])(/|月)([1-3][0-9]|[1-9])',s).group() ## 日付の取得
# day_of_week=re.search('\((日|月|火|水|木|金|土)\)',s).group() ## 曜日の取得
print(date)
# ----- #

# # date=result.group()
# if result:
#   print("yes")
#   print(date)
#   print(day_of_week)
# else: 
#   print("no")

# # print(re.search("f",s))
# print(result)

# # {[0-9],4}{/|"年"}[0-12]{/|"月"}[0-31]


# # ----- #
# store_db={"FOOD STYLE": "イオン","ENEOS": "エネオス"}
# word="*EON FOOD STYLE"

# store_name="" ## お店の名前
# if store_name == "":
#   for store_key in store_db.keys(): ## 辞書内ループ
#     regular=re.escape(store_key)  ## 正規表現オブジェクト
#     if re.search(regular,word) :  
#       store_name=store_db[store_key] ## お店の名前を確定する
#       # print(store_name)
# # ----- #

## 漢字-> ひらがな -> カタカナ　-> 半角カタカナ


# ----- #日付の取得から小計までループ
"""dairy_products=["牛乳","卵","チーズ"]
meat=["鶏","豚","牛"]
snack=["チョコ","アーモンド","ケーキ"]

item_db={"乳製品": dairy_products,"肉類": meat,"お菓子": snack}
# オブジェクトをインスタンス化
kakasi = kakasi()

word="にわとり"
item_name="" ## 商品の名前
item_genre="" ## 商品のジャンル


if item_name == "":
  for k,item_value in item_db.items(): ## 辞書内ループ
    for item in item_value:
      item_convert=item
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
        if re.search(regular,word):
item_genre=k ## 商品のジャンルを確定する
          item_name=item ## 商品の名前を確定する
          item_status=1
        item_status-=1

        if item_status ==3:
          item_convert = kakasi.convert(item_convert)[0]['hira']
        elif item_status ==2:
          item_convert = kakasi.convert(item_convert)[0]['kana']
        elif item_status ==1:
          item_convert=mojimoji.zen_to_han(item_convert)

print(item_name,item_genre)"""
# ----- #
# new_item_db=[]
# if item_name=="":
#   new_item_db.append(word)

# ----- # 知らない商品の場合用


# matplotlib inline

""" # いらないかも opencvとtesseractによる画像認識の際のpriceを認識するコード
from PIL import Image 
import sys
import pyocr
import pyocr.builders
import cv2

img = cv2.imread('ion.jpg')

tools=pyocr.get_available_tools()
if len(tools)==0:
  print("error")
  sys.exit(1)

tool=tools[0]
langs=tool.get_available_languages()

txt=tool.image_to_string(Image.fromarray(img),lang=langs[1],builder=pyocr.builders.TextBuilder())
# print(txt)

date=2023
item_name=["フルグラ","たまご"]
item_amount=len(item_name)-1

item_count=0
match_count=0 # item_nameの要素との一致率を数える
confidence=0.0 # item_nameの要素との一致率
item_price_dic={} # 金額辞書
item_discount_dic={} # 割引辞書
one_line=""

start_posision=txt.find('\n\n',txt.find(str(date)))
if start_posision==-1:
  start_posision=txt.find(str(date))


for i,c in enumerate(txt):
  if i > start_posision and c=='\n': # 次の行を検索する
    match_count=0 # item_nameの要素との一致率を数える
    one_line=txt[i+1:txt.find('\n',i+1)] # 次の行を取得
    for j in item_name[item_count]: # item_nameの要素とどのくらい一致するかを調べる
      regular=re.escape(j)  ## 正規表現オブジェクト
      if re.search(regular,one_line):
        match_count+=1
    if confidence<0.5 and re.search("割引",one_line): # 割引があったら別で保存しておく
      if item_count>0:
        item_discount_dic[item_name[item_count-1]]=int(re.search("[0-9](?!.*([a-z]|%)).*$",one_line).group())
    confidence=match_count/len(item_name[item_count]) # item_nameの要素との一致率
    
    if confidence>0.5: # 一致率が0.5を超えていたら、一致している扱い
      item_price_str=re.search("[0-9](?!.*([a-z]|%)).*$",one_line).group() # 金額を取得(この際、※や.が含まれる)
      item_price=0
      for k in item_price_str: # item_price_strから数字のみを取得する
        if re.match("[0-9]",k):
          item_price=item_price*10+int(k)
      item_price_dic[item_name[item_count]]=item_price # 商品名と関連付けて金額を格納する
      item_count+=1
    print (confidence,item_count)
    if item_count>item_amount: # 全てのitemを数え終わったら終了。
      break
print(item_price_dic)
"""


# --- #
"""
傾きを考える
文字の左上のy座標-文字の右上のy座標

"""

# x_1=381
# y_1=401
# x_2=443
# y_2=404
# x_3=442
# y_3=417
# x_4=380
# y_4=414
# get_item=[["フルグラ","食品"],["卵","乳製品"]]
# # slope=1 # レシートが右肩上がりなら1,右下がりなら-1
# hight=2*(y_3-y_2)/3

# if (text_annotation.bounding_poly.vertices[0].x >y_1-hight or text_annotation.bounding_poly.vertices[0].x <y_1+hight) and re.search("[0-9](?!.*([a-z]|%)).*$",text_annotation.description):
#   item_price=int(text_annotation.description.replace(",","")) # 金額を取得(この際、,が含まれるのを消しています)
#   get_item[0].append(item_price)

# print(int(1/2))
# print(int(3/2))
# print(int(4/2))
# import sys
# def same_last_item(aaa):
#   import re
#   print("---------",sys.stderr)
#   print("---------",aaa)
# try:
#   same_last_item()
# except:
#   print("error")
# s="123ああ"
# # print(re.match('a',s).group())
# print(s)
# # result=re.match('(\D)',s[-1])
# # print(result)
# # t=s[0]+2
# if re.match('[0-9]',s):
#   price=re.match('[0-9]*',s)
#   # print(price.start)
#   # print(price.start())
#   s=s[price.end():]+price.group()
# print(s)

data=[0,2,1,34,2,1,574,3,5,7,3]
def sort(data):
  def find_pivot(data,left,right):
    return data[int((left+right)/2)]
  def quick_sort(data,left,right):
    if left>=right:
      # exit()
      return 0
    pivot=find_pivot(data,left,right)
    i=left
    j=right
    while(1):
      while(data[i]<pivot):
        i+=1
        # jikkou_i+=1
      while(data[j]>pivot):
        j-=1
        # jikkou_j-=1
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

print(data)
sort(data)
print(data)