from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import configparser
import logging
import redis
from ChatGPT_HKBU import HKBU_ChatGPT


global redis1


def echo(update: Update, context: CallbackContext) -> None:
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Helping you helping you.')

def add(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        msg = context.args[0]
        logging.info(msg)
        redis1.incr(msg)

        update.message.reply_text('You have said ' + msg + ' for ' + 
                                redis1.get(msg) + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def equiped_chatgpt(update: Update, context: CallbackContext) -> None:
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=config['TELEGRAM']['ACCESS_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher

    global redis1, chatgpt
    redis1 = redis.Redis(
        host=config['REDIS']['HOST'],
        password=config['REDIS']['PASSWORD'],
        port=config['REDIS']['REDISPORT'],
        decode_responses=config['REDIS']['DECODE_RESPONSE'],
        username=config['REDIS']['USER_NAME']
    )

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                         level=logging.INFO)
    
    #echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    #dispatcher.add_handler(echo_handler)
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    dispatcher.add_handler(CommandHandler('add',add))
    dispatcher.add_handler(CommandHandler('help',help_command))



    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
