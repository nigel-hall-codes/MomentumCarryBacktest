import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Plan


df = pd.read_csv('/Users/Hallshit/newdir/Finance/CurrencyTrading/DepositRates.csv')
df = df.rename(columns={'#NAME?': 'Date'})
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')
df = df.loc[df.index > '2012-01-01']

rates = ['CAD CASH DEPOSIT 6 MONTH (TP) - MIDDLE RATE', 'NOK CASH DEPOSIT 6 MONTH (TP) - MIDDLE RATE',
              'JPY CASH DEPOSIT 6 MONTH (TP) - MIDDLE RATE', 'HKD CASH DEPOSIT 6 MONTH (TP) - MIDDLE RATE',
              'EUR CASH DEPOSIT 6 MONTH (TP) - MIDDLE RATE', 'SAR CASH DEPOSIT 6 MONTH (TP) - MIDDLE RATE',
              'PLN CASH DEPOSIT 6 MONTH (TP) - MIDDLE RATE', 'NZD CASH DEPOSIT 6 MONTH (TP) - MIDDLE RATE',
              'DKK CASH DEPOSIT 6 MONTH (TP) - MIDDLE RATE', 'CHF CASH DEPOSIT 6 MONTH (TP) - MIDDLE RATE']



df = df[rates]
# df.to_csv('DepositRates.csv')
cols = []
for r in rates:
    cols.append(r[:3] + ' 6 mo rate')
df.columns = cols
rates = cols

forwards = ['CANADIAN $ TO US $ 3M FWD (WMR) - EXCHANGE RATE - CANADIAN $ TO US $ 3M FWD (WMR) - EXCHANGE RATE',
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


fw = pd.read_csv('/Users/Hallshit/newdir/Finance/CurrencyTrading/CurrencyForwardRates.csv')
fw = fw.rename(columns={'#NAME?': 'Date'})
fw['Date'] = pd.to_datetime(fw['Date'])
fw = fw.set_index('Date')
fw = fw[forwards]
fw.columns = ['CAN', 'NOR', 'Yen', 'HK$', 'Euro', 'SAU', 'POL', 'NZ$', 'Krone', 'Franc']
forwards = fw.columns
fw['Euro'] = 1 / fw['Euro']
fw['NZ$'] = 1 / fw['NZ$']
fw = fw.loc[fw.index > '2012-01-01']

fw.to_csv('ForwardRates.csv')
window = 10
pctMomCols = []

# Get [window] day pct_ch
for f in forwards:
    fw[f + ' %s day pct_ch' % str(window)] = fw[f]/fw[f].shift(window) - 1
    pctMomCols.append(f + ' %s day pct_ch' % str(window))

# Rank the momentum
rank = fw[pctMomCols].rank(axis=1)
ranks = []
for f in pctMomCols:
    fw[f[:3] + ' rank'] = rank[f]
    ranks.append(f[:3] + ' rank')

# Get backtest returns
BTreturns = []
for f in forwards:
    fw[f + ' backtest return'] = fw[f].shift(-2)/fw[f].shift(-1) - 1
    BTreturns.append(f + ' backtest return')

# Get momentum strategy returns

MomstratReturns = []
for c in range(0, len(forwards)):
    # if rank > 5: [long] take backtest return and multiply by portfolio weight. else: [short] take backtest return and multiple - portflio weight
    # fw[forwards[c] + ' momentum strategy'] = np.where(fw[ranks[c]] > 5, fw[BTreturns[c]] * .2, fw[BTreturns[c]] * -.2)
    fw[forwards[c] + ' long momentum strategy'] = np.where(fw[ranks[c]] > 5, fw[BTreturns[c]] * .1, 0)
    fw[forwards[c] + ' short momentum strategy'] = np.where(fw[ranks[c]] <= 5, 0, 0)
    MomstratReturns.append(forwards[c] + ' long momentum strategy')
    MomstratReturns.append(forwards[c] + ' short momentum strategy')

# Carry Trade Section

# rank the momentum
drrank = df[rates].rank(axis=1)
drRanks = []
for r in rates:
    fw[r + ' rank'] = drrank[r]
    drRanks.append(r + ' rank')


# get carry Strategy returns
carryStratReturns = []
print len(rates)
for c in range(0, len(rates)):

    # fw[rates[c] + ' carry strategy'] = np.where(fw[drRanks[c]] > 5, fw[BTreturns[c]] * .2, fw[BTreturns[c]] * -.2)
    fw[rates[c] + ' long carry strategy'] = np.where(fw[drRanks[c]] > 5, fw[BTreturns[c]] * .1, 0)
    fw[rates[c] + ' short carry strategy'] = np.where(fw[drRanks[c]] <= 5, fw[BTreturns[c]] * .1, 0)

    carryStratReturns.append(rates[c] + ' long carry strategy')
    carryStratReturns.append(rates[c] + ' short carry strategy')

# sum portfolio of returns
fw['Portfolio Momentum Strategy'] = fw[MomstratReturns].sum(axis=1)
fw['Portfolio Carry Strategy'] = fw[carryStratReturns].sum(axis=1)

# Apply weights to strategies and use cumprod to find total return
fw['Carry and Momentum Strategy'] = (fw['Portfolio Momentum Strategy'] * .5) + (fw['Portfolio Carry Strategy'] * .5)
fw['Carry and Momentum Strategy'] = (1 + fw['Carry and Momentum Strategy']).cumprod() - 1
fw['Portfolio Momentum Strategy cumprod'] = (1 + fw['Portfolio Momentum Strategy']).cumprod() - 1
fw['Portfolio Carry Strategy cumprod'] = (1 + fw['Portfolio Carry Strategy']).cumprod() - 1


print fw.tail()
fw[['Carry and Momentum Strategy', 'Portfolio Momentum Strategy cumprod', 'Portfolio Carry Strategy cumprod']].plot()
# fw.to_csv('CarryMomentum.csv')
plt.show()


# print fw.tail()