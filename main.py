from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWM_API_KEY = os.getenv("OWM_API_KEY")


# Тестовая команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я SkyCastBot 🌤️ Готов показать тебе погоду :)")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи город, например: /weather Kyiv")
        return

    city = " ".join(context.args)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru"
    response = requests.get(url).json()

    if response.get("cod") != 200:
        await update.message.reply_text("Не удалось найти город 😢")
        return

    data = response
    weather_desc = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    wind = data["wind"]["speed"]

    await update.message.reply_text(
        f"🌍 Погода в {city}:\n"
        f"🌡 Температура: {temp}°C\n"
        f"🤗 Ощущается как: {feels_like}°C\n"
        f"💨 Ветер: {wind} м/с\n"
        f"🌈 Описание: {weather_desc.capitalize()}"
    )

async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи город, например: /forecast Kyiv")
        return

    city = " ".join(context.args)
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru"
    response = requests.get(url).json()

    if response.get("cod") != "200":
        await update.message.reply_text("Не удалось найти город 😢")
        return

    forecast_list = response["list"][:5]  # Берем ближайшие 5 интервалов (примерно 15 часов)
    msg = f"🔮 Прогноз погоды в {city.title()} на ближайшие часы:\n"

    for entry in forecast_list:
        time = entry["dt_txt"][11:16]  # Время в формате ЧЧ:ММ
        temp = entry["main"]["temp"]
        desc = entry["weather"][0]["description"]
        msg += f"\n🕒 {time}: {temp}°C, {desc.capitalize()}"

    await update.message.reply_text(msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("forecast", forecast))


    print("Бот запущен!")
    app.run_polling()
