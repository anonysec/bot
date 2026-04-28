# 🌐 VPN Selling Bot for 3x-ui Panel

A complete Telegram bot + web panel for selling VPN configs with multi-panel management, per-reseller payments, Tetra gateway (TON/TRON/Card to Card), referrals, traffic alerts, backups, and admin management.

## ✨ What’s Included

- **Multi-Panel Management** - Single bot managing multiple 3x-ui panels simultaneously
- **Per-Reseller Payments** - Each reseller has their own Tetra payment gateway configuration- **3x-ui Style Web Interface** - Modern, professional dashboard with dark theme
- **Modern Subscription Pages** - Beautiful pricing cards with trial options (25MB/50MB for 1h)
- **Decoy Landing Page** - Fake legitimate VPN site to mask bot purpose
- **Percentage-Based Alerts** - Traffic alerts at 80% and critical at 95% usage- Telegram bot for config purchase, trial access, referrals, wallet, and backups
- Flask web dashboard with setup wizard for easy configuration
- 3x-ui panel integration with proxy support
- Tetra payment gateway (TON/TRON/Card to Card payments)
- Flexible traffic plans with MB/GB support
- Traffic alerting and leak protection
- Psiphon abuse detection and prevention
- Admin/reseller management with isolated access
- Backup and restore functionality
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

Use the advanced TUI (x-ui style interface):
```bash
python bot.py tui
```

This provides a comprehensive menu-driven interface with:
- 📊 System Status monitoring
- ⚙️ Configuration management
- 🔧 Panel management tools
- 👥 User administration
- 🚀 Bot control (start/stop/restart)

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

**JSON Configuration Only (No .env support)**

This bot uses JSON configuration exclusively. Use the web setup wizard to configure everything:

```bash
python bot.py setup
```
Then open http://localhost:5000/setup in your browser to configure multiple panels and resellers.

**Configuration Structure:**
```json
{
  "panels": [
    {
      "id": "panel1",
      "url": "https://panel1.example.com",
      "username": "admin",
      "password": "password123",
      "inbound_id": 1,
      "proxy": "",
      "enabled": true
    }
  ],
  "resellers": [
    {
      "id": "reseller1",
      "name": "Reseller One",
      "telegram_ids": [123456789],
      "panels": ["panel1"],
      "payments": {
        "tetra": {
          "enabled": true,
          "api_key": "tetra_key_for_reseller"
        }
      },
      "enabled": true
    }
  ],
  "telegram_bot_token": "your-bot-token",
  "payment_enabled": true,
  "trial_duration_hours": 2,
  "trial_traffic_limit": 1,
  "trial_traffic_unit": "GB"
}
```

## 🏢 Multi-Panel & Multi-Reseller Management

This bot supports managing multiple 3x-ui panels simultaneously, with each reseller having their own payment gateway configuration.

### Configuration Structure

The new configuration supports multiple panels and resellers:

```json
{
  "panels": [
    {
      "id": "panel1",
      "url": "https://panel1.example.com",
      "username": "admin",
      "password": "password123",
      "inbound_id": 1,
      "proxy": "socks5://proxy:1080",
      "enabled": true
    },
    {
      "id": "panel2", 
      "url": "https://panel2.example.com",
      "username": "admin",
      "password": "password456",
      "inbound_id": 1,
      "enabled": true
    }
  ],
  "resellers": [
    {
      "id": "reseller1",
      "name": "Reseller One",
      "telegram_ids": [123456789, 987654321],
      "panels": ["panel1"],
      "payments": {
        "tetra": {
          "enabled": true,
          "api_key": "tetra_key_for_reseller1"
        }
      },
      "enabled": true
    },
    {
      "id": "reseller2",
      "name": "Reseller Two", 
      "telegram_ids": [111222333],
      "panels": ["panel2"],
      "payments": {
        "tetra": {
          "enabled": true,
          "api_key": "tetra_key_for_reseller2"
        }
      },
      "enabled": true
    }
  ],
  "telegram_bot_token": "your-bot-token",
  "payment_enabled": true,
  "trial_duration_hours": 2,
  "trial_traffic_limit": 1,
  "trial_traffic_unit": "GB"
}
```

### How It Works

- **Users are assigned to resellers** based on their `reseller_id` in the database
- **Each reseller has their own payment configuration** (separate Tetra API keys)
- **Resellers can access specific panels** as defined in their configuration
- **Load balancing** automatically distributes users across available panels
- **Per-reseller admin control** - each reseller only sees their own users and panels

### Running Multiple Resellers

Each reseller runs the same bot instance but with different configurations:

```bash
# All resellers use the same bot, but users are segregated by reseller_id
python bot.py start
```

The bot automatically:
- Routes users to their assigned reseller's panels
- Uses the correct payment gateway for each reseller
- Provides admin access only to the appropriate reseller admins

### Example Configuration

See `config.multi-panel-example.json` for a complete example configuration with multiple panels and resellers.

## 🎨 Web Interface

### Modern 3x-ui Style Design
The bot features a professional, modern web interface inspired by x-ui with:
- **Dark theme** with blue accent colors
- **3x-ui Dashboard** - Real-time stats, traffic monitoring, subscription overview
- **Modern Pricing Page** - Beautiful subscription cards with annual/monthly plans
- **Trial Options** - Users can choose between 25MB or 50MB for 1 hour free trial
- **Decoy Landing Page** - Fake legitimate VPN service to maintain privacy
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Real-time Alerts** - Percentage-based traffic warnings (80% and 95%)

### Web Interface Routes
- `/` or `/decoy` - Public landing page (decoy site)
- `/dashboard` - Modern 3x-ui style dashboard (requires login)
- `/subscriptions` - Beautiful subscription/pricing page
- `/configs` - Download VPN configurations
- `/backup` - Backup and restore settings
- `/admin` - Admin panel for reseller/admin users

### Features Included
- **Traffic Monitoring** - Real-time usage percentage tracking
- **Smart Alerts** - Notifications at 80% and 95% usage
- **One-Click Trial** - Quick-start 25MB or 50MB trials
- **Plan Comparison** - Feature comparison table
- **FAQ Section** - Common questions answered
- **Mobile Responsive** - Full mobile optimization

## 🧪 Trial Configuration

Trial settings are now optimized for affordability:
- **Duration**: 1 hour (down from 2 hours)
- **Data Options**: 
  - 25MB option (lighter use)
  - 50MB option (more generous)
- **No Card Required**: Instant access
- **Automatic Cleanup**: Trial configs automatically expire

## 📊 Traffic Alerts (Percentage-Based)

Since traffic is expensive, the system now uses percentage-based alerts:

```json
{
  "traffic_alert_percent": 80,      // Alert when user hits 80%
  "traffic_critical_percent": 95    // Critical warning at 95%
}
```

**Features:**
- Real-time percentage calculation
- Dynamic alert colors (yellow at 80%, red at 95%)
- API endpoint for alert checking
- Automatic subscription termination at limits

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

This project uses `config.json` exclusively for all configuration. The web setup wizard provides a complete interface for configuring:

- Multiple 3x-ui panels with different credentials
- Per-reseller payment gateway configurations
- Panel assignments and load balancing
- Admin access controls

**No .env support** - All configuration must be done through the web interface.

## 🛡️ Key Features

- **Multi-Panel Management** - Single bot managing multiple 3x-ui panels
- **Per-Reseller Payments** - Isolated payment configurations per reseller
- Telegram bot with purchase, trial, referral, wallet, and backup flows
- Web UI for setup, dashboards, and admin pages
- 3x-ui panel client creation and config delivery
- Tetra payment gateway for TON/TRON/Card to Card payments
- Traffic alerts and leak detection
- MB/GB plan support and flexible trial limits

## 🧠 Changelog Summary

- **3x-ui Web Interface** - Modern dark-themed dashboard with real-time traffic monitoring
- **Modern Subscription Pages** - Beautiful pricing cards and plan comparison
- **Decoy Landing Page** - Legitimate-looking VPN site for privacy
- **Trial Options** - Users choose 25MB or 50MB for 1 hour (updated from 2h/1GB)
- **Percentage-Based Alerts** - Traffic alerts at 80% and critical at 95% usage
- **Traffic API** - Real-time alert endpoint for percentage-based monitoring
- **JSON-Only Configuration** - Removed .env support, web setup is now the only configuration method
- **Advanced TUI** - Redesigned terminal interface to match x-ui style with comprehensive menus
- **Multi-Panel Management** - Single bot can now manage multiple 3x-ui panels simultaneously
- **Per-Reseller Payments** - Each reseller has isolated payment gateway configurations
- Migrated to a single unified `bot.py` manager script
- Added web-based setup wizard and JSON configuration support
- Added Tetra-only payment gateway support
- Added traffic limit enforcement and Psiphon prevention
- Added Nginx deployment template and MIT license

## 🚩 Notes

- `bot.py` is the unified launcher for all operations
- Use `python bot.py setup` to configure everything via web UI (no .env support)
- Use `python bot.py start` to launch bot + web panel
- Use `python bot.py stop` to stop the background process
- Use `python bot.py status` to check whether the bot is running
- Use `python bot.py tui` for advanced x-ui style terminal interface
- Configuration is stored exclusively in `config.json`

## 🔧 Troubleshooting

- **Multi-Panel Setup**: Ensure all panel URLs are accessible and credentials are correct
- **Single Panel**: Verify `panel_url`, `panel_username`, `panel_password`, and `inbound_id`
- **Telegram**: Verify `telegram_bot_token` and Telegram proxy settings
- **Web Setup**: Confirm the Flask port is free and accessible
- **Daemon Mode**: Check `bot.log` for startup issues
- **Payments**: Verify Tetra API keys are correct for each reseller

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
