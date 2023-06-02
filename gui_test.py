# # ウィンドウ立ち上げ
# #--------------------------------
# # Tkinterモジュールのインポート
# # import tkinter
# import tkinter as tk
# from  tkinter import ttk
# # import tkinter.ttk as ttk
# # # ウィンドウ（フレーム）の作成
# # root = tkinter.Tk()

# # # ウィンドウの名前を設定
# # root.title("demo_Tkinter")

# # # ウィンドウの大きさを設定
# # root.geometry("400x400")


# # # ラベルの作成
# # label = tkinter.Label(root, text="This is the Label.")

# # frame2=tkinter.Frame(root)
# # label2=tkinter.Label(frame2,text="frame2")

# # # frame3=tkinter.Frame()
# # label3=tkinter.Label(root,text="label3")

# # #ラベルの表示
# # label.pack(side=tkinter.LEFT)
# # label2.pack(side=tkinter.RIGHT)
# # label3.grid()


# # root = tkinter.Tk()
# # root.title("demo_Tkinter")
# # root.geometry("400x400")

# # # フレームその２（子フレーム・親にフレームその１を指定）
# # frame2 = tkinter.Frame(root)

# # label = tkinter.Label(root, text="rootlabel")

# # # ラベルその１、その２（配置先：フレームその２（子フレーム））
# # label1 = tkinter.Label(frame2, text="This is the Label_1.")
# # label2 = tkinter.Label(frame2, text="This is the Label_2.")

# # # ラベルその３（配置先：フレームその１（ウィンドウ・最上位フレーム））
# # label3 = tkinter.Label(root, text="This is the Label_3.")


# # label.grid()

# # # frame2.grid()

# # # ラベルその１、その２をフレームその２に表示
# # label1.pack(side=tkinter.RIGHT)
# # label2.pack(side=tkinter.LEFT)
# # # label2.grid()

# # # フレームその２をフレームその１に表示

# # # ラベルその３をフレームその１に表示
# # label3.grid()

# # # イベントループ（TK上のイベントを捕捉し、適切な処理を呼び出すイベントディスパッチャ）

# # # コンソールに"Button is clicked."を出力する関数
# # def clicked():
# #   label1=(tkinter.Label(frame2,text="aa"))
# #   # print("Button is clicked.")

# # # ボタンの作成（text=ボタンに表示されるテキスト, command=押下時に呼び出す関数）
# # button = tkinter.Button(root, text="ボタン", command=clicked)
# # button.grid()
# class Todoapp(tk.Tk):
#   def __init__(self,title):
#     super().__init__()
#     self.title(title)
#     self.geometry("400x600")

#     input_frame=tk.Frame(self)
#     # frame = tk.Frame(root, option)
#     input_frame.pack(pady=10)#表示
#     tk.Label(input_frame,text="Task:").grid(row=0,column=0)#
#     self.task_entry=tk.Entry(input_frame,width=10)# 加えるだけ加える
#     self.task_entry.grid(row=0,column=1) #表示
#     # self.task_entry=tk.Entry(input_frame,width=10).grid(row=0,column=1)# セット(加える＋表示)

#     btn_frame=tk.Frame(self)
#     btn_frame.pack(pady=10)
#     tk.Button(btn_frame,text="add task",command=self.add_task).pack(side="left")
#     tk.Button(btn_frame,text="delete task",command=self.delete_task).pack(side="right")


#     # self.task_list=tk.Listbox(self,selectmode="multiple",bd=10)
#     # listbox = tk.Listbox(parent, options)
#     # self.task_list.pack(fill="both",expand=True)

#     # column=("bb","bbb")
#     self.tasks=[]
#     self.tree=ttk.Treeview(self,columns=(1,2,3))
#     self.tree.column("#0",width=0,stretch='no')
#     self.tree.column("1",anchor="center",width=100)
#     self.tree.column("2",anchor="center",width=100)
#     self.tree.column("3",anchor="center",width=100)
#     # self.tree=ttk.Treeview(self,columns=column)
#     # self.tree.heading("#0",text="")

#     self.tree.heading("1",text="a")
#     self.tree.heading("2",text="aa")
#     self.tree.heading("3",text="aaa")

#     self.tree.pack(pady=50)
#     self.tree.pack(fill="both",expand=True)

#     # combo_frame=tk.Frame(self.tree)

    
    
#     table_btn=tk.Frame(self.tree)
#     table_btn.pack(pady=10)
#     tk.Button(table_btn,text="button",command=self.test).pack(side="top")
#     self.tree.insert(parent="",index=0, iid=0, values=(1,11,111))

#     # combo_frame.pack(pady=10)
#     list_frame= ttk.LabelFrame(self,text="list_frame")
#     idPathLabel=ttk.Label(list_frame,text="idPathLabel")
#     idPathLabel.grid(column=0,row=0)

#     namePathLabel=ttk.Label(list_frame,text="namePathLabel")
#     namePathLabel.grid(column=1,row=0)

#     id=ttk.Label(list_frame,text="id")
#     id.grid(column=0,row=1)

#     combobox = ttk.Combobox(list_frame,width=7 ,height=3,value=('a','b','c'))
#     combobox.grid(column=1,row=1)
#     # name=ttk.Label(list_frame,text="name")
#     # name.grid(column=1,row=1)
    
#     list_frame.pack(pady=10)

#   def test(self):
#     # print("11")
#     selected = self.tree.focus()
#     item = self.tree.item(0)
#     # print(item)
#     # print(selected)

#     # tmp=self.tree.item(selected,'values')
#     tmp=self.tree.item("0",'values')
#     self.tree.insert(parent="",index=0,value=(tmp[1],tmp[2],tmp[0]))

#   def add_task(self):
#     task=self.task_entry.get()
#     if task:
#       self.tasks.append(task)
#       self.task_list.insert("end",task)
#       self.task_entry.delete(0,"end")
#   def delete_task(self):
#     selected_indices=self.task_list.curselection()
#     for index in selected_indices[::-1]:
#       self.task_list.delete(index)
#       self.tasks.pop(index)

    
# if __name__=="__main__":
#   app=Todoapp("title")
#   app.mainloop()
    



# # root.mainloop()


import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as tkmsg
import sys, os.path
# from pytube import YouTube

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.grid()
        self.create_widgets()
        master.title(u"ユーチューブ")
        master.geometry("720x480")

    def create_widgets(self):
        #リストボックス
        self.ListBox1 = tk.Listbox(self,height=10,width=108)
        self.ListBox1.grid(column=0,row=0,padx=5,pady=5)
        #スクロールバー
        self.scrollbar1 = tk.Scrollbar(self,orient=tk.VERTICAL,command=self.ListBox1.yview)
        self.ListBox1['yscrollcommand'] = self.scrollbar1.set
        self.scrollbar1.grid(column=1,row=0,sticky=tk.W+tk.N+tk.S)
        #ラベル
        self.Label1 = tk.Label(text=u'test')
        self.Label1.grid(column=0,row=1,pady=10,sticky=tk.W)
        #入力ボックス
        self.TextBox1 = tk.Entry(width=50)
        self.TextBox1.grid(column=0,row=2)
        copy_board = root.clipboard_get()
        self.TextBox1.insert(tk.END,copy_board)
        #ボタン１
        self.Button1 = tk.Button(text=u'URLを入力',width=20,command=self.button_click)
        self.Button1.grid(column=0,row=3,pady=5)
        #ボタン２
        self.Button2 = tk.Button(text=u'ダウンロード',width=20,command=self.button_click1)
        self.Button2.grid(column=0,row=4,pady=5)

    #URL入力の関数
    def button_click(self):
        Val = self.TextBox1.get()
        if Val == "":
            return
        self.Label1["text"] = Val + " を入力しました"
        # self.yt = YouTube(Val)
        for list_data in self.yt.streams.all():
            self.ListBox1.insert(tk.END,list_data)
        self.TextBox1.delete(0,tk.END)
        self.Label1["text"] = "itag番号を入力してダウンロードボタンを押してください"

    #ダウンロードの関数
    def button_click1(self):
        Val = self.TextBox1.get()
        if Val == "":
            return
        fTyp=[('動画ファイル','*.mp4;*.webm')]
        out_filename=filedialog.asksaveasfilename(filetypes=fTyp,initialfile=self.yt.title)
        if out_filename == "":
            return
        path_name,filename_only = os.path.split(out_filename)
        self.yt.streams.get_by_itag(int(Val)).download(output_path=path_name,filename=filename_only)
        tkmsg.showinfo( title = 'information', message = 'ダウンロードされました：')

#本体
if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


# styleNormal=ttk.Style()
# self.styleError=ttk.Style()
# style.configure(bd=-2)
# styleNormal.theme_use('default')
# styleNormal.configure("label.TEntry",foreground="blue")
# self.styleError.configure("error",backgraound="red")