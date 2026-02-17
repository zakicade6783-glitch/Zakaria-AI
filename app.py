import streamlit as st
from PyPDF2 import PdfReader
import json
import os

# 1. SETTINGS & MODERN THEME
st.set_page_config(page_title="Zakaria AI - Executive", page_icon="🧠", layout="wide")

# CSS Professional ah
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }

    /* Sidebar ChatGPT-style */
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #1e293b; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Qurxinta Profile-ka dhinac */
    .profile-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .profile-img {
        width: 60px; height: 60px; border-radius: 50%; 
        border: 2px solid #3b82f6; margin-bottom: 10px;
    }

    /* Chat Bubbles */
    .stChatMessage { border-radius: 15px !important; margin-bottom: 10px !important; }
</style>
""", unsafe_allow_html=True)

# 2. DATABASE MANAGEMENT
DB_FILE = "zakaria_database.json"

def load_all_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"qa_data": {}, "pdf_text": "", "registered_emails": [], "chat_history": []}

def save_all_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_all_data()

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- LOGIN SECTION ---
if not st.session_state.user_email:
    st.markdown("<h1 style='text-align: center;'>🌐 Zakaria AI Portal</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        email_input = st.text_input("Geli Email-kaaga")
        if st.button("Access Portal", use_container_width=True):
            if "@" in email_input:
                st.session_state.user_email = email_input
                if email_input not in st.session_state.db["registered_emails"]:
                    st.session_state.db["registered_emails"].append(email_input)
                    save_all_data(st.session_state.db)
                st.rerun()
    st.stop()

# --- SIDEBAR (HISTROY & PROFILE) ---
with st.sidebar:
    # Sawirka Profile-ka iyo Email-ka
    st.markdown(f"""
        <div class="profile-card">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="profile-img">
            <div style="font-weight: 600; font-size: 14px;">{st.session_state.user_email}</div>
            <div style="color: #10b981; font-size: 12px;">● Online</div>
        </div>
    """, unsafe_allow_html=True)
    
    # KALIYA TAARIIKHDA (Sidebar-ka ayay ku jiraysaa)
    st.subheader("📜 Chat History")
    history = [m for m in st.session_state.db["chat_history"] if m["role"] == "user"]
    if history:
        for m in reversed(history[-10:]): # 10-ka u dambeeya
            st.caption(f"💬 {m['content'][:35]}...")
    else:
        st.write("Wali wax ma weydiin AI-ga.")

    st.write("---")
    with st.expander("🛠 Admin Control"):
        admin_pass = st.text_input("Password", type="password")
        if admin_pass == "zakaria2026":
            up_file = st.file_uploader("Upload PDF", type="pdf")
            if up_file:
                reader = PdfReader(up_file)
                text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
                st.session_state.db["pdf_text"] = " ".join(text.split()).lower()
                save_all_data(st.session_state.db)
                st.toast("Brain Updated! 🧠")

    if st.button("Log Out", use_container_width=True):
        st.session_state.user_email = ""
        st.rerun()

# --- MAIN CHAT SCREEN (Halkan waa nadiif) ---
st.title("🤖 Zakaria Intelligence")

# 1. Muuji fariimaha hadda socda (Current Session kaliya hadaad rabto)
# Laakiin hadaad rabto history-ga oo dhan inuu halkan joogo, koodhkan ha beddelin:
for m in st.session_state.db.get("chat_history", []):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 2. Input-ka
if prompt := st.chat_input("I weydii wax kasta..."):
    st.session_state.db["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        q_low = prompt.lower().strip()
        ans = ""
        db = st.session_state.db

        # Search Logic
        if q_low in db["qa_data"]:
            ans = db["qa_data"][q_low]
        elif db["pdf_text"] and q_low in db["pdf_text"]:
            idx = db["pdf_text"].find(q_low)
            context = db["pdf_text"][idx:idx+600]
            ans = context.split("jawaab:")[1].split("su'aal:")[0].strip().capitalize() if "jawaab:" in context else context[:400]
        
        if not ans:
            ans = "Raalli ahow, xogtaas wali kuma jiro nidaamkayga."

        st.markdown(ans)
        st.session_state.db["chat_history"].append({"role": "assistant", "content": ans})
        save_all_data(st.session_state.db)