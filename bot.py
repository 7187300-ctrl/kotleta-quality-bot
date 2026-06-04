import logging
import sqlite3
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8891826393:AAF2q6sBRf1StTpKsxZmbMQ0bhjAUMMMzrI")
ADMIN_IDS = [213356772, 300594899]
PORT = int(os.environ.get("PORT", 8443))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

TASTE, APPEARANCE, TEXTURE, ROAST, STABILITY, NOTES = range(6)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def init_db():
    conn = sqlite3.connect("quality.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            taste INTEGER,
            appearance INTEGER,
            texture INTEGER,
            roast INTEGER,
            stability INTEGER,
            notes TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_review(data: dict):
    conn = sqlite3.connect("quality.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO reviews
        (user_id, username, first_name, taste, appearance, texture, roast, stability, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["user_id"], data["username"], data["first_name"],
        data["taste"], data["appearance"], data["texture"],
        data["roast"], data["stability"], data["notes"],
        data["created_at"]
    ))
    conn.commit()
    conn.close()


def score_keyboard(step: str) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(str(i), callback_data=f"{step}:{i}") for i in range(6)]]
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Добро пожаловать в систему контроля качества!\n\n"
        "Команды:\n"
        "/review — начать оценку котлеты\n"
        "/stats — статистика (только администраторы)\n"
        "/cancel — отменить текущую оценку"
    )


async def review_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "🍔 *Оценка котлеты* — шаг 1 из 5\n\n"
        "🍽 *ВКУС* — поставь оценку от 0 до 5:",
        parse_mode="Markdown",
        reply_markup=score_keyboard("taste"),
    )
    return TASTE


async def handle_taste(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    score = int(query.data.split(":")[1])
    context.user_data["taste"] = score
    await query.edit_message_text(
        f"✅ Вкус: *{score}/5*\n\n"
        "Шаг 2 из 5\n\n"
        "👁 *ВНЕШНИЙ ВИД* — поставь оценку от 0 до 5:",
        parse_mode="Markdown",
        reply_markup=score_keyboard("appearance"),
    )
    return APPEARANCE


async def handle_appearance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    score = int(query.data.split(":")[1])
    context.user_data["appearance"] = score
    await query.edit_message_text(
        f"✅ Вкус: *{context.user_data['taste']}/5*\n"
        f"✅ Внешний вид: *{score}/5*\n\n"
        "Шаг 3 из 5\n\n"
        "🖐 *ПЛОТНОСТЬ ТЕКСТУРЫ* — поставь оценку от 0 до 5:",
        parse_mode="Markdown",
        reply_markup=score_keyboard("texture"),
    )
    return TEXTURE


async def handle_texture(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    score = int(query.data.split(":")[1])
    context.user_data["texture"] = score
    await query.edit_message_text(
        f"✅ Вкус: *{context.user_data['taste']}/5*\n"
        f"✅ Внешний вид: *{context.user_data['appearance']}/5*\n"
        f"✅ Плотность текстуры: *{score}/5*\n\n"
        "Шаг 4 из 5\n\n"
        "🔥 *ЗАЖАРЕННОСТЬ* — поставь оценку от 0 до 5:",
        parse_mode="Markdown",
        reply_markup=score_keyboard("roast"),
    )
    return ROAST


async def handle_roast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    score = int(query.data.split(":")[1])
    context.user_data["roast"] = score
    await query.edit_message_text(
        f"✅ Вкус: *{context.user_data['taste']}/5*\n"
        f"✅ Внешний вид: *{context.user_data['appearance']}/5*\n"
        f"✅ Плотность текстуры: *{context.user_data['texture']}/5*\n"
        f"✅ Зажаренность: *{score}/5*\n\n"
        "Шаг 5 из 5\n\n"
        "🔁 *СТАБИЛЬНОСТЬ ВКУСА* — поставь оценку от 0 до 5:",
        parse_mode="Markdown",
        reply_markup=score_keyboard("stability"),
    )
    return STABILITY


async def handle_stability(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    score = int(query.data.split(":")[1])
    context.user_data["stability"] = score
    await query.edit_message_text(
        f"✅ Вкус: *{context.user_data['taste']}/5*\n"
        f"✅ Внешний вид: *{context.user_data['appearance']}/5*\n"
        f"✅ Плотность текстуры: *{context.user_data['texture']}/5*\n"
        f"✅ Зажаренность: *{context.user_data['roast']}/5*\n"
        f"✅ Стабильность вкуса: *{score}/5*\n\n"
        "📝 *ЗАМЕЧАНИЯ* — напиши что понравилось или не понравилось.\n"
        "Если замечаний нет — напиши: *нет*",
        parse_mode="Markdown",
    )
    return NOTES


async def handle_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    notes = update.message.text
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    data = {
        "user_id": user.id,
        "username": user.username or "нет",
        "first_name": user.first_name or "нет",
        "taste": context.user_data["taste"],
        "appearance": context.user_data["appearance"],
        "texture": context.user_data["texture"],
        "roast": context.user_data["roast"],
        "stability": context.user_data["stability"],
        "notes": notes,
        "created_at": now,
    }

    save_review(data)

    total = data["taste"] + data["appearance"] + data["texture"] + data["roast"] + data["stability"]
    avg = total / 5

    summary = (
        f"✅ *Оценка сохранена!*\n\n"
        f"👤 {data['first_name']} (@{data['username']})\n"
        f"🕐 {now}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🍽 Вкус: *{data['taste']}/5*\n"
        f"👁 Внешний вид: *{data['appearance']}/5*\n"
        f"🖐 Плотность текстуры: *{data['texture']}/5*\n"
        f"🔥 Зажаренность: *{data['roast']}/5*\n"
        f"🔁 Стабильность вкуса: *{data['stability']}/5*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📊 Средний балл: *{avg:.1f}/5*\n\n"
        f"📝 Замечания: {notes}"
    )

    await update.message.reply_text(summary, parse_mode="Markdown")

    notification = (
        f"🔔 *Новая оценка котлеты*\n\n"
        f"👤 {data['first_name']} (@{data['username']}) | ID: `{data['user_id']}`\n"
        f"🕐 {now}\n\n"
        f"🍽 Вкус: *{data['taste']}/5*\n"
        f"👁 Внешний вид: *{data['appearance']}/5*\n"
        f"🖐 Плотность текстуры: *{data['texture']}/5*\n"
        f"🔥 Зажаренность: *{data['roast']}/5*\n"
        f"🔁 Стабильность вкуса: *{data['stability']}/5*\n"
        f"📊 Средний балл: *{avg:.1f}/5*\n\n"
        f"📝 Замечания: {notes}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=notification, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление {admin_id}: {e}")

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("❌ Оценка отменена. Напиши /review чтобы начать заново.")
    return ConversationHandler.END


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет доступа к статистике.")
        return

    conn = sqlite3.connect("quality.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reviews")
    total = c.fetchone()[0]

    if total == 0:
        await update.message.reply_text("📊 Оценок пока нет.")
        conn.close()
        return

    c.execute("SELECT AVG(taste), AVG(appearance), AVG(texture), AVG(roast), AVG(stability) FROM reviews")
    avgs = c.fetchone()

    c.execute("""
        SELECT first_name, username, taste, appearance, texture, roast, stability, notes, created_at
        FROM reviews ORDER BY id DESC LIMIT 5
    """)
    recent = c.fetchall()
    conn.close()

    overall = sum(avgs) / 5

    text = (
        f"📊 *Статистика контроля качества*\n\n"
        f"Всего оценок: *{total}*\n\n"
        f"Средние показатели:\n"
        f"🍽 Вкус: *{avgs[0]:.2f}/5*\n"
        f"👁 Внешний вид: *{avgs[1]:.2f}/5*\n"
        f"🖐 Плотность текстуры: *{avgs[2]:.2f}/5*\n"
        f"🔥 Зажаренность: *{avgs[3]:.2f}/5*\n"
        f"🔁 Стабильность вкуса: *{avgs[4]:.2f}/5*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📈 Общий средний балл: *{overall:.2f}/5*\n\n"
        f"*Последние 5 оценок:*\n"
    )

    for r in recent:
        avg_r = (r[2] + r[3] + r[4] + r[5] + r[6]) / 5
        text += f"\n• {r[0]} (@{r[1]}) — {r[8]}: *{avg_r:.1f}/5*"
        if r[7] and r[7].lower() != "нет":
            text += f"\n  📝 {r[7]}"

    await update.message.reply_text(text, parse_mode="Markdown")


def main() -> None:
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("review", review_start)],
        states={
            TASTE:      [CallbackQueryHandler(handle_taste,      pattern=r"^taste:\d$")],
            APPEARANCE: [CallbackQueryHandler(handle_appearance, pattern=r"^appearance:\d$")],
            TEXTURE:    [CallbackQueryHandler(handle_texture,    pattern=r"^texture:\d$")],
            ROAST:      [CallbackQueryHandler(handle_roast,      pattern=r"^roast:\d$")],
            STABILITY:  [CallbackQueryHandler(handle_stability,  pattern=r"^stability:\d$")],
            NOTES:      [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_notes)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
        per_chat=True,
        per_user=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("stats", stats))

    logger.info("Бот запущен...")

    if WEBHOOK_URL:
        # Webhook режим для продакшена (Render Web Service)
        logger.info(f"Запуск в webhook режиме на порту {PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
            drop_pending_updates=True,
        )
    else:
        # Polling режим для локальной разработки
        logger.info("Запуск в polling режиме (локально)")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )


if __name__ == "__main__":
    main()
