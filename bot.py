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
import logging

# Logging sozlamalari (xatolarni ko'rish uchun)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# TOKEN
TOKEN = "8716483413:AAEqs14n3l6hRrXC6hwAhkggTqI772ub-iY"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

agents = {}
visits = []  # Doktor tashriflari
pharmacy_visits = []  # Apteka tashriflari

# ==================== MUHIM: HEALTH CHECK ENDPOINTS ====================
@app.route('/', methods=['GET'])
def index():
    """Render health check uchun - bot ishlayotganini ko'rsatadi"""
    logger.info("Health check (/) so'rovi keldi")
    return 'KPI Bot is running!', 200

@app.route('/health', methods=['GET'])
def health():
    """Render health check uchun alternativ endpoint"""
    logger.info("Health check (/health) so'rovi keldi")
    return 'OK', 200
# =======================================================================

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram dan keladigan barcha update larni qabul qiladi"""
    try:
        logger.info("✅ Webhook endpointiga POST so'rov keldi")
        
        # So'rov ma'lumotini o'qish
        json_str = request.get_data().decode('UTF-8')
        logger.info(f"📦 Kelgan ma'lumot (boshi): {json_str[:200]}...")
        
        # Update ni Telegram bot ga yuborish
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        
        logger.info("✅ So'rov muvaffaqiyatli qayta ishlandi")
        return 'OK', 200
    except Exception as e:
        logger.error(f"❌ Webhook xatoligi: {str(e)}", exc_info=True)
        return f'Error: {str(e)}', 500

# Bot polling o'rniga webhook bilan ishlaydi
def setup_webhook():
    """Render ishga tushgandan keyin webhook ni sozlash"""
    time.sleep(3)  # Render to'liq ishga tushishi uchun biroz kutish
    try:
        # Render URL'ni olish
        render_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://kpi-med-bot.onrender.com')
        webhook_url = f"{render_url}/webhook"
        
        logger.info(f"🔧 Webhook sozlanmoqda: {webhook_url}")
        
        # Eski webhook ni o'chirish
        bot.remove_webhook()
        time.sleep(1)
        
        # Yangi webhook o'rnatish
        bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook muvaffaqiyatli o'rnatildi: {webhook_url}")
        
        # Webhook info ni tekshirish
        webhook_info = bot.get_webhook_info()
        logger.info(f"📊 Webhook info: {webhook_info}")
        
    except Exception as e:
        logger.error(f"❌ Webhook o'rnatishda xatolik: {str(e)}", exc_info=True)

# ============== BOT BUYRUQLARI (ODDIY TEST UCHUN) ==============
@bot.message_handler(commands=['start'])
def start(message):
    """Start komandasi - bot ishlayotganini tekshirish"""
    logger.info(f"/start komandasi keldi: user={message.from_user.id}")
    bot.send_message(message.chat.id, "KPI BOT ishga tushdi!")
    
# ============== QOLGAN BUYRUQLAR (KEYINROQ QO'SHILADI) ==============
# Sizning to'liq kodlaringiz shu yerdan davom etadi...
# /doctor, /apteka, /report, /plan, /stats, /monthly_excel, /monthly_word, /all_report

# ==================== ASOSIY QISM ====================
if __name__ == "__main__":
    logger.info("✅ Bot ishga tushmoqda...")
    
    # Webhook sozlash uchun alohida thread
    threading.Thread(target=setup_webhook, daemon=True).start()
    
    # Flask serverni ishga tushirish
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Flask server ishga tushmoqda: 0.0.0.0:{port}")
    
    # Flask ni ishga tushirish (debug=False MUHIM!)
    app.run(host='0.0.0.0', port=port, debug=False)
