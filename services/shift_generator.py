import pandas as pd
from datetime import date
import calendar
from services import csv_manager

def check_time_coverage(df_day_roster, open_time_str, close_time_str):
    try:
        open_h = int(open_time_str.split(":")[0])
        close_h = int(close_time_str.split(":")[0])
    except Exception:
        return "⚠️店舗営業時間の設定が不正です"
        
    required_hours = set(range(open_h, close_h))
    covered_hours = set()
    
    for _, row in df_day_roster.iterrows():
        try:
            time_frame = str(row["時間枠"]).strip()
            if "-" in time_frame:
                start_str, end_str = time_frame.split("-")
                sh = int(start_str.split(":")[0])
                eh = int(end_str.split(":")[0])
                covered_hours.update(range(sh, eh))
        except Exception:
            continue
            
    missing_hours = required_hours - covered_hours
    if not missing_hours:
        return "充足"
        
    missing_list = sorted(list(missing_hours))
    intervals = []
    if missing_list:
        start = missing_list[0]
        end = start
        for h in missing_list[1:]:
            if h == end + 1:
                end = h
            else:
                intervals.append(f"{str(start).zfill(2)}:00-{str(end+1).zfill(2)}:00")
                start = h
                end = h
        intervals.append(f"{str(start).zfill(2)}:00-{str(end+1).zfill(2)}:00")
        return "⚠️不足: " + ", ".join(intervals)
    return "充足"

def generate_monthly_shift(base_dir, shop_code, target_month):
    try:
        year, month = map(int, target_month.split("-"))
    except Exception:
        return False, "年月フォーマットが不正です"
        
    df_emp = csv_manager.load_employees(base_dir, shop_code)
    if df_emp is None or df_emp.empty:
        return False, "従業員マスタデータが存在しません。"
        
    df_req = csv_manager.load_holiday_requests(base_dir, shop_code)
    
    _, total_days = calendar.monthrange(year, month)
    roster_records = []
    
    from collections import defaultdict
    weekly_counts = defaultdict(lambda: defaultdict(int))
    
    for d in range(1, total_days + 1):
        current_date = date(year, month, d)
        date_str = current_date.strftime("%Y-%m-%d")
        day_str = str(d)
        
        days_map = ["月", "火", "水", "木", "金", "土", "日"]
        day_of_week = days_map[current_date.weekday()]
        iso_week = current_date.isocalendar()[1]
        
        for _, emp in df_emp.iterrows():
            emp_id = str(emp["従業員ID"]).strip()
            name = str(emp["氏名"]).strip()
            
            if not df_req.empty:
                is_holiday = df_req[(df_req["従業員ID"] == emp_id) & (df_req["日付"] == date_str)]
                if not is_holiday.empty:
                    continue
                    
            normal_days = [d.strip() for d in str(emp.get("通常出勤曜日", "")).split(",") if d.strip()]
            extra_days = [d.strip() for d in str(emp.get("追加可能曜日", "")).split(",") if d.strip()]
            ng_days = [d.strip() for d in str(emp.get("絶対NG曜日", "")).split(",") if d.strip()]
            
            if day_of_week in ng_days:
                continue
                
            raw_max = str(emp.get("週最大出勤日数", "7")).strip()
            max_days = int(raw_max) if raw_max.isdigit() else 7
            allow_over = str(emp.get("週制限超過許可", "0"))
            
            if allow_over == "0" and weekly_counts[emp_id][iso_week] >= max_days:
                continue 
                
            time_frame = None
            if day_of_week in normal_days:
                time_frame = f"{emp.get('通常開始時刻', '10:00')}-{emp.get('通常終了時刻', '19:00')}"
            elif day_of_week in extra_days:
                time_frame = f"{emp.get('追加可能開始時刻', '10:00')}-{emp.get('追加可能終了時刻', '19:00')}"
                
            # 未成年深夜労働(22:00以降)の自動除外制約
            if time_frame and str(emp.get("未成年フラグ", "0")) == "1":
                try:
                    end_str = time_frame.split("-")[1].strip()
                    end_h = int(end_str.split(":")[0])
                    end_m = int(end_str.split(":")[1]) if ":" in end_str else 0
                    if end_h > 22 or (end_h == 22 and end_m > 0):
                        time_frame = None
                except Exception:
                    pass
                
            if time_frame:
                roster_records.append({
                    "店舗コード": str(shop_code).zfill(3),
                    "日付": date_str,
                    "日": day_str,
                    "曜日": day_of_week,
                    "従業員ID": emp_id,
                    "氏名": name,
                    "時間枠": time_frame,
                    "経験者フラグ": emp.get("経験者フラグ", "0"),
                    "未成年フラグ": emp.get("未成年フラグ", "0")
                })
                weekly_counts[emp_id][iso_week] += 1
                
    if not roster_records:
        return False, "条件に一致するシフトを1件も生成できませんでした。"
        
    df_new_roster = pd.DataFrame(roster_records)
    success, msg = csv_manager.save_roster_directly(base_dir, shop_code, target_month, df_new_roster)
    return success, msg if not success else "シフトを自動生成しました。"