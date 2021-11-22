import requests.exceptions
import telebot
import stock_handler
from user_portfolio import User
import user_portfolio
import json
from telebot import types

bot = telebot.TeleBot("2075815152:AAGrkae06TYfdCLIglo8fyLOzth1Byvq6JU")


class State:
    HOME = 0
    PORTFOLIO = 1
    RENAME_PORTFOLIO = 2
    SWITCH_PORTFOLIO = 3
    CREATE_PORTFOLIO = 4
    SEARCH = 5
    BUY = 6
    SELL = 7
    SELL_SHORT = 8
    BUY_SHORT = 9
    CHALLENGE = 10
    RENAME_CHALLENGE = 11
    CREATE_CHALLENGE = 12
    SWITCH_CHALLENGE = 13
    ADD_MONEY = 14


# bot.send_message(chat_id, "Choose what you want to do: ", reply_markup=markup)
use_buttons_message = "Please, use buttons to interact with the bot. If you don't see them, click on /show_buttons."
users = user_portfolio.users
challenges = user_portfolio.challenges
state = dict()
search_history = dict()
buying = dict()
selling = dict()
buying_short = dict()
selling_short = dict()

HISTORY_SIZE = 4


def save():
    user_portfolio.save()
    f = open("main_stuff.json", "w")
    f.write(json.dumps(get_dict()))
    f.close()


def restore():
    global users, challenges
    try:
        f = open("main_stuff.json", "r")
        set_dict(json.loads(f.readline()))
        f.close()
        user_portfolio.restore()
        print("Restored last save successfully")
    except FileNotFoundError:
        print("Nothing to restore")
    # print(id(users))
    # print(id(user_portfolio.users))
    users = user_portfolio.users
    challenges = user_portfolio.challenges
    # print(id(users) == id(user_portfolio.users))


def get_dict():
    result = {
        "state": state,
        "search_history": search_history,
        "buying": buying,
        "selling": selling,
        "buying_short": buying_short,
        "selling_short": selling_short
    }
    return result


def set_dict(d):
    global state, search_history, buying, selling, buying_short, selling_short
    state = d["state"]
    search_history = d["search_history"]
    buying = d["buying"]
    selling = d["selling"]
    buying_short = d["buying_short"]
    selling_short = d["selling_short"]


def add_to_search_history(user_id, symbol):
    new_history = [symbol]
    for s in search_history[user_id]:
        if s != symbol:
            new_history.append(s)
    if len(new_history) > HISTORY_SIZE:
        new_history.pop()
    search_history[user_id] = new_history


def get_markup(user_id):
    state_id = state[user_id][-1]
    if state_id == State.HOME:
        return get_home_markup()
    if state_id == State.PORTFOLIO:
        return get_portfolio_markup()
    if state_id == State.SWITCH_PORTFOLIO:
        return get_switch_portfolio_markup(user_id)
    if state_id == State.SEARCH:
        return get_search_markup(user_id)
    if state_id == State.CHALLENGE:
        return get_challenge_markup()
    if state_id == State.SWITCH_CHALLENGE:
        return get_switch_challenge_markup(user_id)
    return get_return_home_markup()


def get_return_home_markup():
    return types.ReplyKeyboardMarkup().row("◀Back", "🏠Return home")


def get_yes_no_markup():
    return types.ReplyKeyboardMarkup().row("Yes", "No")


def get_home_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row("💼Portfolio", "🔎Search")
    markup.row("🏅Challenges")
    return markup


def get_portfolio_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row("Show portfolio", "Get statistics")
    markup.row("Rename", "💵Add money")
    markup.row("Switch portfolio", "Delete portfolio", "Create portfolio")
    markup.row("◀Back", "🏠Return home")
    return markup


def get_search_markup(user_id):
    markup = types.ReplyKeyboardMarkup()
    last_views = search_history[user_id]
    if len(last_views) != 0:
        markup.row(f"📈Buy {last_views[0]}", f"📈Sell {last_views[0]}")
        markup.row(f"📉Sell short {last_views[0]}", f"📉Buy short {last_views[0]}")
        markup.row(*last_views)
    markup.row("◀Back", "🏠Return home")
    return markup


def get_challenge_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row("Show rankings")
    markup.row("Quit", "End challenge", "Rename", "Join message")
    markup.row("Switch challenge", "Create challenge")
    markup.row("◀Back", "🏠Return home")
    return markup


def get_switch_portfolio_markup(user_id):
    markup = types.ReplyKeyboardMarkup()
    markup.row("◀Back", "🏠Return home")
    portfolios = users[user_id].get_private_names()
    for name in portfolios:
        markup.row(name)
    return markup


def get_switch_challenge_markup(user_id):
    markup = types.ReplyKeyboardMarkup()
    markup.row("◀Back", "🏠Return home")
    challenge_list = users[user_id].get_challenge_names()
    for name in challenge_list:
        markup.row(name)
    return markup


def send_message(chat_id, message, user_id):
    bot.send_message(chat_id, message, reply_markup=get_markup(user_id))


admin_id = "476183318"


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    global admin_id
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    chat_id = message.chat.id
    if user_id not in users:
        users[user_id] = User(user_name, user_id)
        state[user_id] = [State.HOME]
        search_history[user_id] = []
        buying[user_id] = ""
        selling[user_id] = ""
        buying_short[user_id] = ""
        selling_short[user_id] = ""
        send_message(chat_id, "An empty private portfolio with name 'main' is created for you.", user_id)
    users[user_id].name = user_name
    cur_portfolio_type = "private" if users[user_id].in_private_portfolio() else "challenge"
    cur_portfolio_name = users[user_id].get_cur_portfolio_name()
    # is_group = (message.chat.type == "group")
    print(f"Message from {user_name} ({user_id}): '{message.text}'")
    if message.text == "/switch_type":
        if user_id == admin_id:
            stock_handler.switch_type()
            send_message(chat_id, f"You switched to {'sandbox' if stock_handler.get_type() else 'real'} information.",
                         user_id)
        else:
            send_message(chat_id, f"You are not allowed to do this :(", user_id)
        return
    if message.text == "/save":
        if user_id == admin_id:
            save()
            send_message(chat_id, "Successfully saved current state.", user_id)
        else:
            send_message(chat_id, "You are not allowed to save the state.", user_id)
        return
    if message.text.split("_")[0] == "join":
        challenge_id = message.text.split("_")[1]
        if challenge_id not in challenges:
            send_message(chat_id, "This is an invalid join query. "
                                  "You might have made a mistake while copying.", user_id)
            return
        if challenges[challenge_id].finished:
            send_message(chat_id, "This challenge is already finished", user_id)
            return
        if user_id in challenges[challenge_id].users_id:
            send_message(chat_id, f"You are already in that challenge. Local name for this challenge is: '"
                                  f"{users[user_id].get_challenge_name(challenge_id)}'", user_id)
            return
        users[user_id].join_challenge(challenge_id,
                                      users[challenges[challenge_id].host].get_challenge_name(
                                          challenge_id).split('(')[0])
        respond = f"You successfully joined '{users[user_id].get_challenge_name(challenge_id)}' challenge.\n" \
                  f"You have {users[user_id].invested[challenge_id]} USD to invest in stock.\n" \
                  f"Your portfolio is switched to '{users[user_id].get_challenge_name(challenge_id)}'" \
                  f" challenge portfolio."
        send_message(chat_id, respond, user_id)
        return
    if message.text == '/start':
        state[user_id] = [State.HOME]
        send_message(chat_id, f"Hello, {user_name}!", user_id)
        return
    if message.text == "/help":
        # TODO: write help
        return
    if message.text == "/show_buttons":
        send_message(chat_id, "Here are your buttons:", user_id)
        return
    if message.text == "🏠Return home":
        state[user_id] = [State.HOME]
        send_message(chat_id, "All activity is interrupted.", user_id)
        return
    if message.text == "◀Back":
        if len(state[user_id]) > 1:
            state[user_id].pop()
        else:
            state[user_id] = [State.HOME]
        send_message(chat_id, "All activity is interrupted", user_id)
        return
    if state[user_id][-1] == State.HOME:
        if message.text == "💼Portfolio":
            respond = f"You're currently at" \
                      f" '{cur_portfolio_name}'" \
                      f" {cur_portfolio_type} portfolio."
            state[user_id].append(State().PORTFOLIO)
            send_message(chat_id, respond, user_id)
            return
        if message.text == "🔎Search":
            respond = f"Enter a symbol of a stock."
            state[user_id].append(State().SEARCH)
            send_message(chat_id, respond, user_id)
            return
        if message.text == "🏅Challenges":
            respond = f"You're currently at" \
                      f" '{cur_portfolio_name}'" \
                      f" {cur_portfolio_type} portfolio."
            state[user_id].append(State().CHALLENGE)
            send_message(chat_id, respond, user_id)
            return
    if state[user_id][-1] == State().PORTFOLIO:
        if message.text == "Show portfolio":
            respond = users[user_id].show_portfolio()
            send_message(chat_id, respond, user_id)
            return
        if message.text == "Get statistics":
            respond = users[user_id].get_statistics()
            send_message(chat_id, respond, user_id)
            return
        if message.text == "Rename":
            respond = "Enter a new name of current portfolio. New name cannot contain '(' character:"
            state[user_id].append(State().RENAME_PORTFOLIO)
            send_message(chat_id, respond, user_id)
            return
        if message.text == "💵Add money":
            if not challenges[users[user_id].cur_challenge_id].is_private:
                send_message(chat_id, "This is a challenge portfolio, you can't add money to it.", user_id)
                return
            respond = "Enter how mush money in USD you want to add:"
            state[user_id].append(State().ADD_MONEY)
            send_message(chat_id, respond, user_id)
            return
        if message.text == "Switch portfolio":
            respond = "Choose portfolio to switch to from the list:"
            state[user_id].append(State().SWITCH_PORTFOLIO)
            send_message(chat_id, respond, user_id)
            return
        if message.text == "Create portfolio":
            respond = "Enter a name of a new private portfolio (a name cannot contain '(' character)" \
                      " and an initial amount of money in it:\nExample: 'My new portfolio 1000'"
            state[user_id].append(State().CREATE_PORTFOLIO)
            send_message(chat_id, respond, user_id)
            return
    if state[user_id][-1] == State.RENAME_PORTFOLIO:
        new_name = message.text.strip(' \n\v\t\r')
        if new_name.find("(") != -1:
            send_message(chat_id, "New name can't contain '(' character, please enter a new name again:", user_id)
            return
        users[user_id].rename_portfolio(new_name)
        respond = f"The {cur_portfolio_type} portfolio " \
                  f"'{cur_portfolio_name}'" \
                  f" now renamed to '{users[user_id].get_cur_portfolio_name()}'."
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        return
    if state[user_id][-1] == State.ADD_MONEY:
        msg = message.text.strip().split()
        if len(msg) > 1 or not msg[0].isdigit():
            send_message(chat_id, "Invalid message, please insert a number:", user_id)
            return
        users[user_id].add_currency(int(msg[0]), "USD")
        respond = f"Successfully added {msg[0]} USD to '{cur_portfolio_name}' {cur_portfolio_type} profile"
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        return
    if state[user_id][-1] == State.SWITCH_PORTFOLIO:
        if message.text not in users[user_id].get_private_names():
            send_message(chat_id, "Please choose a portfolio from the list", user_id)
            return
        users[user_id].switch_portfolio(users[user_id].get_id_by_name(message.text))
        respond = f"Your current portfolio is '{users[user_id].get_cur_portfolio_name()}'"
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        return
    if state[user_id][-1] == State.CREATE_PORTFOLIO:
        msg = message.text.strip().split()
        name = ""
        print(msg)
        for i in range(len(msg) - 1):
            name += msg[i] + (" " if i != len(msg) - 2 else "")
        if name == "" or not msg[-1].isdigit():
            send_message(chat_id, "Please enter a valid name and a number.\n Example: 'New portfolio 1000'", user_id)
            return
        if name.find("(") != -1:
            send_message(chat_id, "Name of portfolio cannot contain '(' character", user_id)
            return
        users[user_id].add_portfolio(name)
        users[user_id].add_currency(int(msg[-1]), "USD")
        respond = f"Successfully created a new " \
                  f"'{users[user_id].get_cur_portfolio_name()}' private portfolio" \
                  f" with {msg[-1]} USD.\n Your current portfolio switched to the created one."
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        return
    if state[user_id][-1] == State.SEARCH:
        cur_message = message.text.strip().split()
        if len(cur_message) == 1:
            cur_message[0] = cur_message[0].upper()
            data = stock_handler.get_quote(cur_message[0])
            if not data:
                send_message(chat_id, "Sorry, we don't know that symbol. :(\nTry another one", user_id)
                return
            company_name = cur_message[0]
            try:
                company_name = data["companyName"]
            except KeyError:
                pass
            latest_price = "unknown"
            try:
                latest_price = float(data["latestPrice"])
            except (KeyError, TypeError):
                pass
            currency = " of unknown currency"
            try:
                currency = data["currency"]
            except KeyError:
                pass
            print(data)
            if latest_price == "unknown" or currency != "USD":
                send_message(chat_id, "The company is bankrupt.", user_id)
                return
            can_afford = 0
            if currency == "USD":
                can_afford = users[user_id].can_afford(latest_price, currency)
            respond = f"===== {company_name} =====\n" \
                      f"Symbol: {cur_message[0]}\n" \
                      f"Latest price: {latest_price} {currency}\n" \
                      f"You can afford: {can_afford}\n" \
                      f"You already have: {users[user_id].can_sell(cur_message[0])}"
            add_to_search_history(user_id, cur_message[0])
            send_message(chat_id, respond, user_id)
            return
        if len(cur_message) == 2:
            if cur_message[0] == "📈Buy":
                cur_message[1] = cur_message[1].upper()
                data = stock_handler.get_quote(cur_message[1])
                if not data:
                    send_message(chat_id, "You can't buy that stock for some reason. Try another one!", user_id)
                    return
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
                if latest_price == "unknown" or currency != "USD":
                    send_message(chat_id, "You can't buy that stock for some reason. Try another one!", user_id)
                    return
                if users[user_id].can_afford(latest_price, currency) == 0:
                    send_message(chat_id, "You cannot afford even a one share. Earn money, before buying.", user_id)
                    return
                buying[user_id] = cur_message[1].upper()
                state[user_id].append(State.BUY)
                can_afford = users[user_id].can_afford(latest_price, currency)
                respond = f"==== Buying {cur_message[1]} ====\n" \
                          f"Buying with {cur_portfolio_type} portfolio: '{cur_portfolio_name}'\n" \
                          f"Available money: " \
                          f"{users[user_id].currency[users[user_id].cur_challenge_id][currency]} {currency}\n" \
                          f"Price {latest_price} {currency}\n" \
                          f"You can buy: {can_afford} share{'s' if can_afford > 1 else ''}.\n" \
                          f"Enter the amount to buy:"
                send_message(chat_id, respond, user_id)
                return
            if cur_message[0] == "📈Sell":
                cur_message[1] = cur_message[1].upper()
                if users[user_id].can_sell(cur_message[1]) == 0:
                    send_message(chat_id, f"You don't have any shares of {cur_message[1]}!", user_id)
                    return
                selling[user_id] = cur_message[1].upper()
                state[user_id].append(State.SELL)
                respond = f"==== Selling {cur_message[1]} ====\n" \
                          f"Selling with {cur_portfolio_type} portfolio: '{cur_portfolio_name}'.\n" \
                          f"You can sell:{users[user_id].can_sell(cur_message[1])}.\n" \
                          f"Price: {stock_handler.get_price(cur_message[1])} USD.\n" \
                          f"Enter the amount to sell:"
                send_message(chat_id, respond, user_id)
                return
        if len(cur_message) == 3:
            if cur_message[0] + cur_message[1] == "📉Sellshort":
                cur_message[2] = cur_message[2].upper()
                data = stock_handler.get_quote(cur_message[2])
                if not data:
                    send_message(chat_id, "We don't know about that stock. :(", user_id)
                    return
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
                if latest_price == "unknown" or currency != "USD":
                    send_message(chat_id, "You can't short a stock for some reason. Try another one!", user_id)
                    return
                selling_short[user_id] = cur_message[2].upper()
                state[user_id].append(State.SELL_SHORT)
                can_sell = users[user_id].can_afford(latest_price, currency)
                respond = f"==== Selling short {cur_message[2]} ====\n" \
                          f"Short with {cur_portfolio_type} portfolio: '{cur_portfolio_name}'.\n" \
                          f"Price: {latest_price} {currency}.\n" \
                          f"You can sell: {can_sell} share{'s' if can_sell > 1 else ''}.\n" \
                          f"Enter the amount of shares to short:"
                send_message(chat_id, respond, user_id)
                return
            if cur_message[0] + cur_message[1] == "📉Buyshort":
                cur_message[2] = cur_message[2].upper()
                if users[user_id].can_buy_short(cur_message[2], 0, "USD") == 0:
                    send_message(chat_id,
                                 f"You either didn't short this stock or can't afford buying back even one share",
                                 user_id)
                    return
                buying_short[user_id] = cur_message[2].upper()
                state[user_id].append(State.BUY_SHORT)
                price = stock_handler.get_price(cur_message[2])
                delta = users[user_id].get_delta_short(cur_message[2], price)
                currency = users[user_id].get_currency(cur_message[2])
                can_afford = users[user_id].can_buy_short(cur_message[2], delta, currency)
                respond = f"==== Buying short {cur_message[2]} ====\n" \
                          f"Buying short with {cur_portfolio_type} portfolio: '{cur_portfolio_name}'.\n" \
                          f"You can buy: {can_afford} share{'s' if can_afford > 1 else ''}.\n" \
                          f"Price: {price} {currency}.\n" \
                          f"Enter the amount to buy back:"
                send_message(chat_id, respond, user_id)
                return
    if state[user_id][-1] == State.BUY:
        if not message.text.isdigit():
            send_message(chat_id, "Please enter a number", user_id)
            return
        amount = int(message.text)
        if amount == 0:
            send_message(chat_id, "That is a strange amount to buy. o_o", user_id)
            return
        price = stock_handler.get_price(buying[user_id])
        if price <= 0:
            send_message(chat_id,
                         f"Something went wrong. We can't get a price of {buying[user_id]}. Please, try again later.",
                         user_id)
        if amount > users[user_id].can_afford(price, "USD"):
            send_message(chat_id, f"You can afford only {users[user_id].can_afford(price, 'USD')}"
                                  f" shares, but tried to buy {amount}. Please enter a valid amount.", user_id)
            return
        users[user_id].buy_stock(buying[user_id], amount, price, "USD")
        respond = f"Successfully bought {amount} share{'s' if amount > 1 else ''} of {buying[user_id]} " \
                  f"for {price} USD per each."
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        return
    if state[user_id][-1] == State.SELL:
        if not message.text.isdigit():
            send_message(chat_id, "Please enter a digit", user_id)
            return
        amount = int(message.text)
        if amount == 0:
            send_message(chat_id, "That is a strange amount to sell. o_o", user_id)
            return
        price = stock_handler.get_price(selling[user_id])
        if amount > users[user_id].can_sell(selling[user_id]):
            send_message(chat_id, f"You can sell only {users[user_id].can_sell(selling[user_id])}"
                                  f" shares, but tried to sell {amount}. Please enter a valid amount.", user_id)
            return
        users[user_id].sell_stock(selling[user_id], amount, price)
        respond = f"Successfully sold {amount} share{'s' if amount > 1 else ''} of {selling[user_id]} " \
                  f"for {price} USD per each."
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        return
    if state[user_id][-1] == State.SELL_SHORT:
        # TODO: make restriction on the amount of bought shares
        if not message.text.isdigit():
            send_message(chat_id, "Please enter a digit", user_id)
            return
        amount = int(message.text)
        if amount == 0:
            send_message(chat_id, "That is a strange amount to sell. o_o", user_id)
            return
        price = stock_handler.get_price(selling_short[user_id])
        if amount > users[user_id].can_afford(price, "USD"):
            send_message(chat_id, "You can't sell so much, because you cannot afford 100% raise of a stock.", user_id)
            return
        users[user_id].sell_short(selling_short[user_id], amount, price, "USD")
        respond = f"Successfully sold short {amount} share{'s' if amount > 1 else ''} of {selling_short[user_id]} " \
                  f"for {price} USD per each."
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        return
    if state[user_id][-1] == State.BUY_SHORT:
        if not message.text.isdigit():
            send_message(chat_id, "Please enter a digit", user_id)
            return
        amount = int(message.text)
        if amount == 0:
            send_message(chat_id, "That is a strange amount to buy. o_o", user_id)
            return
        price = stock_handler.get_price(buying_short[user_id])
        print(buying_short[user_id], price)
        delta = users[user_id].get_delta_short(buying_short[user_id], price)
        currency = users[user_id].get_currency(buying_short[user_id])
        print("can_buy: ", users[user_id].can_buy_short(buying_short[user_id], delta, currency))
        if amount > users[user_id].can_buy_short(buying_short[user_id], delta, currency):
            send_message(chat_id, f"You can buy short only "
                                  f"{users[user_id].can_buy_short(buying_short[user_id], delta, currency)}"
                                  f" shares, but tried to sell {amount}. Please enter a valid amount.", user_id)
            return
        users[user_id].buy_short(buying_short[user_id], amount, price)
        respond = f"Successfully bought short {amount} share{'s' if amount > 1 else ''} of {buying_short[user_id]} " \
                  f"for {price} {currency} per each."
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        return
    if state[user_id][-1] == State.CHALLENGE:
        if message.text == "Show rankings":
            if users[user_id].in_private_portfolio():
                send_message(chat_id, "You are now in private portfolio. "
                                      "Please switch to a challenge portfolio to see rankings.", user_id)
                return
            respond = f"====== Rank list of '{users[user_id].get_cur_portfolio_name()}'" \
                      f" ======\n" + challenges[users[user_id].cur_challenge_id].show_rankings()
            send_message(chat_id, respond, user_id)
            return
        if message.text == "Quit":
            if users[user_id].in_private_portfolio():
                send_message(chat_id, "You are now in private portfolio. You can't quit it.", user_id)
                return
            users[user_id].quit_challenge(users[user_id].cur_challenge_id)
            respond = f"Successfully quit '{cur_portfolio_name}' {cur_portfolio_type} portfolio"
            send_message(chat_id, respond, user_id)
            return
        if message.text == "End challenge":
            if users[user_id].in_private_portfolio():
                send_message(chat_id, "You are now in private portfolio. You can't end it.", user_id)
                return
            if challenges[users[user_id].cur_challenge_id].host != user_id:
                send_message(chat_id, f"You can't end that challenge because you are not the host."
                                      f"\nThe host is {users[challenges[users[user_id].cur_challenge_id].host].name}",
                             user_id)
                return
            respond = challenges[users[user_id].cur_challenge_id].show_rankings()
            users_id = set(challenges[users[user_id].cur_challenge_id].finish(user_id))
            challenge_id = users[user_id].cur_challenge_id
            print(len(users_id))
            for cur_id in users_id:
                print(cur_id, len(users_id))
                portfolio_changed = (users[cur_id].cur_challenge_id == challenge_id)
                users[cur_id].quit_challenge(challenge_id)
                bot.send_message(cur_id, f"{user_name} ended a '{cur_portfolio_name}' challenge."
                                         f" Here is a final rank list:\n" + respond)
                if portfolio_changed:
                    bot.send_message(cur_id, f"Your portfolio automatically changed to "
                                             f"'{users[cur_id].get_cur_portfolio_name()}' "
                                             f"private portfolio.")
                print(len(users_id))
            return
        if message.text == "Rename":
            respond = f"Enter a new name of current challenge. Current challenge is '{cur_portfolio_name}'"
            state[user_id].append(State().RENAME_CHALLENGE)
            send_message(chat_id, respond, user_id)
            return
        if message.text == "Switch challenge":
            respond = f"Choose challenge to switch to from the list below:"
            state[user_id].append(State().SWITCH_CHALLENGE)
            send_message(chat_id, respond, user_id)
            return
        if message.text == "Create challenge":
            respond = "Enter a name of a new challenge (a name cannot contain '(' character)" \
                      " and an initial amount of money for every participant in it:" \
                      "\nExample: 'Homeless challenge 1'"
            state[user_id].append(State().CREATE_CHALLENGE)
            send_message(chat_id, respond, user_id)
            return
    if state[user_id][-1] == State.RENAME_CHALLENGE:
        new_name = message.text.strip(' \n\v\t\r')
        if new_name.find("(") != -1:
            send_message(chat_id, "New name can't contain '(' character, please enter a new name again:", user_id)
            return
        users[user_id].rename_portfolio(new_name)
        respond = f"The challenge " \
                  f"'{cur_portfolio_name}'" \
                  f" now renamed to '{users[user_id].get_cur_portfolio_name()}'."
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        return
    if state[user_id][-1] == State.SWITCH_CHALLENGE:
        if message.text not in users[user_id].get_challenge_names():
            send_message(chat_id, "Please choose a challenge from the list", user_id)
            return
        users[user_id].switch_portfolio(users[user_id].get_id_by_name(message.text))
        respond = f"Your current challenge is '{users[user_id].get_cur_portfolio_name()}'"
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        return
    if state[user_id][-1] == State.CREATE_CHALLENGE:
        msg = message.text.strip().split()
        name = ""
        for i in range(len(msg) - 1):
            name += msg[i] + (" " if i != len(msg) - 2 else "")
        if name == "" or not msg[-1].isdigit():
            send_message(chat_id, "Please enter a valid name and a number separated by spaces.\n"
                                  " Example: 'New challenge 1000'", user_id)
            return
        if name.find("(") != -1:
            send_message(chat_id, "Name of challenge cannot contain '(' character", user_id)
            return
        users[user_id].add_challenge(name, int(msg[-1]), "USD")
        respond = f"Successfully created a new " \
                  f"'{users[user_id].get_cur_portfolio_name()}' challenge" \
                  f" with {msg[-1]} USD.\n Your current portfolio switched to the created one.\n" \
                  f"One can join a challenge by sending the text from the next message to the bot:\n"
        print(challenges[users[user_id].cur_challenge_id].initial_money)
        state[user_id].pop()
        send_message(chat_id, respond, user_id)
        send_message(chat_id, f"join_{users[user_id].cur_challenge_id}\n", user_id)
        return
    send_message(chat_id, use_buttons_message, user_id)


telebot.apihelper.SESSION_TIME_TO_LIVE = 5 * 60

while True:
    try:
        restore()
        bot.polling(none_stop=True, interval=0)
    except requests.exceptions.ConnectTimeout:
        save()
        print("========= CONNECTION TROUBLES, TRYING TO RERUN! ==========")
    except requests.exceptions.ReadTimeout:
        save()
        print("========= NO INTERNET, BOT STOPPED SAFELY ==========")
        break
