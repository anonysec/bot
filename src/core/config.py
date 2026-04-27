# config.py
import os
from ..utils.helpers import convert_traffic
from ..utils.constants import TRAFFIC_UNIT_MB, TRAFFIC_UNIT_GB

# Panel Configuration
PANEL_URL = os.getenv('PANEL_URL', 'https://your-panel-url')  # Use HTTPS
USERNAME = os.getenv('PANEL_USERNAME', 'admin')
PASSWORD = os.getenv('PANEL_PASSWORD', 'password')
PANEL_PROXY = os.getenv('PANEL_PROXY')  # e.g., 'http://proxy:port' or 'socks5://proxy:port'

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your-bot-token')
TELEGRAM_PROXY = os.getenv('TELEGRAM_PROXY')  # e.g., 'http://proxy:port' or 'socks5://proxy:port'

# Inbound ID
INBOUND_ID = int(os.getenv('INBOUND_ID', '1'))

# Plans - Support MB/GB mixed units
PLANS = {
    'basic': {'name': 'Basic (500MB)', 'traffic': 500, 'unit': TRAFFIC_UNIT_MB, 'price': 5, 'name_fa': 'پایه (500 مگ)', 'duration_days': 30},
    'standard': {'name': 'Standard (10GB)', 'traffic': 10, 'unit': TRAFFIC_UNIT_GB, 'price': 15, 'name_fa': 'استاندارد (10 گیگ)', 'duration_days': 30},
    'premium': {'name': 'Premium (50GB)', 'traffic': 50, 'unit': TRAFFIC_UNIT_GB, 'price': 20, 'name_fa': 'پریمیوم (50 گیگ)', 'duration_days': 30}
}

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///vpn_bot.db')

# Web App
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())  # Secure random key
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
WEB_PORT = int(os.getenv('WEB_PORT', '5000'))

# Traffic Alert Threshold (GB)
TRAFFIC_ALERT_GB = float(os.getenv('TRAFFIC_ALERT_GB', '1'))

# Software Links
SOFTWARE_LINKS = {
    'android': 'https://play.google.com/store/apps/details?id=com.v2ray.ang',
    'ios': 'https://apps.apple.com/app/v2box/id6446814690',
    'windows': 'https://github.com/2dust/v2rayN/releases',
    'mac': 'https://github.com/yanue/V2rayU/releases'
}

# Payment Gateways
PAYMENT_GATEWAY = os.getenv('PAYMENT_GATEWAY', 'zarinpal')  # zarinpal, payir, or idpay
ZARINPAL_MERCHANT_ID = os.getenv('ZARINPAL_MERCHANT_ID', '')
PAYIR_API_KEY = os.getenv('PAYIR_API_KEY', '')
IDPAY_API_KEY = os.getenv('IDPAY_API_KEY', '')

# Trial Config Settings
TRIAL_DURATION_HOURS = int(os.getenv('TRIAL_DURATION_HOURS', '2'))
TRIAL_TRAFFIC_LIMIT = float(os.getenv('TRIAL_TRAFFIC_LIMIT', '1'))
TRIAL_TRAFFIC_UNIT = os.getenv('TRIAL_TRAFFIC_UNIT', TRAFFIC_UNIT_GB)

# Referral Commission
REFERRAL_COMMISSION_PERCENT = float(os.getenv('REFERRAL_COMMISSION_PERCENT', '10'))

# Admin IDs (comma-separated)
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]