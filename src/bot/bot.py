# bot.py - Enhanced with all new features
import asyncio
import re
import json
import qrcode
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from ..core.config import TELEGRAM_BOT_TOKEN, TELEGRAM_PROXY, PLANS, INBOUND_ID, SOFTWARE_LINKS, ADMIN_IDS, TRIAL_DURATION_HOURS, TRIAL_TRAFFIC_LIMIT, TRIAL_TRAFFIC_UNIT, REFERRAL_COMMISSION_PERCENT
from ..utils.helpers import convert_traffic
from ..db.database import (SessionLocal, get_user_by_telegram_id, get_user_by_id, create_user, create_subscription, 
                      get_user_subscriptions, update_balance, get_wallet, check_rate_limit, record_action,
                      create_payment, update_payment_status, create_referral, get_referrals, get_backups, create_backup)
from ..core.panel import XUIPanel
from ..core.payment import has_payment_gateway, get_payment_buttons
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

panel = XUIPanel()

def generate_qr(config_text):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(config_text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

async def send_config_with_qr(update, config, lang):
    await update.message.reply_text(f"Your VPN config:\n\n{config}" if lang == 'en' else f"کانفیگ VPN شما:\n\n{config}")
    qr_buf = generate_qr(config)
    await update.message.reply_photo(photo=qr_buf, caption="Scan QR code" if lang == 'en' else "کد QR را اسکن کنید")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data='lang_en')],
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data='lang_fa')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose your language / زبان خود را انتخاب کنید:', reply_markup=reply_markup)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Access denied")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Statistics", callback_data='admin_stats')],
        [InlineKeyboardButton("💳 Payments", callback_data='admin_payments')],
        [InlineKeyboardButton("👥 Users", callback_data='admin_users')],
        [InlineKeyboardButton("🎁 Create Giveaway", callback_data='admin_giveaway')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Admin Panel", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db = SessionLocal()
    user = get_user_by_telegram_id(db, user_id)
    
    if user is None and not query.data.startswith('lang_'):
        await query.edit_message_text("Please start with /start first")
        db.close()
        return
    
    lang = user.language if user else 'en'

    if query.data.startswith('lang_'):
        lang = query.data.split('_')[1]
        if user:
            user.language = lang
            db.commit()
        else:
            referral_code = context.args[0] if context.args else None
            user = create_user(db, user_id, '', lang, referral_code)
            if referral_code:
                referrer = db.query(User).filter_by(referral_code=referral_code).first()
                if referrer:
                    create_referral(db, referrer.id, user.id, 0)
        await show_main_menu(query, lang)
    elif query.data == 'buy_config':
        await show_plans(query, lang)
    elif query.data == 'trial_config':
        if not check_rate_limit(db, user.id, 'trial_config', max_attempts=1):
            await query.edit_message_text("You can only get one trial config per day!" if lang == 'en' else "شما فقط می‌توانید یک کانفیگ آزمایشی در روز دریافت کنید!")
            db.close()
            return
        
        try:
            email = f"trial_{user_id}_{int(datetime.utcnow().timestamp())}@trial.vpn"
            expiry_date = datetime.utcnow() + timedelta(hours=TRIAL_DURATION_HOURS)
            trial_gb = convert_traffic(TRIAL_TRAFFIC_LIMIT, TRIAL_TRAFFIC_UNIT)
            client_id = panel.add_client(INBOUND_ID, email, total_gb=trial_gb * 1024**3, expiry_time=int(expiry_date.timestamp()*1000))
            create_subscription(db, user.id, client_id, 'trial', trial_gb, expiry_date, is_trial=True)
            record_action(db, user.id, 'trial_config')
            config = panel.get_client_config(client_id)
            await send_config_with_qr(query, config, lang)
            await query.message.reply_text(f"Trial config valid for {TRIAL_DURATION_HOURS} hours with {TRIAL_TRAFFIC_LIMIT} {TRIAL_TRAFFIC_UNIT}" if lang == 'en' else f"کانفیگ آزمایشی به مدت {TRIAL_DURATION_HOURS} ساعت با {TRIAL_TRAFFIC_LIMIT} {TRIAL_TRAFFIC_UNIT}")
            record_action(db, user.id, 'trial_config')
        except Exception as e:
            await query.edit_message_text(f"Failed: {str(e)}" if lang == 'en' else f"شکست خورد: {str(e)}")
    elif query.data.startswith('plan_'):
        plan_key = query.data.split('_')[1]
        context.user_data['selected_plan'] = plan_key
        plan = PLANS[plan_key]
        price = plan['price']
        text = f"You selected {plan['name']}. Price: ${price}" if lang == 'en' else f"شما {plan['name_fa']} را انتخاب کردید. قیمت: {price} تومان"
        await query.edit_message_text(text=text)
        
        # Check if payment is enabled
        if has_payment_gateway():
            # Show available payment methods
            payment_buttons = get_payment_buttons()
            keyboard = []
            for gateway_name, callback in payment_buttons:
                keyboard.append([InlineKeyboardButton(f"💳 {gateway_name}", callback_data=callback)])
            keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data='buy_config')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=text, reply_markup=reply_markup)
        else:
            # Payments disabled, ask for email directly
            await query.edit_message_text("Enter your email:" if lang == 'en' else "ایمیل خود را وارد کنید:")
            context.user_data['waiting_for_email'] = True
    elif query.data.startswith('gateway_'):
        # Gateway selection
        gateway_name = query.data.split('_')[1]
        context.user_data['selected_gateway'] = gateway_name
        await query.edit_message_text("Enter your email:" if lang == 'en' else "ایمیل خود را وارد کنید:")
        context.user_data['waiting_for_email'] = True
    elif query.data == 'my_configs':
        subs = get_user_subscriptions(db, user.id) if user else []
        if not subs:
            text = "No configs yet" if lang == 'en' else "هنوز کانفیگی ندارید"
        else:
            text = "Your configs:\n" if lang == 'en' else "کانفیگ های شما:\n"
            for sub in subs:
                remaining = sub.total_gb - sub.used_gb
                text += f"\n- {sub.plan}: {remaining:.2f} GB left, Expires: {sub.expiry_date.strftime('%Y-%m-%d')}"
        await query.edit_message_text(text=text)
    elif query.data == 'wallet':
        wallet = get_wallet(db, user.id)
        text = f"💰 Wallet: ${wallet.balance:.2f}" if lang == 'en' else f"💰 کیف پول: {wallet.balance:.2f} تومان"
        await query.edit_message_text(text=text)
    elif query.data == 'referral':
        referrals = get_referrals(db, user.id)
        text = f"🤝 Referral Code: {user.referral_code}\nReferrals: {len(referrals)} people" if lang == 'en' else f"🤝 کد معرفی: {user.referral_code}\nمعرفی شدگان: {len(referrals)} نفر"
        await query.edit_message_text(text=text)
    elif query.data == 'backup':
        subs = get_user_subscriptions(db, user.id)
        backup_data = json.dumps([{'plan': s.plan, 'gb': s.total_gb, 'expiry': s.expiry_date.isoformat()} for s in subs])
        create_backup(db, user.id, backup_data)
        await query.edit_message_text("✅ Backup created" if lang == 'en' else "✅ بکاپ ایجاد شد")
    db.close()

async def show_main_menu(query, lang):
    keyboard = [
        [InlineKeyboardButton("💳 Buy Config" if lang == 'en' else "خرید کانفیگ", callback_data='buy_config')],
        [InlineKeyboardButton("🎁 Trial Config" if lang == 'en' else "کانفیگ آزمایشی", callback_data='trial_config')],
        [InlineKeyboardButton("📋 My Configs" if lang == 'en' else "کانفیگ های من", callback_data='my_configs')],
        [InlineKeyboardButton("💰 Wallet" if lang == 'en' else "کیف پول", callback_data='wallet')],
        [InlineKeyboardButton("🤝 Referral" if lang == 'en' else "معرفی", callback_data='referral')],
        [InlineKeyboardButton("💾 Backup" if lang == 'en' else "بکاپ", callback_data='backup')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = 'Main Menu' if lang == 'en' else 'منوی اصلی'
    await query.edit_message_text(text=welcome_text, reply_markup=reply_markup)

async def show_plans(query, lang):
    keyboard = []
    for key, plan in PLANS.items():
        name = plan['name'] if lang == 'en' else plan['name_fa']
        keyboard.append([InlineKeyboardButton(name, callback_data=f'plan_{key}')])
    keyboard.append([InlineKeyboardButton("⬅️ Back" if lang == 'en' else "⬅️ بازگشت", callback_data='back_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Choose a plan:" if lang == 'en' else "یک پلن انتخاب کنید:"
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    user = get_user_by_telegram_id(db, user_id)
    
    if not user:
        await update.message.reply_text("Please start with /start first")
        db.close()
        return
    
    lang = user.language

    if context.user_data.get('waiting_for_email'):
        email = update.message.text.strip()
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            text = "Invalid email format." if lang == 'en' else "فرمت ایمیل نامعتبر."
            await update.message.reply_text(text)
            db.close()
            return
        
        plan_key = context.user_data.get('selected_plan')
        if not plan_key:
            await update.message.reply_text("No plan selected" if lang == 'en' else "پلنی انتخاب نشده")
            db.close()
            return

        plan = PLANS[plan_key]
        plan_gb = convert_traffic(plan['traffic'], plan['unit'])
        expiry_date = datetime.utcnow() + timedelta(days=plan['duration_days'])
        
        try:
            if not check_rate_limit(db, user.id, 'buy_config', max_attempts=10):
                await update.message.reply_text("Rate limited. Try again later." if lang == 'en' else "محدود شد. بعدا تلاش کنید.")
                db.close()
                return
            
            client_id = panel.add_client(INBOUND_ID, email, total_gb=plan_gb * 1024**3, expiry_time=int(expiry_date.timestamp()*1000))
            create_subscription(db, user.id, client_id, plan_key, plan_gb, expiry_date)
            record_action(db, user.id, 'buy_config')
            
            config = panel.get_client_config(client_id)
            await send_config_with_qr(update, config, lang)
            
            # Send software links
            links = "\n".join([f"{platform}: {url}" for platform, url in SOFTWARE_LINKS.items()])
            await update.message.reply_text(f"Download apps:\n{links}" if lang == 'en' else f"اپلیکیشن ها را دانلود کنید:\n{links}")
        except Exception as e:
            error_text = f"Failed: {str(e)}" if lang == 'en' else f"شکست خورد: {str(e)}"
            await update.message.reply_text(error_text)

        context.user_data['waiting_for_email'] = False
    db.close()

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()