import dash
from dash import Dash, ALL, Input, Output,State, ctx, html, dcc, callback
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


purpose = ["家族", "父", "全て"]
purpose_options =[{"label": x,"value": x} for x in purpose]

def get_category(i, df, page, options=None):
  page = page[:-1]
  if options is None:
    options = [{"label":x,"value":x} for x in df["ジャンル"].unique().tolist()]
  id_for_input = {"id": "category_name", "index": i,"page": page}
  id_for_dropdown = {"id": "selected_category", "index": i,"page": page}
  id_for_delete_button = {"id": "delete_category", "index": i,"page": page}
  category_name = "カテゴリー"+str(i+1)
  category = dbc.Row([ 
              dbc.Col([
                dbc.Row([
                  dbc.Col(html.Span('カテゴリー名:  '),width = 7),
                  dbc.Col(dcc.Input(
                    id = id_for_input,
                    placeholder=category_name,
                    value = "",
                    style={"width": "170%"}
                  ),style={"margin-left": "-20%"},
                width = 5)]),
                dbc.Row(
                  dcc.Dropdown(
                    id = id_for_dropdown,
                    options = options,
                    multi = True,
                    value = None,
                  )
                )],width=10)
                ,
              dbc.Col(dbc.Button(html.I(className= "bi bi-x-circle"),className="rounded-circle" ,id = id_for_delete_button,style={"margin":"10px 0 0 0"}),width=2)
             ],style={"padding": "10px 0 10px 5px"})
  return category
def set_id(id, page):
  return {"id": id, "page": page}

def create_col_sidebar(categories, page):
  page = page[:-1]
  return dbc.Col(
          html.Div(
          [
                    html.P("独自のカテゴリー"),
                    dbc.Row(categories,id="new_categories",style={"height":"650px","display": "block"},className="overflow-auto"),
                    dbc.Row(dbc.Button(html.I(className= "bi bi-plus-circle-dotted"),id = set_id("button_add_new_category",page))),
                    dcc.Store(id="hidden_score", data={'hidden': False}),
                    ],
                    id="div_for_hidden_statue"),
                    className="bg-info opacity-25",
                    id="sidebar",
                    width=3
                  )

def create_col_button_expense_purpose(page):
  page = page[:-1]
  return dbc.Col([
          dbc.Row([
            dbc.Button(html.I(className= "bi bi-arrow-left-square-fill",id = "icon_display_hide"),style={"width": "40px"} ,id = set_id("button_display_hide", page)),
            dbc.Row(id = "expense")]),
          dcc.Dropdown(
            id = set_id("dropdown_purpose", page),
            options = purpose_options,
            value = purpose_options[0]["value"],
            style={"width": "100px"}
          ),],
        width = 6)


# ページ遷移時のcallback
@callback(Output("container","children"),Input('url', 'pathname'))
def display_page(pathname):
  print(pathname)
  if pathname == "/":
    return dash.dash.no_update
  elif pathname == "/food":
    return dash.dash.no_update
  elif pathname == "/no_receipt_item":
    return dash.dash.no_update
   


@callback(
          Output("div_for_hidden_statue", "hidden"),
          Output("hidden_score", "data"),
          Output("icon_display_hide", "className"),
          Output("sidebar", "width"),
          Output("main", "width"),
          Input({"id": "button_display_hide", "page": ALL}, "n_clicks"),
          State("hidden_score", "data"), 
          )
def sidebar(_,data):
#   # n_clicksはどんどん加算されていくので、起動時の実行かどうかしか判定できない
#   # ctx.triggered_idには押されたinputが入るためこっちの方が確実かな
  print(ctx.triggered_id)
  if ctx.triggered_id is None:
    return ddash.no_update
  data["hidden"] = not data["hidden"]
  class_name= "bi bi-arrow-right-square-fill" if data["hidden"] else "bi bi-arrow-left-square-fill"
  width_sidebar = 0 if data["hidden"] else 3
  width_main = 12 if data["hidden"] else 9
  return data["hidden"], data, class_name, width_sidebar,width_main