import streamlit as st
import os
import config
from views import auth_view, admin_view, employee_view

# ページ初期化設定
config.init_page()

def main():
    base_dir = st.sidebar.text_input("データ保存先パス", value="data")
    if not os.path.exists(base_dir): 
        os.makedirs(base_dir)

    if "logged_in" not in st.session_state: 
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        auth_view.auth_screen(base_dir)
    else:
        st.sidebar.write(f"ログイン: **{st.session_state['name']}**")
        if st.sidebar.button("ログアウト"):
            st.session_state.clear()
            st.rerun()
        
        if st.session_state["role"] == "admin":
            admin_view.admin_dashboard(base_dir)
        else:
            employee_view.employee_dashboard(base_dir)

if __name__ == "__main__": 
    main()