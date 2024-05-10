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

def change_period(period):
  today = d.today()
  if period == "今月":
    return f"{today.year}-{today.month}"
  elif period == "先月":
    if today.month == 1:
      return f"{today.year-1}-{12}" #1月 => 12月
    else:
      return f"{today.year}-{today.month-1}" # 2月 => 1月　月だけならtoday.month % 12 + 1 でも成り立つが1月の際に年も変える必要があるためifで分けている
  return period

def get_month(df):
  df_date = df[["年","月"]].drop_duplicates().sort_values(["年","月"])
  # if start is not None:
  #   df_date = df_date[(df_date["年"] > start.split("-")[0]) | ((df_date["年"] > start.split("-")[0]) & (df_date["月"] > start.split("-")[1]))]
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
  data = processing_data()
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
      # textinfo='none',  # ラベルを非表示にする
      uniformtext_mode='hide',
      showlegend=False,
  )
  return dbc.Row([dbc.Col(table,width=4),dbc.Col(html.Div(dcc.Graph(figure=fig_pie)),width = 8)],style={"height":"300px"})

def create_table_and_pie_at_year(year, purpose):
  data = processing_data()
  # 月を指定
  data = data[(data["年"] == year) & (data["目的"] == purpose)]
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
  options_period = get_month(df_output)
  if start is None:
    today = d.today()
    for x in options_period:
      if x["value"] < f"{today.year}-0":
        continue
      start = x["value"]
      break
    else:
      start =  options_period[0]["value"]
  if end is None:
    end = options_period[-1]["value"]
  return (start, end)

def create_row_period_specification(start=None, end=None):
  options_period = get_month(df_output)
  start, end = get_default_start_end(start, end)
  options_end = list(filter(lambda x: x["value"] >= start, options_period))
  start_dropdown = dcc.Dropdown(options = options_period,
                     value = start,
                     id = co.set_id("dropdown_start_period", page),
                     style={"width":"150px"})
  end_dropdown = dcc.Dropdown(options = options_end,
                     value = end,
                     id = co.set_id("dropdown_end_period", page),
                     style={"width":"150px"})
  row = dbc.Row([html.Div("期間",className="mx-auto text-center"),html.Br(),html.Div([start_dropdown,html.P("~"),end_dropdown],className="d-flex justify-content-center")])
  return (start, end, row)

def processing_data_for_fig_bar(start, end, purpose):
  data = processing_data()
  data['年-月'] = data['年'].astype(str) + '-' + data['月'].astype(str)
  data = data[(data["年-月"] >= start) & (data["年-月"] <= end) & (data["目的"] == purpose)]
  data = data.groupby(["年-月","分類"])["金額"].sum()
  return data

def create_fig_bar_total_in_right_side(start=None, end=None, purpose=None):
  start, end = get_default_start_end(start, end)
  if purpose is None:
    purpose = "家族"
  data = processing_data_for_fig_bar(start, end, purpose)
  
  data = data.reset_index().sort_values(by=['年-月', '金額'], ascending=[True, False]).set_index("年-月")
  if data.empty:
    print("データがありません。")
    return
  fig_bar = px.bar(data, x=data.index, y="金額", color="分類")
  fig_bar.update_yaxes(tickformat=',d', ticksuffix=' 円')
  fig_bar.update_layout(margin=dict(t=0))
  return fig_bar

def create_fig_bar_rate_year_in_right_side(start=None, end=None, purpose=None):
  start, end = get_default_start_end(start, end)
  if purpose is None:
    purpose = "家族"
  data = processing_data_for_fig_bar(start, end, purpose).reset_index()
  total_amounts = data.groupby('年-月')['金額'].sum()
  # 各グループ内の金額を合計で割って比率を計算し、新しい列として追加
  data['金額比率'] = data.apply(lambda row: row['金額'] / total_amounts[row['年-月']]*100, axis=1)
  data = data.sort_values(by=['年-月', '金額'], ascending=[True, False]).set_index("年-月")
  
  data = data.reset_index().sort_values(by=['年-月', '金額比率'], ascending=[True, False]).set_index("年-月")
  if data.empty:
    print("データがありません。")
    return
  fig_bar = px.bar(data, x=data.index, y="金額比率", color="分類")
  fig_bar.update_layout(margin=dict(t=0))
  return fig_bar

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
    dbc.Row([
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
    # dbc.Row(html.Div(dcc.Graph(figure=fig_pie)),style={"height":"300px"},className="bg-success")
  ],width=6),
  dbc.Col(dbc.Row(
    [
    create_row_period_specification()[2],
    dbc.Row(dcc.Graph(figure = go.Figure(create_fig_bar_total_in_right_side())),style={"height":"300px"}),
    dbc.Row(dcc.Graph(figure = go.Figure(create_fig_bar_rate_year_in_right_side())),style={"height":"300px"}),
    ],
    id="period_and_fig_in_right_side"
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

@callback(
  Output("fig_at_year", "children"),
  Input({"id": "input_year", "page": "index"},"value"),
  Input({"id": "dropdown_purpose", "page": "index"},"value"),
)
def update_fig_at_year(year, purpose):
  return create_table_and_pie_at_year(year, purpose)


@callback(
  Output("period_and_fig_in_right_side", "children"),
  Input({"id": "dropdown_start_period", "page": "index"},"value"),
  Input({"id": "dropdown_end_period", "page": "index"},"value"),
  Input({"id": "dropdown_purpose", "page": "index"},"value"),
)
def update_right_side_by_period(start, end, purpose):
  start, end, row_period = create_row_period_specification(start, end)
  return  [
    row_period,
    dbc.Row(dcc.Graph(figure = go.Figure(create_fig_bar_total_in_right_side(start, end,purpose))),style={"height":"300px"}),
    dbc.Row(dcc.Graph(figure = go.Figure(create_fig_bar_rate_year_in_right_side(start, end,purpose))),style={"height":"300px"}),
    ]

