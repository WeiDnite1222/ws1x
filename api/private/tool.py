import requests
from fastapi import Request

def check_server_2_status():
    try:
        r = requests.get("https://storage.weispace.net/")

        if r.status_code == 200:
            return True
        else:
            return False

    except Exception as error:
        print("[警告] 伺服器2號機可能出現異常。 {}".format(error))
        return False

def get_articles_index_data():
    try:
        r = requests.get("https://storage.weispace.net/main-sites/post/index.json")
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except Exception as error:
        print("[錯誤] 無法取得文章索引資料! {}".format(error))
        return None

def get_server_message_data():
    try:
        r = requests.get("https://storage.weispace.net/main-sites/server/message-global.json")
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except Exception as error:
        print("[錯誤] 無法取得伺服器訊息! {}".format(error))
        return None