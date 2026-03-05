import requests
import pandas as pd
from plt_data import PLOT_CHART
from indicatoros import calculate_all_indicators
from points_of_intrest import get_gold_area , is_price_in_gold_area , is_we_make_gold_area



class CandleClass:
    def __init__(self, timestamp, open, high, low, close, vloume, index):#vloume vloume
        self.timestamp = timestamp
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.vloume = float(vloume)  # ✅ Fixed typo from vloume to volume
        self.date = pd.to_datetime(timestamp, unit='ms')
        self.index = index

    def data(self):
        return {
            "index": self.index,
            "open": self.open,
            "close": self.close,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,  # ✅ Fixed typo here as well
            "date": self.date
        }

def fetch_binance_data(symbol="BTCUSDT", interval="1h", limit=1000):
    """
    Fetches historical candlestick (kline) data from Binance.
    
    :param symbol: Trading pair symbol (e.g., "BTCUSDT").
    :param interval: Timeframe (e.g., "1m", "5m", "1h", "1d").
    :param limit: Number of candles to retrieve (Max = 1000).
    :return: List of CandleClass objects.
    """
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    print("response : ", response)
    if response.status_code == 200:
        raw_data = response.json()
        candles = []
        for index, entry in enumerate(raw_data):
            candle = CandleClass(
                timestamp=entry[0],  # Open time
                open=entry[1],       # Open price
                high=entry[2],       # High price
                low=entry[3],        # Low price
                close=entry[4],      # Close price
                vloume=entry[5],     # vloume
                index=index
            )
            candles.append(candle)
        return candles
    else:
        print("Error fetching data:", response.status_code)
        return []

# Example Usage: Fetch last 1000 candles for BTC/USDT on 1-hour timeframe
symbol = "SLFUSDT"
timeframe = "4h"
num_candles = 1000
print("start get candle ...")
candles = fetch_binance_data(symbol, timeframe, num_candles)
print("candle is here")
print( "Len Candles" , len(candles))
ma_list = calculate_all_indicators(candles_ob=candles )
gold_area_list = get_gold_area(candles_ob=candles , ma_list=ma_list)

is_we_are_inter_gold_area_state , gold_area_we_are_inter = is_price_in_gold_area(candle=candles[-1] , gold_area_list=gold_area_list)
is_we_make_gold_area_state , gold_area_we_make = is_we_make_gold_area(candle=candles[-1] , gold_area_list=gold_area_list)

print("is we are inter gold area" , is_we_are_inter_gold_area_state)
print("is we make gold area state" , is_we_make_gold_area_state)

# print(candles_data["candles_objects_list"][0].data()["date"])
# print("min :" , candles_data["candles_objects_list"][0].data()["date"].minute)
# print("hour :" , candles_data["candles_objects_list"][0].data()["date"].hour)
# print("Day :" , candles_data["candles_objects_list"][0].data()["date"].day)
# print("Month :" , candles_data["candles_objects_list"][0].data()["date"].month)
# print("Year :" , candles_data["candles_objects_list"][0].data()["date"].year)
        
## plot data
PLOT_CHART(sympol=symbol , candles_ob=candles , xlim_num=200 , line_candle_type=False , ma_list=ma_list , gold_area_list = gold_area_list , percent_change=0.2 , paint_trend_st=True , paint_ex_zigzag=False , ).paint()

