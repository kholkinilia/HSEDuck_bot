import telebot

bot = telebot.TeleBot('2075815152:AAGrkae06TYfdCLIglo8fyLOzth1Byvq6JU')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    pass


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "Забудь этот номер...")


bot.polling(none_stop=True, interval=0)
