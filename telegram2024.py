# 7581620320:AAEfu4zc2kfr6iSLarP6bYHX8zK5tLNatuI
from telegram import InputMediaPhoto, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, \
    MessageHandler, filters

# Стадії конверсії
DATE_START, VOZRAST, GUESTS, BRON = range(4)
app = ApplicationBuilder().token('7581620320:AAEfu4zc2kfr6iSLarP6bYHX8zK5tLNatuI').build()


async def start(update, context):
    await update.message.reply_text(
        "Рада приветствовать Вас в боте, который поможет нам быстрее связаться\n"
        "Я помогу Вам с записью на консультацию, выбором удобного времени и обратной связью после консультации.\n"
        "/information - Уманец Мария Вадимовна - логопед, дефектолог. Работаю с детьми от 4-х лет, занимаюсь постановкой и коррекцией речи, а так же работаю с дизартрией. Занятия провожу онлайн. Номер телефона для дополнительной информации +380(98)-701-38-22.\n"
        "/book - запись на консультацию\n"
        "/schedule - вторник 16.00, четверг 16.00\n"
        "/comment - Напишите свой отзыв после консультации, а так же занятий"
    )


async def start_command(update, context):
    inline_keyboard = [
        [InlineKeyboardButton("запись на консультацию", callback_data="book")],
        [InlineKeyboardButton("вторник 16.00, четверг 16.00", callback_data="schedule")],
        [InlineKeyboardButton("Напишите свой отзыв после консультации, а так же занятий", callback_data="comment")],
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

    elif query.data == "book":
        await query.message.reply_text("запись на консультацию")
        return DATE_START


    elif query.data == "schedule":
        await query.message.reply_text("вторник 16.00, четверг 16.00")

    elif query.data == "comment":
        await query.message.reply_text("Напишите свой отзыв после консультации, а так же занятий")


async def question(update, context):
    await update.message.reply_text('Стоимость занятий?')


async def date_start(update, context):
    context.user_data['date_start'] = update.message.text
    await update.message.reply_text("Введите дату и время занятия (например 2024-11-20, 16.00):")
    return VOZRAST


async def vozrast(update, context):
    context.user_data['vozrast'] = update.message.text
    await update.message.reply_text("Какой возраст ребёнка?")
    return GUESTS


async def guests(update, context):
    context.user_data['guests'] = update.message.text
    reply_keyboard = [["Консультация, Занятие"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Выберите тип встречи:", reply_markup=markup)
    return BRON


async def bron(update, context):
    context.user_data['bron'] = update.message.text
    booking_details = (
        f"Ваши данные для бронирования:\n",
        f"- Дата и время занятия: {context.user_data['date_start']}\n"
        f"- Возраст: {context.user_data['vozrast']}\n"
        f"- Тип занятия: {context.user_data['guests']}\n"
        "Если всё верно, я перезвоню Вам для подтверждения."
    )


async def cancel(update, context):
    await update.message.reply_text("Бронирование отменено. Возвращайтесь, когда будете готовы!",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


app.add_handler(CommandHandler("start", start_command))
booking_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(button_handler, pattern="^book$")],
    states={
        DATE_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_start)],
        VOZRAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, vozrast)],
        GUESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, guests)],
        BRON: [MessageHandler(filters.TEXT & ~filters.COMMAND, bron)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
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

app.add_handler(booking_handler)

if __name__ == '__main__':
    app.run_polling()
