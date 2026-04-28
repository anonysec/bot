# config.py
import os
from ..utils.helpers import convert_traffic
from ..utils.constants import TRAFFIC_UNIT_MB, TRAFFIC_UNIT_GB
import json

# Try to load from config.json first, fallback to environment variables
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')

def load_json_config():
    """Load configuration from JSON file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

json_config = load_json_config()

# Panel Configuration
PANEL_URL = json_config.get('panel_url') or os.getenv('PANEL_URL', 'https://your-panel-url')  # Use HTTPS
USERNAME = json_config.get('panel_username') or os.getenv('PANEL_USERNAME', 'admin')
PASSWORD = json_config.get('panel_password') or os.getenv('PANEL_PASSWORD', 'password')
PANEL_PROXY = json_config.get('panel_proxy') or os.getenv('PANEL_PROXY')  # e.g., 'http://proxy:port' or 'socks5://proxy:port'

# Telegram Configuration
TELEGRAM_BOT_TOKEN = json_config.get('telegram_bot_token') or os.getenv('TELEGRAM_BOT_TOKEN', 'your-bot-token')
TELEGRAM_PROXY = json_config.get('telegram_proxy') or os.getenv('TELEGRAM_PROXY')  # e.g., 'http://proxy:port' or 'socks5://proxy:port'

# Inbound ID
INBOUND_ID = json_config.get('inbound_id', 1) if json_config.get('inbound_id') is not None else int(os.getenv('INBOUND_ID', '1'))

# Plans - Support MB/GB mixed units
PLANS = {
    'basic': {'name': 'Basic (500MB)', 'traffic': 500, 'unit': TRAFFIC_UNIT_MB, 'price': 5, 'name_fa': 'پایه (500 مگ)', 'duration_days': 30},
    'standard': {'name': 'Standard (10GB)', 'traffic': 10, 'unit': TRAFFIC_UNIT_GB, 'price': 15, 'name_fa': 'استاندارد (10 گیگ)', 'duration_days': 30},
    'premium': {'name': 'Premium (50GB)', 'traffic': 50, 'unit': TRAFFIC_UNIT_GB, 'price': 20, 'name_fa': 'پریمیوم (50 گیگ)', 'duration_days': 30}
}

# Database
DATABASE_URL = json_config.get('database_url') or os.getenv('DATABASE_URL', 'sqlite:///vpn_bot.db')

# Web App
SECRET_KEY = json_config.get('secret_key') or os.getenv('SECRET_KEY', os.urandom(24).hex())  # Secure random key
WEB_HOST = json_config.get('web_host') or os.getenv('WEB_HOST', '0.0.0.0')
WEB_PORT = json_config.get('web_port', 5000) if json_config.get('web_port') is not None else int(os.getenv('WEB_PORT', '5000'))

# Traffic Alert Threshold (GB)
TRAFFIC_ALERT_GB = json_config.get('traffic_alert_gb', 1) if json_config.get('traffic_alert_gb') is not None else float(os.getenv('TRAFFIC_ALERT_GB', '1'))

# Software Links
SOFTWARE_LINKS = {
    'android': 'https://play.google.com/store/apps/details?id=com.v2ray.ang',
    'ios': 'https://apps.apple.com/app/v2box/id6446814690',
    'windows': 'https://github.com/2dust/v2rayN/releases',
    'mac': 'https://github.com/yanue/V2rayU/releases'
}

# Payment Gateways - Tetra only
PAYMENT_ENABLED = json_config.get('payment_enabled', True) if json_config.get('payment_enabled') is not None else os.getenv('PAYMENT_ENABLED', 'true').lower() == 'true'

# Tetra (https://tetra98.com/docs) - TON/TRON/Card to Card
TETRA_ENABLED = json_config.get('tetra_enabled', False) if json_config.get('tetra_enabled') is not None else os.getenv('TETRA_ENABLED', 'false').lower() == 'true'
TETRA_API_KEY = json_config.get('tetra_api_key') or os.getenv('TETRA_API_KEY', '')

# Legacy: Backward compatibility
PAYMENT_GATEWAY = os.getenv('PAYMENT_GATEWAY', '')  # Optional fallback

# Trial Config Settings
TRIAL_DURATION_HOURS = json_config.get('trial_duration_hours', 2) if json_config.get('trial_duration_hours') is not None else int(os.getenv('TRIAL_DURATION_HOURS', '2'))
TRIAL_TRAFFIC_LIMIT = json_config.get('trial_traffic_limit', 1) if json_config.get('trial_traffic_limit') is not None else float(os.getenv('TRIAL_TRAFFIC_LIMIT', '1'))
TRIAL_TRAFFIC_UNIT = json_config.get('trial_traffic_unit') or os.getenv('TRIAL_TRAFFIC_UNIT', TRAFFIC_UNIT_GB)

# Referral Commission
REFERRAL_COMMISSION_PERCENT = json_config.get('referral_commission_percent', 10) if json_config.get('referral_commission_percent') is not None else float(os.getenv('REFERRAL_COMMISSION_PERCENT', '10'))

# Admin IDs (comma-separated)
ADMIN_IDS = json_config.get('admin_ids', []) if json_config.get('admin_ids') else [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]