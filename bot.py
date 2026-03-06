from flask import Flask, request
import telebot
from telebot.types import Update
import os
import time
import logging

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot tokeni
TOKEN = "8716483413:AAEqs14n3l6hRrXC6hwAhkggTqI772ub-iY"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Health check
@app.route('/', methods=['GET'])
def home():
    return 'Bot is running!', 200

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        logger.info("📩 Webhook so'rovi keldi")
        json_str = request.get_data().decode('UTF-8')
        update = Update.de_json(json_str)
        bot.process_new_updates([update])
        logger.info("✅ Update qayta ishlandi")
        return 'OK', 200
    except Exception as e:
        logger.error(f"❌ Xatolik: {e}")
        return 'Error', 500

# ============= HANDLERLAR =============
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Start va help komandalari"""
    logger.info(f"Komanda keldi: {message.text}")
    welcome_text = """
🤖 **KPI BOT**

Assalomu alaykum! Bot ishga tushdi.

📋 **MAVJUD BUYRUQLAR:**
/start - Botni ishga tushirish
/help - Yordam
/doctor - Doktor tashrifi
/apteka - Apteka tashrifi
/report - Kunlik hisobot

✅ Istalgan buyruqni yozing.
    """
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['doctor'])
def doctor(message):
    """Doktor tashrifi"""
    logger.info(f"Doktor komandasi: {message.from_user.first_name}")
    bot.send_message(message.chat.id, "✅ Doktor tashrifi qo'shildi!")

@bot.message_handler(commands=['apteka'])
def apteka(message):
    """Apteka tashrifi"""
    logger.info(f"Apteka komandasi: {message.from_user.first_name}")
    bot.send_message(message.chat.id, "✅ Apteka tashrifi qo'shildi!")

@bot.message_handler(commands=['report'])
def report(message):
    """Kunlik hisobot"""
    logger.info(f"Report komandasi: {message.from_user.first_name}")
    bot.send_message(message.chat.id, "📊 Kunlik hisobot tayyorlanmoqda...")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    """Boshqa barcha xabarlar"""
    logger.info(f"Xabar keldi: {message.text}")
    bot.send_message(message.chat.id, f"Siz yozdingiz: {message.text}")

# ============= ASOSIY QISM =============
if __name__ == '__main__':
    logger.info("✅ Bot ishga tushmoqda...")
    
    # Webhook o'rnatish
    bot.remove_webhook()
    time.sleep(1)
    webhook_url = 'https://kpi-med-bot.onrender.com/webhook'
    bot.set_webhook(url=webhook_url)
    logger.info(f"✅ Webhook o'rnatildi: {webhook_url}")
    
    # Webhook info
    webhook_info = bot.get_webhook_info()
    logger.info(f"📊 Webhook info: {webhook_info.url}")
    
    # Serverni ishga tushirish
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
