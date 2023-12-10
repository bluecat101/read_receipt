import read_receipt as readre
import item_db as db
import tkinter as tk
import gui as ui
import record_receipt as recordre
from tkinter import filedialog


def main(filename):
  receiptInfo=readre.ReadReceipt(filename)
  Itemline=receiptInfo.getItemLine()
  store=receiptInfo.getStore()
  date=receiptInfo.getDate()
  
  gui=ui.ComfirmReciept(Itemline,date,store)
  gui.mainloop()
  
  if not(gui.getHasIssue()):
    recordOb=recordre.RecordReceipt(gui.getAllItem(),gui.getNewCategory(),gui.date,gui.store)
  


Itemline=[
['深蒸し緑茶', '緑茶', '飲み物', 498, '2'],
# ['クーポン嗜好品20%', 'bb', 'aa', '200', 1],
# ['揚げせん', 'item', 'cc', 90, '2'],
# ['深蒸し緑茶', '緑茶', 'dd', 498, '2'],
# ['クーポン嗜好品20%', 'ee', 'aa', '200', 1],
# ['揚げせん', 'item', 'ff', 90, '2']
]
date="2023/4/9"
store="ダイエーaaa"

if __name__ == "__main__":
  filename = filedialog.askopenfilename(
    title = "レシートを選択してください。",
    filetypes = [("Image file", ".png .jpg "),("PNG", ".png"), ("JPEG", ".jpg")], # ファイルフィルタ
    initialdir = "./" # 自分自身のディレクトリ
    )
  if filename != "":
    main(filename)

