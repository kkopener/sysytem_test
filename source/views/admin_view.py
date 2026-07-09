import streamlit as st
import pandas as pd
import os
import time
from services import csv_manager, shift_generator

def admin_dashboard(base_dir):
    st.title("管理者ダッシュボード")
    shop_code = st.session_state['shop_code']
    st.write(f"現在の管理店舗: **{shop_code}**")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 シフト対象年月")
    if "target_month" not in st.session_state:
        st.session_state["target_month"] = "2026-07"
        
    months_options = [f"2026-{str(i).zfill(2)}" for i in range(1, 13)]
    target_month = st.sidebar.selectbox("編集・生成する年月を選択", options=months_options, index=months_options.index(st.session_state["target_month"]))
    st.session_state["target_month"] = target_month
    
    settings = csv_manager.load_shop_settings(base_dir, shop_code)
    with st.sidebar.expander("⚙️ 店舗営業時間の設定", expanded=False):
        open_time = st.text_input("開店時間 (hh:mm)", value=settings["開店時間"])
        close_time = st.text_input("閉店時間 (hh:mm)", value=settings["閉店時間"])
        if st.button("営業時間を保存"):
            try:
                oh = int(open_time.split(":")[0])
                ch = int(close_time.split(":")[0])
                if ch <= oh:
                    st.error("⚠️ 閉店時間は開店時間より後に設定してください。")
                else:
                    success, msg = csv_manager.save_shop_settings(base_dir, shop_code, open_time, close_time)
                    if success: st.success(msg); time.sleep(0.5); st.rerun()
                    else: st.error(msg)
            except Exception:
                st.error("⚠️ 正しい時間形式(hh:mm)で入力してください。")

    tab_roster, tab_emp = st.tabs(["📅 シフト自動生成・手動微調整", "👥 従業員マスタ管理"])
    df_emp = csv_manager.load_employees(base_dir, shop_code)
    
    with tab_emp:
        st.subheader("👥 従業員マスタ一覧")
        if df_emp is not None and not df_emp.empty:
            st.dataframe(df_emp, use_container_width=True)
        else:
            st.info("従業員が登録されていません。")
            
        with st.expander("➕ 従業員・管理者を追加する"):
            with st.form("add_emp_form"):
                new_id = st.text_input("従業員ID")
                new_pass = st.text_input("パスワード", type="password")
                new_name = st.text_input("氏名")
                new_role = st.selectbox("役割", options=["staff", "admin"])
                
                days_list = ["月", "火", "水", "木", "金", "土", "日"]
                
                st.write("通常出勤曜日")
                cols_n = st.columns(7)
                n_days_checked = [day for i, day in enumerate(days_list) if cols_n[i].checkbox(day, key=f"n_{day}", value=(day in ["月", "火", "水", "木", "金"]))]
                
                t_start = st.text_input("通常開始時刻", value="09:00")
                t_end = st.text_input("通常終了時刻", value="18:00")
                
                st.write("追加可能曜日")
                cols_e = st.columns(7)
                e_days_checked = [day for i, day in enumerate(days_list) if cols_e[i].checkbox(day, key=f"e_{day}")]
                
                e_start = st.text_input("追加可能開始時刻", value="")
                e_end = st.text_input("追加可能終了時刻", value="")
                
                st.write("絶対NG曜日")
                cols_ng = st.columns(7)
                ng_days_checked = [day for i, day in enumerate(days_list) if cols_ng[i].checkbox(day, key=f"ng_{day}")]
                
                max_d = st.text_input("週最大出勤日数", value="5")
                allow_ov = st.selectbox("週制限超過許可", options=["0", "1"])
                exp_flg = st.selectbox("経験者フラグ", options=["0", "1"])
                min_flg = st.selectbox("未成年フラグ", options=["0", "1"])
                
                if st.form_submit_button("追加する"):
                    normal_days = ",".join(n_days_checked)
                    extra_days = ",".join(e_days_checked)
                    ng_days = ",".join(ng_days_checked)

                    n_list = [x.strip() for x in normal_days.split(",") if x.strip()]
                    e_list = [x.strip() for x in extra_days.split(",") if x.strip()]
                    ng_list = [x.strip() for x in ng_days.split(",") if x.strip()]
                    
                    n_set = set(n_list)
                    e_set = set(e_list)
                    ng_set = set(ng_list)

                    if not new_id.strip() or not new_pass.strip() or not new_name.strip():
                        st.error("⚠️ 従業員ID、パスワード、氏名は必須項目です。")
                    elif (n_list and (not t_start.strip() or not t_end.strip())) or ((t_start.strip() or t_end.strip()) and not n_list):
                        st.error("⚠️ 通常出勤曜日を設定する場合は通常開始・終了時刻も入力してください。また、時刻を入力する場合は曜日も設定してください。")
                    elif t_start.strip() and t_end.strip() and t_start.strip() >= t_end.strip():
                        st.error("⚠️ 通常開始時刻は通常終了時刻より前の時間を指定してください。")
                    elif (e_list and (not e_start.strip() or not e_end.strip())) or ((e_start.strip() or e_end.strip()) and not e_list):
                        st.error("⚠️ 追加可能曜日を設定する場合は追加可能開始・終了時刻も入力してください。また、時刻を入力する場合は曜日も設定してください。")
                    elif e_start.strip() and e_end.strip() and e_start.strip() >= e_end.strip():
                        st.error("⚠️ 追加可能開始時刻は追加可能終了時刻より前の時間を指定してください。")
                    elif len(n_list) != len(n_set):
                        st.error("⚠️ 通常出勤曜日に同じ曜日が複数回登録されています。")
                    elif len(e_list) != len(e_set):
                        st.error("⚠️ 追加可能曜日に同じ曜日が複数回登録されています。")
                    elif len(ng_list) != len(ng_set):
                        st.error("⚠️ 絶対NG曜日に同じ曜日が複数回登録されています。")
                    elif n_set & e_set:
                        st.error("⚠️ 通常出勤曜日と追加可能曜日に同じ曜日が設定されています。")
                    elif n_set & ng_set:
                        st.error("⚠️ 通常出勤曜日と絶対NG曜日に同じ曜日が設定されています。")
                    elif e_set & ng_set:
                        st.error("⚠️ 追加可能曜日と絶対NG曜日に同じ曜日が設定されています。")
                    elif str(max_d).isdigit() and len(n_set) > int(max_d):
                        st.error("⚠️ 通常出勤曜日の日数が、週最大出勤日数を超えています。")
                    elif df_emp is not None and new_id.strip() in df_emp["従業員ID"].astype(str).values:
                        st.error("⚠️ 既に存在する従業員IDです。")
                    else:
                        new_row = {
                            "店舗コード": str(shop_code).zfill(3), "従業員ID": new_id.strip(), "パスワード": new_pass.strip(),
                            "氏名": new_name.strip(), "役割": new_role, "通常出勤曜日": normal_days,
                            "通常開始時刻": t_start, "通常終了時刻": t_end, "追加可能曜日": extra_days,
                            "追加可能開始時刻": e_start, "追加可能終了時刻": e_end, "絶対NG曜日": ng_days,
                            "週最大出勤日数": max_d, "週制限超過許可": allow_ov, "経験者フラグ": exp_flg, "未成年フラグ": min_flg
                        }
                        if df_emp is None:
                            df_emp = pd.DataFrame([new_row])
                        else:
                            df_emp = pd.concat([df_emp, pd.DataFrame([new_row])], ignore_index=True)
                        csv_manager.save_employees_directly(base_dir, shop_code, df_emp)
                        st.success("従業員を追加しました。")
                        time.sleep(0.5)
                        st.rerun()
                        
        with st.expander("✏️ 従業員情報を編集する"):
            if df_emp is not None and not df_emp.empty:
                edit_id = st.selectbox("編集する従業員を選択", options=df_emp["従業員ID"].values, key="edit_select")
                target_emp = df_emp[df_emp["従業員ID"] == edit_id].iloc[0]
                
                with st.form("edit_emp_form"):
                    edit_pass = st.text_input("パスワード", value=str(target_emp.get("パスワード", "")), type="password")
                    edit_name = st.text_input("氏名", value=str(target_emp.get("氏名", "")))
                    
                    roles = ["staff", "admin"]
                    current_role = str(target_emp.get("役割", "staff"))
                    edit_role = st.selectbox("役割", options=roles, index=roles.index(current_role) if current_role in roles else 0)
                    
                    days_list = ["月", "火", "水", "木", "金", "土", "日"]
                    
                    st.write("通常出勤曜日")
                    cols_n_e = st.columns(7)
                    curr_n_list = str(target_emp.get("通常出勤曜日", "")).split(",")
                    n_days_checked_e = [day for i, day in enumerate(days_list) if cols_n_e[i].checkbox(day, key=f"e_n_{day}", value=(day in curr_n_list))]
                    
                    edit_t_start = st.text_input("通常開始時刻", value=str(target_emp.get("通常開始時刻", "")))
                    edit_t_end = st.text_input("通常終了時刻", value=str(target_emp.get("通常終了時刻", "")))
                    
                    st.write("追加可能曜日")
                    cols_e_e = st.columns(7)
                    curr_e_list = str(target_emp.get("追加可能曜日", "")).split(",")
                    e_days_checked_e = [day for i, day in enumerate(days_list) if cols_e_e[i].checkbox(day, key=f"e_e_{day}", value=(day in curr_e_list))]
                    
                    edit_e_start = st.text_input("追加可能開始時刻", value=str(target_emp.get("追加可能開始時刻", "")))
                    edit_e_end = st.text_input("追加可能終了時刻", value=str(target_emp.get("追加可能終了時刻", "")))
                    
                    st.write("絶対NG曜日")
                    cols_ng_e = st.columns(7)
                    curr_ng_list = str(target_emp.get("絶対NG曜日", "")).split(",")
                    ng_days_checked_e = [day for i, day in enumerate(days_list) if cols_ng_e[i].checkbox(day, key=f"e_ng_{day}", value=(day in curr_ng_list))]
                    
                    edit_max_d = st.text_input("週最大出勤日数", value=str(target_emp.get("週最大出勤日数", "5")))
                    
                    ov_opts = ["0", "1"]
                    curr_ov = str(target_emp.get("週制限超過許可", "0"))
                    edit_allow_ov = st.selectbox("週制限超過許可", options=ov_opts, index=ov_opts.index(curr_ov) if curr_ov in ov_opts else 0, key="e_ov")
                    
                    curr_exp = str(target_emp.get("経験者フラグ", "0"))
                    edit_exp_flg = st.selectbox("経験者フラグ", options=ov_opts, index=ov_opts.index(curr_exp) if curr_exp in ov_opts else 0, key="e_exp")
                    
                    curr_min = str(target_emp.get("未成年フラグ", "0"))
                    edit_min_flg = st.selectbox("未成年フラグ", options=ov_opts, index=ov_opts.index(curr_min) if curr_min in ov_opts else 0, key="e_min")
                    
                    if st.form_submit_button("更新する"):
                        normal_days_e = ",".join(n_days_checked_e)
                        extra_days_e = ",".join(e_days_checked_e)
                        ng_days_e = ",".join(ng_days_checked_e)
                        
                        n_list_e = [x.strip() for x in normal_days_e.split(",") if x.strip()]
                        e_list_e = [x.strip() for x in extra_days_e.split(",") if x.strip()]
                        ng_list_e = [x.strip() for x in ng_days_e.split(",") if x.strip()]
                        
                        n_set_e = set(n_list_e)
                        e_set_e = set(e_list_e)
                        ng_set_e = set(ng_list_e)

                        if not edit_pass.strip() or not edit_name.strip():
                            st.error("⚠️ パスワード、氏名は必須項目です。")
                        elif (n_list_e and (not edit_t_start.strip() or not edit_t_end.strip())) or ((edit_t_start.strip() or edit_t_end.strip()) and not n_list_e):
                            st.error("⚠️ 通常出勤曜日を設定する場合は通常開始・終了時刻も入力してください。また、時刻を入力する場合は曜日も設定してください。")
                        elif edit_t_start.strip() and edit_t_end.strip() and edit_t_start.strip() >= edit_t_end.strip():
                            st.error("⚠️ 通常開始時刻は通常終了時刻より前の時間を指定してください。")
                        elif (e_list_e and (not edit_e_start.strip() or not edit_e_end.strip())) or ((edit_e_start.strip() or edit_e_end.strip()) and not e_list_e):
                            st.error("⚠️ 追加可能曜日を設定する場合は追加可能開始・終了時刻も入力してください。また、時刻を入力する場合は曜日も設定してください。")
                        elif edit_e_start.strip() and edit_e_end.strip() and edit_e_start.strip() >= edit_e_end.strip():
                            st.error("⚠️ 追加可能開始時刻は追加可能終了時刻より前の時間を指定してください。")
                        elif n_set_e & e_set_e:
                            st.error("⚠️ 通常出勤曜日と追加可能曜日に同じ曜日が設定されています。")
                        elif n_set_e & ng_set_e:
                            st.error("⚠️ 通常出勤曜日と絶対NG曜日に同じ曜日が設定されています。")
                        elif e_set_e & ng_set_e:
                            st.error("⚠️ 追加可能曜日と絶対NG曜日に同じ曜日が設定されています。")
                        elif str(edit_max_d).isdigit() and len(n_set_e) > int(edit_max_d):
                            st.error("⚠️ 通常出勤曜日の日数が、週最大出勤日数を超えています。")
                        else:
                            if current_role == "admin" and edit_role == "staff":
                                admins = df_emp[df_emp["役割"] == "admin"]
                                if len(admins) <= 1:
                                    st.error("⚠️ 管理者がいなくなるため、この管理者の役割をstaffに変更できません。")
                                    st.stop()
                                    
                            idx = df_emp.index[df_emp["従業員ID"] == edit_id][0]
                            df_emp.at[idx, "パスワード"] = edit_pass.strip()
                            df_emp.at[idx, "氏名"] = edit_name.strip()
                            df_emp.at[idx, "役割"] = edit_role
                            df_emp.at[idx, "通常出勤曜日"] = normal_days_e
                            df_emp.at[idx, "通常開始時刻"] = edit_t_start.strip()
                            df_emp.at[idx, "通常終了時刻"] = edit_t_end.strip()
                            df_emp.at[idx, "追加可能曜日"] = extra_days_e
                            df_emp.at[idx, "追加可能開始時刻"] = edit_e_start.strip()
                            df_emp.at[idx, "追加可能終了時刻"] = edit_e_end.strip()
                            df_emp.at[idx, "絶対NG曜日"] = ng_days_e
                            df_emp.at[idx, "週最大出勤日数"] = edit_max_d
                            df_emp.at[idx, "週制限超過許可"] = edit_allow_ov
                            df_emp.at[idx, "経験者フラグ"] = edit_exp_flg
                            df_emp.at[idx, "未成年フラグ"] = edit_min_flg
                            
                            csv_manager.save_employees_directly(base_dir, shop_code, df_emp)
                            st.success("従業員情報を更新しました。")
                            time.sleep(0.5)
                            st.rerun()

        with st.expander("❌ 従業員の契約解除(削除)"):
            if df_emp is not None and not df_emp.empty:
                del_id = st.selectbox("削除する従業員を選択", options=df_emp["従業員ID"].values)
                if st.button("契約を解除する"):
                    if del_id == st.session_state['emp_id']:
                        st.error("⚠️ 自分自身を削除することはできません。")
                    else:
                        admins = df_emp[df_emp["役割"] == "admin"]
                        if del_id in admins["従業員ID"].values and len(admins) <= 1:
                            st.error("⚠️ 管理者がいなくなるため、この管理者を削除できません。")
                        else:
                            df_emp = df_emp[df_emp["従業員ID"] != del_id]
                            csv_manager.save_employees_directly(base_dir, shop_code, df_emp)
                            st.success("契約を解除しました。")
                            time.sleep(0.5)
                            st.rerun()

    with tab_roster:
        st.subheader(f"✨ {target_month} のシフト管理")
        
        with st.expander("📝 従業員の希望休提出状況を確認する", expanded=False):
            try:
                # ▼ 修正ポイント: ファイルパスを店舗フォルダ直下の holiday_requests.csv に変更
                req_file = os.path.join(base_dir, str(shop_code).zfill(3), "holiday_requests.csv")
                
                if os.path.exists(req_file):
                    df_req = pd.read_csv(req_file, encoding="utf-8-sig")
                    # 対象月のデータ（例: "2026-07" から始まる日付）のみに絞り込む
                    df_req_target = df_req[df_req["日付"].astype(str).str.startswith(target_month)]
                    
                    if not df_req_target.empty:
                        # 日付順に並び替えて綺麗に表示
                        st.dataframe(df_req_target.sort_values("日付"), use_container_width=True, hide_index=True)
                    else:
                        st.info(f"{target_month} の希望休はまだ提出されていません。")
                else:
                    st.info("希望休データがまだありません。")
            except Exception as e:
                st.warning(f"希望休データの読み込みに失敗しました: {e}")
        
        if st.button("🔄 シフトを自動生成する"):
            success, msg = shift_generator.generate_monthly_shift(base_dir, shop_code, target_month)
            if success: st.success(msg); time.sleep(0.5); st.rerun()
            else: st.error(msg)
            
        df_active_roster = csv_manager.load_roster(base_dir, shop_code, target_month)
        if df_active_roster is not None and not df_active_roster.empty:
            alert_days = []
            try:
                import calendar
                y, m = map(int, target_month.split("-"))
                _, total_days = calendar.monthrange(y, m)
                for d in range(1, total_days + 1):
                    d_str = f"{y}-{str(m).zfill(2)}-{str(d).zfill(2)}"
                    df_day = df_active_roster[df_active_roster["日付"] == d_str]
                    res = shift_generator.check_time_coverage(df_day, settings["開店時間"], settings["閉店時間"])
                    if "⚠️" in res:
                        alert_days.append(str(d))
            except Exception:
                pass
                
            st.markdown("### 📊 シフトマトリックス一覧")
            if alert_days:
                st.error(f"⚠️ 以下の日にちで営業時間のカバーが不足しています: {', '.join(alert_days)}日")
            try:
                all_days_list = [str(i) for i in range(1, total_days + 1)]
                matrix_df = df_active_roster.pivot(index="氏名", columns="日", values="時間枠").fillna("-")
                for day_col in all_days_list:
                    if day_col not in matrix_df.columns: matrix_df[day_col] = "-"
                def highlight_alert_days(s):
                    if s.name in alert_days: return ['background-color: #ffe6e6; color: #cc0000; font-weight: bold;'] * len(s)
                    return [''] * len(s)
                st.dataframe(matrix_df[all_days_list].style.apply(highlight_alert_days, axis=0), use_container_width=True)
            except Exception as e: st.warning(f"マトリックス再構成中: {e}")
                
            st.markdown("---")
            st.markdown("### ✍️ シフトの手動調整・直接編集")
            edited_df = st.data_editor(
                df_active_roster, num_rows="dynamic",
                column_config={"店舗コード": st.column_config.TextColumn(disabled=True)},
                use_container_width=True, key="roster_editor"
            )
            if st.button("💾 【重要】修正したシフトを最終保存する", type="primary"):
                edited_df["店舗コード"] = shop_code
                cleaned_df = edited_df.dropna(subset=["従業員ID", "氏名", "日付"])
                cleaned_df = cleaned_df[cleaned_df["従業員ID"].astype(str).str.strip() != ""]
                
                invalid_formats = cleaned_df[
                    (~cleaned_df["時間枠"].astype(str).str.contains("-", na=False)) & 
                    (cleaned_df["時間枠"].astype(str).str.strip() != "") &
                    (cleaned_df["時間枠"].astype(str).str.strip() != "-")
                ]
                
                valid_emp_ids = set(df_emp["従業員ID"].astype(str).str.strip().values) if df_emp is not None else set()
                invalid_ids = cleaned_df[~cleaned_df["従業員ID"].astype(str).str.strip().isin(valid_emp_ids)]
                
                if not invalid_formats.empty:
                    st.error("⚠️ 「時間枠」に不正な形式が含まれています。「10:00-19:00」のような形式で入力してください。")
                elif not invalid_ids.empty:
                    st.error(f"⚠️ 従業員マスタに存在しない従業員IDが含まれています: {', '.join(invalid_ids['従業員ID'].astype(str).unique())}")
                else:
                    success, msg = csv_manager.save_roster_directly(base_dir, shop_code, target_month, cleaned_df)
                    if success:
                        st.success(f"✨ {target_month} のシフトを保存しました！")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
                        
            st.markdown("---")
            st.markdown("### 📢 シフトの公開・エクスポート")
            col1, col2 = st.columns(2)
            
            pub_file = os.path.join(base_dir, str(shop_code).zfill(3), target_month, "published.txt")
            is_published = os.path.exists(pub_file)
            
            with col1:
                if is_published:
                    st.info("📢 この月のシフトは現在【公開済み】です。")
                    if st.button("🔒 シフトを非公開に戻す"):
                        try:
                            os.remove(pub_file)
                            st.success("シフトを非公開にしました。")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e: st.error(f"エラー: {e}")
                else:
                    st.warning("🔒 この月のシフトは現在【未公開（下書き）】です。")
                    if st.button("🚀 確定シフトを従業員に公開する", type="primary"):
                        try:
                            os.makedirs(os.path.dirname(pub_file), exist_ok=True)
                            with open(pub_file, "w") as f: f.write("published")
                            st.success("✨ シフトを公開しました！従業員画面から閲覧可能です。")
                            time.sleep(0.5); st.rerun()
                        except Exception as e: st.error(f"エラー: {e}")
                            
            with col2:
                st.download_button(
                    label="📥 シフト表をCSVダウンロード",
                    data=df_active_roster.to_csv(index=False, encoding="utf-8-sig"),
                    file_name=f"shift_{shop_code}_{target_month}.csv",
                    mime="text/csv"
                )
        else:
            st.info("現在この月のシフトは生成されていません。")