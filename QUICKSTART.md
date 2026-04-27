# 🚀 Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Configuration File
```bash
cp .env.example .env
```

### 3. Edit `.env` with Your Settings

#### Minimum Required:
```env
# 3x-ui Panel
PANEL_URL=https://your-3xui-panel.com
PANEL_USERNAME=admin
PANEL_PASSWORD=your_password
INBOUND_ID=1

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
```

#### Add Payment Gateway (Iran):
```env
# Option 1: Zarinpal
PAYMENT_GATEWAY=zarinpal
ZARINPAL_MERCHANT_ID=your_merchant_id

# Option 2: Pay.ir
# PAYMENT_GATEWAY=payir
# PAYIR_API_KEY=your_api_key

# Option 3: IDPay
# PAYMENT_GATEWAY=idpay
# IDPAY_API_KEY=your_api_key
```

#### Admin Access:
```env
ADMIN_IDS=YOUR_TELEGRAM_ID,ANOTHER_ADMIN_ID
```

#### Optional (For Iran/Restricted Networks):
```env
PANEL_PROXY=socks5://proxy_ip:port
TELEGRAM_PROXY=socks5://proxy_ip:port
```

### 4. Run the Application

**Option A - Everything Together**:
```bash
python main.py
```

**Option B - Separate Components**:
```bash
# Terminal 1 - Bot
python bot.py

# Terminal 2 - Web Dashboard
python web.py

# Terminal 3 - Scheduler (optional)
python scheduler.py
```

### 5. Access Applications

- **Telegram Bot**: Contact your bot with `/start`
- **Web Dashboard**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin (requires admin ID)

---

## Testing

### Test Telegram Bot
1. Send `/start` to your bot
2. Choose English or Persian (فارسی)
3. Click "Trial Config" to get a free test account
4. You should receive a config with QR code

### Test Web Panel
1. Open http://localhost:5000
2. Enter your Telegram user ID (use `/start` in any Telegram bot with /id command)
3. View your configs and wallet

### Test Admin Panel
1. Set your Telegram ID in `ADMIN_IDS`
2. Open http://localhost:5000/admin
3. View statistics and payments

---

## Common Configuration Issues

### Bot Not Responding
```bash
# Check token is correct
# Verify TELEGRAM_BOT_TOKEN in .env

# For Iran: Add proxy
TELEGRAM_PROXY=socks5://proxy:1080
```

### Cannot Connect to Panel
```bash
# Verify panel is running and URL is correct
# Check credentials
# If on Iran network:
PANEL_PROXY=socks5://proxy:1080
```

### Payment Gateway Errors
```bash
# Zarinpal: Get merchant ID from your Zarinpal account
# Pay.ir: Get API key from dashboard
# IDPay: Get API key from their console
```

---

## Customization

### Change Plans
Edit `config.py` or add to `.env`:

```python
# In config.py
PLANS = {
    'starter': {'name': 'Starter (5GB)', 'gb': 5, 'price': 3, ...},
    'pro': {'name': 'Pro (100GB)', 'gb': 100, 'price': 50, ...},
}
```

### Change Trial Settings
```env
TRIAL_DURATION_HOURS=4
TRIAL_GB_LIMIT=2
```

### Change Referral Commission
```env
REFERRAL_COMMISSION_PERCENT=15
```

### Add More Languages
Edit `bot.py` - look for language conditionals:
```python
if lang == 'en':
    # English text
elif lang == 'fa':
    # Persian text
elif lang == 'new_lang':
    # New language text
```

---

## Important Files to Know

| File | Purpose |
|------|---------|
| `bot.py` | Telegram bot logic |
| `web.py` | Web dashboard |
| `panel.py` | 3x-ui API integration |
| `database.py` | Database models |
| `payment.py` | Payment gateways |
| `scheduler.py` | Background tasks |
| `config.py` | Configuration |
| `templates/` | Web UI templates |

---

## Database

By default uses SQLite: `vpn_bot.db`

To use PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@localhost/vpndb
```

---

## Troubleshooting Commands

```bash
# Check if all modules import correctly
python -c "import config, bot, web, database, payment; print('✅ OK')"

# Test database connection
python -c "from database import SessionLocal; db = SessionLocal(); print('✅ DB Connected')"

# List all created tables
python -c "from database import Base; print([t.name for t in Base.metadata.tables.values()])"

# Check Telegram connection
python -c "from config import TELEGRAM_BOT_TOKEN; print(f'✅ Token: {TELEGRAM_BOT_TOKEN[:10]}...')"
```

---

## Next Steps

1. **Deploy to Server**: Use systemd, Docker, or screen
2. **Add Payment Callback**: Configure webhook for payment verification
3. **Customize Branding**: Edit templates for your brand
4. **Monitor**: Check logs and database regularly
5. **Backup**: Regular database backups recommended

---

## Production Deployment

### Using Systemd (Ubuntu/Linux)

Create `/etc/systemd/system/vpn-bot.service`:
```ini
[Unit]
Description=VPN Bot Service
After=network.target

[Service]
Type=simple
User=vpnbot
WorkingDirectory=/home/vpnbot/bot
ExecStart=/usr/bin/python3 /home/vpnbot/bot/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable vpn-bot
sudo systemctl start vpn-bot
sudo systemctl status vpn-bot
```

### Using Docker

Coming soon - Dockerfile template

### Using Gunicorn (Web)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web:app
```

---

## Security Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Use strong panel password
- [ ] Enable HTTPS for web app (reverse proxy)
- [ ] Set admin IDs only to trusted users
- [ ] Regularly update dependencies
- [ ] Monitor admin access logs
- [ ] Backup database regularly
- [ ] Use unique referral codes

---

## Support & Help

- Check `FEATURES.md` for detailed feature documentation
- Read `README.md` for full documentation
- Check logs: `python main.py 2>&1 | tee bot.log`
- Review database: Use SQLite browser on `vpn_bot.db`

---

## Success! 🎉

If you see configs being purchased and appearing in the database, everything is working!

Next: Customize plans, add more languages, deploy to production.

Happy selling! 🚀