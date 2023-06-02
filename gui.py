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

    styleNormal=ttk.Style()
    self.styleError=ttk.Style()
    # styleNormal.theme_use('default')

    styleNormal.configure("label.TEntry",foreground="blue")
    self.styleError.configure("error",backgraound="red")
        #     element.bd=3
        # element.relief="solid"
        # element.bg="green"
    for i,item in enumerate(items):
      # globals()["item"+str(i)]=tk.StringVar()
      productNameLabel=ttk.Entry(self.tableFrame, width=len(str(item[0])),style="label.TEntry")
      productNameLabel.insert(0,item[0])
      productNameLabel.grid(row=i+1,column=0)
      # print(item0)
      itemLabel=ttk.Combobox(self.tableFrame,value=itemList,width=7)
      itemLabel.set(item[1])
      itemLabel.grid(row=i+1,column=1)

      priceLabel=ttk.Entry(self.tableFrame,width=len(str(item[2])))
      priceLabel.insert(0,item[2])
      priceLabel.grid(row=i+1,column=2)

      amountLabel=ttk.Entry(self.tableFrame,width=len(str(item[3])))
      amountLabel.insert(0,item[3])
      amountLabel.grid(row=i+1,column=3)

      discountLabel=ttk.Entry(self.tableFrame,width=len(str(item[4])))
      discountLabel.insert(0,item[4])
      discountLabel.grid(row=i+1,column=4)

      totalLabel=ttk.Entry(self.tableFrame,width=len(str(item[5])))
      totalLabel.insert(0,item[5])
      totalLabel.grid(row=i+1,column=5)
      
      deleteButton=ttk.Button(self.tableFrame,text="delete")
      deleteButton.bind("<ButtonPress>",self.delete)
      deleteButton.grid(row=i+1,column=6)


    self.tableFrame.pack(pady=10)
    children = self.tableFrame.winfo_children()
    # for child in children:
    #   print(child)
    # print(children[7].get())
    # decideFrame=ttk.LabelFrame(parent)
    decideButton=ttk.Button(parent,text="決定",command=self.decide)
    decideButton.pack()
    # print(itemLabel.get()[1])
    # combobox.grid(column=1,row=1)
    
    
    # table_btn=tk.Frame(self.tree)
    # table_btn.pack(pady=10)
    # tk.Button(table_btn,text="button",command=self.test).pack(side="top")
    # self.tree.insert(parent="",index=0, iid=0, values=(1,11,111))

    # combo_frame.pack(pady=10)
    # list_frame= ttk.LabelFrame(self,text="list_frame")
    # idPathLabel=ttk.Label(list_frame,text="idPathLabel")
    # idPathLabel.grid(column=0,row=0)

    # namePathLabel=ttk.Label(list_frame,text="namePathLabel")
    # namePathLabel.grid(column=1,row=0)

    # id=ttk.Label(list_frame,text="id")
    # id.grid(column=0,row=1)

    # combobox = ttk.Combobox(list_frame,width=7 ,height=3,value=('a','b','c'))
    # combobox.grid(column=1,row=1)
    # # name=ttk.Label(list_frame,text="name")
    # # name.grid(column=1,row=1)
    
    # list_frame.pack(pady=10)

  def delete(self,event):
    elements=self.tableFrame.winfo_children()
    row=event.widget.grid_info()["row"]
    for i in range(7):
      elements[row*7+i].grid_remove()


  def decide(self):
    elements=self.tableFrame.winfo_children()
    result=[]

    # print("bbb")

    #### for i,element in enumerate(elements):###
      # if i%6!=4 or type(element)==ttk.Combobox and element.get():
      # if i>=6 and 12>i:
        # element.destroy()
      # print(i,type(element))
      # print(element.keys())
      # if element.get().isdecimal()and int(element.get())< 10:
      # element.configure(foreground="red")
      # print(element.keys())
      # for j in element.keys():
      #   print(j,"[",element.cget(j),"]")


  def test(self):
    # print("11")
    selected = self.tree.focus()
    item = self.tree.item(0)
    # print(item)
    # print(selected)

    # tmp=self.tree.item(selected,'values')
    tmp=self.tree.item("0",'values')
    self.tree.insert(parent="",index=0,value=(tmp[1],tmp[2],tmp[0]))

  def add_task(self):
    task=self.task_entry.get()
    if task:
      self.tasks.append(task)
      self.task_list.insert("end",task)
      self.task_entry.delete(0,"end")
  def delete_task(self):
    selected_indices=self.task_list.curselection()
    for index in selected_indices[::-1]:
      self.task_list.delete(index)
      self.tasks.pop(index)




if __name__=="__main__":
  root = tk.Tk()
  app=ComfirmReciept(parent=root)
  app.mainloop()
    



# root.mainloop()