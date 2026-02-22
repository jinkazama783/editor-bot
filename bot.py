import os
import logging
import asyncio
import aiohttp
from io import BytesIO
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.constants import ParseMode

from telegram.request import HTTPXRequest
from config import Config
from database import Database
from image_processor import ImageProcessor
from ai_editor import AIEditor, AI_STYLES

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()
img_proc = ImageProcessor()
ai_editor = AIEditor()

USER_IMAGE_CACHE: dict = {}


# ─── KEYBOARDS ─────────────────────────────────────────────────────────────────

def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎨 Filters (25)", callback_data="menu_filters"),
            InlineKeyboardButton("✂️ Crop (5)", callback_data="menu_crop"),
        ],
        [
            InlineKeyboardButton("✨ Enhance (10)", callback_data="menu_enhance"),
            InlineKeyboardButton("🤖 AI Tips 💎", callback_data="menu_ai"),
        ],
        [
            InlineKeyboardButton("📝 AI Captions 💎", callback_data="menu_captions"),
            InlineKeyboardButton("🔍 AI Analysis 💎", callback_data="menu_analysis"),
        ],
        [
            InlineKeyboardButton("📊 My Stats", callback_data="menu_stats"),
            InlineKeyboardButton("💎 Get Premium", callback_data="menu_premium"),
        ],
    ])


def filters_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i, (label, code) in enumerate(Config.FILTERS_LIST):
        row.append(InlineKeyboardButton(label, callback_data=f"filter_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def crop_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for label, code in Config.CROP_LIST:
        buttons.append([InlineKeyboardButton(label, callback_data=f"filter_{code}")])
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def enhance_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i, (label, code) in enumerate(Config.ENHANCE_LIST):
        row.append(InlineKeyboardButton(label, callback_data=f"filter_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def ai_styles_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for label, code in AI_STYLES:
        buttons.append([InlineKeyboardButton(label, callback_data=f"ai_style_{code}")])
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def premium_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐ Pay with Telegram Stars", callback_data="pay_stars")],
        [InlineKeyboardButton("📧 Contact Admin for Payment", callback_data="contact_admin")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_main")],
    ])


# ─── COMMANDS ──────────────────────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_or_create_user(user.id, user.username or "", user.full_name or "")
    remaining = db.get_remaining_edits(user.id)

    text = (
        f"👋 *Welcome, {user.first_name}!*\n\n"
        "🤖 I am your *Professional AI Photo Editor Bot*!\n\n"
        "📸 *How to use:*\n"
        "1️⃣ Send me any photo\n"
        "2️⃣ Choose from 40+ editing options\n"
        "3️⃣ Get your edited photo instantly!\n\n"
        f"🆓 *Free edits today:* {remaining}/{Config.FREE_DAILY_LIMIT}\n\n"
        "💎 *Premium features:*\n"
        "• Unlimited edits\n"
        "• AI Style Transfer (8 styles)\n"
        "• AI Image Analysis\n"
        "• Social Media Caption Generator\n\n"
        "👇 *Send a photo to get started!*"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *How to use this bot:*\n\n"
        "1. Send any photo\n"
        "2. Choose editing category:\n"
        "   🎨 *Filters* - 25 creative filters\n"
        "   ✂️ *Crop* - 5 aspect ratios\n"
        "   ✨ *Enhance* - 10 enhancements\n"
        "   🤖 *AI Styles* - 8 AI art styles 💎\n\n"
        "📊 *Commands:*\n"
        "/start - Welcome message\n"
        "/stats - Your usage stats\n"
        "/premium - Get unlimited access\n"
        "/help - This message\n\n"
        "💡 *Tip:* Send multiple photos for batch editing!"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_or_create_user(user.id)
    remaining = db.get_remaining_edits(user.id)

    premium_status = "💎 Premium" if user_data["is_premium"] else "🆓 Free"
    expiry = user_data.get("premium_expiry", "N/A") if user_data["is_premium"] else "—"

    text = (
        f"📊 *Your Statistics*\n\n"
        f"👤 Name: {user.full_name}\n"
        f"🏷️ Plan: {premium_status}\n"
        f"📅 Premium until: {expiry}\n\n"
        f"✏️ Total edits: {user_data['total_edits']}\n"
        f"📆 Edits today: {user_data['daily_count']}\n"
        f"🔋 Remaining today: {remaining}\n\n"
        f"📅 Joined: {user_data['joined_at'][:10]}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💎 *Premium Plan*\n\n"
        f"💰 Price: *${Config.PREMIUM_MONTHLY_PRICE}/month*\n\n"
        "✅ *What you get:*\n"
        "• Unlimited photo edits\n"
        "• 🤖 AI Style Transfer (8 styles)\n"
        "• 🔍 AI Image Analysis\n"
        "• 📝 Caption Generator\n"
        "• Priority processing\n"
        "• New features first\n\n"
        "👇 Choose payment method:"
    )
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=premium_keyboard()
    )


async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_USER_ID:
        await update.message.reply_text("❌ Admin only!")
        return

    stats = db.get_stats()
    text = (
        f"🔧 *Admin Dashboard*\n\n"
        f"👥 Total Users: {stats['total_users']}\n"
        f"💎 Premium Users: {stats['premium_users']}\n"
        f"✏️ Total Edits: {stats['total_edits']}\n"
        f"📆 Today's Edits: {stats['today_edits']}\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def grant_premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_USER_ID:
        await update.message.reply_text("❌ Admin only!")
        return

    if not context.args or len(context.args) < 1:
        await update.message.reply_text("Usage: /grant <user_id> [days]")
        return

    try:
        target_id = int(context.args[0])
        days = int(context.args[1]) if len(context.args) > 1 else 30
        db.set_premium(target_id, days)
        await update.message.reply_text(f"✅ Premium granted to {target_id} for {days} days!")
        try:
            await context.bot.send_message(
                target_id,
                f"🎉 *Congratulations!* You have been upgraded to *Premium* for {days} days!\n\nEnjoy unlimited edits and AI features! 💎",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")


# ─── PHOTO HANDLER ─────────────────────────────────────────────────────────────

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_or_create_user(user.id, user.username or "", user.full_name or "")

    msg = await update.message.reply_text("⏳ Processing your image...")

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_bytes = await file.download_as_bytearray()
        USER_IMAGE_CACHE[user.id] = bytes(image_bytes)

        remaining = db.get_remaining_edits(user.id)
        user_data = db.get_or_create_user(user.id)
        plan = "💎 Premium" if user_data["is_premium"] else "🆓 Free"

        text = (
            f"✅ *Photo received!*\n\n"
            f"🏷️ Plan: {plan}\n"
            f"🔋 Remaining edits: {remaining}\n\n"
            f"👇 *Choose what to do with your photo:*"
        )

        await msg.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Photo handler error: {e}")
        await msg.edit_text("❌ Failed to process image. Please try again.")


# ─── CALLBACK HANDLER ──────────────────────────────────────────────────────────

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    # ── Menu Navigation ──
    if data == "back_main":
        remaining = db.get_remaining_edits(user.id)
        await query.edit_message_text(
            f"✅ *Photo ready!*\n🔋 Remaining edits: {remaining}\n\n👇 Choose an option:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard()
        )
        return

    if data == "menu_filters":
        await query.edit_message_text(
            "🎨 *Choose a Filter:*\n\nAll 25 filters are available!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=filters_keyboard()
        )
        return

    if data == "menu_crop":
        await query.edit_message_text(
            "✂️ *Choose Crop Ratio:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=crop_keyboard()
        )
        return

    if data == "menu_enhance":
        await query.edit_message_text(
            "✨ *Choose Enhancement:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=enhance_keyboard()
        )
        return

    if data == "menu_ai":
        user_data = db.get_or_create_user(user.id)
        if not user_data["is_premium"]:
            await query.edit_message_text(
                "💎 *AI Suggestions — Premium Feature*\n\n"
                "Upgrade to Premium to unlock:\n"
                "• 🔍 Smart edit suggestions\n"
                "• 📝 Caption generator\n"
                "• 🔬 Deep image analysis\n\n"
                f"Only ${Config.PREMIUM_MONTHLY_PRICE}/month",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=premium_keyboard()
            )
            return
        await _handle_ai_suggestions(query, user)
        return

    if data == "menu_captions":
        user_data = db.get_or_create_user(user.id)
        if not user_data["is_premium"]:
            await query.edit_message_text(
                "💎 *AI Captions — Premium Feature*\n\nUpgrade to get AI-generated social media captions!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=premium_keyboard()
            )
            return
        await _handle_ai_captions(query, user)
        return

    if data == "menu_analysis":
        user_data = db.get_or_create_user(user.id)
        if not user_data["is_premium"]:
            await query.edit_message_text(
                "💎 *AI Analysis — Premium Feature*\n\nUpgrade to get professional AI photo analysis!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=premium_keyboard()
            )
            return
        await _handle_ai_analysis(query, user)
        return

    if data == "menu_stats":
        user_data = db.get_or_create_user(user.id)
        remaining = db.get_remaining_edits(user.id)
        premium_status = "💎 Premium" if user_data["is_premium"] else "🆓 Free"
        text = (
            f"📊 *Your Stats*\n\n"
            f"🏷️ Plan: {premium_status}\n"
            f"✏️ Total edits: {user_data['total_edits']}\n"
            f"📆 Today: {user_data['daily_count']}\n"
            f"🔋 Remaining: {remaining}"
        )
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
            ])
        )
        return

    if data == "menu_premium":
        await query.edit_message_text(
            f"💎 *Premium Plan — ${Config.PREMIUM_MONTHLY_PRICE}/month*\n\n"
            "✅ Unlimited edits\n"
            "✅ AI Style Transfer\n"
            "✅ AI Image Analysis\n"
            "✅ Caption Generator\n\n"
            "👇 Choose payment:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=premium_keyboard()
        )
        return

    if data == "pay_stars":
        await query.edit_message_text(
            "⭐ *Pay with Telegram Stars*\n\n"
            "Contact admin to complete your Stars payment:\n"
            f"Admin: @{await _get_admin_username(context)}\n\n"
            "After payment, premium will be activated within minutes!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="menu_premium")]
            ])
        )
        return

    if data == "contact_admin":
        await query.edit_message_text(
            "📧 *Contact Admin*\n\n"
            "Send a message to admin to complete your payment.\n"
            f"Your User ID: `{user.id}`\n\n"
            "Payment methods accepted:\n"
            "• JazzCash / Easypaisa\n"
            "• USDT (Crypto)\n"
            "• Telegram Stars",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="menu_premium")]
            ])
        )
        return

    # ── Filter/Crop/Enhance Actions ──
    if data.startswith("filter_"):
        action = data[len("filter_"):]
        await _apply_filter(query, user, action)
        return

    # ── AI Style Actions ──
    if data.startswith("ai_style_"):
        style = data[len("ai_style_"):]
        await _apply_ai_style(query, user, style)
        return


async def _get_admin_username(context) -> str:
    try:
        admin = await context.bot.get_chat(Config.ADMIN_USER_ID)
        return admin.username or str(Config.ADMIN_USER_ID)
    except Exception:
        return str(Config.ADMIN_USER_ID)


async def _apply_filter(query, user, action: str):
    if user.id not in USER_IMAGE_CACHE:
        await query.edit_message_text(
            "❌ No image found! Please send a photo first.",
            reply_markup=None
        )
        return

    if not db.can_edit(user.id):
        remaining = db.get_remaining_edits(user.id)
        await query.edit_message_text(
            f"⚠️ *Daily limit reached!*\n\n"
            f"🆓 Free plan: {Config.FREE_DAILY_LIMIT} edits/day\n"
            f"🔋 Remaining: {remaining}\n\n"
            f"Upgrade to 💎 Premium for unlimited edits!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=premium_keyboard()
        )
        return

    await query.edit_message_text("⏳ Applying edit, please wait...")

    try:
        image_bytes = USER_IMAGE_CACHE[user.id]
        result_bytes = img_proc.process(image_bytes, action)

        action_name = action.replace("_", " ").title()
        db.increment_edit_count(user.id, "filter", action)
        remaining = db.get_remaining_edits(user.id)

        caption = (
            f"✅ *{action_name}* applied!\n"
            f"🔋 Remaining edits: {remaining}\n\n"
            "Send another photo or choose another edit:"
        )

        await query.message.reply_photo(
            photo=BytesIO(result_bytes),
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard()
        )
        await query.delete_message()

    except Exception as e:
        logger.error(f"Filter error: {e}")
        await query.edit_message_text(
            "❌ Edit failed. Please try again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
            ])
        )


async def _handle_ai_suggestions(query, user):
    if user.id not in USER_IMAGE_CACHE:
        await query.edit_message_text("❌ No image found! Please send a photo first.")
        return

    await query.edit_message_text("🤖 AI suggestions generate ho rahi hain... ⏳")

    try:
        image_bytes = USER_IMAGE_CACHE[user.id]
        suggestions = ai_editor.get_edit_suggestions(image_bytes)
        db.increment_edit_count(user.id, "ai_suggestions")

        await query.edit_message_text(
            f"🤖 *AI Edit Suggestions*\n\n{suggestions}\n\n"
            "👇 Ab in filters ko apply karo:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎨 Apply Filters", callback_data="menu_filters")],
                [InlineKeyboardButton("⬅️ Back", callback_data="back_main")],
            ])
        )

    except Exception as e:
        logger.error(f"AI suggestions error: {e}")
        await query.edit_message_text(
            "❌ AI suggestions failed. Please try again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
            ])
        )


async def _apply_ai_style(query, user, style: str):
    pass


async def _handle_ai_analysis(query, user):
    if user.id not in USER_IMAGE_CACHE:
        await query.edit_message_text("❌ No image found! Please send a photo first.")
        return

    await query.edit_message_text("🔍 Analyzing your image with AI... ⏳")

    try:
        image_bytes = USER_IMAGE_CACHE[user.id]
        analysis = ai_editor.analyze_image(image_bytes)
        db.increment_edit_count(user.id, "ai_analysis")

        await query.edit_message_text(
            f"🔍 *AI Image Analysis*\n\n{analysis}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Edit", callback_data="back_main")]
            ])
        )

    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        await query.edit_message_text(
            "❌ Analysis failed. Please try again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
            ])
        )


async def _handle_ai_captions(query, user):
    if user.id not in USER_IMAGE_CACHE:
        await query.edit_message_text("❌ No image found! Please send a photo first.")
        return

    await query.edit_message_text("📝 Generating captions... ⏳")

    try:
        image_bytes = USER_IMAGE_CACHE[user.id]
        captions = ai_editor.get_caption_suggestions(image_bytes)
        db.increment_edit_count(user.id, "ai_captions")

        await query.edit_message_text(
            f"📝 *AI Caption Suggestions*\n\n{captions}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Edit", callback_data="back_main")]
            ])
        )

    except Exception as e:
        logger.error(f"AI captions error: {e}")
        await query.edit_message_text(
            "❌ Caption generation failed. Please try again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
            ])
        )


async def unknown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Please send a *photo* to get started!\n\nUse /help for instructions.",
        parse_mode=ParseMode.MARKDOWN
    )


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not set in .env file!")
        return

    print("Starting Editor Bot...")

    proxy = os.getenv("PROXY_URL", "")
    if proxy:
        request = HTTPXRequest(proxy=proxy, connect_timeout=30, read_timeout=30)
        app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).request(request).build()
    else:
        request = HTTPXRequest(connect_timeout=30, read_timeout=30)
        app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("premium", premium_command))
    app.add_handler(CommandHandler("admin", admin_stats_command))
    app.add_handler(CommandHandler("grant", grant_premium_command))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_handler))

    print("Bot is running! Press Ctrl+C to stop.")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30,
        pool_timeout=30,
    )


if __name__ == "__main__":
    main()
