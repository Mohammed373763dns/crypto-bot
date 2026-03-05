# ## imports
# from fetch_candles import FechCandlesClass
# from plt_data import PLOT_CHART
# import pandas as pd
# from indicatoros import calculate_ma
# from points_of_intrest import get_gold_area
             
# ## get candles+
# print("==> Get Candles")
# sympol , interval  ,start_index , end_index , percent_change = "btcusdt" , "5m" , 30000 , -5000, 0.2
# candles_data = FechCandlesClass(sympol=sympol ,interval=interval , local_candles_start_index_=start_index , local_candles_end_index=end_index).re_structure_candle_data()
# ma_list = calculate_ma(candles_ob=candles_data["candles_objects_list"] , close_period=14 , volume_period=20)
# gold_area_list = get_gold_area(candles_ob=candles_data["candles_objects_list"] , ma_list=ma_list)


# print(candles_data["candles_objects_list"][0].data()["date"] , "--" ,  candles_data["candles_objects_list"][-1].data()["date"] )
# # print("min :" , candles_data["candles_objects_list"][0].data()["date"].minute)
# # print("hour :" , candles_data["candles_objects_list"][0].data()["date"].hour)
# # print("Day :" , candles_data["candles_objects_list"][0].data()["date"].day)
# # print("Month :" , candles_data["candles_objects_list"][0].data()["date"].month)
# # print("Year :" , candles_data["candles_objects_list"][0].data()["date"].year)
        
# ## plot data
# PLOT_CHART(sympol=sympol , candles_ob=candles_data["candles_objects_list"] , xlim_num=200 , line_candle_type=True , ma_list=ma_list , gold_area_list = gold_area_list , percent_change=percent_change , paint_trend_st=True , paint_ex_zigzag=True).paint()


## imports
from fetch_candles import FechCandlesClass
from plt_data import PLOT_CHART
import pandas as pd
from indicatoros import calculate_all_indicators
from points_of_intrest import get_gold_area
             
## get candles+
print("==> Get Candles")
sympol , interval  ,start_index , end_index , percent_change = "bnbusdt", "15m",  20000 , -1 ,  0.2
candles_data = FechCandlesClass(sympol=sympol ,interval=interval , local_candles_start_index_=start_index , local_candles_end_index=end_index).re_structure_candle_data()
ma_list = calculate_all_indicators(candles_ob=candles_data["candles_objects_list"])
gold_area_list = get_gold_area(candles_ob=candles_data["candles_objects_list"] , ma_list=ma_list)


print(candles_data["candles_objects_list"][0].data()["date"] , "--" ,  candles_data["candles_objects_list"][-1].data()["date"] )
# print("min :" , candles_data["candles_objects_list"][0].data()["date"].minute)
# print("hour :" , candles_data["candles_objects_list"][0].data()["date"].hour)
# print("Day :" , candles_data["candles_objects_list"][0].data()["date"].day)
# print("Month :" , candles_data["candles_objects_list"][0].data()["date"].month)
# print("Year :" , candles_data["candles_objects_list"][0].data()["date"].year)9

print(len(candles_data["candles_objects_list"]))        
## plot data
PLOT_CHART(sympol=sympol , candles_ob=candles_data["candles_objects_list"] , xlim_num=200 , line_candle_type=True , ma_list=ma_list , gold_area_list = gold_area_list , percent_change=percent_change , paint_trend_st=True , paint_ex_zigzag=True , secound_time_frame="4h" ,paint_zigzag=True).paint()