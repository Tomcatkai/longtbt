from backtesting import Strategy, Backtest
from backtesting.lib import crossover
import pandas as pd
from backtesting.test import GOOG


def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()


class SmaCross(Strategy):
    # 将两个 MA 滞后定义为 *class variables*
    # 用于后期优化
    n1 = 10
    n2 = 20

    def init(self):
        # 预先计算两条移动平均线
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        # 如果 sma1 越过 sma2，关闭任何现有的
        # 做空交易，并买入资产
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # 否则，如果 sma1 低于 sma2，则关闭任何现有的
        # 多头交易，并卖出资产
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


bt = Backtest(GOOG, SmaCross, cash=10_000, commission=.002)
stats = bt.run()
stats = bt.optimize(n1=range(5, 30, 5),
                    n2=range(10, 70, 5),
                    maximize='Equity Final [$]',
                    constraint=lambda param: param.n1 < param.n2)
print(stats)
bt.plot()
