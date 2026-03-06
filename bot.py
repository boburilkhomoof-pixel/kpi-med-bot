import telebot
import datetime
import os

# TOKEN environment variable dan olinadi
TOKEN = "8716483413:AAEqs14n3l6hRrXC6hwAhkggTqI772ub-iY"  # Sizning tokeningiz

bot = telebot.TeleBot(TOKEN)

agents = {}
visits = []

# /start komandasi - bot haqida ma'lumot va buyruqlar
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = """
🤖 **KPI BOT**

Assalomu alaykum! KPI bot orqali kunlik faoliyatingizni kuzatishingiz mumkin.

📋 **MAVJUD BUYRUQLAR:**

/help - Barcha buyruqlar ro'yxati
/doctor - Doktor tashrifini qo'shish
/report - Bugungi hisobot
/plan - Ertangi reja tuzish
/stats - Oylik statistika

✅ Foydalanish uchun yuqoridagi buyruqlardan birini tanlang.
    """
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

# /help komandasi - barcha buyruqlar
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📋 **BATAFSIL BUYRUQLAR:**

/start - Botni ishga tushirish
/help - Bu yordam oynasi

**🏥 ASOSIY BUYRUQLAR:**
/doctor - Doktor tashrifini qo'shish
/plan - Ertangi kun rejasini tuzish
/report - Bugungi kun hisoboti
/stats - Oylik statistika

**📊 MANAGER UCHUN:**
/all_report - Barcha agentlar hisoboti
/top_agents - Eng yaxshi agentlar

🔹 Har bir doktorga kuniga 1 marta kirish mumkin
🔹 Kechki 21:00 dan keyin plan tuzish mumkin
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# /doctor komandasi - doktor qo'shish
@bot.message_handler(commands=['doctor'])
def doctor(message):
    user = message.from_user.id
    today = datetime.date.today()
    
    # Foydalanuvchi ismini olish
    user_name = message.from_user.first_name
    
    # Bugun kirganligini tekshirish
    for v in visits:
        if v["user"] == user and v["date"] == today:
            bot.send_message(message.chat.id, 
                           "⚠️ **Bugun allaqachon doktor kiritilgan!**\n\n"
                           "1 kunda faqat 1 marta doktor kiritish mumkin.",
                           parse_mode='Markdown')
            return

    # Yangi tashrif qo'shish
    visits.append({
        "user": user,
        "user_name": user_name,
        "date": today
    })

    # Doktorlar sonini hisoblash
    today_count = 0
    for v in visits:
        if v["date"] == today:
            today_count += 1

    success_text = f"""
✅ **Doktor tashrifi yozildi!**

👤 Agent: {user_name}
📅 Sana: {today}
📊 Bugungi tashriflar: {today_count}/12

KPI: {int((today_count/12)*100)}%
    """
    bot.send_message(message.chat.id, success_text, parse_mode='Markdown')

# /report komandasi - bugungi hisobot
@bot.message_handler(commands=['report'])
def report(message):
    today = datetime.date.today()
    user = message.from_user.id
    user_name = message.from_user.first_name
    
    # Bugungi tashriflarni hisoblash
    count = 0
    for v in visits:
        if v["user"] == user and v["date"] == today:
            count += 1

    # KPI hisoblash (norma: 12 doktor)
    kpi = int((count / 12) * 100) if count <= 12 else 100
    qolgan = 12 - count if count < 12 else 0
    
    # Progress bar
    progress = "🟩" * (count // 2) + "⬜" * ((12 - count) // 2)
    
    report_text = f"""
📊 **KUNLIK HISOBOT**
👤 Agent: {user_name}
📅 Sana: {today}

✅ **Kirilgan doktorlar: {count}/12**
{progress}

📈 **KPI: {kpi}%**

"""
    if qolgan > 0:
        report_text += f"⏳ Yana {qolgan} ta doktor kirishingiz kerak"
    else:
        report_text += "🎉 Bugungi normani bajardingiz! Tabriklaymiz!"
    
    bot.send_message(message.chat.id, report_text, parse_mode='Markdown')

# /plan komandasi - reja tuzish
@bot.message_handler(commands=['plan'])
def plan(message):
    user_name = message.from_user.first_name
    plan_text = """
📝 **ERTANGI REJA TUZISH**

Ertangi kun uchun rejangizni yozing.
Format:
`Doktorlar soni | Aptekalar soni | Hudud`

Misol:
`12 | 5 | Chilonzor`

Yoki oddiy matn shaklida yozishingiz mumkin.
    """
    msg = bot.send_message(message.chat.id, plan_text, parse_mode='Markdown')
    bot.register_next_step_handler(msg, save_plan)

def save_plan(message):
    user_name = message.from_user.first_name
    plan_data = message.text
    
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    
    success_text = f"""
✅ **ERTANGI REJA SAQLANDI!**

👤 Agent: {user_name}
📅 Sana: {tomorrow}

📋 Reja:
{plan_data}

Ertalab eslatma yuboriladi. Omad! 🚀
    """
    bot.send_message(message.chat.id, success_text, parse_mode='Markdown')
    
    # Regional manager ga xabar (agar ID ma'lum bo'lsa)
    try:
        manager_id = 6995658625  # Manager ID
        bot.send_message(manager_id, 
                        f"📋 Yangi plan:\nAgent: {user_name}\n{plan_data}")
    except:
        pass

# /stats komandasi - oylik statistika
@bot.message_handler(commands=['stats'])
def stats(message):
    user = message.from_user.id
    user_name = message.from_user.first_name
    today = datetime.date.today()
    
    # Oy boshidan buyon hisoblash
    month_start = datetime.date(today.year, today.month, 1)
    month_visits = 0
    
    for v in visits:
        if v["user"] == user and v["date"] >= month_start:
            month_visits += 1
    
    stats_text = f"""
📊 **OYLIK STATISTIKA**
👤 Agent: {user_name}
📅 Oy: {today.strftime('%B %Y')}

✅ Jami tashriflar: {month_visits}
📈 O'rtacha kunlik: {month_visits / today.day:.1f}

🏆 Kategoriya: {
    "A (3+ marta)" if month_visits > 30 else 
    "B (2 marta)" if month_visits > 20 else 
    "C (1 marta)" if month_visits > 10 else 
    "D (0 marta)"
}
    """
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

# /all_report komandasi - manager uchun (hammaga)
@bot.message_handler(commands=['all_report'])
def all_report(message):
    # Faqat manager tekshirish
    if message.from_user.id != 6995658625:
        bot.send_message(message.chat.id, "⛔ Bu buyruq faqat manager uchun!")
        return
    
    today = datetime.date.today()
    
    # Agentlar bo'yicha guruhlash
    agents_stats = {}
    for v in visits:
        if v["date"] == today:
            user_id = v["user"]
            if user_id not in agents_stats:
                agents_stats[user_id] = {
                    "name": v.get("user_name", f"User {user_id}"),
                    "count": 0
                }
            agents_stats[user_id]["count"] += 1
    
    if not agents_stats:
        bot.send_message(message.chat.id, "📊 Bugun hech qanday tashrif yo'q")
        return
    
    report = "📊 **BUGUNGI UMUMIY HISOBOT**\n\n"
    for agent_id, data in agents_stats.items():
        kpi = int((data["count"] / 12) * 100)
        report += f"👤 {data['name']}: {data['count']}/12 ({kpi}%)\n"
    
    bot.send_message(message.chat.id, report, parse_mode='Markdown')

print("✅ Bot ishga tushdi...")
bot.polling()
