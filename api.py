import uvicorn
from fastapi import FastAPI
import threading
import time
from fastapi.responses import HTMLResponse
from  historical_api.client.ib import TradingApp
from historical_api.strategies.get_hist_data import GetHistData
from historical_api.settings import BASE_DIR

# Initialize app
app = FastAPI()




# # Create new thread and run it in background
# client_thread = IBApi()
# client_thread.daemon = True
# client_thread.start()


@app.get("/")
async def get():
    html_file_path = BASE_DIR / 'index.html'
    with open(html_file_path, "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.get('/data')
async def get_data(symbol: str):
    # Function to fetch data for give symbol
    #'ticker':'ES','exch':'CME','sec_type':'FUT','expiry_date':'202309','curr':'USD'
    # ES-202309, ES-FUT-CME-202309, ES-STK-SMART
    symbol = symbol.strip().upper()
    sym, exp = symbol.split('-')
    
    def websocket_con():
        client.run()
    client = TradingApp()
    socket_port = 7497 
    client.connect("127.0.0.1", socket_port, clientId=1)
    con_thread = threading.Thread(target=websocket_con, daemon=True)
    con_thread.start()
    time.sleep(5)
    print('connected!')

    
    obj = GetHistData(symbol={'ticker':sym,'exch':'CME','sec_type':'FUT','expiry_date':exp,'curr':'USD'},app=client,resample=False)
    data = obj.run()
    # data = data_function(symbol=symbol)
    # data = {'high_low': [
    #                         {'timeframe': 'Night', 'open': 98, 'high': 101, 'low': 97, 'close': 99.5, 'volume': 10654},
    #                         { 'timeframe': 'Day', 'open': 98, 'high': 101, 'low': 97, 'close': 99.5, 'volume': 10454},
    #                         {'timeframe': 'Yesterday',  'open': 98,  'high': 101,  'low': 97,  'close': 99.5,  'volume': 10465},
    #                         {'timeframe': 'This Week', 'open': 98, 'high': 101, 'low': 97, 'close': 99.5, 'volume': 10454},
    #                         {'timeframe': 'Last Week', 'open': 98, 'high': 101, 'low': 97, 'close': 99.5, 'volume': 1454}
    #     ],
    #         'indicators': [
    #             {
    #             'indicator': 'SMA(5)',
    #             '15min': 98.45, 
    #             '30min': 99.6, 
    #             '1hour': 99.12, 
    #             '2hour': 99.45,
    #             '4hour': 100.3, 
    #             '1day': 99.95},
                
    #             {
    #             'indicator': 'SMA(15)', 
    #             '15min': 98.45, 
    #             '30min': 99.6, 
    #             '1hour': 99.12, 
    #             '2hour': 99.45,
    #             '4hour': 100.3, 
    #             '1day': 99.95},
    #                        {'indicator': 'SMA(30)', '15min': 98.45, '30min': 99.6, '1hour': 99.12, '2hour': 99.45,
    #                         '4hour': 100.3, '1day': 99.95},
    #                        {'indicator': 'SMA(52)', '15min': 98.45, '30min': 99.6, '1hour': 99.12, '2hour': 99.45,
    #                         '4hour': 100.3, '1day': 99.95},
    #                        {'indicator': 'SMA(100)', '15min': 98.45, '30min': 99.6, '1hour': 99.12, '2hour': 99.45,
    #                         '4hour': 100.3, '1day': 99.95},
    #                        {'indicator': 'SMA(200)', '15min': 98.45, '30min': 99.6, '1hour': 99.12, '2hour': 99.45,
    #                         '4hour': 100.3, '1day': 99.95}],
            
    #         'trends': [
    #             {'duration': 'Short', 'time': '15 Min-1 Hour', 'trend': 'Up'},
    #                    {'duration': 'Medium', 'time': 'Day', 'trend': 'Down'},
    #                    {'duration': 'Long', 'time': 'Week', 'trend': 'Up'}],
    #         'price': 101.25,
    #         'ticker': symbol,
    #         'time': '2023-07-07 10:05'}
    # # # If any error
    # # if error:
    #     return {"success": False, "message": "Error fetching data"}

    return {"success": True, "message": "Successfully fetched data", **data}


if __name__ == "__main__":
    host = "127.0.0.1"
    uvicorn.run(app, host=host, port=8000, log_level="info")
    # uvicorn api:app --host 0.0.0.0 --port 80

