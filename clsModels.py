# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 20:48:47 2018

@author: johnw
"""

import clsTrade
import clsPortfolio

import pandas as pd
import numpy as np

import collections
import clsDB

class PLModel:
    def __init__(self, dictSymbolPx):
        self._entries = []
        
        self.objTrade = clsTrade.Trade()
        self.objPortfolio = clsPortfolio.Portfolio()
        
        
        raworderHistory = self.objTrade.OrderHistoryRaw()
        rawportfolio = self.objPortfolio.ReadHoldingsRawWithCash()
        symbolList = pd.DataFrame(["ETH-USD","BTC-USD","LTC-USD","BCH-USD"])
        
        if raworderHistory and rawportfolio:
        
            orderHistory = pd.DataFrame(list(raworderHistory))
            portfolio= pd.DataFrame(list(rawportfolio))
            
            #get symbol with units for current positions
            sym_pos = pd.pivot_table(portfolio,values='Units', index=['Symbol'], aggfunc=np.sum)
            sym_pos.reset_index(inplace=True) #reset before merging
            
             
            #get unrealized costbasis for current position
            sym_costbasis = pd.pivot_table(portfolio,values='CostBasis', index=['Symbol'], aggfunc=np.sum)
            sym_costbasis.reset_index(inplace=True) #reset before merging
            
            
            
            #get Realized P/L per symbol
            sym_RUL = orderHistory.query('Action == "BUY_TO_CLOSE" or Action == "SELL"')
            
            if sym_RUL.empty:
                sym_RUL = pd.DataFrame([["ETH-USD",0,0],["BTC-USD",0,0],["LTC-USD",0,0],["BCH-USD",0,0]])
                sym_RUL.columns =  ['Symbol','CostBasis','Amount']
            
            sym_RUL = pd.pivot_table(sym_RUL, values=['CostBasis','Amount'], index=['Symbol'], aggfunc=np.sum )
            sym_RUL.reset_index(inplace=True) #reset before merging
            
            
            
            
            symbolList.columns = ["Symbol"] #add column header before merging
            
            symbolList.reset_index(inplace=True)  #reset before merging
            
            
            
            #merge symbol (with dummy columns) with traded cost basis and amount for Realized P/L
            total_sym = pd.merge(symbolList, sym_RUL, 'outer', on = ['Symbol'])
            total_sym.fillna(0, inplace=True)
            
           
            print(total_sym)
            
            #update RUL with costbasis / units
            for i, row in total_sym.iterrows():
                if row['Amount'] == 0 and row['CostBasis'] == 0:
                    tmp_RUL = 0.0
                else: 
                    tmp_RUL = float(row['CostBasis']) + float(row['Amount'])
                total_sym.set_value(i,'RUL',tmp_RUL)
            
            #drop cost basis and amount columns after RUL calculation
            total_sym = total_sym.drop(['Amount', 'CostBasis'], axis=1)
            
            
            #merge position 
            total_sym = pd.merge(total_sym, sym_pos, 'outer', on = ['Symbol'])
            
            #merge cost basis for Unrealised PL 
            total_sym = pd.merge(total_sym, sym_costbasis, 'outer', on = ['Symbol'])
            
            
            #update WAP with costbasis / units
            for i, row in total_sym.iterrows():
                if row['Units'] == 0:
                    tmp_wap = 0.0
                else: 
                    tmp_wap = float(row['CostBasis'])/ float(row['Units'])
                total_sym.set_value(i,'WAP',tmp_wap)
            
            total_sym.fillna(0, inplace=True)
            
            #get current price for each symbol
            for i, row in total_sym.iterrows():
                current_px = dictSymbolPx[row['Symbol']] #get  quote
                total_sym.set_value(i,'MarketPx',current_px)
           
            
            
             #update Unrealized PL =  (current share * price ) + costBasis
            
            
            
             #UPL = CostBasis column at this moment
           
            
            #Unrealized P/L
            #for long, (unit * current price) + cost basis
            #for short, (-1 * unit  * current price) + cost basis
            
            #fix Nan in multiplication
            total_sym.fillna(0, inplace=True)
                        
            for i, row in total_sym.iterrows():
                tmp_UPL = 0
                if row["Units"] > 0: #long
                    tmp_UPL = (float(row["Units"]) * float(row["MarketPx"]) )+ float(row["CostBasis"])
                if row["Units"] < 0: #Short
                    tmp_UPL = float(row["CostBasis"]) + (-1 * float(row["Units"]) * float(row["MarketPx"])) 
                
                total_sym.set_value(i,'CostBasis',tmp_UPL)
                
            #fix cash line
            for i, row in total_sym.iterrows():
                if row["Symbol"] == 'CASH-1': 
                    total_sym.set_value(i,'MarketPx',row["Units"])
                    total_sym.set_value(i,'CostBasis',0)
                    
                    
            #drop unused 'index' column
            total_sym = total_sym.drop(['index'], axis=1)
            
           
            
                    
                
            
            total_sym.fillna(0, inplace=True)
            
            
           
            
            
            #convert pd back to tuples
            tuples = [tuple(x) for x in total_sym.values]
                
                
            self._entries = tuples
        
        #else:
        #    self._entries = () 
        
    @property
    def Entries(self): #P/L Entries
        return self._entries


OrderedEntry = collections.namedtuple('Entry',['Side','Ticker','Quantity','ExecPx','MoneyInOut','ExecDate'])
    
class BlotterModel:
    def __init__(self):
        self._entries = []
        
        dbName = "CyptoTrading"
        dbTableName = "OrderHistory"

         #link db
        self.db = clsDB.DB(dbName)
        
        dbReader = self.db.read(dbTableName)

        for row in dbReader:
        
            #JSON format:
            # {
            # "Action": order.Action,
            # "Symbol": order.Symbol,
            # "Units": order.Units,
            # "Amount": order.Amount,
            # "ExecPx": order.ExecPx,
            # "ExecDate": order.ExecDate,
            # "CostBasis": order.CostBasis,
            # "PurchasedDate": order.PurchasedDate
            # }
        
            i_entry = OrderedEntry(row["Action"],row["Symbol"],row["Units"],row["ExecPx"],row["Amount"],row["ExecDate"])
            self._entries.append(i_entry)
        
        #sort entries for display purpose
        self._entries = sorted( self._entries, key = lambda entry: (entry.ExecDate), reverse=True)
                   
       

    @property
    def Entries(self): #Blotter Entries
        return self._entries

class TradeModel:
    def __init__(self):
        self._committedOrder = clsTrade.Order()
        self.objPortfolio = clsPortfolio.Portfolio()
        self.objTrade = clsTrade.Trade()
        
    @property
    def Entries(self): #Current Holdings
        return self.objPortfolio.GetPositions()
    
    @property
    def AggEntries(self):#Get aggregated holidings
        aggRawHoldings = self.objPortfolio.ReadHoldingsRaw()
        
        if aggRawHoldings:
            _rawentries = list(aggRawHoldings)
            _rawentries_df = pd.DataFrame(_rawentries)
            
            print(_rawentries_df)
            #get symbol with units for current positions
            sym_pos = pd.pivot_table(_rawentries_df,values='Units', index=['Symbol'], aggfunc=np.sum)
            sym_pos.reset_index(inplace=True) #reset before converting
    
            
            tuples = [tuple(x) for x in sym_pos.values]
            
            print(tuples)
            return tuples
        else:
            return [("No Holdings",0)]
    
    @property
    def CashEntry(self):
        return self.objPortfolio.Cash
    
    
            
    def TradeBuy(self,Symbol,Units, sym_price):
        print("TradeBuy")
        
        #long buy: unit > 0, amount < 0, cost basis = 0, exec date = now, purchased date = ""
        #Cover buy: unit > 0, amount > 0, cost basis > 0, exec date = now, purchased date = original short exec date
        
        #how to calculate the amount, cost basis, unit, and cash
        #long buy: cash = cash + (amount), unit > 0, amount = -1 * unit*current_px, amount < 0
        #Cover buy: cash = cash + (amount), unit > 0, amount = unit * current_px, amount > 0
        
        #for any delay priced, unable to get price
        priceWarning = False
        
        input_sym = Symbol.upper() #converrt symbol to uppper class
        
        int_units = Units
               
        if int_units > 0: #buy units > 0
            
            #buy with cover shorting possible:
            #1. sum of all positions with the same symbol
            #2. reduce target buy units by short lots in FIFO order
            #3. if target buy unit > 0 after all lots are covered,
            #       start to buy, but cash is withhold / used (shorting)
                
                
                
            #1. sum of all positions with the same symbol
                
            #get symbol positions (all +/- lots) 
            sym_pos = self.objPortfolio.GetPositionsBySym(Symbol)
                
            #sort the lots by FIFO order (by purchased date)
            sym_pos_agg = 0
                
            if sym_pos:
                sym_pos = sorted(sym_pos, key = lambda pos: (pos.PurchasedDate))
                for p in sym_pos:
                    sym_pos_agg = sym_pos_agg + p.Units
                
            
            
            ###Get price for stock at this moment
            ###later, turn it to get from websocket
                
            #sym_quote = self.objTrade.GetQuote(input_sym) #get  quote
            
            ## for some reasons that unable to get the quote
            ## maybe refuse to accept to trade if it happen
            #if(sym_quote.Bid == 0 or sym_quote.Ask == 0):
            #    priceWarning = True     
            
            
                
            current_price = 0
            ## for best price, use last ask price, otherwise, use the last closed price
            #if priceWarning == True:
            #    current_price = sym_quote.Close 
            #else:
            #    current_price = sym_quote.Ask
            
            current_price = sym_price
                
            buy_units = int_units #copy user input unit to  sell unit                                
              
                
            #Cash control that prevent account in debt, use ask for buy
            #both buy and buy to cover require cash to buy units 
            if int_units * current_price < self.objPortfolio.GetCash():
                
                    
                
            #2. reduce target buy units by short lots in FIFO order
                    
            #long buy: unit > 0, amount < 0, cost basis = 0, exec date = now, purchased date = ""
            #Cover buy: unit > 0, amount > 0, adj cost basis = (buy units/orig units) * orig cost basis, exec date = now, purchased date = original short exec date
   
            #for some of the +/- lots, if aggregated lots is negative, buy to cover first
                if sym_pos_agg < 0:     
        
                    for lots in sym_pos:
                        if lots.Units < 0: #short lots
                            if buy_units >= abs(lots.Units):
                                #reduce target sell units with whole lot
                                buy_units = buy_units - abs(lots.Units)
                                    
                                #send trade order
                                committedOrder = self.objTrade.OrderEntry("BUY_TO_CLOSE",input_sym,-1* lots.Units,lots.CostBasis,lots.PurchasedDate, current_price)
                                       
                                #update portfolio with order (lot level) to reflect to change the current holdings
                                self.objPortfolio.UpdatePosition(committedOrder)
                                    
                            else: #buy is not enough to cover current short lots
                                    
                                #only partial lots are sold when abs(lots.Units) > buy_units
                                #calculate partail cost_basis from the short lots
                                partial_short_costBasis =  (   (float(buy_units)/abs(float(lots.Units))   ) * float(lots.CostBasis))
                                    
                                #buy unit will be zero after this sell
                                #retain the original purchased date (exec Date)
                                committedOrder = self.objTrade.OrderEntry("BUY_TO_CLOSE",input_sym,buy_units,partial_short_costBasis,lots.PurchasedDate, current_price)
                                    
                                buy_units = 0
    
                                #update portfolio with order (lot level) to reflect to change the current holdings
                                self.objPortfolio.UpdatePosition(committedOrder)
                                    
                                break #stop here when the current lot is enough to cover the sells
                        
                #if there is still remain buy units, meaning all short lots are covered, create just a long buy
                if buy_units > 0:
                    committedOrder = self.objTrade.OrderEntry("BUY",input_sym,buy_units,0,"", current_price)
                    buy_units = 0
                    self.objPortfolio.UpdatePosition(committedOrder)
                
            else: # if int_units * current_price < self.objPortfolio.GetCash():....Cash control
                return ("Not Enough Cash to perform your order.  Order is cancelled.")

        return "Done"
        
    
    def TradeSell(self,Symbol,Units, sym_price):
        print("TradeSell")
        
        #long sell: unit < 0, amount > 0, cost basis = (sell units/full units) * full cost basis , exec date = now, purchased date = original long exec date
        #   full units > 0 & full cost basis < 0 & cost basis >0
        
        #Short sell: unit < 0, amount < 0, cost basis = 0, exec date = now, purchased date = ""
        
        
        #how to calculate the amount, cost basis, unit, and cash
        #Long sell:  cash = cash + (amount), unit <0, amount = -1 * unit*current_px, amount > 0
        
        #Short sell: cash = cash + (amount), unit <0, amount = unit * current_px, amount < 0
        
        
        #priceWarning = True  
      
        
        input_sym = Symbol.upper() #converrt symbol to uppper class
        
        int_units = Units
        
        
        

        if int_units > 0: # units > 0
        
            #sell with short possible:
            #1. sum of all positions with the same symbol
            #2. reduce target sell unit by lots in FIFO order
            #3. if target sell unit > 0 after all lots are sold,
            #       start to short, but cash is withhold / used (shorting)
            
            
            
            
            #get symbol positions (all lots) 
            sym_pos_agg = 0
            
            sym_pos = self.objPortfolio.GetPositionsBySym(input_sym)
            
            if sym_pos:
            
            #sort the lots by FIFO order (by purchased date)
                sym_pos = sorted(sym_pos, key = lambda pos: (pos.PurchasedDate))
                for p in sym_pos:
                    sym_pos_agg = sym_pos_agg + p.Units



            ###Get price for stock at this moment
            ###later, turn it to get from websocket
                
            #sym_quote = self.objTrade.GetQuote(input_sym) #get  quote
             
            
            
            ## for some reasons that unable to get the quote
            ## maybe refuse to accept to trade if it happen
            #if(sym_quote.Bid == 0 or sym_quote.Ask == 0):
            #    priceWarning = True     
            
            
                
            current_price = 0
            ## for best price, use last bid price, otherwise, use the last closed price
            #if priceWarning == True:
            #    current_price = sym_quote.Close 
            #else:
            #    current_price = sym_quote.Bid

            current_price = sym_price
            
            #1. sum of all positions with the same symbol

                
            #3. if target sell unit > 0 after all lots are sold,
            #       start to short, but cash is withhold / used (shorting)
            
            
            sell_units = int_units #copy user input unit to  sell unit                                
            
            #overall check: available fund - (sell unit - sum of aggregated holdings) * price > 0
            
            if self.objPortfolio.GetCash() - ((sell_units - sym_pos_agg) * current_price) > 0:
                
                #2. reduce target sell units by long lots in FIFO order
                
                #long sell: unit < 0, amount > 0, adj cost basis = (sell units/full units) * full cost basis, exec date = now, purchased date = original long exec date
                if sym_pos_agg > 0:
                    for lots in sym_pos:
                        if sell_units >= lots.Units:
                            #reduce target sell units with whole lot
                            sell_units = sell_units - lots.Units
                            
                            #send trade order
                            committedOrder = self.objTrade.OrderEntry("SELL",input_sym,-1* lots.Units,lots.CostBasis,lots.PurchasedDate, current_price)
                               
                            #update portfolio with order (lot level) to reflect to change the current holdings
                            self.objPortfolio.UpdatePosition(committedOrder)
                            
                        else:
                            
                            #only partial lots are sold when lots.Units > sell_units
                            #calculate partail cost_basis
                            partial_sell_costBasis =  (float(sell_units)/float(lots.Units) * float(lots.CostBasis))
                            
                            #sell unit will be zero after this sell
                            #retain the original purchased date
                            committedOrder = self.objTrade.OrderEntry("SELL",input_sym,-1*sell_units,partial_sell_costBasis,lots.PurchasedDate, current_price)
                            
                            sell_units = 0

                            #update portfolio with order (lot level) to reflect to change the current holdings
                            self.objPortfolio.UpdatePosition(committedOrder)
                            
                            break #stop here when the current lot is enough to cover the sells
                    
                
                
                
                #3 if sell_unit > 0 after selling all positions, start to short         
                if sell_units > 0:
                     #sell_unit will be zero after trade
                     #cost_basis is zero for shorting just like long buy
                     
                     #send trade order, for the short sell, original purchase date is "" and no cost basis because it is new position
                     committedOrder = self.objTrade.OrderEntry("SELL_TO_OPEN",input_sym,-1* sell_units,0,"", current_price)
                     self.objPortfolio.UpdatePosition(committedOrder)
            
            else: #if self.objPortfolio.GetCash() - ((sell_units - sym_pos_agg) * current_price) > 0:                          
                print("Not Enough Cash to cover your order.  Order is cancelled.")

        
        return "Done"        
        
    
    #def _OrderEntry(self,Action,Symbol,Units,CostBasis,PurchasedDate):
    #    print("OrderEntry")           