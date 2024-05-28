from typing import List
import sqlite3
import os
import secrets



class Client:
    client_id:int
    redirect_prefix:str
    allowed_scope:List[str]
    def __init__(self,client_id:str,redirect_prefix:str,allowed_scope:List[str]) -> None:
        self.client_id=client_id
        self.redirect_prefix=redirect_prefix
        self.allowed_scope=allowed_scope
def getClientById(client_id: str) -> Client:
    # SQLiteデータベースに接続
    db_path = './db/clients.db'
    # ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    # SQLiteデータベースに接続
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("searching client by id:", str(client_id))
    # ユーザー名とパスワードを使ってユーザーを検索
    cursor.execute("SELECT * FROM clients WHERE client_id = ?",
                   (str(client_id),))
    client = cursor.fetchone()
        # データベース接続を閉じる
    conn.close()
    modeledClient=Client(client[0],client[1],client[2])
    print("fetched client by id: ", modeledClient)
    return modeledClient


def seed_user_data():
    # SQLiteデータベースに接続
    conn = sqlite3.connect('./db/clients.db')
    cursor = conn.cursor()

    # ユーザーテーブルが存在しない場合は作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            redirect_prefix TEXT NOT NULL,
            allowed_scope TEXT NOT NULL
        )
    ''')
    cursor.execute('SELECT * FROM clients WHERE client_id = ?', ('1'))
    user = cursor.fetchone()

    if not user:
        cursor.execute('INSERT INTO clients (redirect_prefix,allowed_scope) VALUES ( ?, ?)',
                       ('http://localhost/', 'read'))
        # 変更をコミットしてデータベース接続を閉じる
        conn.commit()
        conn.close()


# シード関数を呼び出す
seed_user_data()
