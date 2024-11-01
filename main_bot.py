import telebot
from telebot import types
import os
from bot_manager import BotManager
import logging

# API Token
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
manager = BotManager()

# Logging সেটআপ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# স্টার্ট কমান্ড
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🚀 Deploy Bot', '🛑 Stop Bot', '🔄 Restart Bot')
    markup.row('📋 List Bots', '⚙️ Configure Bot')
    markup.row('🔍 Status Check', '💾 Logs')
    markup.row('🖥 Resource Usage', '🛠 Update Bot Code')
    markup.row('💬 Help', 'ℹ️ About')
    
    bot.send_message(
        message.chat.id, 
        "স্বাগতম! 😊\n\nএই বট দিয়ে আপনি নতুন বট তৈরি, বন্ধ, পরিচালনা ও রিস্টার্ট করতে পারবেন।\nদয়া করে মেনু থেকে একটি অপশন নির্বাচন করুন।", 
        reply_markup=markup
    )

# বট ডিপ্লয়
@bot.message_handler(regexp="🚀 Deploy Bot")
def deploy_bot_command(message):
    msg = bot.send_message(
        message.chat.id, 
        "নতুন বটের নাম এবং ভাষা (python/nodejs) লিখুন (উদাহরণ: bot_name python):"
    )
    bot.register_next_step_handler(msg, deploy_bot)

def deploy_bot(message):
    try:
        bot_name, language = message.text.split()
        port = manager.deploy_bot(bot_name, language)
        bot.send_message(
            message.chat.id, 
            f"🎉 {bot_name} বটটি সফলভাবে ডিপ্লয় করা হয়েছে! ✅\n📍 পোর্ট: {port}"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ ত্রুটি: {e}")

# বট বন্ধ
@bot.message_handler(regexp="🛑 Stop Bot")
def stop_bot_command(message):
    msg = bot.send_message(message.chat.id, "যে বটটি বন্ধ করতে চান তার নাম লিখুন:")
    bot.register_next_step_handler(msg, stop_bot)

def stop_bot(message):
    bot_name = message.text
    if manager.stop_bot(bot_name):
        bot.send_message(message.chat.id, f"🛑 {bot_name} বটটি সফলভাবে বন্ধ হয়েছে!")
    else:
        bot.send_message(message.chat.id, f"⚠️ {bot_name} বটটি চালু ছিল না।")

# বট রিস্টার্ট
@bot.message_handler(regexp="🔄 Restart Bot")
def restart_bot_command(message):
    msg = bot.send_message(message.chat.id, "যে বটটি রিস্টার্ট করতে চান তার নাম লিখুন:")
    bot.register_next_step_handler(msg, restart_bot)

def restart_bot(message):
    bot_name = message.text
    if manager.restart_bot(bot_name):
        bot.send_message(message.chat.id, f"🔄 {bot_name} বটটি সফলভাবে রিস্টার্ট হয়েছে!")
    else:
        bot.send_message(message.chat.id, f"⚠️ {bot_name} বটটি চালু ছিল না।")

# বটের তালিকা
@bot.message_handler(regexp="📋 List Bots")
def list_bots(message):
    bots = manager.list_bots()
    if bots:
        bot_list = "\n".join([f"🟢 {b['name']} - পোর্ট: {b['port']}" for b in bots])
        bot.send_message(message.chat.id, f"চালু থাকা বট:\n\n{bot_list}")
    else:
        bot.send_message(message.chat.id, "⚠️ বর্তমানে কোনো বট চালু নেই।")

# বট কনফিগারেশন চেক
@bot.message_handler(regexp="⚙️ Configure Bot")
def configure_bot(message):
    bot.send_message(message.chat.id, "আপনি এখানে বটের কনফিগারেশন এবং সেটিংস পরিবর্তন করতে পারবেন।")

# স্থিতি পরীক্ষা
@bot.message_handler(regexp="🔍 Status Check")
def status_check(message):
    status_info = manager.check_health()
    if status_info:
        status_list = "\n".join([f"🟢 {s['name']} - স্থিতি: {s['status']}" for s in status_info])
        bot.send_message(message.chat.id, f"বটগুলোর বর্তমান স্থিতি:\n\n{status_list}")
    else:
        bot.send_message(message.chat.id, "⚠️ কোনো বট চলছে না।")

# লগ দেখানো
@bot.message_handler(regexp="💾 Logs")
def show_logs(message):
    msg = bot.send_message(message.chat.id, "যে বটটির লগ দেখতে চান তার নাম লিখুন:")
    bot.register_next_step_handler(msg, show_bot_logs)

def show_bot_logs(message):
    bot_name = message.text
    logs = manager.get_logs(bot_name)
    if logs:
        bot.send_message(message.chat.id, f"📄 **{bot_name} বটের লগ:**\n\n{logs}")
    else:
        bot.send_message(message.chat.id, "⚠️ কোনো লগ পাওয়া যায়নি।")

# রিসোর্স ব্যবহার
@bot.message_handler(regexp="🖥 Resource Usage")
def resource_usage(message):
    usage = manager.get_resource_usage()
    bot.send_message(message.chat.id, f"📊 **রিসোর্স ব্যবহার:**\n\n{usage}")

# বট কোড আপডেট করা
@bot.message_handler(regexp="🛠 Update Bot Code")
def update_bot_code(message):
    msg = bot.send_message(message.chat.id, "যে বটটির কোড আপডেট করতে চান তার নাম লিখুন:")
    bot.register_next_step_handler(msg, update_code)

def update_code(message):
    bot_name = message.text
    if manager.update_bot_code(bot_name):
        bot.send_message(message.chat.id, f"🛠 {bot_name} বটের কোড সফলভাবে আপডেট হয়েছে!")
    else:
        bot.send_message(message.chat.id, "⚠️ আপডেট করতে সমস্যা হয়েছে।")

# সহায়তা
@bot.message_handler(regexp="💬 Help")
def help_section(message):
    help_text = (
        "💡 **সহায়তা মেনু** 💡\n\n"
        "🚀 **Deploy Bot** - নতুন একটি বট তৈরি করুন\n"
        "🛑 **Stop Bot** - চলমান বট বন্ধ করুন\n"
        "🔄 **Restart Bot** - বট পুনরায় চালু করুন\n"
        "📋 **List Bots** - সব চালু থাকা বট তালিকা দেখুন\n"
        "⚙️ **Configure Bot** - বট কনফিগারেশন পরিবর্তন\n"
        "🔍 **Status Check** - বটের স্থিতি পরীক্ষা করুন\n"
        "💾 **Logs** - লগ দেখুন\n"
        "🖥 **Resource Usage** - CPU এবং RAM ব্যবহার\n"
        "🛠 **Update Bot Code** - বটের কোড আপডেট করুন\n"
    )
    bot.send_message(message.chat.id, help_text)

# সম্পর্কে তথ্য
@bot.message_handler(regexp="ℹ️ About")
def about_bot(message):
    about_text = (
        "ℹ️ **বট ম্যানেজার সম্পর্কে** ℹ️\n\n"
        "এই বট ম্যানেজারটি আপনাকে আপনার প্রয়োজন অনুসারে নতুন বট তৈরি, পরিচালনা, বন্ধ, রিস্টার্ট এবং আপডেট করতে সাহায্য করে।\n\n"
        "✔️ **ভাষা সমর্থন:** Python, Node.js\n"
        "✔️ **ফিচার:** Docker এবং ক্লাউডে পরিচালনার জন্য সাপোর্ট\n\n"
        "📌 **©Created By Rahat**\n"
    )
    bot.send_message(message.chat.id, about_text)

bot.polling()
