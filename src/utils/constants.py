# src/utils/constants.py - Constants used throughout the application

# Traffic Units
TRAFFIC_UNIT_BYTES = 'bytes'
TRAFFIC_UNIT_KB = 'kb'
TRAFFIC_UNIT_MB = 'mb'
TRAFFIC_UNIT_GB = 'gb'

# Conversion factors
KB_TO_BYTES = 1024
MB_TO_BYTES = 1024 * KB_TO_BYTES
GB_TO_BYTES = 1024 * MB_TO_BYTES

# Leak Protection URLs
LEAK_PROTECTION_URLS = {
    'dns': 'https://whoami.akamai.net/',
    'dns_test': 'https://dns.google/dns-query?name=whoami.akamai.net&type=TXT',
    'ipv6': 'https://ipv6.myexternalip.com/raw',
    'ipv4': 'https://api.ipify.org?format=json',
}

# Payment Status Codes
PAYMENT_STATUS_PENDING = 'pending'
PAYMENT_STATUS_COMPLETED = 'completed'
PAYMENT_STATUS_FAILED = 'failed'
PAYMENT_STATUS_CANCELLED = 'cancelled'

# Subscription Status
SUBSCRIPTION_STATUS_ACTIVE = 'active'
SUBSCRIPTION_STATUS_EXPIRED = 'expired'
SUBSCRIPTION_STATUS_SUSPENDED = 'suspended'
SUBSCRIPTION_STATUS_TRIAL = 'trial'

# Rate Limit Actions
RATE_LIMIT_BUY_CONFIG = 'buy_config'
RATE_LIMIT_TRIAL_CONFIG = 'trial_config'
RATE_LIMIT_LOGIN = 'login'

# Default Values
DEFAULT_LANGUAGE = 'en'
DEFAULT_TRIAL_HOURS = 2
DEFAULT_TRIAL_GB = 1
DEFAULT_TRIAL_MB = 1024
DEFAULT_REFERRAL_COMMISSION = 0.10
DEFAULT_TRAFFIC_ALERT_GB = 1
DEFAULT_RATE_LIMIT_TIMEOUT = 3600  # 1 hour

# Supported Languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'fa': 'فارسی',
    'ar': 'العربية'
}

# VPN Protocols
PROTOCOLS = {
    'vless': 'VLESS',
    'vmess': 'VMess',
    'trojan': 'Trojan',
    'shadowsocks': 'Shadowsocks',
}

# Admin Permissions
PERMISSION_VIEW_STATS = 'view_stats'
PERMISSION_MANAGE_USERS = 'manage_users'
PERMISSION_MANAGE_PAYMENTS = 'manage_payments'
PERMISSION_CREATE_GIVEAWAY = 'create_giveaway'
PERMISSION_VIEW_LOGS = 'view_logs'