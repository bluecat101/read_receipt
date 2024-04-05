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
    `root () `: The base frame for gui
    `date () `: To store purchase date
    `store () `: To store purchase store
    `discount () `: To store special discount like coupon
    `main_table () `: 
    `shopping_results () `: 
    `allItem () `: 
    `new_category () `: 
  
  """
  root = tk.Tk() # Make display
  def __init__(self,items,date,store,discount): 
    """
    ## Description:
      Set class argument and set frame and input recognized item

    ## Args:
        `items (str[][])`: All item
        `date (str)`: Purchase date
        `store (str)`: Purchase store
        `discount (str[][])`: Special discount
    """
    super().__init__(self.root)
    
    self.root.title("comfirm detail") # Set gui title 
    self.root.geometry("800x1000")    # Set size
    self.root.update_idletasks()      # Update root size (default is 1x1)
    
    self.date=date                    
    self.store=[store,sdb.tax(store)] # Get purchase store and whether tax is included or excluded from store name
    self.discount = discount
    self.discount_total = sum(list(zip(*discount))[1]) if len(discount) > 0 else 0 # Total discount, self.discount is duplicate list so calculate this way

    # Make frame for part of header and set purchase store,purpose and date.
    self.header={"Frame":tk.Frame(self.root,height=40)}
    self.header["Frame"].pack(pady = 0)
    self.header.update(
      store_Label      = tk.Label(self.header["Frame"],text="店舗名: "),
      store_Entry      = tk.Entry(self.header["Frame"],width=20),
      purpose_Label    = tk.Label(self.header["Frame"],text="目的: "),
      purpose_Combobox = ttk.Combobox(self.header["Frame"],value=["家族","父"]),
      date_Label       = tk.Label(self.header["Frame"],text="日付: "),
      date_Entry       = tk.Entry(self.header["Frame"],width=15)
    )
    # Inisialize data
    self.header["store_Entry"].insert(0,self.store[0]) # Set store name
    self.header["date_Entry"].insert(0,self.date)      # Set date             
    self.set_style(self.header["purpose_Combobox"])     # Set style
    self.header["purpose_Combobox"].set("家族")        # Set item category 
    
    # Set up things
    self.header["store_Label"].place(relx=0.0)         
    self.header["store_Entry"].place(relx=0.08)        
    self.header["purpose_Label"].place(relx=0.43)      
    self.header["purpose_Combobox"].place(relx=0.48)   
    self.header["date_Label"].place(relx=0.7)         
    self.header["date_Entry"].place(relx=0.75)          
    
    # Make frame for main table to display item etc...
    self.main_table = {"Frame":tk.Frame(self.root)}
    self.main_table["Frame"].pack(pady=1)  # Set position

    # Make table head and body and canvas to use scrollbar 
    self.main_table["head_Frame"]= tk.Frame(self.main_table["Frame"])
    self.main_table["Canvas"]=tk.Canvas(self.main_table["Frame"],width=100,height=10,scrollregion=(0,0,0,0), bg='white') # to use scroll bar 
    self.main_table["body_Frame"]=tk.Frame(self.main_table["Canvas"],bg="#3A3A3A",borderwidth=20,highlightbackground="red",relief="flat" ) # this Frame is put item 
    self.main_table["Canvas"].create_window(0,0, window=self.main_table["body_Frame"],anchor="nw") # put canvas for Frame
    self.main_table["Scrollbar"] = tk.Scrollbar(self.main_table["Frame"],orient=tk.VERTICAL,command=self.main_table["Canvas"].yview) # Scrollbar for y-axis direction

    # set up things 
    self.main_table["head_Frame"].grid(row=0,column=0)
    self.main_table["Canvas"].grid(row=1,column=0,sticky=tk.N + tk.S)     # Expand y-axis direction 
    self.main_table["Scrollbar"].grid(row=1, column=1,sticky=tk.N + tk.S) # Expand y-axis direction
    self.main_table["Canvas"].config(yscrollcommand = self.main_table["Scrollbar"].set)

    columns=["商品","登録名","カテゴリー","金額","数量","割引","合計"] # Item for table header

    # display table header
    for i,column in enumerate(columns): 
      column_Label=tk.Label(self.main_table["head_Frame"],text=column)
      self.set_style(column_Label) # Set Style
      if i == 1 or i == 2: # Change width of label whether element of table body is tk.Entry or ttk.Combobox 
        column_Label.configure(padx=5)
        column_Label.grid(row=0,column=i,ipadx=6)
      else:
        column_Label.configure(padx=1)
        column_Label.grid(row=0,column=i)
    # For delete button head
    column_Label=tk.Label(self.main_table["head_Frame"],width=8,padx=3,bg="#3A3A3A") # Label for delete Button
    column_Label.grid(row=0,column=7,ipadx=17)

    # Make list of registered name
    # Connect category name(key) and item name(value)
    self.item_list=[] 
    for key,value in db.itemDB.items():
      self.item_list+=["---"+key+"---"]
      for item_name in value: 
        self.item_list+=[item_name]

    # Add each line with item, registered name, category etc...
    for i,item in enumerate(items): # For all items
      self.addItem(item=item["item"], registered_name=item["registered_name"], category=item["category"], price=item["price"], amount=item["amount"], discount=item["discount"])
    # Update self.main_table["Frame"] size because tableFrame is added many item and to change size of scrollbar in canvas
    self.main_table["Frame"].update_idletasks()

    # Include decide, add button and total label
    footer=tk.Frame(self.root)
    decide_Button=ttk.Button(footer,text="決定",command=self.decide) # Button for decide function
    add_Button=ttk.Button(footer,text="+",command=self.addItem)     # Button for add function
    shopping_results_Frame = tk.Frame(footer,relief=tk.SOLID)

    # Label for shopping results
    shopping_results_Label={
      "subtotal": tk.Label(shopping_results_Frame,text="小計"),
      "discount": tk.Label(shopping_results_Frame,text="割引"),
      # tax      = ttk.Combobox(shopping_results_Frame,value=["内税","外税"],width=3),
      "total"   : tk.Label(shopping_results_Frame,text="合計"),
    }
    # Value for shopping results
    self.shopping_results = {
      "subtotal" :tk.Label(shopping_results_Frame,text=0),
      "discount" :tk.Entry(shopping_results_Frame,width=5, justify=tk.RIGHT,bg="#4B4B4B"),
      # "tax"      :tk.Label(shopping_results_Frame,text=0),
      "total"    :tk.Label(shopping_results_Frame,text=0)
    }
    # add style setting and function
    footer.configure(width=self.main_table["Frame"].winfo_width(),height=200)
    # Include subtotal, discount, total to display
    shopping_results_Frame.configure(width=self.main_table["Frame"].winfo_width()/4,height=200)
    self.shopping_results["discount"].insert(0,self.discount_total)
    self.shopping_results["discount"].bind("<Enter>", self.display_discount_detail)
    self.shopping_results["discount"].bind("<Leave>", self.leave_discount_detail)
    self.shopping_results["discount"].bind("<Return>",self.calculateEvent)
    
    
    # shopping_results_Label["tax"].set(self.store[1])        
    # shopping_results_Label["tax"].bind("<<ComboboxSelected>>",lambda event: self.change_tax(event,shopping_results_Label["tax"].get()))
    # shopping_results_Label["tax"].bind("<<ComboboxSelected>>",self.change_tax)
    
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
    self.root.bind_class("Entry", "<FocusOut>", self.calculateEvent) # Add Event for Entry


  # def change_tax(self,event,kind_of_tax):
  #   """
  #   ## Description:


  #   Args:
  #       event (_type_): _description_
  #       kind_of_tax (_type_): _description_
  #   """
  #   self.store[1] = kind_of_tax
  #   self.calculate()
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
  
  # def caculate_result(self,event):
  #   self.shopping_results["subtotal"].configure(text=subtotal)                        # insert subtotal num and "yesn"
  #   discount = int(self.shopping_results["discount"].get())
  #   tax = int((subtotal-discount)*0.08)
  #   self.shopping_results["tax"].configure(text = tax)                        # insert tax num and "yesn"
  #   self.shopping_results["total"].configure(text = subtotal - discount + tax)                        # insert total num and "yesn"
  # def calculate(self,event): # execute when tk.Entry FocusOut
  #   print("aaa")
  #   self.calculate()              # call calculate function

  def category_event(self,event): # When mouse enter one_line["category_Combobox"]
    # subtotal = 0     # total 
    """
    ## Description:
      When selected or type category, match registered name to the category
    ## Args:
      `event`: what wedget is selected
    """
    elements=self.main_table["body_Frame"].winfo_children()  # get all item in tableFrame
    if event.widget.get() in db.itemDB.keys(): # selected category exist in DB
      elements[elements.index(event.widget)-1].configure(value=[value for value in db.itemDB[event.widget.get()]]) # change text of register item name 
    else: # New registered category name
      elements[elements.index(event.widget)-1].configure(value="")
    
  def calculateEvent(self,_event):
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
    subtotal = 0
    for i in range(int(len(elements)/8)):
      row_elements = elements[i*8:i*8+7]
      has_error = self.check_for_error(row_elements,i) # Item price, amount and discount are the right type
      if not(has_error):
        total_element = row_elements[6]
        total_element.delete(0,tk.END)                                           # Delete the value already entered
        total = int(row_elements[3].get())*int(row_elements[4].get())          # Get total from item price and amount
        if row_elements[5].get().isdecimal():                                 # Discount is only integer
          total -= int(row_elements[5].get())                                
        elif re.match("^[0-9]+%$",row_elements[5].get()):                    # Discount has "%"
          total = int(total*(1-int(re.match("^[0-9]+",row_elements[5].get()).group())/100))
        total_element.insert(0,total)         
    self.shopping_results["subtotal"].configure(text=subtotal)               # Insert subtotal
    # discount = int(self.shopping_results["discount"].get())
    # if self.store[1] == "内税":
    #   # tax = int(((subtotal-discount)/1.08)*0.08)
    #   # self.shopping_results["tax"].configure(text = tax)                        # insert tax num and "yesn"
    #   self.shopping_results["total"].configure(text = subtotal - discount)                        # insert total num and "yesn"
    # else:
    #   self.shopping_results["total"].configure(text = subtotal - discount)                        # insert total num and "yesn"
    #   # tax = int((subtotal-discount)*0.08)
    #   # self.shopping_results["tax"].configure(text = tax)                        # insert tax num and "yesn"
    #   # self.shopping_results["total"].configure(text = subtotal - discount + tax)                        # insert total num and "yesn"
  
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
      if i%8 == 0 and element.get() == "": # For item
          each_has_error = True
      elif (i%8 == 1 or i%8==2) and ("---" in element.get() or element.get() == ""): # For registered name and category
          each_has_error = True
      elif (i%8 == 3 or i%8 == 4) and not(element.get().isdecimal()): # For price and amount. Don't want to use not, but isalpha() method judges "◯" to be a number, and int() method causes an error, so I reject it.                                      
          each_has_error = True
      elif i%8 == 5 and not(element.get().isdecimal() or re.match("^[0-9]+%$",element.get())): # For discount
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
    # Where line is deleted
    elements = self.main_table["body_Frame"].winfo_children() 
    # Delete one line
    for i in range(8):
      elements[elements.index(event.widget)-i].destroy()
    self.calculate()     # Calculate
    self.update_region() # Update region

  def addItem(self,item="",registered_name="---",category="---",price="",amount="",discount=""):
    """
    ## Description
      Add item line when push "+"
    """
    " Get current row"
    if self.main_table["body_Frame"].winfo_children() != []:
      row = (self.main_table["body_Frame"].winfo_children())[-1].grid_info()["row"] 
    else:
      row=0
    one_line={}
    one_line = {
      "item_Entry": tk.Entry(self.main_table["body_Frame"]),
      "registered_name_Combobox": ttk.Combobox(self.main_table["body_Frame"],value=self.item_list),
      "category_Combobox": ttk.Combobox(self.main_table["body_Frame"],value=[value for value in db.itemDB.keys()]),
      "price_Entry": tk.Entry(self.main_table["body_Frame"]) ,
      "amount_Entry": tk.Entry(self.main_table["body_Frame"]),
      "discount_Entry": tk.Entry(self.main_table["body_Frame"]),
      "total_Entry": tk.Entry(self.main_table["body_Frame"]),
      "delete_Button": ttk.Button(self.main_table["body_Frame"],text="delete",width=7)
    }
    # Set Style
    self.set_style(one_line["item_Entry"])
    self.set_style(one_line["registered_name_Combobox"])
    self.set_style(one_line["category_Combobox"])
    self.set_style(one_line["price_Entry"])
    self.set_style(one_line["amount_Entry"])
    self.set_style(one_line["discount_Entry"])
    self.set_style(one_line["total_Entry"])
    one_line["category_Combobox"].bind("<<ComboboxSelected>>",self.category_event)                                        # set Enter Event
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
    one_line["item_Entry"].grid(row=row+1,column=0)
    one_line["registered_name_Combobox"].grid(row=row+1,column=1)
    one_line["category_Combobox"].grid(row=row+1,column=2)
    one_line["price_Entry"].grid(row=row+1,column=3)
    one_line["amount_Entry"].grid(row=row+1,column=4)
    one_line["discount_Entry"].grid(row=row+1,column=5)
    one_line["total_Entry"].grid(row=row+1,column=6)
    one_line["delete_Button"].grid(row=row+1,column=7)
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
    
    
    if re.search('(20[0-9]{2})/(1[0-2]|0[1-9]|[1-9])/([1-3][0-9]|[1-9])',self.header["date_Entry"].get()): # Check purchase date
      self.data=self.header["date_Entry"].get()
      self.header["date_Entry"].configure(highlightbackground="#565656") # Change Style
    else: # No entered name
      self.header["date_Entry"].configure(highlightbackground="red") # If enpty, change Style
      is_ok = False
      
    
    # Check whether has error in item table
    for i in range(int(len(elements)/8)):
      has_error = self.check_for_error(elements[i*8:i*8+7],i)
      if has_error:
        is_ok = False
        break
    # No error
    if is_ok == True:
      self.allItem=[] # To save for csv file
      for i in range(int(len(elements)/8)):
        row_elements = elements[i*8:i*8+7] # Get row elements
        oneLine = {"store":self.store[0],"date":self.date,"purpose":self.header["purpose_Combobox"].get(),"item": row_elements[0].get(),"registered_name": row_elements[1].get(),"category": row_elements[2].get(),"price":row_elements[3].get(),"amount":row_elements[4].get(),"discount":0,"total":0} # Do not inisialize "discount" and "total" now because the calculation formula changes depending on the type of discount.
        line_discount = row_elements[5].get()
        line_total = row_elements[6].get()
        if line_discount.isdecimal(): # Whether discount is included "%" or string or not
          oneLine["discount"] = int(line_discount)
        elif line_discount != "" and line_discount[-1] == "%" and re.match("[0-9]+",line_discount): # Included "%"
          total_without_discount=int(row_elements[3].get())*int(row_elements[4].get()) # Calcurate discount amount from "%"
          oneLine["discount"] = int(total_without_discount*int(re.match("[0-9]+",line_discount).group())/100) # Add dicount amount 
        elif line_discount == "":
          oneLine["discount"] = 0
        oneLine["total"] = line_total
        self.allItem.append(cp.copy(oneLine)) # Add row for all item with copy()
              
      # To has new category
      translator = Translator()
      self.new_category={}
      for item in self.allItem:
        if not(item["category"] in db.itemDB): # Whether category name is not included register category name
          en_text = translator.translate(item["category"], dest='en').text # Store category name in English
          # If en_text already exist, change name
          tmp_text = en_text
          i = 2
          while tmp_text in db.itemDB.values():
            tmp_text = en_text + str(i)
            i += 1
          en_text = tmp_text

          self.new_category[item["category"]] = "_".join(list(en_text.split())) # Add new category for dictionary
      self.root.destroy() # Destory GUI
      return 
