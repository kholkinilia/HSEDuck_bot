from queue import Queue


class State:
    INITIAL = 0
    EARNING_MONEY = 1
    BUYING_SHARE = 2
    GOING_SHORT = 3
    CHECKING_STOCK = 4


class Position:
    def __init__(self, amount=0, price=0, currency="USD"):
        self.amount = amount
        self.price = price
        self.currency = currency
        self.recently_viewed_stocks = Queue()


class User:
    MAX_VIEWED_LIST_LENGTH = 4

    def __init__(self, name):
        self.name = name
        self.portfolio = dict()
        self.currency_amount = dict()
        self.state = State.INITIAL
        self.viewed_stocks = Queue()

    def can_afford(self, need_amount, currency):
        if currency not in self.currency_amount:
            return False
        return self.currency_amount[currency] <= need_amount

    def buy_symbol(self, symbol, amount, price, currency):
        symbol = symbol.upper()
        if amount == 0:
            return f"You rejected to buy {symbol}"
        if not self.can_afford(price * amount, currency):
            return f"You don't have enough {currency}.\nYou have: " \
                   f"{0 if currency not in self.currency_amount else self.currency_amount[currency]} {currency}, " \
                   f"but need {price * amount} {currency}."
        if symbol not in self.portfolio:
            self.portfolio[symbol] = Position(0, 0, currency)
        self.currency_amount[currency] -= amount * price
        self.portfolio[symbol].amount += amount
        self.portfolio[symbol].price += price
        return f"Bought {amount} share{'s' if amount > 1 else ''} of {symbol} for {amount * price} {currency}."

    def print_portfolio(self):
        if not self.portfolio and not self.currency_amount:
            return "You don't have any shares or currency yet."
        result = f"======= {self.name} =======\n"
        if self.portfolio:
            result += f">>>>>| Stock |<<<<<\n"
        for symbol in self.portfolio:
            result += f"--- {symbol} --- \n" \
                      f"amount: {self.portfolio[symbol].amount}\n" \
                      f"avg price: {self.portfolio[symbol].price / self.portfolio[symbol].amount} " \
                      f"{self.portfolio[symbol].currency}\n" \
                      f"total price: {self.portfolio[symbol].price} {self.portfolio[symbol].currency}\n"
        if self.currency_amount:
            result += f">>>>>| Currency |<<<<<\n"
        for currency in self.currency_amount:
            result += f"--- {currency}\n amount: {self.currency_amount[currency]}\n"
        return result

    def add_currency(self, amount, currency):
        if currency not in self.currency_amount:
            self.currency_amount[currency] = 0
        self.currency_amount[currency] += amount
        return f"{amount} {currency} are successfully added to your wallet."

    def add_viewed_stock(self, symbol):
        symbol = symbol.upper()
        if symbol not in self.get_viewed_list():
            self.viewed_stocks.put(symbol)
            if self.viewed_stocks.qsize() == User.MAX_VIEWED_LIST_LENGTH + 1:
                self.viewed_stocks.get()
        else:
            self.move_up_in_viewed(symbol)

    def move_up_in_viewed(self, symbol):
        symbol = symbol.upper()
        q = Queue()
        while not self.viewed_stocks.empty():
            cur_symbol = self.viewed_stocks.get()
            if cur_symbol == symbol:
                continue
            q.put(cur_symbol)
        q.put(symbol)
        self.viewed_stocks = q

    def get_viewed_list(self):
        result = []
        q = Queue()
        while not self.viewed_stocks.empty():
            result.append(self.viewed_stocks.get())
            q.put(result[-1])
        self.viewed_stocks = q
        return result
