# @HSEDuck_bot
Just a python project in HSE. It has the following functionality:
## Features:
* buy/sell/buy short/sell short stock for the latest price on IEX stock exchange aka real broker.
* Compete with your friends for the title of the most successful(lucky) one.
* See rankings of challenges you are in.
* Search for companies' symbols and then see the latest price of the stock
* See the stats of your portfolio.
* Create multiple portfolios. Just so you can divide your portfolios by the risk level.
### Sandbox initially:
Initially the bot is in sandbox mode, which means that it's operating with not real information. 
To switch the bot to a real mode you either need to change the admin variable to your id
and write `/switch_type` when running the bot, or you can change the initial type int 
the `stock_handler.py` file.
### Non-integer money:
Yep, that's bad, I know. However, my hands resist to rewrite almost every
formula in `user_portfolio.py`. 
### You better not go broke:
When the amount of money becomes negative, strange things happen. Fortunately, it's
quite hard to get a negative amount of dollars in your portfolio,
because of the 100% restriction on selling short. (You still can spend money that guaranteed 
you won't go broke. This is, actually, quite the only way to go broke) So, be careful!
### English:
Sori for mai bad Englich :(
