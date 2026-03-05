import requests
import pandas as pd
from indicatoros import calculate_ma
from points_of_intrest import get_gold_area, is_price_in_gold_area, is_we_make_gold_area , gold_area_type

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
                open=entry[1],       # Open price
                high=entry[2],       # High price
                low=entry[3],        # Low price
                close=entry[4],      # Close price
                vloume=entry[5],     # volume
                index=index
            )
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
        usdt_pairs = [s['symbol'] for s in symbols_data['symbols'] if 'USDT' in s['symbol']]
        return usdt_pairs
    else:
        print("Error fetching symbols:", response.status_code)
        return []

# Fetch all available Binance pairs
coin_list = fetch_binance_symbols()

# Loop through all coins and check the conditions for both timeframes
for symbol in coin_list:
    print(f"Processing {symbol}...")
    
    # Fetch data for 15m time frame
    candles_15m = fetch_binance_data(symbol, "4h", 1000)
    
    if candles_15m:
        ma_list_15m = calculate_ma(candles_ob=candles_15m, close_period=14, volume_period=20)
        gold_area_list_15m = get_gold_area(candles_ob=candles_15m, ma_list=ma_list_15m)
        
        # Check if the price is in the golden area on 15m time frame
        is_in_gold_area_15m, gold_area_15m = is_price_in_gold_area(candle=candles_15m[-1], gold_area_list=gold_area_list_15m)
        
        if is_in_gold_area_15m and gold_area_15m.type == gold_area_type.bullish:
            print(f"{symbol} is in the golden area on the 15m time frame!")
            
            # Fetch data for 3m time frame
            candles_3m = fetch_binance_data(symbol, "15m", 1000)[:-1]
            
            if candles_3m:
                ma_list_3m = calculate_ma(candles_ob=candles_3m, close_period=14, volume_period=20)
                gold_area_list_3m = get_gold_area(candles_ob=candles_3m, ma_list=ma_list_3m)
                
                # Check if a new gold area is being made on 3m time frame
                is_new_gold_area_3m, new_gold_area_3m = is_we_make_gold_area(candle=candles_3m[-1], gold_area_list=gold_area_list_3m)
                
                if is_new_gold_area_3m and new_gold_area_3m.type == gold_area_type.bullish: 
                    print(f"{symbol} is creating a new golden area on the 3m time frame!")
    else:
        print(f"Failed to fetch candles for {symbol} on the 15m timeframe.")

