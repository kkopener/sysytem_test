import os
import time
import pandas as pd

def read_csv_safe(file_path, default_df=None):
    if os.path.exists(file_path):
        for _ in range(3): 
            try:
                return pd.read_csv(file_path, dtype=str)
            except Exception:
                time.sleep(0.3)
    return default_df if default_df is not None else pd.DataFrame()

def write_csv_safe(file_path, df):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        time.sleep(0.2)
        return True, ""
    except PermissionError:
        return False, "⚠️ CSVファイルが【Excel】等で開かれているため保存できません。Excelを閉じてください。"
    except Exception as e:
        return False, f"⚠️ 保存エラーが発生しました: {e}"

def delete_file_safe(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True, ""
        except PermissionError:
            return False, "⚠️ CSVファイルが【Excel】等で開かれているため削除できません。"
    return True, ""