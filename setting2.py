import tkinter as tk
from tkinter import messagebox
import os
import sys

CONFIG_FILE = "config.txt"
SETTING_FILE = "setting.txt"

# 1. データの初期準備
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write("再開時のカウントダウン,count_down,1\n")
        f.write("カウント時のブザー音,buzzer,0\n")
        f.write("途中のアナウンス,announce,0\n")

# 2. データの読み込み
items = []
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    for line in f:
        items.append(line.strip().split(","))

saved_vals = {}
if os.path.exists(SETTING_FILE):
    with open(SETTING_FILE, "r", encoding="utf-8") as f:
        for line in f:
            p = line.strip().split(",")
            saved_vals[p[0]] = int(p[1])

# --- 処理 ---
def save_setting():
    with open(SETTING_FILE, "w", encoding="utf-8") as f:
        for item in items:
            # item[2] は Tkinterの変数(IntVar)になっているので .get() で取得
            f.write(f"{item[1]},{item[2].get()}\n")
    messagebox.showinfo("完了", "設定を保存しました")

def open_edit():
    edit_win = tk.Toplevel(root)
    edit_win.title("項目編集")
    edit_win.geometry("400x450") # 縦長にして10行入るようにする

    entries = []
    # 項目編集画面では、ファイルから読み込んだ「元の文字列」を表示したい
    # 再度config.txtを読み直して表示用のリストを作るのが一番確実でシンプルです
    current_config = []
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            current_config.append(line.strip())

    for i in range(10):
        en = tk.Entry(edit_win, width=50)
        en.pack(pady=5, padx=10)
        # 既存の項目があれば流し込む
        if i < len(current_config):
            en.insert(0, current_config[i])
        entries.append(en)

    def update_config():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            for en in entries:
                val = en.get().strip()
                if val: f.write(val + "\n")
        os.execl(sys.executable, sys.executable, *sys.argv)

    tk.Button(edit_win, text="項目更新＆再起動", command=update_config).pack(pady=10)

# --- 画面作成 ---
root = tk.Tk()
root.title("設定")

# 編集ボタン
tk.Button(root, text="項目編集", command=open_edit).pack(anchor="e", padx=10, pady=5)

for item in items:
    val = saved_vals.get(item[1], int(item[2]))
    var = tk.IntVar(value=val)
    tk.Checkbutton(root, text=item[0], variable=var).pack(anchor="w", padx=20)
    # ここで item[2] が「数値」から「Tkinter変数」に置き換わる
    item[2] = var

tk.Button(root, text="設定更新", command=save_setting).pack(pady=10)

root.mainloop()