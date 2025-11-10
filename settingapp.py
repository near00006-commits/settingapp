import tkinter as tk
from tkinter import ttk, messagebox
import os
import csv
import sys # アプリケーションを再起動するためにsysモジュールを使用

# --- 1. 定数とグローバル変数 ---

# プログラムで必ず使用する基本の項目 (デフォルト)
DEFAULT_ITEMS = [
    ["再開時のカウントダウン", "count_down", "1"],
    ["カウント時のブザー音", "buzzer", "0"],
    ["途中のアナウンス", "announce", "0"]
]
# メモリファイル名
MEMORY_FILE = "item_config_memory.txt"
# 設定値ファイル名
SETTING_FILE = "count_down_settei.txt"

# 全ての項目データ を格納
all_items = []
# ラジオボタンの状態を保持するtk.IntVarの辞書
settings_vars = {}

# --- 2. ファイル操作関数 (変更なし) ---

def load_or_create_memory_file(root_dir):
    """メモリファイルを読み込み、存在しなければ作成してデフォルト値を書き込む。"""
    global all_items
    file_path = os.path.join(root_dir, MEMORY_FILE)
    
    # ... (前回のコードと同じ)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                all_items = [row for row in reader if row]
            if not all_items:
                all_items = list(DEFAULT_ITEMS)
                save_memory_file(root_dir)
        except Exception as e:
            messagebox.showerror("エラー", f"メモリファイルの読み込みに失敗しました: {e}\nデフォルト設定を使用します。")
            all_items = list(DEFAULT_ITEMS)
    else:
        all_items = list(DEFAULT_ITEMS)
        save_memory_file(root_dir)

def save_memory_file(root_dir):
    """現在の項目データをメモリファイルに書き込む。"""
    file_path = os.path.join(root_dir, MEMORY_FILE)
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(all_items)
        return True
    except Exception as e:
        messagebox.showerror("エラー", f"メモリファイルの書き込みに失敗しました: {e}")
        return False

# --- 3. メイン画面の定義 ---

def create_main_window():
    """項目設定（ラジオボタン）画面を作成・表示する"""
    root = tk.Tk()
    root.title("項目設定")
    
    root_dir = os.getcwd()
    load_or_create_memory_file(root_dir) # 起動時にメモリをロード

    # Xボタンでの終了処理
    root.protocol("WM_DELETE_WINDOW", lambda: handle_exit(root))

    # フレーム定義: Top (項目設定ボタン)、Main (ラジオボタン)、Bottom (更新・終了ボタン)
    top_frame = ttk.Frame(root, padding="10")
    top_frame.pack(fill='x', padx=10, pady=(10, 0))
    
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill='x', padx=10, pady=10) 
    
    button_frame = ttk.Frame(root, padding="10")
    button_frame.pack(fill='x', padx=10, pady=(0, 10))

    # --- Top Frame: 項目設定ボタン ---
    edit_button = ttk.Button(
        top_frame, 
        text="項目内容の編集", 
        command=lambda: open_edit_window(root, root_dir) # メインウィンドウを渡す
    )
    edit_button.pack(side=tk.LEFT)
    
    # --- Main Frame: ラジオボタンの構築 ---
    def setup_radio_buttons():
        """all_itemsの内容に基づいてラジオボタンを再構築する"""
        global settings_vars
        
        # 既存ウィジェットのクリア
        for widget in main_frame.winfo_children():
            widget.destroy()
            
        settings_vars.clear()
        
        # ヘッダー行
        ttk.Label(main_frame, text="設定項目", font='Arial 10 bold').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(main_frame, text="ON", font='Arial 10 bold').grid(row=0, column=1, sticky='w', padx=5, pady=5)
        ttk.Label(main_frame, text="OFF", font='Arial 10 bold').grid(row=0, column=2, sticky='w', padx=5, pady=5)

        # データを反復処理してウィジェットを作成・配置
        for row_index, row_data in enumerate(all_items):
            display_name, internal_name, default_value_str = row_data
            default_value = int(default_value_str) 
            
            var = tk.IntVar(value=default_value)
            settings_vars[internal_name] = var 
            
            ttk.Label(main_frame, text=display_name, anchor='w').grid(row=row_index + 1, column=0, sticky='w', padx=5, pady=2) 
            ttk.Radiobutton(main_frame, text="ON", variable=var, value=1).grid(row=row_index + 1, column=1, sticky='w', padx=5, pady=2)
            ttk.Radiobutton(main_frame, text="OFF", variable=var, value=0).grid(row=row_index + 1, column=2, sticky='w', padx=5, pady=2)

        # レイアウトの調整
        main_frame.grid_columnconfigure(0, weight=1) 
        main_frame.grid_columnconfigure(1, weight=0)
        main_frame.grid_columnconfigure(2, weight=0)
        
    setup_radio_buttons() # 初回構築

    # --- Bottom Frame: 更新・終了ボタン ---
    update_button = ttk.Button(
        button_frame, 
        text="更新 (設定値保存)", 
        command=lambda: handle_update(root_dir)
    )
    update_button.pack(side=tk.LEFT, fill='x', expand=True, padx=5) 

    exit_button = ttk.Button(
        button_frame, 
        text="終了", 
        command=lambda: handle_exit(root)
    )
    exit_button.pack(side=tk.RIGHT, fill='x', expand=True, padx=5)

    # アプリケーションのメインループを開始
    root.mainloop()

# --- 4. 項目内容編集ウィンドウの定義 ---

def open_edit_window(main_root, root_dir):
    """項目内容の編集画面（サブウィンドウ）を表示する"""
    edit_window = tk.Toplevel(main_root) # Toplevelでサブウィンドウを作成
    edit_window.title("項目内容の編集")
    
    # (中略：編集画面のウィジェット定義、temp_itemsの操作などは前コードと同じ)
    # ... Listbox, Entry, Add/Delete Buttons ...

    edit_frame = ttk.Frame(edit_window, padding="10")
    edit_frame.pack(fill='both', expand=True)
    
    # データを一時的にコピーして編集する 
    temp_items = [list(item) for item in all_items]
    
    # ListboxとScrollbarを配置
    listbox_frame = ttk.Frame(edit_frame)
    listbox_frame.pack(fill='both', expand=True, pady=(0, 10))
    
    scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
    listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, width=60, height=10)
    scrollbar.config(command=listbox.yview)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Listboxにデータを表示する関数
    def refresh_listbox():
        listbox.delete(0, tk.END)
        # ヘッダー行
        listbox.insert(tk.END, f"{'No':<4} {'表示名':<15} {'内部項目名':<15} {'デフォルト値':<5}")
        listbox.itemconfig(0, {'bg': 'lightgray'})
        
        # データ行
        for i, item in enumerate(temp_items):
            display, internal, default = item
            listbox.insert(tk.END, f"{i+1:<4} {display:<15} {internal:<15} {default:<5}")
            
    refresh_listbox()

    # --- 編集・追加・削除機能 ---
    
    # 項目追加用の入力欄
    input_frame = ttk.Frame(edit_frame)
    input_frame.pack(fill='x', pady=5)
    
    ttk.Label(input_frame, text="表示名:").pack(side=tk.LEFT)
    entry_display = ttk.Entry(input_frame, width=15)
    entry_display.pack(side=tk.LEFT, padx=(0, 5))
    
    ttk.Label(input_frame, text="内部名:").pack(side=tk.LEFT)
    entry_internal = ttk.Entry(input_frame, width=15)
    entry_internal.pack(side=tk.LEFT, padx=(0, 5))
    
    ttk.Label(input_frame, text="デフ(0/1):").pack(side=tk.LEFT)
    entry_default = ttk.Entry(input_frame, width=5)
    entry_default.pack(side=tk.LEFT, padx=(0, 5))

    def add_item():
        display = entry_display.get().strip()
        internal = entry_internal.get().strip()
        default = entry_default.get().strip()
        
        # 内部項目名の重複チェック
        internal_names = [item[1] for item in temp_items]
        if internal in internal_names:
            messagebox.showwarning("入力エラー", "内部項目名が重複しています。")
            return

        if display and internal and default in ('0', '1'):
            temp_items.append([display, internal, default])
            refresh_listbox()
            entry_display.delete(0, tk.END)
            entry_internal.delete(0, tk.END)
            entry_default.delete(0, tk.END)
        else:
            messagebox.showwarning("入力エラー", "すべての項目を入力し、デフォルト値は0または1にしてください。")

    def delete_item():
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "削除する項目を選択してください。")
            return
        
        # 選択された行のインデックスを取得 (ヘッダー行を除くため -1)
        selected_row = selected_indices[0] - 1
        
        if selected_row < 0 or selected_row < len(DEFAULT_ITEMS):
             messagebox.showwarning("警告", "デフォルトの基本項目は削除できません。")
             return

        # 逆順に削除することでインデックスのずれを防ぐ
        del temp_items[selected_row]
        refresh_listbox()

    action_frame = ttk.Frame(edit_frame)
    action_frame.pack(fill='x', pady=5)
    ttk.Button(action_frame, text="項目追加", command=add_item).pack(side=tk.LEFT, padx=5)
    ttk.Button(action_frame, text="選択項目削除", command=delete_item).pack(side=tk.LEFT, padx=5)
    
    # --- 編集画面の更新・終了ボタン ---
    edit_button_frame = ttk.Frame(edit_frame, padding="10")
    edit_button_frame.pack(fill='x', pady=(10, 0))

    def handle_edit_update():
        """編集画面の更新処理：メモリファイルを更新し、アプリケーションを再起動する"""
        global all_items
        
        if len(temp_items) < len(DEFAULT_ITEMS):
            messagebox.showwarning("警告", "項目数はデフォルト項目数未満にはできません。")
            return
        
        # グローバルデータとメモリファイルを更新
        all_items = temp_items 
        if save_memory_file(root_dir):
            messagebox.showinfo("完了", "項目内容を更新しました。\n変更を反映するため、アプリケーションを再起動します。")
            
            # アプリケーションを終了し、再起動させる
            main_root.destroy() # メインウィンドウを完全に閉じる
            restart_application() # アプリケーション再起動を試みる関数を呼び出す
            
    ttk.Button(edit_button_frame, text="更新 (メモリファイル保存)", command=handle_edit_update).pack(side=tk.LEFT, fill='x', expand=True, padx=5)
    ttk.Button(edit_button_frame, text="終了 (編集破棄)", command=edit_window.destroy).pack(side=tk.RIGHT, fill='x', expand=True, padx=5)

# --- 5. 更新・終了処理関数 (変更なし) ---

def handle_update(root_dir):
    """項目設定画面の更新ボタン処理：設定値ファイルを更新する"""
    # ... (前回のコードと同じ)
    response = messagebox.askyesno("確認", "設定値を更新しますか？")
    
    if response:
        current_settings = {}
        for name, var in settings_vars.items():
            current_settings[name] = var.get()
        
        file_path = os.path.join(root_dir, SETTING_FILE) 
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for internal_name, value in current_settings.items():
                    string_value = "ON" if value == 1 else "OFF"
                    f.write(f"{internal_name}={string_value}\n")
            
            messagebox.showinfo("完了", f"設定値をファイルに書き込みました:\n{file_path}")
            
        except IOError as e:
            messagebox.showerror("エラー", f"ファイルの書き込みに失敗しました: {e}")

def handle_exit(root_window):
    """終了ボタン処理：アプリケーションを終了する"""
    # ... (前回のコードと同じ)
    response = messagebox.askyesno("確認", "アプリケーションを終了しますか？")
    if response:
        root_window.quit()
        
# --- 6. 再起動処理 ---

def restart_application():
    """現在のPythonスクリプトを再実行してアプリケーションを再起動する"""
    # 現在のスクリプトの実行ファイルパスを取得
    python = sys.executable
    # 現在のスクリプトのパスを取得
    script = os.path.abspath(sys.argv[0])
    
    # 新しいプロセスとしてアプリケーションを起動
    os.execl(python, python, script)

# --- 7. アプリケーションの実行 ---

if __name__ == "__main__":
    create_main_window()