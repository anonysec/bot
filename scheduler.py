# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import SessionLocal, get_user_subscriptions, update_subscription_traffic
from panel import XUIPanel
from config import TRAFFIC_ALERT_GB
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

panel = XUIPanel()
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def check_traffic():
    db = SessionLocal()
    subs = db.query(Subscription).all()
    for sub in subs:
        # Get current traffic from panel
        remaining = panel.get_client_traffic(sub.email)  # Assuming email is unique
        if remaining is not None:
            update_subscription_traffic(db, sub.client_id, sub.total_gb - remaining)
            if remaining <= TRAFFIC_ALERT_GB:
                # Send alert
                asyncio.run(send_alert(sub.user.telegram_id, f"Low traffic alert: {remaining} GB left"))
    db.close()

async def send_alert(chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)

scheduler = BackgroundScheduler()
scheduler.add_job(check_traffic, IntervalTrigger(hours=1))  # Check every hour
scheduler.start()