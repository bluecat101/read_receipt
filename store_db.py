storeDB = ['ダイエー', 'ローゼン', 'イオン', 'FamilyMart',"セブン-イレブン"]
target ={'ダイエー':"", 'ローゼン':"", 'イオン':"", 'FamilyMart':"領収証","セブン-イレブン":"領収書"}

def setting(store_name,text):
  if store_name == "":
    return text
  elif store_name == "ダイエー":
    return text
  elif store_name == "ローゼン":
    return text
  elif store_name == "イオン":
    return text
  elif store_name == "FamilyMart":
    if len(text) >0:
      idx = text.find("¥")
      if idx != -1:
        return text[:idx] + text[idx+1:]
    return text
  else:
    return text

def tax(store_name):
  include_tax = ["FamilyMart"]
  exclude_tax = ["","ダイエー","ローゼン","イオン","セブン-イレブン"]
  if store_name in include_tax:
    return "内税"
  else:
    return "外税"