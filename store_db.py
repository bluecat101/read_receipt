import re
storeDB = ['ダイエー', 'ローゼン', 'イオン', 'FamilyMart', 'セブン-イレブン', '吉野家', 'まかいの牧場', 'EXCELSIOR CAFFE', '業務スーパー', 'KAMUKURA', 'LAWSON', 'EXCELSIOR CAFFEEXCELSIOR CAFFE', '業務スーパー', '山安', '文左亭', 'LAWSON', 'KALDI', '世界一のアップルパイ', 'サービスエリア', 'NewDays', 'STARBUCKS', 'アトレ', 'クリエイト', ' くら寿司', 'お菓子のゆりかご', 'ダイソー', 'くら寿司', ' ロイヤル', 'マック', ' EXCELSIOR CAFFE', '博多劇場', 'オーエスドラッグ', 'サンドラック', 'すき家']
target = {'ダイエー': '', 'ローゼン': '', 'イオン': '', 'FamilyMart': '領収証', 'セブン-イレブン': '領収書', '吉野家': '', 'まかいの牧場': '', '業務スーパー': '', 'EXCELSIOR CAFFE': '', 'KAMUKURA': '', 'LAWSON': 'お客様控え', 'EXCELSIOR CAFFEEXCELSIOR CAFFE': '', '山安': '', '文左亭': '', 'KALDI': '', '世界一のアップルパイ': '', 'サービスエリア': '', 'NewDays': '', 'STARBUCKS': '', 'アトレ': '', 'クリエイト': '', ' くら寿司': '', 'お菓子のゆりかご': '', 'ダイソー': '', 'くら寿司': '', 'サンドラック': '', 'すき家': ''}

def setting(store_name,text):
  if store_name == "":
    return text
  elif store_name == "ダイエー":
    return text
  elif store_name == "ローゼン":
    if len(text) >0:
      extra_char = re.match("\*?([A-Z]|[a-z]|[0-9])+",text)
      if not(extra_char):
        print("NO char")
        return text
      text = text[extra_char.end():]
      idx = text.find("¥")
      if idx != -1:
        return text[:idx] + text[idx+1:]
    return text
  elif store_name == "イオン":
    return text
  elif store_name == "FamilyMart":
    if len(text) >0:
      idx = text.find("¥")
      if idx != -1:
        return text[:idx] + text[idx+1:]
    return text
  elif store_name == "セブン-イレブン":
    if len(text) >0:
      idx = text.find("*")
      if idx != -1:
        return text[:idx] + text[idx+1:]
    return text
  elif store_name == "業務スーパー":
    if len(text) >0:
      extra_char = re.search(".?([A-Z]|[a-z]|[0-9])+",text)
      # print(text,extra_char)
      if extra_char:
        text = text[extra_char.end():]
      idx = text.find("¥")
      if idx != -1:
        return text[:idx] + text[idx+1:]
    return text
  else:
    return text

def tax(store_name):
  include_tax = ["FamilyMart","EXCELSIOR CAFFE","LAWSON"]
  exclude_tax = ["","ダイエー","ローゼン","イオン","セブン-イレブン",]
  if store_name in include_tax:
    return "内税"
  else:
    return "外税"