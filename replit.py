import requests
import pandas as pd


## api key : 8bu3QQW7INvxqbkfj8lSRgeNAFFYeVnFxjTJ5aahE399UisknzFTrkQfqRnWZzdJ
## secret key : QwAK4y45DClAPBUNHHJLjnhEoRjwzjKd4fd3GUiwz52FPTIQ51dp1ushFIHou1ha


# Moving Average Class
class MovingAverage:

    def __init__(self, index, close_ma, volume_ma):
        self.index = index
        self.close_ma = close_ma
        self.volume_ma = volume_ma


# Function to calculate Simple Moving Average (SMA)
def calculate_ma(candles_ob, close_period, volume_period):
    ma_list = []

    for i in range(len(candles_ob)):
        if i >= close_period - 1:
            close_ma = sum(candle.close
                           for candle in candles_ob[i - close_period + 1:i +
                                                    1]) / close_period
        else:
            close_ma = None  # Not enough data points for MA

        if i >= volume_period - 1:
            volume_ma = sum(candle.vloume
                            for candle in candles_ob[i - volume_period + 1:i +
                                                     1]) / volume_period
        else:
            volume_ma = None  # Not enough data points for MA

        ma_list.append(
            MovingAverage(index=candles_ob[i].index,
                          close_ma=close_ma,
                          volume_ma=volume_ma))

    return ma_list


class gold_area_end_state:
    end = "Ended"
    not_end = "Not Ended"


class gold_area_type:
    bullish = "bullish"
    bearsh = "bearsh"


class gold_area:

    def __init__(self, candle, type, end_state, end_candle=None):
        self.type = type
        self.candle = candle
        self.end_state = end_state
        self.end_candle = end_candle


def check_the_gold_end_state(candle, candles_ob, type):
    invalidation_bullish = candle.low
    invalidation_bearsh = candle.high
    for i in range(candle.index + 1, len(candles_ob)):
        if type == gold_area_type.bullish and candles_ob[
                i].close < invalidation_bullish:
            return gold_area_end_state.end, candles_ob[i]
        elif type == gold_area_type.bearsh and candles_ob[
                i].close > invalidation_bearsh:
            return gold_area_end_state.end, candles_ob[i]
    return gold_area_end_state.not_end, None


def get_gold_area(candles_ob, ma_list):
    gold_area_list = []

    for candle_index, candle in enumerate(candles_ob):
        # Ensure we have enough candles before and after the current one
        if candle_index < 50 or candle_index >= len(candles_ob) - 1:
            continue

        # Check volume moving average condition safely
        if (candle_index + 1 < len(candles_ob)
                and candle.vloume > ma_list[candle_index].volume_ma
                and candles_ob[candle_index + 1].vloume
                > ma_list[candle_index + 1].volume_ma):

            # Check if the candle is a swing low
            if (candle_index - 1 >= 0
                    and candle.low < candles_ob[candle_index - 1].low
                    and candle.low < candles_ob[candle_index + 1].low
                    and candles_ob[candle_index - 1].low
                    < candles_ob[candle_index - 2].low):

                # Check the moving average close condition
                if (candle.high < ma_list[candle_index].close_ma
                        and candles_ob[candle_index + 1].close
                        > ma_list[candle_index + 1].close_ma):

                    # Bullish no gold area
                    type = gold_area_type.bullish
                    end_state, end_candle = check_the_gold_end_state(
                        candle=candle, candles_ob=candles_ob, type=type)
                    gold_area_list.append(
                        gold_area(candle=candle,
                                  end_state=end_state,
                                  end_candle=end_candle,
                                  type=type))

            # Check if the candle is a swing high
            elif (candle_index - 1 >= 0
                  and candle.high > candles_ob[candle_index - 1].high
                  and candle.high > candles_ob[candle_index + 1].high
                  and candles_ob[candle_index - 1].high
                  > candles_ob[candle_index - 2].high):

                # Check the moving average close condition
                if (candle.low > ma_list[candle_index].close_ma
                        and candles_ob[candle_index + 1].close
                        < ma_list[candle_index + 1].close_ma):

                    # Bearish gold area
                    type = gold_area_type.bearsh
                    end_state, end_candle = check_the_gold_end_state(
                        candle=candle, candles_ob=candles_ob, type=type)
                    gold_area_list.append(
                        gold_area(candle=candle,
                                  end_state=end_state,
                                  end_candle=end_candle,
                                  type=type))

    return gold_area_list


def is_price_in_gold_area(candle, gold_area_list):
    for gold_area in gold_area_list:
        if gold_area.end_state == gold_area_end_state.not_end:
            candle_area = gold_area.candle
            if gold_area.type == gold_area_type.bullish:
                if candle.close > candle_area.low and candle.low < candle_area.high:
                    return True, gold_area
            elif gold_area.type == gold_area_type.bearsh:
                if candle.close > candle_area.low and candle.close < candle_area.high:
                    return True, gold_area

    return False, None


def is_we_make_gold_area(candle, gold_area_list):
    candle_index = candle.index
    for gold_area in gold_area_list:
        if gold_area.candle.index == candle_index - 1:
            return True, gold_area
    return False, None


class CandleClass:

    def __init__(self, timestamp, open, high, low, close, vloume, index):
        self.timestamp = timestamp
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.vloume = float(vloume)
        self.date = pd.to_datetime(timestamp, unit='ms')
        self.index = index

    def data(self):
        return {
            "index": self.index,
            "open": self.open,
            "close": self.close,
            "high": self.high,
            "low": self.low,
            "volume": self.vloume,
            "date": self.date
        }


def fetch_binance_data(symbol="BTCUSDT", interval="1h", limit=1000):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)

    if response.status_code == 200:
        raw_data = response.json()
        candles = []
        for index, entry in enumerate(raw_data):
            candle = CandleClass(
                timestamp=entry[0],  # Open time
                open=entry[1],  # Open price
                high=entry[2],  # High price
                low=entry[3],  # Low price
                close=entry[4],  # Close price
                vloume=entry[5],  # volume
                index=index)
            candles.append(candle)
        return candles
    else:
        print("Error fetching data:", response.status_code)
        return []


def fetch_binance_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)

    if response.status_code == 200:
        symbols_data = response.json()
        usdt_pairs = [
            s['symbol'] for s in symbols_data['symbols']
            if 'USDT' in s['symbol']
        ]
        return usdt_pairs
    else:
        print("Error fetching symbols:", response.status_code)
        return []


# Fetch all available Binance pairs
coin_list = fetch_binance_symbols()

# Loop through all coins and check the conditions for both timeframes
high_time_frame = "30m"
low_time_frame = "5m"
buy_num = 0
sell_num = 0
for symbol in coin_list:
    # Fetch data for 15m time frame
    candles_15m = fetch_binance_data(symbol, high_time_frame, 1000)

    if candles_15m:
        ma_list_15m = calculate_ma(candles_ob=candles_15m,
                                   close_period=14,
                                   volume_period=20)
        gold_area_list_15m = get_gold_area(candles_ob=candles_15m,
                                           ma_list=ma_list_15m)

        # Check if the price is in the golden area on 15m time frame
        is_in_gold_area_15m, gold_area_15m = is_price_in_gold_area(
            candle=candles_15m[-1], gold_area_list=gold_area_list_15m)

        if is_in_gold_area_15m :
            if gold_area_15m.type  == gold_area_type.bullish:
                buy_num +=1
                print(f"{symbol} in buy zone ")
            elif gold_area_15m.type  == gold_area_type.bearsh:
                sell_num +=1
                print(f"{symbol} in sell zone ")

            # Fetch data for 3m time frame
            candles_3m = fetch_binance_data(symbol, low_time_frame, 1000)[:-1]

            if candles_3m:
                ma_list_3m = calculate_ma(candles_ob=candles_3m,
                                          close_period=14,
                                          volume_period=20)
                gold_area_list_3m = get_gold_area(candles_ob=candles_3m,
                                                  ma_list=ma_list_3m)

                # Check if a new gold area is being made on 3m time frame
                is_new_gold_area_3m, new_gold_area_3m = is_we_make_gold_area(
                    candle=candles_3m[-1], gold_area_list=gold_area_list_3m)

                if is_new_gold_area_3m:
                  if new_gold_area_3m.type == gold_area_type.bullish :  
                    print(
                        f"{symbol} is creating buy confirmatiom"
                                                                )
                  elif new_gold_area_3m.type == gold_area_type.bearsh :
                    print(
                        f"{symbol} is creating sell confirmatiom"
                    )                    
    else:
        print(f"Failed to fetch candles for {symbol} on the 15m timeframe.")

hfb = buy_num / (buy_num + sell_num)
print("HFB Indicator : ", hfb)