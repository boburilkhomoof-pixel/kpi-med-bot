import telebot
import datetime
import os
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from flask import Flask, request
import threading
import time

# TOKEN
TOKEN = "8716483413:AAEqs14n3l6hRrXC6hwAhkggTqI772ub-iY"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

agents = {}
visits = []  # Doktor tashriflari
pharmacy_visits = []  # Apteka tashriflari

# Health check endpoint
@app.route('/')
def index():
    return '🤖 KPI Bot is running!', 200

@app.route('/health')
def health():
    return 'OK', 200

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("✅ Webhook so'rov keldi!")
        
        json_str = request.get_data().decode('UTF-8')
        print(f"📦 Ma'lumot: {json_str[:100]}...")
        
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        
        print("✅ So'rov muvaffaqiyatli qayta ishlandi")
        return 'OK', 200
    except Exception as e:
        print(f"❌ XATOLIK: {str(e)}")
        return 'Error', 500

# Webhook sozlash
def setup_webhook():
    time.sleep(3)
    try:
        render_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://kpi-med-bot.onrender.com')
        webhook_url = f"{render_url}/webhook"
        
        print(f"🔧 Webhook sozlanmoqda: {webhook_url}")
        
        bot.remove_webhook()
        time.sleep(1)
        
        bot.set_webhook(url=webhook_url)
        
        print(f"✅ Webhook sozlandi: {webhook_url}")
        
        info = bot.get_webhook_info()
        print(f"📊 Webhook info: {info.url}")
    except Exception as e:
        print(f"❌ Webhook xatosi: {e}")

# ============== OYLIK HISOBOT FUNKSIYALARI ==============
# (bu qism avvalgidek qoladi - joy tejash uchun qisqartirildi)
# Siz avvalgi kodingizdagi generate_excel_report va generate_word_report 
# funksiyalarini shu yerga qo'shishingiz kerak

# ============== BOT BUYRUQLARI ==============
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = """
🤖 **KPI BOT**

Assalomu alaykum! KPI bot ishga tushdi.

📋 **MAVJUD BUYRUQLAR:**
/help - Yordam
/doctor - Doktor tashrifi
/apteka - Apteka tashrifi
/report - Kunlik hisobot
    """
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📋 **BATAFSIL BUYRUQLAR:**
/doctor - Doktor tashrifi qo'shish
/apteka - Apteka tashrifi qo'shish
/report - Bugungi hisobot
/plan - Reja tuzish
/stats - Oylik statistika
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['doctor'])
def doctor(message):
    user = message.from_user.id
    today = datetime.date.today()
    user_name = message.from_user.first_name
    
    for v in visits:
        if v["user"] == user and v["date"] == today:
            bot.send_message(message.chat.id, "⚠️ Bugun allaqachon doktor kiritilgan!")
            return

    visits.append({"user": user, "user_name": user_name, "date": today})
    bot.send_message(message.chat.id, f"✅ Doktor tashrifi yozildi! ({user_name})")

@bot.message_handler(commands=['apteka'])
def apteka(message):
    user = message.from_user.id
    today = datetime.date.today()
    user_name = message.from_user.first_name
    
    pharmacy_visits.append({"user": user, "user_name": user_name, "date": today})
    bot.send_message(message.chat.id, f"✅ Apteka tashrifi yozildi! ({user_name})")

@bot.message_handler(commands=['report'])
def report(message):
    today = datetime.date.today()
    user = message.from_user.id
    
    doctor_count = sum(1 for v in visits if v["user"] == user and v["date"] == today)
    apteka_count = sum(1 for p in pharmacy_visits if p["user"] == user and p["date"] == today)
    
    report_text = f"""
📊 **KUNLIK HISOBOT**
📅 Sana: {today}
🏥 Doktor: {doctor_count}/12
💊 Apteka: {apteka_count}/5
    """
    bot.send_message(message.chat.id, report_text)

# Boshqa buyruqlarni ham shu yerga qo'shing...

if __name__ == "__main__":
    # Webhook sozlash
    threading.Thread(target=setup_webhook, daemon=True).start()
    
    # Flask serverni ishga tushirish
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
