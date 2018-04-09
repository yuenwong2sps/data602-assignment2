



#Trade and order history class
#get yahoo stock quote - unused

#Preview trade with symbol, direction, quantity, and total amount
#trade and return result

from requests import get
from bs4 import BeautifulSoup
import re
import collections
import datetime

import clsDB


Quote = collections.namedtuple('Quote',['Symbol','Status','Bid','Ask','Open','Close'])

#database name and table name in mongodb for order history
dbName = "CyptoTrading"
dbTableName = "OrderHistory"

#Order type
#Only one action
#Only one symbol
#Multiple units for taxlot
class Order:
    def __init__(self):
        self._id = 0
        self._units = 0
        self._action = ""
        self._Symbol = ""
        self._amount = 0
        self._ExecPx = 0
        self._CostBasis = 0
        self._ExecDate = datetime.MINYEAR
        self._status = ""
        self._purchasedDate = datetime.MINYEAR
        
    def __getattr__(self,attr):
        self._id = attr.ID
        self._units = attr.Units
        self._action = attr.Action
        self._Symbol = attr.Symbol
        self._amount = attr.Amount
        self._ExecPx = attr.ExecPx
        self._CostBasis = attr.CostBasis
        self._ExecDate = attr.ExecDate
        self._status = attr.Status
        self._purchasedDate = attr.PurchasedDate

    @property
    def ID(self):
        return self._id
    @ID.setter
    def ID(self, x):
        self._id = x
    
    @property
    def Action(self):
        return self._action
    @Action.setter
    def Action(self,x):
        self._action = x
                 
    @property
    def Units(self):
        return self._units
    @Units.setter
    def Units(self,x):
        self._units = x         

    @property
    def Symbol(self):
        return self._Symbol
    
    @Symbol.setter
    def Symbol(self, x):
        self._Symbol = x
    
    @property
    def Amount(self):
        return self._amount
    @Amount.setter
    def Amount(self,x):
        self._amount = x
        
    @property
    def ExecPx(self):
        return self._ExecPx
    
    @ExecPx.setter
    def ExecPx(self,x):
        self._ExecPx = x
    
    @property
    def CostBasis(self):
        return self._CostBasis
    @CostBasis.setter
    def CostBasis(self,x):
        self._CostBasis = x
        
    @property
    def ExecDate(self):
        return self._ExecDate
    @ExecDate.setter
    def ExecDate(self,x):
        self._ExecDate = x
    
    @property
    def Status(self):
        return self._status
    @Status.setter
    def Status(self,x):
        self._status = x
        
    @property
    def PurchasedDate(self):
        return self._purchasedDate
    
    @PurchasedDate.setter
    def PurchasedDate(self,x):
        self._purchasedDate = x

class Trade:
    def __init__(self):
       
        self.id = 0
        #link db
        self.db = clsDB.DB(dbName)
        

    def OrderHistoryRaw(self):
        dbReader = self.db.read(dbTableName)
        return dbReader

    #Enter trade order, return status, exec price, cost basis, save order history
    #cost basis according to the units (not the full original units)
    #PL = difference of Amount and cost basis
    def OrderEntry(self,Action,Symbol,Units,CostBasis,PurchasedDate, quote):
        
        
        #pretent to trade order and save the history
        
        
        #long buy: unit > 0, amount < 0, cost basis = 0, exec date = now, purchased date = ""
        #long sell: unit < 0, amount > 0, cost basis = (sell units/full units) * full cost basis , exec date = now, purchased date = original long exec date
        #   full units > 0 & full cost basis < 0 & cost basis >0
        #Short sell: unit < 0, amount < 0, cost basis = 0, exec date = now, purchased date = ""
        #Cover buy: unit > 0, amount > 0, cost basis = (buy units/full units) * full cost basis, exec date = now, purchased date = original short exec date
        #   full units < 0 & full cost basis < 0 & cost basis > 0
        
        #full cost basis is previous amount
        
        #quote = self.GetQuote(Symbol)
        order = Order()
        order.Symbol = Symbol
        order.Action = Action
        order.Units = Units
        order.PurchasedDate = PurchasedDate        
        
        if Action == "BUY":
           
            #get bitcoin px from other process
            order.ExecPx = quote
           
           #unused code for stock quote 
           # if quote.Ask == 0:
           #     order.ExecPx = quote.Close
           # else:
           #     order.ExecPx = quote.Ask
            
            order.Amount = -1* order.ExecPx *  order.Units
        
        if Action == "SELL":

            #get bitcoin px from other process
            order.ExecPx = quote
           
            #unused code for stock quote
            #if quote.Bid == 0:
            #    order.ExecPx = quote.Close
            #else:
            #    order.ExecPx = quote.Bid
            
            order.Amount = -1* order.ExecPx *  order.Units
        
        
        if Action == "SELL_TO_OPEN":

            #get bitcoin px from other process
            order.ExecPx = quote
            
            #unused code for stock quote
            #if quote.Bid == 0:
            #    order.ExecPx = quote.Close
            #else:
            #    order.ExecPx = quote.Bid
            
            order.Amount = order.ExecPx *  order.Units
        
        
        if Action == "BUY_TO_CLOSE":
            
            #get bitcoin px from other process
            order.ExecPx = quote
            
            #unused code for stock quote
            #if quote.Ask == 0:
            #    order.ExecPx = quote.Close
            #else:
            #    order.ExecPx = quote.Ask
            
            order.Amount = order.ExecPx *  order.Units
        
        
        #buy/short sell have cost basis = 0, sell/cover buy have cost basis
        #value from variable
        order.CostBasis = float(CostBasis) 
        
        
        
        order.ExecDate = str(datetime.datetime.now())
        
        
        order.Status = "Y"
        
        post_data = {
                "Action": order.Action,
                "Symbol": order.Symbol,
                "Units": order.Units,
                "Amount": order.Amount,
                "ExecPx": order.ExecPx,
                "ExecDate": order.ExecDate,
                "CostBasis": order.CostBasis,
                "PurchasedDate": order.PurchasedDate
                
                }
        
        self.db.insert(dbTableName, post_data)
        

        
        return order
    
    
    

    
    #for stock quote, so it is unused
    def GetQuote(self,symbol):
        
        
        BidPx = -1
        AskPx = -1
        OpenPx = -1
        ClosePx = -1
        
        #create url with symbol
        url = 'https://finance.yahoo.com/quote/' + symbol + '/?p=' + symbol
        
        #query page
        response = get(url)
        
        #convert content page to soup object
        soup = BeautifulSoup(response.text, "lxml")
    
        summary_value = ""
    
        #get content with tag id = "quote-summary"
        if soup.find(id="quote-summary"):
            summary_value = soup.find(id="quote-summary").get_text()    
    
        else: #code stop here if id="quote-summary" is not found
            error_q = Quote(symbol,'N',BidPx, AskPx, OpenPx, ClosePx)
            return error_q 
    
        #bid price regular expression
        regex = r'(Bid)[,0-9]*(.)[0-9]*'
    
        #if bid price pattern found
        if re.search(regex,summary_value):
            #get the text of Bid price = Bidxx.xx
            match = re.search(regex,summary_value)
            #extract price and convert to float
            
            BidPx = float(match.group(0).replace('Bid','').replace(',',''))
    
        #ask price regular expression
        regex = r'(Ask)[,0-9]*(.)[0-9]*'
    
        #if bid price pattern found
        if re.search(regex,summary_value):
            #get the text of Bid price = Askxx.xx
            match = re.search(regex,summary_value)
            #extract price and convert to float
            AskPx = float(match.group(0).replace('Ask','').replace(',',''))
    
        #Open price regular expression
        regex = r'(Open)[,0-9]*(.)[0-9]*'
    
        #if Open price pattern found
        if re.search(regex,summary_value):
            #get the text of Open price = Openxx.xx
            match = re.search(regex,summary_value)
            #extract price and convert to float
            OpenPx = float(match.group(0).replace('Open','').replace(',',''))
        
        #Close price regular expression
        regex = r'(Close)[,0-9]*(.)[0-9]*'
    
        #if Close price pattern found
        if re.search(regex,summary_value):
            #get the text of Close price = Closexx.xx
            match = re.search(regex,summary_value)
            #extract price and convert to float
            ClosePx = float(match.group(0).replace('Close','').replace(',',''))
        
    
        #return quote with status = 'N' if fail to retreive price
        if (OpenPx > 0 and ClosePx > 0):        
            q = Quote(symbol,'Y',BidPx, AskPx, OpenPx, ClosePx)
            return q
        else:
            q = Quote(symbol,'N',BidPx, AskPx, OpenPx, ClosePx)
            return q
    
