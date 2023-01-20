
import openai
import re
import random
import httpx
import traceback

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus
from rich import print
from utils import printlog, no_can_do

import config



async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await no_can_do(update, context):
        return
    if update.effective_chat.id in [config.ID_TIMELINE]:
        try:
            this_user = await context.bot.get_chat_member(update.message.chat.id, update.effective_user.id)
        except Exception as e:
            return
        if this_user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return

    elif update.effective_chat.id not in [config.ID_ASPHALTO, config.ID_DIOCHAN, config.ID_LOTTO, config.ID_RITALY, config.ID_NINJA, ] and update.message.from_user.id != config.ID_TRIF:
        return

    model = 'text-davinci-001'

    if '--003' in context.args:
        model = 'text-davinci-003'
    price_per_1k = 0.02

    try:

        input = update.message.text[4:].replace('--003 ', '')

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config.OPENAI_API_KEY}',
        }

        data = {
            "prompt": f"{input}",
            "model": model,
            "temperature": 1,
            "max_tokens": 300,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        
        async with httpx.AsyncClient() as session:
            r = await session.post("https://api.openai.com/v1/completions", json=data, headers=headers)
        response = r.json()



        output = response['choices'][0]['text'].strip()

        total_tkns = response['usage']['total_tokens']
        total_price = (price_per_1k/1000)*total_tkns
        rounded_price = str(round(total_price, 4))
        if not 'openai_stats' in context.chat_data:
            context.chat_data['openai_stats'] = {}

        if not update.effective_user.id in context.chat_data['openai_stats']:
            context.chat_data['openai_stats'][update.effective_user.id] = {}
        
        context.chat_data['openai_stats'][update.effective_user.id]['total_tokens'] = context.chat_data['openai_stats'][update.effective_user.id].get('total_tokens', 0) + total_tkns
        context.chat_data['openai_stats'][update.effective_user.id]['total_price'] = context.chat_data['openai_stats'][update.effective_user.id].get('total_price', 0) + total_price

        await printlog(update, "interroga OpenAI", f"{total_tkns} tokens, circa ${rounded_price}")

        await update.message.reply_html(f"<b>{input}</b>\n{output}\n<i>______</i>\n<i>Questo messaggio è costato circa ${rounded_price}</i>")

    except Exception as e:
        print(traceback.format_exc())
        await update.message.reply_text(f"Stong rott")

async def openai_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await no_can_do(update, context):
        return
    if update.effective_chat.id in [config.ID_TIMELINE]:
        try:
            this_user = await context.bot.get_chat_member(update.message.chat.id, update.effective_user.id)
        except Exception as e:
            return
        if this_user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return

    elif update.effective_chat.id not in [config.ID_ASPHALTO, config.ID_DIOCHAN, config.ID_LOTTO, config.ID_RITALY, config.ID_NINJA, ] and update.message.from_user.id != config.ID_TRIF:
        return

    tokens = context.chat_data['openai_stats'][update.effective_user.id].get('total_tokens', 0)
    money = context.chat_data['openai_stats'][update.effective_user.id].get('total_price', 0)
    money = str(round(money, 4))

    await printlog(update, "chiede le statistiche OpenAI")
    await update.message.reply_text(f"Token generati totali: {tokens}\nCosto totale: ${money} ")


async def ai_blank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await no_can_do(update, context):
        return

    if update.effective_chat.id in [config.ID_DIOCHAN, config.ID_RITALY, config.ID_ASPHALTO]:
        pass
    else:
        if update.effective_user.id in config.ADMINS:
            pass
        else:
            return
    await printlog(update, "interroga OpenAI")

    try:
        input = update.message.text[7:]

        if input.count("BLANK") != 1:
            await update.message.reply_text("Devi inserire un BLANK nel testo.")
            return

        fixes = re.split('(BLANK)', input)

        openai.api_key = config.OPENAI_API_KEY
        response = openai.Completion.create(
            engine="text-davinci-001",
            prompt=f"{fixes[0]}",
            suffix=f"{fixes[2]}",
            temperature=0.9,
            max_tokens=300,
            top_p=1,
            frequency_penalty=0.2,
            presence_penalty=0.5
        )
        output = response['choices'][0]['text'].replace("\n\n", "\n")

        await update.message.reply_html(f"{fixes[0]}<b>{output}</b>{fixes[2]}")

    except Exception as e:
        await update.message.reply_text(f"{e}")


async def ai_tarocchi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await no_can_do(update, context):
        return

    try:
        input_list = [
            "previsioni dei tarocchi di oggi",
            "tarocchi previsioni del giorno",
            "le previsioni di oggi coi tarocchi",
            "cosa accadrà oggi secondo i tarocchi",
            "tarocchi: le previsioni odierne",
            "lettura dei tarocchi di oggi"
        ]

        input = random.choice(input_list)

        openai.api_key = config.OPENAI_API_KEY
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{input}",
            temperature=1,
            max_tokens=300,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        output = response['choices'][0]['text'].strip()
        await printlog(update, "chiede i tarocchi ad OpenAI")
        await update.message.reply_html(f"<b>{input}</b>\n{output}")

    except Exception as e:
        await update.message.reply_text(f"{e}")
