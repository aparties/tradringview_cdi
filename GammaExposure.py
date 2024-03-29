#%%
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
from datetime import timedelta, date
import datetime
import itertools


#%%
#Make dataframe by cutting out top values of data file
df = pd.read_csv('SPY-09-23', sep='\s+', header=None, skiprows=0)
df.columns = ['1stCol','2ndCol','3rdCol','4thCol','5thCol','6thCol']

#%%
#Store spot price
spot_price = df['6thCol'][0].split(',')[1]
spot_price = float(spot_price)
df = df.iloc[3:]


#%%
#Split first column into 21 columns
new = df["1stCol"].str.split(",", n = 21, expand = True) 
new.columns = ['ExpirationDate','Calls','CallLastSale','CallNet','CallBid','CallAsk','CallVol','CallIV','CallDelta','CallGamma','CallOpenInt','CallStrike','Puts','PutLastSale','PutNet','PutBid','PutAsk','PutVol','PutIV','PutDelta','PutGamma','PutOpenInt']


#%%
#Store strike price
callStrike = [x[-6:-3] for x in new.Calls]
new['StrikePrice'] = callStrike


#%%
#Calculate Call GEX by doing calculation and Call GEX Notional Value
new['CallGamma'] = new['CallGamma'].astype(float)
new['CallOpenInt'] = new['CallOpenInt'].astype(float)
new['CallGEX'] = new['CallGamma'] * new['CallOpenInt'] * 100 * spot_price
new['CallGEXNotional'] = new.CallGEX * (spot_price * .01)
new['CallIV'] = new['CallIV'].astype(float)
new['PutIV'] = new['PutIV'].astype(float)


#%%
#Calculate Put GEX and Put GEX Notional Value
new['PutGamma'] = new['PutGamma'].astype(float)
new['PutOpenInt'] = new['PutOpenInt'].astype(float)
new['PutGEX'] = new['PutGamma'] * new['PutOpenInt'] * 100 * spot_price * -1
new['PutGEXNotional'] = new.PutGEX * (spot_price * .01)


#%%
#Only choose expirations within 94 days
#EndDate = new.iloc[0]['ExpirationDate']+ timedelta(days=94)
EndDate = date.today()+ timedelta(days=94)
new['ExpirationDate']= pd.to_datetime(new['ExpirationDate'])
df = [x for x in new['ExpirationDate'] if x <= EndDate]
new['ExpirationDate'] = pd.Series(df)
new = new.fillna(0)
new = new[(new['ExpirationDate'] != 0.0)]


#%%
#Calculate Total Gamma and Total Gamma Notional Value
flag = True
new['TotalGamma'] = new.CallGEX + new.PutGEX
new['TotalGammaNotional'] = new.CallGEXNotional + new.PutGEXNotional
count = 0
strikeWithGamma = []
#Make a list of tuples for strike price and gamma
for a, b in zip(new.StrikePrice, new.TotalGammaNotional):
    strikesPlusGamma = (a,b)
    strikeWithGamma.append(strikesPlusGamma)
new['StrikeAndGamma'] = strikeWithGamma

#%%
#Cut out values of dataframe which the TotalGamma is 0
new = new[(new['TotalGamma'] != 0.0)]

#%%
#Calculate flip point
def _zero_gex(strikes):
    def _aux_add(a, b):
        return (b[0], a[1] + b[1])

    cumsum = list(itertools.accumulate(strikes, _aux_add))
    if cumsum[len(strikes) // 10][1] < 0:
        op = min
    else:
        op = max
    return op(cumsum, key=lambda i: i[1])[0]

#%%
_zero_gex(new.StrikeAndGamma)

#%%
#new = new[(new['TotalGamma'] != 0.0)]
_zero_gex(new.StrikeAndGamma)
#Updating Changes


#%%
#More plotting 
#fig, ax = plt.subplots()
#fig = ax.bar(new['StrikePrice'], new['PutGEX'])
#bar1 = ax.bar(new['StrikePrice'], new['CallGEX'])
#plt.show()
#plt.bar(new['StrikePrice'], new['CallGEX'])
#plt.bar(new['StrikePrice'], new['PutGEX'])
#plt.show()


#%%
#Plot trying to replicate CDF

#s = pd.Series(new['TotalGamma'], name = 'TotalGamma')
##print(s)
# CDF
#new_df = pd.DataFrame(s)
#new_df['cdf'] = new_df.rank(method = 'average', pct = True)
#new_df['StrikePrice'] = new['StrikePrice']
#x = new_df.sort_values('TotalGamma')
#print(x)
#new_df.sort_values('StrikePrice').plot(x = 'StrikePrice', y = 'cdf', grid = True)
#new_df.sort_values('StrikePrice').plot(x = 'StrikePrice', y = 'TotalGamma', grid = True)
#new_df.sort_values('TotalGamma').plot(x = 'TotalGamma', y = 'cdf', grid = True)


#%%
#Plot for regular CDF

#Define your Series
#s = pd.Series(np.random.normal(loc = 10, scale = 0.1, size = 1000), name = 'value')
#df = pd.DataFrame(s)
# Get to the CDF directly
#df['cdf'] = df.rank(method = 'average', pct = True)
#print(max(df['cdf']))
# Sort and plot
#x = df.sort_values('value')
#print(x)
#x.plot(x = 'value', y = 'cdf', grid = True)
