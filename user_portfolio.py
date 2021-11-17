import random
import stock_handler

# TODO: make money integers

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
    def __init__(self, users_id, is_private, initial_money, duration, chat_id):
        self.id = get_id()
        self.users_id = set(users_id)
        self.is_private = is_private
        self.initial_money = None
        self.left_time = None
        self.chat_id = users_id[0]
        self.finished = False
        self.host = users_id[0]
        if not is_private:
            self.initial_money = initial_money
            self.left_time = duration
            self.chat_id = chat_id

    def get_rankings(self):
        rankings = [(users[user_id].get_wealth(self.id, stock_handler.get_multiple_quote(
                     users[user_id].get_stock_list(self.id))),
                     users[user_id].name) for user_id in self.users_id]
        rankings.sort(reverse=True)
        return rankings

    def show_rankings(self):
        rankings = self.get_rankings()
        result = ""
        medals = "X🥇🥈🥉"
        rank = 1
        for participant in rankings:
            result += f"{medals[rank] if rank <= 3 else rank}| {'%.3f' % participant[0]} | {participant[1]}\n"
            rank += 1
        return result

    def finish(self, user_id):
        assert (self.host == user_id)
        self.finished = True
        return self.users_id

    def add_user(self, user_id):
        if user_id in self.users_id:
            return False
        self.users_id.add(user_id)
        return True

    def remove_user(self, user_id):
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
        self.currency = dict()
        self.challenge_name = dict()
        self.taken_name_counters = dict()
        self.shorted_stocks = dict()
        self.name = name
        self.id = user_id
        self.cur_challenge_id = 0
        self.invested = dict()
        self.add_portfolio("main")
        self.main_portfolio_id = self.cur_challenge_id
        users[user_id] = self

    def add_portfolio(self, name):
        cur = Challenge([self.id], True, None, None, None)
        self.cur_challenge_id = cur.id
        self.portfolios[cur.id] = dict()
        self.currency[cur.id] = dict()
        self.shorted_stocks[cur.id] = dict()
        challenges[cur.id] = cur
        self.invested[cur.id] = 0
        name_counter = self.get_name_counter(name)
        self.challenge_name[cur.id] = name + f"({name_counter})"
        self.taken_name_counters[name].add(name_counter)

    def get_private_names(self):
        result = []
        for key in self.challenge_name:
            if challenges[key].is_private:
                result.append(self.get_challenge_name(key))
        return result

    def get_challenge_names(self):
        result = []
        for key in self.challenge_name:
            if not challenges[key].is_private:
                result.append(self.get_challenge_name(key))
        return result

    def get_challenge_name(self, challenge_id):
        name = self.challenge_name[challenge_id]
        if name[len(name) - 3::] == "(0)":
            name = name[:len(name) - 3:]
        return name

    def get_name_counter(self, name):
        if name not in self.taken_name_counters:
            self.taken_name_counters[name] = set()
        name_counter = 0
        while name_counter in self.taken_name_counters[name]:
            name_counter += 1
        return name_counter

    def get_cur_portfolio_name(self):
        result = self.challenge_name[self.cur_challenge_id]
        print(result[len(result) - 3::])
        if result[len(result) - 3::] == "(0)":
            return result[:len(result) - 3:]
        return result

    def switch_portfolio(self, chall_id):
        self.cur_challenge_id = chall_id

    def rename_portfolio(self, new_name):
        # TODO: create a good name handling
        name = self.challenge_name[self.cur_challenge_id].split("(")
        name[1] = name[1][:len(name[1]) - 1:]
        name[1] = int(name[1])
        print(name)
        print(new_name)
        self.taken_name_counters[name[0]].remove(name[1])
        name_counter = self.get_name_counter(new_name)
        self.challenge_name[self.cur_challenge_id] = new_name + f"({name_counter})"
        self.taken_name_counters[new_name].add(name_counter)

    def get_id_by_name(self, name):
        if name.find("(") == -1:
            name += "(0)"
        for ch_id in self.challenge_name:
            if self.challenge_name[ch_id] == name:
                return ch_id

    def get_wealth(self, challenge_id, data):
        cur_wealth = self.currency[challenge_id]["USD"]
        for symbol in data:
            if symbol == 'error':
                continue
            if symbol in self.portfolios[challenge_id]:
                cur_wealth += data[symbol]["quote"]["latestPrice"] * self.portfolios[challenge_id][
                    symbol].amount
            if symbol in self.shorted_stocks[challenge_id]:
                cur_wealth += -(data[symbol]["quote"]["latestPrice"] * self.shorted_stocks[challenge_id][
                    symbol].amount - self.shorted_stocks[challenge_id][symbol].total_price)
        return cur_wealth

    def show_portfolio(self):
        if not self.portfolios[self.cur_challenge_id] and not self.currency[self.cur_challenge_id]:
            return "You don't have any shares or currency yet."
        data = stock_handler.get_multiple_quote(self.get_stock_list(self.cur_challenge_id))
        print(data, self.get_stock_list(self.cur_challenge_id))
        # TODO: make it work for all currencies
        cur_wealth = self.get_wealth(self.cur_challenge_id, data)
        cur_invest = self.invested[self.cur_challenge_id]
        result = f">>>>>>>| '{self.get_cur_portfolio_name()}' portfolio of {self.name} |<<<<<<<\n"
        result += f"total: {cur_invest} => {'%.3f' % cur_wealth} USD\n"
        result += f"prcnt: {'%.3f' % (100 * (cur_wealth - cur_invest) / cur_invest)}%\n"
        for currency in self.currency[self.cur_challenge_id]:
            result += f"{currency}: {'%.3f' % self.currency[self.cur_challenge_id][currency]}\n"
        for symbol in self.portfolios[self.cur_challenge_id]:
            cur_price = self.portfolios[self.cur_challenge_id][symbol].total_price
            cur_amount = self.portfolios[self.cur_challenge_id][symbol].amount
            avg_price = cur_price / cur_amount
            cur_currency = self.portfolios[self.cur_challenge_id][symbol].currency
            result += f"--- /{symbol} --- \n"
            result += f"amount: {cur_amount}\n"
            real_price = float(data[symbol]["quote"]["latestPrice"])
            result += f"price: {'%.3f' % avg_price} => {'%.3f' % real_price} {cur_currency}\n"
            result += f"total price: {'%.3f' % cur_price} => {'%.3f' % (real_price * cur_amount)} {cur_currency}\n"
            result += f"change: {'%.3f' % (real_price * cur_amount - cur_price)} {cur_currency}\n"
            result += f"percent: {'%.3f' % (100 * (real_price * cur_amount - cur_price) / cur_price)}%\n"
        for symbol in self.shorted_stocks[self.cur_challenge_id]:
            cur_price = self.shorted_stocks[self.cur_challenge_id][symbol].total_price
            cur_amount = self.shorted_stocks[self.cur_challenge_id][symbol].amount
            avg_price = cur_price / cur_amount
            cur_currency = self.shorted_stocks[self.cur_challenge_id][symbol].currency
            result += f"--- /{symbol} (shorted) --- \n"
            result += f"amount: {cur_amount}\n"
            real_price = float(data[symbol]["quote"]["latestPrice"])
            result += f"price: {'%.3f' % avg_price} => {'%.3f' % real_price} {cur_currency}\n"
            result += f"total price: {'%.3f' % cur_price} => {'%.3f' % (real_price * cur_amount)} {cur_currency}\n"
            result += f"change: {'%.3f' % -(real_price * cur_amount - cur_price)} {cur_currency}\n"
            result += f"percent: {'%.3f' % -(100 * (real_price * cur_amount - cur_price) / cur_price)}%\n"
        return result

    def get_stock_list(self, challenge_id):
        return list(self.portfolios[challenge_id].keys()) + \
               list(self.shorted_stocks[challenge_id].keys())

    def get_statistics(self):
        # TODO: ask kellon, what should be in stats and implement
        result = f"Sorry, {self.name}, this feature is for VIP users only."
        return result

    def add_currency(self, amount, currency):
        print(amount, currency)
        if amount == 0:
            return
        if currency not in self.currency[self.cur_challenge_id]:
            self.currency[self.cur_challenge_id][currency] = 0
        self.invested[self.cur_challenge_id] += amount
        self.currency[self.cur_challenge_id][currency] += amount

    def buy_stock(self, symbol, amount, price, currency):
        symbol = symbol.upper()
        if currency not in self.currency[self.cur_challenge_id] or amount * price > \
                self.currency[self.cur_challenge_id][currency]:
            return False
        if symbol not in self.portfolios[self.cur_challenge_id]:
            self.portfolios[self.cur_challenge_id][symbol] = Share(0, 0, currency)
        self.portfolios[self.cur_challenge_id][symbol].amount += amount
        self.portfolios[self.cur_challenge_id][symbol].total_price += price * amount
        self.currency[self.cur_challenge_id][currency] -= amount * price
        return True

    def sell_stock(self, symbol, amount, price):
        symbol = symbol.upper()
        if symbol not in self.portfolios[self.cur_challenge_id] or amount > \
                self.portfolios[self.cur_challenge_id][symbol].amount:
            return False
        cur_total_price = self.portfolios[self.cur_challenge_id][symbol].total_price
        cur_amount = self.portfolios[self.cur_challenge_id][symbol].amount
        cur_currency = self.portfolios[self.cur_challenge_id][symbol].currency
        if cur_currency not in self.currency[self.cur_challenge_id]:
            self.currency[self.cur_challenge_id][cur_currency] = 0
        self.portfolios[self.cur_challenge_id][symbol].amount -= amount
        self.portfolios[self.cur_challenge_id][symbol].total_price -= amount * (cur_total_price / cur_amount)
        self.currency[self.cur_challenge_id][cur_currency] += amount * price
        if self.portfolios[self.cur_challenge_id][symbol].amount == 0:
            del self.portfolios[self.cur_challenge_id][symbol]
        return True

    def sell_short(self, symbol, amount, price, currency):
        symbol = symbol.upper()
        if currency not in self.currency[self.cur_challenge_id]:
            self.currency[self.cur_challenge_id][currency] = 0
        if symbol not in self.shorted_stocks[self.cur_challenge_id]:
            self.shorted_stocks[self.cur_challenge_id][symbol] = Share(0, 0, currency)
        self.shorted_stocks[self.cur_challenge_id][symbol].amount += amount
        self.shorted_stocks[self.cur_challenge_id][symbol].total_price += price * amount
        return True

    def buy_short(self, symbol, amount, price):
        # TODO: fix, not working in challenge
        symbol = symbol.upper()
        if symbol not in self.shorted_stocks[self.cur_challenge_id] or self.shorted_stocks[self.cur_challenge_id][
            symbol].currency not in self.portfolios[self.cur_challenge_id]:
            return False
        cur_total_price = self.shorted_stocks[self.cur_challenge_id][symbol].total_price
        cur_amount = self.shorted_stocks[self.cur_challenge_id][symbol].amount
        cur_currency = self.shorted_stocks[self.cur_challenge_id][symbol].currency
        if self.currency[self.cur_challenge_id][cur_currency] + amount * (
                price - cur_total_price / cur_amount) < 0:
            return False
        self.shorted_stocks[self.cur_challenge_id][symbol].amount -= amount
        self.shorted_stocks[self.cur_challenge_id][symbol].total_price -= amount * (cur_total_price / cur_amount)
        self.currency[self.cur_challenge_id][cur_currency] += amount * (price - cur_total_price / cur_amount)
        return True

    def can_afford(self, price, currency):
        if currency not in self.currency[self.cur_challenge_id]:
            return 0
        return int(self.currency[self.cur_challenge_id][currency] // price)

    def can_sell(self, symbol):
        if symbol not in self.portfolios[self.cur_challenge_id]:
            return 0
        return self.portfolios[self.cur_challenge_id][symbol].amount

    def can_buy_short(self, symbol):
        if symbol not in self.shorted_stocks[self.cur_challenge_id]:
            return 0
        return self.shorted_stocks[self.cur_challenge_id][symbol].amount

    def in_private_portfolio(self):
        return challenges[self.cur_challenge_id].is_private

    def add_challenge(self, name, initial_money, currency):
        cur = Challenge([self.id], False, initial_money, None, None)
        self.cur_challenge_id = cur.id
        self.portfolios[cur.id] = dict()
        self.currency[cur.id] = dict()
        self.invested[cur.id] = 0
        self.shorted_stocks[cur.id] = dict()
        challenges[cur.id] = cur
        self.add_currency(initial_money, currency)
        name_counter = self.get_name_counter(name)
        self.challenge_name[cur.id] = name + f"({name_counter})"
        self.taken_name_counters[name].add(name_counter)

    def join_challenge(self, challenge_id, name):
        self.cur_challenge_id = challenge_id
        challenges[challenge_id].add_user(self.id)
        if challenge_id not in self.portfolios:
            self.portfolios[challenge_id] = dict()
            self.currency[challenge_id] = dict()
            self.shorted_stocks[challenge_id] = dict()
            self.invested[challenge_id] = 0
            self.add_currency(challenges[challenge_id].initial_money, "USD")
        name_counter = self.get_name_counter(name)
        self.challenge_name[challenge_id] = name + f"({name_counter})"
        self.taken_name_counters[name].add(name_counter)

    def quit_challenge(self, challenge_id):
        challenges[challenge_id].remove_user(self.id)
        if challenge_id == self.cur_challenge_id:
            self.cur_challenge_id = self.main_portfolio_id
        if challenges[challenge_id].finished:
            del self.portfolios[challenge_id]
            del self.challenge_name[challenge_id]
            del self.currency[challenge_id]
            del self.shorted_stocks[challenge_id]
            del self.invested[challenge_id]


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
    for port_id in kellon.challenge_name:
        kellon.switch_portfolio(port_id)
        print(kellon.show_portfolio())
