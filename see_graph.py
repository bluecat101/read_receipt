import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import japanize_matplotlib
import datetime as dt
from dateutil.relativedelta import relativedelta
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
    frame = tk.Frame(self.master)
    fig_pie = plt.Figure()
    fig_bar = plt.Figure()
    # dtaw total in pie chart
    self.set_total_in_pie_chart(fig_pie)
    # dtaw total by month in bar graph
    self.set_total_for_each_month_in_bar_chart(fig_bar)
    # declare FigureCanvasTkAgg to attach matplotlib for tkinter
    canvas_pie_chart = FigureCanvasTkAgg(fig_bar, frame)
    canvas_bar_graph = FigureCanvasTkAgg(fig_pie, frame)
    # change tk_widget and attach frame
    canvas_pie_chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas_bar_graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    # canvas_pie_chart.get_tk_widget().place(x = 100, y = 50)
    # canvas_bar_graph.get_tk_widget().place(x = 200, y = 50)
    canvas_pie_chart.draw()
    canvas_bar_graph.draw()
    frame.pack()
    

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
  def rankingMonthByCategory(self,fig,ago): # 何ヶ月前か
    # 内部で表示を行う
    # categoryThisMonth
    # totalCategoryThisMonth
    return # 何も返さなくていいかな
  
  def ByMonth(self): # 月毎の情報のページ
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


