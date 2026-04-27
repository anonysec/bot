# admin_commands.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, get_user_by_telegram_id, get_user_by_id, User, Payment, Subscription, Referral
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    user = get_user_by_telegram_id(db, user_id)
    
    if not user or not user.is_admin:
        await update.message.reply_text("Access denied")
        db.close()
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Statistics", callback_data='admin_stats')],
        [InlineKeyboardButton("💳 Payments", callback_data='admin_payments')],
        [InlineKeyboardButton("👥 Users", callback_data='admin_users')],
        [InlineKeyboardButton("🎁 Create Giveaway", callback_data='admin_giveaway')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Admin Panel", reply_markup=reply_markup)
    db.close()

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = SessionLocal()
    
    total_users = db.query(User).count()
    total_payments = db.query(Payment).filter(Payment.status == 'completed').count()
    total_revenue = db.query(Payment).filter(Payment.status == 'completed').with_entities(db.func.sum(Payment.amount)).scalar() or 0
    total_subs = db.query(Subscription).count()
    
    stats_text = f"""
📊 **Statistics**
- Total Users: {total_users}
- Total Subscriptions: {total_subs}
- Completed Payments: {total_payments}
- Total Revenue: ${total_revenue:.2f}
"""
    await query.edit_message_text(stats_text)
    db.close()

async def admin_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = SessionLocal()
    
    recent_payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(10).all()
    text = "💳 Recent Payments:\n"
    for p in recent_payments:
        user = get_user_by_id(db, p.user_id)
        text += f"\n- User: {user.email if user else 'Unknown'}\n  Amount: ${p.amount}\n  Status: {p.status}\n  Gateway: {p.gateway}"
    
    await query.edit_message_text(text)
    db.close()

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = SessionLocal()
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    resellers = db.query(User).filter(User.is_reseller == True).count()
    
    text = f"""
👥 **User Management**
- Total Users: {total_users}
- Active Users: {active_users}
- Resellers: {resellers}
"""
    await query.edit_message_text(text)
    db.close()

async def admin_create_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    user = get_user_by_telegram_id(db, user_id)
    
    if not user or not user.is_admin:
        await update.message.reply_text("Access denied")
        db.close()
        return
    
    await update.message.reply_text("Create Giveaway - Enter plan name (basic/premium)")
    context.user_data['waiting_for_giveaway_plan'] = True
    db.close()