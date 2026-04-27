# main.py
import threading
from .bot import main as bot_main
from .web import app
from .core.scheduler import scheduler
from .core.config import WEB_HOST, WEB_PORT

def run_web():
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Start scheduler
    scheduler.start()

    # Start web in a thread
    web_thread = threading.Thread(target=run_web)
    web_thread.start()

    # Run bot
    bot_main()