import pandas as pd
import json
# from binance import Client ;
# client = Client(); 
# class Candels 
class CandleClass : 
    def __init__(self , timestamp , close , open , high , low , vloume , index ) :
        self.timestamp =timestamp;
        self.close = float(close) ;
        self.open =float(open);
        self.high = float(high) ;
        self.low =float(low);
        self.vloume = float(vloume) ;
        self.date =pd.to_datetime(timestamp, unit='ms')     
        self.index = index
    def data(self):
        return {
                "index" : self.index, 
                "open" : self.open ,
                "close" :self.close ,
                "high" : self.high ,
                "low" : self.low ,
                "vloume": self.vloume ,
                "date" : self.date
            }
        
# Fech Candles Class
class FechCandlesClass:
    feched_Candles = [];
    def __init__(self , local_candles_start_index_ = 10000 ,local_candles_end_index = None, client = None,sympol="BTCUSDT", interval="1h", start_time=(pd.Timestamp.utcnow() - pd.DateOffset(days=50)).isoformat() ) :
        self.client = client ;
        self.sympol = sympol ;
        self.interval = interval ;
        self.start_time = start_time;
        self.local_candles_start_index = local_candles_start_index_ ;
        self.local_candles_end_index = local_candles_end_index;
        # self.feched_Candles = [] ;
        self.feched_Candles = self.get_Local_Candles() ;
    def get_candles_from_Binance_api(self ):
        try:
            # Fetch historical candlestick data
            candles = self.client.get_historical_klines(self.sympol, self.interval, self.start_time)
            self.feched_Candles = candles
        except Exception as e:
            print(f"Error fetching historical candles: {e}")
            return None

        if not candles:
            print("No data retrieved from Binance API.")
            return None

    def update_Local_Candle_File(self):
        with open('data/candles_'+str(self.sympol)+'_'+str(self.interval)+'.json', 'w') as file:
            json.dump(self.feched_Candles, file, indent=4)


    def get_Local_Candles(self):
        with open('data/candles_'+str(self.sympol)+'_'+str(self.interval)+'.json', 'r') as file:
            array = json.load(file)
        return list(array[-(self.local_candles_start_index):self.local_candles_end_index])
    
    def re_structure_candle_data(self) :
       columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
       Candles_Objects_List = [];
       for index ,candle in enumerate(self.feched_Candles) :
           Candles_Objects_List.append(CandleClass(timestamp=candle[0] ,open=candle[1] , high=candle[2] , low=candle[3], close=candle[4] ,vloume=candle[5] , index=index));
       candle_for_df = [[candle[0], float(candle[1]), float(candle[2]), float(candle[3]), float(candle[4]), float(candle[5])] for candle in self.feched_Candles]
       Candles_DF = pd.DataFrame(candle_for_df ,columns=columns )
       return {
          "candles_objects_list" : Candles_Objects_List ,
          "candles_df" : Candles_DF
       }


# fechCandlesClass  = FechCandlesClass(client=client,sympol="BTCUSDT" , interval="1h" ,  start_time=(pd.Timestamp.utcnow() - pd.DateOffset(hours=  10000)).isoformat() )
# fechCandlesClass.get_candles_from_Binance_api()
# fechCandlesClass.update_Local_Candle_File()