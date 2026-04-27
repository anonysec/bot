# 🌐 VPN Selling Bot for 3x-ui Panel

A comprehensive Telegram bot with web control panel for managing and selling VPN configurations, featuring Iranian payment gateways, referral system, traffic alerts, and admin management.

## ✨ Features

- **Telegram Bot Interface** - Interactive menu for buying/selling VPN configs
- **Web Control Panel** - Dashboard for users to view configs, backups, and wallet
- **Payment Gateways** - Zarinpal, Pay.ir, IDPay (suitable for Iranian users)
- **Trial/Test Configs** - Configurable trial periods with MB/GB limits
- **Wallet System** - User balance tracking and credit management
- **Referral System** - Earn commissions by referring others (10% default)
- **Traffic Alerts** - Automatic alerts when traffic is low
- **Backup/Restore** - Users can backup and restore configurations
- **Admin Panel** - Analytics, payment management, user statistics
- **Rate Limiting** - Protection against spam and abuse
- **QR Codes** - Scannable config delivery
- **Multi-Language** - English and Persian support
- **Proxy Support** - HTTP and SOCKS5 for restricted networks
- **Leak Protection** - Automatic VPN leak detection and alerts
- **Flexible Traffic Plans** - Support for MB and GB based plans
- **TUI Installer** - Text-based installer for easy setup
- **Cross-Platform** - Works on Windows and Ubuntu

## 🚀 Installation

### Requirements
- Python 3.8+
- 3x-ui panel running and accessible
- Telegram Bot Token (from @BotFather)

### Quick Setup with TUI Installer

1. **Clone and Run Installer**:
```bash
git clone <your-repo>
cd bot
python scripts/install.py
```

The TUI installer will guide you through:
- Panel configuration
- Telegram bot setup
- Payment gateway configuration
- Traffic plan customization
- Admin user setup

2. **Alternative Manual Setup**:
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
```

### Start the Bot

```bash
./start.sh
```

Or manually:
```bash
cd src
python main.py
```

## 📁 Project Structure

```
bot/
├── src/
│   ├── bot/           # Telegram bot logic
│   ├── web/           # Flask web application
│   ├── core/          # Core modules (config, panel, scheduler)
│   ├── db/            # Database models and operations
│   └── utils/         # Utility functions and helpers
├── scripts/
│   └── install.py     # TUI installer
├── templates/         # HTML templates
├── backup/            # Database backups
├── logs/              # Application logs
├── start.sh           # Startup script
├── requirements.txt   # Python dependencies
└── README.md
```

```env
# Panel
PANEL_URL=https://your-panel.com
PANEL_USERNAME=admin
PANEL_PASSWORD=password

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# Payment Gateway (choose one)
PAYMENT_GATEWAY=zarinpal
ZARINPAL_MERCHANT_ID=your-merchant-id

# Admin IDs
ADMIN_IDS=123456789,987654321

# Trial Settings
TRIAL_DURATION_HOURS=2
TRIAL_GB_LIMIT=1
```

4. **Run Application**:
```bash
# Start everything (bot + web + scheduler)
python main.py

# Or run components separately
python bot.py           # Telegram bot
python web.py          # Web dashboard (port 5000)
python scheduler.py    # Traffic alerts
```

## 📚 Project Structure

```
bot/
├── bot.py              # Telegram bot logic
├── web.py              # Flask web app
├── panel.py            # 3x-ui API integration
├── database.py         # SQLAlchemy models
├── payment.py          # Payment gateway integration
├── scheduler.py        # Background tasks
├── config.py           # Configuration
├── main.py             # Entry point
├── admin_commands.py    # Admin commands
├── requirements.txt    # Dependencies
├── templates/          # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── configs.html
│   ├── backup.html
│   └── admin.html
└── static/             # CSS/JS files
```

## 🤖 Bot Commands

### User Commands
- `/start` - Initialize bot, choose language
- `/admin` - Admin panel (admins only)

### Bot Menu
- 💳 Buy Config - Purchase a VPN config
- 🎁 Trial Config - Get free 2-hour test config
- 📋 My Configs - View active subscriptions
- 💰 Wallet - Check balance
- 🤝 Referral - Share referral code
- 💾 Backup - Backup configurations

## 💳 Payment Gateways

### Zarinpal (Recommended for Iran)
```env
PAYMENT_GATEWAY=zarinpal
ZARINPAL_MERCHANT_ID=your-merchant-id
```

### Pay.ir
```env
PAYMENT_GATEWAY=payir
PAYIR_API_KEY=your-api-key
```

### IDPay
```env
PAYMENT_GATEWAY=idpay
IDPAY_API_KEY=your-api-key
```

## 📊 Admin Dashboard

Access at `http://localhost:5000` with admin Telegram ID:

- **Statistics** - Total users, revenue, subscriptions
- **Payments** - Recent transactions and status
- **Users** - Active users and resellers
- **Giveaways** - Create and manage free configs

## 🔒 Security Optimizations

- HTTPS for all panel communications
- Secure random secret keys
- Input validation and sanitization
- Environment variables for sensitive data
- Rate limiting on actions
- Password hashing in database
- CSRF protection in web app

## 🌐 Bypassing Iran GFW

- Use TLS-enabled protocols (VLESS, Trojan)
- Enable obfuscation in 3x-ui
- Configure CDN fronting (Cloudflare)
- Use alternative ports
- VMess with WebSocket/HTTP2

## 📱 Supported VPN Apps

- Android: [V2RayNG](https://play.google.com/store/apps/details?id=com.v2ray.ang)
- iOS: [V2Box](https://apps.apple.com/app/v2box/id6446814690)
- Windows: [v2rayN](https://github.com/2dust/v2rayN/releases)
- Mac: [V2rayU](https://github.com/yanue/V2rayU/releases)

## 💰 Pricing Plans

Default plans (customize in config.py):
- Basic: 10GB for $5 (30 days)
- Premium: 50GB for $20 (30 days)
- Trial: 1GB for 2 hours (free)

## 🤝 Referral System

- Users get unique referral code
- 10% commission on referred user purchases
- Automatic tracking and wallet updates

## ⚙️ Advanced Configuration

### Proxy Settings
For servers behind proxies (Iran):
```env
PANEL_PROXY=socks5://proxy:1080
TELEGRAM_PROXY=http://proxy:8080
```

### Database
SQLite by default:
```env
DATABASE_URL=sqlite:///vpn_bot.db
```

PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@localhost/vpn_bot
```

### Rate Limiting
- Buy config: 10 per hour per user
- Trial config: 1 per day per user

## 🐛 Troubleshooting

### Bot not responding
- Check TELEGRAM_BOT_TOKEN
- Verify telegram proxy settings
- Check internet connectivity

### Panel connection failed
- Verify PANEL_URL is correct
- Check authentication credentials
- Test PANEL_PROXY if using

### Payment gateway errors
- Verify merchant/API credentials
- Check callback URL configuration
- Review payment gateway logs

## 📝 Database Models

### User
- telegram_id, email, language
- is_reseller, is_admin, is_active
- referral_code, referred_by

### Subscription
- user_id, client_id, plan
- total_gb, used_gb
- expiry_date, is_trial

### Payment
- user_id, amount, status
- gateway, transaction_id

### Wallet
- user_id, balance
- total_earned, total_spent

### Referral
- referrer_id, referred_user_id
- commission, created_at

## 🔄 Scheduler Tasks

Runs every hour:
- Check traffic usage
- Send alerts for low traffic
- Update subscription status
- Process referral commissions

## 📖 API Documentation

### Web API

```
GET /api/user-stats
- Returns: total_configs, total_traffic, used_traffic, balance

GET /admin
- Requires: Admin ID
- Returns: Analytics dashboard
```

### Bot API

Integrated with 3x-ui REST API for:
- Client management
- Config generation
- Traffic tracking
- Protocol support

## 🚀 Deployment Options

### Docker
```dockerfile
# Coming soon
```

### Ubuntu/Linux
```bash
python3 main.py &
# Run in background with systemd or screen
```

### Windows
```cmd
python main.py
# Or create batch script
```

## 📄 License

MIT License - Feel free to modify and use

## 🤝 Support

- Telegram: [@support_bot](https://t.me/support_bot)
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## ⚠️ Disclaimer

This tool is for legitimate VPN service management only. Ensure compliance with local laws and regulations.

3. Run the bot:
   ```bash
   python vpn_bot.py
   ```

## Usage

- Start the bot with `/start`
- Click "Buy VPN Config"
- Enter your email
- Receive your VPN config

## Libraries Used

- `requests` - For HTTP API calls to 3x-ui
- `python-telegram-bot` - For Telegram bot functionality

## Security Notes

- Store credentials securely
- Use HTTPS for panel access
- Implement proper error handling and logging
- Consider rate limiting and user verification

## Customization

- Modify the bot to support different pricing plans
- Add payment integration (e.g., with Stripe, PayPal)
- Implement user management and config renewal
- Add support for multiple inbounds/protocols
