import copy as cp
import tkinter as tk
from  tkinter import ttk
import item_db as db
import re
from googletrans import Translator

# hasIssue = True # Whether System behavior is nomal
class ComfirmReciept(tk.Frame):
  root = tk.Tk() # make display
  def __init__(self,items,date,store,discount): 
    super().__init__(self.root)
    
    self.root.title("comfirm detail") # title 
    self.root.geometry("800x1000")    # size
    self.root.update_idletasks()      # updadate root size (default is 1x1)
    self.date=date   # to instance variable
    self.store=store # to instance variable
    self.discount = discount
    self.discount_total = sum(list(zip(*discount))[1])

    storeDateFrame=tk.Frame(self.root,height=27) # Frame for store name and date 
    storeDateFrame.pack(pady=0)                  # set position
    
    storeNameLabel=tk.Label(storeDateFrame,text="店舗名: ") # Label for "店舗名: "
    storeNameLabel.place(relx=0.0)                         # set position

    self.storeNameEntry=tk.Entry(storeDateFrame,width=20) # Entry for store name
    self.storeNameEntry.insert(0,self.store)              # set store name
    self.storeNameEntry.place(relx=0.08)                  # set position

    dateLabel=tk.Label(storeDateFrame,text="日付: "+self.date) # Label for date
    dateLabel.place(relx=0.8)                                 # set position


    parentFrame=ttk.LabelFrame(self.root) # Frame for item list
    parentFrame.pack(pady=1)              # set position

    columnHaedFrame=tk.Frame(parentFrame) # Frame for header of item
    columnHaedFrame.pack(pady=0)          # set position


    listFrame=tk.Frame(parentFrame) # Frame for body of item
    listFrame.pack(pady=1)          # set position

    

    self.canvas=tk.Canvas(listFrame,width=100,height=10,scrollregion=(0,0,0,0), bg='white') # to use scroll bar 
    self.tableFrame=tk.Frame(self.canvas,bg="#3A3A3A",borderwidth=20,highlightbackground="red",relief="flat") # this Frame is put item 
    self.canvas.create_window(0,0, window=self.tableFrame,anchor="nw") # put canvas for Frame
    self.canvas.grid(row=0,column=0) # decide position

    ybar = tk.Scrollbar(listFrame,orient=tk.VERTICAL,command=self.canvas.yview,jump=1) # Scrollbar for y-axis direction
    ybar.grid(row=0, column=1,sticky=tk.N + tk.S) # decide position and expand y-axis direction
    self.canvas.config(yscrollcommand = ybar.set)
    columns=["商品","登録名","カテゴリー","金額","数量","割引","合計"] # header of item
    ### display header of item ###
    for i,column in enumerate(columns): 
      columnLabel=tk.Label(columnHaedFrame,text=column) 
      self.setStyle(columnLabel) # set Style
      if i == 1 or i == 2: # change length of Label whether tk.Entry or ttk.Combobox 
        columnLabel.configure(padx=5) # change width
        columnLabel.grid(row=0,column=i,ipadx=6)
      else:
        columnLabel.configure(padx=1) # change width
        columnLabel.grid(row=0,column=i)
    columnLabel=tk.Label(columnHaedFrame,width=8,padx=3,bg="#3A3A3A") # Label for delete Button
    columnLabel.grid(row=0,column=7,ipadx=17)

    self.itemList=[] # to make list of register item name
    for primary_item_key,primary_item_value in db.itemDB.items():
      self.itemList+=["---"+primary_item_key+"---"] # punctuate with key
      for item_name in primary_item_value: 
        self.itemList+=[item_name] # append register item name

    for i,item in enumerate(items): # for all items
      hasDiscount= len(item)>5 # if having discount label 
      
      productNameEntry=tk.Entry(self.tableFrame) # Entry for item name
      self.setStyle(productNameEntry)            # set Style
      productNameEntry.insert(0,item[0])         # set item name
      productNameEntry.grid(row=i+1,column=0)    # set position

      registerNameCombobox=ttk.Combobox(self.tableFrame,value=self.itemList) # Combobox for register item list
      self.setStyle(registerNameCombobox)                                    # set Style 
      registerNameCombobox.set(item[1])                                      # set register item name 
      registerNameCombobox.grid(row=i+1,column=1)                            # set position

      categoryCombobox=ttk.Combobox(self.tableFrame,value=[value for value in db.itemDB.keys()]) # Combobox for item category
      self.setStyle(categoryCombobox)                                                            # set Style  
      categoryCombobox.set(item[2])                                                              # set item category 
      categoryCombobox.bind("<Enter>",self.categoryEvent)                                        # set Enter Event
      categoryCombobox.grid(row=i+1,column=2)                                                    # set position 

      priceEntry=tk.Entry(self.tableFrame) # Entry for item price
      self.setStyle(priceEntry)            # set Style
      priceEntry.insert(0,item[3])         # set item price
      priceEntry.grid(row=i+1,column=3)    # set position

      amountEntry=tk.Entry(self.tableFrame) # Entry for item amount
      self.setStyle(amountEntry)            # set Style
      amountEntry.insert(0,item[4])         # set item amount
      amountEntry.grid(row=i+1,column=4)    # set position

      discountEntry=tk.Entry(self.tableFrame) # Entry for item discount
      self.setStyle(discountEntry)            # set Style
      if hasDiscount:                         
        discountEntry.insert(0,item[5])       # set item discount
      else:
        discountEntry.insert(0,"---")         # set no discount as "---"
      discountEntry.grid(row=i+1,column=5)    # set position

      totalEntry=tk.Entry(self.tableFrame)    # set item total price
      self.setStyle(totalEntry)               # set Style
      if type(item[3]) == int and type(item[4]) == int:
        if hasDiscount: 
          totalEntry.insert(0,int(item[3])*int(item[4])-int(item[5])) # set total (discount)
        else:
          totalEntry.insert(0,int(item[3])*int(item[4])) # set total (no discount)
      totalEntry.grid(row=i+1,column=6)       # set position
      
      deleteButton=ttk.Button(self.tableFrame,text="delete",width=7)  # set Button for delete
      deleteButton.bind("<ButtonPress>",self.deleteItem)              # set ButtonPress Event
      deleteButton.grid(row=i+1,column=7)                             # set position

    parentFrame.update_idletasks()                                     # update parentFrame size because tableFrame is added many item and parentFrame include tableFrame
    functionFrame=tk.Frame(self.root)                                  # include decide , back ,next button and total label
    functionFrame.propagate(False)                                     # can not chage automatic
    functionFrame.configure(width=parentFrame.winfo_width(),height=200) # set Style
    functionFrame.pack()                                               # set position

    
    result_tk ={"frame":tk.Frame(functionFrame,relief=tk.SOLID)}
    result_tk["frame"].configure(width=parentFrame.winfo_width()/4,height=200) # set Style
    # print(parentFrame.winfo_width())
    # print(result_tk["frame"].winfo_width(),result_tk["frame"].winfo_height())
    # print(functionFrame.winfo_width(),functionFrame.winfo_height())
    result_tk["frame"].place(relx=0.75)
    
    result_tk.update(
      subtotal = tk.Label(result_tk["frame"],text="小計"),
      discount = tk.Label(result_tk["frame"],text="割引"),
      tax      = tk.Label(result_tk["frame"],text="税"),
      total    = tk.Label(result_tk["frame"],text="合計"),
    )
    self.result_tk_value = {
      "subtotal" :tk.Label(result_tk["frame"],text=0),
      "discount" :tk.Entry(result_tk["frame"],width=5, justify=tk.RIGHT,bg="#4B4B4B"),
      "tax"      :tk.Label(result_tk["frame"],text=0),
      "total"    :tk.Label(result_tk["frame"],text=0)
    }
    self.result_tk_value["discount"].insert(0,self.discount_total)
    self.result_tk_value["discount"].bind("<Enter>", self.display_discount_detail)
    self.result_tk_value["discount"].bind("<Leave>", self.leave_discount_detail)
    self.result_tk_value["discount"].bind("<Return>",self.calculateEvent)
    for i,key_value in enumerate(result_tk.items()):
      key ,value = key_value
      if key == "frame":
        continue
      else:
        value.grid(row = i-1, column = 0)
        self.result_tk_value[key].grid(row = i-1, column = 1,sticky=tk.E)
        unit_label = tk.Label(result_tk["frame"],text ="円")
        unit_label.grid(row = i-1, column = 2)
        

    decideButton=ttk.Button(functionFrame,text="決定",command=self.decideItem) # Button for decide function
    decideButton.place(relx=0.35)                                             # set position

    decideButton=ttk.Button(functionFrame,text="+",command=self.addItem) # Button for add function
    decideButton.place(relx=0.5)                                         # set position
    
    
    self.updateRegion() # update field
    self.calculate()    # calcukate total
    # print(functionFrame.winfo_width(),functionFrame.winfo_height())
    # print(resultFrame.winfo_width(),resultFrame.winfo_height())

    storeDateFrame.configure(width=parentFrame.winfo_width()) # update parentFrame width


    self.root.bind_class("Entry", "<FocusOut>", self.calculateEvent) # Add Event for Entry

  def display_discount_detail(self,event):
    x = self.result_tk_value["discount"].winfo_rootx()+ 25
    y = self.result_tk_value["discount"].winfo_rooty()+ 20
    h = len(self.discount)*50
    w = 50
    self.discount_detail = tk.Toplevel(self.result_tk_value["discount"])
    self.discount_detail.wm_overrideredirect(True)
    self.discount_detail.wm_geometry("%dx%d+%d+%d" % (h,w,x, y))
    
    for i,d in enumerate(self.discount):
      name_label = tk.Label(self.discount_detail,text=d[0])
      value_label = tk.Label(self.discount_detail,text=d[1])
      name_label.grid(row = i, column = 0)
      value_label.grid(row = i, column = 1)
    return
  def leave_discount_detail(self,event): 
    tw = self.discount_detail
    self.discount_detail= None
    if tw:
      tw.destroy()
    return
  
  # def caculate_result(self,event):
  #   self.result_tk_value["subtotal"].configure(text=subtotal)                        # insert subtotal num and "yesn"
  #   discount = int(self.result_tk_value["discount"].get())
  #   tax = int((subtotal-discount)*0.08)
  #   self.result_tk_value["tax"].configure(text = tax)                        # insert tax num and "yesn"
  #   self.result_tk_value["total"].configure(text = subtotal - discount + tax)                        # insert total num and "yesn"
  # def calculate(self,event): # execute when tk.Entry FocusOut
  #   print("aaa")
  #   self.calculate()              # call calculate function

  def categoryEvent(self,event): # When mouse enter categoryCombobox
    subtotal = 0     # total 
    elements=self.tableFrame.winfo_children()  # get all item in tableFrame
    if event.widget.get() in db.itemDB.keys(): # category name include in register category name
      elements[elements.index(event.widget)-1].configure(value=[value for value in db.itemDB[event.widget.get()]]) # change text of register item name 
    else:
      elements[elements.index(event.widget)-1].configure(value="") # no category name in register category name
    
  def calculateEvent(self,event): # execute when tk.Entry FocusOut
    self.calculate()              # call calculate function

  def calculate(self): # calucute
    elements = self.tableFrame.winfo_children() # get all item in tableFrame
    eachTotal = 0 # each item 
    subtotal = 0     # total 
    isInt = True  # item price and item amount are int type 
    for i,element in enumerate(elements):  
      if i%8 == 3 or i%8 == 4:                                                           # for item price or item amount
        if not(element.get().isdecimal()):                                               # not integer
          element.configure(highlightbackground="red")                                   # cahnge Style
          isInt=False
        else:                                                                            # integer or not
          element.configure(highlightbackground="#565656")                               # change default Style
      elif i%8 == 5 and isInt and element.get() != "":                                   # for discount and item price and item amount is integer
        eachTotal=int(elements[i-2].get())*int(elements[i-1].get())                      # calculate each item total
        if element.get().isdecimal():                                                    # discount is integer
          eachTotal-=int(element.get())                                                  # calculate total
        elif element.get()[-1] == "%" and re.match("[0-9]+",element.get()):              # discount is include "%"
          eachTotal=int(eachTotal*(1-int(re.match("[0-9]+",element.get()).group())/100)) # calculate total
      elif i%8 == 6:                                                                     # for total
        if isInt:                                                                        # integer or not
          eachTotal=int(elements[i-3].get())*int(elements[i-2].get())                      # calculate each item total
          element.delete(0,tk.END)                                                       # delete text in the total Label
          element.insert(0,eachTotal)                                                    # input total
          subtotal+=eachTotal                                                               # add each item total to total
        eachTotal=0
        isInt=True                                                                       # init variable
    self.result_tk_value["subtotal"].configure(text=subtotal)                        # insert subtotal num and "yesn"
    discount = int(self.result_tk_value["discount"].get())
    tax = int((subtotal-discount)*0.08)
    self.result_tk_value["tax"].configure(text = tax)                        # insert tax num and "yesn"
    self.result_tk_value["total"].configure(text = subtotal - discount + tax)                        # insert total num and "yesn"
  

  def updateRegion(self):
    """ update region """
    self.tableFrame.update_idletasks()
    canvas_height = 500                              # max canvas size
    if canvas_height>self.tableFrame.winfo_height(): # if height of tableFrame under height of canvas
      canvas_height=self.tableFrame.winfo_height()   # set height of canvas
    self.canvas.config(width=self.tableFrame.winfo_width(), height=canvas_height,scrollregion=(0,0,0,self.tableFrame.winfo_height()))  # change size

  def setStyle(self,widget):
    """ set Style for tk or ttk """
    if type(widget) == tk.Entry:       # for tk.Entry
      widget.configure(width=7,justify="center",bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
    elif type(widget) == ttk.Combobox: # for ttk.Combobox
      widget.configure(width=7)
    elif type(widget) == tk.Label:     # for tk.Label
      widget.configure(width=7,padx=2,justify="center")
      

  def deleteItem(self,event):
    """ delete the row """
    elements=self.tableFrame.winfo_children()
    for i in range(8):
      elements[elements.index(event.widget)-i].destroy()
    self.calculate()    # calculate total
    self.updateRegion() # update region

  def addItem(self):
    """ add new row for new item """
    if self.tableFrame.winfo_children() != []: # get last number of row
      row=(self.tableFrame.winfo_children())[-1].grid_info()["row"] 
    else:
      row=0

    productNameEntry=tk.Entry(self.tableFrame) # Entry for item name
    self.setStyle(productNameEntry)            # set Style 
    productNameEntry.grid(row=row+1,column=0)  # set position

    registerNameCombobox=ttk.Combobox(self.tableFrame,value=self.itemList) # Combobox for register item name
    self.setStyle(registerNameCombobox)                                    # set Style 
    registerNameCombobox.grid(row=row+1,column=1)                          # set position

    categoryCombobox=ttk.Combobox(self.tableFrame,value=[value for value in db.itemDB.keys()]) # Combobox for item category
    self.setStyle(categoryCombobox)                                                            # set Style  
    categoryCombobox.bind("<Enter>",self.categoryEvent)                                        # set Enter Event
    categoryCombobox.grid(row=row+1,column=2)                                                  # set position 

    priceEntry=tk.Entry(self.tableFrame) # Entry for item price
    self.setStyle(priceEntry)            # set Style 
    priceEntry.grid(row=row+1,column=3)  # set position

    amountEntry=tk.Entry(self.tableFrame) # Entry for item amount
    self.setStyle(amountEntry)            # set Style 
    amountEntry.grid(row=row+1,column=4)  # set position

    discountEntry=tk.Entry(self.tableFrame) # Entry for item discount
    self.setStyle(discountEntry)            # set Style 
    discountEntry.grid(row=row+1,column=5)  # set position

    totalEntry=tk.Entry(self.tableFrame) # Entry for total price
    self.setStyle(totalEntry)            # set Style 
    totalEntry.grid(row=row+1,column=6)  # set position

    deleteButton=ttk.Button(self.tableFrame,text="delete") # Button for delete row
    deleteButton.bind("<ButtonPress>",self.deleteItem)     # set ButtonPress Event
    deleteButton.grid(row=row+1,column=7)                  # set position

    self.updateRegion() # update region



  def decideItem(self):
    """ Called when decide button is clicked. check all item is validation and class new category GUI """
    elements = self.tableFrame.winfo_children()
    isOk = (elements!=[]) # if item is null = false
    if self.storeNameEntry.get() == "": # Check store name is entered
      self.storeNameEntry.configure(highlightbackground="red") # if enpty, change Style
      isOk=False # error
    else: # entered
      self.store=self.storeNameEntry.get() 
      self.storeNameEntry.configure(highlightbackground="#565656") # cahnge Style
    
    for i,element in enumerate(elements):
      if type(element) == ttk.Combobox: # check for Combobox
        if "---" in element.get(): # if entered "---""
          isOk=False # error
          element.configure(foreground="red") # change Style
        else: # no problem for Combobox
          element.configure(foreground="white") # change Style
      elif type(element) == tk.Entry: # check for Entry
        if i%8 == 0 and (("---" in element.get()) or element.get() == ""): # item name is "---" or enpty
          isOk=False # error
          element.configure(highlightbackground="red") # change Style
        elif i%8 >= 3 and not(element.get().isdecimal()) and i%8 != 5: # item price and item amount and total are int type 
          isOk=False # error
          element.configure(highlightbackground="red") # change Style
        else:
          element.configure(highlightbackground="#565656") # change Style
          
    if isOk == True: # no error
      oneLine=[] # for each row
      self.allItem=[] # for all item 
      for i,element in enumerate(elements):
        if type(element) == tk.Entry or type(element) == ttk.Combobox: # only item infomation widget
          if i%8 < 5 : 
            oneLine.append(element.get()) # add element for oneLine[]
          elif i%8 == 5:
            if element.get().isdecimal(): # whether discount is included "%" or string or not
              oneLine.append(element.get()) # only int type
            elif element.get() != "" and element.get()[-1] == "%" and re.match("[0-9]+",element.get()): # included "%"
              totalNoDiscount=int(elements[i-2].get())*int(elements[i-1].get()) # calcurate discount amount from "%"
              oneLine.append(int(totalNoDiscount*int(re.match("[0-9]+",element.get()).group())/100)) # add dicount amount 
            else:
              oneLine.append("0") # no dicount
          elif i%8 == 6: # end row
            oneLine.append(element.get()) # add total for oneLine[]
            self.allItem.append(cp.copy(oneLine)) # add row for all item with copy()
            oneLine.clear() # reset oneLine[]
      translator = Translator()
      # self.newCategory = NewCategory(self.allItem,self.root) # make new GUI for let user type new categpry name in English
      self.newCategory={}
      for item in self.allItem:
        if not(item[2] in db.itemDB):    # category name is not included register category name
          en_text = translator.translate(item[2], dest='en').text
          # if en_text already exist, change name
          tmp_text = en_text
          i = 2
          while tmp_text in db.itemDB.values():
            tmp_text = en_text + str(i)
            i += 1
          en_text += str(i)

          self.newCategory[item[2]] = "_".join(list(en_text.split())) # add category for dictionary
      print(self.newCategory)
      self.root.destroy()              # destory parent gui
      return 

  def getAllItem(self): # get all item 
    return self.allItem
 