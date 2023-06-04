# import tkinter as tk
# from tkinter import ttk

# # rootメインウィンドウの設定
# root = tk.Tk()
# root.title("scroll app")
# root.geometry("200x100")

# # メインフレームの作成と設置
# frame = ttk.Frame(root)
# frame.pack(padx=20,pady=10)

# # Listboxの選択肢
# days = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
# lists = tk.StringVar(value=days)

# # 各種ウィジェットの作成
# Listbox = tk.Listbox(frame, listvariable=lists, height=4)

# # スクロールバーの作成
# scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=Listbox.yview)

# # スクロールバーをListboxに反映
# Listbox["yscrollcommand"] = scrollbar.set

# # 各種ウィジェットの設置
# Listbox.grid(row=0, column=0)
# scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

# root.mainloop()
# -*- coding:utf-8 -*-
import tkinter

# メインウィンドウの作成
app = tkinter.Tk()

# キャンバスの作成と配置
canvas = tkinter.Canvas(
    app,
    width=400,
    height=300,
    scrollregion=(0, 0, 0, 600)
)
canvas.grid(row=0, column=0)

# 楕円をキャンバスからはみ出るように描画
canvas.create_oval(
    300, 250,
    500, 350,
    fill="blue"
)

# 楕円をキャンバスの外に描画
canvas.create_oval(
    700, 0,
    800, 200,
    fill="red"
)

# 長方形をキャンバスの外に描画
canvas.create_rectangle(
    600, 400,
    800, 500,
    fill="green"
)

# 長方形をキャンバスの外に描画
canvas.create_rectangle(
    -200, -100,
    0, 0,
    fill="purple"
)

# 水平方向のスクロールバーを作成
xbar = tkinter.Scrollbar(
    app,  # 親ウィジェット
    orient=tkinter.HORIZONTAL,  # バーの方向
)

# 垂直方向のスクロールバーを作成
ybar = tkinter.Scrollbar(
    app,  # 親ウィジェット
    orient=tkinter.VERTICAL,  # バーの方向
)

# キャンバスの下に水平方向のスクロールバーを配置
xbar.grid(
    row=1, column=0,  # キャンバスの下の位置を指定
    sticky=tkinter.W + tkinter.E  # 左右いっぱいに引き伸ばす
)

# キャンバスの右に垂直方向のスクロールバーを配置
ybar.grid(
    row=0, column=1,  # キャンバスの右の位置を指定
    sticky=tkinter.N + tkinter.S  # 上下いっぱいに引き伸ばす
)


# キャンバスをスクロールするための設定

# スクロールバーのスライダーが動かされた時に実行する処理を設定
xbar.config(
    command=canvas.xview
)
ybar.config(
    command=canvas.yview
)


# キャンバススクロール時に実行する処理を設定
canvas.config(
    xscrollcommand=xbar.set
)
canvas.config(
    yscrollcommand=ybar.set
)


# メインループ
app.mainloop()