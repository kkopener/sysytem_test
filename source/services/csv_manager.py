import os
import pandas as pd
from database import storage

def load_shop_settings(base_dir, shop_code):
    settings_file = os.path.join(base_dir, str(shop_code).zfill(3), "shop_settings.csv")
    df = storage.read_csv_safe(settings_file)
    if not df.empty:
        return df.iloc[0]
    return {"店舗コード": str(shop_code).zfill(3), "開店時間": "09:00", "閉店時間": "21:00"}

def save_shop_settings(base_dir, shop_code, open_time, close_time):
    settings_file = os.path.join(base_dir, str(shop_code).zfill(3), "shop_settings.csv")
    df = pd.DataFrame([{"店舗コード": str(shop_code).zfill(3), "開店時間": open_time, "閉店時間": close_time}])
    success, msg = storage.write_csv_safe(settings_file, df)
    return success, msg if not success else "営業時間を保存しました。"

def load_employees(base_dir, shop_code):
    emp_file = os.path.join(base_dir, str(shop_code).zfill(3), "employees.csv")
    df = storage.read_csv_safe(emp_file, None)
    if df is not None:
        df = df.dropna(subset=["従業員ID", "氏名"])
        df = df[df["従業員ID"].astype(str).str.strip() != ""]
        df["店舗コード"] = df["店舗コード"].astype(str).str.strip().str.zfill(3)
        df["従業員ID"] = df["従業員ID"].astype(str).str.strip()
        df["パスワード"] = df["パスワード"].astype(str).str.strip()
        return df
    return None

def load_holiday_requests(base_dir, shop_code):
    req_file = os.path.join(base_dir, str(shop_code).zfill(3), "holiday_requests.csv")
    df = storage.read_csv_safe(req_file, pd.DataFrame(columns=["店舗コード", "従業員ID", "氏名", "日付", "備考"]))
    if not df.empty:
        df = df.dropna(subset=["従業員ID", "日付"])
        df = df[df["従業員ID"].astype(str).str.strip() != ""]
        df["店舗コード"] = df["店舗コード"].astype(str).str.strip().str.zfill(3)
        df["日付"] = pd.to_datetime(df["日付"], errors='coerce').dt.strftime("%Y-%m-%d")
        df = df.dropna(subset=["日付"])
    return df

def save_holiday_request_to_file(base_dir, shop_code, emp_id, name, selected_dates, memo):
    req_file = os.path.join(base_dir, str(shop_code).zfill(3), "holiday_requests.csv")
    df_req = load_holiday_requests(base_dir, shop_code)
    new_rows = []
    for d in selected_dates:
        new_rows.append({
            "店舗コード": str(shop_code).zfill(3),
            "従業員ID": str(emp_id).strip(),
            "氏名": name,
            "日付": d.strftime("%Y-%m-%d"),
            "備考": memo
        })
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df_req = pd.concat([df_req, df_new], ignore_index=True)
        df_req["店舗コード"] = df_req["店舗コード"].astype(str).str.strip().str.zfill(3)
        df_req = df_req.drop_duplicates(subset=["店舗コード", "従業員ID", "日付"], keep="last")
        success, msg = storage.write_csv_safe(req_file, df_req)
        return success, msg if not success else "休み希望を正常に保存しました！"
    return False, "日付が選択されていません。"

def remove_holiday_request_from_file(base_dir, shop_code, emp_id, target_date_str):
    req_file = os.path.join(base_dir, str(shop_code).zfill(3), "holiday_requests.csv")
    df_req = load_holiday_requests(base_dir, shop_code)
    if not df_req.empty:
        df_req = df_req[~(
            (df_req["店舗コード"] == str(shop_code).zfill(3)) & 
            (df_req["従業員ID"] == str(emp_id).strip()) & 
            (df_req["日付"] == str(target_date_str))
        )]
        success, msg = storage.write_csv_safe(req_file, df_req)
        return success, msg if not success else "休み希望を取り消しました。"
    return False, "対象データがありません。"

def load_roster(base_dir, shop_code, target_month):
    roster_file = os.path.join(base_dir, str(shop_code).zfill(3), target_month, "roster.csv")
    if os.path.exists(roster_file):
        df = storage.read_csv_safe(roster_file, None)
        if df is not None:
            df = df.dropna(subset=["従業員ID", "氏名", "日付"])
            df = df[df["従業員ID"].str.strip() != ""]
            return df
    return None

def save_roster_directly(base_dir, shop_code, target_month, df_roster):
    target_dir = os.path.join(base_dir, str(shop_code).zfill(3), target_month)
    roster_file = os.path.join(target_dir, "roster.csv")
    if df_roster is not None and not df_roster.empty:
        df_roster = df_roster.dropna(subset=["従業員ID", "氏名", "日付"])
        success, msg = storage.write_csv_safe(roster_file, df_roster)
        return success, msg if not success else "シフトをCSVに保存しました！"
    else:
        success, msg = storage.delete_file_safe(roster_file)
        return success, msg if not success else "空のシフトファイルを削除しました。"