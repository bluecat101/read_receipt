import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
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

dashboard = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP,'./assets/stylesheet.css'])
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
    # 配列で受け取る[start_day,end_day]
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
  
## 今月のデータがないときに”データなし”と表示させる




# fig_right_bar = px.bar(year_bar,x=list(map(lambda x: str(x)+"月",right_bar.index)), y="金額",color="ジャンル")

right_pie = get_data_for_period(period = "先月").groupby("ジャンル")["金額"].sum()
fig_right_pie = go.Figure(
    data=[go.Pie(labels=list(right_pie.index),
      values=right_pie.values,
      hole=.1,
      marker=dict(colors=['#bad6eb', '#2b7bba']),
      textinfo = "label+percent",
      direction='clockwise'
      )])
fig_right_pie.update_layout(
    width=500,
    height=250,
    margin=dict(l=30, r=10, t=10, b=10),
    paper_bgcolor='rgba(0,0,0,0)',
    uniformtext_minsize = 10,
    uniformtext_mode='hide',
    showlegend=False,
)
fig_right_pie.update_traces(textposition='inside')
# サンプルのデータを作成
df_sample = {
    '名前': ['Alice', 'Bob', 'Charlie', 'David', 'Emma'],
    'スコア': [90, 85, 80, 95, 88]
}
df_sample = pd.DataFrame(df_sample)

# スコアで降順にソートしてランキングを作成
df_ranked = df_sample.sort_values(by='スコア', ascending=False).reset_index(drop=True)
df_ranked.index += 1  # ランキングは1から始まる

period_options =[{"label": x,"value": x} for x in period]
purpose_options =[{"label": x,"value": x} for x in purpose]
dashboard.layout = dbc.Container([
  dbc.Row([
    dbc.Col([
      dbc.Row([
        dbc.Col([
          dbc.Row(id = "expense"),
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
             start_date = d(d.today().year,d.today().month,1),
             end_date= d.today()
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
      ),
    ],width=6),
    dbc.Col([ ## 右側
      dcc.Graph(
        id = "genre_bar_chart",
        
      ),
      dbc.Row([
        html.Div([
          html.Label(
            dcc.Dropdown(
            id = 'dropdown_genre',
            # options = purpose_options,
            options =[{"label": genre, "value": genre } for genre in data["ジャンル"].unique()] if not(data.empty) else [],
            style={"width": "200px"}
          ),),
          html.Label(          
            dcc.Dropdown(
            id = 'dropdown_summary',
            options = [{"label":x,"value":x} for x in ["","日付", "場所", "商品名"]],
            style={"width": "100px"}
          ),),
          html.Label(
            html.Button("決定",id = 'button_decide',
            style={"width": "100px"}
          ),
          ),
        ]),
        html.Div(id="item_table")
      ])
    ],
    width=6)
  ])
],style={"margin":"0"})

def genre_pie_chart_at_left_side(data):
  fig_pie = go.Figure(
      data=[go.Pie(labels=list(data.index),
        values=data.values,
        hole=.1,
        marker=dict(colors=['#bad6eb', '#2b7bba']),
        textinfo = "label+percent",
        direction='clockwise'
        )])
  fig_pie.update_layout(
      width=500,
      height=250,
      margin=dict(l=30, r=10, t=10, b=10),
      paper_bgcolor='rgba(0,0,0,0)',
      uniformtext_minsize = 10,
      uniformtext_mode='hide',
      showlegend=False,
  )
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

def get_triggered_element_for_period(*args):
  if dash.callback_context.triggered:
    trigger_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0] # "triggered_name.value"という形で格納されているのでtriggeredの部分を取得
    # print(dash.callback_context.triggered_id)
    if trigger_id == "radio_period_standard":
      # return get_period_from_word(args[0])
      return args[0]
  #   elif trigger_id == "calender_period_custom":
  #     return [args[1],args[2]]
  return selected_period # default値

@dashboard.callback(
  [dash.dependencies.Output("calender_period_custom","start_date"),
  dash.dependencies.Output("calender_period_custom","end_date")],
  dash.dependencies.Input("radio_period_standard","value"),
  dash.dependencies.Input("calender_period_custom","start_date"),
  dash.dependencies.Input("calender_period_custom","end_date"),
  dash.dependencies.Input("dropdown_purpose","value"),
)
def update_data(radio_period, start_date, end_date, purpose):
  if dash.callback_context.triggered and dash.callback_context.triggered_id == "radio_period_standard":
    start_date, end_date = get_period_from_word(radio_period)
    # print(start_date,end_date)
  global data
  data = get_data_for_period(get_data_for_purpose(purpose = purpose), period = [start_date, end_date])
  # print(data)
  return [start_date, end_date]
  
@dashboard.callback(
  dash.dependencies.Output("expense","children"),
  dash.dependencies.Output("genre_pie_chart_and_ranking_table","children"),
  dash.dependencies.Input("radio_period_standard","value"),
  dash.dependencies.Input("calender_period_custom","start_date"),
  dash.dependencies.Input("calender_period_custom","end_date"),
  dash.dependencies.Input("dropdown_purpose","value"),
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
  fig_pie = genre_pie_chart_at_left_side(data_by_genre)
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
  # print("aaa")
  return expense_html, graph_html

@dashboard.callback(
  dash.dependencies.Output("year_bar","figure"),
  dash.dependencies.Input("input_year","value"),
  dash.dependencies.Input("dropdown_purpose","value"),
)
def update_year_bar_chart_at_left_side(year,purpose):
  if year is None: # 未入力時
    return dash.no_update
  # globalのdataとは期間が異なるので新しく生成している。
  data_year = get_data_for_purpose(purpose = purpose)
  data_year = data_year[data_year["年"] == year].groupby(["月","ジャンル"])[["金額"]].sum()
  # if year == 2023: print(data_year)
  is_empty = False
  if data_year.empty:
    is_empty = True
    # return dash.no_update
  if is_empty:
    data_year = pd.DataFrame([{"ジャンル":"","金額":0}],index=[1])
  else:
    data_year = data_year.reset_index(level="ジャンル")
  #　足りない月を追加する
  # year_bar["ジャンル"][0]をダミー要素として他の月を生成する。もしyear_bar["ジャンル"][0]が表示しない設定の場合には表示する中で一番上のものを表示するようにする。
  for i in range(1,13):
    if not(i in data_year.index):
     data_year.loc[i] = [data_year["ジャンル"].iloc[0],0] 
  data_year = data_year.sort_index()
  # list(map(lambda x: str(x)+"月",data_year.index))
  # print("year",year)
  # pd.set_option('display.max_rows', None)
  # pd.set_option('display.max_columns', None)
  # print(data_year,data_year.index,data_year.columns)
  # x_values = data_year.index
  # y_values = data_year["金額"]
  # colors = data_year["ジャンル"]
  # bars = []
  # for x, y, color in zip(x_values, y_values, colors):
  #     bars.append(go.Bar(
  #         x=[x],
  #         y=[y],
  #         marker=dict(color=color),
  #         hoverinfo='y+name',
  #     ))
  # layout = go.Layout(
  #     title='Monthly Expenses by Genre',
  #     xaxis=dict(title='Month'),
  #     yaxis=dict(title='Amount'),
  #     barmode='stack'
  # )

  # グラフオブジェクトの作成
  # fig_bar = go.Figure(data=bars, layout=layout)
  fig_bar = px.bar(data_year, x=data_year.index, y="金額", color="ジャンル")
  fig_bar.update_yaxes(tickformat=',d', ticksuffix=' 円')
  if is_empty:
    fig_bar.update_yaxes(range=[0,100000],tickformat=',d', ticksuffix=' 円')
  fig_bar.update_xaxes(title = "月",tickvals=data_year.index,)
  fig_bar.update_layout(margin=dict(t=0))
  monthly_total = data_year.groupby(level=0)["金額"].sum()
  for month, total_amount in monthly_total.items():
    if total_amount == 0:
      continue
    fig_bar.add_annotation(x=month, y=total_amount+2000, text=str(total_amount), showarrow=False)
  return fig_bar

@dashboard.callback(
  dash.dependencies.Output("genre_bar_chart","figure"),
  dash.dependencies.Input("radio_period_standard","value"),
  dash.dependencies.Input("calender_period_custom","start_date"),
  dash.dependencies.Input("calender_period_custom","end_date"),
  dash.dependencies.Input("dropdown_purpose","value"),
)
def update_genre_bar_chart(*_args):
  data_by_genre = data.groupby(["月","ジャンル"])["金額"].sum().reset_index(level="ジャンル")
  fig_right_bar = px.bar(data_by_genre,x=data_by_genre.index, y="金額",color="ジャンル") # x軸のラベルを変えると思う
  return fig_right_bar

@dashboard.callback(
  dash.dependencies.Output("dropdown_genre","options"),
  dash.dependencies.Input("radio_period_standard","value"),
  dash.dependencies.Input("calender_period_custom","start_date"),
  dash.dependencies.Input("calender_period_custom","end_date"),
  dash.dependencies.Input("dropdown_purpose","value"),
)
def update_dropdown_summry(*_args):
  return [{"label": "全て", "value": "全て"}] + [{"label": genre, "value": genre} for genre in data["ジャンル"].unique()] if not data.empty else [{"label": "No results", "value": "",'disabled': True}]


@dashboard.callback(
  dash.dependencies.Output("item_table","children"),
  dash.dependencies.Input("button_decide","n_clicks"),
  [dash.dependencies.State("dropdown_genre","value"),
  dash.dependencies.State("dropdown_summary","value"),]
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

