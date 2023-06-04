import receipt
import item_db as db
import tkinter as tk
import gui


def main():
  receiptInfo=receipt.Receipt("ion_long.png")
  Itemline=receiptInfo.getItemLine()
  total=receiptInfo.getTotal()
  date=receiptInfo.getDate()
  for item in Itemline:
    print(item)
  print(total)
  print(date)
  # root = tk.Tk()
  # app=gui.ComfirmReciept(Itemline,parent=root)
  app=gui.ComfirmReciept(Itemline)
  app.mainloop()

if __name__ == "__main__":
  main()

