import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import japanize_matplotlib
# from  tkinter import ttk


class SeeGraph(tk.Frame):
  root = tk.Tk() # make display
  def __init__(self):
    super().__init__(self.root)
    self.root.title("Analyze")
    self.root.geometry("800x1000")
    # self.root.update_ideletaskes()
    # get data
    data = pd.read_csv('output.csv')
    # initialize
    total = data["金額"].sum()
    genre = data["ジャンル"].unique()
    totalenre=[]
    # get price by each genre
    for x in genre:
      totalenre.append(data.query("ジャンル==@x")["金額"].sum())

    # for figure
    frame = tk.Frame(self.master)
    fig = plt.Figure()
    # dtaw total with circle graph
    self.setCircleGraph(fig,totalenre,genre,total)
    
    canvas = FigureCanvasTkAgg(fig, frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()
    frame.pack()
    

    # month: 配列(data?,string?)
    # totalMonth: 配列(integer)

  def setCircleGraph(self,fig,sizes,labels,total):
    # creating instance
    instance=fig.subplots()
    # sort sizes and labels together 
    zip_list = zip(sizes,labels)
    sizes,labels = zip(*sorted(zip_list,reverse=True))
    # set font size
    plt.rcParams['font.size'] = 15
    # draw circle graph
    instance.pie(
      # data
      sizes,
      # price by each genre
      labels=list(map(lambda size : str(size)+'円' if size/total>=0.05 else "" ,sizes)),
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
  def rankingMonthByCategory(self,ago): # 何ヶ月前か
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


