import pprint
import time

from telegram import Update
from telegram.ext import ContextTypes

from utils import printlog


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = time.time()
    start = time.perf_counter()
    m = await update.message.reply_html("Test fallito.")
    await m.edit_text(f"[{s}] Test fallito in {round((time.perf_counter() - start) * 1000)}ms")
    # print(f'{get_now()} {await get_display_name(update.effective_user)} in {await get_chat_name(update.message.chat.id)} testa tantissimo!')
    await printlog(update, "testa tantissimo")

    # print(update.to_json())
    # print()
    # user = await context.bot.get_chat_member(update.message.chat.id, update.effective_user.id)
    # print(user.to_json())

    # await alert(update, context, "ha testato tantissimo", "errore di prova")

    # pprint.pprint(sys.modules['space'])

async def getfile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    picture = update.message.reply_to_message.photo[-1]
    actual_picture = await picture.get_file()
    pprint.pprint(actual_picture.to_dict())