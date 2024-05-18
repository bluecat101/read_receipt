import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

dashboard = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP,'./assets/stylesheet.css', dbc.icons.BOOTSTRAP],use_pages=True,pages_folder="dashboard")
# ヘッダーの設定
navbar = dbc.Nav(
          children=[dbc.NavItem(dbc.NavLink(page["name"], 
            href=page["relative_path"],
            class_name="nav-item")) for page in dash.page_registry.values()],
          id = "navibar",
          class_name = "navbar navbar-expand-lg bg-dark"
        )
# mainのレイアウトの設定
dashboard.layout = dbc.Container([
                      dcc.Location(id='url', refresh=False),
                      navbar, # ヘッダーの設定
                      html.Br(),
                      dash.page_container, # 各ページのviewを作成する
                    ],id="container",style={"margin":"0","padding":"0"}, fluid=True)

if __name__=='__main__':
  dashboard.run_server(debug=True, dev_tools_ui=True)