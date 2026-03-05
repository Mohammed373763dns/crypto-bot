## imports
from fetch_candles import FechCandlesClass
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from math import sqrt

# inputs
symbol, interval, start_index, end_index, percent_change = "dotusdt", "15m", 20000, -1, 0.2

balance = 1000
risk_to_reward = 1
rafeha_malia = 1

# data
candles_data = FechCandlesClass(sympol=symbol, interval=interval, 
                               local_candles_start_index_=start_index, 
                               local_candles_end_index=end_index).re_structure_candle_data()["candles_objects_list"]

print(candles_data[0].data()["date"], "--", candles_data[-1].data()["date"])

# Helper functions for technical indicators
def calculate_ema(prices, period):
    if len(prices) < period:
        return np.array([np.nan] * len(prices))
    ema = np.zeros(len(prices))
    ema[period-1] = np.mean(prices[:period])
    multiplier = 2 / (period + 1)
    for i in range(period, len(prices)):
        ema[i] = (prices[i] - ema[i-1]) * multiplier + ema[i-1]
    return ema

def calculate_sma(prices, period):
    if len(prices) < period:
        return np.array([np.nan] * len(prices))
    sma = np.zeros(len(prices))
    for i in range(period-1, len(prices)):
        sma[i] = np.mean(prices[i-period+1:i+1])
    return sma

def calculate_atr(high, low, close, period):
    tr = np.zeros(len(close))
    tr[0] = high[0] - low[0]
    for i in range(1, len(close)):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i-1])
        lc = abs(low[i] - close[i-1])
        tr[i] = max(hl, hc, lc)
    
    atr = np.zeros(len(close))
    atr[period-1] = np.mean(tr[:period])
    for i in range(period, len(close)):
        atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
    return atr

def calculate_macd(close, fast=12, slow=26, signal=9):
    if len(close) < slow + signal:
        return np.array([np.nan] * len(close)), np.array([np.nan] * len(close)), np.array([np.nan] * len(close))
    
    ema_fast = calculate_ema(close, fast)
    ema_slow = calculate_ema(close, slow)
    macd = ema_fast - ema_slow
    signal_line = calculate_ema(macd, signal)
    hist = macd - signal_line
    return macd, signal_line, hist

def calculate_rsi(close, period=14):
    if len(close) <= period:
        return np.array([np.nan] * len(close))
    
    deltas = np.diff(close)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down
    rsi = np.zeros(len(close))
    rsi[:period] = 100. - 100./(1.+rs)
    
    for i in range(period, len(close)):
        delta = deltas[i-1]
        
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
            
        up = (up*(period-1) + upval)/period
        down = (down*(period-1) + downval)/period
        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)
    
    return rsi

def calculate_wma(prices, period):
    if len(prices) < period:
        return np.array([np.nan] * len(prices))
    
    weights = np.arange(1, period+1)
    wma = np.zeros(len(prices))
    
    for i in range(period-1, len(prices)):
        wma[i] = np.sum(weights * prices[i-period+1:i+1]) / weights.sum()
    
    return wma

def calculate_hma(prices, period):
    if len(prices) < period:
        return np.array([np.nan] * len(prices))
    
    half_period = period // 2
    sqrt_period = int(sqrt(period))
    
    wma_half = calculate_wma(prices, half_period)
    wma_full = calculate_wma(prices, period)
    hma_series = 2 * wma_half - wma_full
    hma = calculate_wma(hma_series, sqrt_period)
    
    return hma

# deal class
class Deal_State:
    done = "done"
    fail = "fail"

class Deal_Type:
    long = "long"
    short = "short"

class Deal:
    def __init__(self, index, stoplose, tp, inter_price, state=None, type=Deal_Type.long):
        self.index = index
        self.stoplose = stoplose
        self.tp = tp
        self.inter_price = inter_price
        self.state = state
        self.type = type
        self.deal_profit_percent = self.calac_deal_profit_percent()

    def calac_deal_profit_percent(self):
        if self.type == Deal_Type.long:
            return ((self.tp - self.inter_price) / self.inter_price)
        elif self.type == Deal_Type.short:
            return ((self.inter_price - self.tp) / self.inter_price)

    def print_data(self):
        print()
        print("= = = = = = = =")
        print()
        print("index : ", self.index)
        print("type : ", self.type)
        print("state : ", self.state)
        print("stoplose : ", self.stoplose)
        print("tp : ", self.tp)
        print("inter_price : ", self.inter_price)
        print("deal_profit_percent :", self.deal_profit_percent * 100)

class Order:
    def __init__(self, index, deal):
        self.index = index
        self.deal = deal

class FreshAlgoStrategy:
    def __init__(self, candles_ob):
        self.close = np.array([c.close for c in candles_ob])
        self.high = np.array([c.high for c in candles_ob])
        self.low = np.array([c.low for c in candles_ob])
        self.open = np.array([c.open for c in candles_ob])
        self.volume = np.array([c.vloume for c in candles_ob])  # Fixed typo in 'volume'
        
        # Initialize indicators
        self.ema150 = self.calculate_ema(self.close, 150)
        self.ema250 = self.calculate_ema(self.close, 250)
        self.supertrend = self.calculate_supertrend()
        self.macd, self.signal, self.hist = self.calculate_macd()
        self.rsi = self.calculate_rsi(self.close, 14)
        self.hma55 = self.calculate_hma(self.close, 55)
        self.trend_direction = self.calculate_trend_direction()

    def calculate_hma(self, prices, period=55):
        """
        Calculate Hull Moving Average (HMA) for given prices and period.
        
        Args:
            prices (np.array): Array of price data (typically closing prices)
            period (int): The period for HMA calculation
            
        Returns:
            np.array: HMA values for the given prices
        """
        if len(prices) < period:
            return np.zeros(len(prices))
            
        # Calculate Weighted Moving Average (WMA) for half period
        half_period = int(period/2)
        wma_half = np.zeros(len(prices))
        
        # Calculate WMA for full period
        wma_full = np.zeros(len(prices))
        
        # Calculate WMA for sqrt(period)
        sqrt_period = int(np.sqrt(period))
        wma_sqrt = np.zeros(len(prices))
        
        # Helper function to calculate WMA
        def weighted_moving_average(data, window):
            weights = np.arange(1, window+1)
            wma = np.zeros(len(data))
            for i in range(window-1, len(data)):
                wma[i] = np.sum(weights * data[i-window+1:i+1]) / weights.sum()
            return wma
        
        # Calculate all WMAs needed
        wma_half = weighted_moving_average(prices, half_period)
        wma_full = weighted_moving_average(prices, period)
        
        # Calculate raw HMA (2*WMA(n/2) - WMA(n))
        raw_hma = 2 * wma_half - wma_full
        
        # Final smoothing with WMA on sqrt(n) period
        hma = weighted_moving_average(raw_hma, sqrt_period)
        
        return hma
    
    def calculate_rsi(self, prices, period=14):
        """
        Calculate Relative Strength Index (RSI) for given prices and period.
        """
        if len(prices) < period + 1:
            return np.zeros(len(prices))
            
        deltas = np.diff(prices)
        seed = deltas[:period + 1]
        
        # Initial calculations
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - (100. / (1. + rs))
        
        # Subsequent calculations
        for i in range(period, len(prices) - 1):
            delta = deltas[i]
            
            if delta > 0:
                up_val = delta
                down_val = 0.
            else:
                up_val = 0.
                down_val = -delta
                
            up = (up * (period - 1) + up_val) / period
            down = (down * (period - 1) + down_val) / period
            
            rs = up / down
            rsi[i + 1] = 100. - (100. / (1. + rs))
            
        return rsi
    
    def calculate_macd(self, fast_period=12, slow_period=26, signal_period=9):
        """
        Calculate MACD (Moving Average Convergence Divergence) indicator.
        """
        # Calculate EMAs
        fast_ema = self.calculate_ema(self.close, fast_period)
        slow_ema = self.calculate_ema(self.close, slow_period)
        
        # MACD line is fast EMA minus slow EMA
        macd_line = fast_ema - slow_ema
        
        # Signal line is EMA of MACD line
        signal_line = self.calculate_ema(macd_line, signal_period)
        
        # Histogram is MACD line minus signal line
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_ema(self, data, period):
        """
        Calculate Exponential Moving Average (EMA) for given data and period.
        """
        if len(data) < period:
            return np.zeros(len(data))
            
        ema = np.zeros(len(data))
        multiplier = 2 / (period + 1)
        
        # Start with SMA as the first EMA value
        ema[period-1] = np.mean(data[:period])
        
        for i in range(period, len(data)):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
            
        return ema
    
    def calculate_supertrend(self, factor=3, period=10):
        atr = calculate_atr(self.high, self.low, self.close, period)
        hl2 = (self.high + self.low) / 2
        upper = hl2 + (factor * atr)
        lower = hl2 - (factor * atr)
        
        supertrend = np.zeros(len(self.close))
        supertrend[0] = upper[0]
        
        for i in range(1, len(self.close)):
            if self.close[i-1] > supertrend[i-1]:
                supertrend[i] = max(lower[i], supertrend[i-1])
            else:
                supertrend[i] = min(upper[i], supertrend[i-1])
        
        return supertrend
    
    def calculate_trend_direction(self, period=30):
        hh = np.zeros(len(self.close))
        ll = np.zeros(len(self.close))
        
        for i in range(period, len(self.close)):
            hh[i] = np.max(self.high[i-period:i+1])
            ll[i] = np.min(self.low[i-period:i+1])
        
        trend = np.zeros(len(self.close))
        
        for i in range(1, len(self.close)):
            if self.close[i] > hh[i-1]:
                trend[i] = 1
            elif self.close[i] < ll[i-1]:
                trend[i] = -1
            else:
                trend[i] = trend[i-1]
        return trend
    
    def generate_signal(self, i):
        if i < 250:  # Need enough data for indicators
            return None, None, None, None , None
        
        # Check EMA cross
        ema_bullish = self.ema150[i] > self.ema250[i]
        ema_bearish = self.ema150[i] < self.ema250[i]
        
        # Check supertrend cross
        st_bullish = self.close[i] > self.supertrend[i] and self.close[i-1] <= self.supertrend[i-1]
        st_bearish = self.close[i] < self.supertrend[i] and self.close[i-1] >= self.supertrend[i-1]
        
        # Check MACD
        macd_bullish = self.macd[i] > 0 and self.macd[i] > self.macd[i-1]
        macd_bearish = self.macd[i] < 0 and self.macd[i] < self.macd[i-1]
        
        # Check HMA
        hma_bullish = self.hma55[i] > self.hma55[i-2]
        hma_bearish = self.hma55[i] < self.hma55[i-2]
        
        # Check trend direction
        trend_bullish = self.trend_direction[i] > 0
        trend_bearish = self.trend_direction[i] < 0
        
        # Strong signals
        strong_bull = (st_bullish or (self.close[i-1] <= self.supertrend[i-1] and self.trend_direction[i-1] < 0)) and \
                     macd_bullish and ema_bullish and hma_bullish and trend_bullish
        
        strong_bear = (st_bearish or (self.close[i-1] >= self.supertrend[i-1] and self.trend_direction[i-1] > 0)) and \
                     macd_bearish and ema_bearish and hma_bearish and trend_bearish
        
        # Generate signals
        if strong_bull:
            # Calculate stop loss and take profit
            atr = calculate_atr(self.high, self.low, self.close, 14)[i]
            stop_loss = self.low[i] - 2.2 * atr
            take_profit = self.close[i] + (self.close[i] - stop_loss) * risk_to_reward
            return True, self.close[i], stop_loss, take_profit, Deal_Type.long
        
        elif strong_bear:
            atr = calculate_atr(self.high, self.low, self.close, 14)[i]
            stop_loss = self.high[i] + 2.2 * atr
            take_profit = self.close[i] - (stop_loss - self.close[i]) * risk_to_reward
            return True, self.close[i], stop_loss, take_profit, Deal_Type.short
        
        return False, None, None, None, None

def strategy(candles_ob,):
    # Add Fresh Algo strategy
    fresh_algo = FreshAlgoStrategy(candles_ob)
    signal, price, sl, tp, deal_type = fresh_algo.generate_signal(len(candles_ob)-1)
    
    if signal:
        return signal, price, sl, tp, deal_type
    
    return False, None, None, None, None

def test_strategy(ma_period, volume_period, candles_ob, rr):
    deals = []
    orders = []
    in_deal = False
    in_order = False
    
    for candle_index in range(250, len(candles_ob)):  # Start from 250 to have enough data for indicators
        if candle_index % 2000 == 0:
            print(candle_index)
            
        if in_deal == False and in_order == False:
            state, buy_limit_price, stoplose, tp, deal_type = strategy(
                candles_ob=candles_ob[0:candle_index][-1000:], 
            )
            
            if state == True:
                orders.append(Order(
                    deal=Deal(
                        index=candle_index, 
                        stoplose=stoplose, 
                        tp=tp, 
                        inter_price=buy_limit_price,
                        type=deal_type
                    ), 
                    index=candle_index
                ))
                in_order = True

        elif in_deal == True and in_order == False:
            current_deal = deals[-1]
            
            if current_deal.type == Deal_Type.long:
                if candles_ob[candle_index].high >= current_deal.tp:
                    current_deal.state = Deal_State.done
                    in_deal = False
                elif candles_ob[candle_index].close < current_deal.stoplose:
                    current_deal.state = Deal_State.fail
                    in_deal = False
                    
            elif current_deal.type == Deal_Type.short:
                if candles_ob[candle_index].low <= current_deal.tp:
                    current_deal.state = Deal_State.done
                    in_deal = False
                elif candles_ob[candle_index].close > current_deal.stoplose:
                    current_deal.state = Deal_State.fail
                    in_deal = False

        elif in_order == True:
            current_order = orders[-1]
            
            if candle_index - current_order.index > 10:
                in_order = False
            else:
                if current_order.deal.type == Deal_Type.long:
                    if candles_ob[candle_index].low <= current_order.deal.inter_price:
                        in_order = False
                        current_order.deal.index = candle_index
                        deals.append(current_order.deal)
                        in_deal = True
                elif current_order.deal.type == Deal_Type.short:
                    if candles_ob[candle_index].high >= current_order.deal.inter_price:
                        in_order = False
                        current_order.deal.index = candle_index
                        deals.append(current_order.deal)
                        in_deal = True
                        
    return deals

def calaculate_win_rate(deals):
    done_deals = []
    fail_deals = []
    
    for deal in deals:
        if deal.state != None:
            if deal.state == Deal_State.done:
                done_deals.append(deal)
            elif deal.state == Deal_State.fail:
                fail_deals.append(deal)

    all_deals_len = len(done_deals) + len(fail_deals)
    if all_deals_len != 0:
        win_rate = len(done_deals) / all_deals_len
        return all_deals_len, win_rate, done_deals, fail_deals
    return all_deals_len, 0, done_deals, fail_deals

# Run the test
deals = test_strategy(ma_period=14, volume_period=20, candles_ob=candles_data, rr=risk_to_reward)

all_deals_len, win_rate, done_deals, fail_deals = calaculate_win_rate(deals=deals)
print()
print("Deals : ", all_deals_len)
print("Done Deal :", len(done_deals))
print("Fail Deal :", len(fail_deals))
print("Win Rate : ", (win_rate * 100), "%")

balance_list = [balance]
for deal in deals:
    if deal.state == Deal_State.done:
        balance_list.append(balance_list[-1] + ((balance_list[-1] * deal.deal_profit_percent) * rafeha_malia))
    elif deal.state == Deal_State.fail:
        balance_list.append(balance_list[-1] - (((balance_list[-1] * deal.deal_profit_percent) / risk_to_reward) * rafeha_malia))
    deal.print_data()

plt.plot([i for i in range(0, len(balance_list))], [y for y in balance_list])
plt.title("Strategy Performance")
plt.xlabel("Trades")
plt.ylabel("Balance")
plt.grid(True)
plt.show()