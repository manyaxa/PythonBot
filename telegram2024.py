# 7581620320:AAEfu4zc2kfr6iSLarP6bYHX8zK5tLNatuI
from telegram import InputMediaPhoto, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, \
    MessageHandler, filters
import sqlite3
import asyncio



# Стадії конверсії
DATE_START, VOZRAST, GUESTS, BRON = range(4)
app = ApplicationBuilder().token('7581620320:AAEfu4zc2kfr6iSLarP6bYHX8zK5tLNatuI').build()


def setup_database():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    # Створення таблиці користувачів
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS users (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           username TEXT NOT NULL,
           chat_id INTEGER NOT NULL UNIQUE,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       )
       """)

    # Створення таблиці бронювань
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS bookings (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_id INTEGER NOT NULL,
           date_start TEXT NOT NULL,
           vozrast TEXT NOT NULL,
           guests TEXT NOT NULL,
           bron TEXT NOT NULL,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
           FOREIGN KEY (user_id) REFERENCES users (id)
       )
       """)
    connection.commit()
    connection.close()
    print("База даних успішно налаштована.")

async def broadcast_message(update, context):
    users = get_all_users()
    message = "Здраствуйте, приглашаю Вас и Вашего ребёнка на консультацию, на который мы проверим произношение, понимание и правильность речи, а так же подготовку ребёнка к школе."
    successful = 0
    failed = 0

    for chat_id in users:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message)
            successful += 1
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {chat_id}: {e}")
            failed += 1
        await asyncio.sleep(0.1)

    await update.message.reply_text(f"Рассылка завершена. Успешно: {successful}, Неудачно: {failed}")



def add_user(username, chat_id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO users (username, chat_id)
        VALUES (?, ?)
        """, (username, chat_id))
        connection.commit()
        print(f"Користувач {username} успішно доданий.")
    except sqlite3.Error as e:
        print(f"Помилка при додаванні користувача: {e}")
    finally:
        connection.close()

def add_booking(chat_id, date_start, vozrast, quests, bron):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    try:
        cursor.execute( "SELECT id FROM users WHERE chat_id = ?", (chat_id))
        user_id = cursor.fetchone()
        if user_id:
            user_id = user_id[0]
            cursor.execute("""
            INSERT INTO bookings (user_id, date_start, vozrast, quests, bron)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, date_start, vozrast, quests, bron))
            connection.commit()
            print("Бронювання успішно додано.")
        else:
            print ("Користувача не знайдено в базі.")
    except sqlite3.Error as e:
        print(f"Помилка при додаванні бронювання : {e}")
    finally:
        connection.close()

def get_all_users():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT chat_id FROM users")
    users = cursor.fetchall()
    connection.close()
    return [user[0] for user in users]


async def start_command(update, context):
    username = update.effective_user.username or "NoUsername"
    chat_id = update.effective_user.id

    add_user(username, chat_id)
    inline_keyboard = [
        [InlineKeyboardButton("Консультация", callback_data="book")],
        [InlineKeyboardButton("График", callback_data="schedule")],
        [InlineKeyboardButton("Оставить отзыв", callback_data="comment")],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard)

    await update.message.reply_text(
        "Рада приветствовать Вас в боте, который поможет нам быстрее связаться. Выберите действие:",
        reply_markup=markup)


async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "information":
        await query.message.reply_text(
            "Уманец Мария Вадимовна - логопед, дефектолог. Работаю с детьми от 4-х лет, занимаюсь постановкой и коррекцией речи, а так же работаю с дизартрией. Занятия провожу онлайн. Номер телефона для дополнительной информации +380(98)-701-38-22.\n")
        return ConversationHandler.END

    elif query.data == "book":
        await query.message.reply_text("Чтобы записаться на консультацию, введите свои данные, как я могу к Вам обращаться и коротко про Ваш запрос.")
        return DATE_START


    elif query.data == "schedule":
        await query.message.reply_text("вторник 16.00 или четверг 16.00")
        return ConversationHandler.END

    elif query.data == "comment":
        comment_image_url = "image/leasson1.jpg"
        caption = "Вот как проходят мои занятия и отзывы о них!"
        try:
            await query.message.reply_photo(photo=comment_image_url, caption=caption)
        except FileNotFoundError as e:
            await query.message.reply_text(f"Помилка: файл {e.filename} не знайдено.")
        except Exception as e :
            await query.message.reply_text(f"Виникла помилка: {str(e)}")
            #await query.message.reply_text("Напишите свой отзыв после консультации, а так же занятий")
        return ConversationHandler.END


async def question(update, context):
    await update.message.reply_text('Стоимость занятий?')


async def date_start(update, context):
    context.user_data['date_start'] = update.message.text
    await update.message.reply_text("Введите дату и время занятия (например 20.11.2024, 16.00):")
    return VOZRAST


async def vozrast(update, context):
    context.user_data['vozrast'] = update.message.text
    await update.message.reply_text("Какой возраст ребёнка?")
    return GUESTS


async def guests(update, context):
    context.user_data['guests'] = update.message.text
    reply_keyboard = [["Консультация"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Выберите тип встречи:", reply_markup=markup)
    return BRON


async def bron(update, context):
    chat_id = update.effective_user.id
    context.user_data['bron'] = update.message.text
    booking_details = (
        f"Ваши данные для бронирования:\n"
        f"- Дата и время консультации: {context.user_data['date_start']}\n"
        f"- Возраст: {context.user_data['vozrast']}\n"
        f"- Тип занятия: {context.user_data['guests']}\n"
        "Если всё верно, я перезвоню Вам для подтверждения."
    )
    add_booking(
        chat_id,
        context.user_data['date_start'],
        context.user_data['vozrast'],
        context.user_data['guests'],
        context.user_data['bron']
    )
    await update.message.reply_text(booking_details, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Бронирование отменено. Возвращайтесь, когда будете готовы!",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


app.add_handler(CommandHandler("start", start_command))
booking_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(button_handler, pattern="^(information|book|schedule|comment)$")],
    states={
        DATE_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_start)],
        VOZRAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, vozrast)],
        GUESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, guests)],
        BRON: [MessageHandler(filters.TEXT & ~filters.COMMAND, bron)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_user=True
)

async def send_photos(update,context):
    photo_paths = ["image/hello.png", "image/review.png", "image/done.png"]

    try:
        media_group = [InputMediaPhoto(open(photo, "rb")) for photo in photo_paths]
        await update.message.reply_media_group(media_group)
    except FileNotFoundError as e:
        await update.message.reply_text(f"Помилка: файл {e.filename} не знайдено.")
    except Exception as e :
        await update.message.reply_text(f"Виникла помилка: {str(e)}")

app.add_handler(CommandHandler("sendphotos", send_photos))

setup_database()
app.add_handler(booking_handler)

if __name__ == '__main__':
    app.run_polling()
