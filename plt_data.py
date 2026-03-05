import matplotlib.pyplot as plt 
from points_of_intrest import gold_area_type , gold_area_end_state
from zigzag import get_zigzag_data, refine_external_zigzag
from trends import get_trends, trend_structure_state
import numpy as np


# => 
class PLOT_CHART : 
    def __init__(self , sympol  , candles_ob ,ma_list , gold_area_list, percent_change ,xlim_num = 1000 , candles_color = "black"  ,   line_candle_type = False , paint_candles = True , paint_trend_st = True , paint_zigzag = False , paint_ex_zigzag = True , secound_time_frame = "5m") :
        self.sympol = sympol
        self.candles_ob= candles_ob
        self.xlim_num = xlim_num
        self.candles_color= candles_color
        self.paint_candles = paint_candles
        self.line_candle_type = line_candle_type
        self.ma_list =ma_list
        self.gold_area_list = gold_area_list
        self.paint_trend_st =paint_trend_st
        self.paint_zigzag =paint_zigzag
        self.paint_ex_zigzag =paint_ex_zigzag
        self.percent_change = percent_change
        self.secound_time_frame = secound_time_frame
    def paint_horizantal_line( self , x_start , x_end ,y_line , color = "red"):
       x= [x_start , x_end]
       y= [y_line , y_line]
       plt.plot(x , y , color = color)
    def paint_MovingAverage(self ,macd_list  , color) : 
        plt.plot( macd_list , color =color)
    ## painy_candle
    def plt_candles(self, candles_ob):
        if self.paint_candles:
            if self.line_candle_type:
                plt.plot([candle.index for candle in candles_ob], [candle.close for candle in candles_ob], color=self.candles_color)
            else:
                for candle in candles_ob:
                    color = "green" if candle.open <= candle.close else "red"
                    plt.plot([candle.index + 0.5, candle.index + 0.5], [candle.open, candle.high], color=color, lw=2)
                    plt.plot([candle.index + 0.5, candle.index + 0.5], [candle.close, candle.low], color=color, lw=2)
                    plt.fill([candle.index + 0.2, candle.index + 0.8, candle.index + 0.8, candle.index + 0.2],
                             [candle.open, candle.open, candle.close, candle.close], color=color)
    
    def check_in_mss (self , mss_list_index , candle_index) : 
        state = False
        for mss_index in mss_list_index : 
            if candle_index >= mss_index[0] and candle_index <= mss_index[1] : 
                state = True 
                break
        return state



    def paint_gold_area_list (self , mss_list_index , gold_area_list ,candles_ob , color1 = "red" , color2 = "green" ) : 
        for gold_area in gold_area_list : 
            # is_in_mss = self.check_in_mss(mss_list_index = mss_list_index , candle_index= gold_area.candle.index)
            # if is_in_mss == False : continue
            candle = gold_area.candle
            start_index = gold_area.candle.index
            end_index = candles_ob.index(candles_ob[-1])
            color = color1
            if gold_area.end_state == gold_area_end_state.end : end_index = gold_area.end_candle.index 
            if gold_area.type == gold_area_type.bullish : color = color2
            plt.fill([start_index +0.5, end_index + 0.2, end_index +0.2, start_index +0.5],
                             [candle.high, candle.high, candle.low, candle.low], color=color , alpha=0.5)

    # def plt_ma (self , ma_list ) : 
    #     x = [ma.index for ma in ma_list]
    #     y_sma = [ma.close_ma for ma in ma_list]
    #     y_b_upper = [ma.bb_upper for ma in ma_list]
    #     y_b_down = [ma.bb_lower for ma in ma_list]
    #     plt.plot(x , y_sma , color = "black")
    #     plt.plot(x , y_b_upper , color = "blue")
    #     plt.plot(x , y_b_down , color = "red")


    def plt_ma(self, ma_list):
        x = [ma.index for ma in ma_list]
        y_sma = [ma.close_ma if ma.close_ma is not None else np.nan for ma in ma_list]
        y_b_upper = [ma.bb_upper if ma.bb_upper is not None else np.nan for ma in ma_list]
        y_b_down = [ma.bb_lower if ma.bb_lower is not None else np.nan for ma in ma_list]

        # Convert to numpy arrays (optional but helps with masking)
        x = np.array(x)
        y_sma = np.array(y_sma, dtype=float)
        y_b_upper = np.array(y_b_upper, dtype=float)
        y_b_down = np.array(y_b_down, dtype=float)

        # Highlight areas (matplotlib will ignore NaN values)
        # plt.fill_between(x, y_sma, y_b_upper, color='blue', alpha=0.2)
        # plt.fill_between(x, y_sma, y_b_down, color='red', alpha=0.2)

        # Plot the lines
        plt.plot(x, y_sma, color="black", label="SMA")
        # plt.plot(x, y_b_upper, color="blue", label="Bollinger Upper")
        # plt.plot(x, y_b_down, color="red", label="Bollinger Lower")
        plt.legend()

    def paint_trends_candles_list(self, trends_list, zigzag_list, external_zigzag_list ):
        if self.paint_trend_st:
            for trend in trends_list:
                for  structure_line in trend.trend_structure_list:
                    color = "green" if structure_line.state != trend_structure_state.MSS else "red"
                    color = "orange" if structure_line.state in [trend_structure_state.BSL, trend_structure_state.SSL] else color                    
                    candle_cross = structure_line.get_end_candle()
                    plt.plot([structure_line.s_zigzag.candle.index + 0.5, candle_cross.index + 0.2],
                             [structure_line.s_zigzag.price(), structure_line.s_zigzag.price()], color=color)

        if self.paint_zigzag:
            plt.plot([z.candle.index + 0.5 for z in zigzag_list], [z.price() for z in zigzag_list], color="blue", linestyle='-')

        if self.paint_ex_zigzag:
            plt.plot([ex.candle.index + 0.5 for ex in external_zigzag_list], [ex.price() for ex in external_zigzag_list], color="blue", linestyle='-')
    def get_mss_index_list (self , trends_list) : 
        mss_list_index = []
        for trend in trends_list : 
            for  structure_line in trend.trend_structure_list: 
                if  structure_line.state == trend_structure_state.MSS : 
                    mss_list_index.append([structure_line.s_zigzag.candle.index , structure_line.en_zigzag.candle.index])
        return mss_list_index


    def paint(self) : 
        # Detect zigzag and trends and paint it
        zigzag_list = get_zigzag_data(candles_ob=self.candles_ob, percent_change=self.percent_change)
        external_zigzag_list = refine_external_zigzag(zigzag_list=zigzag_list)
        trends_list = get_trends(ex_zigzag_list=external_zigzag_list, candles_ob=self.candles_ob)
        ## get mss list index  
        mss_list_index = self.get_mss_index_list(trends_list=trends_list) 

        ## plt first graf     
        # plt.subplot(1,2,1)
        ## paint candles
        self.plt_candles(candles_ob=self.candles_ob) 
        ## paint_ma 
        self.plt_ma(ma_list=self.ma_list)
        ## paint zigzag , trends
        self.paint_trends_candles_list(trends_list=trends_list, zigzag_list=zigzag_list, external_zigzag_list=external_zigzag_list)
        ## paint gold_area
        self.paint_gold_area_list(mss_list_index = mss_list_index , candles_ob=self.candles_ob , gold_area_list=self.gold_area_list)   
        ## chart info      
        plt.title(self.sympol + " " +"Chart")
        plt.xlim(0,self.xlim_num)

        ## plt secound graf
        # plt.subplot(1,2,2)

        # ## 1- get the date range 
        # candle_date_range = [self.candles_ob[0].date , self.candles_ob[-1].date]
        
        # ## 2- get the lower time farame candles list
        # candles_lower_tf = FechCandlesClass(sympol=self.sympol ,interval=self.secound_time_frame , local_candles_start_index_=100000 , local_candles_end_index=-1).re_structure_candle_data()["candles_objects_list"]
        # updated_candles_lower_tf = []
        # candle_index = 0
        # for candle in candles_lower_tf :
        #     if candle.date >= candle_date_range[0] and candle.date <= candle_date_range[1]: 
        #         candle.index = candle_index
        #         updated_candles_lower_tf.append(candle)
        #         candle_index = candle_index + 1

        # print( "len",len(updated_candles_lower_tf))
        # ma_lower_tf = calculate_ma(candles_ob=updated_candles_lower_tf ,close_period=14 , volume_period=20)
        # gold_area_list_ltf = get_gold_area(candles_ob=updated_candles_lower_tf , ma_list=ma_lower_tf)
        # golf_area_htf_ltf = []
        # for area in self.gold_area_list : 
        #     area_candle = area.candle
        #     area_end_candle = area.end_candle
        #     area.candle.index =0, 
        #     for ltf_candle in updated_candles_lower_tf : 
        #         if ltf_candle.date == area_candle.date :
        #             area.candle.index = ltf_candle.index 
        #         elif  area_end_candle != None :   
        #             if ltf_candle.date == area_end_candle.date :
        #                area.end_candle.index = ltf_candle.index
        #     golf_area_htf_ltf.append(area)
        # self.plt_candles(candles_ob=updated_candles_lower_tf) 
        # ## paint_ma 
        # self.plt_ma(ma_list=ma_lower_tf)
        # ## paint gold_area
        # self.paint_gold_area_list(mss_list_index = mss_list_index , candles_ob=updated_candles_lower_tf , gold_area_list=gold_area_list_ltf)

        # self.paint_gold_area_list(mss_list_index = mss_list_index , candles_ob=updated_candles_lower_tf , gold_area_list=golf_area_htf_ltf , color1="orange" , color2="blue")


# class gold_area : 
#     def __init__(self , candle , type , end_state , end_candle = None)  : 
#         self.type= type
#         self.candle = candle
#         self.end_state = end_state
#         self.end_candle = end_candle
      


        ## run
        plt.show()
