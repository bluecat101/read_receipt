import re
store_DB = ['ダイエー', 'ローゼン', 'イオン', 'FamilyMart', 'セブン-イレブン', '吉野家', 'まかいの牧場', 'EXCELSIOR CAFFE', '業務スーパー', 'KAMUKURA', 'LAWSON', '業務スーパー', '山安', '文左亭', 'LAWSON', 'KALDI', '世界一のアップルパイ', 'サービスエリア', 'NewDays', 'STARBUCKS', 'アトレ', 'クリエイト', ' くら寿司', 'お菓子のゆりかご', 'ダイソー', 'くら寿司', ' ロイヤル', 'マック', ' EXCELSIOR CAFFE', '博多劇場', 'オーエスドラッグ', 'サンドラック', 'すき家', 'かつや', '駐車場', 'ロイヤルホームセンタ', 'バーミヤン', 'HAC', 'QB', 'Enejet']
keyword = {'ダイエー': '', 'ローゼン': '', 'イオン': '', 'FamilyMart': '領収証', 'セブン-イレブン': '領収書', '吉野家': '', 'まかいの牧場': '', '業務スーパー': '', 'EXCELSIOR CAFFE': '', 'KAMUKURA': '', 'LAWSON': 'お客様控え', '山安': '', '文左亭': '', 'KALDI': '', '世界一のアップルパイ': '', 'サービスエリア': '', 'NewDays': '', 'STARBUCKS': 'TEL', 'アトレ': '', 'クリエイト': '', ' くら寿司': '', 'お菓子のゆりかご': '', 'ダイソー': '', 'くら寿司': '', 'サンドラック': '', 'すき家': '', 'かつや': '', '駐車場': '', 'ロイヤルホームセンター': '', 'バーミヤン': '', 'HAC': '', 'QB': '', 'Enejet': 'ENEOSカード'}
internal_tax = ['FamilyMart', 'EXCELSIOR CAFFE', 'LAWSON', 'Enejet']

def setting(store_name,text):
  if store_name == "":
    return text
  elif store_name == "ダイエー":
    return text
  elif store_name == "ローゼン":
    if len(text) >0:
      extra_char = re.match("\*?([A-Z]|[a-z]|[0-9])+",text)
      if not(extra_char):
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
      if extra_char:
        text = text[extra_char.end():]
      idx = text.find("¥")
      if idx != -1:
        return text[:idx] + text[idx+1:]
    return text
  else:
    return text

def tax(store_name):
  if store_name in internal_tax:
    return "内税"
  else:
    return "外税"