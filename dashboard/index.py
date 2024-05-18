import dash
from dash import Input, Output, html, dcc, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date as d
import numpy as np

import common as co

page = "index"
dash.register_page(__name__, path='/')
# レシートのある買い物のデータを取得
df_output = pd.read_csv('output.csv')
# 日付を年-月-日に変換
co.devide_date(df_output)

# レシートのない公共費、固定費等のデータを取得
df_untility_bill = co.processing_df_untility_bill(pd.read_csv('utility_bill.csv'))

def change_period(period):
  """
  ## Discription
    periodの値が"今月"、"先月"の場合に年、月に変換する
  ## Args:
      period (string): "今月"、"先月"、年-月のような形式で送られてくる
  ## Returns:
      period(string): "累計"以外の場合に年-月の形式で返す
  """
  today = d.today()
  if period == "今月":
    return f"{today.year}-{today.month}"
  elif period == "先月":
    if today.month == 1:
      return f"{today.year-1}-{12}" #1月 => 12月
    else:
      return f"{today.year}-{today.month-1}" # 2月 => 1月　月だけならtoday.month % 12 + 1 でも成り立つが1月の際に年も変える必要があるためifで分けている
  return period

def get_options_month():
  """
  ## Discription
    データから選択可能な年と月を取得してdropdownのoptionsの形で返す
  ## Returns:
      options([{label:,value:}]: dropdownのoptionsに使用する
  """
  df_1 = df_output[["年","月"]].drop_duplicates().sort_values(["年","月"])
  df_2 = df_untility_bill[["年","月"]].drop_duplicates().sort_values(["年","月"])
  df_date = pd.concat([df_1,df_2]).sort_values(["年","月"]) # レシートのあるデータと無いデータを結合する
  options = []
  pre_year = ""
  for _, (year,month) in df_date.iterrows():
    if year == pre_year: 
      options.append({"label":  f"　　　{month}月", "value": f"{year}-{month}"})
    else:
      options.append({"label": f"{year}年{month}月", "value": f"{year}-{month}"})
      pre_year = year
  return options

def processing_data():
  """
  ## Discription
    元データのジャンルから分類を取得して、それに基づいてデータを整形し2つのデータを結合して返す関数
  ## Retuens:
    `data(DataFrame)`: 元データのカテゴリから分類を取得した上で、データにカテゴリではなく分類を付与して返す
  """
  def change_category(genre):
    """
    ## Discription
      ジャンルから分類名を取得する
      設定されていない場合には分類名を「その他」にする
    ## Args:
        `genre(string)`: 分類名に変換するジャンル名
    ## Returns:
        `category(string)`: 引数のジャンル名から分類名を取得する関数
    """
    if genre in reverse_category: ## ジャンルに基づく分類名がある場合
      return reverse_category[genre]
    else:
      category["その他"] = genre
      reverse_category[genre] = "その他"
      return "その他"
  category = { # ジャンル名と分類名の対応
    "食費":["乳製品", "肉類", "お菓子", "主食", "飲み物", "野菜", "加工品", "惣菜", "果物", "調味料", "デザート", "魚類", "食べ物", "レトルト食品", "アイス", "乾物", "シリアル"],
    "外食":["外食"],
    "雑費":["その他"],
    "生活用品":["日用品"],
    "車"  :["車"],
    "例外":["例外"],
    "固定":["保険","通信費"],
    "公共":["水道代","ガス代","電気代"],
    "その他":[],
  }
  for genre_category in df_untility_bill.drop_duplicates(subset=['ジャンル'])[["ジャンル", "分類"]].values: # ジャンル名と分類名を追加
    category[genre_category[1]] = genre_category[0]
  reverse_category = {value: key for key, values in category.items() for value in values} # category{label:value}を{value: label}にする
  data = df_output.drop(columns=["場所", "日付", "取得した商品名", "商品名", "1個あたりの値段", "個数", "合計の割引", "日"]) 
  data["ジャンル"] = data["ジャンル"].apply(change_category) # ジャンルから分類名を取得する
  data = data.rename(columns={"ジャンル": "分類"}).reindex(columns=["年", "月", "目的", "分類", "金額"])
  data = pd.concat([data,df_untility_bill.drop(columns="ジャンル")]).reset_index(drop=True)
  return data
  


def create_table_and_pie_at_month(period, purpose):
  """
  ## Discription
    任意の月において分類ごとの合計を計算して表と円グラフにして返す
  ## Args:
    `period(string)`: 期限を選択(年-月、累計のどちらか)
    `purpose(string)`: 目的を選択

  ## Returns:
    `table_pie(dbc.Row)`: 表と円グラフをdbc.Rowにまとめて返す
  """
  data = processing_data()
  if period != "累計": # データを選択する
    year  = np.int64(period.split("-")[0])
    month = np.int64(period.split("-")[1])
    data = data[(data["年"] == year) & (data["月"] == month) & (data["目的"] == purpose)]
  else:
    data = data[data["目的"] == purpose]
  data = data.groupby("分類")["金額"].sum().sort_values(ascending=False)
  # 表の作成
  table = html.Table([
            html.Thead([
              html.Tr([html.Th('分類',style={"width": "50%",}), html.Th('金額')])
            ]),
            html.Tbody([
              html.Tr([
                  html.Td(category),
                  html.Td(total)
              ],)
              for category, total in data.items()
            ])
          ], className='table table-hover table-striped table-sm sortable')
  # 円グラフの作成
  fig_pie = go.Figure(
      data=[go.Pie(labels=list(data.index),
        values=data.values,
        hole=.3,
        marker=dict(colors=['#bad6eb', '#2b7bba']),
        textinfo = "label+percent",
        direction='clockwise'
        )])
  fig_pie.update_traces(textposition='inside')
  fig_pie.update_layout(
      width=300,
      height=300,
      paper_bgcolor='rgba(0,0,0,0)',
      uniformtext_minsize = 20,
      margin=dict(l=0, r=0, t=00, b=0),
      uniformtext_mode='hide',
      showlegend=False,
  )
  return dbc.Row([dbc.Col(table,width=4),dbc.Col(html.Div(dcc.Graph(figure=fig_pie)),width = 8)],style={"height":"300px"})

def create_table_and_pie_at_year(year, purpose):
  """
  ## Discription
    任意の年において分類ごとの合計を計算して表と円グラフにして返す
  ## Args:
    `year(int)`: 年を取得
    `purpose(int)`: 目的を取得

  ## Returns:
    `table_pie(dbc.Row)`: 表と円グラフをdbc.Rowにまとめて返す
  """
  data = processing_data()
  data = data[(data["年"] == year) & (data["目的"] == purpose)]
  data = data.groupby("分類")["金額"].sum().sort_values(ascending=False)
  # 表の作成
  table = html.Table([
            html.Thead([
              html.Tr([html.Th('分類',style={"width": "50%",}), html.Th('金額')])
            ]),
            html.Tbody([
              html.Tr([
                  html.Td(category),
                  html.Td(total)
              ],)
              for category, total in data.items()
            ])
          ], className='table table-hover table-striped table-sm sortable')
  # 円グラフの作成
  fig_pie = go.Figure(
      data=[go.Pie(labels=list(data.index),
        values=data.values,
        hole=.3,
        marker=dict(colors=['#bad6eb', '#2b7bba']),
        textinfo = "label+percent",
        direction='clockwise'
        )])
  fig_pie.update_traces(textposition='inside')
  fig_pie.update_layout(
      width=300,
      height=300,
      paper_bgcolor='rgba(0,0,0,0)',
      uniformtext_minsize = 20,
      margin=dict(l=0, r=0, t=00, b=0),
      uniformtext_mode='hide',
      showlegend=False,
  )
  return dbc.Row([dbc.Col(table,width=4),dbc.Col(html.Div(dcc.Graph(figure=fig_pie)),width = 8)],style={"height":"300px"})

def get_default_start_end(start, end):
  """
  ## Discription
    期間選択において初めの期間(今月、直近)と終わり(選択可能な最後の月)の期間のデフォルト値を元データから計算して返す関数
  ## Args:
    `start(string)`: 現在の初めの期間を取得
    `end(string)`: 現在の終わりの期間を取得

  ## Returns:
    `start, end(string, string)`: 初め、終わりの期間を返す
  """
  options_period = get_options_month() # 選択できる期間を取得
  if start is None:
    today = d.today()
    for x in options_period: # 今月もしくはその一つ前の月を探す(今月のデータがない場合には1つ前のデータとなる)
      if x["value"] < f"{today.year}-0":
        continue
      start = x["value"]
      break
    else:
      start =  options_period[0]["value"]
  if end is None:
    end = options_period[-1]["value"] # 期間の最後を取得する
  return (start, end)

def create_row_period_specification(start=None, end=None):
  """
  ## Discription
    dropdownの選択できる期間を指定する
  ## Args:
    `start(string)`: 選択している初めの期間を取得. Defaults to None.
    `end(string)`: . 選択している終わりの期間を取得.Defaults to None.

  ## Returns:
    `start, end, row(string, string, dbc.Row)`: 選択した初め、終わりの期間とそれによって変わったコンテンツのRowを返す
  """
  options_period = get_options_month()
  start, end = get_default_start_end(start, end)
  # 終わりの期間の表示されるlabelを制限
  options_end = list(filter(lambda x: x["value"] >= start, options_period))
  # 初めの期間
  start_dropdown = dcc.Dropdown(options = options_period,
                     value = start,
                     id = co.set_id("dropdown_start_period", page),
                     style={"width":"150px"})
  # 終わりの期間
  end_dropdown = dcc.Dropdown(options = options_end,
                     value = end,
                     id = co.set_id("dropdown_end_period", page),
                     style={"width":"150px"})
  row = dbc.Row([html.Div("期間",className="mx-auto text-center"),html.Br(),html.Div([start_dropdown,html.P("~"),end_dropdown],className="d-flex justify-content-center")])
  return (start, end, row)

def processing_data_for_fig_bar(start, end, purpose):
  """
  ## Discription
    棒グラフように期間、目的からデータを加工しデータを返す関数

  ## Args:
    `start(string)`: 初めの期間
    `end(string)`: 終わりの期間
    `purpose(string)`: 目的

  ## Returns:
    `data(DataFrame)`: 期間と目的のデータを分類ごとに合計したデータを返す
  """
  data = processing_data()
  data['年-月'] = data['年'].astype(str) + '-' + data['月'].astype(str)
  data = data[(data["年-月"] >= start) & (data["年-月"] <= end) & (data["目的"] == purpose)]
  data = data.groupby(["年-月","分類"])["金額"].sum()
  return data

def create_fig_bar_total_in_right_side(start=None, end=None, purpose=None):
  """
  ## Discription

  ## Args:
    `start(string)`: 初めの期間. Defaults to None.
    `end(string)`: 終わりの期間. Defaults to None.
    `purpose(string)`: 目的. Defaults to None.

  ## Returns:
    `fig_bar(px.bar)`: 棒グラフを作成して返す
  """
  start, end = get_default_start_end(start, end)
  if purpose is None:
    purpose = "家族"
  data = processing_data_for_fig_bar(start, end, purpose)
  
  data = data.reset_index().sort_values(by=['年-月', '金額'], ascending=[True, False]).set_index("年-月")
  if data.empty:
    print("データがありません。")
    return html.Div(html.P("データがありません"))
  fig_bar = px.bar(data, x=data.index, y="金額", color="分類")
  fig_bar.update_yaxes(tickformat=',d', ticksuffix=' 円')
  fig_bar.update_layout(margin=dict(t=0))
  return fig_bar

def create_fig_bar_rate_year_in_right_side(purpose,start=None, end=None):
  start, end = get_default_start_end(start, end)
  data = processing_data_for_fig_bar(start, end, purpose).reset_index()
  total_amounts = data.groupby('年-月')['金額'].sum()
  # 各グループ内の金額を合計で割って比率を計算し、新しい列として追加
  data['金額比率'] = data.apply(lambda row: row['金額'] / total_amounts[row['年-月']]*100, axis=1)
  data = data.sort_values(by=['年-月', '金額'], ascending=[True, False]).set_index("年-月")
  # "年-月"カラムをindexとする
  data = data.reset_index().sort_values(by=['年-月', '金額比率'], ascending=[True, False]).set_index("年-月")
  if data.empty:
    print("データがありません。")
    return
  # 棒グラフの作成
  fig_bar = px.bar(data, x=data.index, y="金額比率", color="分類")
  fig_bar.update_layout(margin=dict(t=0))
  return fig_bar


# サイドバー用のカテゴリーを追加
new_categories = co.create_new_category(df_output, page)
sidebar = co.create_col_sidebar(new_categories, page)

layout = dbc.Row([sidebar,dbc.Col(
dbc.Row([
  dbc.Col([
    dbc.Row([
      co.create_col_button_expense_purpose(page),
      dbc.Col([
        html.Br(),
        dcc.Dropdown(options = [{"label": x, "value": x} for x in ["今月", "先月", "累計"]]+get_options_month(),
                     value = "今月",
                     id = co.set_id("dropdown_period", page))
      ]),
    ]),
    dbc.Row(id = "fig_at_month",style={"height":"300px"}),
      dbc.Row([ # 年ごとのグラフを表示するための年入力欄
        html.Label([
          dcc.Input(
          id= co.set_id("input_year",page),
          placeholder=d.today().year,
          type="number",
          value= d.today().year,
          style={"width": "100px"}
          ),
          html.Span("年"),
        ],htmlFor="input_year"),
      ]),
    dbc.Row(id = "fig_at_year",style={"height":"300px"}),
  ],width=6),
  dbc.Col(dbc.Row( # 右側
    create_row_period_specification()[2], # この中にidが含まれるため、ここで作らないとidが見つからないとエラーが出る
    id="period_and_fig_in_right_side"
  ),width=6)
]),width=9, id = "main")])


@callback(
  Output("fig_at_month", "children"),
  Input({"id": "dropdown_period", "page": "index"},"value"),
  Input({"id": "dropdown_purpose", "page": "index"},"value"),
)
def update_fig_at_month(period, purpose):
  """
  ## Disctiption
    期間と目的を取得して月毎の分類ごとの金額を計算して表と円グラフで返す
  ## Args:
    `period (string)`: 期限を選択(年-月、累計のどちらか)
    `purpose (string)`: 目的を選択

  ## Returns:
    `table_pie(dbc.Row)`: 表と円グラフをdbc.Rowにまとめて返す
  """
  # periodが"今月","先月"の場合に変換する
  period = change_period(period)
  return create_table_and_pie_at_month(period, purpose)

@callback(
  Output("fig_at_year", "children"),
  Input({"id": "input_year", "page": "index"},"value"),
  Input({"id": "dropdown_purpose", "page": "index"},"value"),
)
def update_fig_at_year(year, purpose):
  """
  ## Disctiption
    年と目的を取得して月毎の分類ごとの金額を計算して表と円グラフで返す
  ## Args:
    `year(int)`: 年を取得
    `purpose(int)`: 目的を取得

  ## Returns:
    `table_pie(dbc.Row)`: 表と円グラフをdbc.Rowにまとめて返す
  """
  return create_table_and_pie_at_year(year, purpose)


@callback(
  Output("period_and_fig_in_right_side", "children"),
  Input({"id": "dropdown_start_period", "page": "index"},"value"),
  Input({"id": "dropdown_end_period", "page": "index"},"value"),
  Input({"id": "dropdown_purpose", "page": "index"},"value"),
)
def update_right_side_by_period(start, end, purpose):
  """
  ## Discprition
    右側において期間から合計と割合によるそれぞれの比率の棒グラフを返す
  ## Args:
    start(string): 初めの期間
    end(string): 終わりの期間
    purpose(string): 目的

  ## Returns:
    dbc.Row[]: 帰還指定のdropdownと棒グラフの合計と割合を返す
  """
  start, end, row_period = create_row_period_specification(start, end)
  return  [
    row_period,
    dbc.Row(dcc.Graph(figure = go.Figure(create_fig_bar_total_in_right_side(start, end,purpose))),style={"height":"300px"}),
    dbc.Row(dcc.Graph(figure = go.Figure(create_fig_bar_rate_year_in_right_side(purpose, start, end))),style={"height":"300px"}),
    ]

