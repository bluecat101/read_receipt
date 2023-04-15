# ウィンドウ立ち上げ
#--------------------------------
# Tkinterモジュールのインポート
# import tkinter
import tkinter

# ウィンドウ（フレーム）の作成
root = tkinter.Tk()

# ウィンドウの名前を設定
root.title("demo_Tkinter")

# ウィンドウの大きさを設定
root.geometry("400x400")


# ラベルの作成
label = tkinter.Label(root, text="This is the Label.")

#ラベルの表示
label.grid()
# イベントループ（TK上のイベントを捕捉し、適切な処理を呼び出すイベントディスパッチャ）
root.mainloop()