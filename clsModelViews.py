# -*- coding: utf-8 -*-
"""
Created on Sun Mar 04 17:25:37 2018

@author: John
"""

import clsTrade
import clsPortfolio

import csv

import collections

import pandas as pd
import numpy as np


        
        
StockList = ['AAPL','AMZN','INTC', 'MSFT', 'SNAP']
priceWarning = False

class TradeModelView:
    def __init__(self):
        self.objTrade = clsTrade.Trade()
        self.objPortfolio = clsPortfolio.Portfolio()    
        self.dict_stockBidPx = {}
        self.dict_stockAskPx = {}
        self.dict_stockOpenPx = {}
        self.dict_stockClosePx = {}        
        self.dict_stockStatusPx = {} #Y = good data, N =bad data
        
    #return records for holdings    
    def DisplayCurrentHoldings(self):
        
        self.RefreshPrice()
        
        
        
        print("Current Cash: $" + str(self.objPortfolio.GetCash()))
        currentHoldings = self.objPortfolio.GetPositions()
        
        dict_symbolaggHld = {}
        
        #aggreate holdings (lot level, different by trade time)
        for h in currentHoldings:
            if dict_symbolaggHld.has_key(h.Symbol):
                dict_symbolaggHld[h.Symbol] = dict_symbolaggHld[h.Symbol] + h.Units
            else:
                dict_symbolaggHld[h.Symbol] = h.Units
       
        
        print("Current Holdings:")
        #display sorted holdings
        print("Symbol | Units | Price | Market Value")
        for h_key in sorted(dict_symbolaggHld.keys()):
            current_price = 0
            
            if (self.dict_stockAskPx[h_key] == 0 or  self.dict_stockBidPx[h_key] == 0):
                current_price = self.dict_stockClosePx[h_key]
            else:
                current_price = (self.dict_stockAskPx[h_key] + self.dict_stockBidPx[h_key])/2 #usually curretn price = (bid + ask)/2
           
            market_value = float(dict_symbolaggHld[h_key])*float(current_price) # market value for position = units * current price           
            print(h_key + "   " + str(dict_symbolaggHld[h_key]) + "   " + str(current_price) + "   " + str(market_value) )
    
        
    
    
    def RefreshPrice(self):
        print("Refreshing price...")
        
        priceWarning = False
        
        for sym in StockList:
            stock_quote = clsTrade.Quote #create new instance
            stock_quote = self.objTrade.GetQuote(sym) #get stock quote
            
            #add or update stock bid price
            self.dict_stockBidPx[sym] = stock_quote.Bid
            self.dict_stockAskPx[sym] = stock_quote.Ask
            self.dict_stockOpenPx[sym] = stock_quote.Open
            self.dict_stockClosePx[sym] = stock_quote.Close 
            self.dict_stockStatusPx[sym] = stock_quote.Status
            
            if(stock_quote.Bid == 0 or stock_quote.Ask == 0):
                priceWarning = True                       
    
        if priceWarning == True:
            print("Warning: Some prices have zero $ for bid or ask price, switch to Close price.\n\n")
            
    def TradeBuy(self):
        
    
        #long buy: unit > 0, amount < 0, cost basis = 0, exec date = now, purchased date = ""
        #Cover buy: unit > 0, amount > 0, cost basis > 0, exec date = now, purchased date = original short exec date
        
        #how to calculate the amount, cost basis, unit, and cash
        #long buy: cash = cash + (amount), unit > 0, amount = -1 * unit*current_px, amount < 0
        #Cover buy: cash = cash + (amount), unit > 0, amount = unit * current_px, amount > 0
        
        
        self.RefreshPrice()
        
        #once it is done, clear the screen
        print("\n"*100)
        self.DisplayCurrentHoldings()
        
        print("\nQuote\nStock | Bid | Ask | Open | Close | Quote Status")
        for sym in StockList:
            print(sym + "  " + str(self.dict_stockBidPx[sym]) + " " +  str(self.dict_stockAskPx[sym]) + " " +  str(self.dict_stockOpenPx[sym]) + " " +  str(self.dict_stockClosePx[sym]) + " " +  str(self.dict_stockStatusPx[sym]))

        print("\n")
        print("Action: Buy")
        input_sym = raw_input("Enter the stock symbol:").strip()
        input_units = raw_input("Enter units:").strip()
        
        input_sym = input_sym.upper() #converrt symbol to uppper class
        
        int_units = 0
        
        if input_units.isdigit(): #convert to digit for input
            int_units = int(input_units)    
        
        
        print("Buy " + str(int_units) + " shares of " + str(input_sym))
        
        input_confirm = raw_input("Confirm (Y/N):").strip().upper()
        
        
        if input_confirm == "Y":
            if self.dict_stockBidPx.has_key(input_sym) and input_units.isdigit():
                if int_units > 0: #buy units > 0
                
                    #buy with cover shorting possible:
                    #1. sum of all positions with the same symbol
                    #2. reduce target buy units by short lots in FIFO order
                    #3. if target buy unit > 0 after all lots are covered,
                    #       start to buy, but cash is withhold / used (shorting)
                    
                    
                    
                    #1. sum of all positions with the same symbol
                    
                    #get symbol positions (all +/- lots) 
                    sym_pos = self.objPortfolio.GetPositionsBySym(input_sym)
                    
                    #sort the lots by FIFO order (by purchased date)
                    sym_pos_agg = 0
                    
                    if sym_pos:
                        sym_pos = sorted(sym_pos, key = lambda pos: (pos.PurchasedDate))
                        for p in sym_pos:
                            sym_pos_agg = sym_pos_agg + p.Units
                            
                        
                   
                    current_price = 0
                    if priceWarning == True:
                        current_price = self.dict_stockClosePx[input_sym]
                    else:
                        current_price = self.dict_stockAskPx[input_sym]
                    
                    
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
                                        committedOrder = self.objTrade.OrderEntry("BUY_TO_CLOSE",input_sym,-1* lots.Units,lots.CostBasis,lots.PurchasedDate)
                                           
                                        #update portfolio with order (lot level) to reflect to change the current holdings
                                        self.objPortfolio.UpdatePosition(committedOrder)
                                        
                                    else: #buy is not enough to cover current short lots
                                        
                                        #only partial lots are sold when abs(lots.Units) > buy_units
                                        #calculate partail cost_basis from the short lots
                                        partial_short_costBasis =  (   (float(buy_units)/abs(float(lots.Units))   ) * float(lots.CostBasis))
                                        
                                        #buy unit will be zero after this sell
                                        #retain the original purchased date (exec Date)
                                        committedOrder = self.objTrade.OrderEntry("BUY_TO_CLOSE",input_sym,buy_units,partial_short_costBasis,lots.PurchasedDate)
                                        
                                        buy_units = 0
        
                                        #update portfolio with order (lot level) to reflect to change the current holdings
                                        self.objPortfolio.UpdatePosition(committedOrder)
                                        
                                        break #stop here when the current lot is enough to cover the sells
                            
                        #if there is still remain buy units, meaning all short lots are covered, create just a long buy
                        if buy_units > 0:
                            committedOrder = self.objTrade.OrderEntry("BUY",input_sym,buy_units,0,"")
                            buy_units = 0
                            self.objPortfolio.UpdatePosition(committedOrder)
                    
                    else:
                        print("Not Enough Cash to perform your order.  Order is cancelled.")
        else:    
            print("Cancel!")
        
        input_pause = raw_input("Enter to Continue...").strip()
        
    def TradeSell(self):
        
        
        #long sell: unit < 0, amount > 0, cost basis = (sell units/full units) * full cost basis , exec date = now, purchased date = original long exec date
        #   full units > 0 & full cost basis < 0 & cost basis >0
        
        #Short sell: unit < 0, amount < 0, cost basis = 0, exec date = now, purchased date = ""
        
        
        #how to calculate the amount, cost basis, unit, and cash
        #Long sell:  cash = cash + (amount), unit <0, amount = -1 * unit*current_px, amount > 0
        
        #Short sell: cash = cash + (amount), unit <0, amount = unit * current_px, amount < 0
        
        
        
        self.RefreshPrice()
        
        #once it is done, clear the screen
        print("\n"*100)
        self.DisplayCurrentHoldings()
        
        print("\nQuote\nStock | Bid | Ask | Open | Close | Quote Status")
        for sym in StockList:
            print(sym + "  " + str(self.dict_stockBidPx[sym]) + " " +  str(self.dict_stockAskPx[sym]) + " " +  str(self.dict_stockOpenPx[sym]) + " " +  str(self.dict_stockClosePx[sym]) + " " +  str(self.dict_stockStatusPx[sym]))
        
        print("\n")
        print("Action: Sell")
        input_sym = raw_input("Enter the stock symbol:").strip()
        input_units = raw_input("Enter units:").strip()
        
        input_sym = input_sym.upper() #converrt symbol to uppper class
        
        int_units = 0
        
        if input_units.isdigit(): #convert to digit for input
            int_units = abs(int(input_units))    
        
        
        print("Sell " + str(int_units) + " shares of " + str(input_sym))
        
        input_confirm = raw_input("Confirm (Y/N):").strip().upper()
        
        
        if input_confirm == "Y":
            if self.dict_stockBidPx.has_key(input_sym) and input_units.isdigit():
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
                        
                    #use close price if bid price is zero
                    current_price = 0
                    if(self.dict_stockBidPx[input_sym] == 0):
                        current_price = self.dict_stockClosePx[input_sym]
                    else:
                        current_price = self.dict_stockBidPx[input_sym]
                    
                    
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
                                    committedOrder = self.objTrade.OrderEntry("SELL",input_sym,-1* lots.Units,lots.CostBasis,lots.PurchasedDate)
                                       
                                    #update portfolio with order (lot level) to reflect to change the current holdings
                                    self.objPortfolio.UpdatePosition(committedOrder)
                                    
                                else:
                                    
                                    #only partial lots are sold when lots.Units > sell_units
                                    #calculate partail cost_basis
                                    partial_sell_costBasis =  (float(sell_units)/float(lots.Units) * float(lots.CostBasis))
                                    
                                    #sell unit will be zero after this sell
                                    #retain the original purchased date
                                    committedOrder = self.objTrade.OrderEntry("SELL",input_sym,-1*sell_units,partial_sell_costBasis,lots.PurchasedDate)
                                    
                                    sell_units = 0
    
                                    #update portfolio with order (lot level) to reflect to change the current holdings
                                    self.objPortfolio.UpdatePosition(committedOrder)
                                    
                                    break #stop here when the current lot is enough to cover the sells
                            
                        
                        
                        
                        #3 if sell_unit > 0 after selling all positions, start to short         
                        if sell_units > 0:
                             #sell_unit will be zero after trade
                             #cost_basis is zero for shorting just like long buy
                             
                             #send trade order, for the short sell, original purchase date is "" and no cost basis because it is new position
                             committedOrder = self.objTrade.OrderEntry("SELL_TO_OPEN",input_sym,-1* sell_units,0,"")
                             self.objPortfolio.UpdatePosition(committedOrder)
                    
                    else:                           
                        print("Not Enough Cash to cover your order.  Order is cancelled.")

        else:    
            print("Cancel!")
        
        input_pause = raw_input("Enter to Continue...").strip()

OrderedEntry = collections.namedtuple('Entry',['Side','Ticker','Quantity','ExecPx','MoneyInOut','ExecDate'])

class BlotterModelView:
    def ReadOrderHistory(self):
        entries = []
        
        f = open("OrderHistory.csv",'rb')
        csvReader = csv.reader(f)
        print("Side | Ticker | Quantity | ExecPx | Money In/Out | ExecDate" )
        for row in csvReader:
            if len(row) > 3:
                if(row[0]!='Action'): #skip the header line
                    #File format:
                    #Action,Symbol,Units,Amount,ExecPx,ExecDate,CostBasis,LotPurChasedDate
                    i_entry = OrderedEntry(row[0],row[1],row[2],row[4],row[3],row[5])
                    entries.append(i_entry)
                   
        f.close()
    
        entries = sorted(entries, key = lambda entry: (entry.ExecDate), reverse=True)
                   
        for i_entry in entries:
            print(i_entry.Side + "," + i_entry.Ticker + "," + i_entry.Quantity + "," + i_entry.ExecPx + "," + i_entry.MoneyInOut + "," + i_entry.ExecDate)

class PLModelView:
    def PLView(self):
        self.objTrade = clsTrade.Trade()
        orderHistory = pd.read_csv("OrderHistory.csv")
        portfolio = pd.read_csv("Portfolio.csv")
        symbolList = pd.read_csv("SymbolList.csv")
        
        #get symbol with units for current positions
        sym_pos = pd.pivot_table(portfolio,values='Units', index=['Symbol'], aggfunc=np.sum)
        sym_pos.reset_index(inplace=True) #reset before merging
        
        #get unrealized costbasis for current position
        sym_costbasis = pd.pivot_table(portfolio,values='CostBasis', index=['Symbol'], aggfunc=np.sum)
        sym_costbasis.reset_index(inplace=True) #reset before merging
        
        #get Realized P/L per symbol
        sym_RUL = orderHistory.query('Action == "BUY_TO_CLOSE" or Action == "SELL"')
        sym_RUL = pd.pivot_table(sym_RUL, values=['CostBasis','Amount'], index=['Symbol'], aggfunc=np.sum )
        sym_RUL.reset_index(inplace=True) #reset before merging
        
        
        #merge symbol (with dummy columns) with traded cost basis and amount for Realized P/L
        total_sym = pd.merge(symbolList, sym_RUL, 'outer', on = ['Symbol'])
        total_sym.fillna(0, inplace=True)
        
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
        
        
        total_sym.rename(index=str, columns={"Units": "Positions", "CostBasis": "UPL"})
        
        total_sym.columns =  ['Ticker','WAP','RUL','MarketPx','Positions','UPL']
        
        total_sym = total_sym[['Ticker','Positions','MarketPx','WAP','UPL','RUL']]
        
        
        #update Market Px with quotes
        priceWarning = False
        
        for i, row in total_sym.iterrows():
            tmp_quotes = self.objTrade.GetQuote(row['Ticker']) #get stock quote
            current_px = 0
            
            if(tmp_quotes.Bid == 0 or tmp_quotes.Ask == 0):
                priceWarning = True
                current_px =   float(tmp_quotes.stock_quote.Close)
            else:
                current_px =   (float(tmp_quotes.Bid) +  float(tmp_quotes.Bid))/2
            
            total_sym.set_value(i,'MarketPx',current_px)
        
        #update Unrealized PL =  (current share * price ) + costBasis
        
        #Unrealized P/L
        #for long, (unit * current price) + cost basis
        #for short, (-1 * unit  * current price) + cost basis
        
        for i, row in total_sym.iterrows():
            tmp_UPL = 0
            if row["Positions"] > 0: #long
                tmp_UPL = (row["Positions"] * row["MarketPx"] )+ row["UPL"]
            if row["Positions"] < 0: #Short
                tmp_UPL = row["UPL"] + (-1 * row["Positions"] * row["MarketPx"]) 
            
            total_sym.set_value(i,'UPL',tmp_UPL)
            
        #fix cash line
        for i, row in total_sym.iterrows():
            if row["Ticker"] == 'CASH-1': 
                total_sym.set_value(i,'MarketPx',row["Positions"])
                total_sym.set_value(i,'UPL',0)
                
                
                
        if priceWarning == True:
            print("Warning: Some prices have zero $ for bid or ask price, switch to Close price.\n\n")
            
        
        total_sym.fillna(0, inplace=True)
        
        print(total_sym)