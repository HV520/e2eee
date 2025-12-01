import streamlit as st
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path
import database as db

# ========================= CONFIG =========================
st.set_page_config(page_title="HASSAN RAJPUT E2EE BOMBER", page_icon="👑", layout="wide")

st.markdown("""
<style>
    .big-font {font-size:50px !important; font-weight:bold; text-align:center; color:#667eea;}
    .log-box {background:#000; color:#00ff00; padding:15px; border-radius:10px; font-family:'Courier New'; height:500px; overflow-y:auto;}
    .stButton>button {background:linear-gradient(135deg,#667eea,#764ba2); color:white; font-size:18px; padding:15px; border-radius:12px;}
    .stButton>button:hover {transform:scale(1.05);}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">HASSAN RAJPUT E2EE BOMBER 👑</p>', unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'username' not in st.session_state: st.session_state.username = None
if 'running' not in st.session_state: st.session_state.running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'sent' not in st.session_state: st.session_state.sent = 0

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    full = f"[{timestamp}] {msg}"
    st.session_state.logs.append(full)
    print(full)  # terminal me bhi dikhe

# ===================== BROWSER SETUP =====================
def get_driver():
    log("Browser setup kar raha hu...")
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1366,768')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        driver = webdriver.Chrome(options=options)
        log("✅ Chrome ready ho gaya!")
        return driver
    except Exception as e:
        log(f"❌ Chrome error: {e}")
        st.error("ChromeDriver nahi mila! Server pe install karo.")
        return None

# ===================== FIND MESSAGE BOX (100% WORKING 2025) =====================
def find_msg_box(driver):
    selectors = [
        'div[aria-label="Message"][contenteditable="true"]',
        'div[role="textbox"][contenteditable="true"]',
        'div[data-lexical-editor="true"]',
        'div[contenteditable="true"]'
    ]
    for sel in selectors:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, sel)
            if elem.is_displayed():
                log(f"✅ Message box mila → {sel}")
                return elem
        except: pass
    return None

# ===================== SEND MESSAGE =====================
def send_message(driver, msg_box, text):
    try:
        driver.execute_script("""
            arguments[0].innerText = arguments[1];
            arguments[0].textContent = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
        """, msg_box, text)
        time.sleep(0.8)

        # Enter press (works everywhere – E2EE, normal, group)
        driver.execute_script("""
            const el = arguments[0];
            el.focus();
            ['keydown','keypress','keyup'].forEach(type => {
                el.dispatchEvent(new KeyboardEvent(type, {key:'Enter', code:'Enter', keyCode:13, bubbles:true}));
            });
        """, msg_box)
        return True
    except:
        return False

# ===================== MAIN AUTOMATION =====================
def automation_loop(config, user_id):
    driver = get_driver()
    if not driver: return

    try:
        driver.get("https://facebook.com")
        time.sleep(5)

        # Add cookies if provided
        if config.get('cookies'):
            for cookie in config['cookies'].split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    try:
                        driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})
                    except: pass
            driver.refresh()
            time.sleep(8)

        # Open chat (works for E2EE, normal, group – any ID)
        chat_url = f"https://www.facebook.com/messages/t/{config['chat_id']}"
        log(f"Chat khol raha hu → {chat_url}")
        driver.get(chat_url)
        time.sleep(10)

        msg_box = find_msg_box(driver)
        if not msg_box:
            log("❌ Message box nahi mila! Chat ID check karo.")
            st.error("Chat open nahi hua! ID sahi daalo.")
            return

        messages = [m.strip() for m in config['messages'].split('\n') if m.strip()]
        if not messages: messages = ["Hello bro 👑"]

        delay = int(config['delay'])
        prefix = config['name_prefix'] + " " if config['name_prefix'] else ""

        log("🚀 BOMBING SHURU! Press STOP to rukna.")
        st.session_state.running = True

        while st.session_state.running:
            for msg in messages:
                if not st.session_state.running: break
                full_msg = prefix + msg
                if send_message(driver, msg_box, full_msg):
                    st.session_state.sent += 1
                    log(f"Sent → {full_msg[:40]}...")
                else:
                    log("❌ Message nahi gaya!")
                time.sleep(delay)

        log("🛑 Automation ruk gaya.")
    except Exception as e:
        log(f"❌ Error: {e}")
    finally:
        try: driver.quit()
        except: pass
        st.session_state.running = False
        db.set_automation_running(user_id, False)

# ===================== UI =====================
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "✨ Register"])
    with tab1:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            uid = db.verify_user(user, pwd)
            if uid:
                st.session_state.logged_in = True
                st.session_state.user_id = uid
                st.session_state.username = user
                st.success("Login ho gaya!")
                st.rerun()
            else:
                st.error("Galat username/password")
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            ok, msg = db.create_user(nu, np)
            st.write(msg if ok else "❌ Username already hai")

else:
    st.sidebar.success(f"👑 {st.session_state.username}")
    if st.sidebar.button("Logout"): 
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

    config = db.get_user_config(st.session_state.user_id) or {}

    with st.form("config_form"):
        st.write("### ⚙️ Settings")
        chat_id = st.text_input("Chat/Convo ID (E2EE ya normal – dono chalega)", value=config.get('chat_id',''))
        prefix = st.text_input("Haters Name (optional)", value=config.get('name_prefix',''))
        delay = st.number_input("Delay (seconds)", 1, 60, value=int(config.get('delay',5)))
        cookies = st.text_area("Cookies (optional – private rahega)", height=80, help="Sirf naye cookies daalo, purane safe hain")
        messages = st.text_area("Messages (ek line pe ek)", value=config.get('messages','Hello\nKese ho?\nHassan Rajput OP'), height=150)

        saved = st.form_submit_button("💾 Save Settings")
        if saved:
            final_cookies = cookies.strip() if cookies.strip() else config.get('cookies','')
            db.update_user_config(st.session_state.user_id, chat_id, prefix, delay, final_cookies, messages)
            st.success("Settings save ho gayi!")
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 START BOMBER", disabled=st.session_state.running, use_container_width=True):
            if not chat_id.strip():
                st.error("Chat ID daal pehle!")
            else:
                st.session_state.sent = 0
                st.session_state.logs = []
                db.set_automation_running(st.session_state.user_id, True)
                threading.Thread(target=automation_loop, args=(db.get_user_config(st.session_state.user_id), st.session_state.user_id), daemon=True).start()
                st.success("Bomber shuru ho gaya!")

    with col2:
        if st.button("🛑 STOP", disabled=not st.session_state.running, use_container_width=True):
            st.session_state.running = False
            db.set_automation_running(st.session_state.user_id, False)
            st.warning("Ruk gaya!")

    # Live Stats
    c1, c2, c3 = st.columns(3)
    c1.metric("Messages Sent", st.session_state.sent)
    c2.metric("Status", "🟢 Running" if st.session_state.running else "🔴 Stopped")
    c3.metric("Logs", len(st.session_state.logs))

    # Live Logs
    log_container = st.empty()
    if st.session_state.logs:
        log_container.markdown(f'<div class="log-box">{"<br>".join(st.session_state.logs[-100:])}</div>', unsafe_allow_html=True)
    else:
        log_container.info("Logs yaha dikhega...")

    if st.session_state.running:
        time.sleep(1)
        st.rerun()

st.markdown("<br><hr><center>Made with ❤️ by <b>HASSAN RAJPUT</b> © 2025</center>", unsafe_allow_html=True)
