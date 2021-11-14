import random
import stock_handler

challenges = dict()
users = dict()


def get_id():
    result = ""
    for i in range(20):
        result += chr(random.randint(ord('a'), ord('z')))
    return result


class Share:
    def __init__(self, amount, price, currency):
        # if currency == "_CURRENCY_" then the Share is a currency
        self.amount = amount
        self.total_price = price
        self.currency = currency


class Challenge:
    def __init__(self, users_id, is_portfolio, initial_money, duration, chat_id):
        self.id = get_id()
        self.users_id = set(users_id)
        self.is_main_challenge = is_portfolio
        self.initial_money = None
        self.left_time = None
        self.chat_id = users[0]
        self.finished = False
        self.host = users_id[0]
        if not is_portfolio:
            self.initial_money = initial_money
            self.left_time = duration
            self.chat_id = chat_id

    def finish(self, user_id):
        if self.host != user_id:
            return None
        self.finished = True
        rankings = [(users[user_id].get_wealth(), users[user_id].name) for user_id in users]
        rankings.sort(reverse=True)
        return rankings

    def add_user(self, user_id):
        if user_id in self.users_id:
            return False
        self.users_id.add(user_id)
        return True

    def remove(self, user_id):
        if user_id not in self.users_id:
            return False
        self.users_id.remove(user_id)
        if len(self.users_id) == 0:
            self.finished = True
        elif self.host == user_id:
            self.host = next(iter(self.users_id))
        return True


class User:
    def __init__(self, name, user_id):
        global challenges
        self.portfolios = dict()
        self.challenge_name = dict()
        self.challenges = set()
        self.shorted_stocks = dict()
        self.name = name
        self.id = user_id
        self.cur_challenge_id = 0
        self.main_portfolio_id = 0
        self.invested = dict()
        self.add_portfolio("Main portfolio")
        users[user_id] = self

    def add_portfolio(self, name):
        cur = Challenge([self.id], True, None, None, None)
        self.challenges.add(cur.id)
        self.cur_challenge_id = cur.id
        self.portfolios[cur.id] = dict()
        self.shorted_stocks[cur.id] = dict()
        challenges[cur.id] = cur
        self.main_portfolio_id = cur.id
        self.invested[cur.id] = 0
        self.challenge_name[cur.id] = name

    def switch_portfolio(self, chall_id):
        self.cur_challenge_id = chall_id

    def rename_portfolio(self, challenge_id, new_name):
        self.challenge_name[challenge_id] = new_name

    def get_wealth(self, data):
        cur_wealth = self.portfolios[self.cur_challenge_id]["USD"].amount
        for symbol in data:
            if symbol == 'error':
                break
            if symbol in self.portfolios[self.cur_challenge_id]:
                cur_wealth += data[symbol]["quote"]["latestPrice"] * self.portfolios[self.cur_challenge_id][
                    symbol].amount
            elif symbol in self.shorted_stocks[self.cur_challenge_id]:
                cur_wealth += -(data[symbol]["quote"]["latestPrice"] * self.shorted_stocks[self.cur_challenge_id][
                    symbol].amount - self.shorted_stocks[self.cur_challenge_id][symbol].total_price)
        return cur_wealth

    def show_portfolio(self):
        if not self.portfolios[self.cur_challenge_id]:
            return "You don't have any shares or currency yet."
        data = stock_handler.get_multiple_quote(self.get_stock_list())
        # TODO: make it work for all currencies
        cur_wealth = self.get_wealth(data)
        cur_invest = self.invested[self.cur_challenge_id]
        result = f">>>>>>>| {self.challenge_name[self.cur_challenge_id]} of {self.name} |<<<<<<<\n"
        result += f"TOTAL: {cur_invest} -> {'%.3f' % cur_wealth} USD\n"
        result += f"PRCNT: {'%.3f' % (100 * (cur_wealth - cur_invest) / cur_invest)}%\n"
        for symbol in self.portfolios[self.cur_challenge_id]:
            cur_price = self.portfolios[self.cur_challenge_id][symbol].total_price
            cur_amount = self.portfolios[self.cur_challenge_id][symbol].amount
            avg_price = cur_price / cur_amount
            cur_currency = self.portfolios[self.cur_challenge_id][symbol].currency
            result += f"--- {'/' if self.portfolios[self.cur_challenge_id][symbol].currency != '_CURRENCY_' else ''}" \
                      f"{symbol} --- \n"
            if self.portfolios[self.cur_challenge_id][symbol].currency != "_CURRENCY_":
                result += f"amount: {cur_amount}\n"
                real_price = float(data[symbol]["quote"]["latestPrice"])
                result += f"price: {'%.3f' % avg_price} -> {'%.3f' % real_price} {cur_currency}\n"
                result += f"total price: {'%.3f' % cur_price} -> {'%.3f' % (real_price * cur_amount)} {cur_currency}\n"
                result += f"change: {'%.3f' % (real_price * cur_amount - cur_price)} {cur_currency}\n"
                result += f"percent: {'%.3f' % (100 * (real_price * cur_amount - cur_price) / cur_price)}%\n"
            else:
                result += f"amount: {'%.3f' % cur_amount}\n"
        for symbol in self.shorted_stocks[self.cur_challenge_id]:
            cur_price = self.shorted_stocks[self.cur_challenge_id][symbol].total_price
            cur_amount = self.shorted_stocks[self.cur_challenge_id][symbol].amount
            avg_price = cur_price / cur_amount
            cur_currency = self.shorted_stocks[self.cur_challenge_id][symbol].currency
            result += f"--- " \
                      f"{'/' if self.shorted_stocks[self.cur_challenge_id][symbol].currency != '_CURRENCY_' else ''}" \
                      f" {symbol} (shorted) --- \n"
            if self.shorted_stocks[self.cur_challenge_id][symbol].currency != "_CURRENCY_":
                result += f"amount: {cur_amount}\n"
                real_price = float(data[symbol]["quote"]["latestPrice"])
                result += f"price: {'%.3f' % avg_price} -> {'%.3f' % real_price} {cur_currency}\n"
                result += f"total price: {'%.3f' % cur_price} -> {'%.3f' % (real_price * cur_amount)} {cur_currency}\n"
                result += f"change: {'%.3f' % -(real_price * cur_amount - cur_price)} {cur_currency}\n"
                result += f"percent: {'%.3f' % -(100 * (real_price * cur_amount - cur_price) / cur_price)}%\n"
            else:
                result += f"amount: {'%.3f' % cur_amount}\n"

        return result

    def get_stock_list(self):
        stock = []
        for symbol in self.portfolios[self.cur_challenge_id]:
            if self.portfolios[self.cur_challenge_id][symbol].currency != "_CURRENCY_":
                stock.append(symbol)
        for symbol in self.shorted_stocks[self.cur_challenge_id]:
            if self.shorted_stocks[self.cur_challenge_id][symbol].currency != "_CURRENCY_":
                stock.append(symbol)
        return stock

    def get_stats(self):
        # TODO: ask kellon, what should be in stats and implement
        result = f"Sorry, {self.name}, this feature is for VIP users only."
        return result

    def add_currency(self, amount, currency):
        if currency not in self.portfolios[self.cur_challenge_id]:
            self.portfolios[self.cur_challenge_id][currency] = Share(0, 0, "_CURRENCY_")
        self.invested[self.cur_challenge_id] += amount
        self.portfolios[self.cur_challenge_id][currency].amount += amount

    def buy_stock(self, symbol, amount, price, currency):
        symbol = symbol.upper()
        if currency not in self.portfolios[self.cur_challenge_id] or amount * price > \
                self.portfolios[self.cur_challenge_id][currency].amount:
            print(currency not in self.portfolios[self.cur_challenge_id],
                  amount * price > self.portfolios[self.cur_challenge_id][currency].amount)
            return False
        if symbol not in self.portfolios[self.cur_challenge_id]:
            self.portfolios[self.cur_challenge_id][symbol] = Share(0, 0, currency)
        self.portfolios[self.cur_challenge_id][symbol].amount += amount
        self.portfolios[self.cur_challenge_id][symbol].total_price += price * amount
        self.portfolios[self.cur_challenge_id][currency].amount -= amount * price
        return True

    def sell_stock(self, symbol, amount, price):
        symbol = symbol.upper()
        if symbol not in self.portfolios[self.cur_challenge_id] or amount > \
                self.portfolios[self.cur_challenge_id][symbol]:
            return False
        cur_total_price = self.portfolios[self.cur_challenge_id][symbol].total_price
        cur_amount = self.portfolios[self.cur_challenge_id][symbol].total_amount
        cur_currency = self.portfolios[self.cur_challenge_id][symbol].currency
        if cur_currency not in self.portfolios[self.cur_challenge_id]:
            self.portfolios[self.cur_challenge_id][cur_currency] = Share(0, 0, "_CURRENCY_")
        self.portfolios[self.cur_challenge_id][symbol].amount -= amount
        self.portfolios[self.cur_challenge_id][symbol].total_price -= amount * (cur_total_price / cur_amount)
        self.portfolios[self.cur_challenge_id][cur_currency].amount += amount * price
        if self.portfolios[self.cur_challenge_id][symbol].amount == 0:
            del self.portfolios[self.cur_challenge_id][symbol]
        return True

    def sell_short(self, symbol, amount, price, currency):
        symbol = symbol.upper()
        if currency not in self.portfolios[self.cur_challenge_id]:
            self.portfolios[self.cur_challenge_id][self.portfolios[self.cur_challenge_id].currency] \
                = Share(0, 0, "_CURRENCY_")
        if symbol not in self.shorted_stocks[self.cur_challenge_id]:
            self.shorted_stocks[self.cur_challenge_id][symbol] = Share(0, 0, currency)
        self.shorted_stocks[self.cur_challenge_id][symbol].amount += amount
        self.shorted_stocks[self.cur_challenge_id][symbol].total_price += price * amount
        return True

    def buy_short(self, symbol, amount, price):
        symbol = symbol.upper()
        if symbol not in self.shorted_stocks[self.cur_challenge_id] or self.shorted_stocks[self.cur_challenge_id][
           symbol].currency not in self.portfolios[self.cur_challenge_id]:
            return False
        cur_total_price = self.shorted_stocks[self.cur_challenge_id][symbol].total_price
        cur_amount = self.shorted_stocks[self.cur_challenge_id][symbol].amount
        cur_currency = self.shorted_stocks[self.cur_challenge_id][symbol].currency
        if self.portfolios[self.cur_challenge_id][cur_currency].amount + amount * (
                price - cur_total_price / cur_amount) < 0:
            return False
        self.shorted_stocks[self.cur_challenge_id][symbol].amount -= amount
        self.shorted_stocks[self.cur_challenge_id][symbol].total_price -= amount * (cur_total_price / cur_amount)
        self.portfolios[self.cur_challenge_id][cur_currency].amount += amount * (price - cur_total_price / cur_amount)
        return True


if __name__ == "__main__":
    kellon = User("Kellon", 1)
    kellon.add_currency(1000, "USD")
    kellon.buy_stock("qdel", 3, stock_handler.get_price("qdel"), "USD")
    kellon.buy_stock("baba", 1, stock_handler.get_price("baba"), "USD")
    kellon.add_portfolio("NEW")
    kellon.add_currency(10, "USD")
    kellon.sell_short("SPCE", 2, stock_handler.get_price("spce"), "USD")
    print(kellon.show_portfolio())
    kellon.buy_short("SPCE", 1, stock_handler.get_price("spce"))
    for port_id in kellon.challenges:
        kellon.switch_portfolio(port_id)
        print(kellon.show_portfolio())
