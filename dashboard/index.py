import dash
from dash import Dash, ALL, Input, Output,State, ctx, html, dcc, callback,MATCH
from dash import dash as ddash
from dash._utils import AttributeDict
import dash_bootstrap_components as dbc
import dash_table
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
from datetime import datetime as dt,date as d
import calendar as cal
from dateutil.relativedelta import relativedelta
import dash_defer_js_import as dji
import random
import regex as re
import numpy as np

import common as co
page = "index"
df_output = pd.read_csv('output.csv')
co.devide_date(df_output)
df_untility_bill = pd.read_csv('utility_bill.csv')

def get_month(df):
  date = pd.DataFrame(df["日付"].map(lambda x: x.split("-")[0] + "-" + x.split("-")[1]).unique(),columns=["年月"]).sort_values("年月")["年月"].tolist()
  options = []
  pre_year = ""
  for x in date:
    year = x.split("-")[0]
    month = re.sub("^0","",x.split("-")[1])
    if year == pre_year:
      options.append({"label":  "　　　" + month + "月", "value": year + "-" + month})
    else:
      options.append({"label": year + "年" + month + "月", "value": year + "-" + month})
      pre_year = year
  return options

def proessing_data():
  def change_category(genre):
    if genre in reverse_category:
      return reverse_category[genre]
    else:
      category["その他"] = genre
      reverse_category[genre] = "その他"
      return "その他"
  category = {
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
  for genre_category in df_untility_bill.drop_duplicates(subset=['ジャンル'])[["ジャンル", "分類"]].values:
    category[genre_category[1]] = genre_category[0]
  reverse_category = {value: key for key, values in category.items() for value in values}
  data = df_output.drop(columns=["場所", "日付", "取得した商品名", "商品名", "1個あたりの値段", "個数", "合計の割引", "日"])
  data["ジャンル"] = data["ジャンル"].apply(change_category)
  data = data.rename(columns={"ジャンル": "分類"}).reindex(columns=["年", "月", "目的", "分類", "金額"])
  data = pd.concat([data,df_untility_bill.drop(columns="ジャンル")]).reset_index(drop=True)
  return data
  


def create_table_and_pie_at_month(period, purpose):
  data = proessing_data()
  # 月を指定
  if period != "累計":
    year  = np.int64(period.split("-")[0])
    month = np.int64(period.split("-")[1])
    data = data[(data["年"] == year) & (data["月"] == month) & (data["目的"] == purpose)]
  else:
    data = data[data["目的"] == purpose]
  data = data.groupby("分類")["金額"].sum().sort_values(ascending=False)
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
  fig_pie = go.Figure(
      data=[go.Pie(labels=list(data.index),
        values=data.values,
        hole=.1,
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
      # textinfo='none',  # ラベルを非表示にする
      uniformtext_mode='hide',
      showlegend=False,
  )
  return dbc.Row([dbc.Col(table,width=4),dbc.Col(html.Div(dcc.Graph(figure=fig_pie)),width = 8)],style={"height":"300px"})



def change_period(period):
  today = d.today()
  if period == "今月":
    return str(today.year) + "-" + str(today.month)
  elif period == "先月":
    if today.month == 1:
      return str(today.year-1) + "-12" #1月 => 12月
    else:
      return str(today.year) + "-" + str(today.month-1) # 2月 => 1月　月だけならtoday.month % 12 + 1 でも成り立つが1月の際に年も変える必要があるためifで分けている
  return period
dash.register_page(__name__, path='/')
df = pd.read_csv('output.csv')
co.devide_date(df)

period  = ["今月", "先月", "累計"]

period_options =[{"label": x,"value": x} for x in period]

new_categories = []
for _ in range(7):
  new_categories.append(co.get_category(len(new_categories),df,page))

sidebar = co.create_col_sidebar(new_categories, page)

layout = dbc.Row([sidebar,dbc.Col(
dbc.Row([
  dbc.Col([
    dbc.Row([
      co.create_col_button_expense_purpose(page),
      dbc.Col([
        html.Br(),
        dcc.Dropdown(options = [{"label": x, "value": x} for x in ["今月", "先月", "累計"]]+get_month(df_output),
                     value = "今月",
                     id = co.set_id("dropdown_period", page))
      ]),
    ]),
    dbc.Row(id = "fig_at_month",style={"height":"300px"}),
    dbc.Row(id = "fig_at_year",style={"height":"300px"}),
    # dbc.Row(html.Div(dcc.Graph(figure=fig_pie)),style={"height":"300px"},className="bg-success")
  ],width=6),
  dbc.Col(dbc.Row(
    [
    dbc.Row(style={"height":"300px"},className="bg-primary"),
    dbc.Row(style={"height":"300px"},className="bg-secondary")]
  ),width=6)
]),width=9, id = "main")])


@callback(
  Output("fig_at_month", "children"),
  Input({"id": "dropdown_period", "page": "index"},"value"),
  Input({"id": "dropdown_purpose", "page": "index"},"value"),
)
def update_fig_at_month(period, purpose):
  period = change_period(period)
  return create_table_and_pie_at_month(period, purpose)
