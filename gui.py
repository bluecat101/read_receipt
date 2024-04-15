################################################
# ------------------ README ------------------ #
# Display waht was recognized as an item.      #
# Sometime, OCR misstake so you can fix it.    #
#                                              #
################################################

import copy as cp        # To prevent it from being reflected after copying
import tkinter as tk     # To dispaly GUI
from  tkinter import ttk # To dispaly GUI
import item_db as db     # To access item DataBase
import store_db as sdb   # To access store DataBase
import re                # To check whether input is integer or percentage display
from googletrans import Translator # To translate Japanese to English to make category in English

# hasIssue = True # Whether System behavior is nomal
class ComfirmReceipt(tk.Frame):
  """
  ## Description:
    This class is related GUI. You can comfirm OCR is correct or not.
    You add some new data, delete extra data and fix data
  ## Attributes:
    `root () `            : The base frame for gui
    `date () `            : To store purchase date
    `store () `           : To store purchase store
    `discount () `        : To store special discount like coupon
    `main_table () `      : Display information related to products
    `boolean_Checkbox ()` : To refer to whether the reduced tax rate is applicable or not between different methods without registering in the widget
    `shopping_results () `: Display subtotal, special discount, total
    `all_item () `        : To pass all data
    `new_category () `    : To record new category with Japanese and English
  """
  def __init__(self,items,date,store,discount): 
    """
    ## Description:
      Set class argument and set frame and input recognized item

    ## Args:
        `items (str[][])`   : All item
        `date (str)`        : Purchase date
        `store (str)`       : Purchase store
        `discount (str[][])`: Special discount
    """
    self.root = tk.Tk() # Make display
    super().__init__(self.root)
    
    self.root.title("comfirm detail") # Set gui title 
    self.root.geometry("800x1000")    # Set size
    self.root.update_idletasks()      # Update root size (default is 1x1)
    
    self.date=date                    
    self.store=[store,sdb.tax(store)] # Get purchase store and whether tax is included or excluded from store name
    self.discount = discount
    self.discount_total = sum(list(zip(*discount))[1]) if len(discount) > 0 else 0 # Total discount, self.discount is duplicate list so calculate this way
    self.boolean_Checkbox = []
    # Make frame for part of header and set purchase store,purpose and date.
    self.header={"Frame":tk.Frame(self.root,height=40)}
    self.header["Frame"].pack(pady = 0)
    self.header.update(
      store_Label      = tk.Label(self.header["Frame"], text="店舗名: "),
      store_Entry      = tk.Entry(self.header["Frame"], width=20),
      purpose_Label    = tk.Label(self.header["Frame"], text="目的: "),
      purpose_Combobox = ttk.Combobox(self.header["Frame"], value=["家族","父"], width=3),
      tax_Label        = tk.Label(self.header["Frame"], text="税: "),
      tax_Combobox     = ttk.Combobox(self.header["Frame"], value=["内税","外税"], width=3),
      date_Label       = tk.Label(self.header["Frame"], text="日付: "),
      date_Entry       = tk.Entry(self.header["Frame"], width=15)
    )
    # Inisialize data
    self.header["store_Entry"].insert(0,self.store[0])  # Set store name
    self.header["purpose_Combobox"].set("父" if self.store[0] in sdb.purpose_for_father else "家族") # Set item category 
    self.header["tax_Combobox"].set(self.store[1])      # Set item category
    self.header["tax_Combobox"].bind("<<ComboboxSelected>>",self.calculate_event)
    self.header["date_Entry"].insert(0,self.date)       # Set date

    
    # Set up things
    self.header["store_Label"].place(relx=0.0)         
    self.header["store_Entry"].place(relx=0.08)        
    self.header["purpose_Label"].place(relx=0.40)      
    self.header["purpose_Combobox"].place(relx=0.45)
    self.header["tax_Label"].place(relx=0.55)      
    self.header["tax_Combobox"].place(relx=0.58)   
    self.header["date_Label"].place(relx=0.7)         
    self.header["date_Entry"].place(relx=0.75)          
    
    # Make frame for main table to display item etc...
    self.main_table = {"Frame":tk.Frame(self.root)}
    self.main_table["Frame"].pack(pady=1)  # Set position

    # Make table head and body and canvas to use scrollbar 
    self.main_table["head_Frame"]= tk.Frame(self.main_table["Frame"],width=750)
    self.main_table["Canvas"]=tk.Canvas(self.main_table["Frame"],width=100,height=10,scrollregion=(0,0,0,0), bg='white') # to use scroll bar 
    self.main_table["body_Frame"]=tk.Frame(self.main_table["Canvas"],bg="#3A3A3A",borderwidth=20,highlightbackground="red",relief="flat" ) # this Frame is put item 
    self.main_table["Canvas"].create_window(0,0, window=self.main_table["body_Frame"],anchor="nw") # put canvas for Frame
    self.main_table["Scrollbar"] = tk.Scrollbar(self.main_table["Frame"],orient=tk.VERTICAL,command=self.main_table["Canvas"].yview) # Scrollbar for y-axis direction
    
    
    # set up things 
    self.main_table["head_Frame"].grid(row=0,column=0)
    self.main_table["Canvas"].grid(row=1,column=0,sticky=tk.N + tk.S)     # Expand y-axis direction 
    self.main_table["Scrollbar"].grid(row=1, column=1,sticky=tk.N + tk.S) # Expand y-axis direction
    self.main_table["Canvas"].config(yscrollcommand = self.main_table["Scrollbar"].set)
    

    columns=["軽","商品","登録名","カテゴリー","金額","数量","割引","合計"] # Item for table header
    # display table header
    for i,column in enumerate(columns):
      column_Label=tk.Label(self.main_table["head_Frame"],text=column)
      if i == 0: # For tax labe;
        column_Label.configure(padx=5)
        column_Label.grid(row=0,column=i)
      elif i == 2 or i == 3: # Change width of label whether element of table body is tk.Entry or ttk.Combobox 
        column_Label.configure(width=7,padx=10)
        column_Label.grid(row=0,column=i) 
      else:
        column_Label.configure(width=7,padx=3)
        column_Label.grid(row=0,column=i)
    # For delete button head
    column_Label=tk.Label(self.main_table["head_Frame"],width=5,padx=3,bg="#3A3A3A") # Label for delete Button
    column_Label.grid(row=0,column=8,ipadx=20)

    # Make list of registered name
    # Connect category name(key) and item name(value)
    self.item_list=[] 
    for key,value in db.item_DB.items():
      self.item_list+=["---"+key+"---"]
      for item_name in value: 
        self.item_list+=[item_name]

    # Add each line with item, registered name, category etc...
    for i,item in enumerate(items): # For all items
      self.add_item(item=item["item"], registered_name=item["registered_name"], category=item["category"], price=item["price"], amount=item["amount"], discount=item["discount"])
    # Update self.main_table["Frame"] size because tableFrame is added many item and to change size of scrollbar in canvas
    self.main_table["Frame"].update_idletasks()

    # Include decide, add button and total label
    footer=tk.Frame(self.root)
    decide_Button=ttk.Button(footer,text="決定",command=self.decide) # Button for decide function
    add_Button=ttk.Button(footer,text="+",command=self.add_item)     # Button for add function
    shopping_results_Frame = tk.Frame(footer,relief=tk.SOLID)

    # Label for shopping results
    shopping_results_Label={
      "subtotal": tk.Label(shopping_results_Frame,text="小計(税)"),
      "discount": tk.Label(shopping_results_Frame,text="割引"),
      "total"   : tk.Label(shopping_results_Frame,text="合計"),
    }
    # Value for shopping results
    self.shopping_results = {
      "subtotal" :tk.Label(shopping_results_Frame,text=0),
      "discount" :tk.Entry(shopping_results_Frame,width=5, justify=tk.RIGHT,bg="#4B4B4B"),
      "total"    :tk.Label(shopping_results_Frame,text=0)
    }
    # add style setting and function
    footer.configure(width=self.main_table["Frame"].winfo_width(),height=200)
    # Include subtotal, discount, total to display
    shopping_results_Frame.configure(width=self.main_table["Frame"].winfo_width()/4,height=200)
    self.shopping_results["discount"].insert(0,self.discount_total)
    self.shopping_results["discount"].bind("<Enter>", self.display_discount_detail)
    self.shopping_results["discount"].bind("<Leave>", self.leave_discount_detail)
    self.shopping_results["discount"].bind("<Return>",self.calculate_event)

    # Setting up
    footer.pack() 
    decide_Button.place(relx=0.35)
    add_Button.place(relx=0.5)
    shopping_results_Frame.place(relx=0.75)
    for i,key_value in enumerate(shopping_results_Label.items()):
      key ,value = key_value
      value.grid(row = i, column = 0)
      self.shopping_results[key].grid(row = i, column = 1,sticky=tk.E)
      # Display unit each price
      unit_label = tk.Label(shopping_results_Frame,text ="円")
      unit_label.grid(row = i, column = 2)
    # Update Region and inisialize total because frame size is too small now
    self.update_region() # Update field
    self.calculate()    # calculate total

    self.header["Frame"].configure(width=self.main_table["Frame"].winfo_width()) # update self.main_table["Frame"] width because the width was changed by added item
    self.root.bind_class("Entry", "<FocusOut>", self.calculate_event) # Add Event for Entry

  def display_discount_detail(self,_event):
    """
    ## Description:
     Display specail discount with popup style.
    ## Args:
        `_event`: don't use it but need it
    """
    # Set range of popup space
    x = self.shopping_results["discount"].winfo_rootx()+ 25
    y = self.shopping_results["discount"].winfo_rooty()+ 20
    w = max(map(len,list(zip(*self.discount))[0])) * 12 +60 # Reference number of special discount
    h = len(self.discount)*50                               # Reference number of special discount
    self.shopping_results["discount_detail"] = tk.Toplevel(self.shopping_results["discount"])
    self.shopping_results["discount_detail"].wm_overrideredirect(True)
    self.shopping_results["discount_detail"].wm_geometry("%dx%d+%d+%d" % (w,h,x, y))
    
    for i,d in enumerate(self.discount):
      name_Label = tk.Label(self.shopping_results["discount_detail"],text=d[0])
      value_Label = tk.Label(self.shopping_results["discount_detail"],text=str(d[1])+"円")
      # Setting up
      name_Label.grid(row = i, column = 0)
      value_Label.grid(row = i, column = 1)

  def leave_discount_detail(self,_event): 
    """
    ## Description:
      Display specail discount with popup style. When mouse is left, delete popup
    ## Args:
        `_event`: don't use it but need it
    """
    tw = self.shopping_results["discount_detail"]
    self.shopping_results["discount_detail"]= None
    # delete widget
    if tw:
      tw.destroy()

  def category_event(self,event): # When mouse enter one_line["category_Combobox"]
    """
    ## Description:
      When selected or type category, match registered name to the category
    ## Args:
      `event`: what wedget is selected
    """
    elements=self.main_table["body_Frame"].winfo_children()  # get all item in tableFrame
    if event.widget.get() in db.item_DB.keys(): # selected category exist in DB
      elements[elements.index(event.widget)-1].configure(value=[value for value in db.item_DB[event.widget.get()]]) # change text of register item name 
    else: # New registered category name
      elements[elements.index(event.widget)-1].configure(value="")
    
  def calculate_event(self,_event):
    """
    ## Description:
      To overload method of calculate
    ## Args:
      `_event`: don't use it but need it
    """
    self.calculate()

  def calculate(self): # calucute
    """
    ## Description:
      To calculate item price from price per one, amount and discount for all item.
      And Check item whether type of item is int or not
    """
    elements = self.main_table["body_Frame"].winfo_children() # Get all item in tableFrame
    subtotal = [0,0] # [0] is total include tax and [1] is only tax. Don't mind internal or external taxes
    for i in range(int(len(elements)/9)):
      row_element = elements[i*9:i*9+8]
      has_error = self.check_for_error(row_element,i) # Item price, amount and discount are the right type
      if not(has_error):
        total_element = row_element[7]
        total_element.delete(0,tk.END)                                        # Delete the value already entered
        total = [int(row_element[4].get())*int(row_element[5].get()),0]     # Get total from item price and amount. [0] is total include tax and [1] is total don't include tax
        if row_element[6].get().isdecimal():                                 # Discount is only integer
          total[0] -= int(row_element[6].get())                                
        elif re.match("^[0-9]+%$",row_element[6].get()):                    # Discount has "%"
          total[0] = int(total[0]*(1-int(re.match("^[0-9]+",row_element[6].get()).group())/100))
        # Calculate the total by dividing into cases including tax and excluding tax.
        if self.is_external_tax(): # External tax
          total[1] = total[0]
          if self.boolean_Checkbox[i].get(): # Not eligible for reduced tax rate(軽減税率対象外)
            total[0] = int(total[0] * 1.08)
          else:                        # Eligible for reduced tax rate(軽減税率対象)
            total[0] = int(total[0] * 1.1)
          subtotal[1] += (total[0] - total[1])
          total_element.insert(0,"%d(%d)"%(total[0],total[1]))
        else:                      # Internal tax
          # Calculate internal tax
          if self.boolean_Checkbox[i].get(): # Not eligible for reduced tax rate(軽減税率対象外)
            subtotal[1] += total[0]*(8/108)
          else:                        # Eligible for reduced tax rate(軽減税率対象)
            subtotal[1] += total[0]*(1/11)
          total_element.insert(0,total[0])
        subtotal[0] += total[0]
    
    if self.is_external_tax(): # External tax
      self.shopping_results["subtotal"].configure(text="%d(%d)"%(subtotal[0],subtotal[1])) # Display total and tax amount
    else:                      # Internal tax
      self.shopping_results["subtotal"].configure(text=subtotal[0])
    discount = int(self.shopping_results["discount"].get())
    self.shopping_results["total"].configure(text = subtotal[0] - discount)
  
  def is_external_tax(self):
    """
    ## Description:
      Whether tax is ecternal or internal
    ## Retuens:
      `_(bool)` : Internal tax or external tax
    """
    return (self.header["tax_Combobox"].get() == "外税")
  
  def check_for_error(self,elements,row):
    """
    ## Description:
      Check each_line has error or not
    ## Args:
      `elements(widget[])`: Widget in a row
      `row(int)`: Number of lines
    ## Returns:
      `has_error(bool)`: Generates an error when there is a part that does not match the type
    """
    has_error = False
    for i,element in enumerate(elements):
      each_has_error = False   # Item price, amount and discount are the right type
      if i%8 == 1 and element.get() == "": # For item
          each_has_error = True
      elif (i%8 == 2 or i%8==3) and ("---" in element.get() or element.get() == ""): # For registered name and category
          each_has_error = True
      elif (i%8 == 4 or i%8 == 5) and not(element.get().isdecimal()): # For price and amount. Don't want to use not, but isalpha() method judges "◯" to be a number, and int() method causes an error, so I reject it.                                      
          each_has_error = True
      elif i%8 == 6 and not(element.get().isdecimal() or re.match("^[0-9]+%$",element.get())): # For discount
          each_has_error = True
      # Change styles depending on type and presence/absence of errors
      if type(element) == ttk.Combobox: # For registered name and category
        if each_has_error:
          element.configure(foreground="red")
        else:
          element.configure(foreground="white") # Change default Style
      elif type(element) == tk.Entry: # item name, price, amount, discount
        if each_has_error:
          element.configure(highlightbackground="red")
        else:
          element.configure(highlightbackground="#565656") # Change default Style
      has_error = any([has_error,each_has_error])
    return has_error
  
  def update_region(self):
    """
    ## Description:
      Update self.main_table["body_Frame"] region after added item
    """
    self.main_table["body_Frame"].update_idletasks()
    canvas_height = 500 # Max canvas size
    if canvas_height>self.main_table["body_Frame"].winfo_height(): # Whether height of tableFrame under height of canvas
      canvas_height=self.main_table["body_Frame"].winfo_height()
    # Change size
    self.main_table["Canvas"].config(width=self.main_table["body_Frame"].winfo_width(), height=canvas_height,scrollregion=(0,0,0,self.main_table["body_Frame"].winfo_height()))

  def set_style(self,widget):
    """
    ## Description:
      Set style for default
    Args:
      `widget`: Widget to be changed
    """
    if type(widget) == tk.Entry:       # For tk.Entry
      widget.configure(width=7,justify="center",bg="#4B4B4B",borderwidth=-0.5,highlightbackground="#565656",relief="flat")
    elif type(widget) == ttk.Combobox: # For ttk.Combobox
      widget.configure(width=7)
    elif type(widget) == tk.Label:     # For tk.Label
      widget.configure(width=7,padx=2,justify="center")
      
  def delete_item(self,event):
    """
    ## Description:
      Delete line item when clicked
    ## Args:
      `event`: what wedget is selected
    """
    elements = self.main_table["body_Frame"].winfo_children()
    # Where line is deleted
    row = int(elements.index(event.widget)/9)
    row_elements = elements[row*9:row*9+9]
    # Delete one line
    for element in row_elements:
      element.destroy()
    del self.boolean_Checkbox[row] # Delete tk.BooleanVar() associated with the Checkbox in this row
    self.calculate()     # Calculate
    self.update_region() # Update region

  def add_item(self,item="",registered_name="---",category="---",price="",amount="",discount=""):
    """
    ## Description
      Add item line when push "+"
    """
    " Get current row"
    if self.main_table["body_Frame"].winfo_children() != []:
      row = (self.main_table["body_Frame"].winfo_children())[-1].grid_info()["row"] 
    else:
      row=0
    # Add widget for one line
    self.boolean_Checkbox.append(tk.BooleanVar()) # To get statue of tax Checkbutton 
    self.boolean_Checkbox[-1].set(True) # Inisialize to True
    # Not eligible for reduced tax rate(軽減税率対象外)
    if registered_name in ["酒", "ビール"]  or category in ["その他", "車", "外食"]:
      self.boolean_Checkbox[-1].set(False)
    one_line={
      "tax_Checkbutton"          : tk.Checkbutton(self.main_table["body_Frame"], variable=self.boolean_Checkbox[-1]),
      "item_Entry"               : tk.Entry(self.main_table["body_Frame"]),
      "registered_name_Combobox" : ttk.Combobox(self.main_table["body_Frame"],value=self.item_list),
      "category_Combobox"        : ttk.Combobox(self.main_table["body_Frame"],value=[value for value in db.item_DB.keys()]),
      "price_Entry"              : tk.Entry(self.main_table["body_Frame"]) ,
      "amount_Entry"             : tk.Entry(self.main_table["body_Frame"]),
      "discount_Entry"           : tk.Entry(self.main_table["body_Frame"]),
      "total_Entry"              : tk.Entry(self.main_table["body_Frame"]),
      "delete_Button"            : ttk.Button(self.main_table["body_Frame"],text="delete",width=7)
    }
      
    # Set Style
    self.set_style(one_line["item_Entry"])
    self.set_style(one_line["registered_name_Combobox"])
    self.set_style(one_line["category_Combobox"])
    self.set_style(one_line["price_Entry"])
    self.set_style(one_line["amount_Entry"])
    self.set_style(one_line["discount_Entry"])
    self.set_style(one_line["total_Entry"])
    one_line["category_Combobox"].bind("<<ComboboxSelected>>",self.category_event)
    one_line["delete_Button"].bind("<ButtonPress>",self.delete_item)

    # Inisialize and link functions
    one_line["item_Entry"].insert(0,item)
    one_line["registered_name_Combobox"].set(registered_name)
    one_line["category_Combobox"].set(category)
    one_line["price_Entry"].insert(0,price)
    one_line["amount_Entry"].insert(0,amount)
    one_line["discount_Entry"].insert(0,discount)
    if price != "" and amount != "" and discount == "": # Not default value
      one_line["total_Entry"].insert(0,int(price)*int(amount)-int(discount))

    # Setting up position
    one_line["tax_Checkbutton"].grid(row=row+1,column=0)
    one_line["item_Entry"].grid(row=row+1,column=1)
    one_line["registered_name_Combobox"].grid(row=row+1,column=2)
    one_line["category_Combobox"].grid(row=row+1,column=3)
    one_line["price_Entry"].grid(row=row+1,column=4)
    one_line["amount_Entry"].grid(row=row+1,column=5)
    one_line["discount_Entry"].grid(row=row+1,column=6)
    one_line["total_Entry"].grid(row=row+1,column=7)
    one_line["delete_Button"].grid(row=row+1,column=8)
    self.update_region() # pdate region

  def decide(self):
    """
    ## Description
      Get item line and check for errors.
      If there are new category, get category name in English using translation
    """
    # Calculate all item
    self.calculate()
    # Get all element
    elements = self.main_table["body_Frame"].winfo_children()
    is_ok = (elements!=[]) # If item is null => false. 
    # Check part of header
    if self.header["store_Entry"].get() != "": # Check purchase store
      self.store[0]=self.header["store_Entry"].get()
      self.header["store_Entry"].configure(highlightbackground="#565656") # Change Style
    else: # No entered name
      self.header["store_Entry"].configure(highlightbackground="red") # If enpty, change Style
      is_ok = False
    
    
    if re.search('(20[0-9]{2})-(1[0-2]|0[1-9]|[1-9])-([1-3][0-9]|0[1-9]|[1-9])',self.header["date_Entry"].get()): # Check purchase date
      self.data=self.header["date_Entry"].get()
      self.header["date_Entry"].configure(highlightbackground="#565656") # Change Style
    else: # No entered name
      self.header["date_Entry"].configure(highlightbackground="red") # If enpty, change Style
      is_ok = False
      
    
    # Check whether has error in item table
    for i in range(int(len(elements)/9)):
      has_error = self.check_for_error(elements[i*9:i*9+8],i)
      if has_error:
        is_ok = False
        break
    # No error
    if is_ok == True:
      self.all_item=[] # To save for csv file
      self.store[1] = self.header["tax_Combobox"].get()
      for i in range(int(len(elements)/9)):
        row_elements = elements[i*9:i*9+8] # Get row elements
        one_line = {"store": self.store[0],"date": self.date,"purpose": self.header["purpose_Combobox"].get(),"item":  row_elements[1].get(),"registered_name":  row_elements[2].get(),"category":  row_elements[3].get(),"price": row_elements[4].get(),"amount": row_elements[5].get(),"discount": 0,"total": 0} # Do not inisialize "discount" and "total" now because the calculation formula changes depending on the type of discount.
        if one_line["registered_name"] in ["酒", "ビール"]: # If the registered name is related to alcohol, change purpose
          one_line["purpose"] = "父"
        line_discount = row_elements[6].get()
        line_total = re.search("^\d+",row_elements[7].get()).group()
        if line_discount.isdecimal(): # Whether discount is included "%" or string or not
          one_line["discount"] = int(line_discount)
        elif line_discount != "" and line_discount[-1] == "%" and re.match("[0-9]+",line_discount): # Included "%"
          total_without_discount=int(row_elements[4].get())*int(row_elements[5].get()) # calculate discount amount from "%"
          one_line["discount"] = int(total_without_discount*int(re.match("[0-9]+",line_discount).group())/100) # Add dicount amount 
        elif line_discount == "":
          one_line["discount"] = 0
        one_line["total"] = line_total
        self.all_item.append(cp.copy(one_line)) # Add row for all item with copy()
              
      # To has new category
      translator = Translator()
      self.new_category={}
      for item in self.all_item:
        if not(item["category"] in db.item_DB): # Whether category name is not included register category name
          en_text = translator.translate(item["category"], dest='en').text # Store category name in English
          # If en_text already exist, change name
          tmp_text = en_text
          i = 2
          while tmp_text in db.item_DB.values():
            tmp_text = en_text + str(i)
            i += 1
          en_text = tmp_text

          self.new_category[item["category"]] = "_".join(list(en_text.split())) # Add new category for dictionary
      self.root.destroy() # Destory GUI
      return 
