import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import datetime as dt
import calendar as cal
from dateutil.relativedelta import relativedelta
import dash_defer_js_import as dji
import random

period  = ["今月", "先月", "今年", "昨年", "累計"]
purpose = ["家族", "父", "全て"]

# 付け加え　色
# colors = {
#   'background': 'lightblue  ',
#   'background1': 'limegreen  ',
#   'text': '#FFFFFF'
# }

df = pd.read_csv('output.csv')
df["年"] = df["日付"].str.split("-").apply(lambda row: int(row[0]))
df["月"] = df["日付"].str.split("-").apply(lambda row: int(row[1]))
df["日"] = df["日付"].str.split("-").apply(lambda row: int(row[2]))

dashboard = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP,'./assets/stylesheet.css'])
def get_data_for_period(data = None,period = None,):
  today = dt.datetime.today()
  if data is None:
    data = df
  if period is None:
     period = "今月"
  if period == "今月":
    return data[(data["年"] == today.year) & (data["月"] == today.month)]
    # start_day = dt.datetime(today.year,today.month,1)
    # end_day = dt.datetime(today.year,today.month,1)+relativedelta(months=1)
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
  return data[(start_day <= pd.to_datetime(data["日付"])) & (pd.to_datetime(data["日付"]) < end_day)]

def get_data_for_purpose(data = None,purpose = None,):
  today = dt.datetime.today()
  if data is None:
    data = df
  if purpose is None:
     purpose = "全て"

  if purpose == "家族" or purpose == "父":
    return data[data["目的"] == purpose]
  elif purpose == "全て":
    return data
  
## 今月のデータがないときに”データなし”と表示させる



right_bar = get_data_for_period(period = "先月").groupby(["月","ジャンル"])[["金額"]].sum().reset_index(level="ジャンル")
fig_right_bar = px.bar(right_bar,x=right_bar.index, y="金額",color="ジャンル") # x軸のラベルを変えると思う
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
data = {
    '名前': ['Alice', 'Bob', 'Charlie', 'David', 'Emma'],
    'スコア': [90, 85, 80, 95, 88]
}
df_sample = pd.DataFrame(data)

# スコアで降順にソートしてランキングを作成
df_ranked = df_sample.sort_values(by='スコア', ascending=False).reset_index(drop=True)
df_ranked.index += 1  # ランキングは1から始まる

period_options =[{"label": x,"value": x} for x in period]
purpose_options =[{"label": x,"value": x} for x in purpose]
dashboard.layout = dbc.Container([
  dbc.Row([
    dbc.Col([
      dbc.Row([
        dbc.Col(
        width = 6,id = "expense"),
        dbc.Col([
          # デフォルト値を今月にしてドロップダウンを作成
          dcc.Dropdown(
            id = 'dropdown_for_left_side_period',
            options = period_options,
            value = period_options[0]["value"]
          ),
          dcc.Dropdown(
            id = 'dropdown_for_left_side_purpose',
            options = purpose_options,
            value = purpose_options[0]["value"]
          ),
        ],width = 6),
      ]),
      dbc.Row(id="genre_chart_at_left_side"),
      dbc.Row([
        html.Label([
          dcc.Input(
          id="input_year",
          placeholder="2024",
          type="number",
          value= dt.datetime.today().year-1,
          style={"width": "100px"}
          ),
          html.Span("年"),
        ],htmlFor="input_year"),
        ]),
      dcc.Graph(
        id = "year_bar",
        # figure = fig_bar
      ),
    ],width=6),
    dbc.Col([
      html.Div(
        html.P("選択可能(日時、)",style={"height":"100%",
                      "background-color":"lightblue"}),
      ),
      dcc.Graph(
        id = "right-bar-grath",
        figure = fig_right_bar
      ),
      dbc.Row([
        dbc.Col(dcc.Graph(id = "right-pie-graph", 
                      figure=fig_right_pie),width=6),
        dbc.Col(html.Table([
            html.Thead([
              html.Tr([html.Th('順位'), html.Th('名前'), html.Th('スコア')])
            ]),
            html.Tbody([
              html.Tr([
                  html.Td(rank),
                  html.Td(name),
                  html.Td(score)
              ], className='table-primary' if rank % 2 == 0 else 'table-secondary')
              for rank, (name, score) in df_ranked.iterrows()
            ])
          ], className='table table-hover'),width=6)

        
        
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
  table = html.Div([html.Table([
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
          , dji.Import(src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js")]
          ,style={"height": "250px","overflow-y": "auto"}
          
          )
  
  # table = dash_table.DataTable(
  #       # id='datatable',
  #       columns=[{'name': col, 'id': col} for col in ["順位", "ジャンル", "金額"]],
  #       data=ranked_data2.to_dict('records'),
  #       editable=False,  # セルの編集を許可
  #       sort_action = 'native',
  # )
  return table

@dashboard.callback(
  dash.dependencies.Output("expense","children"),
  dash.dependencies.Input("dropdown_for_left_side_period","value"),
  dash.dependencies.Input("dropdown_for_left_side_purpose","value")
)
def update_expense(period,purpose):
  total = get_data_for_period(data = get_data_for_purpose(purpose = purpose),period = period)["金額"].sum()
  return  html.Div(
            html.P("支出: "+str(total)),
            # style={"hight"}
            # className="px-auto"
          )

@dashboard.callback(
  dash.dependencies.Output("genre_chart_at_left_side","children"),
  dash.dependencies.Input("dropdown_for_left_side_period","value"),
  dash.dependencies.Input("dropdown_for_left_side_purpose","value")
)
def update_genre_chart_at_left_side(period,purpose):
  data = get_data_for_period(data = get_data_for_purpose(purpose = purpose),period = period).groupby("ジャンル")["金額"].sum()
  if data.empty:
    return html.Div(html.P("データがありません",className="border border-4 border-dark",style={"margin-top":"100px"}),style={"height":"250px"})
  fig_pie = genre_pie_chart_at_left_side(data)
  table = genre_ranking_table_at_left_side(data)
  return  dbc.Row([
            dbc.Col([
              # genre_pie_chart_at_left_side(period)
              html.Div(dcc.Graph(figure=fig_pie))
            ],width = 4),
            dbc.Col([
              table
            ],width = 5,id="genre_ranking_table_at_left_side",className="offset-md-3"),
          ])

@dashboard.callback(
  dash.dependencies.Output("year_bar","figure"),
  dash.dependencies.Input("input_year","value"),
)
def update_year_bar_chart_at_left_side(year):
  if year is None: # 未入力時
    return dash.no_update
  data = df[df["年"] == year].groupby(["月","ジャンル"])[["金額"]].sum()
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
  # added_year = pd.DataFrame()
  for i in range(1,13):
    if not(i in data.index):
     data.loc[i] = [data["ジャンル"].iloc[0],0] 
  # print(data)
  # if year == 2022: print(data)
  # data = pd.concat([data,added_year])
  data = data.sort_index()
  # list(map(lambda x: str(x)+"月",data.index))
  fig_bar = px.bar(data,x=data.index, y="金額",color="ジャンル")
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



if __name__=='__main__':
    dashboard.run_server(debug=True)