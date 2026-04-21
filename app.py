import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ページ設定
st.set_page_config(page_title="バンドメンバー名簿", layout="centered")

# --- パスワード認証 ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.subheader("パスワードを入力してくださいにゃん")
        password = st.text_input("パスワード", type="password")
        if st.button("ログイン"):
            if password == "202410675":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("違うがな")
        return False
    return True

if check_password():
    st.title("🎸 バンドメンバー名簿")

    # Google Sheets接続
    conn = st.connection("gsheets", type=GSheetsConnection)

    # データの読み込み
    df = conn.read(ttl=0) # ttl=0で常に最新を取得

    # --- 新規登録セクション ---
    with st.expander("➕ 新規メンバー登録"):
        with st.form("register_form", clear_on_submit=True):
            new_name = st.text_input("名前")
            new_band = st.text_input("好きなバンド")
            new_insts = st.multiselect("演奏できる楽器", ["ギター", "ベース", "ドラム", "ヴォーカル", "キーボード", "その他(サックス、同期音源等)"])
            new_announced = st.text_input("発表済みバンド")
            new_unannounced = st.text_input("未発表バンド")
            
            submit = st.form_submit_button("登録")
            
            if submit:
                if new_name and new_band and new_insts:
                    new_data = pd.DataFrame([{
                        "名前": new_name,
                        "好きなバンド": new_band,
                        "楽器": ", ".join(new_insts),
                        "発表済みバンド": new_announced,
                        "未発表バンド": new_unannounced
                    }])
                    updated_df = pd.concat([df, new_data], ignore_index=True)
                    conn.update(worksheet="meibo", data=updated_df)
                    st.success(f"{new_name}さんを登録しました！")
                    st.rerun()
                else:
                    st.error("必須項目（名前・バンド・楽器）を入力してください")

    # --- 検索・フィルター ---
    st.subheader("🔍 メンバー検索")
    col1, col2 = st.columns(2)
    with col1:
        search_name = st.text_input("名前で検索")
    with col2:
        search_inst = st.selectbox("楽器でフィルター", ["すべて"] + ["ギター", "ベース", "ドラム", "ヴォーカル", "キーボード"])

    # フィルタリング処理
    filtered_df = df.copy()
    if search_name:
        filtered_df = filtered_df[filtered_df["名前"].str.contains(search_name, na=False)]
    if search_inst != "すべて":
        filtered_df = filtered_df[filtered_df["楽器"].str.contains(search_inst, na=False)]

    # --- メンバー一覧表示 ---
    st.subheader("👥 メンバー一覧")
    for index, row in filtered_df.iterrows():
        with st.container():
            st.markdown(f"### **{row['名前']}**")
            st.write(f"🎸 **楽器:** {row['楽器']}")
            st.write(f"❤️ **好きなバンド:** {row['好きなバンド']}")
            st.write(f"📢 **発表済み:** {row['発表済みバンド'] if row['発表済みバンド'] else 'なし'}")
            st.write(f"🤫 **未発表:** {row['未発表バンド'] if row['未発表バンド'] else 'なし'}")
            
            # 削除機能（デモ用：必要に応じて追加）
            if st.button(f"🗑️ {row['名前']}を削除", key=f"del_{index}"):
                df = df.drop(index)
                conn.update(worksheet="meibo", data=df)
                st.rerun()
            st.divider()