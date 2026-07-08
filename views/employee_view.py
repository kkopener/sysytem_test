import streamlit as st
import pandas as pd
from datetime import date
import calendar
from services import csv_manager

def employee_dashboard(base_dir):
    st.title("従業員ダッシュボード")
    shop_code = st.session_state['shop_code']
    emp_id = st.session_state['emp_id']
    st.write(f"ログイン: **{st.session_state['name']}** さん (店舗: {shop_code})")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 対象年月")
    if "target_month" not in st.session_state:
        st.session_state["target_month"] = "2026-07"
    months_options = [f"2026-{str(i).zfill(2)}" for i in range(1, 13)]
    target_month = st.sidebar.selectbox("表示する年月を選択", options=months_options, index=months_options.index(st.session_state["target_month"]))
    st.session_state["target_month"] = target_month

    tab_view, tab_req = st.tabs(["📅 シフト閲覧", "📝 休み希望提出"])

    with tab_view:
        st.subheader(f"✨ {target_month} の確定シフト")
        
        pub_file = os.path.join(base_dir, str(shop_code).zfill(3), target_month, "published.txt")
        if not os.path.exists(pub_file):
            st.warning("⚠️ 現在、対象月のシフトは編集中のため未公開です。管理者の公開をお待ちください。")
        else:
            df_roster = csv_manager.load_roster(base_dir, shop_code, target_month)
            if df_roster is not None and not df_roster.empty:
                st.dataframe(df_roster, use_container_width=True, hide_index=True)
                
                try:
                    y, m = map(int, target_month.split("-"))
                    _, total_days = calendar.monthrange(y, m)
                    all_days_list = [str(i) for i in range(1, total_days + 1)]
                    matrix_df = df_roster.pivot(index="氏名", columns="日", values="時間枠").fillna("-")
                    for day_col in all_days_list:
                        if day_col not in matrix_df.columns: matrix_df[day_col] = "-"
                    st.markdown("### 📊 全体シフト表")
                    st.dataframe(matrix_df[all_days_list], use_container_width=True)
                except Exception:
                    pass
            else:
                st.info("確定したシフトはありません。")

    with tab_req:
        st.subheader("📝 休み希望の提出・変更")
        df_my_req = csv_manager.load_holiday_requests(base_dir, shop_code)
        if not df_my_req.empty:
            df_my_req = df_my_req[df_my_req["従業員ID"] == str(emp_id).strip()]
            
        try:
            y, m = map(int, target_month.split("-"))
            _, total_days = calendar.monthrange(y, m)
            date_options = [date(y, m, d) for d in range(1, total_days + 1)]
        except Exception:
            date_options = []
            
        with st.form("req_form"):
            sel_dates = st.multiselect("希望休の日付", options=date_options, format_func=lambda x: x.strftime("%m/%d(%a)"))
            memo = st.text_input("備考")
            if st.form_submit_button("希望を提出・更新する"):
                if not sel_dates: st.warning("日付を選択してください。")
                else:
                    success, msg = csv_manager.save_holiday_request_to_file(base_dir, shop_code, emp_id, st.session_state['name'], sel_dates, memo)
                    if success: st.success(msg); time.sleep(0.5); st.rerun()
                    else: st.error(msg)

        st.markdown("### 📋 あなたが提出済みの希望休一覧")
        if not df_my_req.empty:
            df_my_req_sorted = df_my_req.sort_values("日付")
            st.dataframe(df_my_req_sorted[["日付", "備考"]], use_container_width=True, hide_index=True)
            with st.expander("🗑️ 希望を1日ずつ取り消す"):
                cancel_target_date = st.selectbox("取り消したい日付を選択", options=df_my_req_sorted["日付"].values)
                if st.button("選択した希望を取り消す"):
                    success, msg = csv_manager.delete_holiday_request_from_file(base_dir, shop_code, emp_id, cancel_target_date)
                    if success: st.success(msg); time.sleep(0.5); st.rerun()
                    else: st.error(msg)
        else:
            st.info("提出済みの希望休はありません。")