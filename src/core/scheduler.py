# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from ..db.database import SessionLocal, get_user_subscriptions, update_subscription_traffic, Subscription
from ..core.panel import XUIPanel
from ..core.config import TRAFFIC_ALERT_GB, TELEGRAM_BOT_TOKEN, ADMIN_IDS
from ..utils.leak_protection import LeakDetector
from telegram import Bot
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

panel = XUIPanel()
bot = Bot(token=TELEGRAM_BOT_TOKEN)
leak_detector = LeakDetector()

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

def check_leaks():
    """Check for VPN leaks and alert admins"""
    try:
        leaks = leak_detector.check_all_leaks()
        if leaks:
            alert_msg = "🚨 VPN Leak Detected!\n" + "\n".join(leaks)
            # Send to all admins
            for admin_id in ADMIN_IDS:
                asyncio.run(send_alert(admin_id, alert_msg))
    except Exception as e:
        logger.error(f"Leak check failed: {e}")

async def send_alert(chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)

scheduler = BackgroundScheduler()
scheduler.add_job(check_traffic, IntervalTrigger(hours=1))  # Check every hour
scheduler.add_job(check_leaks, IntervalTrigger(hours=6))    # Check for leaks every 6 hours
scheduler.start()