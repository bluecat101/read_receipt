from dash import dash, Dash, ALL, Input, Output,State, ctx, html, dcc, callback
# import copy
# import dash
# import dash_core_components as dcc
import dash_bootstrap_components as dbc
# import dash_html_components as html
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

period  = ["今月", "先月", "今年", "昨年", "累計"]
purpose = ["家族", "父", "全て"]
selected_period = period[0]
data = pd.DataFrame()
self_categories = {}
# 付け加え　色
# colors = {
#   'background': 'lightblue  ',
#   'background1': 'limegreen  ',
#   'text': '#FFFFFF'
# }

df = pd.read_csv('output.csv')
# data = df
df["年"] = df["日付"].str.split("-").apply(lambda row: int(row[0]))
df["月"] = df["日付"].str.split("-").apply(lambda row: int(row[1]))
df["日"] = df["日付"].str.split("-").apply(lambda row: int(row[2]))

dashboard = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP,'./assets/stylesheet.css', dbc.icons.BOOTSTRAP])
def get_data_for_period(data = None,period = None,):
  today = d.today()
  if data is None:
    data = df
  if period is None:
     period = "今月"
  if period == "今月":
    return data[(data["年"] == today.year) & (data["月"] == today.month)]
    # start_day = dt(today.year,today.month,1)
    # end_day = dt(today.year,today.month,1)+relativedelta(months=1)
  elif period == "先月":
    if today.month == 1:
      return data[(data["年"] == today.year-1) & (data["月"] == 12)] #1月 => 12月
    else:
      return data[(data["年"] == today.year) & (data["月"] == today.month - 1)] # 2月 => 1月　月だけならtoday.month % 12 + 1 でも成り立つが1月の際に年も変える必要があるためifで分けている
  elif period == "今年":
    return data[(data["年"] == today.year)] 
  elif period == "昨年":
    return data[(data["年"] == today.year-1)]
  else:
    # 配列で受け取る[start_day,end_day
    start_day = dt.strptime(period[0],"%Y-%m-%d")
    end_day = dt.strptime(period[1],"%Y-%m-%d")
  return data[(start_day <= pd.to_datetime(data["日付"])) & (pd.to_datetime(data["日付"]) <= end_day)]

def get_data_for_purpose(data = None,purpose = None,):
  today = d.today()
  if data is None:
    data = df
  if purpose is None:
     purpose = "全て"

  if purpose == "家族" or purpose == "父":
    return data[data["目的"] == purpose]
  elif purpose == "全て":
    return data
  

period_options =[{"label": x,"value": x} for x in period]
purpose_options =[{"label": x,"value": x} for x in purpose]
def make_category(i):
  id_for_input = {"type": "input", "index": i}
  id_for_dropdown = {"type": "dropdown", "index": i}
  id_for_delete_button = {"type": "button", "index": i}
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
                    options = [{"label":x,"value":x} for x in df["ジャンル"].unique().tolist()],
                    multi = True,
                    value = None,
                  )
                )],width=10)
                ,
              dbc.Col(dbc.Button(html.I(className= "bi bi-x-circle"),className="rounded-circle" ,id = id_for_delete_button,style={"margin":"10px 0 0 0"}),width=2)
             ],style={"padding": "10px 0 10px 5px"})
  return category
new_categories = []
for _ in range(4):
  new_categories.append(make_category(len(new_categories)))
sidebar = dbc.Col(
  html.Div(
  [
            html.P("独自のカテゴリー"),
            dbc.Row(new_categories,id="new_categories",style={"height":"650px","display": "block"},className="overflow-auto"),
            dbc.Row(dbc.Button(html.I(className= "bi bi-plus-circle-dotted"),id = 'button_add_new_category')),
            dcc.Store(id='hidden_score', data={'hidden': False}),
            ],
            id="div_for_hidden_statue"),
            className="bg-info opacity-25",
            id="sidebar",
            width=3
          )
dashboard.layout = dbc.Container([
  dbc.Row([sidebar,dbc.Col(
dbc.Row([
    dbc.Col([
      dbc.Row([
        dbc.Col([
          dbc.Row([
            dbc.Button(html.I(className= "bi bi-arrow-left-square-fill",id = "icon_display_hide"),style={"width": "40px"} ,id = "button_display_hide"),
            dbc.Row(id = "expense")]),
          dcc.Dropdown(
            id = 'dropdown_purpose',
            options = purpose_options,
            value = purpose_options[0]["value"],
            style={"width": "100px"}
          ),],
        width = 6),
        dbc.Col([dcc.RadioItems(options=period_options,value=period_options[0]["value"],inline=True, id = "radio_period_standard"),
          dcc.DatePickerRange(id='calender_period_custom',
            max_date_allowed = d.today(),
            #  start_date = d(d.today().year,d.today().month,1),
            #  end_date= d.today()
            start_date = d(d.today().year,d.today().month-1,1),
            end_date = d(d.today().year,d.today().month-1,31),
          )
         
      ]),
      ]),
      html.Div(id="genre_pie_chart_and_ranking_table"),
      dbc.Row([
      html.Label([
        dcc.Input(
        id="input_year",
        placeholder="2024",
        type="number",
        value= d.today().year,
        style={"width": "100px"}
        ),
        html.Span("年"),
      ],htmlFor="input_year"),
        ]),
      dcc.Graph(
        id = "year_bar",
        figure = go.Figure(layout=dict(template='plotly')) # 初期化しないと最初のcallでエラーが出る
        ,style={"height": "370px"}
      ),
    ],width=6),
    dbc.Col([ ## 右側
      dbc.Row(dcc.RadioItems(options=[{"label":x,"value":x} for x in ["週","月"]],inline=True, id="type_of_x_axis")),
      dbc.Row(dcc.Graph(
        id = "genre_bar_chart"
        ,style={"height": "370px"}
      ),),
      dbc.Row([
          dbc.Col(html.Span("ジャンル: "),width="auto",class_name="py-atuo mx-0 px-0"),
          dbc.Col(dcc.Dropdown(
            id = 'dropdown_genre',
            options =[{"label": genre, "value": genre } for genre in data["ジャンル"].unique()] if not(data.empty) else [],
          style={"width": "150px"} 
          ),width="auto",className="mx-0 px-2"),
          dbc.Col(html.Span("まとめて表示する: "),width="auto",class_name="py-atuo mx-0 px-2"),
          dbc.Col(dcc.Dropdown(
            id = 'dropdown_summary',
            options = [{"label":x,"value":x} for x in ["","日付", "場所", "商品名"]],
            style={"width": "100px"}
          ),width="auto",className="mx-0 px-0"),
          dbc.Col(
            html.Button("決定",id = 'button_decide',
            style={"width": "100px","margin":"auto", 'display':'inline-block'},
           
          ), width="auto",className="mx-0 px-2")
        ]),
        html.Div(id="item_table")
      # ])
    ],
    width=6)
  ]),width=9


  ,id="main")])
  
],style={"margin":"0"})

def genre_pie_chart_at_left_side(data,is_hidden_sidebar):
  fig_pie = go.Figure(
      data=[go.Pie(labels=list(data.index),
        values=data.values,
        hole=.1,
        marker=dict(colors=['#bad6eb', '#2b7bba']),
        textinfo = "label+percent",
        direction='clockwise'
        )])
  fig_pie.update_layout(
      width=300,
      height=250,
      paper_bgcolor='rgba(0,0,0,0)',
      uniformtext_minsize = 10,
      uniformtext_mode='hide',
      showlegend=False,
  )
  if is_hidden_sidebar:
    fig_pie.update_layout(margin=dict(l=100, r=0, t=10, b=10),)    
  else:
    fig_pie.update_layout(margin=dict(l=0, r=0, t=10, b=10),)
  fig_pie.update_traces(textposition='inside')
  return fig_pie


def genre_ranking_table_at_left_side(data):
  ranked_data = data.sort_values(ascending=False).reset_index()
  ranked_data.index += 1  # ランキングは1から始まる
  ranked_data2 = data.sort_values(ascending=False).reset_index()
  ranked_data2["順位"] = [i for i in range(1,len(ranked_data2)+1)]
  
  table = html.Table([
            html.Thead([
              html.Tr([html.Th('順位',style={"width": "25%",}), html.Th("ジャンル",style={"width": "50%"}), html.Th('金額')])
            ]),
            html.Tbody([
              html.Tr([
                  html.Td(rank),
                  html.Td(genre),
                  html.Td(total)
              ],)
              for rank, (genre, total) in ranked_data.iterrows()
            ])
          ]
          , className='table table-hover table-striped table-sm sortable')
  return table
def get_period_from_word(period):
  today = d.today()
  this_year  = today.year
  this_month = today.month
  last_year  = this_year - 1
  last_month = (today - relativedelta(months=1)).month
  if period == "今月":
    start_date = "{0}-{1}-1".format(this_year,this_month)
    end_date = "{0}-{1}-{2}".format(this_year,this_month,cal.monthrange(this_year,this_month)[1])
  elif period == "先月":
    start_date = "{0}-{1}-1".format(this_year,last_month)
    end_date = "{0}-{1}-{2}".format(this_year,last_month,cal.monthrange(this_year,last_month)[1])
  elif period == "今年":
    start_date = "{0}-1-1".format(this_year)
    end_date = "{0}-12-31".format(this_year)
  elif period == "昨年":
    start_date = "{0}-1-1".format(last_year)
    end_date = "{0}-12-31".format(last_year)
  elif period == "累計":
    start_date = df.sort_values("日付").iloc[0]["日付"] # df.sort_values("日付")["日付"]だとindex番号を参照してしまいsort後の結果を得られない(sortによってindex番号も一緒にずれており、index番号を取得するともとの部分を取得していることと変わらないため)
    end_date = str(today)
  return [start_date,end_date]

# def get_triggered_element_for_period(*args):
#   if ctx.triggered:
#     trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] # "triggered_name.value"という形で格納されているのでtriggeredの部分を取得
#     # print(ctx.triggered_id)
#     if trigger_id == "radio_period_standard":
#       # return get_period_from_word(args[0])
#       return args[0]
#   #   elif trigger_id == "calender_period_custom":
#   #     return [args[1],args[2]]
#   return selected_period # default値
def set_data(start_date, end_date, purpose):
  def classify_category(genre):
    for label, category in self_categories.items():
      if genre in category:
        return label
    return genre # 見つからなかった場合、区分をジャンル名を同じにして返す
  # print("self_categories",self_categories)
  global data
  data= df.copy()
  data["ジャンル"] = data["ジャンル"].apply(classify_category) # ジャンルの名前を変更
  data = get_data_for_period(get_data_for_purpose(data = data, purpose = purpose), period = [start_date, end_date]) #dfから取得

def update_self_categories(labels, value):
  labels = ["カテゴリー"+str(i+1) if x == "" else x for i,x in enumerate(labels)]# 未入力のlabelを変換(カテゴリーn)する
  value  = [x if x is not None else [] for x in value]
  global self_categories
  self_categories = {labels[i]: value[i] for i in range(len(new_categories))} # 追加だと過去のが残ってしまう

@callback(
    # Output("sidebar", "width"),
          Output("div_for_hidden_statue", "hidden"),
          Output("hidden_score", "data"),
          Output("icon_display_hide", "className"),
          Output("sidebar", "width"),
          Output("main", "width"),
          # Output("genre_pie_chart", "style"),
          Input("button_display_hide", "n_clicks"),
          State("hidden_score", "data"), 
          )
def sidebar(n_clicks,data):
  if n_clicks is None:
    return dash.no_update
  data["hidden"] = not data["hidden"]
  class_name= "bi bi-arrow-right-square-fill" if data["hidden"] else "bi bi-arrow-left-square-fill"
  width_sidebar = 0 if data["hidden"] else 3
  width_main = 12 if data["hidden"] else 9
  # update_genre_chart_at_left_side(data)
  return data["hidden"], data, class_name, width_sidebar,width_main

@dashboard.callback(
    Output({'type':'dropdown', 'index':ALL}, 'options'),
    Input({'type':'dropdown', 'index':ALL}, 'value'),
    State("calender_period_custom","start_date"),
    State("calender_period_custom","end_date"),
    State("dropdown_purpose","value"),
    State({'type':'input', 'index':ALL},"value"),
)
def update_categories(value,start_date, end_date, purpose, labels):
    if ctx.triggered_id is not None:
        # この時点で押されたnew_categoryに値が格納されているので、押されたindexを取得してそれだけ例外で押された要素等から生成する必要なdし
        genre_no_selected = df["ジャンル"].unique().tolist()
        for i in range(len(new_categories)):
          # Noneは値が挿入されていないことを意味するので、空の配列とみなす
          if value[i] is None:
            value[i] = []
          genre_no_selected = [x for x in genre_no_selected if x not in value[i]]
        options = [] # return用
        for i in range(len(new_categories)):
          # genre_no_selected + 各new_categoryの今の値をoprionsとする。もし今の値をoptionsに入れないと値が候補に無い扱いになり消される
          # i番目の値が無い(None)の時にlist+Noneはエラーとなるので注意
          options.append([{"label":x,"value":x} for x in genre_no_selected + value[i]])
        update_self_categories(labels,value)
        set_data(start_date, end_date, purpose)
        print("update_categories")
        # print("aaa",data)
        return options
    # データの加工
    # inputの値をdropdownのlabelの値にしても良かったが、そのような設計であるとinputの値を決める必要があるため、デフォルト値としてcategory1等を入れる必要があるため今回は不採用
    else:
      # default値
      options = [[{"label":x,"value":x} for x in df["ジャンル"].unique().tolist()] for i in range(len(new_categories))]
      return options
@dashboard.callback(
  Output("new_categories", 'style'),
  Input("button_add_new_category", 'n_clicks'),
)
def add_new_category(n_clicks):
  if n_clicks is None:
    return dash.no_update
  new_categories.append(make_category(len(new_categories)))
  return new_categories

@dashboard.callback(
  [Output("calender_period_custom","start_date"),
  Output("calender_period_custom","end_date")],
  Input("radio_period_standard","value"),
  Input("calender_period_custom","start_date"),
  Input("calender_period_custom","end_date"),
  Input("dropdown_purpose","value"),
  Input({'type':'input', 'index':ALL},"value"),
  Input({'type':'dropdown', 'index':ALL}, 'value'),
)
def update_data(radio_period, start_date, end_date, purpose, labels, categories_name):
  if ctx.triggered_id == "radio_period_standard":
    start_date, end_date = get_period_from_word(radio_period)
  update_self_categories(labels,categories_name) # label,カテゴリーの内訳の更新を反映
  set_data(start_date, end_date, purpose)
  return [start_date, end_date]
  
@dashboard.callback(
  Output("expense","children"),
  Output("genre_pie_chart_and_ranking_table","children"),
  Input("radio_period_standard","value"),
  Input("calender_period_custom","start_date"),
  Input("calender_period_custom","end_date"),
  Input("dropdown_purpose","value"),
  Input("button_display_hide", "n_clicks"),
  State("hidden_score", "data"), 
)
def update_genre_chart_at_left_side(*_args): # 上のコールバックでselected_periodを更新しているため
  total = data["金額"].sum()
    # print(data["ジャンル"].unique())
  expense_html = html.Div(
            html.P("支出: "+str(total)),
            # style={"hight"}
            # className="px-auto"
          )
  # data = だと　local変数と認識されて、total = data["金額"].sum()でdataがlocalとして扱われるため参照できないとなってしまう。
  data_by_genre = data.groupby("ジャンル")["金額"].sum()
  if data_by_genre.empty:
    # return expense_html
    return expense_html, html.P("データがありません")
  # return expense_html, html.Div(html.P("データがありません",className="border border-4 border-dark",style={"margin-top":"100px"}),style={"height":"250px"})
  # print("fig",_args[-1]["hidden"])
  is_hidden_sidebar = not(_args[-1]["hidden"]) if ctx.triggered_id == "button_display_hide" else _args[-1]["hidden"]
    
  fig_pie = genre_pie_chart_at_left_side(data_by_genre,is_hidden_sidebar)
  table = genre_ranking_table_at_left_side(data_by_genre)
  graph_html = dbc.Row([
            dbc.Col([
              html.Div(dcc.Graph(figure=fig_pie))
            ],width = 4),
            dbc.Col([
              table
              ,dji.Import(src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js")
            ],width = 5,className="offset-md-3 overflow-auto",style={"height": "250px"}),
            
          ] )
  # return expense_html
  # print()
  return expense_html, graph_html

@dashboard.callback(
  Output("year_bar","figure"),
  Input("input_year","value"),
  Input("dropdown_purpose","value"),
)
def update_year_bar_chart_at_left_side(year,purpose):
  if year is None: # 未入力時
    return dash.no_update
  # globalのdataとは期間が異なるので新しく生成している。
  data = get_data_for_purpose(data= df, purpose = purpose)
  data = data[data["年"] == year].groupby(["月","ジャンル"])[["金額"]].sum()
  # if year == 2023: print(data)
  is_empty = False
  if data.empty:
    is_empty = True
    # return dash.no_update
  if is_empty:
    data = pd.DataFrame([{"ジャンル":"","金額":0}],index=[1])
  else:
    data = data.reset_index(level="ジャンル")
  #　足りない月を追加する
  # year_bar["ジャンル"][0]をダミー要素として他の月を生成する。もしyear_bar["ジャンル"][0]が表示しない設定の場合には表示する中で一番上のものを表示するようにする。
  for i in range(1,13):
    if not(i in data.index):
     data.loc[i] = [data["ジャンル"].iloc[0],0] 
  data = data.sort_index()
  fig_bar = px.bar(data, x=data.index, y="金額", color="ジャンル")
  fig_bar.update_yaxes(tickformat=',d', ticksuffix=' 円')
  if is_empty:
    fig_bar.update_yaxes(range=[0,100000],tickformat=',d', ticksuffix=' 円')
  fig_bar.update_xaxes(title = "月",tickvals=data.index,)
  fig_bar.update_layout(margin=dict(t=0))
  monthly_total = data.groupby(level=0)["金額"].sum()
  for month, total_amount in monthly_total.items():
    if total_amount == 0:
      continue
    fig_bar.add_annotation(x=month, y=total_amount+2000, text=str(total_amount), showarrow=False)
  return fig_bar




@dashboard.callback(
  Output("type_of_x_axis","value"),
  Output("genre_bar_chart","figure"),
  Input("type_of_x_axis","value"),
  Input("radio_period_standard","value"),
  Input("calender_period_custom","start_date"),
  Input("calender_period_custom","end_date"),
  Input("dropdown_purpose","value"),
)
def update_genre_bar_chart(unit, _radio_value, start_date, end_date, _purpose):
  triggered_id = ctx.triggered_id
  #起動時はcalender_period_customを受け取る(上のcallbackで値を変えるため)
  if triggered_id != "type_of_x_axis":
    unit = ""
  def get_week_number(day, offset):
    return (day + offset) // 7 + 1
    
  data_by_genre = data
  # fig_right_bar = px.bar(data_by_genre,x=data_by_genre.index, y="金額",color="ジャンル") # x軸のラベルを変えると思う
  start_date = list(map(int,start_date.split("-")))
  end_date = list(map(int,end_date.split("-")))
  if unit == "週" or (unit == "" and start_date[0] == end_date[0] and start_date[1] == end_date[1]):
    unit= "週"
    first_day = pd.to_datetime("%s-%s-1"%(start_date[0],start_date[1])).weekday()
    start_week_number = get_week_number(start_date[2], first_day)
    end_week_number = get_week_number(end_date[2], first_day)
    x_label = list(range(start_week_number,end_week_number+1))
    data_by_genre["週"] = data_by_genre["日"].apply(get_week_number,args=(first_day,))
    data_by_genre = data.groupby(["週","ジャンル"])["金額"].sum().reset_index(level="ジャンル")
    #それぞれの第何週がm/d~m/dまでかを示す
    # week_period = []
    # for i in x_label:
    #   sunday_date = (offset+1)+(i-2)*7 if (offset+1)+(i-2)*7 > 0 else 1 # 曜日から日にちを計算する際に0または負の値は1とする
    #   saturday_date = offset+(i-1)*7
    #   week_period.append([sunday_date, saturday_date]) # 日~土
    # データの加工
  else:
    unit= "月"
    start_month_number = start_date[1]
    end_month_number = end_date[1]
    # print(start_month_number,type(start_month_number),end_month_number,type(end_month_number))
    x_label = list(range(start_month_number,end_month_number+1))
    data_by_genre = data.groupby(["月","ジャンル"])["金額"].sum().reset_index(level="ジャンル")
  fig_bar = px.bar(data_by_genre,x=data_by_genre.index, y="金額",color="ジャンル") # x軸のラベルを変えると思う
  total_by_each_x = data_by_genre.groupby(level=0)["金額"].sum()
  for x, total_amount in total_by_each_x.items():
    if total_amount == 0:
      continue
    fig_bar.add_annotation(x=x, y=total_amount+2000, text=str(total_amount), showarrow=False)
  # unit_for_x_axis = html.P("data for x axis is "+unit)
  return unit, fig_bar





@dashboard.callback(
  Output("dropdown_genre","options"),
  Input("radio_period_standard","value"),
  Input("calender_period_custom","start_date"),
  Input("calender_period_custom","end_date"),
  Input("dropdown_purpose","value"),
)
def update_dropdown_summry(*_args):
  return [{"label": "全て", "value": "全て"}] + [{"label": genre, "value": genre} for genre in data["ジャンル"].unique()] if not data.empty else [{"label": "No results", "value": "",'disabled': True}]


@dashboard.callback(
  Output("item_table","children"),
  Input("button_decide","n_clicks"),
  [State("dropdown_genre","value"),
  State("dropdown_summary","value"),]
)
def update_item_table(_, genre, summary_value):
  data_item = data
  if genre is None:
    return html.P("データがありません")
  elif genre != "全て":
    data_item = data[data["ジャンル"] == genre]
  if summary_value is not None:# データがない時用
    # if summary_value == "":
        # data_item = data_item[["日付","場所"]].reset_index()
    if summary_value == "日付":
        data_item = data_item.groupby(summary_value).agg({'場所':lambda x: ','.join(sorted(list(set(x)))),'商品名':lambda x: ','.join(sorted(list(set(x)))),'金額':sum}).reset_index()
    elif summary_value == "場所":
      data_item = data_item.groupby(summary_value).agg({'日付':lambda x: '~'.join(list(set(x)) if len(set(x))== 1 else [min(x),max(x)]),'商品名':lambda x: ','.join(sorted(list(set(x)))),'金額':sum}).reset_index()
    elif summary_value == "商品名":
        data_item = data_item.groupby(summary_value).agg({'日付':lambda x: '~'.join(list(set(x)) if len(set(x))== 1 else [min(x),max(x)]),'場所':lambda x: ','.join(sorted(list(set(x)))),'金額':sum}).reset_index()
    elif summary_value == "商品名":
        data_item = data_item.groupby(summary_value).agg({'日付':lambda x: '~'.join(list(set(x)) if len(set(x))== 1 else [min(x),max(x)]),'場所':lambda x: ','.join(sorted(list(set(x)))),'金額':sum}).reset_index()
  data_item = data_item.reindex(columns=['日付', '場所', '商品名', '金額']) ## "" の時にはここでカラムが4つだけになる,summary_value is Noneの時も要素を減らす
  return html.Div([html.Table([
    html.Thead([
      html.Tr([html.Th('日付'), html.Th('場所'), html.Th('商品名'), html.Th('金額')])
    ]),
    html.Tbody([
      html.Tr([
          html.Td(date),
          html.Td(store),
          html.Td(item),
          html.Td(total)
      ], className='table-primary' if rank % 2 == 0 else 'table-secondary')
      for rank, (date, store, item, total) in data_item.iterrows()
    ])
  ], className='table table-hover sortable')
  ,dji.Import(src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js")
  ], className='overflow-auto',style={"height": "250px"})


if __name__=='__main__':
    dashboard.run_server(debug=True)

