
from dateutil.parser import parse
from historical_api.settings import logger, TZ, BASE_DIR, CONFIG_DIR, RECORDS_DIR
import time
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from historical_api.settings import logger
import pytz


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        
        self.histData = {}
        self.histData_end = set()
        self.errors_store = set()
        self.error_ids = list()
        self.ltp={}
        self.reqid_to_ticker = {}


    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId


    def error(self, reqId, errorCode: int, errorString: str, advancedOrderRejectJson=""):
        super().error(reqId, errorCode, errorString, advancedOrderRejectJson)
        self.error_ids.append(reqId)
        errorCode = int(errorCode)
        if errorCode == 10090: return
        if errorCode == 300: return
        if advancedOrderRejectJson:
            logger.debug("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString, "AdvancedOrderRejectJson:",
                         advancedOrderRejectJson)
        else:
            if errorCode != 300:
                logger.debug(f'Error. Id:", {reqId} "Code:", {errorCode}, "Msg:", {errorString}')


    def historicalData(self, reqId, bar):
        date_str = bar.date if len(bar.date.split()) < 2 else bar.date.split()[0] + ' ' + bar.date.split()[1]
        
        if reqId not in self.histData:
            self.histData[reqId] = [
                {"Date": parse(date_str).astimezone(pytz.timezone('US/Eastern')), "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume}]
        else:
            self.histData[reqId].append(
                {"Date": parse(date_str).astimezone(pytz.timezone('US/Eastern')), "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume})
    @staticmethod
    def make_contract(symbol, sec_type, exch, prim_exch=None, curr='USD', opt_type=None, expiry_date=None,
                      strike=None, multipler=100, tradingClass=None):
        contract = Contract()
        contract.symbol = str(symbol)
        contract.secType = sec_type
        contract.exchange = exch
        contract.primaryExch = prim_exch
        contract.currency = str(curr)
        contract.lastTradeDateOrContractMonth = str(expiry_date)
        
        if sec_type == 'OPT':
            contract.multiplier = multipler
            if expiry_date != None:
                contract.lastTradeDateOrContractMonth = str(expiry_date)
            if opt_type != None:
                contract.right = str(opt_type)
            if strike != None:
                contract.strike = float(strike)
            if tradingClass != None:
                contract.tradingClass = tradingClass 
        return contract

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        self.histData_end.add(reqId)
    
    def stop_streaming(self, reqId):
        super().cancelMktData(reqId)

                    
