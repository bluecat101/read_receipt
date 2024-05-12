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

page = "no_receipt"

dash.register_page(__name__)

df_untility_bill = co.processing_df_untility_bill(pd.read_csv('utility_bill.csv'),has_index = True)
# data = df_untility_bill
# co.add_purpose_and_total_by_month(df_untility_bill)
new_categories = []
for _ in range(7):
  new_categories.append(co.get_category(len(new_categories),df_untility_bill,page))

sidebar = co.create_col_sidebar(new_categories, page)

def create_row_period_specification():
  options_year = [{"label":  year, "value": year} for year in df_untility_bill["年"].unique()]+[{"label":  d.today().year, "value": d.today().year}]
  options_month = [{"label": "1~12","value": "1~12"}]+[{"label":  month, "value": month} for month in range(1,13)]
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
  if month == "1~12":
    data = df_untility_bill[(df_untility_bill["年"] == year)]
  else:
    data = df_untility_bill[(df_untility_bill["年"] == year) & (df_untility_bill["月"] == month)]
  data = data.groupby("ジャンル")["金額"].sum().sort_values(ascending=False)
  if data.empty:
    return
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

def create_table_for_fixed_costs(year, month):
  if month == "1~12":
    index = df_untility_bill[(df_untility_bill["年"] == year) & (df_untility_bill["分類"] == "固定")].index.unique()
  else:
    index = df_untility_bill[(df_untility_bill["年"] == year) & (df_untility_bill["月"] == month) & (df_untility_bill["分類"] == "固定")].index.unique()
  # data = data.groupby("ジャンル")["金額"].sum().sort_values(ascending=False)
  df_untility_bill_origin = pd.read_csv('utility_bill.csv')
  # return 
  if index.empty:
    return
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



layout = dbc.Row([sidebar,dbc.Col(
dbc.Row([
  dbc.Col([
    dbc.Row([
      dbc.Col(co.create_button_for_hidden_sidebar(page),width=4),
      dbc.Col(create_row_period_specification(),width=8)
    ],style={"height":"50px"}, className = "bg-danger"),
    dbc.Row(id=co.set_id("table_pie_chart",page), style={"height":"350px"}),
    dbc.Row(html.P("固定費"),id = co.set_id("fixed_costs", page)),
    # dbc.Row([
    #   html.Label([
    #     dcc.Input(
    #     id= co.set_id("input_year",page),
    #     placeholder=d.today().year,
    #     type="number",
    #     value= d.today().year,
    #     style={"width": "100px"}
    #     ),
    #     html.Span("年"),
    #   ],htmlFor="input_year"),
        # ]),
    # dbc.Row(id = "fig_at_year",style={"height":"300px"}),
    # dbc.Row(html.Div(dcc.Graph(figure=fig_pie)),style={"height":"300px"},className="bg-success")
  ],width=6),
  dbc.Col(dbc.Row(
    [
    # create_row_period_specification()[2],
    # dbc.Row(dcc.Graph(figure = go.Figure(create_fig_bar_total_in_right_side())),style={"height":"300px"}),
    # dbc.Row(dcc.Graph(figure = go.Figure(create_fig_bar_rate_year_in_right_side())),style={"height":"300px"}),
    ],
    id="period_and_fig_in_right_side"
),width=6)
]),width=9, id = "main")])


# @callback(
#   Output({"id": "expense", "page": "food"},"children"),
#   Input({"id": "dropdown_purpose", "page": "food"},"value"),
#   Input({"id": "button_display_hide", "page": "food"}, "n_clicks"),
#   State("hidden_score", "data"), 
# )
# def update_genre_chart_at_left_side(*_args): # 上のコールバックでselected_periodを更新しているため
#   total = df_untility_bill["金額"].sum()
#     # print(data["ジャンル"].unique())
#   expense_html = html.Div(
#             html.P("支出: "+str(total)),
#           )
  
@callback(
  Output({"id": "table_pie_chart", "page": "no_receipt"},"children"),
  Input({"id": "dropdown_year", "page": "no_receipt"},"value"),
  Input({"id": "dropdown_month", "page": "no_receipt"},"value")
)
def update_chart_at_left_side(year, month):
  row = create_row_table_pie(year, month)
  if row is None:
    return ddash.no_update
  return row



@callback(
  Output({"id": "fixed_costs", "page": "no_receipt"},"children"),
  Input({"id": "dropdown_year", "page": "no_receipt"},"value"),
  Input({"id": "dropdown_month", "page": "no_receipt"},"value")
)
def update_chart_at_left_side(year, month):
  table = create_table_for_fixed_costs(year, month)
  if table is None:
    return ddash.no_update
  return [html.P("固定費"),table]


