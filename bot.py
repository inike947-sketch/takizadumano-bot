"""
Брифинг-бот медиастудии «Так и задумано»
Версия: 1.0
Требует: python-telegram-bot==20.7

Настройка:
  1. Вставь BOT_TOKEN — токен от @BotFather
  2. Вставь ADMIN_CHAT_ID — твой Telegram ID (узнай у @userinfobot)
  3. Запусти: python bot.py
"""

import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# ─── НАСТРОЙКИ ────────────────────────────────────────────────────────────────

BOT_TOKEN   = os.getenv("BOT_TOKEN", "8906747788:AAFSm-TC3NrHeWDw9kntFYK7baPBAcstofM")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_ID", "7987727520"))

# ─── ЛОГИ ─────────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── СОСТОЯНИЯ ДИАЛОГА ────────────────────────────────────────────────────────

(
    S_NAME, S_BUSINESS, S_PRODUCT, S_PAIN,
    S_AUDIENCE, S_SOCIALS, S_REELS,
    S_STYLE, S_TOV,
    S_GOAL, S_TIMELINE, S_BUDGET, S_CONTACT
) = range(13)

# ─── КНОПКИ ───────────────────────────────────────────────────────────────────

KB_SOCIALS = ReplyKeyboardMarkup([
    ["Instagram / Reels", "TikTok"],
    ["YouTube / Shorts", "Telegram"],
    ["ВКонтакте", "Везде понемногу"],
], resize_keyboard=True, one_time_keyboard=True)

KB_REELS = ReplyKeyboardMarkup([
    ["✅ Да, активно снимаю"],
    ["🟡 Иногда, редко"],
    ["🚀 Нет, начинаю с нуля"],
    ["📦 Только чужой контент"],
], resize_keyboard=True, one_time_keyboard=True)

KB_TOV = ReplyKeyboardMarkup([
    ["🤝 Дружеский и тёплый"],
    ["🎓 Экспертный и строгий"],
    ["🔥 Провокационный, дерзкий"],
    ["💬 Доверительный, «свой»"],
    ["🚀 Вдохновляющий, мотивирующий"],
], resize_keyboard=True, one_time_keyboard=True)

KB_GOAL = ReplyKeyboardMarkup([
    ["📣 Узнаваемость / охваты"],
    ["👥 Новые подписчики"],
    ["🎯 Горячие лиды / заявки"],
    ["💰 Продажи на конкретную сумму"],
    ["🌱 Запуск с нуля"],
], resize_keyboard=True, one_time_keyboard=True)

KB_TIMELINE = ReplyKeyboardMarkup([
    ["🔴 Срочно — в течение 2 недель"],
    ["🟡 В этом месяце"],
    ["🟢 1–2 месяца"],
    ["🔵 Не горит, готовим основательно"],
], resize_keyboard=True, one_time_keyboard=True)

KB_BUDGET = ReplyKeyboardMarkup([
    ["До 25 000 ₽"],
    ["25 000 – 50 000 ₽"],
    ["50 000 – 100 000 ₽"],
    ["100 000 – 150 000 ₽"],
    ["150 000 ₽ и выше"],
], resize_keyboard=True, one_time_keyboard=True)

# ─── ПАКЕТЫ ПО БЮДЖЕТУ ────────────────────────────────────────────────────────

PACKAGES = {
    "До 25 000 ₽": (
        "«Стартовый» — от 12 000 ₽/мес",
        "• Упаковка профиля Instagram\n"
        "• 8 Reels / мес (монтаж + стратегия)\n"
        "• Базовая контент-стратегия\n"
        "• Рекомендации по продвижению"
    ),
    "25 000 – 50 000 ₽": (
        "«Запуск» — от 40 000 ₽/мес",
        "• Контент-стратегия под нишу\n"
        "• 12 Reels / мес (съёмка + монтаж)\n"
        "• Сторителлинг и сценарии\n"
        "• Настройка таргета (базовая)\n"
        "• Аналитика раз в месяц"
    ),
    "50 000 – 100 000 ₽": (
        "«Запуск Про» — от 80 000 ₽/мес",
        "• Полная контент-стратегия\n"
        "• 16 Reels + Stories / мес\n"
        "• Сценарии, съёмка, монтаж\n"
        "• Таргетированная реклама (ведение)\n"
        "• Ежемесячный отчёт по KPI\n"
        "• Личный менеджер"
    ),
    "100 000 – 150 000 ₽": (
        "«Рост» — от 115 000 ₽/мес",
        "• Всё из «Запуск Про»\n"
        "• Продюсирование съёмок\n"
        "• 20 единиц контента / мес\n"
        "• Таргет + посевы\n"
        "• Стратегические сессии 2×/мес"
    ),
    "150 000 ₽ и выше": (
        "«Масштабный» — от 150 000 ₽/мес",
        "• Личный бренд «под ключ»\n"
        "• Продюсирование съёмок\n"
        "• 20+ единиц контента / мес\n"
        "• Запуск автоворонок\n"
        "• Таргет + посевы + коллабы\n"
        "• Стратегические сессии 2×/мес\n"
        "• Приоритетная поддержка"
    ),
}

DEFAULT_PACKAGE = (
    "«Запуск» — от 40 000 ₽/мес",
    "• Контент-стратегия под нишу\n• 12 Reels / мес\n• Сценарии, монтаж"
)

# ─── ХЕЛПЕРЫ ──────────────────────────────────────────────────────────────────

def get_brief(context) -> dict:
    if "brief" not in context.user_data:
        context.user_data["brief"] = {}
    return context.user_data["brief"]

def first_name(update: Update) -> str:
    return update.effective_user.first_name or "друг"

async def send(update: Update, text: str, keyboard=None):
    """Отправляет сообщение с опциональной клавиатурой."""
    kwargs = {"text": text, "parse_mode": "HTML"}
    if keyboard:
        kwargs["reply_markup"] = keyboard
    else:
        kwargs["reply_markup"] = ReplyKeyboardRemove()
    await update.message.reply_text(**kwargs)

# ─── КОМАНДЫ ──────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    name = first_name(update)
    await send(update,
        f"Привет, {name}! 👋\n\n"
        "Я — брифинг-бот медиастудии <b>«Так и задумано»</b>.\n\n"
        "За несколько вопросов разберём ваш бизнес, стиль и цели — "
        "и подберём решение, которое выстрелит в Reels 🎬\n\n"
        "Готовы? Тогда поехали!\n\n"
        "<b>Как вас зовут и в чём суть вашего проекта?</b>\n"
        "<i>(Например: «Анна, у меня салон красоты в Уфе»)</i>"
    )
    return S_NAME

async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send(update,
        "Брифинг остановлен.\n\n"
        "Если захотите продолжить — просто напишите /start 🙌"
    )
    return ConversationHandler.END

# ─── ШАГИ БРИФИНГА ────────────────────────────────────────────────────────────

async def step_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["name"] = update.message.text
    first = update.message.text.split()[0]

    await send(update,
        f"Отлично, {first}! 🔥\n\n"
        "Расскажите в двух предложениях — <b>чем занимается ваш бизнес или проект?</b>"
    )
    return S_BUSINESS

async def step_business(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["business"] = update.message.text

    await send(update,
        "Понял! Теперь про продукт.\n\n"
        "<b>Какую основную услугу или продукт вы продаёте?</b>\n"
        "И в чём ваша главная «фишка» — чем отличаетесь от конкурентов?"
    )
    return S_PRODUCT

async def step_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["product"] = update.message.text

    await send(update,
        "Хороший продукт! 💡\n\n"
        "<b>Какие главные боли клиентов он закрывает?</b>\n"
        "Что меняется в жизни человека после покупки?"
    )
    return S_PAIN

async def step_pain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["pain"] = update.message.text

    await send(update,
        "Принял! Ключевое для контента — знать боль аудитории.\n\n"
        "<b>Опишите вашего идеального клиента:</b>\n"
        "пол, возраст, интересы, уровень дохода."
    )
    return S_AUDIENCE

async def step_audience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["audience"] = update.message.text

    await send(update,
        "Аудитория ясна 👥\n\n"
        "<b>Где ваша аудитория «обитает» онлайн прямо сейчас?</b>",
        KB_SOCIALS
    )
    return S_SOCIALS

async def step_socials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["socials"] = update.message.text

    await send(update,
        f"{update.message.text} — отличная площадка! 🚀\n\n"
        "<b>Вы уже снимаете Reels или короткие видео?</b>",
        KB_REELS
    )
    return S_REELS

async def step_reels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["reels"] = update.message.text
    has_reels = "активно" in update.message.text.lower()

    comment = "Прекрасно, есть с чем работать!" if has_reels else \
              "Будем строить системно — это даже интереснее!"

    await send(update,
        f"{comment}\n\n"
        "Переходим к визуальному стилю 🎨\n\n"
        "<b>Как бы вы описали желаемый стиль тремя прилагательными?</b>\n"
        "<i>Например: минималистичный, дерзкий, дорогой</i>"
    )
    return S_STYLE

async def step_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["style"] = update.message.text

    await send(update,
        f"«{update.message.text}» — уже чувствую эстетику бренда! 🎨\n\n"
        "<b>Какой Tone of Voice у вашего бренда?</b>",
        KB_TOV
    )
    return S_TOV

async def step_tov(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["tov"] = update.message.text

    await send(update,
        f"{update.message.text} — это точно попадёт в вашу аудиторию!\n\n"
        "Почти финиш! 🚀\n\n"
        "<b>Какая главная цель на ближайшие 3 месяца?</b>",
        KB_GOAL
    )
    return S_GOAL

async def step_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["goal"] = update.message.text

    await send(update,
        f"{update.message.text} — конкретная цель, работаем!\n\n"
        "<b>Есть ли срочность? Когда нужно запустить первые результаты?</b>",
        KB_TIMELINE
    )
    return S_TIMELINE

async def step_timeline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["timeline"] = update.message.text

    await send(update,
        f"Зафиксировал срок.\n\n"
        "И самый важный вопрос 💰\n\n"
        "<b>Какой ориентировочный бюджет на контент и продвижение в месяц?</b>",
        KB_BUDGET
    )
    return S_BUDGET

async def step_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["budget"] = update.message.text

    await send(update,
        "Отлично! Могу предложить конкретный пакет 🎯\n\n"
        "<b>Последний вопрос:</b>\n"
        "Кто с вашей стороны будет принимать решения и давать обратную связь?\n"
        "<i>(Имя и роль)</i>"
    )
    return S_CONTACT

async def step_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    brief = get_brief(context)
    brief["contact"] = update.message.text

    # Определяем пакет
    budget = brief.get("budget", "")
    pkg_name, pkg_items = PACKAGES.get(budget, DEFAULT_PACKAGE)

    # Имя клиента (первое слово из поля name)
    client_name = brief.get("name", "").split()[0]

    # ── Итоговое сообщение клиенту ──────────────────────────────────────────
    summary = (
        f"🎉 <b>Брифинг завершён, {client_name}!</b>\n\n"
        f"Я зафиксировал всё главное о вашем проекте.\n\n"
        f"─────────────────\n"
        f"📋 <b>Ваше резюме:</b>\n\n"
        f"👤 <b>Имя / роль:</b> {brief.get('name', '—')}\n"
        f"🏢 <b>Бизнес:</b> {brief.get('business', '—')}\n"
        f"📣 <b>Площадки:</b> {brief.get('socials', '—')}\n"
        f"🎯 <b>Цель:</b> {brief.get('goal', '—')}\n"
        f"⏱ <b>Срок:</b> {brief.get('timeline', '—')}\n"
        f"💰 <b>Бюджет:</b> {brief.get('budget', '—')}\n"
        f"─────────────────\n\n"
        f"✨ <b>Рекомендуемый пакет:</b>\n"
        f"{pkg_name}\n\n"
        f"{pkg_items}\n\n"
        f"─────────────────\n\n"
        f"Наш менеджер свяжется с вами в ближайшее время!\n\n"
        f"А пока — можете написать нам напрямую:\n"
        f"👉 @zadumanostudio\n"
        f"📞 8 (993) 056-25-85\n"
        f"🌐 takizadumano.ru"
    )
    await send(update, summary)

    # ── Уведомление менеджеру (тебе) ────────────────────────────────────────
    user = update.effective_user
    tg_link = f"@{user.username}" if user.username else f"tg://user?id={user.id}"

    admin_msg = (
        f"🔔 <b>НОВЫЙ БРИФИНГ!</b>\n\n"
        f"👤 Telegram: {tg_link} ({user.full_name})\n"
        f"─────────────────\n"
        f"<b>Имя / роль:</b> {brief.get('name', '—')}\n"
        f"<b>Бизнес:</b>\n{brief.get('business', '—')}\n\n"
        f"<b>Продукт:</b>\n{brief.get('product', '—')}\n\n"
        f"<b>Боли клиентов:</b>\n{brief.get('pain', '—')}\n\n"
        f"<b>Аудитория:</b>\n{brief.get('audience', '—')}\n\n"
        f"<b>Площадки:</b> {brief.get('socials', '—')}\n"
        f"<b>Reels:</b> {brief.get('reels', '—')}\n"
        f"<b>Стиль:</b> {brief.get('style', '—')}\n"
        f"<b>Tone of Voice:</b> {brief.get('tov', '—')}\n\n"
        f"<b>Цель (3 мес):</b> {brief.get('goal', '—')}\n"
        f"<b>Срок запуска:</b> {brief.get('timeline', '—')}\n"
        f"<b>Бюджет/мес:</b> {brief.get('budget', '—')}\n"
        f"<b>ЛПР:</b> {brief.get('contact', '—')}\n"
        f"─────────────────\n"
        f"📦 <b>Подобранный пакет:</b>\n{pkg_name}\n\n"
        f"{pkg_items}"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_msg,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление менеджеру: {e}")

    return ConversationHandler.END

# ─── ОБРАБОТЧИК НЕПРЕДВИДЕННЫХ СООБЩЕНИЙ ──────────────────────────────────────

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send(update,
        "Напишите /start чтобы начать брифинг.\n"
        "Или /cancel чтобы остановить текущий."
    )

# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────

def main() -> None:
    if BOT_TOKEN == "ВСТАВЬ_ТОКЕН_СЮДА":
        logger.error("❌ Не задан BOT_TOKEN! Добавь его в переменные окружения.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler — главный диалог брифинга
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            S_NAME:      [MessageHandler(filters.TEXT & ~filters.COMMAND, step_name)],
            S_BUSINESS:  [MessageHandler(filters.TEXT & ~filters.COMMAND, step_business)],
            S_PRODUCT:   [MessageHandler(filters.TEXT & ~filters.COMMAND, step_product)],
            S_PAIN:      [MessageHandler(filters.TEXT & ~filters.COMMAND, step_pain)],
            S_AUDIENCE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, step_audience)],
            S_SOCIALS:   [MessageHandler(filters.TEXT & ~filters.COMMAND, step_socials)],
            S_REELS:     [MessageHandler(filters.TEXT & ~filters.COMMAND, step_reels)],
            S_STYLE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, step_style)],
            S_TOV:       [MessageHandler(filters.TEXT & ~filters.COMMAND, step_tov)],
            S_GOAL:      [MessageHandler(filters.TEXT & ~filters.COMMAND, step_goal)],
            S_TIMELINE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, step_timeline)],
            S_BUDGET:    [MessageHandler(filters.TEXT & ~filters.COMMAND, step_budget)],
            S_CONTACT:   [MessageHandler(filters.TEXT & ~filters.COMMAND, step_contact)],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    logger.info("✅ Бот «Так и задумано» запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
