from zigzag import zigzag_type
class trend_type : 
    high ="high"
    low = "low"

class trend_structure_state : 
    BOS = "bos"
    SSL = "ssl"
    BSL = "bsl"
    MSS = "mss"

class trend_structure : 
    def __init__(self , state , s_zigzag , en_zigzag , mid_zigzag , candles) :
        self.state = state
        self.s_zigzag = s_zigzag
        self.en_zigzag = en_zigzag
        self.mid_zigzag = mid_zigzag
        self.candles = candles
    def get_end_candle(self) : 
        candle_price = self.s_zigzag.price()
        candle_index = self.s_zigzag.candle.index
        for i in range(candle_index , len(self.candles)) : 
          if self.s_zigzag.type == zigzag_type.high :
             if self.candles[i].high > candle_price :
                return self.candles[i]
          elif self.s_zigzag.type == zigzag_type.low :
             if self.candles[i].low < candle_price :
                return self.candles[i]
        return self.candles[-1]

class trend : 
    def __init__(self , trend_type , ex_zigzag_list , trend_structure_list) :
        self.trend_type = trend_type
        self.ex_zigzag_list = ex_zigzag_list
        self.trend_structure_list = trend_structure_list
    
    
        
def get_trends (ex_zigzag_list , candles_ob) :
     ex_trend_zigzag_list = []
     trend_structure_list = []
     trends_list = []
     for zigzag_ex_index , zigzag_ex in enumerate(ex_zigzag_list) : 
         ## if we are in the first zigzag
         if zigzag_ex_index < 2 : 
             ex_trend_zigzag_list.append(zigzag_ex)
             continue
         ## if we dont have any trend
         if trends_list == [] : ## if we make HH or LL
            if zigzag_ex_index == 3 :
              if zigzag_ex.price() > ex_zigzag_list[1].price() and zigzag_ex.type == zigzag_type.high : ## Make HH
                  ex_trend_zigzag_list.append(zigzag_ex)
                 
                  trend_structure_list.append(trend_structure(state=trend_structure_state.BOS , s_zigzag= ex_zigzag_list[zigzag_ex_index -2] ,mid_zigzag= ex_zigzag_list[zigzag_ex_index -1],  en_zigzag=zigzag_ex ,candles=candles_ob))
                  trends_list.append(trend(trend_type=trend_type.high , ex_zigzag_list=ex_trend_zigzag_list , trend_structure_list=trend_structure_list ))
              elif zigzag_ex.price() < ex_zigzag_list[1].price() and zigzag_ex.type == zigzag_type.low : ## Make LL
                  ex_trend_zigzag_list.append(zigzag_ex)
                  
                  trend_structure_list.append(trend_structure(state=trend_structure_state.BOS , s_zigzag= ex_zigzag_list[zigzag_ex_index -2] ,mid_zigzag= ex_zigzag_list[zigzag_ex_index -1] , en_zigzag=zigzag_ex , candles=candles_ob))
                  trends_list.append(trend(trend_type=trend_type.low , ex_zigzag_list=ex_trend_zigzag_list , trend_structure_list=trend_structure_list ))
            elif zigzag_ex_index == 2 : 
              if zigzag_ex.price() > ex_zigzag_list[0].price() and zigzag_ex.type == zigzag_type.high: ## Make HH
                  ex_trend_zigzag_list.append(zigzag_ex)
                  
                  trend_structure_list.append(trend_structure(state=trend_structure_state.BOS , s_zigzag= ex_zigzag_list[zigzag_ex_index -2] ,mid_zigzag= ex_zigzag_list[zigzag_ex_index -1] ,en_zigzag=zigzag_ex , candles=candles_ob))
                  trends_list.append(trend(trend_type=trend_type.high , ex_zigzag_list=ex_trend_zigzag_list , trend_structure_list=trend_structure_list ))
              elif zigzag_ex.price() < ex_zigzag_list[0].price() and zigzag_ex.type == zigzag_type.low: ## Make LL
                  ex_trend_zigzag_list.append(zigzag_ex)
                   
                  trend_structure_list.append(trend_structure(state=trend_structure_state.BOS , s_zigzag= ex_zigzag_list[zigzag_ex_index -2],mid_zigzag= ex_zigzag_list[zigzag_ex_index -1] ,en_zigzag=zigzag_ex , candles=candles_ob))
                  trends_list.append(trend(trend_type=trend_type.low , ex_zigzag_list=ex_trend_zigzag_list , trend_structure_list=trend_structure_list ))
              else : 
                   ex_trend_zigzag_list.append(zigzag_ex)
         else : 
             trends_list[-1].ex_zigzag_list.append(zigzag_ex)
             if trends_list[-1].trend_type == trend_type.high : ## trend is high
                 if trends_list[-1].trend_structure_list[-1].state == trend_structure_state.BOS and zigzag_ex.price() >  trends_list[-1].trend_structure_list[-1].en_zigzag.price() : ## trend make bos
                     trends_list[-1].trend_structure_list.append(trend_structure(state=trend_structure_state.BOS , s_zigzag= ex_zigzag_list[zigzag_ex_index-2],mid_zigzag= ex_zigzag_list[zigzag_ex_index -1] ,en_zigzag=zigzag_ex , candles=candles_ob))
                 elif trends_list[-1].trend_structure_list[-1].state == trend_structure_state.SSL and zigzag_ex.price() >  trends_list[-1].trend_structure_list[-1].mid_zigzag.price() : ## trend make bos:
                      trends_list[-1].trend_structure_list.append(trend_structure(state=trend_structure_state.BOS , s_zigzag= ex_zigzag_list[zigzag_ex_index-2],mid_zigzag= ex_zigzag_list[zigzag_ex_index -1] ,en_zigzag=zigzag_ex , candles=candles_ob))
                 elif trends_list[-1].trend_structure_list[-1].state == trend_structure_state.BOS and zigzag_ex.price() < trends_list[-1].trend_structure_list[-1].mid_zigzag.price() : ## make ssl
                     
                     trends_list[-1].trend_structure_list.append(trend_structure(state=trend_structure_state.SSL , s_zigzag= ex_zigzag_list[zigzag_ex_index-2],mid_zigzag= ex_zigzag_list[zigzag_ex_index -1] ,en_zigzag=zigzag_ex , candles=candles_ob))                     
                 elif  trends_list[-1].trend_structure_list[-1].state == trend_structure_state.SSL and zigzag_ex.price() < trends_list[-1].trend_structure_list[-1].en_zigzag.price() : ## make mss and change the trend  ## change the ssl to mss an
                    ## change the last ssl tp mss " mean thats the current trend reverse "
                    trends_list[-1].trend_structure_list[-1].state = trend_structure_state.MSS
                    ## add zigzag to new trend and remove zigzag from the last trend
                    ex_trend_zigzag_list = [trends_list[-1].ex_zigzag_list[-4] ,trends_list[-1].ex_zigzag_list[-3] , trends_list[-1].ex_zigzag_list[-2] , trends_list[-1].ex_zigzag_list[-1] ]
                    trend_structure_list = [trend_structure(state=trend_structure_state.BOS ,s_zigzag= ex_zigzag_list[zigzag_ex_index -2] ,mid_zigzag= ex_zigzag_list[zigzag_ex_index -1]  ,en_zigzag=zigzag_ex , candles=candles_ob)]
                    trends_list[-1].ex_zigzag_list.remove( trends_list[-1].ex_zigzag_list[-1])
                    trends_list[-1].ex_zigzag_list.remove( trends_list[-1].ex_zigzag_list[-1])
                    trends_list[-1].ex_zigzag_list.remove( trends_list[-1].ex_zigzag_list[-1])
                    ## add the trend 
                    trends_list.append(trend(trend_type=trend_type.low , ex_zigzag_list=ex_trend_zigzag_list , trend_structure_list=trend_structure_list ))
             elif trends_list[-1].trend_type == trend_type.low : ## trend is low
                 if trends_list[-1].trend_structure_list[-1].state == trend_structure_state.BOS and zigzag_ex.price() <  trends_list[-1].trend_structure_list[-1].en_zigzag.price() : ## trend make bos
                     trends_list[-1].trend_structure_list.append(trend_structure(state=trend_structure_state.BOS , s_zigzag= ex_zigzag_list[zigzag_ex_index-2],mid_zigzag= ex_zigzag_list[zigzag_ex_index -1] ,en_zigzag=zigzag_ex , candles=candles_ob))
                 elif trends_list[-1].trend_structure_list[-1].state == trend_structure_state.BSL and zigzag_ex.price() <  trends_list[-1].trend_structure_list[-1].mid_zigzag.price() : ## trend make bos:
                      trends_list[-1].trend_structure_list.append(trend_structure(state=trend_structure_state.BOS , s_zigzag= ex_zigzag_list[zigzag_ex_index-2],mid_zigzag= ex_zigzag_list[zigzag_ex_index -1] ,en_zigzag=zigzag_ex , candles=candles_ob))
                 elif trends_list[-1].trend_structure_list[-1].state == trend_structure_state.BOS and zigzag_ex.price() > trends_list[-1].trend_structure_list[-1].mid_zigzag.price() : ## make bsl
                     trends_list[-1].trend_structure_list.append(trend_structure(state=trend_structure_state.BSL , s_zigzag= ex_zigzag_list[zigzag_ex_index-2],mid_zigzag= ex_zigzag_list[zigzag_ex_index -1] ,en_zigzag=zigzag_ex , candles=candles_ob))                     
                 elif  trends_list[-1].trend_structure_list[-1].state == trend_structure_state.BSL and zigzag_ex.price() > trends_list[-1].trend_structure_list[-1].en_zigzag.price() : ## make mss and change the trend  ## change the bsl to mss an
                    ## change the last ssl tp mss " mean thats the current trend reverse "
                    trends_list[-1].trend_structure_list[-1].state = trend_structure_state.MSS
                    ## add zigzag to new trend and remove zigzag from the last trend
                    ex_trend_zigzag_list = [trends_list[-1].ex_zigzag_list[-4] ,trends_list[-1].ex_zigzag_list[-3] , trends_list[-1].ex_zigzag_list[-2] , trends_list[-1].ex_zigzag_list[-1] ]
                    trend_structure_list = [trend_structure(state=trend_structure_state.BOS ,s_zigzag= ex_zigzag_list[zigzag_ex_index -2] ,mid_zigzag= ex_zigzag_list[zigzag_ex_index -1]  ,en_zigzag=zigzag_ex , candles=candles_ob)]
                    trends_list[-1].ex_zigzag_list.remove( trends_list[-1].ex_zigzag_list[-1])
                    trends_list[-1].ex_zigzag_list.remove( trends_list[-1].ex_zigzag_list[-1])
                    trends_list[-1].ex_zigzag_list.remove( trends_list[-1].ex_zigzag_list[-1])
                    ## add the trend 
                    trends_list.append(trend(trend_type=trend_type.high , ex_zigzag_list=ex_trend_zigzag_list , trend_structure_list=trend_structure_list ))
     return trends_list
        
                                
               