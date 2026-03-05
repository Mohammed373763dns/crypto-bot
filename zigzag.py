class zigzag_type: 
    high = "high"
    low = "low"

class zigzag: 
    def __init__(self, candle, type):
        self.candle = candle
        self.type = type
        
    def price(self) : 
        if self.type == zigzag_type.high : 
            return self.candle.high
        else : 
            return self.candle.low

def remove_duplicate_zigzag (zigzag_list , percent_change) :
    updated_zigzag_list = []
    for zigzag_index , zigzag in enumerate(zigzag_list) : 
        percent_change_peice = (zigzag.price() * (percent_change / 100)) ## the percent of the last zigzag price
        if zigzag_index == 0 : 
            updated_zigzag_list.append(zigzag)
        elif updated_zigzag_list[-1].type == zigzag_type.high and zigzag.type == zigzag_type.high : 
            if zigzag.candle.high > updated_zigzag_list[-1].candle.high : 
                updated_zigzag_list[-1] = zigzag
        elif updated_zigzag_list[-1].type == zigzag_type.low and zigzag.type == zigzag_type.low : 
            if zigzag.candle.low < updated_zigzag_list[-1].candle.low : 
                updated_zigzag_list[-1] = zigzag
        elif (updated_zigzag_list[-1].type == zigzag_type.low and zigzag.type == zigzag_type.high) :
            if (zigzag.price() - updated_zigzag_list[-1].price()) > percent_change_peice :
                updated_zigzag_list.append(zigzag)
        elif (updated_zigzag_list[-1].type == zigzag_type.high and zigzag.type == zigzag_type.low):
            if ( updated_zigzag_list[-1].price() - zigzag.price() ) > percent_change_peice :
                updated_zigzag_list.append(zigzag)
    return updated_zigzag_list

def get_zigzag_data(candles_ob , percent_change):
    # Remove equal highs and lows
    highs = []
    lows = []
    
    # Process highs and lows
    for candle_el_index, candle_el in enumerate(candles_ob ):
        if candle_el_index > 0:
            # Handle highs
            if candles_ob[candle_el_index - 1].high == candle_el.high:
                highs[-1] = candle_el
            else:
                highs.append(candle_el)
            
            # Handle lows
            if candles_ob[candle_el_index - 1].low == candle_el.low:
                lows[-1] = candle_el
            else:
                lows.append(candle_el)
        else:
            highs.append(candle_el)
            lows.append(candle_el)
    
    # Modify highs and lows
    updated_highs = []
    updated_lows = []

    # Determine highs
    for high_el_index, high_el in enumerate(highs):
        if high_el_index > 0 and len(highs) > high_el_index + 1:
            if high_el.high > highs[high_el_index + 1].high and high_el.high > highs[high_el_index - 1].high:
                updated_highs.append(zigzag(high_el, zigzag_type.high))
    
    # Determine lows
    for low_el_index, low_el in enumerate(lows):
        if low_el_index > 0 and len(lows) > low_el_index + 1:
            if low_el.low < lows[low_el_index + 1].low and low_el.low < lows[low_el_index - 1].low:
                updated_lows.append(zigzag(low_el, zigzag_type.low))
    
    # Merge highs and lows
    zigzag_data = updated_highs + updated_lows
    
    # Sort the merged list by the candle index
    zigzag_data.sort(key=lambda zz: candles_ob.index(zz.candle))

    updated_zigzag_list = remove_duplicate_zigzag(zigzag_list=zigzag_data , percent_change=percent_change)

    if updated_zigzag_list[-1].type == zigzag_type.high : 
        if candles_ob[-1].close > updated_zigzag_list[-1].price() : 
            updated_zigzag_list[-1] = zigzag(candle=candles_ob[-1] , type=zigzag_type.high)
        elif candles_ob[-1].close < updated_zigzag_list[-1].price() : 
            updated_zigzag_list.append(zigzag(candle=candles_ob[-1] , type=zigzag_type.low))
    else : 
        if candles_ob[-1].close < updated_zigzag_list[-1].price() : 
            updated_zigzag_list[-1] = zigzag(candle=candles_ob[-1] , type=zigzag_type.low)
        elif candles_ob[-1].close > updated_zigzag_list[-1].price() : 
            updated_zigzag_list.append(zigzag(candle=candles_ob[-1] , type=zigzag_type.high))
    return updated_zigzag_list

def get_external_zigzag(zigzag_list):

    external_zigzag_list = []
    price_range = [zigzag_list[0], zigzag_list[1]]  # Initial range
    
    for zigzag_index, zigzag in enumerate(zigzag_list):
        if zigzag_index < 2:
            external_zigzag_list.append(zigzag)
            continue
        
        if price_range[0].type == zigzag_type.high and price_range[1].type == zigzag_type.low:
            # high -> low => check for new high or low
            if zigzag.price() > price_range[0].price():  # Make new high
                external_zigzag_list.append(zigzag)
                price_range = [zigzag_list[zigzag_index - 1], zigzag]
            elif zigzag.price() < price_range[1].price():  # Make new low
                highest_high = []
                search_index = zigzag_list.index(price_range[1])
                for i in range(search_index + 1, zigzag_index):
                    if not highest_high and zigzag_list[i].type == zigzag_type.high:
                        highest_high.append(zigzag_list[i])
                    elif highest_high:
                        if zigzag_list[i].type == zigzag_type.high and zigzag_list[i].price() > highest_high[0].price():
                            highest_high[0] = zigzag_list[i]
                external_zigzag_list.append(highest_high[0])  # Append the high
                external_zigzag_list.append(zigzag)  # Append the low
                price_range = [highest_high[0], zigzag]
        
        elif price_range[0].type == zigzag_type.low and price_range[1].type == zigzag_type.high:
            # low -> high => check for new low or high
            if zigzag.price() < price_range[0].price():  # Make new low
                external_zigzag_list.append(zigzag)
                price_range = [zigzag_list[zigzag_index - 1], zigzag]
            elif zigzag.price() > price_range[1].price():  # Make new high
                lowest_low = []
                search_index = zigzag_list.index(price_range[1])
                for i in range(search_index + 1, zigzag_index):
                    if not lowest_low and zigzag_list[i].type == zigzag_type.low:
                        lowest_low.append(zigzag_list[i])
                    elif lowest_low:
                        if zigzag_list[i].type == zigzag_type.low and zigzag_list[i].price() < lowest_low[0].price():
                            lowest_low[0] = zigzag_list[i]
                external_zigzag_list.append(lowest_low[0])  # Append the low
                external_zigzag_list.append(zigzag)  # Append the high
                price_range = [lowest_low[0], zigzag]
    
    return external_zigzag_list

def refine_external_zigzag(zigzag_list):
    prev_length = 0
    while True:
        zigzag_list = get_external_zigzag(zigzag_list)
        if len(zigzag_list) == prev_length:
            break  # Stop when the length no longer changes
        prev_length = len(zigzag_list)
    return zigzag_list
    