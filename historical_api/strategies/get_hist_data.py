import numpy as np
import pandas as pd

from historical_api.settings import logger
import yfinance as yf
import time
from ibapi.contract import Contract
import pandas_ta as ta
import pytz
from pprint import pprint
import datetime

class GetHistData:
    def __init__(self, app,symbol: str,resample:bool ):
        self.app=app
        self.symbol = symbol
        self.resample=resample
        self.time_frame = '15 mins'                                                                                                               # Reference data_frame for resampling purposes
        self.ohlcv={}                                                
        self.indicator_stats={}
        self.time_frames=['15 mins','30 mins','1 hour','2 hours','4 hours','1 day','1 week',]  
        self.time_frame_resample={'15 mins':'15T','30 mins':'30T','1 hour':'60T','2 hours':'120T','4 hours':'240T','1 day':'D','1 week':'W',}
        self.data_to_send={'high_low':[],'indicators':[],'trends':[], 'price':'','ticker':self.symbol['ticker'],'time': '',}
        self.df_main=None
    

        
    def run(self):
        
        # ohlcv
        logger.debug(f'{self.symbol}: Started Working On Main 15 Min candels In order to find Open/High/Low/Close/Volume Stats...')
        self.get_ohlcv()    
                
        # Adding indicators in all time frames 
        time_frames_to_df={}
        if self.resample==False:
            for time_frame in self.time_frames:
                time_frames_to_df[time_frame]=self.fetch_data_and_add_indicators(time_frame)
        else:
            for time_frame in self.time_frames:
                Df=self.df_main.copy()
                if time_frame=='15 mins':
                    time_frames_to_df[time_frame]=self.add_indicator_columns(Df)
                    continue
                _df=Df.resample(self.time_frame_resample[time_frame]).agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})
                print(_df.to_string())          
                _df=self.add_indicator_columns(_df)
                time_frames_to_df[time_frame]=_df
                
        #Indicators    
        map_values={'15 mins':'15min','30 mins':'30min','1 hour':'1hour','2 hours':'2hour','4 hours':'4hour','1 day':'1day','1 week':'1week'}
        d=dict()
        d['indicators']=[]
        l=['SMA(5)','SMA(13)','SMA(52)','SMA(100)','SMA(150)','SMA(200)','STOCKHOSTIC_K' ,'STOCKHOSTIC_D' , 'RSI'  ,'CCI' ,  'BB TOP' ,'BB MIDDLE' ,'BB LOWER','MACD']
        for indicator in l:
            dd={}
            dd['indicator']=indicator
            for time_frame in  time_frames_to_df:
                _df=time_frames_to_df[time_frame]
                ll=len(_df)
                row=_df.iloc[-1]
                dd[map_values[time_frame]]=row[indicator]
            d['indicators'].append(dd)
        
        #high_low
        l=['DAY','NIGHT','YESTERDAY','THIS_WEEK','LAST_WEEK','THIS_MONTH','LAST_MONTH','52WK','YTD']
        d1=dict()
        d1['high_low']=[]
        for time_frame in l:
            dd={}
            dd['timeframe']=time_frame
            for stats in ['open','high','low','close','volume']:
                row=self.ohlcv[time_frame]
                dd[stats]=row[stats]
            d1['high_low'].append(dd)
        
        #Trends
        d2=dict()
        d2['trends']=[]
        dd={}
        df_15_mins=time_frames_to_df['15 mins']
        df_1_hr=time_frames_to_df['1 hour']
        df_4_hr=time_frames_to_df['4 hours']
        df_day=time_frames_to_df['1 day']
        
        #Short
        dd['duration']='Short'
        row_15_min=df_15_mins.iloc[-1]
        if row_15_min['SMA(5)']>row_15_min['SMA(13)']:
            dd['trend']='Up'
        else:
            dd['trend']='Down'
        dd['time']='15min-1Hr'
        d2['trends'].append(dd)
        
        #Medium
        dd={}
        dd['duration']='Medium'
        row_1_hr=df_1_hr.iloc[-1]
        if row_1_hr['SMA(13)']>row_1_hr['SMA(52)']:
            dd['trend']='Up'
        else:
            dd['trend']='Down'
        dd['time']='2hr-4hr'
        d2['trends'].append(dd)
        
        #Long
        dd={}
        dd['duration']='Long'
        row_4_hr=df_4_hr.iloc[-1]
        if row_4_hr['SMA(52)']>row_4_hr['SMA(100)']:
            dd['trend']='Up'
        else:
            dd['trend']='Down'
        dd['time']='day'
        d2['trends'].append(dd)
        
        #Very Long
        dd={}
        dd['duration']='Very Long'
        row_1_day=df_day.iloc[-1]
        if row_1_day['SMA(52)']>row_1_day['SMA(200)']:
            dd['trend']='Up'
        else:
            dd['trend']='Down'
        dd['time']='week'
        d2['trends'].append(dd)
    
        #data
        self.data_to_send['indicators']=d['indicators']
        self.data_to_send['high_low']=d1['high_low']
        self.data_to_send['trends']=d2['trends']
        self.data_to_send['time']=list(df_15_mins.index)[-1]
        self.data_to_send['price']=row_15_min['close']
        
        #pprint(self.data_to_send)
        return self.data_to_send
    
        

    def fetch_data_and_add_indicators(self,time_frame):
            logger.debug(f'Fetching Data in {time_frame},and adding indicatords...')    
            if time_frame=='15 mins':
                df=self.df_main
            else:
                df=self.get_data_by_timeFrame(time_frame)
            if df is None:
                logger.debug(f'Error : No data cant be fetched for timeframe of : {time_frame}')
                return None
            df= self.add_indicator_columns(df)
            df=df.round(2)
            return df

    def get_data_by_timeFrame(self,time_frame):
        
        reqId = self.app.nextorderId
        symbol,exch,sec_type,expiry_date,curr= self.symbol['ticker'],self.symbol['exch'],self.symbol['sec_type'],self.symbol['expiry_date'],self.symbol['curr']
        con = self.app.make_contract(symbol=symbol, exch=exch,sec_type=sec_type,expiry_date=expiry_date,curr=curr)
        
        duration='1 Y'
        if time_frame in ['1 week']:
            duration='8 Y'
        if time_frame =='30 mins':
            duration='1 M'
        
        self.app.reqHistoricalData(reqId=reqId,
                        contract=con,
                        endDateTime='',
                        durationStr=duration,                             
                        barSizeSetting=time_frame,
                        whatToShow='TRADES',
                        useRTH=0,
                        formatDate=1,
                        keepUpToDate=1,
                        chartOptions=[])
        
        self.app.nextorderId += 1
        while reqId not in self.app.histData_end:
            time.sleep(5)
            pass
        
        df = pd.DataFrame(self.app.histData.get(reqId))
        if df is None:
            return 
         
        df=df.set_index('Date')
        
        df.rename(columns = {'Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'}, inplace = True) #'Date':'time',
        return df
    
    def get_ohlcv(self):
        '''
        Functionality : To find OHCLV in (Day,Week,Month,Year,365 Days) time-frame
        
        step-1 : get 15 miniutes , 1years duration dataframe, will call it main df
        step-2 : select two dataframe , first pre-market , second regular-trading-hours, will call pre-main,reg-main
        step-3 : resample pre-main in Day frame and find OHCLV
        step-4 : resample reg-main in (Day,Week,Month,52 Week,365 Day) frame and find current as well previous OHCLV
        '''
        
        df = self.get_data_by_timeFrame(time_frame='15 mins')
        self.df_main=df.copy()
        
        pre_df_15=df.between_time('04:00','9:15').copy()
        pre_df_15.dropna(inplace=True)
        reg_df_15=df.between_time('09:30','16:30').copy()
        reg_df_15.dropna(inplace=True)
        
        pre_df_1D = pre_df_15.resample('1D').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})          # Day - pre-Market       
        reg_df_1D = reg_df_15.resample('1D').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})           # Day - reg-market
        self.ohlcv['DAY']=dict(reg_df_1D.iloc[len(reg_df_1D)-1])
        self.ohlcv['NIGHT']=dict(pre_df_1D.iloc[len(pre_df_1D)-1])
        self.ohlcv['YESTERDAY']=dict(reg_df_1D.iloc[len(reg_df_1D)-2])
        
        reg_df_1W = reg_df_15.resample('1W').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})           # Week - reg-market
        self.ohlcv['THIS_WEEK']=dict(reg_df_1W.iloc[len(reg_df_1W)-1])
        self.ohlcv['LAST_WEEK']=dict(reg_df_1W.iloc[len(reg_df_1W)-2])

        reg_df_1M = reg_df_15.resample('1M').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})           # Month - reg-market 
        self.ohlcv['THIS_MONTH']=dict(reg_df_1M.iloc[len(reg_df_1M)-1])
        self.ohlcv['LAST_MONTH']=dict(reg_df_1M.iloc[len(reg_df_1M)-2])
        
        reg_df_1Y = reg_df_15.resample('365D').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})           # year- reg-market
        self.ohlcv['52WK']=dict(reg_df_1Y.iloc[len(reg_df_1Y)-1]) 
        
        
        reg_df_ytd = reg_df_15.resample('1Y').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})           # year- reg-market
        self.ohlcv['YTD']=dict(reg_df_ytd.iloc[len(reg_df_ytd)-1])

    def add_indicator_columns(self,DF):
        df=DF.copy()
        
        # SMA
        df['SMA(5)'] = ta.sma(df['close'], length=5)
        df['SMA(13)'] = ta.sma(df['close'], length=13)
        df['SMA(52)'] = ta.sma(df['close'], length=52)
        df['SMA(100)'] = ta.sma(df['close'], length=100) 
        df['SMA(150)'] = ta.sma(df['close'], length=150)
        df['SMA(200)'] = ta.sma(df['close'], length=200)
        
        # STOCKHOSTIC           
        df_stoch=ta.stoch(low=df['low'], high=df['high'],close=df['close'])
        df['STOCKHOSTIC_K']=df_stoch['STOCHk_14_3_3']
        df['STOCKHOSTIC_D']=df_stoch['STOCHd_14_3_3']

        # MACD
        df_macd=ta.macd(close=df['close']) #MACD_12_26_9 ,MACDs_12_26_9
        df['MACD']=df_macd['MACD_12_26_9']
        
        # rsi
        df['RSI']=ta.rsi(close=df['close'])
        
        # CCI
        df['CCI']=ta.cci(high=df['high'],close=df['close'],low=df['low'])
        
        # BB
        bb_df=ta.bbands(close=df['close'])        
        df['BB TOP']=bb_df['BBU_5_2.0']
        df['BB MIDDLE']=bb_df['BBM_5_2.0']
        df['BB LOWER']=bb_df['BBL_5_2.0']
        
        return df
        


    
