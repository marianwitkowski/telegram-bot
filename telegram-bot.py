from telegram import Update
from telegram.ext import ApplicationBuilder, \
    MessageHandler, CommandHandler, \
    ContextTypes, filters
import requests
import bs4
from dotenv import dotenv_values

async def get_data(icao):
    try:
        response = requests.get(f"https://www.getmetar.com/{icao.upper()}")
        if response.status_code != 200:
            raise
        return response.text
    except Exception as exc:
        raise Exception(str(exc))


async def get_metar_from_web(icao):
    try:
        txt = await get_data(icao)
        dom = bs4.BeautifulSoup(txt, 'lxml')
        return dom.find("h4").text.strip()
    except Exception as exc:
        raise Exception(str(exc))


async def get_taf_from_web(icao):
    try:
        txt = await get_data(icao)
        dom = bs4.BeautifulSoup(txt, 'lxml')
        return dom.find("h5").text.strip()
    except Exception as exc:
        raise Exception(str(exc))


async def get_metar(update: Update, context: ContextTypes) -> None:
    s = None
    try:
        s = " ".join( update.message.text.split(" ")[1:] )
        s = await get_metar_from_web(s)
    except Exception as exc:
        s = "Sorry, no data!"
    await update.message.reply_text(s)


async def get_taf(update: Update, context: ContextTypes) -> None:
    s = None
    try:
        s = " ".join(update.message.text.split(" ")[1:])
        s = await get_taf_from_web(s)
    except Exception as exc:
        s = "Sorry, no data!"
    await update.message.reply_text(s)


async def get_info(update: Update, context: ContextTypes) -> None:
    s = "/metar ICAO\n/taf ICAO\nexample: /metar EPWA"
    await update.message.reply_text(s)


async def echo(update: Update, context: ContextTypes) -> None:
    """Echo the user message."""
    await update.message.reply_text(f"Don't understand: {update.message.text}")


config = dotenv_values(".env")
app = ApplicationBuilder().token(config.get("API_KEY")).build()

app.add_handler(CommandHandler("metar", get_metar))
app.add_handler(CommandHandler("taf", get_taf))
app.add_handler(CommandHandler("start", get_info))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()