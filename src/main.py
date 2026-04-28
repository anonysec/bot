# main.py
import threading
import sys
import os

# Set config file before importing other modules
if len(sys.argv) > 1:
    config_file = sys.argv[1]
    # Set environment variable for config file path
    os.environ['VPN_BOT_CONFIG_FILE'] = config_file

from .bot.bot import main as bot_main
from .web.web import app
from .core.scheduler import scheduler
from .core.config import WEB_HOST, WEB_PORT, set_config_file

def run_web():
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Set config file if provided
    config_file = os.environ.get('VPN_BOT_CONFIG_FILE', 'config.json')
    config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_file)
    set_config_file(config_file_path)

    # Start scheduler
    scheduler.start()

    # Start web in a thread
    web_thread = threading.Thread(target=run_web)
    web_thread.start()

    # Run bot
    bot_main()