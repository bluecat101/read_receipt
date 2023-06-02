# ウィンドウ立ち上げ
#--------------------------------
# Tkinterモジュールのインポート
# import tkinter
import tkinter as tk
from  tkinter import ttk
# import tkinter.ttk as ttk
# # ウィンドウ（フレーム）の作成
# root = tk.Tk()

# root.title("comfirm detail")
# # ウィンドウの大きさを設定
# root.geometry("400x400")
# class init():

class ComfirmReciept(tk.Frame):
  def __init__(self,parent=None):
    super().__init__(parent)

    parent.title("comfirm detail")
    parent.geometry("400x600")
    self.tableFrame=ttk.LabelFrame(parent)
    parent.columns=["商品","登録名","金額","数量","割引","合計"]# 合計000(-500)で割引金額表してもいいかも
    for i,column in enumerate(parent.columns): 
      columnLabel=ttk.Label(self.tableFrame,text=column)
      columnLabel.grid(row=0,column=i)
    ttk.Label(self.tableFrame).grid(row=0,column=6)
    items=[["fff",2,3,4,5,6],[1+1,2+1,3+1,4+1,5+1,6+1]]
    
    dairyProducts=["牛乳","卵","チーズ"]
    meat=["鶏","豚","牛","ししゃも"]
    snack=["クッキー","パイ","揚げせん","チョコ","アーモンド","ケーキ","フルグラ","コーンフレーク","ポテト"]
    staple=["パン","ブレッド","うどん","ご飯","パスタ"]
    drink=["珈琲","緑茶"]
    vegetable=["じゃがいも","レタス","水菜","舞茸","榎茸","小松菜","ほうれん草","野菜","ブロッコリー","人参","ピーマン","きゅうり"]
    processed_goods=["ちくわ","納豆","西京漬","厚揚げ","かに風","ウインナー"] 
    itemDb={"乳製品": dairyProducts,"肉類": meat,"お菓子": snack,"主食": staple,"飲み物":drink ,"野菜":vegetable ,"加工品":processed_goods}
    itemList=[]
    for primary_item_key,primary_item_value in itemDb.items():
      itemList+=["---"+primary_item_key+"---"]
      for item_name in primary_item_value:
        itemList+=[item_name]

    # styleNormal=ttk.Style()
    # self.styleError=ttk.Style()
    # style.configure(bd=-2)
    # styleNormal.theme_use('default')

    # styleNormal.configure("label.TEntry",foreground="blue")
    # self.styleError.configure("error",backgraound="red")
    for i,item in enumerate(items):
      # globals()["item"+str(i)]=tk.StringVar()
      productNameLabel=tk.Entry(self.tableFrame, width=len(str(item[0])),bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      productNameLabel.insert(0,item[0])
      productNameLabel.grid(row=i+1,column=0)
      # print(item0)
      itemLabel=ttk.Combobox(self.tableFrame,value=itemList,width=7)
      itemLabel.set(item[1])
      itemLabel.grid(row=i+1,column=1)

      priceLabel=tk.Entry(self.tableFrame,width=len(str(item[2])),bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      priceLabel.insert(0,item[2])
      priceLabel.grid(row=i+1,column=2)

      amountLabel=tk.Entry(self.tableFrame,width=len(str(item[3])),bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      amountLabel.insert(0,item[3])
      amountLabel.grid(row=i+1,column=3)

      discountLabel=tk.Entry(self.tableFrame,width=len(str(item[4])),bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      discountLabel.insert(0,item[4])
      discountLabel.grid(row=i+1,column=4)

      totalLabel=tk.Entry(self.tableFrame,width=len(str(item[5])),bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      totalLabel.insert(0,item[5])
      totalLabel.grid(row=i+1,column=5)
      
      deleteButton=ttk.Button(self.tableFrame,text="delete")
      deleteButton.bind("<ButtonPress>",self.delete)
      deleteButton.grid(row=i+1,column=6)

    self.tableFrame.pack(pady=10)
    # children = self.tableFrame.winfo_children()
    decideButton=ttk.Button(parent,text="決定",command=self.decide)
    decideButton.pack()

  def delete(self,event):
    elements=self.tableFrame.winfo_children()
    row=event.widget.grid_info()["row"]
    for i in range(7):
      elements[row*7+i].grid_remove()


  def decide(self):
    elements=self.tableFrame.winfo_children()
    for element in elements:
      if type(element) == ttk.Combobox:
        if "---" in element.get():
          element.configure(foreground="red")
        else:
          element.configure(foreground="white")
      elif type(element) == tk.Entry:
        if not(element.get().isdecimal()):
          element.configure(highlightbackground="red")
        else:
          element.configure(highlightbackground="#565656")


if __name__=="__main__":
  root = tk.Tk()
  app=ComfirmReciept(parent=root)
  app.mainloop()
    



# root.mainloop()