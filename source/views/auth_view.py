import streamlit as st
import pandas as pd
import os
from services import csv_manager

def auth_screen(base_dir):
    st.title("簡易複数店舗対応型・高度シフト管理システム")
    tab_login, tab_setup = st.tabs(["🔑 ログイン", "🏪 新規店舗・部門の設立"])
    
    with tab_login:
        st.subheader("ログイン")
        with st.form("login_form"):
            shop_code = st.text_input("店舗コード (001等)", value="001", key="login_shop_code")
            emp_id = st.text_input("従業員ID", placeholder="例: admin01", key="login_emp_id")
            password = st.text_input("パスワード", type="password", placeholder="例: pass123", key="login_password")
            
            if st.form_submit_button("ログイン"):
                # 【改善】未入力チェックによる安全性向上
                if not str(shop_code).strip() or not str(emp_id).strip() or not str(password).strip():
                    st.warning("⚠️ 店舗コード、従業員ID、パスワードをすべて入力してください。")
                else:
                    padded_code = str(shop_code).zfill(3)
                    df_emp = csv_manager.load_employees(base_dir, padded_code)
                    
                    if df_emp is not None:
                        user = df_emp[(df_emp["店舗コード"] == padded_code) & 
                                      (df_emp["従業員ID"] == str(emp_id).strip()) & 
                                      (df_emp["パスワード"] == str(password).strip())]
                        
                        if not user.empty:
                            user_role = user.iloc[0]["役割"] if "役割" in user.columns else "employee"
                            st.session_state.update({
                                "logged_in": True, 
                                "role": user_role, 
                                "name": user.iloc[0]["氏名"], 
                                "emp_id": str(emp_id).strip(), 
                                "shop_code": padded_code
                            })
                            st.rerun()
                        else: 
                            st.error("店舗コード、ID、またはパスワードが間違っています。")
                    else: 
                        st.error("店舗データが見つかりません。右側の『新規店舗・部門の設立』タブから初期設定を行ってください。")

    with tab_setup:
        st.subheader("🏪 新しい店舗・部門を立ち上げる")
        st.info("💡 新しい店舗コードを決定し、その部門を統括する「初期管理者」のアカウントをその場で同時に作成します。")
        
        with st.form("setup_form"):
            new_shop_code = st.text_input("1. 新設する店舗コード (数字3桁推奨)", placeholder="例: 002", key="setup_shop_code")
            st.markdown("---")
            st.markdown("**👤 2. 初期管理者（店長・責任者）のアカウント設定**")
            admin_id = st.text_input("管理者ログインID", value="admin02", key="setup_emp_id")
            admin_password = st.text_input("管理者ログインパスワード", type="password", placeholder="パスワードを設定してください", key="setup_password")
            admin_name = st.text_input("管理者氏名", placeholder="例: 山田店長", key="setup_name")
        
            if st.form_submit_button("🚀 新規店舗・部門を設立する"):
                # 【改善】未入力チェックと店舗コードの数字指定による安全性向上
                if not new_shop_code.strip() or not admin_id.strip() or not admin_password.strip() or not admin_name.strip():
                    st.error("⚠️ すべての項目を正しく入力してください。")
                elif not str(new_shop_code).strip().isdigit():
                    st.error("⚠️ 店舗コードは半角数字で入力してください。")
                else:
                    padded_new_code = str(new_shop_code).strip().zfill(3)
                    shop_dir = os.path.join(base_dir, padded_new_code)
                    emp_file = os.path.join(shop_dir, "employees.csv")
                    
                    if os.path.exists(emp_file):
                        st.error(f"⚠️ 店舗コード「{padded_new_code}」は既に存在しています。別のコードを指定してください。")
                    else:
                        os.makedirs(shop_dir, exist_ok=True)
                        csv_manager.save_shop_settings(base_dir, padded_new_code, "09:00", "21:00")
                
                        new_admin_records = {
                            "店舗コード": [padded_new_code], "従業員ID": [str(admin_id).strip()], "パスワード": [str(admin_password).strip()],
                            "氏名": [str(admin_name).strip()], "役割": ["admin"], "通常出勤曜日": ["月,火,水,木,金"],
                            "通常開始時刻": ["09:00"], "通常終了時刻": ["18:00"], "追加可能曜日": [""], "追加可能開始時刻": [""],
                            "追加可能終了時刻": [""], "絶対NG曜日": ["土,日"], "経験者フラグ": ["1"], "未成年フラグ": ["0"]
                        }
                        df_new_emp = pd.DataFrame(new_admin_records)
                        df_new_emp.to_csv(emp_file, index=False, encoding="utf-8-sig")
                        st.success(f"🎉 店舗「{padded_new_code}」の設立が完了しました！")