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
    # self.root.update_ideletaskes()
    # get data
    self.data = pd.read_csv('output.csv')
    

    # for figure
    # frame = tk.Frame(self.master)
    self.frame = self.root
    # self.ranking_period_by_category(frame,"testERROR",{"from_month":9, "to_month":2})### 辞書の型がintなら、dateなら...
    self.ranking_period_by_category(self.root,9,2,"")### 辞書の型がintなら、dateなら...
    # self.ranking_period_by_category(frame,"testERROR",{"from_month":8})
    if 0:
      fig_pie = plt.Figure()
      fig_bar = plt.Figure()
      # dtaw total in pie chart
      self.set_total_in_pie_chart(fig_pie)
      # dtaw total by month in bar graph
      self.set_total_for_each_month_in_bar_chart(fig_bar)
      # declare FigureCanvasTkAgg to attach matplotlib for tkinter
      canvas_pie_chart = FigureCanvasTkAgg(fig_bar, self.frame)
      canvas_bar_graph = FigureCanvasTkAgg(fig_pie, self.frame)
      # change tk_widget and attach frame
      canvas_pie_chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)
      canvas_bar_graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)
      ### canvas_pie_chart.get_tk_widget().place(x = 100, y = 50)
      ### canvas_bar_graph.get_tk_widget().place(x = 200, y = 50)
      canvas_pie_chart.draw()
      canvas_bar_graph.draw()
    # frame.pack()
    # exit()
    

    # month: 配列(data?,string?)
    # totalMonth: 配列(integer)

  def set_total_in_pie_chart(self,fig):
    # initialize
    total = self.data["金額"].sum()
    genre = self.data["ジャンル"].unique()
    total_genre=[]
    # get price by each genre
    for x in genre:
      total_genre.append(self.data.query("ジャンル==@x")["金額"].sum())
    # creating instance
    instance=fig.subplots()
    # sort sizes and labels together 
    zip_list = zip(total_genre,genre)
    prices,labels = zip(*sorted(zip_list,reverse=True))
    # set font size
    plt.rcParams['font.size'] = 15
    # draw circle graph
    instance.pie(
      # data
      prices,
      # price by each genre
      labels=list(map(lambda price : str(price)+'円' if price/total>=0.05 else "" ,prices)),
      # setting
      counterclock=False,
      startangle=90,
      # display persentage
      autopct=lambda p:'{:.1f}%'.format(p) if p>=5 else '',
      # set position
      pctdistance=0.7,
      # make hollow at center
      wedgeprops={'width':0.6}
    )
    # display Usage Guide
    instance.legend(labels,fancybox=True,loc='center left',bbox_to_anchor=(1.0,0.6),fontsize=10)
    # total num at center
    instance.set_title('合計\n'+str(total)+'円', fontsize=15,y=0.45)
    # title for figure
    fig.suptitle('ジャンルごとの合計金額', fontsize=15)
  
  def set_total_for_each_month_in_bar_chart(self,fig):
    today = dt.date.today()
    first_day_in_this_month = dt.datetime(today.year,today.month,1)
    month_category_period=[]
    for i in range(5,-2,-1):
      month_category_period.append(first_day_in_this_month+ relativedelta(months=-i))
    # get data from 5 month ago to this month
    data = self.data[(month_category_period[0] <= pd.to_datetime(self.data["日付"])) & (pd.to_datetime(self.data["日付"]) < month_category_period[6])]
    month_category_name =[ str(i.month)+"月" for i in month_category_period[:-1]] #タイトルに範囲をかく
    total_month = []
    for i,x in enumerate(month_category_period[:-1]):
      total_month.append(self.get_data_select_period(x,month_category_period[i+1])["金額"].sum())
    # test_data=[100,300,200,300,400,400]
    # creating instance
    instance=fig.subplots()
    # set font size
    plt.rcParams['font.size'] = 15
    # draw bar grath
    rect = instance.bar(np.array([1, 2, 3, 4, 5, 6]), total_month, tick_label=month_category_name, align="center")

    # add annotation
    for one_rect in rect:
      height = one_rect.get_height()
      #annotationで文字やその位置を定義。文字を改行したいときは\nを挟む。
      instance.annotate('{}'.format(height),
                        xy=(one_rect.get_x() + one_rect.get_width() / 2, height-30),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=14
      )
    fig.suptitle('月ごとの合計金額', fontsize=15)  


  def ranking_period_by_category(self,frame,from_month,to_month,error): # 何ヶ月前か
    frame_period = tk.Frame(frame,height=100, width=350 ,bd=10)
    frame_period.pack()
    style = ttk.Style()
    style.theme_use('clam')
    entry_start_day = DateEntry(frame_period,showweeknumbers=False)
    entry_start_day.place(x=0, y=0)
    entry_end_day = DateEntry(frame_period,showweeknumbers=False)
    entry_end_day.place(x=150, y=0)
    label_tmp = tk.Label(frame_period, text="〜")
    label_tmp.place(x=130, y=0)
    self.seach_button = tk.Button(frame_period, text="検索", bg="coral", font=("Times New Roman", 10), command=lambda:self.click_day_decided(frame,entry_start_day,entry_end_day))
    self.seach_button.place(x=280, y=0)
    if isinstance(from_month, int) and isinstance(to_month, int):
      today = dt.date.today()
      first_day_in_this_month = dt.datetime(today.year,today.month,1)
    if isinstance(from_month, int) and isinstance(to_month, int):
      entry_start_day.set_date(first_day_in_this_month-relativedelta(months=from_month))
      entry_end_day.set_date(first_day_in_this_month-relativedelta(months=to_month)-relativedelta(days=1))
    else:
      entry_start_day.set_date(from_month)
      entry_end_day.set_date(to_month)

    if error != "":
      label_error = tk.Label(frame_period, text=error, foreground='red')
      label_error.place(relx = 0.5, y=35,anchor = tk.CENTER)
      return
    
    if isinstance(from_month, int) and isinstance(to_month, int):
      self.data_period = self.get_data_select_period(first_day_in_this_month-relativedelta(months=from_month),first_day_in_this_month-relativedelta(months=to_month))
    else:
      self.data_period = self.get_data_select_period(from_month,to_month)
    frame_ranking = tk.Frame(frame,height=100, width=500)
    tree = ttk.Treeview(frame_ranking)
    tree.pack()

    tree.bind("<<TreeviewSelect>>", self.select_record)
    tree['columns'] = (1,2,3)
    tree['show'] = 'headings'
    tree.column(1,anchor=tk.CENTER)
    tree.column(2,anchor=tk.CENTER)
    tree.column(3,anchor=tk.CENTER)
    tree.heading(1,text="ランキング",anchor=tk.CENTER)#command=lambda:self.sort_row(tree)
    tree.heading(2,text="ジャンル",anchor=tk.CENTER)#command=lambda:self.sort_row(tree)
    tree.heading(3,text="金額",anchor=tk.CENTER)#command=lambda:self.sort_row(tree)
    sorted_data_by_genre =self.data_period.groupby("ジャンル")[["金額"]].sum().sort_values('金額',ascending=False)    
    for i in range(10): # for文でのdataframeは遅いので
      if len(sorted_data_by_genre) <= i:
        break
      row = sorted_data_by_genre.iloc[i]
      tree.insert("","end",values=(str(i+1)+"位",row.name,row[0]))
    frame_ranking.pack()

    
    # 内部で表示を行う
    # categoryThisMonth
    # totalCategoryThisMonth
    return # 何も返さなくていいかな
  def click_day_decided(self,frame,from_date,to_date):
    from_date = dt.datetime.combine(from_date.get_date(),time())
    to_date = dt.datetime.combine(to_date.get_date(),time())
    error=""
    if from_date > to_date:
      error = "期間の順番に誤りがあります。"
    elif self.get_data_select_period(from_date,to_date).empty:
      error = "指定された期間中のレシートがありませんでした。"
    children = frame.winfo_children()
    for child in children:
      child.destroy()
    self.ranking_period_by_category(frame,from_date,to_date,error)
  
  def select_record(self,event):
    children = self.root.winfo_children()
    for i,child in enumerate(children):
      if i > 2:
        child.destroy()
    widget = event.widget
    record_id = widget.focus()
    record_values = widget.item(record_id, 'values')
    data_period = self.data_period[self.data_period['ジャンル'] == record_values[1]]
    self.data_by_genre(self.root,data_period)
    
    # print(data_period)

  def data_by_genre(self,frame,data): # 何ヶ月前か
    frame_data_by_genre = tk.Frame(frame,height=100, width=350 ,bd=10)
    tree = ttk.Treeview(frame_data_by_genre)
    tree.pack()

    # tree.bind("<<TreeviewSelect>>", self.select_record)
    tree['columns'] = (1,2,3,4)
    tree['show'] = 'headings'
    tree.column(1,anchor=tk.CENTER)
    tree.column(2,anchor=tk.CENTER)
    tree.column(3,anchor=tk.CENTER)
    tree.column(4,anchor=tk.CENTER)
    tree.heading(1,text="日付",anchor=tk.CENTER,command=lambda:self.sort_row(tree,data))
    tree.heading(2,text="場所",anchor=tk.CENTER,command=lambda:self.sort_row(tree,data))
    tree.heading(3,text="商品名",anchor=tk.CENTER,command=lambda:self.sort_row(tree,data))
    tree.heading(4,text="金額",anchor=tk.CENTER,command=lambda:self.sort_row(tree,data))
    for i in range(data.shape[0]): # for文でのdataframeは遅いので
      row = data.iloc[i]
      tree.insert("","end",values=(row[1],row[0],row[3],row[8]))
    frame_data_by_genre.pack()

  def sort_row(self,tree,data):
    # 押されたボタンのx座標の位置を取得
    x = tree.winfo_pointerx() - tree.winfo_rootx()
    # 一番上の要素を取得
    first_row = tree.item(tree.get_children()[0]) 
    # 押されたカラムの情報を取得
    column_clicked = {"name": tree.heading(tree.identify_column(x))["text"], "id": int(tree.column(tree.identify_column(x))["id"])-1}
    # 押されたカラムの一番上の要素を取得
    first_row_item_genre = first_row["values"][column_clicked["id"]]
    
    # データの削除
    tree.delete(*tree.get_children())
    
    # データを作成する
    sorted_data_by_genre=data.sort_values(column_clicked["name"],ascending=False)
    # sort後の内容が変わらなければ降順にする
    if first_row_item_genre == sorted_data_by_genre.iloc[0][column_clicked["name"]]:
      sorted_data_by_genre=data.sort_values(column_clicked["name"],ascending=True)
    # 表示
    for i in range(sorted_data_by_genre.shape[0]): # for文でのdataframeは遅いので
      row = sorted_data_by_genre.iloc[i]
      tree.insert("","end",values=(row[1],row[0],row[3],row[8]))
    
  
  def ByMonth(): # 月毎の情報のページ    
    # カテゴリごとのランキング(円グラフ)
    # 買ったもの一覧
    return 
  
  def suiiByItem(self): # 商品ごとの金額の推移をグラフ化する
    return

  
  def readCSV(self):
    # output.csvをpandasのデータ構造で返す
    return 
  def get_data_select_period(self,from_date,to_date):
    return self.data[(from_date <= pd.to_datetime(self.data["日付"])) & (pd.to_datetime(self.data["日付"]) < to_date)]

  def delete_all_data(self):
    self.frame.delete(*self.frame.get_children())



if __name__ == "__main__":
  # filename = filedialog.askopenfilename(
  #   title = "レシートを選択してください。",
  #   filetypes = [("Image file", ".png .jpg "),("PNG", ".png"), ("JPEG", ".jpg")], # ファイルフィルタ
  #   initialdir = "./" # 自分自身のディレクトリ
  #   )
  # if filename != "":
  #   main(filename)
  graph = SeeGraph()
  graph.mainloop()


