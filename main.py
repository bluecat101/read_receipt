import read_receipt as readre
import item_db as db
import tkinter as tk
import gui as ui
import record_receipt as recordre


def main():
  receiptInfo=readre.ReadReceipt("ion_long.png")
  Itemline=receiptInfo.getItemLine()
  total=receiptInfo.getTotal()
  date=receiptInfo.getDate()
  for item in Itemline:
    print(item)
  print(total)
  print(date)
  # root = tk.Tk()
  # app=gui.ComfirmReciept(Itemline,parent=root)
  gui=ui.ComfirmReciept(Itemline)
  gui.mainloop()
  recordOb=recordre.RecordReceipt(gui.getAllItem())
  
  print("aaa")

if __name__ == "__main__":
  main()

