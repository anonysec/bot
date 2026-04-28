# 🌐 VPN Selling Bot for 3x-ui Panel

A complete Telegram bot + web panel for selling VPN configs with Tetra payment gateway (TON/TRON/Card to Card), referrals, traffic alerts, backups, and admin management.

## ✨ What’s Included

- Telegram bot for config purchase, trial access, referrals, wallet, and backups
- Flask web dashboard with setup wizard for easy configuration
- 3x-ui panel integration with proxy support
- Tetra payment gateway (TON/TRON/Card to Card payments)
- Flexible traffic plans with MB/GB support
- Traffic alerting and leak protection
- Psiphon abuse detection and prevention
- Admin/reseller management
- Backup and restore
- Single unified launcher for Linux and Windows
- Nginx configuration included

## 🚀 Installation

### Quick Start (Recommended)

1. **Download and setup:**
```bash
git clone <repository-url>
cd vpn-bot
python bot.py install
```

2. **Web-based setup:**
```bash
python bot.py setup
```
Then open http://localhost:5000/setup in your browser to configure everything.

3. **Start the bot:**
```bash
python bot.py start
```

### Alternative Installation

Use the interactive TUI:
```bash
python bot.py tui
```

This provides a menu-driven interface for all operations.

## ▶️ Start the Bot

Use the unified bot manager script:
```bash
python bot.py start
```

For interactive management:
```bash
python bot.py tui
```

## 📋 Configuration

Use the web setup wizard first to create `config.json`:
```bash
python bot.py setup
```

If you prefer environment variables, create `.env` from `.env.example` and set at least:
```env
PANEL_URL=https://your-panel.com
PANEL_USERNAME=admin
PANEL_PASSWORD=your-password
INBOUND_ID=1
TELEGRAM_BOT_TOKEN=your-bot-token
ADMIN_IDS=123456789
PAYMENT_GATEWAY=tetra
TETRA_API_KEY=your-tetra-api-key
TRIAL_TRAFFIC_LIMIT=1
TRIAL_TRAFFIC_UNIT=GB
TRAFFIC_ALERT_GB=1
```

### Proxy Settings
```env
PANEL_PROXY=socks5://proxy:1080
TELEGRAM_PROXY=socks5://proxy:1080
```

## 🧩 Bot Manager Script
- `bot.py` — Unified cross-platform installer/start/stop/status/TUI manager

## 🧠 Main Architecture

```
bot/
├── bot.py              # Unified cross-platform manager (install/start/stop/status/tui/setup)
├── nginx.conf          # Nginx configuration template
├── LICENSE             # MIT License
├── src/
│   ├── bot/            # Telegram bot logic
│   ├── web/            # Flask web application with setup wizard
│   ├── core/           # Config, panel, scheduler with Psiphon protection
│   ├── db/             # Database models and access
│   └── utils/          # Helpers and leak protection
├── backup/             # Backups storage
├── logs/               # Runtime logs
├── requirements.txt    # Python dependencies
└── .env.example        # Environment template (fallback)
```

## 💳 Payment Gateway

Tetra payment gateway supports multiple payment methods:
- TON cryptocurrency payments
- TRON cryptocurrency payments  
- Card to Card (bank transfer) payments

### Configuration

```env
# Enable/disable payment system
PAYMENT_ENABLED=true

# Tetra (https://tetra98.com/docs)
TETRA_ENABLED=true
TETRA_API_KEY=your-tetra-api-key
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
```cmd
python bot.py install
```
2. Edit `.env` if needed.
3. Start the bot:
```cmd
python bot.py start
```

## 🌍 Running on Linux/macOS

1. Install dependencies:
```bash
python bot.py install
```
2. Start the bot:
```bash
python bot.py start
```

Or use the interactive TUI:
```bash
python bot.py tui
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛡️ Security Features

- **Traffic Limit Enforcement**: Automatically terminates connections when traffic limits are reached
- **Psiphon Abuse Detection**: Automatically detects and disables clients showing suspicious behavior
- **Traffic Monitoring**: Real-time traffic tracking with alerts
- **Leak Protection**: Built-in VPN leak detection
- **Rate Limiting**: Nginx configuration includes rate limiting
- **Secure Headers**: Nginx config includes security headers

## 🛠️ Configuration Storage

This project prefers `config.json` for deployment and stores secrets there.
The `.env` file remains supported as a fallback for legacy deployments.

## 🛡️ Key Features

- Telegram bot with purchase, trial, referral, wallet, and backup flows
- Web UI for setup, dashboards, and admin pages
- 3x-ui panel client creation and config delivery
- Tetra payment gateway for TON/TRON/Card to Card payments
- Traffic alerts and leak detection
- MB/GB plan support and flexible trial limits

## 🧠 Changelog Summary

- Migrated to a single unified `bot.py` manager script
- Added web-based setup wizard and JSON configuration support
- Added Tetra-only payment gateway support
- Added traffic limit enforcement and Psiphon prevention
- Added Nginx deployment template and MIT license

## 🚩 Notes

- `bot.py` is the unified launcher for all operations
- Use `python bot.py setup` to configure the bot via web UI
- Use `python bot.py start` to launch bot + web panel
- Use `python bot.py stop` to stop the background process
- Use `python bot.py status` to check whether the bot is running
- Configuration is stored in `config.json` (preferred) or `.env` (fallback)

## 🔧 Troubleshooting

- Verify `panel_url`, `panel_username`, `panel_password`, and `inbound_id`
- Verify `telegram_bot_token` and Telegram proxy settings
- If the web setup fails, confirm the Flask port is free and accessible
- Check `bot.log` for startup issues when running in daemon mode

## 🔄 Scheduler Tasks

Runs every hour:
- Check traffic usage and terminate connections when limits exceeded
- Send alerts for low traffic
- Update subscription status

Runs every 2 hours:
- Check for Psiphon abuse patterns and disable suspicious clients

Runs every 6 hours:
- Check for VPN leaks and alert admins

Runs every 2 hours:
- Check for Psiphon abuse patterns and disable suspicious clients

Runs every 6 hours:
- Check for VPN leaks and alert admins
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
