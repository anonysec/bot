# web.py - Enhanced with Bootstrap and better management
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from ..core.config import SECRET_KEY, WEB_HOST, WEB_PORT, ADMIN_IDS, set_config_file, _config_file
from ..db.database import (SessionLocal, get_user_by_telegram_id, get_user_by_id, 
                      get_user_subscriptions, get_backups, Wallet, Payment, User, Subscription)
from functools import wraps
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = SECRET_KEY

CONFIG_FILE = _config_file

def load_config():
    """Load configuration from JSON file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'panel_url': '',
        'panel_username': '',
        'panel_password': '',
        'inbound_id': 1,
        'telegram_bot_token': '',
        'admin_ids': [],
        'tetra_enabled': False,
        'tetra_api_key': '',
        'payment_enabled': True,
        'trial_duration_hours': 1,
        'trial_traffic_limit': 25,
        'trial_traffic_unit': 'MB',
        'trial_options': ['25MB', '50MB'],
        'traffic_alert_percent': 80,
        'traffic_critical_percent': 95,
        'referral_commission_percent': 10,
        'panel_proxy': '',
        'telegram_proxy': '',
        'web_host': '0.0.0.0',
        'web_port': 5000,
        'database_url': 'sqlite:///vpn_bot.db',
        'secret_key': os.urandom(24).hex(),
        'features': {
            'decoy_page': True,
            'referrals': True,
            'backups': True,
            'traffic_monitor': True,
            'wallet': True,
            'stats': True
        }
    }

def get_traffic_percentage(used_gb, total_gb):
    """Calculate traffic usage percentage"""
    if total_gb <= 0:
        return 0
    return (used_gb / total_gb) * 100

def get_traffic_status(percentage):
    """Get traffic status based on percentage"""
    if percentage >= 95:
        return {'status': 'critical', 'color': 'danger', 'message': 'Critical: 95% traffic used!'}
    elif percentage >= 80:
        return {'status': 'warning', 'color': 'warning', 'message': 'Warning: 80% traffic used.'}
    else:
        return {'status': 'normal', 'color': 'success', 'message': 'Normal'}

def save_config(config):
    """Save configuration to JSON file"""
    if 'secret_key' not in config or not config['secret_key']:
        config['secret_key'] = os.urandom(24).hex()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def setup_required():
    """Check if setup is required"""
    config = load_config()
    return not config.get('panel_url') or not config.get('telegram_bot_token')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('telegram_id') not in ADMIN_IDS:
            flash('Admin access required')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if setup_required():
        return redirect(url_for('setup'))
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = SessionLocal()
    user = get_user_by_id(db, session['user_id'])
    subs = get_user_subscriptions(db, session['user_id'])
    wallet = db.query(Wallet).filter_by(user_id=session['user_id']).first()
    db.close()
    return render_template('dashboard.html', user=user, subscriptions=subs, wallet=wallet)

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        # Handle multiple panels
        panels = []
        panel_count = int(request.form.get('panel_count', 1))
        
        for i in range(panel_count):
            panel = {
                'id': request.form.get(f'panel_{i}_id', f'panel_{i+1}'),
                'url': request.form.get(f'panel_{i}_url', ''),
                'username': request.form.get(f'panel_{i}_username', ''),
                'password': request.form.get(f'panel_{i}_password', ''),
                'inbound_id': int(request.form.get(f'panel_{i}_inbound_id', 1)),
                'proxy': request.form.get(f'panel_{i}_proxy', ''),
                'enabled': request.form.get(f'panel_{i}_enabled') == 'on'
            }
            if panel['url']:  # Only add panels with URLs
                panels.append(panel)
        
        # Handle resellers
        resellers = []
        reseller_count = int(request.form.get('reseller_count', 1))
        
        for i in range(reseller_count):
            reseller = {
                'id': request.form.get(f'reseller_{i}_id', f'reseller_{i+1}'),
                'name': request.form.get(f'reseller_{i}_name', ''),
                'telegram_ids': [int(x.strip()) for x in request.form.get(f'reseller_{i}_telegram_ids', '').split(',') if x.strip()],
                'panels': request.form.getlist(f'reseller_{i}_panels'),
                'payments': {
                    'tetra': {
                        'enabled': request.form.get(f'reseller_{i}_tetra_enabled') == 'on',
                        'api_key': request.form.get(f'reseller_{i}_tetra_api_key', '')
                    }
                },
                'enabled': request.form.get(f'reseller_{i}_enabled') == 'on'
            }
            if reseller['name']:  # Only add resellers with names
                resellers.append(reseller)
        
        config = {
            'panels': panels,
            'resellers': resellers,
            'telegram_bot_token': request.form.get('telegram_bot_token', ''),
            'payment_enabled': request.form.get('payment_enabled') == 'on',
            'trial_duration_hours': int(request.form.get('trial_duration_hours', 2)),
            'trial_traffic_limit': float(request.form.get('trial_traffic_limit', 1)),
            'trial_traffic_unit': request.form.get('trial_traffic_unit', 'GB'),
            'traffic_alert_gb': float(request.form.get('traffic_alert_gb', 1)),
            'referral_commission_percent': float(request.form.get('referral_commission_percent', 10)),
            'telegram_proxy': request.form.get('telegram_proxy', ''),
            'web_host': request.form.get('web_host', '0.0.0.0'),
            'web_port': int(request.form.get('web_port', 5000)),
            'database_url': request.form.get('database_url', 'sqlite:///vpn_bot.db')
        }
        save_config(config)
        flash('Configuration saved successfully! Please restart the bot.')
        return redirect(url_for('setup'))

    config = load_config()
    return render_template('setup.html', config=config)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if setup_required():
        return redirect(url_for('setup'))
    if request.method == 'POST':
        telegram_id = request.form.get('telegram_id', '')
        try:
            telegram_id = int(telegram_id)
            db = SessionLocal()
            user = get_user_by_telegram_id(db, telegram_id)
            db.close()
            if user:
                session['user_id'] = user.id
                session['telegram_id'] = user.telegram_id
                session['is_admin'] = user.is_admin
                return redirect(url_for('index'))
            flash('Invalid Telegram ID')
        except ValueError:
            flash('Telegram ID must be a number')
    return render_template('login.html')

@app.route('/configs')
@login_required
def configs():
    db = SessionLocal()
    subs = get_user_subscriptions(db, session['user_id'])
    db.close()
    return render_template('configs.html', subscriptions=subs)

@app.route('/backup')
@login_required
def backup():
    db = SessionLocal()
    backups = get_backups(db, session['user_id'])
    db.close()
    return render_template('backup.html', backups=backups)

@app.route('/admin')
@admin_required
def admin():
    db = SessionLocal()
    total_users = db.query(User).count()
    total_revenue = db.query(Payment).filter(Payment.status == 'completed').\
        with_entities(db.func.sum(Payment.amount)).scalar() or 0
    total_subs = db.query(Subscription).count()
    active_subs = db.query(Subscription).filter(Subscription.expiry_date > datetime.utcnow()).count()
    recent_payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(10).all()
    db.close()
    return render_template('admin.html', 
                          total_users=total_users, 
                          total_revenue=total_revenue,
                          total_subs=total_subs,
                          active_subs=active_subs,
                          recent_payments=recent_payments)

@app.route('/api/user-stats')
@login_required
def user_stats():
    db = SessionLocal()
    subs = get_user_subscriptions(db, session['user_id'])
    wallet = db.query(Wallet).filter_by(user_id=session['user_id']).first()
    db.close()
    return jsonify({
        'total_configs': len(subs),
        'total_traffic': sum(s.total_gb for s in subs),
        'used_traffic': sum(s.used_gb for s in subs),
        'balance': wallet.balance if wallet else 0
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# New Routes for 3x-ui Style Interface

@app.route('/decoy')
def decoy():
    """Fake landing page for privacy"""
    config = load_config()
    if not config.get('features', {}).get('decoy_page', True):
        return redirect(url_for('login'))
    return render_template('decoy.html')

@app.route('/dashboard')
def dashboard_modern():
    """Modern 3x-ui style dashboard"""
    if setup_required():
        return redirect(url_for('setup'))
    if 'user_id' not in session:
        return redirect(url_for('decoy'))
    
    db = SessionLocal()
    user = get_user_by_id(db, session['user_id'])
    subs = get_user_subscriptions(db, session['user_id'])
    wallet = db.query(Wallet).filter_by(user_id=session['user_id']).first()
    
    # Calculate total traffic with percentage
    total_traffic = sum(s.total_gb for s in subs)
    used_traffic = sum(s.used_gb for s in subs)
    
    # Add percentage calculation to each subscription
    for sub in subs:
        sub.usage_percent = get_traffic_percentage(sub.used_gb, sub.total_gb)
        sub.traffic_status = get_traffic_status(sub.usage_percent)
    
    db.close()
    return render_template('dashboard_modern.html', 
                          user=user, 
                          subscriptions=subs, 
                          wallet=wallet,
                          total_traffic=total_traffic,
                          used_traffic=used_traffic)

@app.route('/subscriptions')
def subscriptions_modern():
    """Modern subscription page with 3x-ui style"""
    if setup_required():
        return redirect(url_for('setup'))
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    config = load_config()
    return render_template('subscriptions_modern.html', config=config)

@app.route('/api/traffic-alert', methods=['GET'])
@login_required
def traffic_alert():
    """API endpoint to check traffic alerts"""
    config = load_config()
    alert_percent = config.get('traffic_alert_percent', 80)
    critical_percent = config.get('traffic_critical_percent', 95)
    
    db = SessionLocal()
    subs = get_user_subscriptions(db, session['user_id'])
    
    alerts = []
    for sub in subs:
        percentage = get_traffic_percentage(sub.used_gb, sub.total_gb)
        if percentage >= critical_percent:
            alerts.append({
                'type': 'critical',
                'plan': sub.plan,
                'percentage': round(percentage, 2),
                'message': f'Critical: Your {sub.plan} plan is {percentage:.1f}% full!'
            })
        elif percentage >= alert_percent:
            alerts.append({
                'type': 'warning',
                'plan': sub.plan,
                'percentage': round(percentage, 2),
                'message': f'Warning: Your {sub.plan} plan is {percentage:.1f}% full!'
            })
    
    db.close()
    return jsonify({'alerts': alerts, 'has_alerts': len(alerts) > 0})

if __name__ == '__main__':
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False)