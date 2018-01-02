import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# pd.set_option('display.expand_frame_repr', False)

def momentumreturns():
    df = pd.read_csv('/Users/Hallshit/newdir/Finance/CurrencyTrading/CurrencyForwardRates.csv')
    df = df.rename(columns={'#NAME?': 'Date'})
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    df = df.loc[df.index > '2012-01-01']

    currencies = ['CHINESE YUAN TO US $ 3M FWD (WMR) - EXCHANGE RATE - CHINESE YUAN TO US $ 3M FWD (WMR) - EXCHANGE RATE',
              'NORWEGIAN KRONE TO US $ 3M FWD(WMR) - EXCHANGE RATE - NORWEGIAN KRONE TO US $ 3M FWD(WMR) - EXCHANGE RATE',
              'JAPANESE YEN TO US $ 3M FWD (WMR) - EXCHANGE RATE - JAPANESE YEN TO US $ 3M FWD (WMR) - EXCHANGE RATE',
              'HONG KONG $ TO US $ 3M FWD (WMR) - EXCHANGE RATE - HONG KONG $ TO US $ 3M FWD (WMR) - EXCHANGE RATE',
              'US $ TO EURO 3M FWD (WMR) - EXCHANGE RATE - US $ TO EURO 3M FWD (WMR) - EXCHANGE RATE',
              'SAUDI RIYAL TO US $ 3M FWD (WMR) - EXCHANGE RATE - SAUDI RIYAL TO US $ 3M FWD (WMR) - EXCHANGE RATE',
              'POLISH ZLOTY TO US $ 3M FWD (WMR) - EXCHANGE RATE - POLISH ZLOTY TO US $ 3M FWD (WMR) - EXCHANGE RATE',
              'US $ TO NEW ZEALAND $ 3M FWD (WMR) - EXCHANGE RATE - US $ TO NEW ZEALAND $ 3M FWD (WMR) - EXCHANGE RATE',
              'DANISH KRONE TO US $ 3M FWD (WMR) - EXCHANGE RATE - DANISH KRONE TO US $ 3M FWD (WMR) - EXCHANGE RATE',
              'SWISS FRANC TO US $ 3M FWD (WMR) - EXCHANGE RATE - SWISS FRANC TO US $ 3M FWD (WMR) - EXCHANGE RATE',
              ]


    df = df[currencies]
    # print df
    # simplify col Names
    df.columns = ['Yuan', 'NorKrone','Yen', 'HK', 'Euro', 'Riyal','Zloty', 'NZ$', 'DanKrone', 'Franc']
    currencies = df.columns


    # Create momentum cols
    momentumCols = []
    momRankCols = []
    momStratCols = []
    backTestCols = []


    for c in currencies:
        name = str(c) + ' 10 day Average'
        momRankCols.append(c + ' mom Rank')
        momentumCols.append(name)
        momStratCols.append(c + ' strategy')
        backTestCols.append(c + ' back test returns')
        df[name] = df[c]/df[c].shift(10)-1
        df[c + ' back test returns'] = (df[c].shift(-2)/df[c].shift(-1))-1
        df[c + ' strategy'] = 0


    # Rank 10 day averages
    momdf = df[momentumCols]
    ranked = momdf.rank(axis=1, ascending=1, method='first')
    df[momRankCols] = ranked
    # print df

    # Add to Portfolio if Rank > 3
    returns = []
    for c in currencies:
        rankedC = df[c + ' mom Rank']
        df[c + ' returns'] = (1 + df[c + ' back test returns']).cumprod() - 1
        returns.append(c + ' returns')
        df[c + ' strategy'] = np.where(rankedC > 9, 1 * df[c + ' back test returns'], 0)

    # Get sum of each strategy
    df['Final Strategy'] = df[momStratCols].sum(axis=1)
    df['cumprod'] = (1 + df['Final Strategy']).cumprod() - 1

    # print df['cumsum']


    # Plot
    # df[returns].plot(style='-b')
    # df['cumprod'].plot(style='-g')
    return df['cumprod']

# df.to_csv('MomStrategy.csv')
# plt.show()





# print momentumreturns()



