import telebot
from telebot import apihelper
import stock_handler
from user_portfolio import User, State
from telebot import types

bot = telebot.TeleBot("2075815152:AAGrkae06TYfdCLIglo8fyLOzth1Byvq6JU")

user = dict()
markup = dict()


def build_markups():
    markup[State.INITIAL] = types.ReplyKeyboardMarkup()
    markup[State.INITIAL].row(types.KeyboardButton("Show my stock portfolio"), types.KeyboardButton("$Earn money$"))
    markup[State.INITIAL].row(types.KeyboardButton("Buy stock"), types.KeyboardButton("Sell stock"))
    markup[State.INITIAL].row(types.KeyboardButton("Check the stock info"))
    markup[State.EARNING_MONEY] = types.ReplyKeyboardMarkup()
    markup[State.EARNING_MONEY].row(types.KeyboardButton("100 USD"), types.KeyboardButton("1000 USD"))
    markup[State.EARNING_MONEY].row(types.KeyboardButton("10000 USD"), types.KeyboardButton("100000 USD"))
    markup[State.EARNING_MONEY].row(types.KeyboardButton("Return home"))


def get_recent_views_markup(user_id):
    views_markup = types.ReplyKeyboardMarkup()
    views_list = user[user_id].get_viewed_list()[::-1]
    if views_list:
        views_markup.row(f"Buy last viewed ({views_list[0]})", f"Sell last viewed ({views_list[0]})")
    for i in range(1, len(views_list), 2):
        views_markup.row(views_list[i - 1], views_list[i])
    if len(views_list) % 2 == 1:
        views_markup.row(views_list[-1])
    views_markup.row("Return home")
    return views_markup


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id not in user:
        user[user_id] = User(str(message.from_user.first_name) + str(
            "" if not message.from_user.last_name else message.from_user.last_name))
    print(f"in chat:  {message.chat.first_name} (id={message.chat.id}) from member "
          f"{message.from_user.first_name} (id={message.from_user.id}): ", message.text,
          sep="")
    if user[user_id].state == State.INITIAL:
        if message.text == '/start':
            user[user_id].state = State.INITIAL
            bot.send_message(chat_id, "Choose what you want to do: ", reply_markup=markup[State.INITIAL])
        elif message.text == "Show my stock portfolio":
            bot.send_message(chat_id, user[user_id].print_portfolio())
        elif message.text == "$Earn money$":
            user[user_id].state = State.EARNING_MONEY
            bot.send_message(chat_id, "Choose how much money do you want to earn: ",
                             reply_markup=markup[State.EARNING_MONEY])
        elif message.text == "Check the stock info":
            user[user_id].state = State.CHECKING_STOCK
            bot.send_message(chat_id, "Write a stock symbol or choose from your recently viewed list:",
                             reply_markup=get_recent_views_markup(user_id))
            return
        else:
            bot.send_message(chat_id,
                             "Ты дурак или не дурак? На кнопки нажимать не умеешь..."
                             " (если их нет по какой-то причине - напиши /start)")
        return
    if user[user_id].state == State.EARNING_MONEY:
        if message.text == "Return home":
            user[user_id].state = State.INITIAL
            bot.send_message(chat_id, "Earning money is stopped. Choose what you want to do now: ",
                             reply_markup=markup[State.INITIAL])
        elif message.text in ["100 USD", "1000 USD", "10000 USD", "100000 USD"]:
            amount, currency = message.text.split()
            user[user_id].state = State.INITIAL
            bot.send_message(chat_id, user[user_id].add_currency(int(amount), currency),
                             reply_markup=markup[State.INITIAL])
        else:
            bot.send_message(chat_id,
                             "Invalid query for command: $Earn money$. Please use buttons to reply to the bot.",
                             reply_markup=markup[State.EARNING_MONEY])
        return
    if user[user_id].state == State.CHECKING_STOCK:
        if message.text == "Return home":
            user[user_id].state = State.INITIAL
            bot.send_message(chat_id, "Checking stocks is stopped. Choose what you want to do now: ",
                             reply_markup=markup[State.INITIAL])
            return
        data = stock_handler.get_quote(message.text)
        if not data:
            bot.send_message(chat_id, "This symbol is invalid, please enter symbol again.",
                             reply_markup=get_recent_views_markup(user_id))
            return
        user[user_id].add_viewed_stock(message.text)
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
        bot.send_message(chat_id,
                         f"latest price of `{company_name}` is {latest_price} {currency}.",
                         reply_markup=get_recent_views_markup(user_id))


build_markups()

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
bot.polling(none_stop=True, interval=0)
