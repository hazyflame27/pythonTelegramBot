from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
token = '611151625:AAFt98982QlxdELv4SNJLTOYqpVWxJfTP6s'


def start(bot, update):
  update.message.reply_text("I'm a bot, Nice to meet you!")

  
def convert_uppercase(bot, update):
  update.message.reply_text(update.message.text.upper())

  
def replyHello(bot, update):
    text = update.message.text
    if text == "Hi":
#         bot.send_message(update.message.chat_id, "Hello " + str(update.message.from_user))
        bot.send_message(update.message.chat_id, "Hello " + str(update.message.from_user.last_name) + " " + str(update.message.from_user.first_name))
    else:
        bot.send_message(update.message.chat_id, "Hello everybody")


def main():
  # Create Updater object and attach dispatcher to it
  updater = Updater(token)
  dispatcher = updater.dispatcher
  print("Bot started")

  # Add command handler to dispatcher
  start_handler = CommandHandler('start', start)
  dispatcher.add_handler(start_handler)
  
#   upper
#   upper_case = MessageHandler(Filters.text, convert_uppercase)
#   dispatcher.add_handler(upper_case)

# reply helo
  hello = MessageHandler(Filters.text, replyHello)
  dispatcher.add_handler(hello);

  # Start the bot
  updater.start_polling()

  # Run the bot until you press Ctrl-C
  updater.idle()


if __name__ == '__main__':
    main()
