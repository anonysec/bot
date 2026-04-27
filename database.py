# database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    email = Column(String, unique=True)
    language = Column(String, default='en')
    is_reseller = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    referral_code = Column(String, unique=True)
    referred_by = Column(Integer)  # user_id of referrer
    created_at = Column(DateTime, default=datetime.utcnow)

class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    balance = Column(Float, default=0)
    total_earned = Column(Float, default=0)
    total_spent = Column(Float, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float)
    status = Column(String, default='pending')  # pending, completed, failed
    gateway = Column(String)  # zarinpal, payir, idpay
    transaction_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    client_id = Column(String)
    plan = Column(String)
    total_gb = Column(Float)
    used_gb = Column(Float, default=0)
    expiry_date = Column(DateTime)
    is_trial = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Reseller(Base):
    __tablename__ = 'resellers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    commission_rate = Column(Float, default=0.1)

class Referral(Base):
    __tablename__ = 'referrals'
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer)
    referred_user_id = Column(Integer)
    commission = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Backup(Base):
    __tablename__ = 'backups'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    config_data = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class RateLimit(Base):
    __tablename__ = 'rate_limits'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String)  # buy_config, get_trial, etc
    timestamp = Column(DateTime, default=datetime.utcnow)

class Giveaway(Base):
    __tablename__ = 'giveaways'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    plan = Column(String)
    client_id = Column(String)
    expiry_date = Column(DateTime)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User functions
def create_user(db, telegram_id, email, language='en', referral_code=None):
    import uuid
    ref_code = referral_code or str(uuid.uuid4())[:8]
    user = User(telegram_id=telegram_id, email=email, language=language, referral_code=ref_code)
    db.add(user)
    db.commit()
    db.refresh(user)
    wallet = Wallet(user_id=user.id)
    db.add(wallet)
    db.commit()
    return user

def get_user_by_telegram_id(db, telegram_id):
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def get_user_by_id(db, user_id):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_referral_code(db, code):
    return db.query(User).filter(User.referral_code == code).first()

# Wallet functions
def get_wallet(db, user_id):
    return db.query(Wallet).filter(Wallet.user_id == user_id).first()

def update_balance(db, user_id, amount):
    wallet = get_wallet(db, user_id)
    if wallet:
        wallet.balance += amount
        if amount > 0:
            wallet.total_earned += amount
        else:
            wallet.total_spent += abs(amount)
        db.commit()
        return wallet
    return None

# Subscription functions
def create_subscription(db, user_id, client_id, plan, total_gb, expiry_date, is_trial=False):
    sub = Subscription(user_id=user_id, client_id=client_id, plan=plan, total_gb=total_gb, expiry_date=expiry_date, is_trial=is_trial)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

def get_user_subscriptions(db, user_id):
    return db.query(Subscription).filter(Subscription.user_id == user_id).all()

def update_subscription_traffic(db, client_id, used_gb):
    sub = db.query(Subscription).filter(Subscription.client_id == client_id).first()
    if sub:
        sub.used_gb = used_gb
        db.commit()
        return sub
    return None

# Payment functions
def create_payment(db, user_id, amount, gateway):
    payment = Payment(user_id=user_id, amount=amount, gateway=gateway)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def update_payment_status(db, payment_id, status, transaction_id=None):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment:
        payment.status = status
        if transaction_id:
            payment.transaction_id = transaction_id
        db.commit()
        return payment
    return None

# Rate limiting
def check_rate_limit(db, user_id, action, max_attempts=3, time_window_minutes=60):
    from datetime import timedelta
    cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
    recent_actions = db.query(RateLimit).filter(
        RateLimit.user_id == user_id,
        RateLimit.action == action,
        RateLimit.timestamp > cutoff_time
    ).count()
    return recent_actions < max_attempts

def record_action(db, user_id, action):
    rate_limit = RateLimit(user_id=user_id, action=action)
    db.add(rate_limit)
    db.commit()

# Referral functions
def create_referral(db, referrer_id, referred_user_id, commission=0):
    referral = Referral(referrer_id=referrer_id, referred_user_id=referred_user_id, commission=commission)
    db.add(referral)
    db.commit()
    return referral

def get_referrals(db, referrer_id):
    return db.query(Referral).filter(Referral.referrer_id == referrer_id).all()

# Backup/Restore
def create_backup(db, user_id, config_data):
    backup = Backup(user_id=user_id, config_data=config_data)
    db.add(backup)
    db.commit()
    return backup

def get_backups(db, user_id):
    return db.query(Backup).filter(Backup.user_id == user_id).all()