import read_receipt as readre
import item_db as db
import tkinter as tk
import gui as ui
import record_receipt as recordre


def main():
  # receiptInfo=readre.ReadReceipt("ion_long.png")
  # Itemline=receiptInfo.getItemLine()
  # total=receiptInfo.getTotal()
  # date=receiptInfo.getDate()
  # for item in Itemline:
  #   print(item)
  # print(total)
  # print(date)
  date="2023/4/9"
  store=""
  # gui=ui.ComfirmReciept(Itemline,receiptInfo.date,receiptInfo.store)
  gui=ui.ComfirmReciept(Itemline,date,store)
  gui.mainloop()
  # print(gui.getHasIssue())
  # print(gui.getAllItem())
  # print("-----")
  # print(gui.getNewCategory())
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
# for i,x in enumerate(Itemline):
#   x[2] = i
if __name__ == "__main__":
  main()

