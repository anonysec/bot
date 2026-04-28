# config.py - JSON-only configuration
import os
from ..utils.helpers import convert_traffic
from ..utils.constants import TRAFFIC_UNIT_MB, TRAFFIC_UNIT_GB
import json

# Global config file path - can be overridden
_config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')

def set_config_file(config_file):
    """Set the configuration file path"""
    global _config_file
    _config_file = config_file

def load_json_config():
    """Load configuration from JSON file"""
    if os.path.exists(_config_file):
        try:
            with open(_config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

json_config = load_json_config()

# Panel Configuration - Support multiple panels
PANELS = json_config.get('panels', [])
if not PANELS:
    # Default single panel configuration
    PANELS = [{
        'id': 'default',
        'url': 'https://your-panel-url',
        'username': 'admin',
        'password': 'password',
        'proxy': '',
        'inbound_id': 1,
        'enabled': True
    }]

# For backward compatibility - use first enabled panel as default
DEFAULT_PANEL = next((p for p in PANELS if p.get('enabled', True)), PANELS[0]) if PANELS else None
PANEL_URL = DEFAULT_PANEL['url'] if DEFAULT_PANEL else 'https://your-panel-url'
USERNAME = DEFAULT_PANEL['username'] if DEFAULT_PANEL else 'admin'
PASSWORD = DEFAULT_PANEL['password'] if DEFAULT_PANEL else 'password'
PANEL_PROXY = DEFAULT_PANEL.get('proxy', '')
INBOUND_ID = DEFAULT_PANEL.get('inbound_id', 1)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = json_config.get('telegram_bot_token', 'your-bot-token')
TELEGRAM_PROXY = json_config.get('telegram_proxy', '')  # e.g., 'http://proxy:port' or 'socks5://proxy:port'

# Resellers Configuration - Each reseller can have their own payment settings
RESELLERS = json_config.get('resellers', [])

# Payment Configuration - Support per-reseller payments
PAYMENTS = json_config.get('payments', {})

# For backward compatibility - use global payment settings if no resellers defined
if not RESELLERS:
    RESELLERS = [{
        'id': 'default',
        'name': 'Default Reseller',
        'telegram_ids': json_config.get('admin_ids', []),
        'panels': [panel['id'] for panel in PANELS],
        'payments': {
            'tetra': {
                'enabled': json_config.get('tetra_enabled', False),
                'api_key': json_config.get('tetra_api_key', '')
            }
        },
        'enabled': True
    }]

# Global payment settings for backward compatibility
TETRA_ENABLED = PAYMENTS.get('tetra', {}).get('enabled', json_config.get('tetra_enabled', False))
TETRA_API_KEY = PAYMENTS.get('tetra', {}).get('api_key', json_config.get('tetra_api_key', ''))

# Database
DATABASE_URL = json_config.get('database_url', 'sqlite:///vpn_bot.db')

# Web App
SECRET_KEY = json_config.get('secret_key', os.urandom(24).hex())  # Secure random key
WEB_HOST = json_config.get('web_host', '0.0.0.0')
WEB_PORT = json_config.get('web_port', 5000)

# Traffic Alert Threshold (GB)
TRAFFIC_ALERT_GB = json_config.get('traffic_alert_gb', 1)

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
TETRA_ENABLED = json_config.get('tetra_enabled', False)
TETRA_API_KEY = json_config.get('tetra_api_key', '')

# Trial Config Settings - Modern defaults (25MB or 50MB for 1 hour)
TRIAL_DURATION_HOURS = json_config.get('trial_duration_hours', 1)  # 1 hour trial
TRIAL_TRAFFIC_LIMIT = json_config.get('trial_traffic_limit', 25)  # 25MB default
TRIAL_TRAFFIC_UNIT = json_config.get('trial_traffic_unit', TRAFFIC_UNIT_MB)  # Use MB
TRIAL_OPTIONS = json_config.get('trial_options', ['25MB', '50MB'])  # User can choose

# Traffic Alert Settings - Percentage-based (since traffic is expensive)
TRAFFIC_ALERT_PERCENT = json_config.get('traffic_alert_percent', 80)  # Alert at 80% usage
TRAFFIC_CRITICAL_PERCENT = json_config.get('traffic_critical_percent', 95)  # Critical at 95%

# Referral Commission
REFERRAL_COMMISSION_PERCENT = json_config.get('referral_commission_percent', 10)

# Feature Flags
FEATURES = json_config.get('features', {
    'decoy_page': True,
    'referrals': True,
    'backups': True,
    'traffic_monitor': True,
    'wallet': True,
    'stats': True
})

# Admin IDs
ADMIN_IDS = json_config.get('admin_ids', [])