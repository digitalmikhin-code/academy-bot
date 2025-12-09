from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import random
import datetime


# --------------------
# НАСТРОЙКИ
# --------------------

GROUP_ID = -1003347911685   # ← сюда будут прилетать лиды


# ------------- СТАДИИ -----------------
ROLE, GOAL, FORMAT, DURATION, NAME, PHONE = range(6)

# ------------- КЛЮЧИ -----------------
ROLE_KEYS = {
    "ТОП-менеджер / директор направления": "top",
    "Руководитель подразделения / отдела": "head",
    "Собственник бизнеса / предприниматель": "owner",
    "Специалист (Middle / Senior)": "specialist",
    "HR / L&D специалист": "hr",
}

GOAL_KEYS = {
    "📈 Прокачать управление": "manage",
    "🧩 Убрать хаос в процессах": "chaos",
    "👥 Усилить команду": "team",
    "🛠 Освоить профессию": "profession",
    "🎓 Получить квалификацию": "qualification",
    "💰 Увеличить выручку бизнеса": "revenue",
    "❗️ Решить конкретную проблему": "problem",
}

# ------------- КАТАЛОГ -----------------
CATALOG = {
    "top": {
        "manage": [
            "Управленческий цикл",
            "Системное мышление",
            "Нейробиология для управления",
            "Финансовый интеллект",
            "MBA",
            "Mini MBA HoReCa",
        ],
        "chaos": ["Управление проектами", "Agile практики", "Производственные интенсивы HoReCa"],
        "team": ["Наставничество", "Ответственность персонала", "Управление изменениями"],
        "revenue": ["Экономика продукта", "Финансовый интеллект", "Agile для HoReCa"],
        "problem": ["Управление проектами", "Управление изменениями"],
    },

    "head": {
        "manage": ["Управленческий цикл", "Управление проектами", "Лидерство"],
        "chaos": ["Agile", "Управленческие интенсивы", "Производственные процессы"],
        "team": ["Наставничество", "Ответственность", "Кросс-функ взаимодействие"],
        "qualification": ["Управление проектами", "Soft Skills интенсивы"],
        "revenue": ["Экономика продукта"],
        "problem": ["Agile", "Наставничество"],
    },

    "owner": {
        "revenue": ["Финансовый интеллект", "Экономика продукта", "Agile для бизнеса", "MBA"],
        "manage": ["Mini MBA", "Управленческий цикл"],
        "team": ["Управление изменениями"],
        "chaos": ["Agile для бизнеса", "Управление проектами"],
        "problem": ["Экономика продукта", "Управление изменениями"],
    },

    "specialist": {
        "profession": [
            "Повар Старт",
            "Бариста",
            "Pro Бариста",
            "Латте-арт",
            "Су-шеф",
            "Гастрономические мастер-классы",
        ],
        "qualification": ["Управление проектами", "Soft Skills интенсивы"],
        "manage": ["Лидерство", "Soft Skills"],
        "problem": ["Управление проектами"],
    },

    "hr": {
        "manage": ["HR Digital", "Наставничество", "Удержание сотрудников", "Ответственность"],
        "chaos": ["Система обучения", "Регламенты", "Снижение текучести"],
        "team": ["Наставничество", "Ответственность"],
        "profession": ["HR Digital"],
        "qualification": ["HR Digital", "Наставничество"],
        "problem": ["Система обучения"],
    },
}


# ------------------- КЛАВИАТУРЫ ------------------
def role_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["ТОП-менеджер / директор направления"],
            ["Руководитель подразделения / отдела"],
            ["Собственник бизнеса / предприниматель"],
            ["Специалист (Middle / Senior)"],
            ["HR / L&D специалист"],
        ],
        resize_keyboard=True,
    )


def goal_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📈 Прокачать управление", "🧩 Убрать хаос в процессах"],
            ["👥 Усилить команду", "🛠 Освоить профессию"],
            ["🎓 Получить квалификацию"],
            ["💰 Увеличить выручку бизнеса"],
            ["❗️ Решить конкретную проблему"],
        ],
        resize_keyboard=True,
    )


def format_keyboard():
    return ReplyKeyboardMarkup(
        [["💻 Онлайн", "🏫 Очно (Москва)"], ["♻️ Гибрид", "🟰 Не важно"]],
        resize_keyboard=True,
    )


def duration_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["⚡️ Короткий интенсив (1–2 дня)"],
            ["📘 Курс 3–6 недель"],
            ["🎓 Долгая программа (MBA / 4 месяца / год / 2 года)"],
            ["🕓 Не важно — расскажите, что есть"],
        ],
        resize_keyboard=True,
    )


def contact_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Поделиться номером телефона", request_contact=True)]],
        resize_keyboard=True,
    )


def menu_inline():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔍 Подробнее на сайте", url="https://academybk.neftm.ru/")],
            [InlineKeyboardButton("🗓 Записаться на консультацию", url="https://t.me/Kirill_Academy_Neftm")],
            [InlineKeyboardButton("💬 Задать вопрос менеджеру", url="https://t.me/Kirill_Academy_Neftm")],
        ]
    )


# --------------------- КОМАНДА /id --------------------

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text(f"ID этого чата: {chat_id}")


# --------------------- ХЭНДЛЕРЫ --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n"
        "Я — виртуальный помощник Корпоративной Академии «Нефтьмагистраль & Братья Караваевы».\n\n"
        "Помогу подобрать программу обучения, которая идеально подходит под вашу задачу, роль и цели развития.\n"
        "Давайте начнём — подскажите, пожалуйста, кем вы являетесь по роли?",
        reply_markup=role_keyboard(),
    )
    return ROLE


async def handle_role(update, context):
    text = update.message.text
    if text not in ROLE_KEYS:
        await update.message.reply_text(
            "Пожалуйста, выберите один из вариантов на клавиатуре 👇",
            reply_markup=role_keyboard()
        )
        return ROLE

    context.user_data["role"] = ROLE_KEYS[text]
    context.user_data["role_label"] = text

    await update.message.reply_text(
        "Отлично, спасибо! 🙌\n"
        "Чтобы подобрать наиболее точные варианты, расскажите, пожалуйста, какую задачу хотите решить сейчас.",
        reply_markup=goal_keyboard(),
    )
    return GOAL


async def handle_goal(update, context):
    text = update.message.text
    if text not in GOAL_KEYS:
        await update.message.reply_text(
            "Пожалуйста, выберите задачу из списка 👇",
            reply_markup=goal_keyboard(),
        )
        return GOAL

    context.user_data["goal"] = GOAL_KEYS[text]
    context.user_data["goal_label"] = text

    await update.message.reply_text(
        "Хорошо! 😊\n"
        "В каком формате вам удобнее обучаться?",
        reply_markup=format_keyboard(),
    )
    return FORMAT


async def handle_format(update, context):
    context.user_data["format"] = update.message.text

    await update.message.reply_text(
        "Понял! 🔎\n"
        "Теперь подскажите, пожалуйста, какой темп обучения вам комфортнее?",
        reply_markup=duration_keyboard(),
    )
    return DURATION


async def handle_duration(update, context):
    context.user_data["duration"] = update.message.text
    await update.message.reply_text(
        "Спасибо! 🙏\n"
        "И чтобы сделать подборку максимально персональной, напишите, пожалуйста, как к вам можно обращаться?"
    )
    return NAME


async def handle_name(update, context):
    context.user_data["name"] = update.message.text.strip()

    await update.message.reply_text(
        "Приятно познакомиться! ✨\n"
        "Чтобы я мог отправить вам подборку, поделитесь, пожалуйста, номером телефона.\n"
        "Это безопасно — номер будет доступен только менеджеру Академии.",
        reply_markup=contact_keyboard(),
    )
    return PHONE


async def handle_phone(update, context):
    phone = update.message.contact.phone_number if update.message.contact else update.message.text
    context.user_data["phone"] = phone

    await update.message.reply_text("Отлично! 🤝 Собираю персональную подборку…")

    # Отправка лида в группу менеджеров
    await send_lead_to_group(update, context)

    await send_recommendations(update, context)
    return ConversationHandler.END


async def send_lead_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка лида менеджерам в группу."""

    user = context.user_data

    lead_text = (
        "🔥 Новый лид из чат-бота Академии!\n\n"
        f"👤 Имя: {user.get('name')}\n"
        f"📱 Телефон: {user.get('phone')}\n"
        f"🎯 Роль: {user.get('role_label')}\n"
        f"🧩 Цель: {user.get('goal_label')}\n"
        f"📚 Формат: {user.get('format')}\n"
        f"⏳ Длительность: {user.get('duration')}\n"
        f"🕒 Время заявки: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    )

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=lead_text
    )


async def send_recommendations(update, context):
    role = context.user_data["role"]
    goal = context.user_data["goal"]
    role_label = context.user_data["role_label"]
    goal_label = context.user_data["goal_label"]

    programs = CATALOG.get(role, {}).get(goal, [])
    random.shuffle(programs)
    selected = programs[:3]

    text = (
        "🎓 Готово! Я подобрал программы, которые лучше всего подходят под ваши цели и роль.\n\n"
    )

    for i, prog in enumerate(selected, 1):
        text += f"{i}. {prog}\nПричина: программа соответствует вашей роли ({role_label}) и задаче ({goal_label}).\n\n"

    await update.message.reply_text(text, reply_markup=menu_inline())


# ------------------ ConversationHandler -----------------

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_role)],
        GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_goal)],
        FORMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_format)],
        DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_duration)],
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
        PHONE: [
            MessageHandler(filters.CONTACT, handle_phone),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)
        ],
    },
    fallbacks=[],
)

# ----------------------- ЗАПУСК -------------------------

if __name__ == "__main__":
    app = ApplicationBuilder()\
        .token("8459510275:AAFL4YQdqF0Rr_7FGdtF0n933EXUgHiKJMU")\
        .build()

    app.add_handler(conv)
    app.add_handler(CommandHandler("id", get_chat_id))
    app.add_handler(CallbackQueryHandler(lambda *_: None))

    print("Bot is running…")
    app.run_polling()
