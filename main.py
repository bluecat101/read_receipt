import read_receipt as readre
import item_db as db
import tkinter as tk
import gui as ui
import record_receipt as recordre
from tkinter import filedialog

exec_type = "develop_noreceipt" # select type of execution： production,develop_receipt,develop_noreceipt

"""
# TODO
  - 内税か外税かを計算する
  - (specail discount を計算させる)
  - グラフを２ヶ月分横に表示したりする
  - グラフに対して目的、ジャンルを追加する。
  - 縦グラフにおいて色で分けて比率を比べられるようにする
"""
def main(image_name):
  """ 
  ## Discription
    Do reading receipt, comfirm got data, save it 
  
  ## Args:
    `image_name (str)`: Name of receipt image to use
  """

  if exec_type == "develop_noreceipt":
    # This exec_type is using test data and don't use receipt
    # Set test data
    TEST_DATA=[{'item': 'つぶグミP濃厚ぶどう', 'registered_name': '緑茶', 'category': '飲み物', 'price': 498, 'amount': 2, 'discount': 10},
              {'item': 'ブラックサンダー¥', 'registered_name': 'ブラックサンダー', 'category': 'お菓子', 'price': 38, 'amount': 1, 'discount': 0},
              {"item": "default","registered_name": "---","category": "---","price":-1,"amount":0,"discount":0}
              ]
    
    item_line = TEST_DATA
    date="2023/4/9"
    store="ダイエー"
    special_discount = [['クーポンブラックサンダー', 400]]
  elif exec_type == "develop_receipt":
    # this exec_type is use receipt data but don't read receipt and
    # set receipt data before exec this code.

    # Make ReadRecipt instance and read receipt
    receipt_info=readre.ReadReceipt(image_name,exec_type)
    # Get product details  line by line 
    item_line=receipt_info.item_list
    # Get store name from receipt
    store=receipt_info.store
    # Get Date from receipt
    date=receipt_info.date
    # Get special discount data from receipt because
    # special discout does not belong to any product
    special_discount = receipt_info.special_discount
  elif exec_type == "production":
    # this exec_type is for production.
    # read receipt image

    # Make ReadRecipt instance and read receipt
    receipt_info=readre.ReadReceipt(image_name)
    # Get product details  line by line 
    item_line=receipt_info.item_list
    # Get store name from receipt
    store=receipt_info.store
    # Get Date from receipt
    date=receipt_info.date
    # Get special discount data from receipt because
    # special discout does not belong to any product
    special_discount = receipt_info.special_discount
  # Make Gui object and display got data to comfirm whether tha data is correct
  for x in item_line: print(x)
  gui=ui.ComfirmReceipt(item_line,date,store,special_discount)
  # to diplay gui until user click "決定(dicision)"
  gui.mainloop()
  
  # Save receipt data to csv file
  record_db=recordre.RecordReceipt(gui.all_item,gui.new_category)
  



# Execute first when user execute "python main.py" to read and record receipt
if __name__ == "__main__":
  if "develop" in exec_type:
    # For test, call main method with file name develop
    main("develop")
  else:
    # Get file name that read receipt image file.
    image_name = filedialog.askopenfilename(
      title = "レシートを選択してください。",
      filetypes = [("Image file", ".png .jpg "),("PNG", ".png"), ("JPEG", ".jpg")], # ファイルフィルタ
      initialdir = "./" # 自分自身のディレクトリ
    )
    # Call main method to read receipt
    if image_name != "":
      main(image_name)
