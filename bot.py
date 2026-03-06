from flask import Flask, request  # Bu qator borligiga ishonch hosil qiling
import telebot
import os
import time

TOKEN = "8716483413:AAEqs14n3l6hRrXC6hwAhkggTqI772ub-iY"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# MUHIM: GET so'rovlari uchun alohida endpoint
@app.route('/', methods=['GET'])
def home():
    return 'Bot is running!', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('UTF-8'))
    bot.process_new_updates([update])
    return 'OK', 200

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(message.chat.id, f"Siz yozdingiz: {message.text}")

if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url='https://kpi-med-bot.onrender.com/webhook')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
