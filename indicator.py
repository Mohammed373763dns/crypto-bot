import pandas_ta as ta
import pandas as pd

def supertrend_signal(candles, period=10, multiplier=3.0):
    """
    Robust SuperTrend signal generator with complete error handling
    
    Parameters:
    candles (list): List of candle objects with high, low, close attributes
    period (int): SuperTrend period (default 10)
    multiplier (float): SuperTrend multiplier (default 3.0)
    
    Returns:
    str: Signal ('buy', 'sell', 'in buy', 'in sell', 'neutral') or None if error
    """
    # Validate input
    if not candles or len(candles) < period:
        return 'neutral'
    
    try:
        # Safely convert candles to DataFrame
        required_attrs = ['high', 'low', 'close']
        if not all(hasattr(candles[0], attr) for attr in required_attrs):
            return 'neutral'
            
        df = pd.DataFrame([{
            'high': float(getattr(c, 'high', 0)),
            'low': float(getattr(c, 'low', 0)),
            'close': float(getattr(c, 'close', 0))
        } for c in candles])
        
        # Validate DataFrame
        if df.empty or len(df) < period:
            return 'neutral'
            
        # Calculate SuperTrend with validation
        supertrend = ta.supertrend(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            length=period,
            multiplier=multiplier
        )
        
        if supertrend is None or supertrend.empty:
            return 'neutral'
            
        # Safely get column names
        supertd_cols = [col for col in supertrend.columns if 'SUPERTd' in col]
        if not supertd_cols:
            return 'neutral'
            
        supertd_col = supertd_cols[0]
        valid_signals = supertrend.dropna(subset=[supertd_col])
        
        if len(valid_signals) < 2:
            return 'neutral'
            
        # Get signals safely
        last_signal = valid_signals[supertd_col].iloc[-1]
        prev_signal = valid_signals[supertd_col].iloc[-2]
        
        # Determine signal
        if last_signal == 1 and prev_signal == -1:
            return 'buy'
        elif last_signal == -1 and prev_signal == 1:
            return 'sell'
        elif last_signal == 1:
            return 'in buy'
        elif last_signal == -1:
            return 'in sell'
            
        return 'neutral'
        
    except Exception as e:
        # Log error if needed (uncomment below)
        # print(f"SuperTrend signal error: {str(e)}")
        return 'neutral'