import pandas as pd
from trade_stat_logger._position import _Position
from datetime import datetime
from pytz import timezone
from yahoo_fin import stock_info as si
from warnings import warn

class Logger:

    def __init__(self, time_support=False):
        self.time_support = time_support
        self.positions = {}
        columns = ['security', 'shares', 'share price', 'profit']
        if time_support:
            columns.insert(0, 'time')
        self.trade_history = pd.DataFrame(columns=columns)

    def log(self, security, shares, share_price, time=None):
        profit = float('NaN')
        if security not in self.positions.keys():
            self.positions[security] = _Position(shares, share_price)
        else:
            if shares < 0:
                profit = self.positions[security].sell(abs(shares), share_price)
            else:
                profit = self.positions[security].buy(shares, share_price)

        data = [security, shares, share_price, profit]
        if self.time_support:
            if time is None:
                data.insert(0, datetime.now(tz=timezone('EST')))
            else:
                data.insert(0, time)
        append_index = len(self.trade_history)
        self.trade_history.loc[append_index] = data

    def log_clear_position(self, security, share_price, time=None):
        if security in self.positions.keys():
            self.positions[security].clear_position(share_price)

    def get_positions(self):
        return dict((k, v.to_dict()) for k, v in self.positions.items())

    def close_all_positions(self, get_price_func, closure_date):
        if not callable(get_price_func):
            raise TypeError('get_price_func should be a function')
        for k, _ in self.positions: # k is the name of the security
            self.log_clear_position(k, get_price_func(k, closure_date))

    def get_summary_statistics(self):
        # not 0 == true
        if not len(self.positions):
            warn('For most accurate performance results, please close out all holdings, which you can do with close_all_positions()')

        df = self.trade_history.dropna().copy()
        df['cumulative'] = df['profit'].cumsum()
        df['high'] = df['cumulative'].cummax()
        df['drawdown'] =  df['high'] - df['cumulative']
        max_drawdown = df['drawdown'].max()

        net_profit = df['profit'].sum()
        std_dev = df['profit'].std()

        df_gains = df[df['profit'] > 0]
        df_losses = df[df['profit'] < 0]

        winning_trades = len(df_gains)
        win_ratio = float(winning_trades / len(df))
        average_win = df_gains['profit'].mean()
        average_loss = df_losses['profit'].mean()
        kelly_criterion = win_ratio - (1 - win_ratio) / (average_win / average_loss)

        return {'profit': net_profit,
                'drawdown': max_drawdown,
                'std_dev': std_dev,
                'win_ratio': win_ratio,
                'average_win': average_win,
                'average_loss': average_loss,
                'kelly_criterion': kelly_criterion}

    def close_stock_positions(self, closure_date):
        def get_data(ticker, closure_date_inner):
            try:
                closure_df = si.get_data(ticker, closure_date_inner, closure_date_inner)
                open_price = closure_df.iloc[0]['open']
                self.log_clear_position(ticker, open_price)
            except AssertionError:
                warn(ticker + " is not a valid ticker")
        # validates and reformats user given date
        if closure_date is not None:
            if isinstance(closure_date, datetime):
                closure_date = closure_date.strftime('%d/%m/%Y')
            elif isinstance(closure_date, str):
                try:
                    datetime.datetime.strptime(closure_date, '%d/%m/%Y')
                except ValueError:
                    raise ValueError("Incorrect data format, should be DD/MM/YY")
            else:
                raise TypeError('Please enter a datetime.datetime object or a str date of format: DD/MM/YY')

        if closure_date is None:
            closure_date = datetime.today().date()
        # example on how to use close all positions
        self.close_all_positions(get_data, closure_date)





if __name__ == '__main__':
    logger = Logger()
    logger.log('aapl', 10, 5)
    print(logger.get_positions())
    logger.log('aapl', -10, 4)
    print(logger.get_positions())
    logger.log('aapl', 10, 4)
    print(logger.get_positions())
    logger.log('aapl', -10, 5)
    print(logger.get_positions())
    print(logger.get_summary_statistics())