import dash
from dash import ALL, Input, Output,State, ctx, html, dcc, callback
from dash import dash as ddash
from dash._utils import AttributeDict
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime as dt,date as d
import calendar as cal
from dateutil.relativedelta import relativedelta
import dash_defer_js_import as dji

import common as co
page = "food"


dash.register_page(__name__)
period  = ["今月", "先月", "今年", "昨年", "累計"]
period_options =[{"label": x,"value": x} for x in period]
selected_period = period[0]
self_categories = {} # 現在のカテゴリーを保持する用
data = pd.DataFrame()
df = co.delete_categories_from_data(pd.read_csv('output.csv'))
co.devide_date(df) # # 日付を年-月-日に変換

def get_data_from_period(data = None, period = None):
  """
  ## Discription
    期間からその期間のデータを取得する関数
  ## Args:
      data (DataFrame): 取得するデータ
      period (string): 取得する期間。形式は期間を指す単語か"年-月-日"のどちらかである。

  ## Returns:
      data(DataFrame): 指定された期間のデータを返す
  """
  today = d.today()
  if data is None:
    data = df
  if period is None:
     period = "今月"
  if period == "今月":
    return data[(data["年"] == today.year) & (data["月"] == today.month)]
  elif period == "先月":
    if today.month == 1: # 先月によって去年の12月となるかで場合分け
      return data[(data["年"] == today.year-1) & (data["月"] == 12)] #1月 => 12月
    else:
      return data[(data["年"] == today.year) & (data["月"] == today.month - 1)] # 2月 => 1月　月だけならtoday.month % 12 + 1 でも成り立つが1月の際に年も変える必要があるためifで分けている
  elif period == "今年":
    return data[(data["年"] == today.year)] 
  elif period == "昨年":
    return data[(data["年"] == today.year-1)]
  else:
    start_day = dt.strptime(period[0],"%Y-%m-%d")
    end_day = dt.strptime(period[1],"%Y-%m-%d")
  return data[(start_day <= pd.to_datetime(data["日付"])) & (pd.to_datetime(data["日付"]) <= end_day)]

def get_data_for_purpose(data = None, purpose = None):
  """
  ## Discription
    目的に基づくデータを取得する関数
  ## Args:
      data (DataFrame):取得するデータ
      purpose (String):取得するデータの目的

  ## Returns:
      data: 指定された目的のデータを返す
  """
  if data is None:
    data = df
  if purpose is None:
     purpose = "全て"

  if purpose == "家族" or purpose == "父":
    return data[data["目的"] == purpose]
  elif purpose == "全て":
    return data
  

# サイドバーのカテゴリー用
new_categories = co.create_new_category(df, page)
sidebar = co.create_col_sidebar(new_categories, page)
layout = dbc.Row([sidebar,dbc.Col(
dbc.Row([
  dbc.Col([
    dbc.Row([
      co.create_col_button_expense_purpose(page),
      dbc.Col([dcc.RadioItems(options=period_options,value=period_options[0]["value"],inline=True, id = co.set_id("radio_period_standard", page)),
      dcc.DatePickerRange(id=co.set_id('calender_period_custom', page),
        max_date_allowed = d.today(),
        start_date = d(d.today().year,d.today().month,1),
        end_date = d.today(),
      )]),
    ]),
    html.Div(id=co.set_id("genre_pie_chart_and_ranking_table", page)),
    dbc.Row([
      html.Label([
        dcc.Input(
          id=co.set_id("input_year", page),
          placeholder="2024",
          type="number",
          value= d.today().year,
          style={"width": "100px"}
        ),
        html.Span("年"),
      ],htmlFor="input_year"),
    ]),
    dcc.Graph(
      id = co.set_id("year_bar", page),
      # figure = go.Figure(layout=dict(template='plotly')), # 初期化しないと最初のcallでエラーが出る
      style={"height": "370px"}
    ),
  ],width=6),
  dbc.Col([ ## 右側
    dbc.Row(dcc.RadioItems(options=[{"label":x,"value":x} for x in ["週","月"]],inline=True, id=co.set_id("type_of_x_axis", page))),
    dbc.Row(dcc.Graph(id = co.set_id("genre_bar_chart", page), style={"height": "370px"})),
    dbc.Row([
      dbc.Col(html.Span("ジャンル: "),width="auto",class_name="py-atuo mx-0 px-0"),
      dbc.Col(dcc.Dropdown(
        id = co.set_id('dropdown_genre', page),
        options =[{"label": genre, "value": genre } for genre in data["ジャンル"].unique()] if not(data.empty) else [],
        style={"width": "150px"} 
      ),width="auto",className="mx-0 px-2"),
      dbc.Col(html.Span("まとめて表示する: "),width="auto",class_name="py-atuo mx-0 px-2"),
      dbc.Col(dcc.Dropdown(id = co.set_id('dropdown_summary', page), options = [{"label":x,"value":x} for x in ["","日付", "場所", "商品名"]], style={"width": "100px"}),width="auto",className="mx-0 px-0"),
      dbc.Col(html.Button("決定",id = co.set_id('button_decide', page), style={"width": "100px","margin":"auto", 'display':'inline-block'}), width="auto",className="mx-0 px-2")]),
    html.Div(id=co.set_id("item_table", page))
  ],
  width=6)
]),width=9,id="main")])

def genre_pie_chart_at_left_side(data,is_hidden_sidebar):
  """
  ## Discription
    左側の画面用のジャンルごとに分かれた円グラフを返す関数
  ## Args:
      data (DataFrame): 円グラフにするデータ
      is_hidden_sidebar (bool): サイドバーが隠れているかどうか(隠れているかによって位置が異なるため)

  ## Returns:
     fig_pie (go.Figure) : 円グラフ
  """
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
  # 余白の調整
  if is_hidden_sidebar:
    fig_pie.update_layout(margin=dict(l=100, r=0, t=10, b=10),)    
  else:
    fig_pie.update_layout(margin=dict(l=0, r=0, t=10, b=10),)
  fig_pie.update_traces(textposition='inside')
  return fig_pie


def genre_ranking_table_at_left_side(data):
  """
  ## Discription
    左側の画面用のランキングテーブルを作成する関数
  ## Args:
      data (DataFrame): ランキングに使用するデータ
  ## Returns:
      table (html.Table): ランキング化されたテーブル 
  """
  ranked_data = data.sort_values(ascending=False).reset_index()
  ranked_data.index += 1  # ランキングは1から始まる
  
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
def get_date_from_period(period):
  """
  ## Discription
    期間から日にちを取得する関数
  ## Args:
    period (string): 指定する期間
  ## Returns:
    start_date, end_date(tabple(string, string)): 初めの日にちと終わりの日にちをタプルで返す。
  """
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

def set_data(start_date, end_date, purpose):
  """
  ## Discription
    分けられたカテゴリーごとにジャンル名を変更する関数
  ## Args:
      start_date (string): 指定する開始日
      end_date   (string): 指定する終了日
      purpose    (string): 目的 
  """
  def classify_category(genre):
    """
    ## Discription
      指定されたカテゴリーごとに仕分けする関数
    ## Args:
        genre (string): 仕分け前のジャンル

    ## Returns:
        genre (string): 仕分け後のカテゴリー名 
    """
    for label, category in self_categories.items():
      if genre in category:
        return label
    return genre # 見つからなかった場合、区分をジャンル名を同じにして返す
  global data
  data= df.copy()
  data["ジャンル"] = data["ジャンル"].apply(classify_category) # ジャンルの名前を変更
  data = get_data_from_period(get_data_for_purpose(data = data, purpose = purpose), period = [start_date, end_date]) #dfから取得

def update_self_categories(labels, value):
  """
  ## Discription

  ## Args:
    labels ([string]): カテゴリーの新しい名前
    value  ([string]): 各カテゴリーに含まれている各ジャンル
  """
  labels = ["カテゴリー"+str(i+1) if x == "" else x for i,x in enumerate(labels)]# 未入力のlabelを変換(カテゴリーn)する
  value  = [x if x is not None else [] for x in value]
  global self_categories
  self_categories = {labels[i]: value[i] for i in range(len(new_categories))} # 追加だと過去のが残ってしまう
  


def return_placeholder(num):
  """
  ## Discription
    サイドバーのカテゴリ名のプレイスホルダーを返す関数
  Args:
      num (int): 何番目のプレイスホルダーか 

  Returns:
      placeholder (string): プレイスホルダー 
  """
  return ['カテゴリー'+str(i+1) for i in range(num)]


@callback(
    Output("new_categories", 'children'),
    Output({'id':'selected_category', 'index':ALL,"page": "food"}, 'value'),
    Output({'id':'selected_category', 'index':ALL,"page": "food"}, 'options'),
    Output({'id':'category_name', 'index':ALL,"page": "food"},"placeholder"),
    # dropdownのvalueの値はglobalのnew_categoriesに反映されているわけではなく、new_categoriesを更新するためvalueの値も更新する必要がある
    Input({'id':'selected_category', 'index':ALL,"page": "food"}, 'value'),
    Input({"id": "button_add_new_category", "page": "food"}, 'n_clicks'),
    Input({'id':'delete_category', 'index':ALL,"page": "food"}, 'n_clicks'),
    State({'id':'calender_period_custom', "page": "food"},"start_date"),
    State({'id':'calender_period_custom', "page": "food"},"end_date"),
    State({"id": "dropdown_purpose", "page": "food"},"value"),
    State({'id':'category_name', 'index':ALL,"page": "food"},"value"),
    State({'id':'category_name', 'index':ALL,"page": "food"},"id"), # 現在のidを取得するためにinput_idでなくても良いが1つ必要
    State({'id':'selected_category', 'index':ALL,"page": "food"}, 'options'), # 再読み込み時にplaceholderの値がid参照になっており、idは毎回連番に振り直さないので再読み込み時にplaceholderの値がおかしくなるため再読み込み時にplaceholerを振り直す用
)
def update_categories(value, _add_click, _delete_click, start_date, end_date, purpose, labels,input_id,options):
  """
  ## Discription
    カテゴリに追加、削除、内容の変更があった際にカテゴリを更新して反映させる関数
  ## Args:
    value (string[][]): 各カテゴリに含まれる要素
    _add_click (int): 追加ボタンがクリックされたか
    _delete_click (int): deleteボタンがクリックされたか
    start_date (string): 開始日
    end_date (string): 終了日
    purpose (string): 目的
    labels (string[]): カテゴリのラベル名
    input_id ({"index","id","category_name"}[]): 各カテゴリのid
    options ({"label","value"}[]): 各カテゴリで選択できる内容

  ## Returns:
      new_categories, value, options, placeholder : 新しいカテゴリ、選択されているカテゴリ、選択できるカテゴリ、プレイスホルダー
  """
  print(ctx.triggered_id)
  if ctx.triggered_id is None:
    return ddash.no_update,value,options,return_placeholder(len(value))
    # optionsを指定しないとdfから作成するためすでにカテゴリーに分類されている値を入れてしまう。
    # そのため、何もない状態で生成し他のカテゴリーと一緒にoptionsが変更される
  elif isinstance(ctx.triggered_id, AttributeDict) and ctx.triggered_id["id"] == "delete_category":
    id = ctx.triggered_id["index"]
    for i in range(len(input_id)):
      if input_id[i]["index"] == id:
        index = i
        break
    else:
      index = -1
      print("error")
      return ddash.no_update
    
    global new_categories
    del new_categories[index]
    del labels[index]
    del value[index]
  # この時点で押されたnew_categoryに値が格納されているので、押されたindexを取得してそれだけ例外で押された要素等から生成する必要なし

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
  update_self_categories(labels, value)
  set_data(start_date, end_date, purpose)
  if ctx.triggered_id == {"id": "button_add_new_category", "page": "food"}:
    new_categories.append(co.get_category(input_id[-1]["index"]+1 if len(input_id) > 0 else 0,df,page, options = [{"label":x,"value":x} for x in genre_no_selected ]))
    return new_categories, value, options, return_placeholder(len(value))
  elif  isinstance(ctx.triggered_id, AttributeDict)and ctx.triggered_id["id"] == "delete_category":
    # 出力が元のnew_categoriesの数を求めているため数が合わないのでダミー要素を追加
    placeholder = return_placeholder(len(value))
    placeholder.insert(index,"")
    value.insert(index, [])
    options.insert(index, [])

    # new_categoriesはchildrenで返しているため個数を気にしないのでlen(new_categories)ではエラーになる
    return new_categories, value, options, placeholder
  else:
    return ddash.no_update, value, options, return_placeholder(len(value))
   

@callback(
  [Output({'id':'calender_period_custom', "page": "food"},"start_date"),
  Output({'id':'calender_period_custom', "page": "food"},"end_date")],
  Input({'id':'radio_period_standard', "page": "food"},"value"),
  Input({'id':'calender_period_custom', "page": "food"},"start_date"),
  Input({'id':'calender_period_custom', "page": "food"},"end_date"),
  Input({"id": "dropdown_purpose", "page": "food"},"value"),
  Input({'id':'category_name', 'index':ALL, "page": "food"},"value"),
  Input({'id':'selected_category', 'index':ALL, "page": "food"}, 'value'),
)
def update_data(radio_period, start_date, end_date, purpose, labels, categories_name):
  """
  ## Discription
    データを日付と目的から更新する
  ## Args:
      radio_period (string): 「今月」等の言葉による期間
      start_date   (string): 開始日
      end_date     (string): 終了日
      purpose      (string): 目的
      labels     (string[]): カテゴリの種類
      categories_name (string[]): 新しいカテゴリー名

  ## Returns:
      start_date, end_date: カレンダーになっている日付を更新する 
  """
  if ctx.triggered_id == {'id':'radio_period_standard', "page": "food"}:
    start_date, end_date = get_date_from_period(radio_period)
  update_self_categories(labels,categories_name) # label,カテゴリーの内訳の更新を反映
  set_data(start_date, end_date, purpose)
  return (start_date, end_date)
  
@callback(
  Output({"id": "expense", "page": "food"},"children"),
  Output({'id':'genre_pie_chart_and_ranking_table', "page": "food"},"children"),
  Input({'id':'radio_period_standard', "page": "food"},"value"),
  Input({'id':'calender_period_custom', "page": "food"},"start_date"),
  Input({'id':'calender_period_custom', "page": "food"},"end_date"),
  Input({"id": "dropdown_purpose", "page": "food"},"value"),
  Input({"id": "button_display_hide", "page": "food"}, "n_clicks"),
  State("hidden_score", "data"), 
)
def update_genre_chart_at_left_side(*_args):
  """
  ## Discription
    左上の支出等の情報更新
  Returns:
      expense_html, graph_html(html.Div, dbc.Row):更新するデータ 
  """
  total = data["金額"].sum()
  expense_html = html.Div(html.P("支出: "+str(total)))
  # data = だと　local変数と認識されて、total = data["金額"].sum()でdataがlocalとして扱われるため参照できないとなってしまう。
  data_by_genre = data.groupby("ジャンル")["金額"].sum()
  if data_by_genre.empty:
    return expense_html, html.P("データがありません")
  is_hidden_sidebar = not(_args[-1]["hidden"]) if ctx.triggered_id == {'id': 'button_display_hide', 'page': 'food'} else _args[-1]["hidden"]
    
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
  return expense_html, graph_html

@callback(
  Output({'id':'year_bar', "page": "food"},"figure"),
  Input({'id':'input_year', "page": "food"},"value"),
  Input({"id": "dropdown_purpose", "page": "food"},"value"),
)
def update_year_bar_chart_at_left_side(year,purpose):
  """
  ## Discription
    左側の年ごとの棒グラフの更新
  ## Args:
      year (int): 表示する年
      purpose (string): 目的

  ## Returns:
      fig_bar (px.bar):棒グラフ 
  """
  if year is None: # 未入力時
    return ddash.no_update
  # globalのdataとは期間が異なるので新しく生成している。
  data = get_data_for_purpose(data= df, purpose = purpose)
  data = data[data["年"] == year].groupby(["月","ジャンル"])[["金額"]].sum()
  # if year == 2023: print(data)
  is_empty = False
  if data.empty:
    is_empty = True
    # return ddash.no_update
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




@callback(
  Output({'id':'type_of_x_axis', "page": "food"},"value"),
  Output({'id':'genre_bar_chart', "page": "food"},"figure"),
  Input({'id':'type_of_x_axis', "page": "food"},"value"),
  Input({'id':'radio_period_standard', "page": "food"},"value"),
  Input({'id':'calender_period_custom', "page": "food"},"start_date"),
  Input({'id':'calender_period_custom', "page": "food"},"end_date"),
  Input({"id": "dropdown_purpose", "page": "food"},"value"),
)
def update_genre_bar_chart(unit, _radio_value, start_date, end_date, _purpose):
  """
  ## Discription 
    右側のジャンル分けされた棒グラフの更新
  Args:
      unit         (string): 表示するグラフの単位(週ごとか月毎か)
      _radio_value (string): 期間のラジオボタン 
      start_date   (string): 開始日
      end_date     (string): 終了日
      _purpose     (string): 目的

  Returns:
      unit, fig_bar (string, px.bar): 表示するグラフの単位と棒グラフ
  """
  triggered_id = ctx.triggered_id
  #起動時はcalender_period_customを受け取る(上のcallbackで値を変えるため)
  if triggered_id != {'id':'type_of_x_axis', "page": "food"}:
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





@callback(
  Output({'id':'dropdown_genre', "page": "food"},"options"),
  Input({'id':'radio_period_standard', "page": "food"},"value"),
  Input({'id':'calender_period_custom', "page": "food"},"start_date"),
  Input({'id':'calender_period_custom', "page": "food"},"end_date"),
  Input({"id": "dropdown_purpose", "page": "food"},"value"),
)
def update_dropdown_summry(*_args):
  """
  ## Discription
    右下のジャンルのドロップダウンの内容を更新する
  ## Returns:
      {label:,value}[]: 表示する内容
  """
  return [{"label": "全て", "value": "全て"}] + [{"label": genre, "value": genre} for genre in data["ジャンル"].unique()] if not data.empty else [{"label": "No results", "value": "",'disabled': True}]


@callback(
  Output({'id':'item_table', "page": "food"},"children"),
  Input({'id':'button_decide', "page": "food"},"n_clicks"),
  [State({'id':'dropdown_genre', "page": "food"},"value"),
  State({'id':'dropdown_summary', "page": "food"},"value"),]
)
def update_item_table(_, genre, summary_value):
  """
  ## Discription
    右下に表示する表の更新
  ## Args:
      _                (int): 決定を押したか
      genre         (string): 表示するジャンル名 
      summary_value (string):どの部分をまとめて表示するか

  ## Returns:
      table (html.Div) : 表示するテーブル
  """
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

