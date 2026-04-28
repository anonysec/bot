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
    terminated_count = 0

    for sub in subs:
        try:
            # Get current traffic from panel
            remaining = panel.get_client_traffic(sub.email)
            if remaining is not None:
                used_traffic = sub.total_gb - remaining
                update_subscription_traffic(db, sub.client_id, used_traffic)

                # Check if traffic limit exceeded
                if used_traffic >= sub.total_gb and sub.total_gb > 0:
                    # Traffic limit reached - terminate connection
                    if panel.disable_client(sub.email):
                        logger.info(f"Terminated connection for {sub.email} - traffic limit reached")
                        terminated_count += 1
                        # Send notification to user
                        asyncio.run(send_alert(sub.user.telegram_id,
                            f"🚫 Your VPN connection has been terminated due to traffic limit reached.\n"
                            f"Used: {used_traffic:.2f} GB / Total: {sub.total_gb:.2f} GB"))
                    else:
                        logger.error(f"Failed to terminate connection for {sub.email}")

                # Send low traffic alert (only if not already terminated)
                elif remaining <= TRAFFIC_ALERT_GB and remaining > 0:
                    asyncio.run(send_alert(sub.user.telegram_id, f"⚠️ Low traffic alert: {remaining:.2f} GB left"))
        except Exception as e:
            logger.error(f"Error checking traffic for {sub.email}: {e}")

    db.close()

    if terminated_count > 0:
        logger.info(f"Terminated {terminated_count} connections due to traffic limits")

def check_psiphon_abuse():
    """Check for Psiphon abuse patterns"""
    try:
        # Get all active clients
        clients = panel.get_clients()
        suspicious_clients = []

        for client in clients:
            # Check for Psiphon-like patterns
            email = client.get('email', '')
            if is_psiphon_client(email, client):
                suspicious_clients.append(client)
                # Disable suspicious client
                if panel.disable_client(email):
                    logger.warning(f"Disabled suspected Psiphon client: {email}")
                else:
                    logger.error(f"Failed to disable Psiphon client: {email}")

        if suspicious_clients:
            alert_msg = f"🚨 Disabled {len(suspicious_clients)} suspected Psiphon clients"
            for admin_id in ADMIN_IDS:
                asyncio.run(send_alert(admin_id, alert_msg))

    except Exception as e:
        logger.error(f"Psiphon check failed: {e}")

def is_psiphon_client(email, client_data):
    """Detect Psiphon-like client patterns"""
    # Psiphon typically uses random-looking email patterns
    if not email:
        return False

    # Check for random alphanumeric patterns (Psiphon generates random emails)
    import re
    if re.match(r'^[a-zA-Z0-9]{10,}@.*$', email):
        return True

    # Check for excessive connections (Psiphon creates many connections)
    connections = client_data.get('connections', 0)
    if connections > 50:  # Arbitrary threshold
        return True

    # Check for unusual traffic patterns (very high upload/download ratio)
    up_traffic = client_data.get('up', 0)
    down_traffic = client_data.get('down', 0)
    if down_traffic > 0 and (up_traffic / down_traffic) > 10:  # High upload ratio
        return True

    return False

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
scheduler.add_job(check_psiphon_abuse, IntervalTrigger(hours=2))  # Check for Psiphon abuse every 2 hours
scheduler.add_job(check_leaks, IntervalTrigger(hours=6))    # Check for leaks every 6 hours
scheduler.start()