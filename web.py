# web.py - Enhanced with Bootstrap and better management
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from config import SECRET_KEY, WEB_HOST, WEB_PORT, ADMIN_IDS
from database import (SessionLocal, get_user_by_telegram_id, get_user_by_id, 
                      get_user_subscriptions, get_backups, Wallet, Payment, User, Subscription)
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = SECRET_KEY

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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = SessionLocal()
    user = get_user_by_id(db, session['user_id'])
    subs = get_user_subscriptions(db, session['user_id'])
    wallet = db.query(Wallet).filter_by(user_id=session['user_id']).first()
    db.close()
    return render_template('dashboard.html', user=user, subscriptions=subs, wallet=wallet)

@app.route('/login', methods=['GET', 'POST'])
def login():
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