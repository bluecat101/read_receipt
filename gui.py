import tkinter as tk
from  tkinter import ttk
import item_db as db
class ComfirmReciept(tk.Frame):
  root = tk.Tk()
  def __init__(self,items):
    super().__init__(self.root)
    # items=[["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1]]
    # app=ComfirmReciept(items,self.root=self.root)
    
    self.root.title("comfirm detail")
    self.root.geometry("800x1000")
    # print(self.root.winfo_height())
    # self.root.update_idletasks()
    # print(self.root.winfo_height())
    # self.tableFrame=tk.Canvas(self.root ,width=self.root.winfo_width()/2 ,height=50,scrollregion=(0,0,0,600))
    # canvas=tk.Canvas(self.root ,self.root.winfo_width() ,self.root.winfo_height())
    self.tableFrame=ttk.LabelFrame(self.root)
    # self.tableFrame.grid(row=0, column=0)

    # ybar = tk.Scrollbar(
    # self.root,  # 親ウィジェット
    # orient=tk.VERTICAL,  # バーの方向
    # )
    
    # # キャンバスの右に垂直方向のスクロールバーを配置
    # ybar.grid(
    #     row=0, column=1,  # キャンバスの右の位置を指定
    #     sticky=tk.N + tk.S  # 上下いっぱいに引き伸ばす
    # )
    
    # ybar.config(
    #     command=self.tableFrame.yview
    # )
    
    # self.tableFrame.config(
    #     yscrollcommand=ybar.set
    # )




    columns=["商品","登録名","カテゴリー","金額","数量","割引","合計"] # 合計000(-500)で割引金額表してもいいかも
    for i,column in enumerate(columns): 
      columnLabel=tk.Label(self.tableFrame,text=column,width=7,padx=3,anchor="center",bg="#3A3A3A")
      columnLabel.grid(row=0,column=i)
    ttk.Label(self.tableFrame).grid(row=0,column=7)
    
    self.itemList=[]
    for primary_item_key,primary_item_value in db.itemDB.items():
      self.itemList+=["---"+primary_item_key+"---"]
      for item_name in primary_item_value:
        self.itemList+=[item_name]

    for i,item in enumerate(items):
      hasDiscount= len(item)>5
      productNameLabel=tk.Entry(self.tableFrame, width=7,justify="center",bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      productNameLabel.insert(0,item[0])
      productNameLabel.grid(row=i+1,column=0)

      itemLabel=ttk.Combobox(self.tableFrame,value=self.itemList,width=7)
      itemLabel.set(item[1])
      itemLabel.grid(row=i+1,column=1)

      priceLabel=tk.Entry(self.tableFrame,width=7,justify="center",bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      priceLabel.insert(0,item[2])
      priceLabel.grid(row=i+1,column=2)

      amountLabel=tk.Entry(self.tableFrame,width=7,justify="center",bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      amountLabel.insert(0,item[3])
      amountLabel.grid(row=i+1,column=3)

      discountLabel=tk.Entry(self.tableFrame,width=7,justify="center",bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      discountLabel.insert(0,item[4])
      discountLabel.grid(row=i+1,column=4)

      totalLabel=tk.Entry(self.tableFrame,width=7,justify="center",bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      if hasDiscount:
        totalLabel.insert(0,item[5])
      else:
        totalLabel.insert(0,"---")
      totalLabel.grid(row=i+1,column=5)

      totalLabel=tk.Entry(self.tableFrame,width=7,justify="center",bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
      if hasDiscount:
        totalLabel.insert(0,int(item[3])*int(item[4])-int(item[5]))
      else:
        totalLabel.insert(0,int(item[3])*int(item[4]))
      totalLabel.grid(row=i+1,column=6)
      
      deleteButton=ttk.Button(self.tableFrame,text="delete")
      deleteButton.bind("<ButtonPress>",self.deleteItem)
      deleteButton.grid(row=i+1,column=7)

    self.tableFrame.pack(pady=10)
    
    decideButton=ttk.Button(self.root,text="決定",command=self.decideItem)
    decideButton.pack(pady=10)

    decideButton=ttk.Button(self.root,text="+",command=self.addItem)
    decideButton.pack(pady=10)

  def deleteItem(self,event):
    elements=self.tableFrame.winfo_children()
    row=event.widget.grid_info()["row"]
    for i in range(8):
      elements[row*8+i].grid_remove()

  def addItem(self):
    row=int(len(self.tableFrame.winfo_children())/8)-1

    productNameLabel=tk.Entry(self.tableFrame,width=7,bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
    productNameLabel.grid(row=row+1,column=0)

    itemLabel=ttk.Combobox(self.tableFrame,value=self.itemList,width=7)
    itemLabel.grid(row=row+1,column=1)

    priceLabel=tk.Entry(self.tableFrame,width=7,bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
    priceLabel.grid(row=row+1,column=2)

    amountLabel=tk.Entry(self.tableFrame,width=7,bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
    amountLabel.grid(row=row+1,column=3)

    discountLabel=tk.Entry(self.tableFrame,width=7,bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
    discountLabel.grid(row=row+1,column=4)

    totalLabel=tk.Entry(self.tableFrame,width=7,bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
    totalLabel.grid(row=row+1,column=5)

    totalLabel=tk.Entry(self.tableFrame,width=7,bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
    totalLabel.grid(row=row+1,column=6)

    
    deleteButton=ttk.Button(self.tableFrame,text="delete")
    deleteButton.bind("<ButtonPress>",self.deleteItem)
    deleteButton.grid(row=row+1,column=7)

  def decideItem(self):
    isOk=True
    elements=self.tableFrame.winfo_children()
    for i,element in enumerate(elements):
      if type(element) == ttk.Combobox:
        if "---" in element.get():
          isOk=False
          element.configure(foreground="red")
        else:
          element.configure(foreground="white")
      elif type(element) == tk.Entry:
        if ((i%8 >= 3 and not(element.get().isdecimal())) and (i%8 != 5)) or (("---" in element.get()) and (i%8 != 5)):
          isOk=False
          element.configure(highlightbackground="red")
        else:
          element.configure(highlightbackground="#565656")
    if isOk==True:
      print("submit")
      # for element in elements:
        # print(element.get())

# self.root = tk.Tk()
# if __name__=="__main__":
# #   self.root = tk.Tk()
#   items=[["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1]]
#   app=ComfirmReciept(items)
#   app.mainloop()
    



# self.root.mainloop()