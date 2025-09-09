from linepy import *
import json
import os
from datetime import datetime

# ==========================
# إعداد المتغيرات
AUTH_TOKEN = os.getenv("LINE_AUTH_TOKEN")  # ضع authToken هنا
GROUP_ID = os.getenv("GROUP_ID")           # رقم مجموعتك
MAIN_ADMIN = os.getenv("ADMIN_ID")         # انت فقط المسؤول

client = LINE(AUTH_TOKEN)
print(f"✅ البوت شغال بحساب: {client.profile.displayName}")

# ==========================
# تخزين البيانات
DATA_FILE = "lurk_data.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "lurking": False,
        "lurkers": [],
        "admins": [MAIN_ADMIN]
    }

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================
# متابعة الرسائل
@client.add_event(55)  # OpType 55 = MESSAGE_READ
def on_seen(op):
    if not data["lurking"]: return
    try:
        user = client.getContact(op.param2)
        if not any(l["id"] == user.id for l in data["lurkers"]):
            data["lurkers"].append({
                "id": user.id,
                "name": user.displayName,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_data()
    except: pass

# ==========================
# التعامل مع الرسائل
@client.add_event(26)  # OpType 26 = MESSAGE
def on_message(op):
    msg = op.message
    text = getattr(msg, "text", "")
    sender = msg.from_

    # الأوامر للمسؤول فقط
    if sender in data["admins"]:
        if text.lower() == ".lurk on":
            data["lurking"] = True
            data["lurkers"] = []
            save_data()
            client.sendMessage(GROUP_ID, "✅ تم تفعيل التتبع.")

        elif text.lower() == ".lurk off":
            data["lurking"] = False
            save_data()
            client.sendMessage(GROUP_ID, "⛔ تم إيقاف التتبع.")

        elif text.lower() == ".list":
            if data["lurkers"]:
                lst = "\n".join([f"- {l['name']} ({l['time']})" for l in data["lurkers"]])
                client.sendMessage(GROUP_ID, f"👀 المتصلون:\n{lst}")
            else:
                client.sendMessage(GROUP_ID, "📭 لا يوجد متصلون مسجلون.")

        elif text.lower().startswith(".gadmin "):
            try:
                mention_name = text.split("@")[1].strip()
                mems = client.getGroup(GROUP_ID).members
                found = False
                for m in mems:
                    if m.displayName == mention_name:
                        if m.id not in data["admins"]:
                            data["admins"].append(m.id)
                            save_data()
                        found = True
                        break
                if found:
                    client.sendMessage(GROUP_ID, f"✅ {mention_name} أصبح أدمن.")
                else:
                    client.sendMessage(GROUP_ID, "❌ لم أجد العضو.")
            except:
                client.sendMessage(GROUP_ID, "❌ صيغة الأمر خاطئة. استخدم: .gadmin @الاسم")

# ==========================
# تشغيل البوت
client.pollStream()
