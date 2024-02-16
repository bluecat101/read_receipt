import read_receipt as readre
import item_db as db
import tkinter as tk
import gui as ui
import record_receipt as recordre
from tkinter import filedialog

exec_type = "develop_reciept" # production,develop_receipt,develop_noreceipt

def main(filename):
  if exec_type == "develop_noreciept":
    Itemline=[
    ['つぶグミP濃厚ぶどう', '緑茶', '飲み物', 498, '2'],
    ['かつ丼･小', 'bb', 'aa', '200', 1],
    # ['揚げせん', 'item', 'cc', 90, '2'],
    # ['深蒸し緑茶', '緑茶', 'dd', 498, '2'],
    # ['クーポン嗜好品20%', 'ee', 'aa', '200', 1],
    # ['揚げせん', 'item', 'ff', 90, '2']
    ]
    date="2023/4/9"
    store="ダイエー"
    # specialDiscount =[["フルグラ",50],["割引",532]]
    specialDiscount = []
  elif exec_type == "develop_reciept":
    receiptInfo=readre.ReadReceipt(filename,exec_type)
    Itemline=receiptInfo.getItemLine()
    store=receiptInfo.getStore()
    date=receiptInfo.getDate()
    specialDiscount = receiptInfo.specialDiscount
  elif exec_type == "production":
    receiptInfo=readre.ReadReceipt(filename)
    Itemline=receiptInfo.getItemLine()
    store=receiptInfo.getStore()
    date=receiptInfo.getDate()
    specialDiscount = receiptInfo.specialDiscount
  # print(Itemline)
  gui=ui.ComfirmReciept(Itemline,date,store,specialDiscount)
  gui.mainloop()
  
  # if gui.isOk:
  recordOb=recordre.RecordReceipt(gui.getAllItem(),gui.newCategory)
  




if __name__ == "__main__":
  if "develop" in exec_type:
    main("develop")
  else:
    filename = filedialog.askopenfilename(
      title = "レシートを選択してください。",
      filetypes = [("Image file", ".png .jpg "),("PNG", ".png"), ("JPEG", ".jpg")], # ファイルフィルタ
      initialdir = "./" # 自分自身のディレクトリ
    )
    if filename != "":
      main(filename)
