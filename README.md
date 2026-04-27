# 🌐 VPN Selling Bot for 3x-ui Panel

A complete Telegram bot + web panel for selling VPN configs with Iranian payment gateways, referrals, traffic alerts, backups, and admin management.

## ✨ What’s Included

- Telegram bot for config purchase, trial access, referrals, wallet, and backups
- Flask web dashboard for users and admin statistics
- 3x-ui panel integration with proxy support
- Optional payment gateways: Zarinpal, Pay.ir, IDPay, Tetra (enable/disable as needed)
- Flexible traffic plans with MB/GB support
- Traffic alerting and leak protection
- Admin/reseller management
- Backup and restore
- Single unified launcher for Linux and Windows

## ✅ One File for Docs
All documentation is now consolidated in this `README.md`.
The previous separate docs have been merged to reduce clutter.

## 🚀 Installation

### Requirements
- Python 3.8+
- 3x-ui panel running and accessible
- Telegram bot token from @BotFather

### Recommended Cross-Platform Setup

Use the project manager script:
```bash
python manage.py install
```

On Windows, you can also run:
```bat
install.bat
```

This will:
- create a `venv` environment
- install dependencies from `requirements.txt`
- create `.env` from `.env.example`

### Alternative Linux TUI Installer
If you want the text-based installer on Linux:
```bash
python scripts/install.py
```

## ▶️ Start the Bot

Use the manager script:
```bash
python manage.py start
```

On Windows:
```bat
start.bat
```

On Linux/macOS:
```bash
./start.sh
```

## 📋 Configuration

Create `.env` from `.env.example` and set at least:
```env
PANEL_URL=https://your-panel.com
PANEL_USERNAME=admin
PANEL_PASSWORD=your-password
INBOUND_ID=1
TELEGRAM_BOT_TOKEN=your-bot-token
ADMIN_IDS=123456789
PAYMENT_GATEWAY=zarinpal
ZARINPAL_MERCHANT_ID=your-merchant-id
TRIAL_TRAFFIC_LIMIT=1
TRIAL_TRAFFIC_UNIT=GB
TRAFFIC_ALERT_GB=1
```

### Optional proxy settings
```env
PANEL_PROXY=socks5://proxy:1080
TELEGRAM_PROXY=socks5://proxy:1080
```

## 🧩 Root Launcher Files
- `manage.py` — cross-platform installer/start manager
- `install.bat` — Windows install helper
- `start.bat` — Windows start helper
- `start.sh` — Linux/macOS start helper
- `scripts/install.py` — optional Linux TUI installer

## 🧠 Main Architecture

```
bot/
├── manage.py         # Cross-platform project manager
├── install.bat       # Windows install script
├── start.bat         # Windows start script
├── start.sh          # Linux/macOS start script
├── scripts/install.py # Linux TUI installer
├── src/
│   ├── bot/          # Telegram bot logic
│   ├── web/          # Flask web application
│   ├── core/         # Config, panel, scheduler
│   ├── db/           # Database models and access
│   └── utils/        # Helpers and leak protection
├── backup/           # Backups storage
├── logs/             # Runtime logs
├── requirements.txt  # Python dependencies
└── .env.example      # Environment template
```

## 💳 Payment Gateways (Optional)

Payment systems are **completely optional**. Enable only the gateways you need or disable all for test mode.

### Supported Gateways

| Gateway | Settings | Rate Limit |
|---------|----------|-----------|
| **Zarinpal** | Requires merchant ID | Best for Iran |
| **Pay.ir** | Requires API key | Alternative Iran |
| **IDPay** | Requires API key | Alternative Iran |
| **Tetra** | Requires merchant ID | Newer option |

### Configuration

Set `PAYMENT_ENABLED=true` to enable the feature, then enable individual gateways:

```env
# Enable/disable payment system
PAYMENT_ENABLED=true

# Zarinpal (optional)
ZARINPAL_ENABLED=true
ZARINPAL_MERCHANT_ID=your-merchant-id

# Pay.ir (optional)
PAYIR_ENABLED=false
PAYIR_API_KEY=

# IDPay (optional)
IDPAY_ENABLED=false
IDPAY_API_KEY=

# Tetra (optional, https://tetra98.com/docs)
TETRA_ENABLED=false
TETRA_API_KEY=
```

### Disabling Payments

To run without payments (test/free mode):
```env
PAYMENT_ENABLED=false
```

When payments are disabled:
- Users can still access trial configs
- Paid plans require email only (no payment)
- Admin can still create giveaways

## 🛠️ Running on Windows

1. Install dependencies:
```bat
install.bat
```
2. Edit `.env` if needed.
3. Start the bot:
```bat
start.bat
```

## 🌍 Running on Linux/macOS

1. Install dependencies:
```bash
python manage.py install
```
2. Start the bot:
```bash
python manage.py start
```

## 🚩 Notes

- `manage.py` is the recommended launcher for both platforms.
- `scripts/install.py` remains available as an optional TUI installer.
- `.env.example` now includes the unified trial traffic settings.

## 🛡️ Key Features

- Telegram bot with purchase, trial, referral, wallet, and backup flows
- Web UI for dashboards and admin pages
- 3x-ui panel client creation and config delivery
- Payment gateway integration for Iranian users
- Traffic alerts and leak detection
- MB/GB plan support and flexible trial limits
- All docs merged into this single README

## 🧠 Changelog Summary

- Documentation consolidated into `README.md`
- Added `manage.py` for install/start on all platforms
- Added `install.bat` and `start.bat` for Windows
- Added cross-platform scripting and simplified launch flow
- Improved `.env.example` with trial traffic unit support

## 📌 Next Steps

After install, edit `.env`, then run:
```bash
python manage.py start
```

If you want a text UI installer on Linux, use:
```bash
python scripts/install.py
```

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
