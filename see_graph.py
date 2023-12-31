
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.ttk as ttk
from helper.tkcalendar import Calendar, DateEntry 
# from tkcalendar import Calendar, DateEntry 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import japanize_matplotlib
import datetime as dt
from dateutil.relativedelta import relativedelta
import sys
from datetime import datetime, date, time
# from  tkinter import ttk


class SeeGraph(tk.Frame):
  root = tk.Tk() # make display
  def __init__(self):
    super().__init__(self.root)
    self.root.title("Analyze")
    self.root.geometry("800x1000")
    # get data
    self.data = pd.read_csv('output.csv')
    # root display
    self.total_by_genre()

  # display totals price by genre in pie chart
  def total_by_genre(self):
    # title
    label_tmp = tk.Label(self.root, text="ジャンルごとの合計金額",font=("MSゴシック", "20", "bold"))
    label_tmp.pack()
    
    # frame for figure
    frame_figure = tk.Frame(self.root,height=400, width=350 ,bd=10)
    frame_figure.pack()

    # pie chart
    fig_pie = self.set_total_in_pie_chart()                           # setting pie chart
    canvas_pie_chart = FigureCanvasTkAgg(fig_pie, frame_figure)       # to draw in tkinter
    canvas_pie_chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # how to place
    canvas_pie_chart.draw()                                           # draw piechart

    # button for next page
    button_to_period = tk.Button(self.root, text="期間ごとに見る", command=self.see_period)
    button_to_period.pack()


  def set_total_in_pie_chart(self):
    # initialize
    total = self.data["金額"].sum()
    genre = self.data["ジャンル"].unique()
    total_genre=[]

    # get price by each genre
    for x in genre:
      total_genre.append(self.data[self.data["ジャンル"]==x]["金額"].sum())

    # setting figure
    fig = plt.Figure()          # make object 
    instance_fig=fig.subplots() # make instance
    # sort sizes and labels together 
    zip_list = zip(total_genre,genre)
    prices,labels = zip(*sorted(zip_list,reverse=True)) # sort by price
    # set font size
    plt.rcParams['font.size'] = 15

    # draw circle graph
    instance_fig.pie(
      prices,                                                                                 # data
      labels=list(map(lambda price : str(price)+'円' if price/total>=0.05 else "" ,prices)),  # price by each genre
      counterclock=False,                                                                     # counterclockwise
      startangle=90,                                                                          # rotate 
      autopct=lambda p:'{:.1f}%'.format(p) if p>=5 else '',                                   # display persentage
      pctdistance=0.7,                                                                        # set position
      wedgeprops={'width':0.6}                                                                # make hollow at center
    )
    # setting Usage Guide
    instance_fig.legend(
      bbox_to_anchor=(1.55, 1),   # set relative position
      loc='upper left',           # set position
      borderaxespad=0,            # set distance between anchor and loc frame 
      fontsize=18                 # fontsize
    )

    # display Usage Guide
    instance_fig.legend(labels,fancybox=True,loc='center left',bbox_to_anchor=(1.0,0.6),fontsize=10)
    # total num at center
    instance_fig.set_title('合計\n'+str(total)+'円', fontsize=15,y=0.45)
    return fig

  # bar chart  
  def set_total_period_in_bar_chart(self,from_date,to_date):
    # get some months between from_date and to_date
    year = to_date.year - from_date.year                       # get some years
    from_month = dt.datetime(from_date.year,from_date.month,1) # get from_date's first days of the month
    period = to_date.month-from_date.month+year*12+1           # get some months 
    # make month array
    month_category_period=[from_date] # init 
    for i in range(1,period+1):
      month_category_period.append(from_month+ relativedelta(months=i))
    
    # make x memori name
    month_category_name =[ str(i.month)+"月" if i.month!=1 else str(i.month)+"月     "+str(i.year)+"年" for i in month_category_period] #タイトルに範囲をかく
    # get totals by month
    total_by_month = []
    for i,x in enumerate(month_category_period[:-1]):
      total_by_month.append(self.get_data_select_period(x,month_category_period[i+1])["金額"].sum())
    
    # setting figure
    plt.rcParams['figure.subplot.bottom'] = 0.15 # make space at bottom
    fig = plt.Figure()                           # make figure object
    instance=fig.subplots()                      # make instance
    # set font size
    
    # draw bar grath
    rect = instance.bar(np.array([i for i in range(len(total_by_month))]), total_by_month, tick_label=self.tategaki(month_category_name[:-1]), align="center")#
    
    # add annotation
    for one_rect in rect:
      height = one_rect.get_height()  # get height
      instance.annotate('{}'.format(height),
                        xy=(one_rect.get_x() + one_rect.get_width() / 2, height-30), # position for annotation
                        xytext=(0, 3),              # position for text 
                        textcoords="offset points", # position for figure
                        ha='center',                # horizontalalignment
                        va='bottom',                # verticalalignment
      )
    # other setting
    instance.set_xticklabels(self.tategaki(month_category_name[:-1]), fontsize=10)
    fig.suptitle('月ごとの合計金額', fontsize=15)  
    return fig
  
  # make label name vertical (insert '\n')
  def tategaki(self,labels):
    labels_tategaki =[]
    for label in labels:
      index = label.find("月")
      if label.find("年") != -1:
        # find "年"(== "1月")
        labels_tategaki.append(label[:index]+'\n'+label[index:index+1]+'\n'+label[index+1:index+2]+'\n'+label[index+2:])
      elif index == 2:
        # don't find "年" and month is 2 length(=="10月"or"11月"or"12月")
        labels_tategaki.append(label[:1]+'\n'+label[1:index]+'\n'+label[index:])
      else:
        # don't find "年" and month is 1 length(=="1月"~"9月")
        labels_tategaki.append(label[:index]+'\n'+label[index:])      
    return labels_tategaki
  

  # display category in any period in tree chart
  def ranking_period_by_category(self,from_date,to_date,error):
    # set frame 
    frame_period = tk.Frame(self.sub_frame,height=100, width=350 ,bd=10)
    frame_period.pack()
    # set option for DateEntry
    style = ttk.Style()
    style.theme_use('clam')
    # from Date
    entry_start_day = DateEntry(frame_period,showweeknumbers=False) # make object
    entry_start_day.set_date(from_date)                             # set date
    entry_start_day.place(x=0, y=0)                                 # put 
    # to Date
    entry_end_day = DateEntry(frame_period,showweeknumbers=False) # make object
    entry_end_day.set_date(to_date)                               # set date
    entry_end_day.place(x=150, y=0)                               # put 
    # set label
    label_tmp = tk.Label(frame_period, text="〜")
    label_tmp.place(x=130, y=0)
    # set button for search
    self.seach_button = tk.Button(frame_period, text="検索", bg="coral", font=("Times New Roman", 10), command=lambda:self.click_day_decided(entry_start_day,entry_end_day))
    self.seach_button.place(x=280, y=0)
    
    # has error
    if error != "":
      # display error
      label_error = tk.Label(frame_period, text=error, foreground='red')
      label_error.place(relx = 0.5, y=35,anchor = tk.CENTER)
      return
    
    # get data in the period
    self.data_period = self.get_data_select_period(from_date,to_date)
    
    # setting tree
    frame_ranking = tk.Frame(self.sub_frame,height=100, width=500)
    frame_ranking.pack()
    tree = ttk.Treeview(frame_ranking)                  # make object
    tree.pack()                                         # put
    tree.bind("<<TreeviewSelect>>", self.select_record) # add function of selection
    # set columns
    tree['columns'] = (1,2,3)                           
    tree.column(1,anchor=tk.CENTER)                      
    tree.column(2,anchor=tk.CENTER)                     
    tree.column(3,anchor=tk.CENTER)                     
    # set heading
    tree['show'] = 'headings'                           
    tree.heading(1,text="ランキング",anchor=tk.CENTER)
    tree.heading(2,text="ジャンル",anchor=tk.CENTER)
    tree.heading(3,text="金額",anchor=tk.CENTER)
    # sort data
    sorted_data_by_genre =self.data_period.groupby("ジャンル")[["金額"]].sum().sort_values('金額',ascending=False)    
    # insert 10 genres
    for i in range(10):
      if len(sorted_data_by_genre) <= i:
        break
      row = sorted_data_by_genre.iloc[i]
      tree.insert("","end",values=(str(i+1)+"位",row.name,row[0]))
    return
  
  # whether period is correct
  def check_period(self,from_date,to_date):
    error=""
    if from_date > to_date: # wrong the period
      error = "期間の順番に誤りがあります。"
    elif self.get_data_select_period(from_date,to_date).empty: # no data in the period
      error = "指定された期間中のレシートがありませんでした。"
    return error
  
  # update display content when search button is clicked
  def click_day_decided(self,from_date,to_date):
    # convert type of date
    from_date = dt.datetime.combine(from_date.get_date(),time())
    to_date = dt.datetime.combine(to_date.get_date(),time())
    # get error message
    error= self.check_period(from_date,to_date)
    # update display content
    self.see_period(from_date,to_date,error)
  
  # show detail list when one row is clicked
  def select_record(self,event):
    # get serected row
    widget = event.widget
    record_id = widget.focus()
    record_values = widget.item(record_id, 'values')
    # get data
    data_period = self.data_period[self.data_period['ジャンル'] == record_values[1]]
    self.data_by_genre(data_period)


  # display detail list in tree chart
  def data_by_genre(self,data,status=None):
    # delete show detail
    children = self.sub_frame.winfo_children()
    for i,child in enumerate(children):
      if i > 2:
        child.destroy()
    if status is None:
      status = False
    # setting 
    frame_data_by_genre = tk.Frame(self.sub_frame,height=100, width=350 ,bd=10)
    frame_data_by_genre.pack()

    frame_summarize = tk.Frame(self.sub_frame,height=100, width=350 ,bd=10)
    frame_summarize.pack()
    is_summarize = tk.BooleanVar()
    checkbutton_summarize = tk.Checkbutton(frame_summarize,text="まとめて表示する", variable=is_summarize)
    checkbutton_summarize.grid(row = 0, column = 1)
    button_summarize = tk.Button(frame_summarize,text="再表示",command=lambda:self.data_by_genre(data,is_summarize.get()))
    button_summarize.grid(row = 0, column = 2)
    is_summarize.set(status)

    tree = ttk.Treeview(frame_data_by_genre)
    tree.pack()

    # set columns
    tree['columns'] = (1,2,3,4)
    tree.column(1,anchor=tk.CENTER)
    tree.column(2,anchor=tk.CENTER)
    tree.column(3,anchor=tk.CENTER)
    tree.column(4,anchor=tk.CENTER)
    # set heading
    tree['show'] = 'headings'
    tree.heading(1,text="日付",anchor=tk.CENTER,command=lambda:self.sort_row(tree,data))
    tree.heading(2,text="場所",anchor=tk.CENTER,command=lambda:self.sort_row(tree,data))
    tree.heading(3,text="商品名",anchor=tk.CENTER,command=lambda:self.sort_row(tree,data))
    tree.heading(4,text="金額",anchor=tk.CENTER,command=lambda:self.sort_row(tree,data))
    # whether summarizing display or each display
    if status:
      # summarizing display
      column = ["日付","場所","商品名","金額"]
      items = data['商品名'].unique().tolist() # get all item
      new_data = pd.DataFrame(index=[], columns=column) # make dataframe for display

      for item in items:
        record=[]
        data_by_item = data[data['商品名'] == item] # select by item
        date = data_by_item.iloc[0]["日付"] # get start date
        if date != data_by_item.iloc[-1]["日付"]: # start and end date are different
          date += "-"+data_by_item.iloc[-1]["日付"] # add end date
        place_list = data_by_item["場所"].unique().tolist() # get each place
        place =",".join(place_list) # concat place
        sum = data_by_item.sum()["金額"] # get total proce
        # add date for record
        record.append(date)
        record.append(place)
        record.append(item)
        record.append(sum)
        add_data = pd.DataFrame(data = [record], index=[1], columns=column)
        new_data = pd.concat([new_data,add_data],ignore_index=True)
      
      # insert item
      for i in range(new_data.shape[0]):
        row = new_data.iloc[i]
        tree.insert("","end",values=(row[0],row[1],row[2],row[3]))
    else:
      # insert item
      for i in range(data.shape[0]):
        row = data.iloc[i]
        tree.insert("","end",values=(row[1],row[0],row[3],row[8]))

  # sort data when heading of detail list is clicked
  def sort_row(self,tree,data):
    # get x of the clicked heading
    x = tree.winfo_pointerx() - tree.winfo_rootx()
    # get information of clicked heading column
    column_clicked = {"name": tree.heading(tree.identify_column(x))["text"], "id": int(tree.column(tree.identify_column(x))["id"])-1}
    # get top item in the row
    first_row_item_genre = tree.item(tree.get_children()[0]) ["values"][column_clicked["id"]]
    
    # delete tree data
    tree.delete(*tree.get_children())
    
    # sort data
    sorted_data_by_genre=data.sort_values(column_clicked["name"],ascending=False)
    # whether the sorted data and showed data are some 
    if first_row_item_genre == sorted_data_by_genre.iloc[0][column_clicked["name"]]:
      # change sort order
      sorted_data_by_genre=data.sort_values(column_clicked["name"],ascending=True)
    # insert items
    for i in range(sorted_data_by_genre.shape[0]):
      row = sorted_data_by_genre.iloc[i]
      tree.insert("","end",values=(row[1],row[0],row[3],row[8]))

  # see data in any period 
  def see_period(self,from_date=None,to_date=None,error=""):
    # set default
    if (from_date is None) and (to_date is None):
      from_date = self.get_first_day(6)
      to_date = self.get_last_day(0)
    
    # get error message
    error = self.check_period(from_date,to_date)
    # delete 
    self.delete_all_data()

    # get size of frrot
    root_x = int(re.split("[,x+]",self.root.geometry())[0])
    root_y = int(re.split("[,x+]",self.root.geometry())[1])
    # make canvas for scrollbar
    canvas = tk.Canvas(self.root)
    canvas.pack(expand=True, fill=tk.BOTH)
    # make frame for attach widgets    
    self.sub_frame = tk.Frame(canvas)
    self.sub_frame.pack(expand=True, fill=tk.BOTH)
    # make scrollbar
    scrollbar = tk.Scrollbar(canvas, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side = tk.RIGHT,fill=tk.Y)

    # setting scrollbar for canvas
    canvas.configure(scrollregion=(0, 0, root_x, root_y*2))
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # attach canvas to use sub_frame
    canvas.create_window((0, 0), window=self.sub_frame, anchor="nw", width=root_x, height=root_y*2)
    
    # get data
    self.data_period=pd.DataFrame()
    # display category in tree chart
    self.ranking_period_by_category(from_date,to_date,error)

    # display bar chart
    if error == "":
      fig_bar = self.set_total_period_in_bar_chart(from_date,to_date)
      canvas_bar_graph = FigureCanvasTkAgg(fig_bar, self.sub_frame)
      canvas_bar_graph.get_tk_widget().pack()
      canvas_bar_graph.draw()
    return
  
  # get first day of the month
  def get_first_day(self,ago):
    # get today
    today = dt.date.today()
    # get first day of today's month
    first_day_in_this_month = dt.datetime(today.year,today.month,1)
    return first_day_in_this_month-relativedelta(months=ago-1)
  
  # get last day of the month
  def get_last_day(self,ago):
    # get today
    today = dt.date.today()
    # get first day of today's month
    first_day_in_this_month = dt.datetime(today.year,today.month,1)
    return first_day_in_this_month-relativedelta(months=ago-1)-relativedelta(days=1)
  
  # get data in the period
  def get_data_select_period(self,from_date,to_date):
    return self.data[(from_date <= pd.to_datetime(self.data["日付"])) & (pd.to_datetime(self.data["日付"]) < to_date)]
  
  # delete all content in root frame
  def delete_all_data(self):
    children = self.root.winfo_children()
    for child in children:
      child.destroy()
  
  def readCSV(self):
    # output.csvをpandasのデータ構造で返す
    return 
  
  def ByMonth(): # 月毎の情報のページ    
    # カテゴリごとのランキング(円グラフ)
    # 買ったもの一覧
    return 
  
  def suiiByItem(self): # 商品ごとの金額の推移をグラフ化する
    return

if __name__ == "__main__":
  graph = SeeGraph()
  graph.mainloop()


