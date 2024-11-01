import telebot
from telebot import types
import os
from bot_manager import BotManager
import logging

# API Token
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
manager = BotManager()

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# স্টার্ট কমান্ড
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🚀 Deploy Bot', '🛑 Stop Bot')
    markup.row('📋 List Bots', '⚙️ Configure Bot')
    markup.row('🔍 Status Check', '💬 Help', 'ℹ️ About')
    
    bot.send_message(
        message.chat.id, 
        "স্বাগতম! 😊\n\nএই বট দিয়ে আপনি নতুন বট তৈরি, বন্ধ ও পরিচালনা করতে পারবেন।\nদয়া করে মেনু থেকে একটি অপশন নির্বাচন করুন।", 
        reply_markup=markup
    )

# বট ডিপ্লয় কমান্ড
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
            f"🎉 {bot_name} বটটি সফলভাবে ডিপ্লয় করা হয়েছে! ✅\n📍 পোর্ট: {port}\n\nএটি পরিচালনা করতে মেনু থেকে কমান্ড বেছে নিন।"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ ত্রুটি: {e}")

# বট বন্ধ কমান্ড
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

# বট তালিকা দেখার কমান্ড
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
    bot.send_message(message.chat.id, "⚙️ বটের স্থিতি পরীক্ষা চলছে...")
    # স্থিতি চেক করুন বা যে কোন সমস্যা সমাধান করুন।

# সহায়তা সেকশন
@bot.message_handler(regexp="💬 Help")
def help_section(message):
    help_text = (
        "💡 **সহায়তা মেনু** 💡\n\n"
        "🚀 **Deploy Bot** - নতুন একটি বট তৈরি করুন\n"
        "🛑 **Stop Bot** - চলমান বট বন্ধ করুন\n"
        "📋 **List Bots** - সব চালু থাকা বট তালিকা দেখুন\n"
        "⚙️ **Configure Bot** - বট কনফিগারেশন পরিবর্তন\n"
        "🔍 **Status Check** - বটের স্থিতি পরীক্ষা করুন\n"
    )
    bot.send_message(message.chat.id, help_text)

# সম্পর্কে তথ্য
@bot.message_handler(regexp="ℹ️ About")
def about_bot(message):
    about_text = (
        "ℹ️ **বট ম্যানেজার সম্পর্কে** ℹ️\n\n"
        "এই বট ম্যানেজারটি আপনাকে আপনার প্রয়োজন অনুসারে নতুন বট তৈরি, পরিচালনা, বন্ধ ও কনফিগার করতে সাহায্য করে।\n\n"
        "✔️ **ভাষা সমর্থন:** Python, Node.js\n"
        "✔️ **ফিচার:** Docker এবং ক্লাউডে পরিচালনার জন্য সাপোর্ট\n\n"
        "📌 **©Created By Rahat**\n"
    )
    bot.send_message(message.chat.id, about_text)

bot.polling()
