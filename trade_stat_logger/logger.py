import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from trade_stat_logger._position import _Position
from datetime import datetime
from pytz import timezone
from yahoo_fin import stock_info as si
from warnings import warn
from statsmodels.stats.proportion import proportions_ztest


class SimpleLogger:
    def __init__(self, datetime_support=False):
        self.datetime_support = datetime_support
        self.positions = {}
        # columns = ['security', 'shares', 'share price', 'profit', 'return on trade size']
        columns = ['security', 'shares', 'share price', 'profit']
        if datetime_support:
            columns.insert(0, 'datetime')
        self.trade_history = pd.DataFrame(columns=columns)

    # call when you buy and sell securities
    def log(self, security, shares, share_price, dt=None):
        profit = float('NaN')
        if security not in self.positions.keys():
            self.positions[security] = _Position(shares, share_price)
        else:
            if shares < 0:
                profit = self.positions[security].sell(abs(shares), share_price)
            else:
                profit = self.positions[security].buy(shares, share_price)

        #data = [security, shares, share_price, profit, self.nan_division(profit, (abs(shares) * share_price))]
        data = [security, shares, share_price, profit]
        if self.datetime_support:
            if dt is None:
                data.insert(0, datetime.now(tz=timezone('EST')))
            else:
                data.insert(0, dt)
        append_index = len(self.trade_history)
        self.trade_history.loc[append_index] = data

    def log_cp(self, security, share_price, dt=None):
        if security in self.positions.keys():
            self.log(security, self.positions[security].get_shares(), share_price, dt=dt)

    def get_position(self, security):
        if security in self.positions.keys():
            return self.positions[security].to_tuple()
        else:
            return 0, 0

    def get_positions(self):
        return dict((k, v.to_dict()) for k, v in self.positions.items())

    def clear_all_positions(self, get_price_func, closure_date):
        if not callable(get_price_func):
            raise TypeError('get_price_func should be a function')
        for k, _ in self.positions.items():
            self.log_cp(k, get_price_func(k, closure_date))

    def graph_statistics(self, time_axis=False, time_strformat='%m/%d/%Y', show_window=True):
        stat_summary = self.get_summary_statistics()
        #
        if self.datetime_support and time_axis:
            df = self.trade_history.dropna()
            dts = df['datetime'].dt.strftime(time_strformat)
            profits = df['profit']
        else:
            profits = self.trade_history['profit'].dropna()
        cumulative_profits = profits.cumsum()
        fig, axes = plt.subplots(2, 2, figsize=(15, 8))
        fig.suptitle('Statistics')
        fig.tight_layout(pad=3.0)
        axes[0][0].title.set_text('Return distribution')
        axes[0][1].title.set_text('Profit over time')
        axes[1][0].title.set_text('Statistics summary')

        if self.datetime_support and time_axis:
            axes[0][1].plot(dts, cumulative_profits)
            axes[0][1].set_xlabel('Date/Time')
            #axes[0][1].xaxis.set_major_locator(md.DateFormatter(big_tick_formatter))
            #   axes[0][1].xaxis.set_major_formatter(md.DateFormatter(big_tick_formatter))
        else:
            cumulative_profits = cumulative_profits.reset_index()
            del cumulative_profits['index']
            axes[0][1].xaxis.set_major_locator(MaxNLocator(integer=True))
            axes[0][1].set_xlabel('nth trade')
            axes[0][1].plot(cumulative_profits)

        axes[0][0].hist(profits)
        # plt.text(.9, .9,'matplotlib', horizontalalignment='center',
        #      verticalalignment='center',
        #      transform=axes[0][0].transAxes)
        stat_summary = list(stat_summary.items())
        stat_summary = [(a, round(b, 3)) for (a, b) in stat_summary]
        stat_summary.extend([('', '')] * (len(stat_summary) % 2))
        stat_summary = np.asarray(stat_summary)
        stat_summary = np.reshape(stat_summary, (-1, 4))
        table = axes[1][0].table(cellText=stat_summary, loc='center')
        num_rows, _ = stat_summary.shape
        table.scale(1, 18.5 / num_rows)
        table.set_fontsize(200/num_rows)
        axes[1][0].xaxis.set_visible(False)
        axes[1][0].yaxis.set_visible(False)

        if show_window:
            plt.show()
        else:
            return plt, fig, axes

    def get_summary_statistics(self):
        if len(self.positions):
            warn('For most accurate performance results, please clear all holdings, which you can do with clear_all_positions()')

        df = self.trade_history.dropna().copy()
        # following 4 lines to compute drawdown
        df['cumulative'] = df['profit'].cumsum()
        df['high'] = df['cumulative'].cummax()
        df['drawdown'] = df['high'] - df['cumulative']
        max_drawdown = df['drawdown'].max()

        net_profit = df['profit'].sum()
        num_trades = len(df)
        profit_per_trade = net_profit / num_trades

        std_dev = df['profit'].std()
        fisher_kurtosis = df['profit'].kurtosis()
        skew = df['profit'].skew()

        df_gains = df[df['profit'] > 0]
        avg_win = df_gains['profit'].mean()
        num_gains = len(df_gains)

        df_losses = df[df['profit'] < 0]
        avg_loss = df_losses['profit'].mean()
        num_losses = len(df_losses)

        # rots stands for (r)eturn (o)n (t)rade (s)ize
        df_pos_rots = df[df['return on trade size'] > 0]
        df_neg_rots = df[df['return on trade size'] < 0]
        # avg_pos_rots = df_pos_rots['return on trade size'].mean()
        # avg_neg_rots = abs(df_neg_rots['return on trade size'].mean())

        winning_trades = len(df_gains)
        win_ratio = self.nan_division(winning_trades, num_trades)

        if net_profit > 0:
            kelly_criterion = win_ratio - self.nan_division(1 - win_ratio, self.nan_division(num_gains, num_losses))
        else:
            kelly_criterion = 0

        _, win_ratio_pval = proportions_ztest(count=num_gains, nobs=num_trades, value=.5, alternative='larger')
        return {'profit': net_profit,
                'num_trades': num_trades,
                'profit_per_trade': profit_per_trade,
                'win_ratio': win_ratio,
                'wr_pv_gt_half': win_ratio_pval,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'kelly_criterion': kelly_criterion,
                'fisher_kurtosis': fisher_kurtosis,
                'std_dev': std_dev,
                'skew': skew,
                'drawdown': max_drawdown}

    def clear_stock_positions(self, closure_date):
        def get_data(ticker, closure_date_inner):
            try:
                closure_df = si.get_data(ticker, closure_date_inner, closure_date_inner)
                open_price = closure_df.iloc[0]['open']
                self.log_cp(ticker, open_price)
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
        # example on how to use clear all positions
        self.clear_all_positions(get_data, closure_date)

    def nan_division(self, a, b):
        if b == 0:
            return float('NaN')
        else:
            return float(a / b)


if __name__ == '__main__':
    from datetime import timedelta
    from random import randint
    logger = SimpleLogger(datetime_support=True)

    day_counter = 1
    for x in range(0, 100):
        logger.log('fried chicken futures', randint(90, 100), randint(90, 100), dt=datetime.now()-timedelta(days=day_counter))
        logger.log('fried chicken futures', randint(-100, -90), randint(95, 105), dt=datetime.now()-timedelta(days=day_counter))
        day_counter += 1

    # by setting show_window to false, the graphs aren't plotted, but instead returned
    # axes is 2x2. If there variable names here have don't 1's in name then they interfere with other variables
    plt1, fig1, axes1 = logger.graph_statistics(show_window=False)
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
    