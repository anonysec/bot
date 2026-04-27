# 🚀 Complete Feature List and Implementation Guide

## ✅ Implemented Features

### 1. **Iranian Payment Gateways Integration**
- **Zarinpal** - Primary gateway with merchant ID support
- **Pay.ir** - Secondary gateway with API key
- **IDPay** - Alternative gateway with tracking

**Files**: `payment.py`

**Usage**:
```python
from payment import get_payment_gateway

gateway = get_payment_gateway('zarinpal', merchant_id='YOUR_MERCHANT_ID')
result = gateway.create_payment(amount=100, description="Config Purchase", callback_url="YOUR_URL")
# result = {'success': True, 'payment_url': '...', 'authority': '...'}
```

**Configuration**:
```env
PAYMENT_GATEWAY=zarinpal
ZARINPAL_MERCHANT_ID=your-merchant-id
```

---

### 2. **Trial/Test Config Feature**
- Free 2-hour test configs with 1GB limit
- Automatically expires after time limit
- Rate limited to 1 per day per user
- Marked as trial in database

**Files**: `bot.py`, `database.py`

**Features**:
- `/trial_config` command in bot menu
- Tracks trial usage
- Automatic expiry
- Separate from paid configs

---

### 3. **Wallet/Balance System**
- Track user credits and spending
- Referral earnings auto-credited
- Transaction history
- Balance display in web panel

**Database Model - Wallet**:
```python
class Wallet:
    user_id: int
    balance: float
    total_earned: float
    total_spent: float
```

**Functions**:
```python
from database import get_wallet, update_balance

wallet = get_wallet(db, user_id)
wallet = update_balance(db, user_id, amount=100)  # Add/subtract
```

---

### 4. **Backup/Restore Functionality**
- Export configs to JSON
- Store backups in database
- Download backup files
- Restore from previous backups

**Database Model - Backup**:
```python
class Backup:
    user_id: int
    config_data: str  # JSON string
    created_at: datetime
```

**Usage**:
```python
from database import create_backup, get_backups

create_backup(db, user_id, json_config_data)
backups = get_backups(db, user_id)
```

---

### 5. **Admin Panel (Web + Bot)**
- **Web Dashboard**: Statistics, payments, users
- **Analytics**: Total revenue, active users, subscriptions
- **Payment Management**: View recent transactions
- **Bot Commands**: `/admin` command for admins

**Admin Routes**:
- `/admin` - Dashboard
- `/api/user-stats` - API for stats

**Admin Features**:
- User count
- Revenue tracking
- Payment history
- Subscription analytics

**Configuration**:
```env
ADMIN_IDS=123456789,987654321
```

---

### 6. **Rate Limiting**
- Prevents spam and abuse
- Configurable limits per action
- Time-window based (default 60 minutes)
- Actions tracked: buy_config, trial_config, etc.

**Database Model - RateLimit**:
```python
class RateLimit:
    user_id: int
    action: str
    timestamp: datetime
```

**Usage**:
```python
from database import check_rate_limit, record_action

if check_rate_limit(db, user_id, 'buy_config', max_attempts=10):
    # Proceed with action
    record_action(db, user_id, 'buy_config')
```

---

### 7. **Referral System**
- Unique referral code per user
- 10% commission on referred purchases
- Auto-credit to wallet
- Track referrals in database

**Database Model - Referral**:
```python
class Referral:
    referrer_id: int
    referred_user_id: int
    commission: float
    created_at: datetime
```

**Features**:
- 🤝 Referral menu in bot
- Share referral code
- View referrals made
- Auto-commission calculation

**Configuration**:
```env
REFERRAL_COMMISSION_PERCENT=10
```

---

### 8. **Traffic Alerts**
- Hourly traffic checking
- Alert when below threshold (default 1GB)
- Automatic Telegram notifications
- Configurable threshold

**Features**:
- Monitors subscription traffic
- Sends alerts via Telegram
- Updates usage statistics
- Runs in background scheduler

**Configuration**:
```env
TRAFFIC_ALERT_GB=1
```

---

### 9. **Giveaway System**
- Admin create free configs
- Limited time availability
- Track giveaway usage
- Generate codes for distribution

**Database Model - Giveaway**:
```python
class Giveaway:
    user_id: int  # Admin who created
    plan: str
    client_id: str
    expiry_date: datetime
    used: bool
```

**Usage**:
```python
# Admin creates giveaway
# Users can redeem with code
```

---

### 10. **Enhanced Web UI with Bootstrap 5**
- Modern responsive design
- Dark/light theme support
- Mobile optimized
- Real-time statistics

**Components**:
- Dashboard with stats cards
- Configs table with progress bars
- Login page with gradient
- Admin analytics
- Backup management interface

**Features**:
- Glassmorphism design
- Smooth animations
- Progress indicators
- Responsive tables

---

### 11. **Better Web Management**
- **Dashboard**: User stats and quick actions
- **Configs**: Detailed usage tracking
- **Backup**: Backup creation and restore
- **Admin Panel**: Analytics and management

**Pages**:
- `/` - Dashboard (home)
- `/login` - Login
- `/configs` - View configs
- `/backup` - Backup management
- `/admin` - Admin dashboard (admin only)
- `/api/user-stats` - API endpoint

---

### 12. **QR Code Support**
- Automatic QR generation from configs
- Scannable with VPN apps
- Sent via Telegram with config

**Features**:
- One-step config import
- No manual copying needed
- Photo attachment in Telegram

---

### 13. **Multi-Protocol Support**
- VLESS
- VMess
- Trojan
- Shadowsocks

**From 3x-ui API**:
- Automatic config generation
- Protocol-specific settings
- Subscription endpoints

---

### 14. **Proxy Support (HTTP/SOCKS5)**
- Panel API proxying
- Telegram API proxying
- Bypass Iran GFW
- Multiple proxy formats

**Configuration**:
```env
PANEL_PROXY=socks5://proxy:1080
TELEGRAM_PROXY=http://proxy:8080
```

---

### 15. **Software Links**
- Download links for all platforms
- Android: V2RayNG
- iOS: V2Box
- Windows: v2rayN
- Mac: V2rayU

**Sent automatically** after config delivery

---

## Database Schema

### Users Table
```python
id, telegram_id, email, language, is_reseller, is_admin
is_active, referral_code, referred_by, created_at
```

### Subscriptions Table
```python
id, user_id, client_id, plan, total_gb, used_gb
expiry_date, is_trial, created_at
```

### Payments Table
```python
id, user_id, amount, status, gateway
transaction_id, created_at
```

### Wallet Table
```python
id, user_id, balance, total_earned, total_spent, updated_at
```

### Referral Table
```python
id, referrer_id, referred_user_id, commission, created_at
```

### RateLimit Table
```python
id, user_id, action, timestamp
```

### Backup Table
```python
id, user_id, config_data, created_at
```

### Giveaway Table
```python
id, user_id, plan, client_id, expiry_date, used, created_at
```

---

## Configuration Overview

See `.env.example` for complete list:

```env
# Core
PANEL_URL, PANEL_USERNAME, PANEL_PASSWORD
TELEGRAM_BOT_TOKEN, INBOUND_ID

# Proxies
PANEL_PROXY, TELEGRAM_PROXY

# Payment
PAYMENT_GATEWAY, ZARINPAL_MERCHANT_ID (or PAYIR_API_KEY or IDPAY_API_KEY)

# Security
SECRET_KEY, ADMIN_IDS

# Features
TRIAL_DURATION_HOURS, TRIAL_GB_LIMIT
REFERRAL_COMMISSION_PERCENT
TRAFFIC_ALERT_GB
```

---

## Usage Examples

### Create a trial config
```python
client_id = panel.add_client(
    inbound_id=1,
    email="trial_user@test.com",
    total_gb=1*1024**3,
    expiry_time=unix_timestamp_2h_from_now
)
```

### Process a payment
```python
gateway = get_payment_gateway('zarinpal', merchant_id=MERCHANT_ID)
payment_result = gateway.create_payment(amount=50, callback_url="...")
verify_result = gateway.verify_payment(authority, amount=50)
```

### Handle referral
```python
referrer = get_user_by_referral_code(db, referral_code)
new_user = create_user(db, telegram_id, email, referral_code=referral_code)
create_referral(db, referrer.id, new_user.id, commission=0)
```

### Alert on traffic
```python
remaining = panel.get_client_traffic(email)
if remaining <= TRAFFIC_ALERT_GB:
    await bot.send_message(chat_id, "Low traffic!")
```

---

## Performance Considerations

- **Database**: SQLite default (upgradable to PostgreSQL)
- **Scheduler**: Runs hourly checks (configurable)
- **Rate Limiting**: In-memory tracking with database persistence
- **Web**: Flask development server (use Gunicorn for production)

---

## Security Considerations

✅ Implemented:
- Input validation (email format)
- Environment variable secrets
- Rate limiting
- Admin ID verification
- HTTPS support for panel

⚠️ Recommendations:
- Use HTTPS for web app (reverse proxy)
- Implement TLS for database
- Rotate secrets regularly
- Monitor admin activities
- Use strong panel credentials

---

## Troubleshooting

### Payment Gateway Errors
- Verify API credentials
- Check merchant/API key format
- Test callback URL accessibility

### Trial Config Not Creating
- Check rate limit hasn't been exceeded
- Verify TRIAL_DURATION_HOURS setting
- Check panel authentication

### Referral Not Working
- Verify referral code exists
- Check user creation order
- Verify commission percentage

### Admin Panel Not Accessible
- Verify telegram_id in ADMIN_IDS
- Check database connection
- Verify web.py is running

---

## Future Enhancements

Possible additions:
- Auto-renewal notifications
- Advanced usage analytics
- Custom plan creation
- API for third-party integration
- Mobile app native version
- Subscription tiers for resellers
- White-label options