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

import common as co
page = "index_"


def get_month(df):
  date = pd.DataFrame(df["日付"].map(lambda x: x.split("-")[0] + "-" + x.split("-")[1]).unique(),columns=["年月"]).sort_values("年月")["年月"].tolist()
  pre_year = ""
  for i,x in enumerate(date):
    year = x.split("-")[0]
    month = re.sub("^0","",x.split("-")[1])
    if year == pre_year:
      date[i] = "　　　" + month + "月"
    else:
      date[i] = year + "年" + month + "月"
      pre_year = year
  return date

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
      dbc.Col([dcc.RadioItems(options=period_options,value=period_options[0]["value"],inline=True, id = f"{page}radio_period_standard"),
        dcc.Dropdown(options = [{"label": x, "value": x} for x in get_month(df)])  
      ]),
    ]),
  ],width=6),
  dbc.Col(width=6)
]),width=9, id = "main")])
