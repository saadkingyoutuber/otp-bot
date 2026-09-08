import requests
import time
import json
import os
import uuid
import threading
import random
import re
import html
import pyotp
from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime 
from urllib.parse import urljoin, urlparse, parse_qs

# ==========================================
# Configuration (Environment Variables)
# ==========================================
TOKEN = os.environ.get("TOKEN", "8609598903:AAFOq3hsqVUARY1JQ0rsawbwxnDbSwyO5q8")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = int(os.environ.get("OWNER_ID", 7904042614))
BOT_USERNAME = ""
DB_FILE = os.environ.get("DB_FILE", "data/bot_data.json")
# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="6267000941547885720">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5353032893096567467">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="4969841369850840381">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5352862640592949843">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "4958503072801228000", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": f"{PEM['hi']} Welcome! Please choose an option from the menu below:", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 
    "search_number": {"text": f"{PEM['num']} <b>Search Number</b>\n\nEnter 3 to 9 digits to search for a number (e.g., 880, 9227373):", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>{{ref_reward}} $</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖\n《 💰 WITHDRAWAL 》\n➖➖➖➖➖➖➖\n📱 Total OTP: {total_otp}\n➖➖➖➖➖➖➖\n👥 Total Refer: {total_ref}\n➖➖➖➖➖➖➖\n💰 BALANCE: {bal} $\n➖➖➖➖➖➖➖\n🔐 MINIMUM: {min_w} $\n➖➖➖➖➖➖➖\n💳 SELECT WALLET:", "buttons": []},
    "support": {"text": f"📢 <b>Join Our Channel:</b>\n<a href=\"https://t.me/skcybersecuritytricks\">SAAD KING TRICKS</a>\n\nFor any help, contact our support team.", "buttons": []}
}

# ==========================================
# Database Mode (Local JSON Only)
# ==========================================
print("✅ Running in Local Mode")

bot_settings = {
    "admins": [OWNER_ID],
    "panels": [], 
    "fw_groups": [], 
    "otp_link": "https://t.me/DireOTPGroup",
    "withdraw_on": True,
    "min_withdraw": 10.0,
    "otp_reward": 0.001,
    "refer_reward": 0.001,
    "cooldown": 10,
    "num_req": 3,
    "num_share": 1, 
    "support_link": "https://t.me/skcybersecuritytricks",
    "w_methods": ["TRC20 (Tron)", "BEP20 (BSC)"],
    "w_group": "", 
    
    "fj_on": False,
    "fj_channels": [], 
    "nexa_keys": [], 
    "search_countries": [],
    "nexa_services": {},
    "voltx_services": {},
    "premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5913463998522592692"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"}
    },
    "premium_apps": {
        "FACEBOOK": {"char": "🚫", "id": "5334807341109908955", "name": "Facebook"},
        "WHATSAPP": {"char": "🚫", "id": "5334759662677957452", "name": "WhatsApp"}
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
}


number_batches = {}
used_numbers_list = []
nexa_assigned_numbers = {} 
voltx_assigned_numbers = {}
NEXA_BASE_URL = "http://63.141.255.227"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set()
processed_otps_order = deque()
recent_traffic = []
user_banned_cache = {}
otp_received_numbers = set()
OTP_RECEIVED_CAP = 5000
otp_received_order = deque()

def _track_processed_otp(uid):
    global processed_otps, processed_otps_order
    processed_otps.add(uid)
    processed_otps_order.append(uid)
    while len(processed_otps_order) > 5000:
        oldest = processed_otps_order.popleft()
        processed_otps.discard(oldest)

def _track_otp_received(num):
    global otp_received_numbers, otp_received_order
    if not num or num in otp_received_numbers:
        return
    otp_received_numbers.add(num)
    otp_received_order.append(num)
    while len(otp_received_order) > OTP_RECEIVED_CAP:
        oldest = otp_received_order.popleft()
        otp_received_numbers.discard(oldest)

panel_warmup_done = False
nexa_warmup_done = False
panel_sessions = {}

def fetch_cpt_panel_cdrs(p, session, check_url):
    try:
        res = session.get(check_url, timeout=15)
        html_text = res.text
        
        if "login" in html_text.lower() or "signin" in html_text.lower() or any(x in html_text for x in ["Sign in to your account", "Please sign in", "Welcome back!"]):
            raise Exception("Session expired")
            
        soup = BeautifulSoup(html_text, 'html.parser')
        detected_col_count = 7
        for table in soup.find_all('table'):
            header_rows = table.find_all('tr')
            if header_rows:
                first_row_cols = header_rows[0].find_all(['th', 'td'])
                if len(first_row_cols) > detected_col_count:
                    detected_col_count = len(first_row_cols)
                    break

        s_ajax_source = ""
        for script in soup.find_all("script"):
            script_text = script.string or ""
            match = re.search(r'sAjaxSource"?\s*:\s*"([^"]+)"', script_text)
            if match:
                s_ajax_source = match.group(1)
                break
            match = re.search(r'["\']ajax["\']\s*:\s*["\']([^"\']+)["\']', script_text)
            if match:
                s_ajax_source = match.group(1)
                break
            match = re.search(r'["\']?ajax["\']?\s*:\s*\{[^}]*["\']?url["\']?\s*:\s*["\']([^"\']+)["\']', script_text)
            if match:
                s_ajax_source = match.group(1)
                break
            if 'DataTable' in script_text or 'dataTable' in script_text:
                match = re.search(r'"url"\s*:\s*"([^"]+)"', script_text)
                if match:
                    s_ajax_source = match.group(1)
                    break
                
        results = []
        
        n_col_name = p.get("num_col_name", "number").lower()
        m_col_name = p.get("msg_col_name", "message").lower()
        n_idx = int(p.get("num_col_idx", 1)) - 1 if p.get("num_col_idx") else 1
        m_idx = int(p.get("msg_col_idx", 2)) - 1 if p.get("msg_col_idx") else 2

        if s_ajax_source:
            baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
            if not baseUrl.startswith("http"):
                baseUrl = "http://" + baseUrl
                
            full_ajax_url = ""
            if s_ajax_source.startswith("http"):
                full_ajax_url = s_ajax_source
            elif s_ajax_source.startswith("/"):
                full_ajax_url = f"{baseUrl}{s_ajax_source}"
            else:
                last_slash_idx = check_url.rfind("/")
                if last_slash_idx > 0:
                    current_dir = check_url[:last_slash_idx]
                else:
                    current_dir = check_url.rstrip("/")
                full_ajax_url = f"{current_dir}/{s_ajax_source}"

            if "iDisplayLength" not in full_ajax_url:
                col_search = "&".join([f"sSearch_{i}=&bRegex_{i}=false&bSearchable_{i}=true&bSortable_{i}=true" for i in range(detected_col_count)])
                query_params = f"sEcho=1&iColumns={detected_col_count}&iDisplayStart=0&iDisplayLength=9999&sSearch=&bRegex=false&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc&{col_search}"
                divider = "&" if "?" in full_ajax_url else "?"
                full_ajax_url += f"{divider}{query_params}"

            ajax_headers = {
                "Referer": check_url,
                "X-Requested-With": "XMLHttpRequest"
            }
            
            ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
            rate_limit_phrases = ["too many times", "try again", "rate limit", "slow down", "429", "blocked"]
            if not ajax_res.text.strip():
                raise Exception("AJAX URL returned empty response. Check your Msg Link / check_url setting.")
            if any(ph in ajax_res.text.lower() for ph in rate_limit_phrases) and ajax_res.text.strip()[0] != '{':
                time.sleep(6)
                ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
            try:
                data_dict = ajax_res.json()
            except Exception:
                raise Exception(f"AJAX response is not valid JSON. Got: {ajax_res.text[:120]!r}")
            rows = data_dict.get("aaData", [])
            for row_val in rows:
                if not isinstance(row_val, list):
                    continue
                    
                if len(row_val) < max(n_idx, m_idx) + 1:
                    continue
                    
                num_val = row_val[n_idx] if (0 <= n_idx < len(row_val)) else row_val[2]
                msg_val = row_val[m_idx] if (0 <= m_idx < len(row_val)) else row_val[4]
                
                clean_num = re.sub(r'\D', '', str(num_val))
                if clean_num and 5 <= len(clean_num) <= 18:
                    otp = extract_otp_code(msg_val)
                    if otp and len(msg_val) > 4:
                        results.append({"number": clean_num, "message": msg_val, "otp": otp})
                        
        else:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                if not rows: continue
                
                final_n_idx = n_idx
                final_m_idx = m_idx
                
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(strip=True).lower()
                    if n_col_name in c_text: final_n_idx = i
                    if m_col_name in c_text: final_m_idx = i

                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if all(c.name == 'th' for c in cols): continue
                    
                    if len(cols) > max(final_n_idx, final_m_idx):
                        num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                        msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                        
                        clean_num = re.sub(r'\D', '', num_text)
                        if clean_num and 5 <= len(clean_num) <= 18:
                            otp = extract_otp_code(msg_text)
                            if otp and len(msg_text) > 4:
                                results.append({"number": clean_num, "message": msg_text, "otp": otp})
                                
        return results, html_text
    except Exception as e:
        raise e

user_active_sessions = {}

# Ensure data directory exists
if not os.path.exists("data"):
    os.makedirs("data")
    
def load_db():
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic, otp_received_numbers, otp_received_order
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                saved_settings = data.get("bot_settings", {})
                for key, val in saved_settings.items():
                    if key == "custom_messages":
                        for m_key, m_val in val.items():
                            bot_settings["custom_messages"][m_key] = m_val
                    else:
                        bot_settings[key] = val
                        
                for m_key, m_val in DEFAULT_CUSTOM_MESSAGES.items():
                    if m_key not in bot_settings["custom_messages"]:
                        bot_settings["custom_messages"][m_key] = m_val
                        
                number_batches = data.get("number_batches", {})
                used_numbers_list = data.get("used_numbers_list", [])
                total_uploaded_stats = data.get("total_uploaded_stats", 0)
                total_assigned_stats = data.get("total_assigned_stats", 0)
                recent_traffic = data.get("recent_traffic", [])
                nexa_assigned_numbers = data.get("nexa_assigned_numbers", {})
                loaded_otp_nums = data.get("otp_received_numbers", [])
                if len(loaded_otp_nums) > OTP_RECEIVED_CAP:
                    loaded_otp_nums = loaded_otp_nums[-OTP_RECEIVED_CAP:]
                otp_received_numbers = set(loaded_otp_nums)
                otp_received_order = deque(loaded_otp_nums)
            
            migrated = False
            new_fj = []
            for entry in bot_settings.get("fj_channels", []):
                if isinstance(entry, str):
                    new_fj.append({"chat_id": entry, "type": "channel", "title": entry, "invite_link": "", "is_private": False})
                    migrated = True
                else:
                    new_fj.append(entry)
            if migrated:
                bot_settings["fj_channels"] = new_fj

            inr_migrated = False
            old_methods = bot_settings.get("w_methods", [])
            if any(m.lower() in ["bkash", "nagad"] for m in old_methods):
                bot_settings["w_methods"] = ["UPI", "Paytm"]
                inr_migrated = True
            cm = bot_settings.get("custom_messages", {})
            for m_key in cm:
                if isinstance(cm[m_key], dict) and "text" in cm[m_key]:
                    txt = cm[m_key]["text"]
                    if "৳" in txt or "TK" in txt or "tk" in txt or any(ord(c) >= 0x0980 and ord(c) <= 0x09FF for c in txt):
                        if m_key in DEFAULT_CUSTOM_MESSAGES:
                            cm[m_key]["text"] = DEFAULT_CUSTOM_MESSAGES[m_key]["text"]
                            inr_migrated = True
            if inr_migrated:
                bot_settings["custom_messages"] = cm
                save_local_db()
                print("🔄 Migrated old BDT/Bengali settings to INR/English!")

            print("✅ Local Stock/UI DB Loaded Successfully!")
    except Exception as e:
        print(f"❌ Error loading local DB: {e}")

def save_local_db():
    settings_to_save = dict(bot_settings)
    local_data = {
        "bot_settings": settings_to_save,
        "number_batches": number_batches,
        "used_numbers_list": used_numbers_list,
        "total_uploaded_stats": total_uploaded_stats,
        "total_assigned_stats": total_assigned_stats,
        "recent_traffic": recent_traffic,
        "nexa_assigned_numbers": nexa_assigned_numbers,
        "otp_received_numbers": list(otp_received_numbers) if otp_received_numbers else []
    }
    try:
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump(local_data, f, indent=4)
    except Exception as e:
        print(f"⚠️ DB save failed: {e}")

def save_db():
    save_local_db()
    
# Ensure data directory exists
if not os.path.exists("data"):
    os.makedirs("data")
    
load_db()

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}

tg_session = requests.Session()

def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    try:
        res = tg_session.post(url, json=payload, timeout=15)
        return res.json()
    except Exception as e:
        return {}

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "photo": photo_url_or_file_id, "caption": caption, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendPhoto", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("editMessageText", payload)

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})

def send_document(chat_id, filename, text_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, text_content)}
    data = {'chat_id': chat_id}
    try: requests.post(url, data=data, files=files, timeout=20)
    except Exception as e:
        print(f"⚠️ send_document failed: {e}")

all_known_users = set()

def sync_users_list():
    global all_known_users
    try:
        if os.path.exists("users_list.json"):
            with open("users_list.json", "r") as f:
                all_known_users = set(json.load(f))
        if not all_known_users and local_users_db:
            all_known_users = set(local_users_db.keys())
            with open("users_list.json", "w") as f:
                json.dump(list(all_known_users), f)
    except: pass

threading.Thread(target=sync_users_list, daemon=True).start()

def _save_users_list():
    try:
        with open("users_list.json", "w") as f:
            json.dump(list(all_known_users), f)
    except: pass

def register_user_local(uid):
    uid_str = str(uid)
    if uid_str not in all_known_users:
        all_known_users.add(uid_str)
        threading.Thread(target=_save_users_list, daemon=True).start()

USERS_DB_FILE = "data/users_db.json"
WITHDRAWALS_DB_FILE = "data/withdrawals_db.json"
local_users_db = {}
local_withdrawals_db = {}

def _load_local_users_db():
    global local_users_db, local_withdrawals_db
    try:
        if os.path.exists(USERS_DB_FILE):
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                local_users_db = json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load users DB: {e}")
    try:
        if os.path.exists(WITHDRAWALS_DB_FILE):
            with open(WITHDRAWALS_DB_FILE, "r", encoding="utf-8") as f:
                local_withdrawals_db = json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load withdrawals DB: {e}")

def _save_local_users_db():
    try:
        with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(local_users_db, f, indent=2)
    except: pass

def _save_local_withdrawals_db():
    try:
        with open(WITHDRAWALS_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(local_withdrawals_db, f, indent=2)
    except: pass

_load_local_users_db()

def _get_local_user(user_id):
    uid = str(user_id)
    if uid not in local_users_db:
        local_users_db[uid] = {"user_id": int(user_id), "balance": 0.0, "total_refers": 0, "total_otps": 0, "banned": False, "verified": False}
        threading.Thread(target=_save_local_users_db, daemon=True).start()
    return local_users_db[uid]

def _update_local_user(user_id, updates):
    uid = str(user_id)
    if uid not in local_users_db:
        _get_local_user(user_id)
    local_users_db[uid].update(updates)
    threading.Thread(target=_save_local_users_db, daemon=True).start()

def _increment_local_user(user_id, field, amount):
    uid = str(user_id)
    if uid not in local_users_db:
        _get_local_user(user_id)
    local_users_db[uid][field] = local_users_db[uid].get(field, 0) + amount
    threading.Thread(target=_save_local_users_db, daemon=True).start()

def _local_user_exists(user_id):
    return str(user_id) in local_users_db

def _save_local_withdrawal(req_id, data):
    local_withdrawals_db[req_id] = data
    local_withdrawals_db[req_id]["timestamp"] = time.time()
    threading.Thread(target=_save_local_withdrawals_db, daemon=True).start()

def _update_local_withdrawal(req_id, updates):
    if req_id in local_withdrawals_db:
        local_withdrawals_db[req_id].update(updates)
        threading.Thread(target=_save_local_withdrawals_db, daemon=True).start()

def broadcast_copymessage(from_chat_id, msg_id):
    success = 0
    failed = 0
    users = list(all_known_users)
    
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): success += 1
            else: failed += 1
        except:
            failed += 1
        time.sleep(0.035)
        
    send_message(from_chat_id, render_body_text(f"📢 <b>Broadcast Completed!</b>\n✅ Success: {success}\n❌ Failed: {failed}\n👥 Total Sent: {len(users)}"))

def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)

def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities: return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception as e:
        return text 

def get_flag_info_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data["char"], data.get("iso", "XX"), data.get("id")
    return "🌍", "XX", None

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso

def get_flag_info_html(num_or_iso):
    if len(num_or_iso) == 2:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso") == num_or_iso:
                eid = data.get("id")
                char = data.get("char")
                if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        return "🌍"
        
    char, _, eid = get_flag_info_from_num(num_or_iso)
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char

def mask_number(num, user_id=None):
    clean = num.replace("+", "").replace(" ", "")
    tag = "MSI"
    if len(clean) > 6: return f"{clean[:3]}✦{tag}✦{clean[-3:]}"
    elif len(clean) > 2: return f"{clean[:1]}✦{tag}✦{clean[-1:]}"
    return clean

SERVICE_SMS_KEYWORDS = {
    "whatsapp": ["whatsapp", "wa", "wap", "w/a", "whatsapp business", "wa.me", "wa code", "wh", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "वाट्सएप", "वॉट्सऐप", "व्हाट्सप्प", "হোয়াটসঅ্যাপ", "হোটসঅ্যাপ", "ватсап", "уотсап", "вотсап", "ватс апп", "వాట్సాప్", "വാട്‌സ്ആപ്പ്", "வாட்ஸ்அப்", "ವಾಟ್ಸಾಪ್", "વોટ્સએપ", "ਵਟਸਐਪ", "ହ୍ଵାଟସ୍ ଆପ୍", "වට්ස්ඇප්", "วอตส์แอปป์", "วอทส์แอพ", "ဝက်စ်အက်ပ်", "វ៉តសាប់", "ວອດແອັບ", "ワッツアップ", "왓츠앱", "whatsapp的", "whatsapp验证码", "וואטסאפ", "γουάτσαπ", "ዋትስአፕ", "ვოთსაფი", "վոթսափ"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code", "فيسبوك", "فيس بوك"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code", "انستغرام", "انستقرام"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code", "تيك توك"],
    "snapchat": ["snapchat", "snap", "snap code", "سناب شات"],
    "twitter": ["twitter", "x.com", "x code", "twitter code", "تويتر"],
    "discord": ["discord", "discord code", "ديسكورد"],
    "viber": ["viber", "viber code", "فايبر"],
    "line": ["line", "line code", "line verification", "لاين"],
    "wechat": ["wechat", "we chat", "wechat code", "وي تشات"],
    "signal": ["signal", "signal code", "سيجنال"],
    "linkedin": ["linkedin", "linked in", "لينكد إن"],
    "imo": ["imo", "imo code", "imo verification", "ايمو"],
    "kakaotalk": ["kakao", "kakaotalk", "كاكاو"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],
    "google": ["google", "gmail", "youtube", "g-", "google voice", "جوجل", "غوغل"],
    "microsoft": ["microsoft", "ms", "outlook", "live.com", "hotmail"],
    "apple": ["apple", "icloud", "itunes", "apple id"],
    "yahoo": ["yahoo", "yahoo code", "ymail"],
    "protonmail": ["proton", "protonmail"],
    "binance": ["binance", "bnb", "binances"],
    "coinbase": ["coinbase"],
    "okx": ["okx", "okex"],
    "kucoin": ["kucoin"],
    "bybit": ["bybit"],
    "huobi": ["huobi", "htx"],
    "mexc": ["mexc"],
    "trustwallet": ["trust wallet", "trustwallet"],
    "paytm": ["paytm", "paytm code", "paytm otp"],
    "phonepe": ["phonepe", "phone pe", "phonepe code"],
    "gpay": ["gpay", "google pay", "googlepay"],
    "upi": ["upi", "upi code", "upi otp"],
    "paypal": ["paypal", "pay pal"],
    "cashapp": ["cash app", "cashapp"],
    "wise": ["wise", "transferwise"],
    "amazon": ["amazon", "amzn", "amazon code"],
    "ebay": ["ebay"],
    "aliexpress": ["aliexpress", "ali express"],
    "alibaba": ["alibaba"],
    "daraz": ["daraz", "daraz code"],
    "foodpanda": ["foodpanda", "food panda"],
    "uber": ["uber", "uber code", "uber verification", "uber eats"],
    "pathao": ["pathao", "pathao ride"],
    "netflix": ["netflix", "netflix code"],
    "spotify": ["spotify", "spotify code"],
    "steam": ["steam", "steam guard"],
    "epicgames": ["epic games", "epicgames"],
    "roblox": ["roblox", "roblox code"],
    "riotgames": ["riot", "riot games", "valorant", "league of legends"],
    "garena": ["garena", "free fire", "freefire"],
    "playstation": ["playstation", "psn"],
    "1xbet": ["1xbet", "1x bet"],
    "melbet": ["melbet", "melbet code"],
    "linebet": ["linebet"],
    "bet365": ["bet365"],
    "megapari": ["megapari"],
    "tinder": ["tinder", "tinder code"],
    "bumble": ["bumble"],
    "badoo": ["badoo"]
}

def detect_service(text):
    text_lower = str(text).lower()
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return service_key.upper()
    return None

def get_service_info_html(service_text, msg_text=""):
    s = str(service_text).upper().strip()
    m = str(msg_text).lower().strip()
    apps = bot_settings.get("premium_apps", {})
    
    detected_service = s
    if m:
        for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
            for kw in keywords:
                if kw in m:
                    detected_service = service_key.upper()
                    break
            if detected_service != s: break

    clean_s = re.sub(r'[^\w\s]', '', detected_service).strip()
    
    for app_name, data in apps.items():
        if app_name == detected_service or app_name == clean_s or app_name in detected_service or detected_service in app_name:
            full_name = data.get("name", app_name.title())
            char = data.get("char", "📱")
            eid = data.get("id")
            if eid: return full_name, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            return full_name, char
            
    if len(detected_service) > 20:
        return "Message", "💬"
        
    return detected_service.title(), "📱"

def detect_language(text):
    if not text: return "#EN"
    text_str = str(text)

    if any('\u0600' <= c <= '\u06ff' for c in text_str): return "#AR"
    if any('\u0980' <= c <= '\u09ff' for c in text_str): return "#BN"
    if any('\u0900' <= c <= '\u097f' for c in text_str): return "#HI"
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str): return "#PA"
    if any('\u0a80' <= c <= '\u0aff' for c in text_str): return "#GU"
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str): return "#OR"
    if any('\u0b80' <= c <= '\u0bff' for c in text_str): return "#TA"
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str): return "#TE"
    if any('\u0c80' <= c <= '\u0cff' for c in text_str): return "#KN"
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str): return "#ML"
    if any('\u0d80' <= c <= '\u0dff' for c in text_str): return "#SI"
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str): return "#TH"
    if any('\u0e80' <= c <= '\u0eff' for c in text_str): return "#LO"
    if any('\u0f00' <= c <= '\u0fff' for c in text_str): return "#BO"
    if any('\u1000' <= c <= '\u109f' for c in text_str): return "#MY"
    if any('\u1200' <= c <= '\u137f' for c in text_str): return "#AM"
    if any('\u1780' <= c <= '\u17ff' for c in text_str): return "#KM"
    if any('\u10a0' <= c <= '\u10ff' for c in text_str): return "#KA"
    if any('\u0530' <= c <= '\u058f' for c in text_str): return "#HY"
    if any('\u0590' <= c <= '\u05ff' for c in text_str): return "#HE"
    if any('\u0370' <= c <= '\u03ff' for c in text_str): return "#EL"
    if any('\u0400' <= c <= '\u04ff' for c in text_str): return "#RU"
    if any('\u4e00' <= c <= '\u9fff' for c in text_str): return "#ZH"
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str): return "#JA"
    if any('\uac00' <= c <= '\ud7af' for c in text_str): return "#KO"

    text_lower = text_str.lower()
    
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]): return "#ID"
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]): return "#MS"
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]): return "#VN"
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]): return "#TL"
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]): return "#ES"
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]): return "#PT"
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR"
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE"
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]): return "#IT"
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]): return "#PL"
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]): return "#TR"
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]): return "#NL"
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]): return "#SV"
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]): return "#DA"
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]): return "#NO"
    if any(w in text_lower for w in ["vahvistuskoodi", "älä jaa"]): return "#FI"
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]): return "#CS"
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]): return "#SK"
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]): return "#HU"
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]): return "#RO"
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]): return "#HR"
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]): return "#BG"
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]): return "#UK"
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]): return "#SW"
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]): return "#AF"
    
    return "#EN"

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

def _get_fj_chat_id(entry):
    if isinstance(entry, dict):
        return entry.get("chat_id", "")
    return entry

def _get_fj_info(entry):
    if isinstance(entry, dict):
        return entry
    return {"chat_id": entry, "type": "channel", "title": str(entry), "invite_link": "", "is_private": False}

def auto_detect_chat(chat_id_raw):
    res = api_call("getChat", {"chat_id": chat_id_raw})
    if not res.get("ok"):
        return None
    chat = res["result"]
    chat_type = chat.get("type", "")
    title = chat.get("title", str(chat_id_raw))
    username = chat.get("username", "")
    is_private = not bool(username)
    if chat_type in ["supergroup", "group"]:
        detected_type = "group"
    else:
        detected_type = "channel"
    invite_link = ""
    if is_private:
        link_res = api_call("exportChatInviteLink", {"chat_id": chat_id_raw})
        if link_res.get("ok"):
            invite_link = link_res["result"]
    else:
        invite_link = f"https://t.me/{username}"
    return {
        "chat_id": str(chat.get("id", chat_id_raw)),
        "type": detected_type,
        "title": title,
        "invite_link": invite_link,
        "is_private": is_private
    }

def check_force_join(user_id):
    if not bot_settings["fj_on"] or not bot_settings["fj_channels"]: return True
    if is_admin(user_id): return True
    for entry in bot_settings["fj_channels"]:
        ch = _get_fj_chat_id(entry)
        res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})
        if not res.get("ok"):
            continue
        status = res["result"].get("status", "left")
        if status in ["left", "kicked"]:
            return False
    return True

def send_force_join_msg(chat_id):
    kb = []
    for entry in bot_settings["fj_channels"]:
        info = _get_fj_info(entry)
        ch_type = info.get("type", "channel")
        title = info.get("title", "")
        invite_link = info.get("invite_link", "")
        ch_id = info.get("chat_id", "")
        if invite_link:
            url = invite_link
        elif str(ch_id).startswith("@"):
            url = f"https://t.me/{ch_id.replace('@', '')}"
        else:
            url = f"https://t.me/{ch_id}"
        type_label = "Channel" if ch_type == "channel" else "Group"
        btn_text = f"Join {type_label}: {title}" if title else f"Join {type_label}"
        kb.append([{"text": btn_text, "icon_custom_emoji_id": "5789428375261023681", "url": url, "style": "primary"}])
    kb.append([{"text": "Check Joined", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Please join our channels/groups to use the bot!</b>"), reply_markup={"inline_keyboard": kb})

def is_user_banned(user_id):
    if is_admin(user_id): return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 60:
        return user_banned_cache[user_id]['banned']
    local_u = _get_local_user(user_id)
    banned = local_u.get("banned", False)
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned

# =============================================
# FIX: IMPROVED OTP EXTRACTION - Skip dates
# =============================================
def extract_otp_code(text):
    """Extract OTP code with better accuracy - skip dates/timestamps"""
    if not text:
        return None
        
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))
    
    # Skip date/time formats
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z',
        r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',
        r'\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}',
        r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}',
    ]
    
    for pattern in date_patterns:
        if re.search(pattern, clean_text):
            if len(clean_text) < 30 and re.match(r'^[\d\-:TZ\/\s]+$', clean_text):
                return None
    
    # Priority 1: OTP patterns
    otp_patterns = [
        r'(?:code|otp|pin|verification|auth|your code|is|:)\s*(?:is|:|-|=)?\s*([0-9]{4,8})',
        r'G-([0-9]{6})',
        r'([0-9]{4,8})\s*(?:is your|is the|code|otp|pin)',
        r'(?:verification|verify|confirm)\s*(?:code|pin|otp)?\s*(?:is|:|-|=)?\s*([0-9]{4,8})',
        r'(?<!\d)([0-9]{6})(?!\d)',
        r'(?<!\d)([0-9]{5})(?!\d)',
        r'(?<!\d)([0-9]{4})(?!\d)',
        r'(?<!\d)([0-9]{7})(?!\d)',
        r'(?<!\d)([0-9]{8})(?!\d)',
        # OTP with dash like 451-152
        r'([0-9]{3}[-][0-9]{3})',
        # OTP with space like 451 152
        r'([0-9]{3}\s[0-9]{3})',
    ]
    
    for pattern in otp_patterns:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            otp = match.group(1).replace('-', '').replace(' ', '')
            
            # Skip if it looks like a date
            if re.match(r'^\d{2}-\d{2}-\d{2}$', otp):
                continue
            if re.match(r'^\d{4}-\d{2}-\d{2}$', otp):
                continue
            if re.match(r'^\d{2}-\d{2}$', otp) and len(otp) < 5:
                continue
                
            if len(otp) >= 4 and len(otp) <= 8 and otp not in ['000000', '0000']:
                return otp
    
    # Priority 2: Multi-part OTP
    multi_part = re.search(r'(\d{3}[\s-]+\d{3})|(\d{2}[\s-]+\d{2}[\s-]+\d{2})', clean_text)
    if multi_part:
        otp = multi_part.group(0).replace(" ", "").replace("-", "")
        if len(otp) >= 4 and len(otp) <= 8:
            return otp
    
    # Priority 3: Any 4-8 digit number (last resort)
    digit_matches = re.findall(r'(?<!\d)(\d{4,8})(?!\d)', clean_text)
    
    for match in digit_matches:
        if re.match(r'^\d{2}\d{2}\d{2}$', match) and match[:2] in ['19', '20']:
            continue
        if re.match(r'^\d{4}\d{2}\d{2}$', match) and match[:4] in ['2024', '2025', '2026']:
            continue
        if match not in ['000000', '0000']:
            return match
    
    return None

# =============================================
# FIX: IMPROVED PANEL RESPONSE PARSING FOR THIRDWAVE TRAFFIC
# =============================================
def parse_panel_response(response_text, p_config=None):
    """Parse panel response with Thirdwave traffic support"""
    results = []
    p_type = p_config.get("type", "API Panel") if p_config else "API Panel"
    
    n_col_name = p_config.get("num_col_name", "number").lower() if p_config else "number"
    m_col_name = p_config.get("msg_col_name", "message").lower() if p_config else "message"
    n_idx = int(p_config.get("num_col_idx", 1)) - 1 if p_config and p_config.get("num_col_idx") else 1
    m_idx = int(p_config.get("msg_col_idx", 2)) - 1 if p_config and p_config.get("msg_col_idx") else 2

    # First try JSON parsing
    try:
        data = json.loads(response_text)
        temp_results = []
        
        def extract_data(item):
            number = None
            message = None
            
            if isinstance(item, dict):
                # Try to find number - Thirdwave uses "Action" field
                for key in ['Action', 'number', 'phone', 'msisdn', 'sender', 'num', 'from', 'to']:
                    if key in item:
                        val = str(item[key]).strip()
                        clean_num = re.sub(r'\D', '', val)
                        if 4 <= len(clean_num) <= 18:
                            number = clean_num
                            break
                
                # Try to find message - Thirdwave uses "Message" field
                for key in ['Message', 'message', 'msg', 'sms', 'content', 'text', 'body', 'otp_message']:
                    if key in item:
                        val = str(item[key]).strip()
                        if len(val) > 4:
                            message = val
                            break
                
                # If no message found, check all values
                if not message:
                    for key, val in item.items():
                        if key not in ['Action', 'number', 'phone', 'msisdn', 'sender', 'num', 'from', 'to', 'id', 'timestamp', 'time', 'Rate']:
                            val_str = str(val).strip()
                            if len(val_str) > 4 and val_str != 'null' and val_str != 'None':
                                test_otp = extract_otp_code(val_str)
                                if test_otp:
                                    message = val_str
                                    break
                
                # If number not found, try to extract from message
                if not number and message:
                    num_match = re.search(r'(\d{7,15})', message)
                    if num_match:
                        number = num_match.group(1)
            
            elif isinstance(item, list):
                for val in item:
                    if isinstance(val, str):
                        if re.sub(r'\D', '', val) and 4 <= len(re.sub(r'\D', '', val)) <= 18:
                            if not number:
                                number = re.sub(r'\D', '', val)
                        elif len(val) > 4:
                            if extract_otp_code(val):
                                message = val
                                break
            
            if number and message:
                otp = extract_otp_code(message)
                if otp and len(otp) >= 4:
                    return {"number": number, "message": message, "otp": otp}
            return None
        
        def traverse(node):
            if isinstance(node, dict):
                result = extract_data(node)
                if result:
                    temp_results.append(result)
                for val in node.values():
                    if isinstance(val, (dict, list)):
                        traverse(val)
            elif isinstance(node, list):
                for item in node:
                    if isinstance(item, (dict, list)):
                        traverse(item)
                    elif isinstance(item, str):
                        result = extract_data([item])
                        if result:
                            temp_results.append(result)
        
        # Special handling for Thirdwave traffic response
        if isinstance(data, dict) and 'rows' in data and isinstance(data['rows'], list):
            # Thirdwave traffic format
            for item in data['rows']:
                result = extract_data(item)
                if result:
                    temp_results.append(result)
        else:
            traverse(data)
        
        # Deduplicate
        seen = set()
        for r in temp_results:
            uid = f"{r['number']}_{r['otp']}"
            if uid not in seen:
                seen.add(uid)
                results.append(r)
                
    except json.JSONDecodeError:
        # HTML fallback parsing
        if p_type == "Auto Captcha Panel":
            try:
                soup = BeautifulSoup(response_text, 'html.parser')
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    if not rows: continue
                    
                    final_n_idx = n_idx
                    final_m_idx = m_idx
                    
                    header_cells = rows[0].find_all(['th', 'td'])
                    for i, cell in enumerate(header_cells):
                        c_text = cell.get_text(strip=True).lower()
                        if n_col_name in c_text: final_n_idx = i
                        if m_col_name in c_text: final_m_idx = i

                    for row in rows:
                        cols = row.find_all(['td', 'th'])
                        if all(c.name == 'th' for c in cols): continue
                        
                        if len(cols) > max(final_n_idx, final_m_idx):
                            num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                            msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                            
                            clean_num = re.sub(r'\D', '', num_text)
                            
                            if clean_num and 4 <= len(clean_num) <= 18:
                                otp = extract_otp_code(msg_text)
                                if otp and len(msg_text) > 4:
                                    results.append({"number": clean_num, "message": msg_text, "otp": otp})
            except Exception as e:
                print(f"⚠️ HTML parse error: {e}")
    
    return results

def attempt_auto_login(p, idx):
    login_url = p.get("login_url", "").strip()
    if not login_url.startswith("http"):
        login_url = "http://" + login_url
        
    if not login_url.lower().endswith('/login') and not login_url.lower().endswith('.php'):
        login_url = f"{login_url.rstrip('/')}/login"
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    
    try:
        res = session.get(login_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        all_text = res.text
        
        captcha_match = re.search(r'(\d+\s*[\+\-\*]\s*\d+)\s*[=\?:]', all_text)
        if not captcha_match:
            captcha_match = re.search(r'what is\s*(\d+\s*[\+\-\*]\s*\d+)', all_text, re.I)
        if not captcha_match:
            elements = soup.find_all(["label", "div", "span", "p", "strong"])
            for el in elements:
                txt = el.get_text(separator=" ", strip=True)
                if any(op in txt for op in ["+", "-", "*"]):
                    m = re.search(r'(\d+\s*[\+\-\*]\s*\d+)', txt)
                    if m:
                        captcha_match = m
                        break
                        
        captcha_text = captcha_match.group(1) if captcha_match else "0 + 0"
        answer = "0"
        m2 = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', captcha_text)
        if m2:
            a, op, b = int(m2.group(1)), m2.group(2), int(m2.group(3))
            if op == '+': answer = str(a + b)
            elif op == '-': answer = str(a - b)
            elif op == '*': answer = str(a * b)

        form = soup.find("form")
        if not form:
            p["login_status"] = "❌ No login form found"
            return False
            
        action = form.get("action")
        from urllib.parse import urljoin, urlparse, parse_qs
        post_url = urljoin(login_url, action) if action else login_url

        form_data = {}
        for hidden in form.find_all("input", type="hidden"):
            name = hidden.get("name")
            if name: form_data[name] = hidden.get("value") or ""
        
        def _fmatch(keywords):
            def _check(val):
                if not val: return False
                v = val.lower()
                return any(k in v for k in keywords)
            return _check

        user_input = (
            form.find("input", {"name": _fmatch(["user", "email", "id"])}) or
            form.find("input", {"type": "text", "placeholder": _fmatch(["user", "email"])}) or
            form.find("input", {"type": "text"})
        )

        pass_input = (
            form.find("input", {"name": _fmatch(["pass", "password", "passwd"])}) or
            form.find("input", {"type": "password"})
        )

        captcha_input = (
            form.find("input", {"placeholder": _fmatch(["answer", "ans", "code", "verification", "value", "captcha"])}) or
            form.find("input", {"name": _fmatch(["ans", "captcha", "ver", "code"])})
        )
        
        user_field = user_input.get("name") if user_input else "username"
        pass_field = pass_input.get("name") if pass_input else "password"
        captcha_field = captcha_input.get("name") if captcha_input else "answer"

        form_data[user_field] = p.get("username", "")
        form_data[pass_field] = p.get("password", "")
        if captcha_input and captcha_field:
            form_data[captcha_field] = answer

        login_req = session.post(post_url, data=form_data, allow_redirects=True, timeout=15)
        
        msg_link = p.get("msg_link", "").strip()
        if not msg_link.startswith("http") and msg_link != "":
            msg_link = "http://" + msg_link
            
        check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
        
        check_res = session.get(check_url, timeout=10)
        
        login_success_keywords = [
            'logout', 'log out', 'signout', 'sign out',
            'sms reports', 'dashboard', 'cdrs',
            'welcome', 'profile', 'panel', 'inbox',
            'number', 'report', 'home', 'account',
            'client', 'smscdr', 'numberpanel'
        ]
        combined_text = (login_req.text + check_res.text).lower()
        if any(kw in combined_text for kw in login_success_keywords):
            panel_sessions[idx] = session
            p["login_status"] = "✅ Active & Fetching"
            return True
        else:
            uf = user_input.get("name") if user_input else "NOT FOUND"
            pf = pass_input.get("name") if pass_input else "NOT FOUND"
            cf = captcha_input.get("name") if captcha_input else "none"
            p["login_status"] = f"❌ Login Failed (fields: user={uf}, pass={pf}, captcha={cf})"
            return False
            
    except Exception as e:
        p["login_status"] = f"❌ Error: {str(e)[:50]}"
        
    return False

def panel_monitor_thread():
    global processed_otps, recent_traffic, panel_sessions, panel_warmup_done
    first_run = True
    while True:
        try:
            for idx, p in enumerate(bot_settings.get("panels", [])):
                if p.get("status") == "ON":
                    
                    if p.get("type") == "Auto Captcha Panel":
                        sess = panel_sessions.get(idx)
                        
                        if not sess:
                            now = time.time()
                            if now - p.get("last_login_attempt", 0) < 30: 
                                continue 
                            p["last_login_attempt"] = now
                            
                            success = attempt_auto_login(p, idx)
                            save_db()
                            if not success:
                                continue 
                            sess = panel_sessions.get(idx)
                            
                        try:
                            parsed_data, res_text = fetch_cpt_panel_cdrs(p, sess, p["msg_link"])
                            p["login_status"] = "✅ Active & Fetching"
                        except Exception as e:
                            p["login_status"] = "❌ Session Expired (Retrying...)"
                            del panel_sessions[idx]
                            save_db()
                            continue

                    elif p.get("api_url") or p.get("full_api_url"):
                        full_url = p.get("full_api_url", "").strip()
                        url = p.get("api_url", "").strip()
                        token = p.get("token", "").strip()
                        if not full_url and not url:
                            continue

                        urls_to_try = []
                        try:
                            if full_url:
                                urls_to_try.append(full_url)
                            else:
                                # =============================================
                                # FIX: Thirdwave uses /traffic endpoint for SMS data
                                # =============================================
                                if "thirdwave" in url.lower() or "thirdwave.im" in url.lower() or "app.thirdwave.im" in url:
                                    base_url = url.split('/api/')[0] if '/api/' in url else url
                                    base_url = base_url.rstrip('/')
                                    # As per manager: /traffic contains all data including SMS
                                    urls_to_try = [
                                        f"{base_url}/api/v1/traffic?token={token}",
                                        f"{base_url}/api/v1/traffic?key={token}",
                                        f"{base_url}/api/v1/traffic?api_key={token}",
                                        f"{base_url}/api/v1/traffic?type=sms&token={token}",
                                        f"{base_url}/api/v1/traffic?type=otp&token={token}",
                                        f"{base_url}/api/v1/numbers?token={token}",
                                    ]
                                    print(f"🔍 Thirdwave: Trying /traffic endpoint (manager suggested)")
                                else:
                                    if "{token}" in url or "{key}" in url:
                                        urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                                    elif "token=" in url or "key=" in url:
                                        urls_to_try.append(url)
                                    else:
                                        sep = '&' if '?' in url else '?'
                                        urls_to_try.append(f"{url}{sep}token={token}")
                                        urls_to_try.append(f"{url}{sep}key={token}&start=0")
                                        urls_to_try.append(f"{url}{sep}key={token}")
                        except Exception as e:
                            print(f"Error building URLs: {e}")
                            urls_to_try = []

                        parsed_data = []
                        raw_text = ""
                        try:
                            # =============================================
                            # FIX: Better headers with multiple auth methods
                            # =============================================
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                'Accept': 'application/json',
                            }
                            
                            zenex_target = full_url or url
                            
                            # Thirdwave - Bearer token (as per documentation)
                            if "thirdwave" in str(urls_to_try).lower() or "thirdwave" in zenex_target.lower() or "app.thirdwave.im" in zenex_target:
                                if token:
                                    headers['Authorization'] = f'Bearer {token}'
                                    headers['X-API-Key'] = token
                                    print(f"🔑 Thirdwave: Using Bearer token + X-API-Key")
                            
                            # Green SMS - Bearer token
                            if "143.110.245.86" in str(urls_to_try) or "143.110.245.86" in zenex_target:
                                if token:
                                    headers['Authorization'] = f'Bearer {token}'
                                    print(f"🔑 Green SMS: Using Bearer token")
                            
                            # Zenex - mapikey
                            if "zenexnetwork.com" in zenex_target:
                                zenex_key = token
                                if not zenex_key:
                                    try:
                                        zenex_key = parse_qs(urlparse(zenex_target).query).get("key", [''])[0]
                                    except Exception:
                                        zenex_key = ""
                                if zenex_key:
                                    headers['mapikey'] = zenex_key
                                    print(f"🔑 Zenex: Using mapikey")
                            
                            for try_url in urls_to_try:
                                try:
                                    print(f"🔄 Trying: {try_url}")
                                    res = requests.get(try_url, headers=headers, timeout=10)
                                    raw_text = res.text
                                    status_code = res.status_code
                                    content_type = res.headers.get('content-type', '')
                                    
                                    print(f"📊 Status: {status_code}, Content-Type: {content_type}")
                                    
                                    if status_code == 200 and (content_type.startswith('application/json') or raw_text.strip().startswith('{')):
                                        parsed_data = parse_panel_response(raw_text, p)
                                        if parsed_data:
                                            if not full_url and try_url != url and token:
                                                p["api_url"] = try_url.replace(token, "{token}")
                                                save_db()
                                            print(f"✅ Found {len(parsed_data)} OTPs")
                                            break
                                    else:
                                        print(f"⚠️ Status {status_code}, trying next URL")
                                        continue
                                        
                                except Exception as e:
                                    print(f"❌ URL failed: {str(e)[:50]}")
                                    continue
                                    
                        except Exception as e:
                            print(f"Error fetching API data: {e}")
                        
                        if not parsed_data:
                            continue

                    elif p.get("type") == "VoltX Panel":
                        parsed_data = []
                        base_url = p.get("base_url", "").strip()
                        api_key = p.get("api_key", "").strip()
                        if not base_url or not api_key:
                            continue
                        getmsg_url = p.get("getmsg_url", "").strip() or f"{base_url.rstrip('/')}/success-otp"
                        headers_vx = {"Content-Type": "application/json", "mauthapi": api_key}
                        try:
                            otp_res = requests.get(getmsg_url, headers=headers_vx, timeout=15)
                            if otp_res.status_code == 200:
                                otp_data = otp_res.json()
                                otps = otp_data.get("data", {}).get("otps", [])
                                if not isinstance(otps, list):
                                    continue
                                if "lastSeenGetnumIds" not in p or not isinstance(p["lastSeenGetnumIds"], list):
                                    p["lastSeenGetnumIds"] = []
                                is_initial = len(p["lastSeenGetnumIds"]) == 0
                                updated = False
                                for item in otps:
                                    unique_key = str(item.get("otp_id", ""))
                                    msg_body = str(item.get("message", "")).strip()
                                    raw_num = str(item.get("number", ""))
                                    if unique_key and msg_body and unique_key not in p["lastSeenGetnumIds"]:
                                        p["lastSeenGetnumIds"].append(unique_key)
                                        updated = True
                                        if not is_initial:
                                            parsed_data.append({"number": raw_num, "otp": extract_otp_code(msg_body), "message": msg_body})
                                if len(p["lastSeenGetnumIds"]) > 300:
                                    p["lastSeenGetnumIds"] = p["lastSeenGetnumIds"][-300:]
                                if updated:
                                    save_db()
                                if not parsed_data:
                                    continue
                            else:
                                continue
                        except Exception as e:
                            continue
                    else:
                        continue
                    
                    if p.get("type") != "Auto Captcha Panel" and p.get("type") != "VoltX Panel":
                        limit = p.get("records", 0)
                        if limit > 0: parsed_data = parsed_data[:limit]
                        
                    panel_needs_warmup = p.get("needs_warmup", False)
                    for item in parsed_data:
                        num = item["number"]
                        otp = item["otp"]
                        msg_text = item["message"]
                        unique_id = f"{num}_{otp}"
                        
                        if unique_id not in processed_otps:
                            _track_processed_otp(unique_id)
                            
                            if first_run or panel_needs_warmup:
                                continue
                                 
                            char, iso = get_flag_and_code(num)
                            app_full_name, prem_app_html = get_service_info_html(p.get("name", "Panel"), msg_text)
                            current_time = time.time()
                            
                            recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": num,
                                "time": current_time
                            })
                            save_local_db()
                                 
                            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                            lang = detect_language(msg_text)
                            
                            owners = []
                            clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                            
                            for uid, session_data in user_active_sessions.items():
                                for act_num in session_data.get("nums", []):
                                    act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                        owners.append(uid)
                                        break
                                        
                            if not owners:
                                for nexa_n, n_owner in nexa_assigned_numbers.items():
                                    clean_nexa = str(nexa_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if clean_nexa == clean_api_num or (len(clean_nexa) >= 8 and clean_nexa.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_nexa[-8:])):
                                        owners.append(n_owner)
                                        
                            owners = list(set(owners))
                            
                            first_owner = owners[0] if owners else None
                            masked = mask_number(display_num, user_id=first_owner)
                            
                            platform_name = detect_platform_from_message(msg_text)
                            display_msg = render_body_text(f"╔═══════════════╗\n║ {platform_name} {get_flag_info_html(display_num)} #{iso} {masked} {lang}\n╚═══════════════╝")
                            
                            for fw in bot_settings["fw_groups"]:
                                kb = [[{"text": f"📋 {otp}", "copy_text": {"text": otp}}]]
                                kb.append([{"text": "📋 Full Message", "copy_text": {"text": msg_text}}])
                                kb.append([{"text": "🤖 Get Number", "url": f"https://t.me/{BOT_USERNAME.lstrip('@')}"}])
                                for btn in fw.get("buttons", []):
                                    b_obj = {"text": btn["text"], "url": btn["url"]}
                                    kb.append([b_obj])
                                res = send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                if not res.get("ok"):
                                    print(f"❌ Group send failed [{fw['chat_id']}]: {res.get('description', 'Unknown error')}")
                            
                            for owner_id in owners:
                                platform_name = detect_platform_from_message(msg_text)
                                inbox_msg = render_body_text(f"╔═══════════════╗\n║ {platform_name} {get_flag_info_html(display_num)} #{iso} {display_num} {lang}\n╚═══════════════╝")
                                inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                
                                reward = float(bot_settings.get("otp_reward", 0.0))
                                if reward > 0:
                                    update_balance(owner_id, reward)
                                    inbox_kb.append([{"text": f"Added {reward} ₹", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                
                                send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                _increment_local_user(owner_id, "total_otps", 1)
                            try:
                                clean_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                _track_otp_received(clean_num)
                            except: pass
        except Exception as e:
            print(f"⚠️ Panel monitor error: {str(e)[:80]}")
        if first_run:
            first_run = False
            panel_warmup_done = True
            print("🧹 Panel warmup done — old OTPs skipped, now processing new ones only.")
        for p in bot_settings.get("panels", []):
            if p.get("needs_warmup"):
                p["needs_warmup"] = False
                save_db()
                print(f"🧹 Panel '{p.get('name')}' warmup done — old OTPs skipped.")
        time.sleep(5) 

user_cache = {}

def get_user(user_id):
    if user_id in user_cache: return user_cache[user_id]
    data = _get_local_user(user_id)
    user_cache[user_id] = data
    return data

def update_balance(user_id, amount):
    _increment_local_user(user_id, "balance", float(amount))

def add_referral(inviter_id, new_user_id):
    u_data = _get_local_user(new_user_id)
    if not u_data.get("ref_paid"):
        _update_local_user(new_user_id, {"referred_by": inviter_id, "ref_paid": True})
        reward = bot_settings.get("refer_reward", 0.2)
        update_balance(inviter_id, reward)
        _increment_local_user(inviter_id, "total_refers", 1)
        
        ref_msg = (
            f"{PEM['gift']} <b>New Referral !</b>\n"
            f"------------------\n"
            f"\U0001f525 <b>You Received {reward} INR</b>\n"
            f"------------------\n"
            f"{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>"
        )
        send_message(inviter_id, render_body_text(ref_msg))

def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    kb = [
        [
            {"text": "GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "style": "primary"}, 
            {"text": "Search Number", "icon_custom_emoji_id": "5190645917711114179", "style": "primary"}
        ],
        [
            {"text": "TRAFFIC", "icon_custom_emoji_id": "5353032893096567467", "style": "success"}, 
            {"text": "2FA ONLINE", "icon_custom_emoji_id": "5337255927735163754", "style": "primary"}
        ],
        [
            {"text": "Refer", "icon_custom_emoji_id": "5420396762189831222", "style": "success"}, 
            {"text": "WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "style": "danger"}
        ],
        [
            {"text": "SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "style": "primary"}
        ]
    ]
    if is_admin(user_id): 
        kb.append([{"text": "Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}

def get_admin_text():
    users_count = len(all_known_users)
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"},
         {"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "Used (OTP Received)", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "show_used", "style": "success"},
         {"text": "Unused (No OTP)", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Nexa Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "nexa_control", "style": "success"}],
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}], 
        [{"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"},
         {"text": "Subscription", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "dummy_alert", "style": "success"}],
        [{"text": "Saad King Yt Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "abhi_control", "style": "primary"},
         {"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}], 
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def get_user_management_text():
    total = len(all_known_users)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"},
         {"text": "Edit Search Number", "icon_custom_emoji_id": "5190645917711114179", "callback_data": "md_edit_search_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit TRAFFIC", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "md_edit_traffic", "style": "primary"},
         {"text": "Edit Refer", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Edit WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "md_edit_withdrawal", "style": "danger"},
         {"text": "Edit SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "md_edit_support", "style": "danger"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}

def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, entry in enumerate(bot_settings["fj_channels"]):
        info = _get_fj_info(entry)
        ch_type = info.get("type", "channel")
        title = info.get("title", str(info.get("chat_id", "")))
        is_priv = info.get("is_private", False)
        type_tag = "Channel" if ch_type == "channel" else "Group"
        priv_tag = "Private" if is_priv else "Public"
        btn_label = f"{title} [{type_tag} | {priv_tag}]"
        kb.append([{"text": btn_label, "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel / Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    kb = [[{"text": "Edit OTP Button Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}]]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def nexa_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add Nexa Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_nexa_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_nexa_keys", "style": "danger"}],
        [{"text": "Manage Nexa Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_nexa_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "nexa_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def abhi_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    sup_status = "ON" if bot_settings.get("support_link") else "OFF"
    grp_status = "ON" if bot_settings.get("w_group") else "OFF"
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "abhi_toggle_w", "style": "primary"}],
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "abhi_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "abhi_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "abhi_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "abhi_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "abhi_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "abhi_num_share", "style": "primary"}],
        [{"text": f"SUPPORT LINK: {sup_status}", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "abhi_sup_link", "style": "success"},
         {"text": "W. METHODS", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. GROUP: {grp_status}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "abhi_w_group", "style": "success"},
         {"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        kb.append([{"text": f"Delete: {m}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "abhi_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type: continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703" 
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    if p_type == "API Panel": add_cb = "add_api_panel"
    elif p_type == "VoltX Panel": add_cb = "add_voltx_panel"
    else: add_cb = "add_cpt_panel"
    if p_type == "API Panel": del_cb = "list_del_api"
    elif p_type == "VoltX Panel": del_cb = "list_del_voltx"
    else: del_cb = "list_del_cpt"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5420323438508155202", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": del_cb, "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    
    if p["type"] == "VoltX Panel":
        kb.append([{"text": "🌐 Set Base URL", "icon_custom_emoji_id": "5336972142066047577", "callback_data": f"set_p_vbase_{idx}", "style": "primary"}])
        kb.append([{"text": "🔑 Set API Key", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_vkey_{idx}", "style": "primary"}])
        kb.append([{"text": "📥 Set GetNum URL", "icon_custom_emoji_id": "5337132498965010628", "callback_data": f"set_p_vgetnum_{idx}", "style": "primary"}])
        kb.append([{"text": "📨 Set GetMsg URL", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"set_p_vgetmsg_{idx}", "style": "primary"}])
        kb.append([{"text": "📊 Set Traffic URL", "icon_custom_emoji_id": "5352877703043258544", "callback_data": f"set_p_vtraf_{idx}", "style": "primary"}])
        kb.append([{"text": "🔧 Manage VoltX Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"manage_vx_srv_{idx}", "style": "success"}])
    elif p["type"] != "Auto Captcha Panel":
        rec_count_text = "All (Unlimited)" if p.get('records', 0) == 0 else str(p.get('records'))
        kb.append([{"text": "Set API URL", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_api_{idx}", "style": "primary"}])
        kb.append([{"text": "Set Token", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_tok_{idx}", "style": "primary"}])
        kb.append([{"text": "🌐 Full API (URL+Token)", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_fapi_{idx}", "style": "primary"}])
        kb.append([{"text": f"Set Records Count: {rec_count_text}", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"set_p_rec_{idx}", "style": "primary"}])
        
    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
    
    if p.get("type") == "Auto Captcha Panel": back_data = "manage_cpt_panels"
    elif p.get("type") == "VoltX Panel": back_data = "manage_voltx_panels"
    else: back_data = "manage_api_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
    return {"inline_keyboard": kb}

def build_traffic_ui():
    global recent_traffic
    current_time = time.time()
    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
    
    stats = {}
    for t in recent_traffic:
        srv = t.get("service", "Unknown")
        iso = t.get("iso", "XX")
        flag = t.get("flag", "🌍")
        
        if srv not in stats:
            stats[srv] = {}
        if iso not in stats[srv]:
            stats[srv][iso] = {"count": 0, "flag": flag}
        stats[srv][iso]["count"] += 1
        
    txt = "╔═════════════════╗\n║  📈 <b>NETWORK TRAFFIC</b>\n╚═════════════════╝\n\n"
    
    kb = []
    if not stats:
        txt += "<i>No recent traffic found in the last hour...</i>\n"
    else:
        srv_totals = []
        for srv, countries in stats.items():
            total = sum(c["count"] for c in countries.values())
            srv_totals.append((srv, total, countries))
        
        srv_totals.sort(key=lambda x: x[1], reverse=True)
        
        for srv, total, countries in srv_totals:
            app_full_name, prem_app_html = get_service_info_html(srv)
            txt += f"[ {prem_app_html} <b>{app_full_name}</b> ]\n│\n"
            
            c_list = sorted(countries.items(), key=lambda x: x[1]["count"], reverse=True)
            c_list = c_list[:7] 
            
            for i, (iso, c_data) in enumerate(c_list):
                prem_flag_html = get_flag_info_html(iso)
                count = c_data["count"]
                
                c_name = iso
                for code, fdata in bot_settings.get("premium_flags", {}).items():
                    if fdata.get("iso") == iso:
                        c_name = fdata.get("name", iso)
                        break
                        
                txt += f"├ {prem_flag_html} <b>{c_name} ({iso})</b>\n"
                txt += f"│ ╰ Success: {count}\n"
                if i < len(c_list) - 1:
                    txt += "│\n"
            txt += "\n"
        
        for srv, _, _ in srv_totals: 
            safe_srv = srv[:20] 
            app_full_name, _ = get_service_info_html(safe_srv, safe_srv)
            kb.append([{"text": f"Explore {app_full_name} Range", "icon_custom_emoji_id": "5190645917711114179", "callback_data": f"exp_rng_{safe_srv}", "style": "success"}])
            
    txt = render_body_text(txt)
    kb.append([{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "refresh_traffic", "style": "primary"}])
    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
    
    return txt, {"inline_keyboard": kb}

def handle_message(msg):
    global total_uploaded_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    
    if chat_type != "private":
        return
        
    text = msg.get("text", "")
    register_user_local(chat_id)

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                u_data = _get_local_user(chat_id)
                if not u_data.get("referred_by"):
                    _update_local_user(chat_id, {"referred_by": inviter, "ref_paid": False})
                        
    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
        
    MAIN_MENU_CMDS = ["GET NUMBER", "Search Number", "TRAFFIC", "Refer", "WITHDRAWAL", "SUPPORT", "Admin Panel", "2FA ONLINE"]
    
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True
    
    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]
        
        if state == "wait_for_cpanel_url" and text:
            temp_data[chat_id]["p_data"]["login_url"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_user"
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ Enter Panel Username:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_user" and text:
            temp_data[chat_id]["p_data"]["username"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_pass"
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ Enter Panel Password:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_pass" and text:
            temp_data[chat_id]["p_data"]["password"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_link"
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ Enter the link where SMS/OTP data (JSON) comes from:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_link" and text:
            temp_data[chat_id]["p_data"]["msg_link"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_name"
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ What is the Number column name in Data? (e.g.: number, phone):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp_data[chat_id]["p_data"]["num_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_idx"
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Serial</b>\n➡️ What is the Number Column Serial Number? (e.g.: 3, 5):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["num_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_msg_col_name"
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ What is the Message/OTP column name? (e.g.: message, sms):"), reply_markup=get_cancel_kb())
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp_data[chat_id]["p_data"]["msg_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_col_idx"
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Serial</b>\n➡️ What is the Message Column Serial Number? (e.g.: 5, 7):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["msg_col_idx"] = int(text)
                temp_data[chat_id]["p_data"]["login_status"] = "⏳ Pending Auto-Login..."
                temp_data[chat_id]["p_data"]["needs_warmup"] = True
                bot_settings["panels"].append(temp_data[chat_id]["p_data"])
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Auto Captcha Panel Added Successfully!</b>\nBot will now automatically solve captcha and login in background."), reply_markup=main_menu(chat_id))
                msg_id = temp_data[chat_id]["msg_id"]
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_cpt_panels", "id": "internal"})
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID! Please send a numeric User ID."), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            user_data = _get_local_user(target_uid)
            current_bal = user_data.get('balance', 0.0)
            temp_data[chat_id]["target_uid"] = target_uid
            user_states[chat_id] = "wait_for_um_bal_amt"
            send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {current_bal} ₹\n\n📝 Send the amount to ADD (e.g. 50) or REMOVE (e.g. -50):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip())
                target_uid = temp_data[chat_id]["target_uid"]
                old_bal = _get_local_user(target_uid).get('balance', 0.0)
                update_balance(target_uid, amt)
                new_bal = _get_local_user(target_uid).get('balance', 0.0)
                send_message(chat_id, render_body_text(f"{PEM['ok']} Balance updated!\n{PEM['user']} User: <code>{target_uid}</code>\n💰 Old: {old_bal} ₹ → New: {new_bal} ₹"), reply_markup=main_menu(chat_id))
                
                if amt >= 0:
                    notif_text = f"{PEM['gift']} <b>Balance Added!</b>\n➖➖➖➖➖➖➖\n💰 <b>Amount:</b> +{amt} ₹\n💰 <b>New Balance:</b> {new_bal} ₹\n➖➖➖➖➖➖➖\n👨‍⚖️ <b>By Admin</b>"
                else:
                    notif_text = f"{PEM['warn']} <b>Balance Removed!</b>\n➖➖➖➖➖➖➖\n💰 <b>Amount:</b> {amt} ₹\n💰 <b>New Balance:</b> {new_bal} ₹\n➖➖➖➖➖➖➖\n👨‍⚖️ <b>By Admin</b>"
                send_message(target_uid, render_body_text(notif_text))
                del user_states[chat_id]
                del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount! Please send a number."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            user_data = _get_local_user(target_uid)
            current_status = user_data.get("banned", False)
            new_status = not current_status
            _update_local_user(target_uid, {"banned": new_status})
            user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
            status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
            send_message(chat_id, render_body_text(f"✅ User {target_uid} has been {status_text}!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            data = _get_local_user(target_uid)
            is_verified = True if data.get('total_otps', 0) > 0 else data.get('verified', False)
            prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {data.get('balance', 0.0)} ₹
🤝 Total Refers: {data.get('total_refers', 0)}
🔐 Total OTPs: {data.get('total_otps', 0)}
✅ Verified: {is_verified}
🚫 Banned: {data.get('banned', False)}
➖➖➖➖➖➖➖➖"""
            kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
            send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                formatted_html_text = extract_premium_html(msg)
                bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                save_db()
                delete_message(chat_id, msg["message_id"])
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Message Body Updated successfully!</b>\n\n🎨 <b>Editing: {menu_key.upper()}</b>\n\nPreview of current Text:\n{preview_text}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                send_message(chat_id, f"❌ Error saving text: {e}")
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
            
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    
                    emoji_id = None
                    emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0)
                            length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                            break
                            
                    if emoji_char:
                        btn_text = btn_text.replace(emoji_char, "").strip()
                        
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary"}
                    if emoji_id:
                        btn_data["icon_custom_emoji_id"] = emoji_id
                        
                    bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['gear']} <b>Edit Inline Buttons: {menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format. Use <code>Button Text - https://link.com</code>"))
            except Exception as e:
                 pass
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 Send the Number (e.g. +8801712345678):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 Send the OTP (e.g. 556677):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 Send the Language (e.g. EN, AR):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"):
                lang = "#" + lang
                
            srv = temp_data[chat_id]["service"]
            num = temp_data[chat_id]["number"]
            otp = temp_data[chat_id]["otp"]
            
            masked = mask_number(num, user_id=chat_id)
            prem_flag_html = get_flag_info_html(num)
            char, iso = get_flag_and_code(num)
            app_full_name, prem_app_html = get_service_info_html(srv)
            
            msg_text = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {prem_flag_html} #{iso} {masked} {lang}\n╚═══════════════╝")
            
            for fw in bot_settings["fw_groups"]:
                kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                kb.append([{"text": "Full Message", "icon_custom_emoji_id": "5337302974806922068", "copy_text": {"text": "Test message - no original SMS"}, "style": "primary"}])
                for btn in fw.get("buttons", []):
                    b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
                    if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                    kb.append([b_obj])
                send_message(fw["chat_id"], msg_text, reply_markup={"inline_keyboard": kb})
                
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test message formatted and sent to all Forward Groups!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_emoji_extract":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode('utf-16-le')
                    emoji_text = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                    break
            
            if custom_emoji_id:
                temp_data[chat_id] = {"id": custom_emoji_id, "char": emoji_text}
                user_states[chat_id] = "wait_for_emoji_details"
                send_message(chat_id, render_body_text(f"{PEM['ok']} Emoji ID found: <code>{custom_emoji_id}</code>\n\n📌 Now type and enter the name to save it.\n\n<b>Format:</b>\n`FLAG | 880 | BD | Bangladesh`\nor\n`APP | WhatsApp`"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} No Premium Emoji found! Please send a Custom Emoji."), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_emoji_details" and text:
            parts = [p.strip() for p in text.split("|")]
            mode = parts[0].upper()
            eid = temp_data[chat_id]["id"]
            char = temp_data[chat_id]["char"]
            
            if mode == "FLAG" and len(parts) == 4:
                code, iso, name = parts[1], parts[2], parts[3]
                bot_settings["premium_flags"][code] = {"char": char, "iso": iso.upper(), "name": name, "id": eid}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Flag Emoji saved!\nCode: {code} | Name: {name}"), reply_markup=emoji_settings_keyboard())
            elif mode == "APP" and len(parts) == 2:
                name = parts[1]
                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name.title()}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} App Emoji saved!\nName: {name}"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} Wrong format!\n\nCorrect format:\n`FLAG | 880 | BD | Bangladesh`\n`APP | WhatsApp`"))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            content = requests.get(f"{FILE_URL}{file_path}").text
            
            mode = "flags" if state == "wait_for_flag_txt" else "apps"
            count = 0
            
            if mode == "flags":
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            prefix_str = line[:json_match.start()].strip()
                            code_match = re.search(r'\((\d+)\)', prefix_str)
                            iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                            
                            if code_match and iso_match and char and eid:
                                code = code_match.group(1)
                                iso = iso_match.group(1).upper()
                                name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                count += 1
                        except: pass
            else:
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            name_part = line[:json_match.start()].strip()
                            name = name_part.replace(char, '').strip() if char else name_part
                            
                            if char and eid and name:
                                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                count += 1
                        except: pass
            
            save_db()
            send_message(chat_id, render_body_text(f"{PEM['ok']} Successfully loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            del user_states[chat_id]
            return

        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id)).start()
            del user_states[chat_id]
            return

        elif state == "wait_for_txt" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"{FILE_URL}{file_path}").text
            
            temp_data[chat_id] = {"numbers": file_content.splitlines(), "filename": doc["file_name"]}
            user_states[chat_id] = "wait_for_service"
            send_message(chat_id, render_body_text(f"{PEM['ok']} File received.\n\n📌 Enter the service name (e.g., WHATSAPP):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_service" and text:
            temp_data[chat_id]["service"] = text.upper()
            user_states[chat_id] = "wait_for_country"
            send_message(chat_id, render_body_text(f"{PEM['ok']} Service set.\n\n🌍 Enter the country name (e.g., YEMEN):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_country" and text:
            country = text.upper()
            service = temp_data[chat_id]["service"]
            raw_numbers = temp_data[chat_id]["numbers"]
            
            clean_nums = []
            for num in raw_numbers:
                num = num.strip()
                if num:
                    if not num.startswith('+'): num = '+' + num
                    clean_nums.append(num)
            
            batch_id = str(uuid.uuid4())[:8]
            number_batches[batch_id] = {"filename": temp_data[chat_id]["filename"], "service": service, "country": country, "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]}
            total_uploaded_stats += len(clean_nums)
            save_db()
            
            app_full_name, prem_app_html = get_service_info_html(service)
            prem_flag_html = get_flag_info_html(clean_nums[0]) if clean_nums else f"{PEM['world']} "
            
            broadcast_txt = f"➖➖➖➖➖➖➖➖\n《 NEW NUMBERS 》\n➖➖➖➖➖➖➖➖\n{prem_flag_html} {country} {prem_app_html} {service}\n➖➖➖➖➖➖➖➖\n📤 Total Added: <b>{len(clean_nums)}</b>\n➖➖➖➖➖➖➖➖\nUse /start to get your numbers!"
            broadcast_txt = render_body_text(broadcast_txt)
            
            send_message(chat_id, render_body_text(f"{PEM['ok']} Numbers added to local stock! Starting broadcast..."))
            
            def simple_broadcast(txt):
                b_session = requests.Session()
                url = f"{BASE_URL}/sendMessage"
                for u_id in list(all_known_users):
                    try:
                        b_session.post(url, json={"chat_id": u_id, "text": txt, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=5)
                    except: pass
                    time.sleep(0.035)
            threading.Thread(target=simple_broadcast, args=(broadcast_txt,)).start()
            
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_nexa_key" and text:
            bot_settings["nexa_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Nexa API Key Added! Total Keys: {len(bot_settings.get('nexa_keys', []))}"), reply_markup=nexa_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
            bot_settings["search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            kb = []
            for idx, c in enumerate(bot_settings.get("search_countries", [])):
                kb.append([{"text": f"❌ Delete {c}", "callback_data": f"del_sc_{idx}", "style": "danger"}])
            kb.append([{"text": "➕ Add Country Code", "callback_data": "add_search_country", "style": "success"}])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "nexa_control", "style": "primary"}])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_nx_srv_name" and text:
            srv = text.strip().upper()
            if "nexa_services" not in bot_settings: bot_settings["nexa_services"] = {}
            if srv not in bot_settings["nexa_services"]: bot_settings["nexa_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_nexa_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["nexa_services"][srv]: bot_settings["nexa_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["nexa_services"][srv][cnt]:
                bot_settings["nexa_services"][srv][cnt].append(new_range)
                
                if "search_countries" not in bot_settings:
                    bot_settings["search_countries"] = []
                if new_range not in bot_settings["search_countries"]:
                    bot_settings["search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_wm" and text:
            bot_settings["w_methods"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fj" and text:
            raw_input = text.strip()
            if "t.me/+" in raw_input or "t.me/joinchat/" in raw_input:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("⚠️ <b>Private invite link detected!</b>\n\nPrivate channel/group ke liye numeric ID bhejein (e.g. <code>-1001234567890</code>)\n\nID kaise pata karein:\n1. Channel/Group mein koi message forward karein\n2. @userinfobot ko forward karein\n3. Woh aapko ID de dega"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})
                return
            parsed_id = parse_chat_id(raw_input)
            detected = auto_detect_chat(parsed_id)
            if detected:
                bot_settings["fj_channels"].append(detected)
                save_db()
                delete_message(chat_id, msg["message_id"])
                type_label = "Channel" if detected["type"] == "channel" else "Group"
                priv_label = "Private" if detected["is_private"] else "Public"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ <b>Successfully Added!</b>\n\n{type_label} | {priv_label}\n📌 Title: <b>{detected['title']}</b>\n🆔 ID: <code>{detected['chat_id']}</code>\n🔗 Link: {detected.get('invite_link', 'N/A')}"), reply_markup=fj_settings_keyboard())
            else:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("❌ <b>Error!</b> Bot is not admin in this channel/group ya invalid ID hai.\n\nMake sure:\n1. Bot ko channel/group mein add karein\n2. Bot ko admin banaayein\n3. Phir dobara try karein"), reply_markup={"inline_keyboard": [[{"text": "🔄 Try Again", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                bot_settings["admins"].append(int(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fw_id" and text:
            bot_settings["fw_groups"].append({"chat_id": text.strip(), "buttons": []})
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp_data[chat_id]["fw_idx"]
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                
                emoji_id = None
                emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0)
                        length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                
                if emoji_char:
                    btn_text = btn_text.replace(emoji_char, "").strip()
                    
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id:
                    btn_data["icon_custom_emoji_id"] = emoji_id
                    
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][fw_idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp_data[chat_id].get("add_type", "api")
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            
            if t_key == "logc":
                user_states[chat_id] = "wait_for_cpanel_url"
                temp_data[chat_id] = {"msg_id": msg_id, "p_data": {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", "records": 0, "login_status": "⏳ Pending First Login"
                }}
                edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>\n➡️ Enter Panel Login Link:"), reply_markup=get_cancel_kb())
                return
            elif t_key == "voltx":
                bot_settings["panels"].append({
                    "name": p_name, "type": "VoltX Panel", "status": "OFF",
                    "base_url": "", "api_key": "", "getnum_url": "", "getmsg_url": "", "traffic_url": "",
                    "lastSeenGetnumIds": []
                })
                save_db()
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_panels", "id": "internal"})
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return
            else:
                bot_settings["panels"].append({
                    "name": p_name, "type": "API Panel", "status": "OFF", "api_url": "", "token": "", "records": 0, "needs_warmup": True
                })
                save_db()
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_api_panels", "id": "internal"})
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return

        elif state == "wait_for_p_api" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_tok" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["token"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_fapi" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["full_api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_rec" and text:
            if text.isdigit():
                idx = temp_data[chat_id]["p_idx"]
                bot_settings["panels"][idx]["records"] = int(text)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                
                ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number! Try again."), reply_markup=get_cancel_kb())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_voltx_base_url" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["base_url"] = text.strip().rstrip("/")
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            api_key_m = (p.get("api_key","")[:4]+"****"+p.get("api_key","")[-4:]) if len(p.get("api_key",""))>8 else p.get("api_key","None")
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status']=='ON' else '🔴 Stopped'}\n<b>Base URL:</b> <code>{p.get('base_url','None')}</code>\n<b>API Key:</b> <code>{api_key_m}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]; del temp_data[chat_id]
            return

        elif state == "wait_for_voltx_api_key" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["api_key"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            api_key_m = (p.get("api_key","")[:4]+"****"+p.get("api_key","")[-4:]) if len(p.get("api_key",""))>8 else p.get("api_key","None")
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status']=='ON' else '🔴 Stopped'}\n<b>Base URL:</b> <code>{p.get('base_url','None')}</code>\n<b>API Key:</b> <code>{api_key_m}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]; del temp_data[chat_id]
            return

        elif state == "wait_for_voltx_getnum_url" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["getnum_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>GetNum URL:</b> <code>{p.get('getnum_url','Auto')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]; del temp_data[chat_id]
            return

        elif state == "wait_for_voltx_getmsg_url" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["getmsg_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>GetMsg URL:</b> <code>{p.get('getmsg_url','Auto')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]; del temp_data[chat_id]
            return

        elif state == "wait_for_voltx_traffic_url" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["traffic_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Traffic URL:</b> <code>{p.get('traffic_url','Auto')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]; del temp_data[chat_id]
            return

        elif state == "wait_vx_srv_name" and text:
            srv = text.strip()
            msg_id = temp_data[chat_id]["msg_id"]
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            if srv not in bot_settings["voltx_services"]: bot_settings["voltx_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_vx_srv", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]
            return

        elif state == "wait_vx_cnt_name" and text:
            srv = temp_data[chat_id]["srv"]
            msg_id = temp_data[chat_id]["msg_id"]
            cnt = text.strip()
            if cnt not in bot_settings["voltx_services"][srv]:
                bot_settings["voltx_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]
            return

        elif state == "wait_vx_addr" and text:
            srv = temp_data[chat_id]["srv"]
            cnt = temp_data[chat_id]["cnt"]
            msg_id = temp_data[chat_id]["msg_id"]
            new_range = text.strip()
            if new_range not in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].append(new_range)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]
            return

        elif state == "set_abhi":
            msg_id = temp_data[chat_id]["msg_id"]
            key = temp_data[chat_id]["key"]
            try:
                if key in ["min_withdraw", "otp_reward", "refer_reward"]: bot_settings[key] = float(text)
                elif key in ["cooldown", "num_req", "num_share"]: bot_settings[key] = int(text)
                else: bot_settings[key] = text
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>SAAD KING YT CONTROL PANEL</b>"), reply_markup=abhi_control_keyboard())
            except:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>SAAD KING YT CONTROL PANEL</b>\n\n❌ Invalid value!"), reply_markup=abhi_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text("❌ Please enter a valid 3 to 9 digit number!"))
                return
                
            wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = wait_msg.get("result", {}).get("message_id")
            
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))

            if not found_indices:
                has_matching = False
                for b_id, b_data in number_batches.items():
                    for n_obj in b_data["numbers"]:
                        if n_obj["num"].replace("+", "").startswith(query):
                            has_matching = True
                            n_obj["shares"] = 0
                            n_obj["used_by"] = []
                if has_matching:
                    for b_id, b_data in number_batches.items():
                        for idx, n_obj in enumerate(b_data["numbers"]):
                            if n_obj["num"].replace("+", "").startswith(query):
                                found_indices.append((b_id, idx))

            fetched_nums = []
            if not found_indices:
                allowed_countries = bot_settings.get("search_countries", [])
                
                is_nexa_allowed = False
                if not allowed_countries:
                    is_nexa_allowed = True
                elif any(query.startswith(c) for c in allowed_countries):
                    is_nexa_allowed = True
                    
                if not is_nexa_allowed:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ number out of stock!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                    
                if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Processing... Finding Number via API...</i>"))
                
                nexa_found = False
                nexa_keys = bot_settings.get("nexa_keys", [])
                
                t_len = 12
                if query.startswith("880"): t_len = 13
                elif query.startswith("1") and len(query) < 12: t_len = 11
                
                search_range = query + ("X" * (t_len - len(query))) if len(query) < t_len else query
                
                for _ in range(bot_settings.get("num_req", 1)):
                    for api_key in nexa_keys:
                        try:
                            headers = {"X-API-Key": api_key}
                            res = requests.post(f"{NEXA_BASE_URL}/api/v1/numbers/get", json={"range": search_range, "format": "normal"}, headers=headers, timeout=10)
                            data = res.json()
                            if data.get("success") and data.get("number"):
                                num_str = str(data["number"]).replace("+", "")
                                number_id = data.get("number_id")
                                fetched_nums.append(num_str)
                                nexa_assigned_numbers[num_str] = chat_id 
                                nexa_found = True
                                global total_assigned_stats
                                total_assigned_stats += 1
                                if number_id:
                                    threading.Thread(target=poll_otp_with_status, args=(number_id, num_str, chat_id, api_key), daemon=True).start()
                                break
                        except: continue
                        
                if not nexa_found:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Number out of stock!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    
                    fetched_nums.append(num_str)
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        if num_str not in used_numbers_list:
                            used_numbers_list.append(num_str)
                save_db()
                
            if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("✅ Number Found!"))
            kb = []
            flags_db = bot_settings.get("premium_flags", {})
            for num in fetched_nums:
                _, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not num.startswith("+") else num
                
                emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: emoji_id = flag_data["id"]
                        break
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
                
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"c_n_s_{query}", "style": "danger"},
                       {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, render_body_text("╔═══════════════╗\n║ 💬 Waiting For SMS...\n╚═══════════════╝"), reply_markup={"inline_keyboard": kb})
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            else:
                msg_res = send_message(chat_id, render_body_text("╔═══════════════╗\n║ 💬 Waiting For SMS...\n╚═══════════════╝"), reply_markup={"inline_keyboard": kb})
                if msg_res and "result" in msg_res:
                    user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}
            return
            
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = float(text.strip())
                bal = temp_data[chat_id]["balance"]
                min_w = bot_settings['min_withdraw']
                
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Minimum withdrawal is {min_w} ₹!\n💰 Balance: {bal} ₹\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ You don't have enough balance!\n💰 Balance: {bal} ₹\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                    
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"📝 Enter your {temp_data[chat_id]['method']} number/UPI ID:"), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount! Please enter a valid number."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_2fa_key":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error: Message not found. Try again."))
                del user_states[chat_id]
                return

            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret)
                code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                
                success_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"《 🔐 <b>2FA CODE</b> 》\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                    f"━━━━━━━━━━━━━━━"
                )
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
            except:
                error_txt = "━━━━━━━━━━━━━━━\n《 ❌ <b>INVALID KEY</b> 》\n━━━━━━━━━━━━━━━\n⚠️ Invalid 2FA secret key! Please check and try again.\n━━━━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            
            method = temp_data[chat_id]["method"]
            amount = temp_data[chat_id]["amount"]
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            update_balance(chat_id, -amount)
            pending_withdrawals[req_id] = {"user_id": chat_id, "amount": amount, "method": method, "number": number, "full_name": full_name}
            
            _save_local_withdrawal(req_id, {"user_id": str(chat_id), "amount": amount, "method": method, "status": "pending"})
                
            admin_msg = f"🎙 <b>NEW WITHDRAWAL REQUEST</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={chat_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amount} INR\n🍏 <b>NUMBER:</b> <code>{number}</code>\n🏦 <b>METHOD:</b> {method}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
            wd_kb = {"inline_keyboard": [[{"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"}, {"text": "REJECT", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrej_{req_id}", "style": "danger"}]]}
            rendered_admin_msg = render_body_text(admin_msg)
            sent_messages = []
            if bot_settings.get("w_group"):
                try:
                    res = send_message(bot_settings["w_group"], rendered_admin_msg, reply_markup=wd_kb)
                    if res.get("ok") and res.get("result"):
                        sent_messages.append({"chat_id": bot_settings["w_group"], "message_id": res["result"]["message_id"]})
                    else:
                        for adm_id in bot_settings.get("admins", []):
                            try: send_message(adm_id, render_body_text(f"⚠️ W.GROUP ({bot_settings['w_group']}) mein message send fail hua! Group ID check karein."))
                            except: pass
                except: pass
            for adm_id in bot_settings.get("admins", []):
                if adm_id != chat_id:
                    try:
                        res = send_message(adm_id, rendered_admin_msg, reply_markup=wd_kb)
                        if res.get("ok") and res.get("result"):
                            sent_messages.append({"chat_id": adm_id, "message_id": res["result"]["message_id"]})
                    except: pass
            pending_withdrawals[req_id]["sent_messages"] = sent_messages
            
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            success_text = f"{PEM['ok']} Your withdrawal request has been submitted!\n\n🧾 <b>Req ID:</b> {req_id}\n💰 <b>Amount:</b> {amount} ₹\n🏦 <b>Method:</b> {method}\n📱 <b>Number:</b> <code>{number}</code>"
            
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return

    if text.startswith("/start"):
        get_user(chat_id)
        
        u_data = _get_local_user(chat_id)
        if u_data.get("referred_by") and not u_data.get("ref_paid"):
            inviter = u_data["referred_by"]
            _update_local_user(chat_id, {"ref_paid": True})
            reward = bot_settings.get("refer_reward", 0.2)
            update_balance(inviter, reward)
            _increment_local_user(inviter, "total_refers", 1)
            ref_msg = (
                f"{PEM['gift']} <b>New Referral !</b>\n"
                f"------------------\n"
                f"🔥 <b>You Received {reward} INR</b>\n"
                f"------------------\n"
                f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
            )
            send_message(inviter, render_body_text(ref_msg))

        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))
            
    elif text == "TRAFFIC":
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)
        
    elif text == "Refer":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        
        raw_txt = c_msg.get("text", f"{PEM['gift']} Refer").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", str(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "WITHDRAWAL":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} Withdrawals are currently disabled."))
            return
        
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get('total_otps', 0))).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{min_w}", str(bot_settings['min_withdraw']))
        txt = render_body_text(raw_txt)
        
        kb = []
        for m in bot_settings["w_methods"]:
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Admin Panel" and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text == "GET NUMBER":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        nexa_srvs = set(bot_settings.get("nexa_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        all_services = local_srvs.union(nexa_srvs).union(voltx_srvs)
        
        if not all_services:
            send_message(chat_id, render_body_text(f"{PEM['no']} No numbers or services available!"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            for s in all_services:
                emoji_id = "5352694861990501856"
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                kb.append([{"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"}])
            
            for b in c_msg.get("buttons", []): 
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Search Number":
        user_states[chat_id] = "wait_for_search"
        c_msg = bot_settings["custom_messages"].get("search_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['num']} Search Number"))
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif text == "SUPPORT":
        c_msg = bot_settings["custom_messages"].get("support", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['msg']} Support"))
        if not txt.strip(): txt = render_body_text(f"{PEM['msg']} Support")
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        sup_link = bot_settings.get("support_link", "")
        if sup_link:
            kb.insert(0, [{"text": "Contact Support", "icon_custom_emoji_id": "5337302974806922068", "url": sup_link, "style": "success"}])
            
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb} if kb else None)

def expire_previous_number(chat_id):
    if chat_id in user_active_sessions:
        prev_data = user_active_sessions[chat_id]
        prev_msg_id = prev_data["msg_id"]
        nums = prev_data["nums"]
        
        for num in nums:
            if num in nexa_assigned_numbers:
                del nexa_assigned_numbers[num]
        save_db()
        
        kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
        try:
            edit_message(chat_id, prev_msg_id, render_body_text("╔═══════════════╗\n║ 💬 Waiting For SMS...\n╚═══════════════╝"), reply_markup={"inline_keyboard": kb})
        except:
            pass
        del user_active_sessions[chat_id]

def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")

    if not data.startswith("test_p_conn_") and not data.startswith("c_n_") and not data.startswith("g_c_"):
        try: threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except: pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    msg_id = call["message"]["message_id"]

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned from using this bot!", show_alert=True)
            return

        if not check_force_join(chat_id) and data != "check_fj":
            send_force_join_msg(chat_id)
            return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Thanks for joining! You can now use the bot."), reply_markup=main_menu(chat_id))
            
            u_data = _get_local_user(chat_id)
            if u_data.get("referred_by") and not u_data.get("ref_paid"):
                inviter = u_data["referred_by"]
                _update_local_user(chat_id, {"ref_paid": True})
                reward = bot_settings.get("refer_reward", 0.2)
                update_balance(inviter, reward)
                _increment_local_user(inviter, "total_refers", 1)
                ref_msg = (
                    f"{PEM['gift']} <b>New Referral !</b>\n"
                    f"------------------\n"
                    f"🔥 <b>You Received {reward} INR</b>\n"
                    f"------------------\n"
                    f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                )
                send_message(inviter, render_body_text(ref_msg))
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels yet!", show_alert=True)
        return

    if data == "close_msg":
        delete_message(chat_id, msg_id)
        
    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        delete_message(chat_id, msg_id)

    elif data == "cancel_2fa":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "gen_2fa":
        user_states[chat_id] = "wait_for_2fa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            
            success_txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"《 🔐 <b>2FA CODE</b> 》\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                f"━━━━━━━━━━━━━━━"
            )
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except:
            answer_callback(call["id"], "❌ Error refreshing code!", show_alert=True)

    elif data == "cancel_abhi_edit":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>SAAD KING YT CONTROL PANEL</b>"), reply_markup=abhi_control_keyboard())
        
    elif data == "dummy_alert":
        answer_callback(call["id"], "This feature will be added later!", show_alert=True)
        
    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Traffic Refreshed!", show_alert=False)

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        
        country_stats = {}
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query):
                    iso = t.get("iso", "XX")
                    flag = t.get("flag", "🌍")
                    if iso not in country_stats:
                        country_stats[iso] = {"count": 0, "flag": flag}
                    country_stats[iso]["count"] += 1
        
        if not country_stats:
            answer_callback(call["id"], "❌ No recent traffic found for this service!", show_alert=True)
            return
            
        kb = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]
            c_name = iso
            emoji_id = "5780471598922337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    if "id" in fdata: emoji_id = fdata["id"]
                    break
            
            btn_text = f"{c_name} ({iso}) - {count} OTP"
            kb.append([{"text": btn_text, "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore Service: {prem_app_html} {app_full_name}</b>\n\nSelect a country to view available ranges:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]
        iso_query = parts[3]
        
        nums = []
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                    num = t.get("number", "").replace("+", "").strip()
                    if num: nums.append(num)
        
        if not nums:
            answer_callback(call["id"], "❌ No recent numbers found for this country!", show_alert=True)
            return
            
        known_ranges = set()
        for s_name, c_dict in bot_settings.get("nexa_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list:
                    known_ranges.add(r)
                    
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r):
                    r_counts[r] += 1
                    matched = True
                    break
            if not matched:
                if len(num) >= 7:
                    r_counts[num[:7]] += 1
                else:
                    r_counts[num] += 1
                    
        r_list = r_counts.most_common(12)
        
        kb = []
        for r, count in r_list:
            kb.append([{"text": f"{r} ({count})", "icon_custom_emoji_id": "5352862640592949843", "copy_text": {"text": r}, "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges for {prem_app_html} {app_full_name} - {prem_flag_html} {iso_query}</b>\n\nClick on any range to copy it."), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())

    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Manage Balance:"), reply_markup=get_cancel_kb())
        
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Ban or Unban:"), reply_markup=get_cancel_kb())

    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to View Profile:"), reply_markup=get_cancel_kb())

    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Menu Design Editor</b>\n\nSelect a menu block to edit its Body Text and Inline Buttons. You can use Premium Emojis too!"), reply_markup=menu_design_list_keyboard())

    elif data == "md_reset_defaults":
        bot_settings["custom_messages"] = DEFAULT_CUSTOM_MESSAGES.copy()
        save_db()
        answer_callback(call["id"], "✅ Resetted to Premium Defaults!", show_alert=True)

    elif data.startswith("md_edit_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_edit_", "")
        cm_text = render_body_text(bot_settings["custom_messages"].get(key, {}).get("text", "..."))
        try:
            edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Editing: {key.upper()}</b>\n\nPreview of current Text:\n{cm_text}"), reply_markup=menu_edit_options_keyboard(key))
        except: pass

    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        user_states[chat_id] = "wait_for_menu_text"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Edit Body: {key.upper()}</b>\n\nSend the new text. You can use Premium Emojis directly here.\n(Use standard HTML like <b>bold</b>, <i>italic</i> for formatting)"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})

    elif data.startswith("md_btns_"):
        answer_callback(call["id"]) 
        if chat_id in user_states: del user_states[chat_id] 
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_btns_", "")
        try:
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except: pass

    elif data.startswith("md_addbtn_"):
        key = data.replace("md_addbtn_", "")
        user_states[chat_id] = "wait_for_menu_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"➕ <b>Add Button: {key.upper()}</b>\n\nSend custom button in this format:\n<code>Button Text - https://link.com</code>\n\n<i>(Only normal Emojis supported here!)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_btns_{key}", "style": "danger"}]]})

    elif data.startswith("md_delbtn_"):
        parts = data.split("_")
        key = parts[2]
        b_idx = int(parts[3])
        if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
            del bot_settings["custom_messages"][key]["buttons"][b_idx]
            save_db()
            answer_callback(call["id"], "✅ Button Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        
        if bal < min_w:
            answer_callback(call["id"], f"❌ Insufficient balance! Minimum {min_w} ₹ required.", show_alert=True)
            return
            
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Method: {method}\n💰 Available Balance: {bal} ₹\n\n📝 Enter the amount you want to withdraw (Min: {min_w} ₹):"), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send the Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>\n\nUpload your TXT files or manually add them below:"), reply_markup=emoji_settings_keyboard())

    elif data == "up_flags_txt":
        user_states[chat_id] = "wait_for_flag_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Flag Emojis</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "up_apps_txt":
        user_states[chat_id] = "wait_for_app_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Service Apps</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "add_single_emoji":
        user_states[chat_id] = "wait_for_emoji_extract"
        edit_message(chat_id, msg_id, render_body_text("📝 Send any Premium Emoji (e.g.: 🇧🇩 or 🚫):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "dl_flags_txt":
        content = generate_emoji_txt("flags")
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No Flag Emojis found!", show_alert=True)

    elif data == "dl_apps_txt":
        content = generate_emoji_txt("apps")
        if content:
            send_document(chat_id, "Service_Apps.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No App Emojis found!", show_alert=True)

    elif data == "del_all_flags":
        bot_settings["premium_flags"] = {}
        save_db()
        answer_callback(call["id"], "✅ All Premium Flags Deleted Successfully!", show_alert=True)

    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message you want to broadcast (Text, Photo, Video, File etc)."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the numbers in a <b>.txt</b> file."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "delete_files":
        kb = []
        for b_id, b_data in number_batches.items():
            kb.append([{"text": f"{b_data['filename']} ({len(b_data['numbers'])})", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a file to delete:" if len(kb) > 1 else f"{PEM['no']} No files found."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            del number_batches[b_id]
            save_db()
            answer_callback(call["id"], "✅ File deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_used":
        all_nums = set()
        for b in number_batches.values():
            for n in b["numbers"]:
                all_nums.add(n["num"].replace("+", "").strip())
        for n in used_numbers_list:
            all_nums.add(n.replace("+", "").strip())
        otp_used = [n for n in all_nums if n in otp_received_numbers]
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Used Numbers (OTP Received):</b> {len(otp_used)}"), reply_markup=kb)

    elif data == "show_unused":
        all_nums = set()
        for b in number_batches.values():
            for n in b["numbers"]:
                all_nums.add(n["num"].replace("+", "").strip())
        for n in used_numbers_list:
            all_nums.add(n.replace("+", "").strip())
        otp_unused = [n for n in all_nums if n not in otp_received_numbers]
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Unused Numbers (No OTP):</b> {len(otp_unused)}"), reply_markup=kb)

    elif data == "dl_used":
        all_nums = set()
        for b in number_batches.values():
            for n in b["numbers"]:
                all_nums.add(n["num"].replace("+", "").strip())
        for n in used_numbers_list:
            all_nums.add(n.replace("+", "").strip())
        otp_used = [n for n in all_nums if n in otp_received_numbers]
        if not otp_used:
            answer_callback(call["id"], "No OTP received numbers found!", show_alert=True)
            return
        content = "\n".join(otp_used).encode('utf-8')
        send_document(chat_id, "used_otp_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "dl_unused":
        all_nums = set()
        for b in number_batches.values():
            for n in b["numbers"]:
                all_nums.add(n["num"].replace("+", "").strip())
        for n in used_numbers_list:
            all_nums.add(n.replace("+", "").strip())
        otp_unused = [n for n in all_nums if n not in otp_received_numbers]
        if not otp_unused:
            answer_callback(call["id"], "All numbers have received OTP!", show_alert=True)
            return
        content = "\n".join(otp_unused).encode('utf-8')
        send_document(chat_id, "unused_no_otp_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit_n, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                res_txt = ""
                count = 1
                if not res_txt:
                    sorted_users = sorted(local_users_db.items(), key=lambda x: x[1].get(field, 0), reverse=True)[:limit_n]
                    for uid, d in sorted_users:
                        if d.get(field, 0) > 0:
                            p = "└" if count == limit_n else "├"
                            res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get(field,0)}</b>\n"
                            count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit_n, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                res_txt = ""
                count = 1
                if not res_txt:
                    sorted_users = sorted(local_users_db.items(), key=lambda x: x[1].get(field, 0), reverse=True)[:limit_n]
                    for uid, d in sorted_users:
                        if d.get(field, 0) > 0:
                            p = "└" if count == limit_n else "├"
                            res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get(field,0)}</b>\n"
                            count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit_n, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                res_txt = ""
                count = 1
                if not res_txt:
                    sorted_ws = sorted(local_withdrawals_db.items(), key=lambda x: x[1].get("timestamp", 0), reverse=True)[:limit_n]
                    for wid, d in sorted_ws:
                        s = str(d.get('status','Pending')).lower()
                        stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                        uid = d.get('user_id','User')
                        p = "└" if count == limit_n else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}₹</b> {stat_icon}\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        
    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>\nManage advanced bot configurations below:"), reply_markup=system_settings_keyboard())

    elif data == "manage_vx_srv":
        if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
        vx_srvs = bot_settings["voltx_services"]
        kb = []
        for srv_name in vx_srvs:
            cnt_count = len(vx_srvs[srv_name])
            kb.append([{"text": f"📦 {srv_name} ({cnt_count} countries)", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"vx_srv_{srv_name}", "style": "primary"}])
        kb.append([{"text": "➕ Add Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text(f"📦 <b>VoltX Services Manager</b>\nManage your VoltX API-based services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "vx_add_srv":
        user_states[chat_id] = "wait_vx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the <b>Service Name</b>:\n<i>Example: WhatsApp</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_vx_srv", "style": "danger"}]]})

    elif data.startswith("vx_srv_"):
        srv = data[7:]
        if srv not in bot_settings.get("voltx_services", {}):
            answer_callback(call["id"], "❌ Service not found!", show_alert=True)
            return
        vx_cnt = bot_settings["voltx_services"].get(srv, {})
        kb = []
        for cnt_name, ranges in vx_cnt.items():
            kb.append([{"text": f"🏳️ {cnt_name} ({len(ranges)} ranges)", "icon_custom_emoji_id": "5780471598922337683", "callback_data": f"vx_cnt_{srv}_{cnt_name}", "style": "primary"}])
        kb.append([{"text": "➕ Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "🗑 Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_vx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"🌍 <b>{srv} Countries</b>\nManage countries for this VoltX service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_add_cnt_"):
        srv = data[11:]
        user_states[chat_id] = "wait_vx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the <b>Country Name</b> for <b>{srv}</b>:\n<i>Example: India</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "danger"}]]})

    elif data.startswith("vx_cnt_"):
        rest = data[7:]
        parts = rest.split("_", 1)
        if len(parts) < 2:
            return
        srv, cnt = parts[0], parts[1]
        ranges = bot_settings.get("voltx_services", {}).get(srv, {}).get(cnt, [])
        ranges_text = "\n".join([f"• <code>{r}</code>" for r in ranges]) if ranges else "<i>No ranges yet</i>"
        kb = []
        for r in ranges:
            kb.append([{"text": f"❌ {r}", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"}])
        kb.append([{"text": "➕ Add Range/Prefix", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_rng_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "🗑 Delete Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📱 <b>{srv} → {cnt}</b>\n\n{ranges_text}"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_add_rng_"):
        rest = data[11:]
        parts = rest.split("_", 1)
        if len(parts) < 2:
            return
        srv, cnt = parts[0], parts[1]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the <b>Number Prefix/Range</b> for <b>{cnt}</b>:\n<i>Example: 88017, 91981XXX</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("vx_dr_"):
        rest = data[6:]
        parts = rest.split("_", 2)
        if len(parts) < 3:
            return
        srv, cnt, rng = parts[0], parts[1], parts[2]
        if srv in bot_settings.get("voltx_services", {}) and cnt in bot_settings["voltx_services"][srv]:
            if rng in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].remove(rng)
                save_db()
        answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": call["message"], "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})

    elif data.startswith("vx_del_srv_"):
        srv = data[11:]
        if srv in bot_settings.get("voltx_services", {}):
            del bot_settings["voltx_services"][srv]
            save_db()
        answer_callback(call["id"], f"✅ Service {srv} deleted!", show_alert=True)
        handle_callback({"message": call["message"], "data": "manage_vx_srv", "id": "internal"})

    elif data.startswith("vx_del_cnt_"):
        rest = data[11:]
        parts = rest.split("_", 1)
        if len(parts) < 2:
            return
        srv, cnt = parts[0], parts[1]
        if srv in bot_settings.get("voltx_services", {}) and cnt in bot_settings["voltx_services"][srv]:
            del bot_settings["voltx_services"][srv][cnt]
            save_db()
        answer_callback(call["id"], f"✅ Country {cnt} deleted!", show_alert=True)
        handle_callback({"message": call["message"], "data": f"vx_srv_{srv}", "id": "internal"})

    elif data.startswith("manage_vx_srv_"):
        idx = int(data.split("_")[3])
        handle_callback({"message": call["message"], "data": "manage_vx_srv", "id": call["id"]})

    elif data == "nexa_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>Nexa Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('nexa_keys', []))}\nManage your Nexa API Keys below:"), reply_markup=nexa_control_keyboard())

    elif data == "add_nexa_key":
        user_states[chat_id] = "wait_for_add_nexa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Nexa API Key (e.g. nxa_...):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "nexa_control", "style": "danger"}]]})

    elif data == "view_nexa_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("nexa_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_nxa_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "nexa_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Nexa Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_nxa_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("nexa_keys", [])):
            del bot_settings["nexa_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Nexa Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_nexa_keys", "id": call["id"]})

    elif data == "nexa_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_sc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "nexa_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_search_country":
        user_states[chat_id] = "wait_for_add_sc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Country Code (e.g. 880 or 92):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "nexa_search_country", "style": "danger"}]]})

    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("search_countries", [])):
            del bot_settings["search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Country Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "nexa_search_country", "id": call["id"]})

    elif data == "manage_nexa_srv":
        kb = []
        srvs = bot_settings.get("nexa_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "nx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "nexa_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📦 <b>Nexa Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "nx_add_srv":
        user_states[chat_id] = "wait_nx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_srv_"):
        srv = data.replace("nx_srv_", "")
        kb = []
        countries = bot_settings["nexa_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_nexa_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_add_cnt_"):
        srv = data.replace("nx_add_cnt_", "")
        user_states[chat_id] = "wait_nx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["nexa_services"][srv].get(cnt, [])
        
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"nx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_nx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 88017):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("nx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["nexa_services"].get(srv, {}).get(cnt, []):
            bot_settings["nexa_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("nx_del_srv_"):
        srv = data.replace("nx_del_srv_", "")
        if srv in bot_settings["nexa_services"]: del bot_settings["nexa_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_nexa_srv", "id": call["id"]})

    elif data.startswith("nx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["nexa_services"].get(srv, {}): del bot_settings["nexa_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_srv_{srv}", "id": call["id"]})

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels/groups below:"), reply_markup=fj_settings_keyboard())

    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels/groups below:"), reply_markup=fj_settings_keyboard())

    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Channel ya Group Add Karein</b>\n\n✅ Bot pehle se channel/group mein admin hona chahiye!\n\nBhejein koi bhi ek:\n• Username: <code>@channelname</code>\n• Public Link: <code>https://t.me/channelname</code>\n• Numeric ID: <code>-1001234567890</code>\n\n🔄 Bot auto-detect karega Channel/Group aur Private/Public!"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})

    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            removed = bot_settings["fj_channels"][idx]
            info = _get_fj_info(removed)
            del bot_settings["fj_channels"][idx]
            save_db()
            answer_callback(call["id"], f"✅ {info.get('title', 'Item')} deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels/groups below:"), reply_markup=fj_settings_keyboard())

    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "add_adm":
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID of the new Admin:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})

    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]
            save_db()
            answer_callback(call["id"], "✅ Admin deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Group ID/Username to forward messages to:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_id}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Custom Inline Button format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})

    elif data.startswith("del_fwbtn_"):
        parts = data.split("_")
        idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                save_db()
                answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]
            save_db()
            answer_callback(call["id"], "✅ Group deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        api_count = len([p for p in bot_settings["panels"] if p.get("type") == "API Panel"])
        cpt_count = len([p for p in bot_settings["panels"] if p.get("type", "API Panel") == "Auto Captcha Panel"])
        voltx_count = len([p for p in bot_settings["panels"] if p.get("type") == "VoltX Panel"])
        text = f"{PEM['gear']} <b>Panel Management</b>\n\nSelect which type of panel system you want to manage:"
        kb = {"inline_keyboard": [
            [{"text": f"Manage API Panels ({api_count})", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "manage_api_panels", "style": "primary"}],
            [{"text": f"Manage VoltX Panels ({voltx_count})", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "manage_voltx_panels", "style": "success"}],
            [{"text": f"Manage Auto Captcha Panels ({cpt_count})", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "manage_cpt_panels", "style": "success"}],
            [{"text": "Back to System", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=kb)

    elif data in ["manage_api_panels", "manage_cpt_panels", "manage_voltx_panels"]:
        if data == "manage_api_panels": p_type = "API Panel"
        elif data == "manage_voltx_panels": p_type = "VoltX Panel"
        else: p_type = "Auto Captcha Panel"
        p_list = [p for p in bot_settings["panels"] if p.get("type", "API Panel") == p_type]
        if p_type == "API Panel": icon = f"{PEM['world']} API"
        elif p_type == "VoltX Panel": icon = "🌐 VoltX"
        else: icon = f"{PEM['lock']} Auto Captcha"
        
        text = f"{icon} <b>{p_type}s Management</b>\n\n👀 <b>Active Monitors:</b> {len(p_list)}\n\n🟢 <b>Available Providers:</b>\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                conf = f" {login_state}" if login_state else f"{PEM['ok']} Configured"
            elif p['type'] == 'VoltX Panel':
                conf = f"{PEM['ok']} Configured" if p.get('base_url') else f"{PEM['no']} Not Configured"
            else:
                conf = f"{PEM['ok']} Configured" if p.get('api_url') else f"{PEM['no']} Not Configured"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))

    elif data in ["add_api_panel", "add_cpt_panel", "add_voltx_panel"]:
        user_states[chat_id] = "wait_for_panel_name"
        if data == "add_api_panel": p_type = "api"
        elif data == "add_voltx_panel": p_type = "voltx"
        else: p_type = "logc"
        temp_data[chat_id] = {"msg_id": msg_id, "add_type": p_type}
        back_cb = "manage_api_panels" if p_type == "api" else ("manage_voltx_panels" if p_type == "voltx" else "manage_cpt_panels")
        edit_message(chat_id, msg_id, render_body_text("📝 Please send the name of the New Provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_cb, "style": "danger"}]]})

    elif data.startswith("add_ptype_"):
        pass

    elif data in ["list_del_api", "list_del_cpt", "list_del_voltx"]:
        if data == "list_del_api": p_type = "API Panel"
        elif data == "list_del_voltx": p_type = "VoltX Panel"
        else: p_type = "Auto Captcha Panel"
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            if p.get("type", "API Panel") == p_type:
                kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        if p_type == "API Panel": back_to = "manage_api_panels"
        elif p_type == "VoltX Panel": back_to = "manage_voltx_panels"
        else: back_to = "manage_cpt_panels"
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_to, "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Select a Provider to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(bot_settings["panels"]):
            p_type = bot_settings["panels"][idx].get("type", "API Panel")
            del bot_settings["panels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Provider Deleted!", show_alert=True)
            if p_type == "Auto Captcha Panel": back_mgr = "manage_cpt_panels"
            elif p_type == "VoltX Panel": back_mgr = "manage_voltx_panels"
            else: back_mgr = "manage_api_panels"
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": back_mgr, "id": "internal"})

    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            
            new_status = "ON" if p["status"] == "OFF" else "OFF"
            p["status"] = new_status
            if new_status == "ON":
                p["needs_warmup"] = True
            save_db()
            
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>"
            elif p["type"] == "VoltX Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Base URL:</b> <code>{p.get('base_url', 'None')}</code>\n<b>API Key:</b> <code>{p.get('api_key', 'None')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>\n<b>Num Col:</b> {p.get('num_col_name')} (Idx: {p.get('num_col_idx')})\n<b>Msg Col:</b> {p.get('msg_col_name')} (Idx: {p.get('msg_col_idx')})"
            elif p["type"] == "VoltX Panel":
                api_key_masked = (p.get('api_key', '')[:4] + "****" + p.get('api_key', '')[-4:]) if len(p.get('api_key', '')) > 8 else p.get('api_key', 'None')
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Base URL:</b> <code>{p.get('base_url', 'None')}</code>\n<b>API Key:</b> <code>{api_key_masked}</code>\n<b>GetNum URL:</b> <code>{p.get('getnum_url', 'Auto')}</code>\n<b>GetMsg URL:</b> <code>{p.get('getmsg_url', 'Auto')}</code>\n<b>Traffic URL:</b> <code>{p.get('traffic_url', 'Auto')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("set_p_api_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_api"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the API URL for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_tok_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_tok"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Token for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_fapi_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_fapi"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the FULL API URL (Example: http://api.com/get?key=YOUR_TOKEN&start=0):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_rec_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_rec"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the number of records to fetch (e.g. 10).\nType <code>0</code> for Unlimited:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_vbase_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_voltx_base_url"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("🌐 <b>VoltX Base URL</b>\n\nSend the Base API URL:\n<i>Example: https://api.2oo9.cloud/XXX/tnevs/@public/api</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_vkey_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_voltx_api_key"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("🔑 <b>VoltX API Key</b>\n\nSend your API Key / Token:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_vgetnum_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_voltx_getnum_url"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📥 <b>VoltX GetNum URL</b>\n\nSend GetNum URL (or leave blank to use auto):\n<i>Default: {base_url}/getnum</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_vgetmsg_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_voltx_getmsg_url"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📨 <b>VoltX GetMsg URL</b>\n\nSend GetMsg URL (or leave blank to use auto):\n<i>Default: {base_url}/success-otp</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_vtraf_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_voltx_traffic_url"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📊 <b>VoltX Traffic URL</b>\n\nSend Traffic URL (or leave blank to use auto):\n<i>Default: {base_url}/console</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection. Please wait..."))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])
        
        try:
            parsed = []
            raw_text = ""
            
            if p["type"] == "VoltX Panel":
                base_url = p.get("base_url", "").strip()
                api_key = p.get("api_key", "").strip()
                if not base_url or not api_key:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Please set Base URL and API Key first!"))
                    return
                getmsg_url = p.get("getmsg_url", "").strip() or f"{base_url.rstrip('/')}/success-otp"
                headers_vx = {"Content-Type": "application/json", "mauthapi": api_key}
                try:
                    res_vx = requests.get(getmsg_url, headers=headers_vx, timeout=15)
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    if res_vx.status_code == 200:
                        d = res_vx.json()
                        otps = d.get("data", {}).get("otps", [])
                        if isinstance(otps, list) and otps:
                            sample = otps[0]
                            txt = f"✅ <b>VoltX Connection OK!</b>\n\n🔢 OTPs in queue: <b>{len(otps)}</b>\n\n<b>Sample Entry:</b>\n📱 Number: <code>{sample.get('number','?')}</code>\n📝 Message: <code>{html.escape(str(sample.get('message','')))[:200]}</code>\n🔐 OTP: <code>{extract_otp_code(str(sample.get('message','')))}</code>"
                            send_message(chat_id, render_body_text(txt))
                        else:
                            send_message(chat_id, render_body_text(f"✅ <b>VoltX Connected!</b> No OTPs in queue yet.\n\n<code>{html.escape(str(res_vx.text)[:300])}</code>"))
                    else:
                        send_message(chat_id, render_body_text(f"❌ <b>VoltX Connection Failed!</b>\nHTTP {res_vx.status_code}\n<code>{html.escape(str(res_vx.text)[:300])}</code>"))
                except Exception as e:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text(f"❌ <b>VoltX Error:</b> {html.escape(str(e))}"))
                return

            elif p["type"] == "Auto Captcha Panel":
                sess = panel_sessions.get(idx)
                login_url = p.get("login_url", "").strip()
                if not login_url.startswith("http"): login_url = "http://" + login_url
                msg_link = p.get("msg_link", "").strip()
                if not msg_link.startswith("http") and msg_link != "": msg_link = "http://" + msg_link
                check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"

                for attempt in range(2):
                    if not sess:
                        success = attempt_auto_login(p, idx)
                        save_db()
                        if not success:
                            if wait_msg_id: delete_message(chat_id, wait_msg_id)
                            send_message(chat_id, render_body_text(f"❌ <b>Auto Login Failed!</b>\nReason: {html.escape(str(p.get('login_status', 'Unknown')))}"))
                            return
                        sess = panel_sessions.get(idx)
                    try:
                        parsed, raw_text = fetch_cpt_panel_cdrs(p, sess, check_url)
                        break
                    except Exception as sess_err:
                        if "Session expired" in str(sess_err) and attempt == 0:
                            if idx in panel_sessions: del panel_sessions[idx]
                            sess = None
                            continue
                        raise

            else:
                full_url = p.get("full_api_url", "").strip()
                url = p.get("api_url", "").strip()
                token = p.get("token", "").strip()
                if not full_url and not url:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Please Set API URL or Full API URL first!"))
                    return
                
                urls_to_try = []
                try:
                    if full_url:
                        urls_to_try.append(full_url)
                    else:
                        if "thirdwave" in url.lower() or "thirdwave.im" in url.lower() or "app.thirdwave.im" in url:
                            base_url = url.split('/api/')[0] if '/api/' in url else url
                            base_url = base_url.rstrip('/')
                            urls_to_try = [
                                f"{base_url}/api/v1/traffic?token={token}",
                                f"{base_url}/api/v1/traffic?key={token}",
                                f"{base_url}/api/v1/traffic?api_key={token}",
                                f"{base_url}/api/v1/traffic?type=sms&token={token}",
                                f"{base_url}/api/v1/traffic?type=otp&token={token}",
                                f"{base_url}/api/v1/numbers?token={token}",
                            ]
                            print(f"🔍 Thirdwave: Trying /traffic endpoint")
                        else:
                            if "{token}" in url or "{key}" in url:
                                urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                            elif "token=" in url or "key=" in url:
                                urls_to_try.append(url)
                            else:
                                sep = '&' if '?' in url else '?'
                                urls_to_try.append(f"{url}{sep}token={token}")
                                urls_to_try.append(f"{url}{sep}key={token}&start=0")
                                urls_to_try.append(f"{url}{sep}key={token}")
                except Exception as e:
                    print(f"Error building URLs: {e}")
                    urls_to_try = []
                    
                parsed = []
                raw_text = ""
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'application/json',
                    }
                    
                    zenex_target = full_url or url
                    
                    if "thirdwave" in zenex_target.lower() or "thirdwave" in str(urls_to_try).lower() or "app.thirdwave.im" in zenex_target:
                        if token:
                            headers['Authorization'] = f'Bearer {token}'
                            headers['X-API-Key'] = token
                            print(f"🔑 Thirdwave: Testing with Bearer token + X-API-Key")
                    
                    if "zenexnetwork.com" in zenex_target:
                        zenex_key = token
                        if not zenex_key:
                            try:
                                zenex_key = parse_qs(urlparse(zenex_target).query).get('key', [''])[0]
                            except Exception:
                                zenex_key = ""
                        if zenex_key:
                            headers['mapikey'] = zenex_key
                    
                    for try_url in urls_to_try:
                        try:
                            print(f"🔄 Testing: {try_url}")
                            res = requests.get(try_url, headers=headers, timeout=10)
                            raw_text = res.text
                            content_type = res.headers.get('content-type', '')
                            
                            if res.status_code == 200 and (content_type.startswith('application/json') or raw_text.strip().startswith('{')):
                                parsed = parse_panel_response(raw_text, p)
                                if parsed:
                                    if not full_url and try_url != url and token:
                                        p["api_url"] = try_url.replace(token, "{token}")
                                        save_db()
                                    break
                            else:
                                print(f"⚠️ Status {res.status_code}, Content-Type: {content_type}")
                        except Exception as e:
                            print(f"❌ URL error: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error fetching API data: {e}")
                 
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
                 
            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n🎯 <b>Parsed Data Sample (Max 3):</b>\n\n"
                
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']
                    msg = sample['message']
                    otp = sample['otp']
                    
                    detected_app = detect_service(msg)
                    app_name = detected_app if detected_app else p.get("name", "Unknown")
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg)
                    
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 Number: <code>{num}</code>\n"
                    txt += f"📝 Full Msg: <code>{html.escape(msg)}</code>\n"
                    txt += f"🔐 OTP: <code>{otp}</code>\n"
                    txt += "➖" * 12 + "\n"
                    
                send_message(chat_id, render_body_text(txt))
            else:
                if p["type"] == "Auto Captcha Panel":
                    try:
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            full_table_data = "🔍 FULL TABLE DATA (A-Z)\n" + "="*50 + "\n\n"
                            for t_idx, table in enumerate(tables):
                                full_table_data += f"--- Table {t_idx+1} ---\n"
                                rows = table.find_all('tr')
                                for r_idx, row in enumerate(rows):
                                    cols = row.find_all(['th', 'td'])
                                    col_texts = [f"[{c_idx+1}] {c.get_text(separator=' ', strip=True)}" for c_idx, c in enumerate(cols)]
                                    full_table_data += f"Row {r_idx+1}: {' | '.join(col_texts)}\n"
                                full_table_data += "\n" + "="*50 + "\n"
                            
                            send_document(chat_id, f"Full_Panel_Data_{idx}.txt", full_table_data.encode('utf-8'))
                            fail_txt = f"⚠️ <b>Connected, but couldn't parse OTP data!</b>\n\n<i>I have sent the complete (A-Z) data of that link in a Text File. Open the file and check the correct Column Number (e.g.: [1], [3]) then update in panel.</i>"
                            send_message(chat_id, render_body_text(fail_txt))
                        else:
                            send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but no HTML Table found!</b>\nMake sure the message link is correct."))
                    except Exception as e:
                        send_message(chat_id, render_body_text(f"❌ <b>Error parsing HTML:</b> {html.escape(str(e))}"))
                else:
                    safe_html = html.escape(str(raw_text)[:300])
                    send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but couldn't find/parse OTP data.</b>\n\n<i>Make sure your API config is correct.</i>\n\nRaw HTML/Data (excerpt):\n<code>{safe_html}...</code>"))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Connection Failed!</b>\nError: {html.escape(str(e))}"))

    elif data == "abhi_control":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>SAAD KING YT CONTROL PANEL</b>"), reply_markup=abhi_control_keyboard())

    elif data == "abhi_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>SAAD KING YT CONTROL PANEL</b>"), reply_markup=abhi_control_keyboard())

    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the name of the new Withdrawal Method:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})

    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]
            save_db()
            answer_callback(call["id"], "✅ Method deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data.startswith("abhi_"):
        key = data.replace("abhi_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link", "w_group": "w_group"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_abhi"
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_abhi_edit", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"📝 Please send the new value for <code>{key_map[key]}</code>:"), reply_markup=cancel_kb)
            answer_callback(call["id"])

    elif data.startswith("g_s_"):
        service = data.split("g_s_")[1]
        local_cnts = set([b["country"] for b in number_batches.values() if b["service"] == service and b["numbers"]])
        nexa_cnts = set(bot_settings.get("nexa_services", {}).get(service, {}).keys())
        voltx_cnts = set(bot_settings.get("voltx_services", {}).get(service, {}).keys())
        all_countries = local_cnts.union(nexa_cnts).union(voltx_cnts)
        
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        raw_txt = c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service)
        txt = render_body_text(raw_txt)
        
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in all_countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_c_{service}_{c}", "style": "success"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "close_msg", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_c_") or data.startswith("c_n_"):
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
            return
        
        user_cooldowns[chat_id] = now
        expire_previous_number(chat_id)

        if data.startswith("c_n_s_"):
            parts_s = data.split("_")
            query = parts_s[3]
            service_from_cb = parts_s[4] if len(parts_s) > 4 else None
            
            allowed_countries = bot_settings.get("search_countries", [])
            if allowed_countries and not any(query.startswith(c) for c in allowed_countries):
                answer_callback(call["id"], "❌ This country code is not allowed for search!", show_alert=True)
                return
                
            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = msg_id
            
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))

            if not found_indices:
                has_matching = False
                for b_id, b_data in number_batches.items():
                    for n_obj in b_data["numbers"]:
                        if n_obj["num"].replace("+", "").startswith(query):
                            has_matching = True
                            n_obj["shares"] = 0
                            n_obj["used_by"] = []
                if has_matching:
                    for b_id, b_data in number_batches.items():
                        for idx, n_obj in enumerate(b_data["numbers"]):
                            if n_obj["num"].replace("+", "").startswith(query):
                                found_indices.append((b_id, idx))

            fetched_nums = []
            if not found_indices:
                nexa_found = False
                nexa_keys = bot_settings.get("nexa_keys", [])
                search_range = query + ("X" * (11 - len(query))) if len(query) < 11 else query
                
                for _ in range(bot_settings.get("num_req", 1)):
                    for api_key in nexa_keys:
                        try:
                            headers = {"X-API-Key": api_key}
                            res = requests.post(f"{NEXA_BASE_URL}/api/v1/numbers/get", json={"range": search_range, "format": "normal"}, headers=headers, timeout=10)
                            data = res.json()
                            if data.get("success") and data.get("number"):
                                num_str = str(data["number"]).replace("+", "")
                                number_id = data.get("number_id")
                                fetched_nums.append(num_str)
                                nexa_assigned_numbers[num_str] = chat_id 
                                nexa_found = True
                                total_assigned_stats += 1
                                if number_id:
                                    threading.Thread(target=poll_otp_with_status, args=(number_id, num_str, chat_id, api_key), daemon=True).start()
                                break
                        except: continue
                        
                if not nexa_found:
                    answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
                    delete_message(chat_id, wait_msg_id)
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    fetched_nums.append(num_str)
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        if num_str not in used_numbers_list:
                            used_numbers_list.append(num_str)
                save_db()
                
            kb = []
            if service_from_cb:
                app_full_name, _ = get_service_info_html(service_from_cb)
                emoji_id_srv = "5337302974806922068"
                for app_key, app_data in bot_settings.get("premium_apps", {}).items():
                    if service_from_cb.upper() == app_key or service_from_cb.upper() in app_key or app_key in service_from_cb.upper():
                        if "id" in app_data: emoji_id_srv = app_data["id"]; break
                kb.append([{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id_srv, "callback_data": "ignore", "style": "success"}])

            flags_db = bot_settings.get("premium_flags", {})
            for num in fetched_nums:
                _, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: emoji_id = flag_data["id"]; break
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"c_n_s_{query}", "style": "danger"},
                       {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            edit_message(chat_id, wait_msg_id, render_body_text("╔═══════════════╗\n║ 💬 Waiting For SMS...\n╚═══════════════╝"), reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            return

        parts = data.split("_")
        service = parts[2]
        country = parts[3]

        available_indices = []
        for b_id, b_data in number_batches.items():
            if b_data["service"] == service and b_data["country"] == country:
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if chat_id not in n_obj.get("used_by", []):
                        available_indices.append((b_id, idx))

        if not available_indices:
            has_matching = False
            for b_id, b_data in number_batches.items():
                if b_data["service"] == service and b_data["country"] == country:
                    for n_obj in b_data["numbers"]:
                        has_matching = True
                        n_obj["shares"] = 0
                        n_obj["used_by"] = []
            if has_matching:
                for b_id, b_data in number_batches.items():
                    if b_data["service"] == service and b_data["country"] == country:
                        for idx, n_obj in enumerate(b_data["numbers"]):
                            available_indices.append((b_id, idx))

        if not available_indices:
            nexa_srv_data = bot_settings.get("nexa_services", {}).get(service, {}).get(country)
            if nexa_srv_data and len(nexa_srv_data) > 0:
                random_range = random.choice(nexa_srv_data)
                user_cooldowns[chat_id] = 0
                handle_callback({"message": call["message"], "data": f"c_n_s_{random_range}_{service}", "id": call["id"]})
                return

            voltx_srv_data = bot_settings.get("voltx_services", {}).get(service, {}).get(country)
            if voltx_srv_data and len(voltx_srv_data) > 0:
                random_prefix = random.choice(voltx_srv_data)
                vx_panel = next((p for p in bot_settings["panels"] if p.get("type") == "VoltX Panel" and p.get("status") == "ON" and p.get("base_url") and p.get("api_key")), None)
                if not vx_panel:
                    answer_callback(call["id"], "❌ No active VoltX Panel found! Please configure & turn ON a VoltX Panel from Admin Panel.", show_alert=True)
                    if data.startswith("c_n_"): delete_message(chat_id, msg_id)
                    return
                if vx_panel:
                    edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Getting Number...</i>"))
                    got_number = False
                    try:
                        base_url = vx_panel.get("base_url", "").rstrip("/")
                        api_key = vx_panel.get("api_key", "")
                        getnum_url = vx_panel.get("getnum_url", "").strip() or f"{base_url}/getnum"
                        headers_vx = {"Content-Type": "application/json", "mauthapi": api_key}
                        rid = str(random_prefix).replace("X", "").replace("*", "").strip()
                        res_vx = requests.post(getnum_url, json={"rid": rid}, headers=headers_vx, timeout=20)
                        if res_vx.status_code == 200:
                            vx_data = res_vx.json()
                            if vx_data.get("meta", {}).get("code") == 200 and vx_data.get("data"):
                                num_data = vx_data["data"]
                                raw_num = num_data.get("full_number") or num_data.get("no_plus_number") or ""
                                if raw_num:
                                    got_number = True
                                    num_str = str(raw_num).replace("+", "").strip()
                                    voltx_assigned_numbers[num_str] = chat_id
                                    total_assigned_stats += 1
                                    save_db()

                                    app_full_name, _ = get_service_info_html(service)
                                    emoji_id_srv = "5337302974806922068"
                                    for app_key_s, app_data_s in bot_settings.get("premium_apps", {}).items():
                                        if service.upper() == app_key_s or service.upper() in app_key_s or app_key_s in service.upper():
                                            if "id" in app_data_s: emoji_id_srv = app_data_s["id"]; break
                                    display_num = f"+{num_str}" if not num_str.startswith("+") else num_str
                                    _, iso = get_flag_and_code(num_str)
                                    flags_db = bot_settings.get("premium_flags", {})
                                    emoji_id_flag = "5780471598922337683"
                                    for flag_code, flag_data in flags_db.items():
                                        if iso == flag_data.get("iso"):
                                            if "id" in flag_data: emoji_id_flag = flag_data["id"]; break
                                    kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id_srv, "callback_data": "ignore", "style": "success"}]]
                                    kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id_flag, "copy_text": {"text": display_num}, "style": "primary"}])
                                    kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"c_n_{service}_{country}", "style": "danger"},
                                               {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
                                    c_btns = bot_settings["custom_messages"].get("get_number", {}).get("buttons", [])
                                    for c_b in c_btns:
                                        b_copy = c_b.copy()
                                        if "style" not in b_copy: b_copy["style"] = "primary"
                                        kb.append([b_copy])
                                    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
                                    edit_message(chat_id, msg_id, render_body_text("╔═══════════════╗\n║ 💬 Waiting For SMS...\n╚═══════════════╝"), reply_markup={"inline_keyboard": kb})
                                    user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": [num_str]}
                                    return
                            else:
                                err_msg = vx_data.get("meta", {}).get("message", "No number available")
                                answer_callback(call["id"], f"❌ {err_msg}", show_alert=True)
                        else:
                            answer_callback(call["id"], f"❌ VoltX API Error (HTTP {res_vx.status_code})", show_alert=True)
                    except Exception as e:
                        answer_callback(call["id"], f"❌ VoltX connection failed: {str(e)[:60]}", show_alert=True)
                    if not got_number:
                        if data.startswith("c_n_"): delete_message(chat_id, msg_id)
                        else: edit_message(chat_id, msg_id, render_body_text("❌ <b>Number out of stock!</b>\nTry again later."), reply_markup={"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]})
            if data.startswith("c_n_"): delete_message(chat_id, msg_id)
            return

        random.shuffle(available_indices)
        
        fetched_nums = []
        for b_id, idx in available_indices:
            if len(fetched_nums) >= bot_settings.get("num_req"): break
            n_obj = number_batches[b_id]["numbers"][idx]
            
            fetched_nums.append(n_obj["num"])
            n_obj["shares"] += 1
            n_obj["used_by"].append(chat_id)
            total_assigned_stats += 1
            
            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                if n_obj["num"] not in used_numbers_list:
                    used_numbers_list.append(n_obj["num"])
        save_db()

        if not fetched_nums:
            answer_callback(call["id"], "❌ You have already taken all numbers or stock is empty!", show_alert=True)
            if data.startswith("c_n_"): delete_message(chat_id, msg_id)
            return

        app_full_name, _ = get_service_info_html(service)
        emoji_id = "5337302974806922068"
        apps_db = bot_settings.get("premium_apps", {})
        for app_key, app_data in apps_db.items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data:
                    emoji_id = app_data["id"]
                    break
        kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id, "callback_data": "ignore", "style": "success"}]]
        
        flags_db = bot_settings.get("premium_flags", {})
        for num in fetched_nums:
            _, iso = get_flag_and_code(num)
            display_num = f"+{num}" if not num.startswith("+") else num
            
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data: emoji_id = flag_data["id"]
                    break
            kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
            
        kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"c_n_{service}_{country}", "style": "danger"},
                   {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
                   
        c_btns = bot_settings["custom_messages"].get("get_number", {}).get("buttons", [])
        for c_b in c_btns: 
            b_copy = c_b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        text_numbers = render_body_text("╔═══════════════╗\n║ 💬 Waiting For SMS...\n╚═══════════════╝")
        try:
            edit_message(chat_id, msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums}
        except:
            msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
            if msg_res and "result" in msg_res:
                user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}

    elif data.startswith("wapp_") or data.startswith("wrej_"):
        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Only Bot Admins can process withdrawals!", show_alert=True)
            return
            
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        
        if req_id in pending_withdrawals:
            req_data = pending_withdrawals[req_id]
            u_id, amt = req_data["user_id"], req_data["amount"]
            num = req_data["number"]
            full_name = req_data.get("full_name", u_id)
            
            if action == "APPROVE" and len(num) >= 7:
                masked_num = mask_number(num, user_id=u_id)
            else:
                masked_num = num
            
            status_text = "APPROVED" if action == "APPROVE" else "REJECTED"
            emoji_icon_id = "5352694861990501856" if action == "APPROVE" else "5420130255174145507"
            new_text = f"🎙 <b>WITHDRAWAL {status_text}</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={u_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amt} INR\n🍏 <b>NUMBER:</b> <code>{masked_num}</code>\n🏦 <b>METHOD:</b> {req_data['method']}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
            rendered_new_text = render_body_text(new_text)
            
            for sm in req_data.get("sent_messages", []):
                try: edit_message(sm["chat_id"], sm["message_id"], rendered_new_text)
                except: pass
            try: edit_message(chat_id, msg_id, rendered_new_text)
            except: pass
            
            if action == "REJECT":
                update_balance(u_id, amt) 
                send_message(u_id, render_body_text(f"❌ Your {amt} INR withdrawal request was rejected. Balance refunded."))
            else:
                send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} INR withdrawal request has been paid successfully!"))
            
            _update_local_withdrawal(req_id, {"status": "approved" if action == "APPROVE" else "rejected"})
                
            del pending_withdrawals[req_id]
        else:
            answer_callback(call["id"], "❌ Request already processed!", show_alert=True)

def poll_otp_with_status(number_id, num_str, owner_id, api_key):
    headers = {"X-API-Key": api_key}
    for _ in range(150):
        try:
            res = requests.get(f"{NEXA_BASE_URL}/api/v1/numbers/{number_id}/sms", headers=headers, timeout=10)
            data = res.json()
            if data.get("success") and data.get("otp"):
                otp = str(data["otp"])
                msg_text = data.get("message", f"Your code is {otp}")
                
                extracted_otp = extract_otp_code(msg_text)
                if extracted_otp and len(extracted_otp) > len(otp):
                    otp = extracted_otp
                    
                app_name = data.get("service", "Nexa Service")
                detected_app = detect_service(msg_text)
                if detected_app:
                    app_name = detected_app
                
                unique_id = f"POLL_{number_id}_{otp}"
                if unique_id not in processed_otps:
                    _track_processed_otp(unique_id)

                    char, iso = get_flag_and_code(num_str)
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                    
                    global recent_traffic
                    current_time = time.time()
                    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                    recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num_str, "time": current_time})
                    save_local_db()
                    
                    display_num = f"+{num_str}" if not str(num_str).startswith("+") else str(num_str)
                    masked = mask_number(display_num, user_id=owner_id)
                    lang = detect_language(msg_text)
                    
                    display_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} #{iso} {masked} {lang}\n╚═══════════════╝")
                    
                    for fw in bot_settings.get("fw_groups", []):
                        kb = [[{"text": f"📋 {otp}", "copy_text": {"text": otp}}]]
                        kb.append([{"text": "📋 Full Message", "copy_text": {"text": msg_text}}])
                        kb.append([{"text": "🤖 Get Number", "url": f"https://t.me/{BOT_USERNAME.lstrip('@')}"}])
                        for btn in fw.get("buttons", []):
                            b_obj = {"text": btn["text"], "url": btn["url"]}
                            kb.append([b_obj])
                        res = send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                        if not res.get("ok"):
                            print(f"❌ Group send failed [{fw['chat_id']}]: {res.get('description', 'Unknown error')}")
                    
                    inbox_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} #{iso} {display_num} {lang}\n╚═══════════════╝")
                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                    
                    reward = float(bot_settings.get("otp_reward", 0.0))
                    if reward > 0:
                        update_balance(owner_id, reward)
                        inbox_kb.append([{"text": f"Added {reward} ₹", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                    
                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                    
                    _increment_local_user(owner_id, "total_otps", 1)
                    try:
                        clean_poll_num = str(num_str).replace("+", "").replace(" ", "").replace("-", "").strip()
                        _track_otp_received(clean_poll_num)
                    except: pass
                break
        except: pass
        time.sleep(4)

def global_sms_listener():
    global processed_otps, recent_traffic, nexa_assigned_numbers, nexa_warmup_done
    first_run = True
    while True:
        try:
            nexa_keys = bot_settings.get("nexa_keys", [])
            for api_key in nexa_keys:
                try:
                    headers = {"X-API-Key": api_key}
                    try:
                        res = requests.get(f"{NEXA_BASE_URL}/api/v1/sms/latest", headers=headers, timeout=10)
                        data = res.json()
                    except:
                        res = requests.get(f"{NEXA_BASE_URL}/api/v1/console/logs?limit=20", headers=headers, timeout=10)
                        data = res.json()
                    if data.get("success") and "data" in data:
                        for item in data["data"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("sms", ""))
                            
                            app_name = item.get("app_name", "Unknown")
                            detected_app = detect_service(msg_text)
                            if detected_app:
                                app_name = detected_app
                                
                            otp = extract_otp_code(msg_text) or "CODE"
                            unique_id = f"NEXA_{num}_{item.get('id', otp)}"
                            
                            if unique_id not in processed_otps and num:
                                _track_processed_otp(unique_id)
                                
                                if first_run:
                                    continue
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                lang = detect_language(msg_text)
                                
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for nexa_n, n_owner in nexa_assigned_numbers.items():
                                        clean_nexa = str(nexa_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_nexa == clean_api_num or (len(clean_nexa) >= 8 and clean_nexa.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_nexa[-8:])):
                                            owner_id = n_owner
                                            break
                                
                                masked = mask_number(display_num, user_id=owner_id)
                                
                                display_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} #{iso} {masked} {lang}\n╚═══════════════╝")
                                
                                for fw in bot_settings["fw_groups"]:
                                    kb = [[{"text": f"📋 {otp}", "copy_text": {"text": otp}}]]
                                    kb.append([{"text": "📋 Full Message", "copy_text": {"text": msg_text}}])
                                    kb.append([{"text": "🤖 Get Number", "url": f"https://t.me/{BOT_USERNAME.lstrip('@')}"}])
                                    for btn in fw.get("buttons", []):
                                        b_obj = {"text": btn["text"], "url": btn["url"]}
                                        kb.append([b_obj])
                                    res = send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    if not res.get("ok"):
                                        print(f"❌ Group send failed [{fw['chat_id']}]: {res.get('description', 'Unknown error')}")
                                        
                                if owner_id:
                                    inbox_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} #{iso} {display_num} {lang}\n╚═══════════════╝")
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    reward = float(bot_settings.get("otp_reward", 0.0))
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                        inbox_kb.append([{"text": f"Added {reward} ₹", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    _increment_local_user(owner_id, "total_otps", 1)
                except: continue
        except: pass
        if first_run:
            first_run = False
            nexa_warmup_done = True
            print("🧹 Nexa warmup done — old OTPs skipped, now processing new ones only.")
        time.sleep(5)

def flush_old_updates():
    try:
        res = api_call("getUpdates?offset=-1&timeout=0")
        if res and "result" in res and res["result"]:
            last_id = res["result"][-1]["update_id"]
            api_call(f"getUpdates?offset={last_id + 1}&timeout=0")
            print(f"🧹 Flushed old Telegram updates (last_id={last_id})")
        else:
            print("🧹 No pending Telegram updates to flush.")
    except Exception as e:
        print(f"⚠️ Could not flush old updates: {e}")

def main():
    global BOT_USERNAME
    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")
    
    flush_old_updates()
    
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    print("📡 Background APIs & Global SMS Listener Started!")
    
    executor = ThreadPoolExecutor(max_workers=500)
    
    offset = None
    while True:
        try:
            updates = api_call(f"getUpdates?timeout=50&offset={offset}")
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update: 
                        executor.submit(handle_message, update["message"])
                    elif "callback_query" in update: 
                        executor.submit(handle_callback, update["callback_query"])
        except Exception as e:
            time.sleep(2)

class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        pass

def run_keep_alive():
    PORT = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", PORT), KeepAliveHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_keep_alive, daemon=True).start()
    print(f"🌐 Keep-Alive server started on port {os.environ.get('PORT', 8000)}")
    main()
