import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from datetime import datetime
import logging
import os

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(BASE_DIR, 'credentials.json')
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open("Health_Tracker").sheet1  # Убедитесь, что таблица называется "Health_Tracker"

# Определение состояний для ConversationHandler
(ENERGY, MOOD, SLEEP_QUALITY, SLEEP_DURATION, SLEEP_DEEP, SLEEP_RAPID, CRAVING, AVERAGE_PULSE, NUTRITION_TRACKING, CALORIES, PROTEINS, FATS, CARBS, STEPS, WORKOUT, SQUAT, BENCH_PRESS, PULL_UPS, MILITARY_PRESS, WHAT_WAS_EASY, WHAT_HELD_BACK, ONE_THOUGHT) = range(22)

# Начало опроса
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Давай начнем опрос! Какой у тебя уровень энергии сегодня (от 1 до 10)?")
    context.user_data['responses'] = {'Дата': datetime.now().strftime('%Y-%m-%d')}
    return ENERGY

# Обработка ответов
async def energy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Энергия'] = update.message.text
    await update.message.reply_text("Какое у тебя настроение (от 1 до 10)?")
    return MOOD

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Настроение'] = update.message.text
    await update.message.reply_text("Качество сна (от 1 до 10)?")
    return SLEEP_QUALITY

async def sleep_quality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Сон качество'] = update.message.text
    await update.message.reply_text("Длительность сна (в часах, например, 7.5)?")
    return SLEEP_DURATION

async def sleep_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Сон Длительность'] = update.message.text
    await update.message.reply_text("Длительность глубокой фазы сна (в часах, например, 2.5)?")
    return SLEEP_DEEP

async def sleep_deep(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Сон Глубокая фаза'] = update.message.text
    await update.message.reply_text("Длительность быстрой фазы сна (в часах, например, 1.5)?")
    return SLEEP_RAPID

async def sleep_rapid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Сон Быстрая фаза'] = update.message.text
    await update.message.reply_text("Была ли тяга к вредной еде или привычкам? (Да/Нет)")
    return CRAVING

async def craving(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Была ли тяга'] = update.message.text
    await update.message.reply_text("Какой у тебя средний пульс за день (в ударах в минуту, например, 75)?")
    return AVERAGE_PULSE

async def average_pulse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Средний пульс'] = update.message.text
    await update.message.reply_text("Вел ли ты трекинг питания? (Да/Нет или описание)")
    return NUTRITION_TRACKING

async def nutrition_tracking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Трекинг питания'] = update.message.text
    # Проверяем, велся ли трекинг питания (игнорируем регистр)
    if update.message.text.lower() != "нет":
        await update.message.reply_text("Сколько калорий ты потребил сегодня (примерно, в ккал)?")
        return CALORIES
    else:
        # Если трекинга не было, ставим прочерки и переходим к следующему вопросу
        context.user_data['responses']['Питание ккал'] = "-"
        context.user_data['responses']['Белки'] = "-"
        context.user_data['responses']['Жиры'] = "-"
        context.user_data['responses']['Углеводы'] = "-"
        await update.message.reply_text("Сколько шагов ты прошел сегодня?")
        return STEPS

async def calories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Питание ккал'] = update.message.text
    await update.message.reply_text("Сколько белков (в граммах)?")
    return PROTEINS

async def proteins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Белки'] = update.message.text
    await update.message.reply_text("Сколько жиров (в граммах)?")
    return FATS

async def fats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Жиры'] = update.message.text
    await update.message.reply_text("Сколько углеводов (в граммах)?")
    return CARBS

async def carbs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Углеводы'] = update.message.text
    await update.message.reply_text("Сколько шагов ты прошел сегодня?")
    return STEPS

async def steps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Шагов пройдено'] = update.message.text
    await update.message.reply_text("Была ли тренировка? (Да/Нет или описание)")
    return WORKOUT

async def workout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Тренировка'] = update.message.text
    # Проверяем, была ли тренировка (игнорируем регистр)
    if update.message.text.lower() != "нет":
        await update.message.reply_text("Какой вес в приседаниях (в кг, например, 100)?")
        return SQUAT
    else:
        # Если тренировки не было, ставим прочерки и переходим к следующему вопросу
        context.user_data['responses']['Присяд кг'] = "-"
        context.user_data['responses']['Жим лежа кг'] = "-"
        context.user_data['responses']['Подтягивания кг'] = "-"
        context.user_data['responses']['Армейский жим кг'] = "-"
        await update.message.reply_text("Что сегодня давалось легко?")
        return WHAT_WAS_EASY

async def squat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Присяд кг'] = update.message.text
    await update.message.reply_text("Какой вес в жиме лежа (в кг, например, 80)?")
    return BENCH_PRESS

async def bench_press(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Жим лежа кг'] = update.message.text
    await update.message.reply_text("Какой вес в подтягиваниях (в кг, например, 10)?")
    return PULL_UPS

async def pull_ups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Подтягивания кг'] = update.message.text
    await update.message.reply_text("Какой вес в армейском жиме (в кг, например, 50)?")
    return MILITARY_PRESS

async def military_press(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Армейский жим кг'] = update.message.text
    await update.message.reply_text("Что сегодня давалось легко?")
    return WHAT_WAS_EASY

async def what_was_easy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Что давалось легко'] = update.message.text
    await update.message.reply_text("Что тянуло назад или мешало?")
    return WHAT_HELD_BACK

async def what_held_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Что тянуло назад'] = update.message.text
    await update.message.reply_text("Одна мысль или наблюдение за день?")
    return ONE_THOUGHT

# Завершение опроса и запись в Google Sheets
async def one_thought(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['responses']['Одна мысль или наблюдение'] = update.message.text
    
    # Формирование строки для записи в таблицу
    responses = context.user_data['responses']
    row = [
        responses['Дата'],
        responses['Энергия'],
        responses['Настроение'],
        responses['Сон качество'],
        responses['Сон Длительность'],
        responses['Сон Глубокая фаза'],
        responses['Сон Быстрая фаза'],
        responses['Была ли тяга'],
        responses['Средний пульс'],
        responses['Трекинг питания'],
        responses.get('Питание ккал', '-'),
        responses.get('Белки', '-'),
        responses.get('Жиры', '-'),
        responses.get('Углеводы', '-'),
        responses['Шагов пройдено'],
        responses['Тренировка'],
        responses.get('Присяд кг', '-'),
        responses.get('Жим лежа кг', '-'),
        responses.get('Подтягивания кг', '-'),
        responses.get('Армейский жим кг', '-'),
        responses['Что давалось легко'],
        responses['Что тянуло назад'],
        responses['Одна мысль или наблюдение']
    ]
    
    # Запись в Google Sheets
    sheet.append_row(row)
    await update.message.reply_text("Спасибо! Данные записаны в таблицу. Можешь начать новый опрос с /start.")
    
    # Очистка данных
    context.user_data.clear()
    return ConversationHandler.END

# Обработка отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Опрос отменен. Начни заново с /start.")
    context.user_data.clear()
    return ConversationHandler.END

# Обработка ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    
    bot_token = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')  # Использует переменную окружения или значение по умолчанию
    application = Application.builder().token(bot_token).build()
    

    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ENERGY: [MessageHandler(filters.TEXT & ~filters.COMMAND, energy)],
            MOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, mood)],
            SLEEP_QUALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, sleep_quality)],
            SLEEP_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, sleep_duration)],
            SLEEP_DEEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, sleep_deep)],
            SLEEP_RAPID: [MessageHandler(filters.TEXT & ~filters.COMMAND, sleep_rapid)],
            CRAVING: [MessageHandler(filters.TEXT & ~filters.COMMAND, craving)],
            AVERAGE_PULSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, average_pulse)],
            NUTRITION_TRACKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, nutrition_tracking)],
            CALORIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, calories)],
            PROTEINS: [MessageHandler(filters.TEXT & ~filters.COMMAND, proteins)],
            FATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, fats)],
            CARBS: [MessageHandler(filters.TEXT & ~filters.COMMAND, carbs)],
            STEPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, steps)],
            WORKOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, workout)],
            SQUAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, squat)],
            BENCH_PRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bench_press)],
            PULL_UPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, pull_ups)],
            MILITARY_PRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, military_press)],
            WHAT_WAS_EASY: [MessageHandler(filters.TEXT & ~filters.COMMAND, what_was_easy)],
            WHAT_HELD_BACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, what_held_back)],
            ONE_THOUGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, one_thought)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавление обработчиков
    application.add_handler(conv_handler)
    application.add_error_handler(error)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()