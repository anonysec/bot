# web.py - Enhanced with Bootstrap and better management
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from ..core.config import SECRET_KEY, WEB_HOST, WEB_PORT, ADMIN_IDS
from ..db.database import (SessionLocal, get_user_by_telegram_id, get_user_by_id,
                      get_user_subscriptions, get_backups, Wallet, Payment, User, Subscription)
from functools import wraps
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = SECRET_KEY

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')

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
        'trial_duration_hours': 2,
        'trial_traffic_limit': 1,
        'trial_traffic_unit': 'GB',
        'traffic_alert_gb': 1,
        'referral_commission_percent': 10,
        'panel_proxy': '',
        'telegram_proxy': '',
        'web_host': '0.0.0.0',
        'web_port': 5000,
        'database_url': 'sqlite:///vpn_bot.db',
        'secret_key': os.urandom(24).hex()
    }

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
        config = {
            'panel_url': request.form.get('panel_url', ''),
            'panel_username': request.form.get('panel_username', ''),
            'panel_password': request.form.get('panel_password', ''),
            'inbound_id': int(request.form.get('inbound_id', 1)),
            'telegram_bot_token': request.form.get('telegram_bot_token', ''),
            'admin_ids': [int(x.strip()) for x in request.form.get('admin_ids', '').split(',') if x.strip()],
            'tetra_enabled': request.form.get('tetra_enabled') == 'on',
            'tetra_api_key': request.form.get('tetra_api_key', ''),
            'payment_enabled': request.form.get('payment_enabled') == 'on',
            'trial_duration_hours': int(request.form.get('trial_duration_hours', 2)),
            'trial_traffic_limit': float(request.form.get('trial_traffic_limit', 1)),
            'trial_traffic_unit': request.form.get('trial_traffic_unit', 'GB'),
            'traffic_alert_gb': float(request.form.get('traffic_alert_gb', 1)),
            'referral_commission_percent': float(request.form.get('referral_commission_percent', 10)),
            'panel_proxy': request.form.get('panel_proxy', ''),
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

if __name__ == '__main__':
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False)