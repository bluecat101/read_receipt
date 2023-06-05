import copy as cp
import csv
import tkinter as tk
from  tkinter import ttk
import item_db as db
class ComfirmReciept(tk.Frame):
  root = tk.Tk()
  def __init__(self,items):
    super().__init__(self.root)
    
    self.root.title("comfirm detail")
    self.root.geometry("800x1000")
    self.root.update_idletasks()

    parentFrame=ttk.LabelFrame(self.root)
    parentFrame.pack(pady=0)

    columnHaedFrame=tk.Frame(parentFrame)
    columnHaedFrame.pack(pady=0)

    
    listFrame=tk.Frame(parentFrame)
    listFrame.pack(pady=1)

    self.canvas=tk.Canvas(listFrame,width=100,height=10,scrollregion=(0,0,0,0), bg='white')
    self.tableFrame=tk.Frame(self.canvas,bg="#3A3A3A",borderwidth=20,highlightbackground="red",relief="flat")
    self.canvas.create_window(0,0, window=self.tableFrame,anchor="nw")
    self.canvas.grid(row=0,column=0)

    ybar = tk.Scrollbar(
      listFrame,  # 親ウィジェット
      orient=tk.VERTICAL,  # バーの方向
    )
    
    # キャンバスの右に垂直方向のスクロールバーを配置
    ybar.grid(
      row=0, column=1,  # キャンバスの右の位置を指定
      sticky=tk.N + tk.S  # 上下いっぱいに引き伸ばす
    )
    
    ybar.config(
      command=self.canvas.yview,
      jump=1
    )
    
    self.canvas.config(
        yscrollcommand=ybar.set
    )
    
    columns=["商品","登録名","カテゴリー","金額","数量","割引","合計"] # 合計000(-500)で割引金額表してもいいかも
    for i,column in enumerate(columns): 
      if i == 1 or i == 2:
        columnLabel=tk.Label(columnHaedFrame,text=column)
        self.setStyle(columnLabel)
        columnLabel.configure(padx=5)
        columnLabel.grid(row=0,column=i,ipadx=6)
      elif i%2==1:
        columnLabel=tk.Label(columnHaedFrame,text=column)
        self.setStyle(columnLabel)
        columnLabel.configure(padx=1)
        columnLabel.grid(row=0,column=i)
      else:
        columnLabel=tk.Label(columnHaedFrame,text=column,width=7,padx=1,justify="center")
        columnLabel.grid(row=0,column=i)

    columnLabel=tk.Label(columnHaedFrame,width=8,padx=3,bg="#3A3A3A")
    columnLabel.grid(row=0,column=7,ipadx=17)

    self.itemList=[]
    for primary_item_key,primary_item_value in db.itemDB.items():
      self.itemList+=["---"+primary_item_key+"---"]
      for item_name in primary_item_value:
        self.itemList+=[item_name]

    for i,item in enumerate(items):
      hasDiscount= len(item)>5
      productNameEntry=tk.Entry(self.tableFrame)
      self.setStyle(productNameEntry)
      productNameEntry.insert(0,item[0])
      productNameEntry.grid(row=i+1,column=0)

      registerNameCombobox=ttk.Combobox(self.tableFrame)
      self.setStyle(registerNameCombobox)
      registerNameCombobox.set(item[1])
      registerNameCombobox.grid(row=i+1,column=1)

      categoryCombobox=ttk.Combobox(self.tableFrame)
      self.setStyle(categoryCombobox)
      categoryCombobox.set(item[2])
      categoryCombobox.grid(row=i+1,column=2)

      priceEntry=tk.Entry(self.tableFrame)
      self.setStyle(priceEntry)
      priceEntry.insert(0,item[3])
      priceEntry.grid(row=i+1,column=3)

      amountEntry=tk.Entry(self.tableFrame)
      self.setStyle(amountEntry)
      amountEntry.insert(0,item[4])
      amountEntry.grid(row=i+1,column=4)

      discountEntry=tk.Entry(self.tableFrame)
      self.setStyle(discountEntry)
      if hasDiscount:
        discountEntry.insert(0,item[5])
      else:
        discountEntry.insert(0,"---")
      discountEntry.grid(row=i+1,column=5)

      totalEntry=tk.Entry(self.tableFrame)
      self.setStyle(totalEntry)
      if hasDiscount:
        totalEntry.insert(0,int(item[3])*int(item[4])-int(item[5]))
      else:
        totalEntry.insert(0,int(item[3])*int(item[4]))
      totalEntry.grid(row=i+1,column=6)
      
      deleteButton=ttk.Button(self.tableFrame,text="delete",width=7)
      deleteButton.bind("<ButtonPress>",self.deleteItem)
      deleteButton.grid(row=i+1,column=7)

    parentFrame.update_idletasks()
    functionFrame=tk.Frame(self.root)
    functionFrame.propagate(False)
    functionFrame.configure(width=parentFrame.winfo_width(),height=30)
    functionFrame.pack()

    
    totalLabel=tk.Label(functionFrame,text="合計")
    totalLabel.place(relx=0.8)
    self.totalNumLabel=tk.Label(functionFrame,text=0)
    self.totalNumLabel.place(relx=0.9)

    decideButton=ttk.Button(functionFrame,text="決定",command=self.decideItem)
    decideButton.place(relx=0.35)

    decideButton=ttk.Button(functionFrame,text="+",command=self.addItem)
    decideButton.place(relx=0.5)


    self.updateRegion()
    self.root.config(width=self.tableFrame.winfo_width())
    self.calculate()
    
    self.root.bind_class("Entry", "<FocusOut>", self.calculateEvent)

  def calculateEvent(self,event):
    self.calculate()

  def calculate(self):
    elements=self.tableFrame.winfo_children()
    eachTotal=0
    total=0
    isInt=True
    for i,element in enumerate(elements):
      if i%8 == 3 or i%8 == 4:
        if not(element.get().isdecimal()):
          element.configure(highlightbackground="red")
          isInt=False
        else:
          element.configure(highlightbackground="#565656")
      elif i%8 == 5 and isInt:
        eachTotal=int(elements[i-2].get())*int(elements[i-1].get())
        if element.get().isdecimal():
          eachTotal-=int(element.get())
      elif i%8 == 6:
        if isInt:
          element.delete(0,tk.END)
          element.insert(0,eachTotal)
          total+=eachTotal
        eachTotal=0
        isInt=True
    self.totalNumLabel.configure(text=str(total)+"円")
          

  def updateRegion(self):
    self.tableFrame.update_idletasks() 
    canvas_height=500
    if canvas_height>self.tableFrame.winfo_height():
      canvas_height=self.tableFrame.winfo_height()
    self.canvas.config(width=self.tableFrame.winfo_width(), height=canvas_height,scrollregion=(0,0,0,self.tableFrame.winfo_height()))
    # """"""
    # self.calculate()

  def setStyle(self,widget):
    if type(widget) == tk.Entry:
      widget.configure(width=7,justify="center",bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
    elif type(widget) == ttk.Combobox:
      widget.configure(value=self.itemList,width=7)
    elif type(widget) == tk.Label:
      widget.configure(width=7,padx=2,justify="center")
      

  def deleteItem(self,event):
    elements=self.tableFrame.winfo_children()
    for i in range(8):
      elements[elements.index(event.widget)-i].destroy()
    self.updateRegion()

  def addItem(self):
    if self.tableFrame.winfo_children() != []:
      row=(self.tableFrame.winfo_children())[-1].grid_info()["row"] 
    else:
      row=0

    productNameEntry=tk.Entry(self.tableFrame)
    self.setStyle(productNameEntry)
    productNameEntry.grid(row=row+1,column=0)

    registerNameCombobox=ttk.Combobox(self.tableFrame)
    self.setStyle(registerNameCombobox)
    registerNameCombobox.grid(row=row+1,column=1)

    categoryCombobox=ttk.Combobox(self.tableFrame)
    self.setStyle(categoryCombobox)
    categoryCombobox.grid(row=row+1,column=2)

    priceEntry=tk.Entry(self.tableFrame)
    self.setStyle(priceEntry)
    priceEntry.grid(row=row+1,column=3)

    amountEntry=tk.Entry(self.tableFrame)
    self.setStyle(amountEntry)
    amountEntry.grid(row=row+1,column=4)

    discountEntry=tk.Entry(self.tableFrame)
    self.setStyle(discountEntry)
    discountEntry.grid(row=row+1,column=5)

    totalEntry=tk.Entry(self.tableFrame)
    self.setStyle(totalEntry)
    totalEntry.grid(row=row+1,column=6)

    deleteButton=ttk.Button(self.tableFrame,text="delete")
    deleteButton.bind("<ButtonPress>",self.deleteItem)
    deleteButton.grid(row=row+1,column=7)

    self.updateRegion()



  def decideItem(self):
    elements = self.tableFrame.winfo_children()
    isOk = (elements!=[])

    for i,element in enumerate(elements):
      if type(element) == ttk.Combobox:
        if "---" in element.get():
          isOk=False
          element.configure(foreground="red")
        else:
          element.configure(foreground="white")
      elif type(element) == tk.Entry:
        if i%8 < 3 and (("---" in element.get()) or element.get()==""):
          isOk=False
          element.configure(highlightbackground="red")
        elif i%8 >= 3 and not(element.get().isdecimal()) and i%8 != 5:
          isOk=False
          element.configure(highlightbackground="red")
        else:
          element.configure(highlightbackground="#565656")
    if isOk==True:
      path = 'output.csv'
      f = open(path, mode='a')
      oneLine=[]
      allItem=[]
      for i,element in enumerate(elements):
        if type(element) == tk.Entry or type(element) == ttk.Combobox:
          oneLine.append(element.get())
          if i%8==6:
            allItem.append(cp.copy(oneLine))
            oneLine.clear()
      for i,element in enumerate(elements):
          elements[i].destroy()
      writer = csv.writer(f)
      for lineItem in allItem:
        writer.writerow(lineItem)
      f.close()
      print("write for file")
      self.updateRegion()
      self.addItem()
      for element in self.tableFrame.winfo_children():
        element.destroy()


if __name__=="__main__":
#   self.root = tk.Tk()
  items=[["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1]
        #  ,["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1]
        #  ,["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1]
        #  ,["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1]
        #  ,["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1]
        #  ,["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1]
        #  ,["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1],["fff",2,3,4,5,6],[1+1,2+1,3+1,4,6+1]

         ]
  app=ComfirmReciept(items)
  app.mainloop()
    



# self.root.mainloop()        