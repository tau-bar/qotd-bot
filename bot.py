#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import random

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate("./key.json")
firebase_admin.initialize_app(cred)

firestore_db = firestore.client()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! This is the Izzu Quote Generator! To be inspired, try typing /inspireme! To see other commands, type /help!')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("""Available commands:
/about - Meet my maker 😉
/inspireme - To get a quote to inspire your day! ✨
/addquote (insert quote here) - To add a new quote to inspire others! 🧠""")

def about(update, context):
    update.message.reply_text("Created by @tau_bar! Enjoy :)")

def inspire(update, context):
    snapshots = firestore_db.collection(u'quotes').get()
    snapshots_len = len(snapshots)
    index = random.randint(0, snapshots_len - 1)
    # currently using linear search, could implement binary search here to search the array instead
    update.message.reply_text(snapshots[index].to_dict().get("quotetext"))
    
def add(update, context):
    if update.message.text == '/addquote' or update.message.text == '/addquote ': 
        update.message.reply_text("Use it by doing /addquote (type quote here)")
    else:   
        try:
            firestore_db.collection(u'quotes').add({'quotetext': update.message.text.split(" ", 1)[1]})
        except Exception as e: 
            update.message.reply_text("Sorry, something went wrong! 😢")
        else:
            update.message.reply_text("Quote successfully added! 😁")
        

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1452285290:AAETh1BiY2nykuLVp0eh5i9QEIpZL3VvDXg", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("inspireme", inspire))
    dp.add_handler(CommandHandler('addquote', add))
    dp.add_handler(CommandHandler('about', about))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()