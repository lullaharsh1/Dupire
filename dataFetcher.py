from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import time
import logging
import threading
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':

    key_secret = open("api_key.txt", 'r').read().split()
    kite = KiteConnect(
        api_key=key_secret[0], access_token="1aitLPnVMnsDNQ4Vqjva7ZOjR1iqOKq8")
    exc = ''
    # instr = pd.read_csv('niftyInstruments1.csv')
    # data = pd.DataFrame()
    instr = pd.DataFrame(kite.instruments())
    # instr.to_csv('instruments.csv')
    # for index, row in instr.iterrows():
    #     df = pd.DataFrame(kite.historical_data(
    #         row['instrument_token'], '2023-06-05 09:45:00', '2023-06-05 10:00:00', 'minute'))
    #     df.to_csv(row['tradingsymbol']+'.csv')
    #     print(row['tradingsymbol'])
    #     time.sleep(0.2)
    kws = KiteTicker(key_secret[0], "1aitLPnVMnsDNQ4Vqjva7ZOjR1iqOKq8")
    tokens = [11660290, 11662850, 11665922, 11666946,
              11670274, 11677186, 11682050, 11689474,
              15415554, 15416578, 15417602, 15418626,
              15419650, 15420674, 15421698, 10231554, 8960770]
    dict = {11660290: '18300', 11662850: '18400', 11665922: '18500', 11666946: '18600',
            11670274: '18700', 11677186: '18800', 11682050: '18900', 11689474: '19000',
            15415554: '18300M', 15416578: '18400M', 15417602: '18500M', 15418626: '18600M',
            15419650: '18700M', 15420674: '18800M', 15421698: '18900M', 10231554: '19000M', 8960770: 'FUT'}

    lastTraded = pd.DataFrame(
        index=['18400', '18500', '18600', '18700', '18800', '18900', '18400M', '18500M', '18600M', '18700M', '18800M', '18900M'], columns=['last_price', 'local_vol', 'timestamp'])
    futPrice = 0

    def on_ticks(ws, ticks):
        # Callback to receive ticks.
        # print(ticks)
        for tick in ticks:
            ticks = [dict[tick['instrument_token']],
                     tick['exchange_timestamp'], float(tick['last_price'])]

            try:
                # print(ticks)
                lastTraded.loc[ticks[0], 'last_price'] = ticks[2]
                lastTraded.loc[ticks[0], 'timestamp'] = ticks[1]
                strike = ticks[0][:5]
                lowerStrike = int(strike)-100
                higherStrike = int(strike)+100
                strikeM = strike+'M'
                num = 2*((lastTraded.loc[strikeM, 'last_price'] -
                          lastTraded.loc[strike, 'last_price']))/10
                # print(num)
                den = lastTraded.loc[str(lowerStrike), 'last_price']-2*lastTraded.loc[strike,
                                                                                      'last_price']+lastTraded.loc[str(higherStrike), 'last_price']
                # print(den)
                denM = lastTraded.loc[str(lowerStrike)+'M', 'last_price']-2*lastTraded.loc[strike,
                                                                                           'last_price']+lastTraded.loc[str(higherStrike)+'M', 'last_price']
                # print(denM)
                lastTraded.loc[strike, 'local_vol'] = num/den
                lastTraded.loc[strikeM, 'local_vol'] = num/denM
                local_vol = 0

                # print(ticks[0])
            except Exception as e:
                exc = e

    def on_connect(ws, response):
        # Callback on successful connect.
        # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
        ws.subscribe(tokens)

        # Set RELIANCE to tick in `full` mode.
        ws.set_mode(ws.MODE_FULL, tokens)

    def on_close(ws, code, reason):
        # On connection close stop the event loop.
        # Reconnection will not happen after executing `ws.stop()`
        ws.stop()

    # Assign the callbacks.
    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.connect(threaded=True)
    count = 0
    local_vols_historical = pd.DataFrame(
        columns=['18400', '18500', '18600', '18700', '18800', '18900'])

    num_contracts = np.zeros(6)
    margin = np.zeros(6)
    profit = np.zeros(6)

    x = np.array([18400, 18500, 18600, 18700, 18800, 18900])
    y = np.zeros(6)

    # to run GUI event loop
    plt.ion()

    # here we are creating sub plots
    figure, ax = plt.subplots(figsize=(10, 8))
    line1, = ax.plot(x, y)
    line2, = ax.plot(x, y)

    # setting title
    plt.title("Local Volatility vs Strike", fontsize=20)

    # setting x-axis label and y-axis label
    plt.xlabel("Strike")
    plt.ylabel("Local Vol")
    plt.ylim([0, 10])

    while True:
        count += 1
        if (count % 2 == 0):
            if kws.is_connected():
                kws.set_mode(kws.MODE_FULL, tokens)
            else:
                if kws.is_connected():
                    kws.set_mode(kws.MODE_FULL, tokens)
            time.sleep(0.35)
        # print(lastTraded)
        # creating new Y values
        new_y = np.array([lastTraded.loc['18400', 'local_vol'], lastTraded.loc['18500', 'local_vol'], lastTraded.loc['18600', 'local_vol'],
                          lastTraded.loc['18700', 'local_vol'], lastTraded.loc['18800', 'local_vol'], lastTraded.loc['18900', 'local_vol']])
        local_vols_historical = pd.concat(
            [local_vols_historical, pd.DataFrame({'18400': new_y[0], '18500':new_y[1], '18600':new_y[2], '18700':new_y[3], '18800':new_y[4], '18900':new_y[5]}, index=[0])], axis=0, ignore_index=True)[-100:]
        # print(local_vols_historical)
        y_avg_rolling = np.array([local_vols_historical['18400'].mean(), local_vols_historical['18500'].mean(), local_vols_historical['18600'].mean(
        ), local_vols_historical['18700'].mean(), local_vols_historical['18800'].mean(), local_vols_historical['18900'].mean()])

        for i in range(len(new_y)):
            if new_y[i] > 1.1*y_avg_rolling[i]:
                strike = int(x[i])
                ltp = lastTraded.loc[str(strike), 'last_price']
                timestamp = lastTraded.loc[str(strike), 'timestamp']
                num_contracts[i] -= 1
                print(futPrice)
                margin[i] += ltp*50
                profit[i] = margin[i]+(num_contracts[i]*ltp*50)
                print("SOLD 8THJUN" + str(strike) + "CE for " +
                      str(ltp) + " at " + str(timestamp))
            if new_y[i] < 0.9*y_avg_rolling[i]:
                strike = int(x[i])
                ltp = lastTraded.loc[str(strike), 'last_price']
                num_contracts[i] += 1
                print(futPrice)
                margin[i] -= ltp*50
                profit[i] = margin[i]+(num_contracts[i]*ltp*50)
                print("BOUGHT 8THJUN" + str(strike) + "CE for " +
                      str(ltp) + " at " + str(timestamp))
        print(profit)
        print(num_contracts)
        # updating data values
        line1.set_ydata(new_y)
        line2.set_ydata(y_avg_rolling)

        # drawing updated values
        figure.canvas.draw()

        # This will run the GUI event
        # loop until all UI events
        # currently waiting have been processed
        figure.canvas.flush_events()
