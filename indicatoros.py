# # Moving Average Class
# class MovingAverage:
#     def __init__(self, index, close_ma, volume_ma):
#         self.index = index
#         self.close_ma = close_ma
#         self.volume_ma = volume_ma

# # Function to calculate Simple Moving Average (SMA)
# def calculate_ma(candles_ob, close_period, volume_period):
#     ma_list = []

#     for i in range(len(candles_ob)):
#         if i >= close_period - 1:
#             close_ma = sum(candle.close for candle in candles_ob[i - close_period + 1 : i + 1]) / close_period
#         else:
#             close_ma = None  # Not enough data points for MA

#         if i >= volume_period - 1:
#             volume_ma = sum(candle.vloume for candle in candles_ob[i - volume_period + 1 : i + 1]) / volume_period
#         else:
#             volume_ma = None  # Not enough data points for MA

#         ma_list.append(MovingAverage(index=candles_ob[i].index, close_ma=close_ma, volume_ma=volume_ma))

#     return ma_list


# -*- coding: utf-8 -*-
from typing import List
import pandas as pd

class MovingAverage:
    def __init__(self, 
                 index: int,
                 close_ma: float = None,
                 volume_ma: float = None,
                 ema_50: float = None,
                 ema_200: float = None,
                 rsi: float = None,
                 bb_middle: float = None,
                 bb_upper: float = None,
                 bb_lower: float = None):
        self.index = index
        self.close_ma = close_ma
        self.volume_ma = volume_ma
        self.ema_50 = ema_50
        self.ema_200 = ema_200
        self.rsi = rsi
        self.bb_middle = bb_middle
        self.bb_upper = bb_upper
        self.bb_lower = bb_lower

def calculate_sma(candles: List, period: int, use_close: bool = True) -> List[float]:
    """Calculate Simple Moving Average"""
    if period < 1:
        raise ValueError("Period must be positive integer")
    
    sma_values = []
    for i in range(len(candles)):
        if i >= period - 1:
            values = [candle.close if use_close else candle.vloume 
                     for candle in candles[i-period+1:i+1]]
            sma = sum(values) / period
            sma_values.append(sma)
        else:
            sma_values.append(None)
    return sma_values

def calculate_ema(candles: List, period: int) -> List[float]:
    """Calculate Exponential Moving Average"""
    if period < 1:
        raise ValueError("Period must be positive integer")
    
    if len(candles) < period:
        return [None] * len(candles)
    
    ema_values = []
    sma = sum(candle.close for candle in candles[:period]) / period
    ema_values.extend([None]*(period-1))
    ema_values.append(sma)
    
    multiplier = 2 / (period + 1)
    
    for i in range(period, len(candles)):
        current_close = candles[i].close
        ema = (current_close - ema_values[-1]) * multiplier + ema_values[-1]
        ema_values.append(ema)
    
    return ema_values

def calculate_rsi(candles: List, period: int = 14) -> List[float]:
    """Calculate Relative Strength Index"""
    if len(candles) < period + 1:
        return [None] * len(candles)
    
    deltas = [candles[i].close - candles[i-1].close 
             for i in range(1, len(candles))]
    gains = [max(delta, 0) for delta in deltas]
    losses = [max(-delta, 0) for delta in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    rsi = [None] * (period)
    if avg_loss == 0:
        rsi.append(100.0)
    else:
        rs = avg_gain / avg_loss
        rsi.append(100 - (100 / (1 + rs)))
    
    for i in range(period + 1, len(candles)):
        avg_gain = (avg_gain * (period - 1) + gains[i-1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i-1]) / period
        
        if avg_loss == 0:
            rsi_value = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi_value = 100 - (100 / (1 + rs))
        rsi.append(rsi_value)
    
    return rsi

def calculate_bollinger_bands(candles: List, period: int = 20, 
                             std_dev: float = 2) -> List[dict]:
    """Calculate Bollinger Bands"""
    bb_values = []
    for i in range(len(candles)):
        if i >= period - 1:
            closes = [candle.close for candle in candles[i-period+1:i+1]]
            sma = sum(closes) / period
            variance = sum((x - sma)**2 for x in closes) / period
            std = variance ** 0.5
            bb_values.append({
                'middle': sma,
                'upper': sma + std_dev * std,
                'lower': sma - std_dev * std
            })
        else:
            bb_values.append({
                'middle': None,
                'upper': None,
                'lower': None
            })
    return bb_values

def calculate_all_indicators(candles_ob: List,
                           ma_period: int = 14,
                           volume_period: int = 20,
                           ema_short: int = 50,
                           ema_long: int = 200,
                           rsi_period: int = 14,
                           bb_period: int = 20,
                           bb_std_dev: float = 2) -> List[MovingAverage]:
    """Calculate all technical indicators with dual EMAs"""
    
    # Validate parameters
    if any(period < 1 for period in [ma_period, volume_period, ema_short, ema_long, rsi_period, bb_period]):
        raise ValueError("All periods must be positive integers")
    
    if bb_std_dev <= 0:
        raise ValueError("Standard deviation multiplier must be positive")
    
    # Calculate indicators
    close_sma = calculate_sma(candles_ob, ma_period, use_close=True)
    volume_sma = calculate_sma(candles_ob, volume_period, use_close=False)
    ema50 = calculate_ema(candles_ob, ema_short)
    ema200 = calculate_ema(candles_ob, ema_long)
    rsi = calculate_rsi(candles_ob, rsi_period)
    bb = calculate_bollinger_bands(candles_ob, bb_period, bb_std_dev)
    
    # Combine results
    results = []
    for i, candle in enumerate(candles_ob):
        results.append(MovingAverage(
            index=candle.index,
            close_ma=close_sma[i],
            volume_ma=volume_sma[i],
            ema_50=ema50[i] if i < len(ema50) else None,
            ema_200=ema200[i] if i < len(ema200) else None,
            rsi=rsi[i] if i < len(rsi) else None,
            bb_middle=bb[i]['middle'],
            bb_upper=bb[i]['upper'],
            bb_lower=bb[i]['lower']
        ))
    
    return results
