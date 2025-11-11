import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# === Настройка логирования ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Данные магазина ===
CATEGORIES = {
    "special": "Специальные предложения",
    "recommended": "Рекомендуемые",
}

PRODUCTS = {
    "special": [
        {
            "id": "jjm",
            "name": "Цзинь Цзюнь Мэй - Золотые брови - Элитный красный чай. 50 грамм.",
            "desc": "Чай Цзинь Цзюнь Мэй - Золотые брови - Элитный красный чай. Свежий, ароматный, бодрящий. 50 грамм...",
            "price": 500,
        },
        {
            "id": "fhdz",
            "name": "Чай Фэн Хуан Дань Цун (Чаочжоу Ча) - Гуандунский улун - ФХДЦ 100 грамм",
            "desc": "Чай Фэн Хуан Дань Цун - ФХДЦ (Чаочжоу Ча) - Гуандунский улун высокого качества. Свежий, крепкий, бод...",
            "price": 1000,
        },
        {
            "id": "dhs",
            "name": "Дянь Хунь Гу Шу - прессованный блин 357 грамм",
            "desc": "Дянь Хунь Гу Шу - прессованный блин 357 грамм..",
            "price": 1700,
        },
    ],
    "recommended": [
        {
            "id": "shen1",
            "name": "Шен Пуэр 2016 года - Павлин Буланшань. Фабрика ЧжунЧа.",
            "desc": "Шен Пуэр 2014 года - Павлин Буланшань. Фабрика ЧжунЧа. Коллекционный чай высокого качества. Бинча 35...",
            "price": 5400,
        },
        {
            "id": "shen2",
            "name": "Шен Пуэр 2016 года - Сокровище Павлина. Фабрика ЧжунЧа.",
            "desc": "Шен Пуэр 2016 года - Сокровище Павлина. Фабрика ЧжунЧа. Коллекционный чай высокого качества. Бинча 3...",
            "price": 5200,
        },
        {
            "id": "shu",
            "name": "Шу пуэр Древний чай Ланьцан. Год Собаки - 2018 год. Блин 357 грамм.",
            "desc": "Шу пуэр оригинальный. Древний чай Ланьцан. Новогодний - Собака - 2018 год. Эксклюзивный натуральный ...",
            "price": 5500,
        },
    ],
}

# === Хранилище корзин (в реальном проекте — база данных) ===
user_carts = {}

def get_cart(user_id):
    if user_id not in user_carts:
        user_carts[user_id] = []
    return user_carts[user_id]

def add_to_cart(user_id, product_id):
    cart = get_cart(user_id)
    cart.append(product_id)

def get_cart_total(user_id):
    cart = get_cart(user_id)
    total = 0
    for pid in cart:
        for cat in PRODUCTS.values():
            for p in cat:
                if p["id"] == pid:
                    total += p["price"]
                    break
    return total

def get_cart_summary(user_id):
    cart = get_cart(user_id)
    if not cart:
        return "Ваша корзина пуста."
    
    items = []
    for pid in cart:
        for cat in PRODUCTS.values():
            for p in cat:
                if p["id"] == pid:
                    items.append(f"• {p['name']} — {p['price']} ₽")
                    break
    total = get_cart_total(user_id)
    return "\n".join(items) + f"\n\nИтого: {total} ₽"

# === Обработчики ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Специальные предложения", callback_data="cat_special")],
        [InlineKeyboardButton("Рекомендуемые", callback_data="cat_recommended")],
        [InlineKeyboardButton("📥 Корзина", callback_data="cart")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать в ЧайХу! 🍵\nВыберите категорию:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "back_to_menu":
        keyboard = [
            [InlineKeyboardButton("Специальные предложения", callback_data="cat_special")],
            [InlineKeyboardButton("Рекомендуемые", callback_data="cat_recommended")],
            [InlineKeyboardButton("📥 Корзина", callback_data="cart")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Выберите категорию:", reply_markup=reply_markup
        )

    elif data.startswith("cat_"):
        cat_key = data[4:]
        keyboard = []
        for prod in PRODUCTS[cat_key]:
            keyboard.append([
                InlineKeyboardButton(
                    f"{prod['name']} — {prod['price']} ₽",
                    callback_data=f"prod_{prod['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🫖 {CATEGORIES[cat_key]}:", reply_markup=reply_markup
        )

    elif data.startswith("prod_"):
        prod_id = data[5:]
        # Найти продукт
        product = None
        for cat in PRODUCTS.values():
            for p in cat:
                if p["id"] == prod_id:
                    product = p
                    break
            if product:
                break
        if product:
            add_to_cart(user_id, prod_id)
            keyboard = [
                [InlineKeyboardButton("🛒 Перейти в корзину", callback_data="cart")],
                [InlineKeyboardButton("⬅️ Назад к категориям", callback_data="back_to_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"✅ Добавлено в корзину:\n\n{product['name']}\n{product['price']} ₽",
                reply_markup=reply_markup
            )

    elif data == "cart":
        summary = get_cart_summary(user_id)
        keyboard = [
            [InlineKeyboardButton("Оформить заказ", url="https://t.me/chahu_ru")],
            [InlineKeyboardButton("⬅️ Назад к категориям", callback_data="back_to_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🛒 Ваша корзина:\n\n{summary}",
            reply_markup=reply_markup
        )

# === Основная функция ===
def main():
    # Вставьте сюда ваш токен от @BotFather
    TOKEN = "8512023531:AAGKNlI2cbfS5HY5jweao0l1ftUrmqtYKGQ"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
