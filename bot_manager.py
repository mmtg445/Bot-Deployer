import os
import subprocess
import logging

class BotManager:
    def __init__(self):
        self.bots = {}
        self.base_port = 8000

    def deploy_bot(self, bot_name, language):
        if bot_name in self.bots:
            logging.warning(f"Bot '{bot_name}' is already running.")
            return self.bots[bot_name]["port"]

        port = self.base_port + len(self.bots)
        bot_path = f"bots/{bot_name}"
        os.makedirs(bot_path, exist_ok=True)

        if language == "python":
            self.create_python_bot(bot_name, port)
            process = subprocess.Popen(["python3", f"{bot_path}/bot.py"])
        elif language == "nodejs":
            self.create_node_bot(bot_name, port)
            process = subprocess.Popen(["node", f"{bot_path}/bot.js"])

        self.bots[bot_name] = {"process": process, "port": port}
        logging.info(f"Bot '{bot_name}' deployed on port {port}.")
        return port

    def create_python_bot(self, bot_name, port):
        bot_path = f"bots/{bot_name}"
        with open(f"{bot_path}/bot.py", "w") as f:
            f.write(f"""
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Python Bot Running!"

if __name__ == '__main__':
    app.run(port={port})
""")

    def create_node_bot(self, bot_name, port):
        bot_path = f"bots/{bot_name}"
        with open(f"{bot_path}/bot.js", "w") as f:
            f.write(f"""
const express = require('express');
const app = express();

app.get('/', (req, res) => {{
    res.send('Node.js Bot Running!');
}});

app.listen({port}, () => {{
    console.log('Bot running on port {port}');
}});
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

    def list_bots(self):
        return [{"name": name, "port": info["port"]} for name, info in self.bots.items()]
