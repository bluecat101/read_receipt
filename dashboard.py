import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import datetime as dt
import calendar as cal
from dateutil.relativedelta import relativedelta
import random

# 付け加え　外部スタイルシート
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

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

dashboard = dash.Dash(__name__)
def get_data_for_period(period = None,):
  today = dt.datetime.today()
  if period is None:
     period = "this month"
  if period == "this month":
    return df[(df["年"] == today.year) & (df["月"] == today.month)]
    # start_day = dt.datetime(today.year,today.month,1)
    # end_day = dt.datetime(today.year,today.month,1)+relativedelta(months=1)
  elif period == "last month":
    if today.month == 1:
      return df[(df["年"] == today.year-1) & (df["月"] == 12)] #1月 => 12月
    else:
      return df[(df["年"] == today.year) & (df["月"] == today.month - 1)] # 2月 => 1月　月だけならtoday.month % 12 + 1 でも成り立つが1月の際に年も変える必要があるためifで分けている
  elif period == "this year":
    return df[(df["年"] == today.year)] 
  elif period == "last year":
    return df[(df["年"] == today.year-1)]
  else:
    # 配列で受け取る[start_day,end_day]
    start_day = dt.strptime(period[0],"%Y-%m-%d")
    end_day = dt.strptime(period[1],"%Y-%m-%d")
  return df[(start_day <= pd.to_datetime(df["日付"])) & (pd.to_datetime(df["日付"]) < end_day)]
  
## 今月のデータがないときに”データなし”と表示させる
pie = get_data_for_period("last month").groupby("ジャンル")["金額"].sum()
fig_pie = go.Figure(
    data=[go.Pie(labels=list(pie.index),
      values=pie.values,
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
)
fig_pie.update_traces(textposition='inside')
year_bar = get_data_for_period("this year").groupby(["月","ジャンル"])[["金額"]].sum() # 棒グラフを作るときのoptionのcolorで指定するときにDataFrame型でないと受け付けないためDataFrame型で取得
year_bar = year_bar.reset_index(level="ジャンル")
#　足りない月を追加する
# year_bar["ジャンル"][0]をダミー要素として他の月を生成する。もしyear_bar["ジャンル"][0]が表示しない設定の場合には表示する中で一番上のものを表示するようにする。
added_year = pd.DataFrame({"ジャンル": [year_bar["ジャンル"].iloc[0] for _i in range(3+1,13)] ,
                           "金額": [0 for _i in range(3+1,13)]},
                          index =[i for i in range(3+1,13)])

year_bar = pd.concat([year_bar,added_year])

fig_bar = px.bar(year_bar,x=list(map(lambda x: str(x)+"月",year_bar.index)), y="金額",color="ジャンル")
fig_bar.update_yaxes(tickformat=',d', ticksuffix=' 円')
fig_bar.update_xaxes(title = "月",)

dashboard.layout = html.Div(
   children =[
    html.H1('Hello Dash',
        style={
        'textAlign': 'center',# テキストセンター寄せ
        # 'color': colors['text'],# 文字色
    }),

    html.Div([dcc.Graph(id = "first-graph", 
                        figure=fig_pie)]),
    html.Div([
       dcc.Graph(
        id = "first-graph",
        figure = fig_bar
    ),
    

    ])                    
    
])


# 実行用③
if __name__=='__main__':
    dashboard.run_server(debug=True)