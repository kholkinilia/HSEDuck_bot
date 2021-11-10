import telebot
import stock_handler

bot = telebot.TeleBot("2075815152:AAGrkae06TYfdCLIglo8fyLOzth1Byvq6JU")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    pass


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    data = stock_handler.get_quote_info(message.text.lower())
    print(message.text)
    if data:
        company_name = message.text
        try:
            company_name = data["companyName"]
        except KeyError:
            pass
        latest_price = "unknown"
        try:
            latest_price = data["latestPrice"]
        except KeyError:
            pass
        currency = " of unknown currency"
        try:
            currency = data["currency"]
        except KeyError:
            pass
        bot.send_message(message.from_user.id,
                         f"latest price of `{company_name}` `is` `{latest_price} {currency}`.")
    else:
        bot.send_message(message.from_user.id, 'Ты дурак или не дурак? Такого не бывает...')


bot.polling(none_stop=True, interval=0)
