import os
import subprocess
import logging
import psutil

class BotManager:
    def __init__(self):
        self.bots = {}
        self.base_port = 8000
        os.makedirs("logs", exist_ok=True)

    def deploy_bot(self, bot_name, language):
        if bot_name in self.bots:
            logging.warning(f"Bot '{bot_name}' is already running.")
            return self.bots[bot_name]["port"]

        port = self.base_port + len(self.bots)
        bot_path = f"bots/{bot_name}"
        
        if language == "python":
            self.create_python_bot(bot_name, port)
            process = subprocess.Popen(["python", f"{bot_path}/bot.py"], stdout=open(f"logs/{bot_name}.log", "w"), stderr=subprocess.STDOUT)
        elif language == "nodejs":
            self.create_node_bot(bot_name, port)
            process = subprocess.Popen(["node", f"{bot_path}/bot.js"], stdout=open(f"logs/{bot_name}.log", "w"), stderr=subprocess.STDOUT)

        self.bots[bot_name] = {"process": process, "port": port, "language": language}
        logging.info(f"Bot '{bot_name}' deployed on port {port}.")
        return port

    def create_python_bot(self, bot_name, port):
        bot_path = f"bots/{bot_name}"
        os.makedirs(bot_path, exist_ok=True)
        with open(f"{bot_path}/bot.py", "w") as f:
            f.write(f"""
import os
import telebot
from flask import Flask

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@app.route('/start', methods=['GET'])
def start():
    bot.send_message(chat_id, "Python Bot Started!")
    return "Bot Started", 200

if __name__ == '__main__':
    app.run(port={port})
""")

    def create_node_bot(self, bot_name, port):
        bot_path = f"bots/{bot_name}"
        os.makedirs(bot_path, exist_ok=True)
        with open(f"{bot_path}/bot.js", "w") as f:
            f.write(f"""
const express = require('express');
const app = express();
const {{ Telegraf }} = require('telegraf');
const bot = new Telegraf(process.env.BOT_TOKEN);

bot.start((ctx) => ctx.reply('Node.js Bot Started!'));
bot.launch();

app.get('/start', (req, res) => {{
    res.send('Bot Started');
}});

app.listen({port});
""")

    def stop_bot(self, bot_name):
        bot_info = self.bots.get(bot_name)
        if not bot_info:
            logging.error(f"No bot named '{bot_name}' is running.")
            return False

        bot_info["process"].terminate()
        bot_info["process"].wait()
        del self.bots[bot_name]
        logging.info(f"Bot '{bot_name}' stopped.")
        return True

    def restart_bot(self, bot_name):
        bot_info = self.bots.get(bot_name)
        if not bot_info:
            logging.error(f"No bot named '{bot_name}' is running.")
            return False

        self.stop_bot(bot_name)
        return self.deploy_bot(bot_name, bot_info["language"])

    def update_bot_code(self, bot_name):
        bot_info = self.bots.get(bot_name)
        if not bot_info:
            logging.error(f"No bot named '{bot_name}' is running.")
            return False

        logging.info(f"Updating code for '{bot_name}'...")
        # Here, implement Git or another method to update the bot code
        return True

    def list_bots(self):
        return [{"name": name, "port": info["port"]} for name, info in self.bots.items()]

    def get_logs(self, bot_name):
        log_path = f"logs/{bot_name}.log"
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                return f.read()
        return "No logs found."

    def get_resource_usage(self):
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        return f"CPU Usage: {cpu_usage}%\nRAM Usage: {ram_usage}%"

    def check_health(self):
        health_data = []
        for bot_name, bot_info in self.bots.items():
            try:
                response = requests.get(f"http://localhost:{bot_info['port']}/start")
                status = "Running" if response.status_code == 200 else "Down"
            except:
                status = "Down"
            health_data.append({"name": bot_name, "status": status})
        return health_data
