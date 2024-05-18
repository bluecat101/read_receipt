from dash import ALL, Input, Output,State, ctx, html, dcc, callback
from dash import dash as ddash
import dash_bootstrap_components as dbc
import pandas as pd

purpose = ["家族", "父", "全て"]
purpose_options =[{"label": x,"value": x} for x in purpose]

changed_categories = ["その他", "例外", "日用品", "車"]
def set_id(id, page):
  return {"id": id, "page": page}


def devide_date(df):
  df["年"] = df["日付"].str.split("-").apply(lambda row: int(row[0]))
  df["月"] = df["日付"].str.split("-").apply(lambda row: int(row[1]))
  df["日"] = df["日付"].str.split("-").apply(lambda row: int(row[2]))

def add_categories_from_data(df):
  df_output = pd.read_csv("output.csv")
  added_df = df_output[df_output["ジャンル"].isin(changed_categories)]
  added_df = added_df[added_df["目的"] == "家族"]
  devide_date(added_df)
  added_df = added_df.drop(columns=["場所", "日付", "取得した商品名", "商品名", "1個あたりの値段", "個数", "合計の割引","日"])
  added_df[["期間_月", "index","分類"]] = [1, -1, "変動費"]
  added_df = added_df.reindex(columns = ["index", "年", "月", "目的", "ジャンル","分類","金額","期間_月"]).set_index("index") 
  return pd.concat([df, added_df])

def delete_categories_from_data(df):
  return df[~df["ジャンル"].isin(changed_categories)] 

def create_new_category(df, page):
  new_categories = []
  for _ in range(4):
    new_categories.append(get_category(len(new_categories),df,page))
  return new_categories

def get_category(i, df, page, options=None):
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

def create_col_sidebar(categories, page):
  
  return dbc.Col(
          html.Div(
          [
                    html.P("独自のカテゴリー"),
                    dbc.Row(categories,id="new_categories",style={"height":"550px","display": "block"},className="overflow-auto"),
                    dbc.Row(dbc.Button(html.I(className= "bi bi-plus-circle-dotted"),id = set_id("button_add_new_category",page))),
                    dcc.Store(id="hidden_score", data={'hidden': False}),
                    ],
                    id="div_for_hidden_statue"),
                    className="bg-info opacity-25",
                    id="sidebar",
                    width=3
                  )

def create_button_for_hidden_sidebar(page):
  return dbc.Button(html.I(className= "bi bi-arrow-left-square-fill",id = "icon_display_hide"),style={"width": "40px"} ,id = set_id("button_display_hide", page))

def create_col_button_expense_purpose(page):
  return dbc.Col([
          dbc.Row([
            create_button_for_hidden_sidebar(page),
# dbc.Button(html.I(className= "bi bi-arrow-left-square-fill",id = "icon_display_hide"),style={"width": "40px"} ,id = set_id("button_display_hide", page)),
            dbc.Row(id = set_id("expense", page))]),
          dcc.Dropdown(
            id = set_id("dropdown_purpose", page),
            options = purpose_options,
            value = purpose_options[0]["value"],
            style={"width": "100px"}
          ),],
        width = 6)


def processing_df_untility_bill(df, has_index = None):
  if has_index is None:
    has_index = False
  purpose = "家族"
  array_for_new_df = []
  for i,(year, month, genre, category, total, unit) in df.iterrows():
    if unit == 1:
      array_for_new_df.append([year, month, purpose, genre, category, total])
      if has_index:
        array_for_new_df[-1].insert(0,i)
      continue
    for j in range(unit):
      new_month = month+j-1
      new_year = year + int(new_month/12)
      new_month = new_month %12+1
      array_for_new_df.append([new_year, new_month, purpose, genre, category, int(total/unit)])
      if has_index:
        array_for_new_df[-1].insert(0,i)

  if has_index:
    return pd.DataFrame(array_for_new_df, columns=["index", "年", "月", "目的", "ジャンル", "分類", "金額"]).set_index("index")
  else:
    return pd.DataFrame(array_for_new_df, columns=["年", "月", "目的", "ジャンル", "分類", "金額"])



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
  if ctx.triggered_id is None:
    return ddash.no_update
  data["hidden"] = not data["hidden"]
  class_name= "bi bi-arrow-right-square-fill" if data["hidden"] else "bi bi-arrow-left-square-fill"
  width_sidebar = 0 if data["hidden"] else 3
  width_main = 12 if data["hidden"] else 9
  return data["hidden"], data, class_name, width_sidebar,width_main
