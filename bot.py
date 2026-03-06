import telebot
import datetime

TOKEN = "BOT_TOKEN"

bot = telebot.TeleBot(TOKEN)

agents = {}
visits = []

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "KPI BOT ishga tushdi")

@bot.message_handler(commands=['doctor'])
def doctor(message):
    user = message.from_user.id
    today = datetime.date.today()

    for v in visits:
        if v["user"] == user and v["date"] == today:
            bot.send_message(message.chat.id,"Bugun allaqachon doktor kiritilgan")
            return

    visits.append({
        "user": user,
        "date": today
    })

    bot.send_message(message.chat.id,"Doktor tashrifi yozildi")

@bot.message_handler(commands=['report'])
def report(message):
    today = datetime.date.today()
    count = 0

    for v in visits:
        if v["date"] == today:
            count += 1

    bot.send_message(message.chat.id,f"Bugungi tashriflar: {count}")

bot.polling()
