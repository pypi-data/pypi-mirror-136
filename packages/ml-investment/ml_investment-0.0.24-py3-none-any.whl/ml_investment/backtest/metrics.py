import numpy as np
import pandas as pd
from scipy import stats



def sharpe_ratio_gen(riskfree_rate=0.):
    def foo(dates, returns):        
        dates = np.array(dates).astype(np.datetime64)
        returns = np.array(returns)
        idxs = np.argsort(dates)
        dates = dates[idxs]
        returns = returns[idxs]
        years_cnt = (dates[-1] - dates[0]) / np.timedelta64(1, 'D') / 365
        ann_factor = np.sqrt(len(dates) / years_cnt)
        
        return ann_factor * (returns - riskfree_rate).mean() / returns.std()
    return foo


def beta_alpha_gen(bench_dates, bench_returns):
    def foo(dates, returns):        
        df = pd.DataFrame()
        df['date'] = np.array(dates).astype(np.datetime64)
        df['return'] = returns

        bench_df = pd.DataFrame()
        bench_df['date'] = np.array(bench_dates).astype(np.datetime64)
        bench_df['bench_return'] = bench_returns

        df = pd.merge(df, bench_df, on='date', how='left').dropna()    

        (beta, alpha) = stats.linregress(df['bench_return'].values,
                                         df['return'].values)[0:2]

        return beta, alpha
    return foo


def max_drawdown(dates, returns):
    dates = np.array(dates).astype(np.datetime64)
    returns = np.array(returns)
    idxs = np.argsort(dates)
    dates = dates[idxs]
    returns = returns[idxs]        
    cum_returns = (returns + 1).cumprod()
    max_return = np.fmax.accumulate(cum_returns, axis=0)

    return np.nanmin((cum_returns - max_return) / max_return)


def annual_return(dates, returns):
    dates = np.array(dates).astype(np.datetime64)
    returns = np.array(returns)
    idxs = np.argsort(dates)
    dates = dates[idxs]
    returns = returns[idxs]        
    cum_returns = (returns + 1).cumprod()
    years_cnt = (dates[-1] - dates[0]) / np.timedelta64(1, 'D') / 365

    return cum_returns[-1] ** (1 / years_cnt) - 1  







