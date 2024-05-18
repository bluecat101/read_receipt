import dash
from dash import Input, Output, html, dcc, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date as d
import common as co

page = "no_receipt"
no_data = html.Div(html.P("データがありません。"))

dash.register_page(__name__)

# utility_billには月による期間があるので(ex:2ヶ月で〇〇円)、1ヶ月ごとにして月も計算する。
# 後に分解する前のデータを参照したいので、utility_bill.csvのindexを持たせておく。
df = co.processing_df_untility_bill(pd.read_csv('utility_bill.csv'),has_index = True)
df = co.add_categories_from_data(df)
# 左側のカテゴリーを作成する
new_categories = co.create_new_category(df, page)
# サイドバーを作成する
sidebar = co.create_col_sidebar(new_categories, page)
 
def create_row_period_specification():
  """ 
  ## Discription
    期間を指定するための表示を行う。
    期間は年、月を選ぶことができ、年はdataから指定できる年を取得する。
  ## Returns:
    `row (dbc.Row)`: 「年-月」の期間のRowを返す。
  """
  # dataから選択できる年を取得してセット
  options_year = [{"label":  year, "value": year} for year in df["年"].unique()]+[{"label":  d.today().year, "value": d.today().year}]
  # 月は1~12月の選択と全ての月の選択を可能にしている。
  options_month = [{"label": "1~12","value": "1~12"}]+[{"label":  month, "value": month} for month in range(1,13)]
  # styleのdirection:rtlはアラビア語を指定しており、右から左に要素が表示される設定にしている。
  year_dropdown = dcc.Dropdown(options = options_year,
                     value = d.today().year,
                     id = co.set_id("dropdown_year", page),
                     style={"width":"100px","direction": "rtl"})
  month_dropdown = dcc.Dropdown(options = options_month,
                     value = d.today().month,
                     id = co.set_id("dropdown_month", page),
                     style={"width":"100px","direction": "rtl"})
  row = dbc.Row([html.Div([html.Span("期間",className=""),year_dropdown,html.Span("年"),month_dropdown,html.Span("月")],className="d-flex justify-content-center align-items-center")])
  return row

def create_row_table_pie(year, month):
  """
  ## Description
    年と月からジャンルごとの金額を計算してtableで表示し、さらに円グラフでも表記する。

  ## Args:
    `year (int)`: 指定する年
    `month (int, string)`: 指定する月(基本的にint型であるが、全月を選択する際にstring型になる)

  ## Returns:
    `div(html.Div)`: 年と月の指定の範囲内のデータをリストと円グラフにして返す。
  """
  # 全ての月が対象であるかによって月を考慮するかを決める
  if month == "1~12":
    data = df[(df["年"] == year)]
  else:
    data = df[(df["年"] == year) & (df["月"] == month)]
  # 項目ごとの金額を取得する
  data = data.groupby("ジャンル")["金額"].sum().sort_values(ascending=False)
  # 対象のデータが無いときは文章を出して抜ける
  if data.empty:
    return no_data
  # tableを作成する
  table = html.Table([
            html.Thead([
              html.Tr([html.Th('項目',style={"width": "50%",}), html.Th('金額')])
            ]),
            html.Tbody([
              html.Tr([
                  html.Td(genre),
                  html.Td(total)
              ],)
              for genre, total in data.items()
            ])
          ], className='table table-hover table-striped table-sm sortable')
  # 円グラフを作成する
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

def create_table_for_fixed_costs(year, month):
  """
  ## Discription
    固定費についてのテーブルを作成する。
  ## Args:
      `year (int)`: 指定する年
      `month (int, string)`: 指定する月(基本的にint型であるが、全月を選択する際にstring型になる)

  ## Returns:
      `table(html.Table)`: 固定費に関するテーブルを返す
  """
  # 全ての月が対象であるかによって月を考慮するかを決める
  if month == "1~12":
    index = df[(df["年"] == year) & (df["分類"] == "固定費")].index.unique()
  else:
    index = df[(df["年"] == year) & (df["月"] == month) & (df["分類"] == "固定費")].index.unique()
  # df(期間_月によって分解したデータ)から元のcsvデータを取得するため
  df_untility_bill_origin = pd.read_csv('utility_bill.csv')
  # データがないとき
  if index.empty:
    return no_data
  # tableを作成する
  table = html.Table([
            html.Thead([
              html.Tr([html.Th('項目'), html.Th('金額'),html.Th("１ヶ月あたり")])
            ]),
            html.Tbody([
              html.Tr([
                html.Td(df_untility_bill_origin[i:i+1]["ジャンル"]),
                  html.Td(f"{df_untility_bill_origin.at[i,'金額']}円/{df_untility_bill_origin.at[i,'期間_月']}ヶ月"),
                  html.Td(f"{int(df_untility_bill_origin.at[i,'金額']/df_untility_bill_origin.at[i,'期間_月'])}円")
              ],)
              for i in index
            ])
          ], className='table table-hover table-striped table-sm sortable')
  return table

def create_fig_for_utility_bills(year):
  """
  ## Discription
    各公共費をyear
  ## Args:
    ` year (int)`: 指定する年

  ## Returns:
    `figs(html.Div[])`: 各公共費を棒グラフにして配列としてまとめて返す。
  """
  # データの取得
  data = df[(df["年"] == year) & ((df["分類"] == "公共費") | (df["分類"] == "変動費"))]
  # データがないとき
  if data.empty:
    return no_data
  figs = []
  # 公共費の種類だけ棒グラフを作成する
  for genre in data["ジャンル"].unique():
    data_genre = data[data["ジャンル"]==genre]
    fig_bar = px.bar(data_genre, x=data_genre["月"], y="金額",height = 200)
    fig_bar.update_layout(margin=dict(t=0))
    fig_bar.update_xaxes(tickvals=data_genre["月"])
    figs.append(html.Div([html.P(genre),dcc.Graph(figure=fig_bar)],style={}))
  return figs

# 表示を行う部分
layout = dbc.Row([sidebar,dbc.Col(
# 左側
dbc.Row([
  dbc.Col([
    dbc.Row([
      dbc.Col(co.create_button_for_hidden_sidebar(page),width=4),
      dbc.Col(create_row_period_specification(),width=8)
    ],style={"height":"50px"}),
    dbc.Row(id=co.set_id("table_pie_chart",page), style={"height":"350px"}), # 表と円グラフ
    dbc.Row(id = co.set_id("fixed_costs", page)), # 固定費
  ],width=6),
  # 右側
  dbc.Col([
    html.P("公共費"),
    html.Label([
      dcc.Input(
        id=co.set_id("input_year",page),
        placeholder=d.today().year,
        type="number",
        value= d.today().year,
        style={"width": "100px"}
      ),
      html.Span("年"),
    ],htmlFor="input_year"), # 右側において指定する年
    dbc.Row(id = co.set_id("figs_unility_bills",page) # 公共費の棒グラフ
  )],width=6,style={"height":"600px",'overflowY': 'scroll'}) # 何個棒グラフが表示されるかわからないため、スクロールの導入
]),width=9, id = "main")])


  
@callback(
  Output({"id": "table_pie_chart", "page": "no_receipt"},"children"),
  Input({"id": "dropdown_year", "page": "no_receipt"},"value"),
  Input({"id": "dropdown_month", "page": "no_receipt"},"value")
)
def update_chart_at_left_side(year, month):
  """
  ## Discription
    年と月を取得してそれに基づいて表と円グラフを作成する
  ## Args:
    `year(int)`: ドロップダウンで指定された年
    `month(int, string)`: ドロップダウンで指定された月(全月を選択した際にstring型になる)
  ## Returns
    `(dbc.Row)`: 全体の表と円グラフを含めたRowを返す
  """
  return create_row_table_pie(year, month)



@callback(
  Output({"id": "fixed_costs", "page": "no_receipt"},"children"),
  Input({"id": "dropdown_year", "page": "no_receipt"},"value"),
  Input({"id": "dropdown_month", "page": "no_receipt"},"value")
)
def update_chart_at_left_side(year, month):
  """
  ## Discription
    固定費の部分の表を作成する
  ## Args:
      `year (int)`: ドロップダウンで指定された年
      `month (int, string)`: ドロップダウンで指定された月(全月を選択した際にstring型になる)

  ## Returns:
      `(html.P,html.Div)`: 固定費のタグと固定費の表を返す
  """
  return [html.P("固定費"),create_table_for_fixed_costs(year, month)]


@callback(
  Output({"id": "figs_unility_bills", "page": "no_receipt"},"children"),
  Input({"id": "input_year", "page": "no_receipt"},"value"),
)
def update_chart_at_left_side(year):
  """
  ## Discription
    年を受け取って公共費の棒グラフを作成する
  ## Args:
      `year (int)`: ドロップダウンで指定された年
  ## Returns:
      `([html.Div])`: 公共費のジャンルごとの棒グラフを返す。
  """
  return create_fig_for_utility_bills(year)
