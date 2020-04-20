# trade-stat-logger
Want to be able to easily log trades of any type of security and measure performance and analyze several factors, such as risk or return distribution? Then check out trade-stat-logger. If you like this project and other projects I've developed, I am looking for a summer internship, so feel free to contact me at shilewen@uw.edu.
## features (SimpleLogger)
- log trades: long and short
- get a statistical summary: 
  - net profit: self-explanatory
  - drawdown: vertical distance between peak and trough of net profits
  - volatility of returns: measures deviation of returns distribution
  - kurtosis: measures tails of returns distribution
  - probability of winning on a trade: self-explanatory
  - Kelly Criterion: estimate of optimal portfolio allocation
  - And more
- visualize performance:
  - visualize distribution of returns
  - analyze movement of gains or losses after every trade or over a period of time
## install
```
pip install trade-stat-logger
```
## Classes and methods
### SimpleLogger Methods:
```
SimpleLogger(datetime_support=False)
```
Constructs a new SimpleLogger object. Set datetime_support=True if you want to log the time at which the trade executed. Ignore future dt key word arguments if you wish to not support datetime logging.
***
```
log(security, shares, share_price, dt=None)
```
Log trades with this method. Shares is the number of shares you wish to purchase, set to negative to short/sell, and share_price is the price of a share. If dt is left as None, it will log current time, else set dt to a datetime object to log a custom time.
***
```
log_cp(security, share_price, dt=None)
```
Clear a position of given security at given share_price and log it. If dt is left as None, it will log current time, else set dt to a datetime object to log a custom time.
***
```
get_position(security)
```
Returns a tuple in the format (# shares, position size), position size is (# shares) * (average share price). It is slightly different from the format of get_positions.
```
get_positions()
```
Returns a dict of current security holdings in form of {security: {'shares': # shares, 'avg_share_price': average share price1}, another_security: {'shares': # shares, 'avg_share_price': average share price1}, ...}, where the key corresponding to a security is the string passed through the log() method.
***
```
clear_all_positions(get_price_func, closure_date)
```
Clears all security holdings, which is advised before calling methods that measure performance of trades. get_price_func should be a function such that get_price_func(security, closure_date) == price of security. For example:
```
logger = SimpleLogger()
...log trades...
def get_price(security, date):
    return api.get_price(security, date)
logger.clear_all_positions(get_price, some_date)
```
However, if you logged the tickers of stocks, you can use an easier alternative: `clear_stock_positions(closure_date)` will clear all stock positions
***
```
get_summary_statistics()
```
Returns a dictionary of various statistics in the form of {statistic1_name: value, statistics2_name: value,...}.
```
graph_statistics(time_axis=False, time_strformat='%m/%d/%Y', show_window=True)
```
Graphs the distribution of trade returns, net profit at the nth trade, and puts the summary statistics in a table, and shows it in a matplotlib popup window. If you would like to have the x-axis for the net profit graph be time, set time_axis=True, and optionally add a custom time format through time_strformat='%Y/%o/%u/%r format'. If you wish to get the plot, figure, and axes, the method will return these if you set show_window=False, and this will also mean the popup window will not appear.
## Examples
Other than the example down below, I have developed a MAC strategy using trade_stat_logger [here](https://github.com/shilewenuw/simple_mac_strategy "A simple MAC strategy using trade_stat_logger")
```
from datetime import timedelta
from random import randint
logger = SimpleLogger(datetime_support=True)

day_counter = 1
for x in range(0, 100):
    logger.log('fried chicken futures', randint(1, 100), randint(1, 100), dt=datetime.now()-timedelta(days=day_counter))
    logger.log('fried chicken futures', randint(-100, 1), randint(1, 130), dt=datetime.now()-timedelta(days=day_counter))
    day_counter += 1

# by setting show_window to false, the graphs aren't plotted, but instead returned
# axes is 2x2
plt, fig, axes = logger.graph_statistics(show_window=False)
# alter as you like, such as axes[0][0].set_xlabel('asdf')

# get current positions in securities (which we will then clear)
print(logger.get_positions())

# example of how to use clear_all_positions(),
#   replace get_price() with a real api call or any other price getter
def get_price(security, dt):
    return len(security) + dt.timetuple().tm_yday
logger.clear_all_positions(get_price, datetime.today())

# shows the statistics in a graphs in a pop up window. since it calls plt.show()
# when show_window is not set to false, all code beyond this point won't be executed
logger.graph_statistics()
    
```
## Hire me?
I am looking for a summer internship, contact me at shilewen@uw.edu if interested.
## Future features
- more time support for SimpleLogger, including time analysis on returns
- I will add a ComplexLogger, which will be built upon SimpleLogger, and it will support initial portfolio size, ROI, and many more.
- KellyLogger, which will dynamically return Kelly Criterion scores based on trade logs
