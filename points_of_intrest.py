class gold_area_end_state : 
    end = "Ended" 
    not_end = "Not Ended"

class gold_area_type : 
    bullish = "bullish"
    bearsh = "bearsh"

class gold_area : 
    def __init__(self , candle , type , end_state , end_candle = None)  : 
        self.type= type
        self.candle = candle
        self.end_state = end_state
        self.end_candle = end_candle
     
def check_the_gold_end_state (candle , candles_ob , type) : 
    invalidation_bullish= candle.low 
    invalidation_bearsh = candle.high
    for i in range(candle.index + 1 , len(candles_ob)) : 
        if type == gold_area_type.bullish and candles_ob[i].close < invalidation_bullish : 
            return gold_area_end_state.end , candles_ob[i]
        elif type == gold_area_type.bearsh and candles_ob[i].close > invalidation_bearsh : 
            return gold_area_end_state.end , candles_ob[i]            
    return gold_area_end_state.not_end , None


def get_gold_area(candles_ob, ma_list):
    gold_area_list = []
    
    for candle_index, candle in enumerate(candles_ob):
        # Ensure we have enough candles before and after the current one
        if candle_index < 50 or candle_index >= len(candles_ob) - 1:
            continue
        
        # Check volume moving average condition safely
        if (candle_index + 1 < len(candles_ob) and
            candle.vloume > ma_list[candle_index].volume_ma and
            candles_ob[candle_index + 1].vloume > ma_list[candle_index + 1].volume_ma):
            
            # Check if the candle is a swing low
            if (candle_index - 1 >= 0 and candle.low < candles_ob[candle_index - 1].low and
                candle.low < candles_ob[candle_index + 1].low and candles_ob[candle_index -1].low < candles_ob[candle_index -2].low):
                
                # Check the moving average close condition
                if (candle.high < ma_list[candle_index].close_ma and
                    candles_ob[candle_index + 1].close > ma_list[candle_index + 1].close_ma):
                    
                    # Bullish gold area
                    type = gold_area_type.bullish
                    end_state, end_candle = check_the_gold_end_state(
                        candle=candle, candles_ob=candles_ob, type=type
                    )
                    gold_area_list.append(
                        gold_area(candle=candle, end_state=end_state, end_candle=end_candle, type=type)
                    )

            # Check if the candle is a swing high
            elif (candle_index - 1 >= 0 and candle.high > candles_ob[candle_index - 1].high and
                  candle.high > candles_ob[candle_index + 1].high and candles_ob[candle_index -1].high > candles_ob[candle_index -2].high):
                
                # Check the moving average close condition
                if (candle.low > ma_list[candle_index].close_ma and
                    candles_ob[candle_index + 1].close < ma_list[candle_index + 1].close_ma):
                    
                    # Bearish gold area
                    type = gold_area_type.bearsh
                    end_state, end_candle = check_the_gold_end_state(
                        candle=candle, candles_ob=candles_ob, type=type
                    )
                    gold_area_list.append(
                        gold_area(candle=candle, end_state=end_state, end_candle=end_candle, type=type)
                    )
    
    return gold_area_list


def is_price_in_gold_area (candle , gold_area_list) : 
    for gold_area in gold_area_list : 
            if gold_area.end_state == gold_area_end_state.not_end : 
                candle_area = gold_area.candle 
                if gold_area.type == gold_area_type.bullish :
                   if candle.close > candle_area.low and candle.close < candle_area.high : 
                      return True , gold_area
                
    return False , None



def is_we_make_gold_area (candle , gold_area_list) : 
    candle_index = candle.index
    for gold_area in gold_area_list : 
        if gold_area.candle.index == candle_index - 1 : 
            return True , gold_area
    return False , None
