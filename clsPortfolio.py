# -*- coding: utf-8 -*-
"""
Created on Sat Mar 03 18:44:56 2018

@author: John
"""

#Portfolio     
#from portfolio.csv
#portfolio, cash, security, price, quantity
#read(), write()


import csv
import clsTrade

portfolioFile = "Portfolio.csv"


class Position:
    def __init__(self):
        self.Symbol = ""
        self.Units = "" #positive for long, negative for short
        self.PurchasedPx = 0
        self.PurchasedDate = 1900/01/01
    
    @property
    def Symbol(self):
        return self._Symbol
    @Symbol.setter
    def Symbol(self, x):
        self._Symbol = x
    
    @property
    def Units(self):
        return self._Units
    @Units.setter
    def Units(self,x):
        self._Units = x
    
    @property    
    def PurchasedPx(self):
        return self._PurchasedPx
    @PurchasedPx.setter
    def PurchasedPx(self,x):
        self._PurchasedPx = x
    
    @property    
    def PurchasedDate(self):
        return self._PurchasedDate
    @PurchasedDate.setter
    def PurchasedDate(self,x):
        self._PurchasedDate = x
    
    @property
    def CostBasis(self):
        return self._CostBasis
    @CostBasis.setter
    def CostBasis(self,x):
        self._CostBasis = x
        

class Portfolio:
    def __init__(self):
        self.Cash = 0
        self.Positions = []
        self.ReadHoldings()
    
    def ReadHoldings(self):
        #read latest portfolio
        del self.Positions [:]
        
        f = open(portfolioFile,'rb')
        csvReader = csv.reader(f)
        for row in csvReader:
            if len(row) > 3:
                if(row[0]!='Symbol'): #skip the header line
                    #create object to store position with non-zero units
                    if float(row[1]) != 0:
                        p = Position()
                    
                        p.Symbol = row[0]
                        p.Units = float(row[1])
                        p.PurchasedPx = float(row[2])
                        p.PurchasedDate = row[3]
                        p.CostBasis = float(row[4])
                        
                        if p.Symbol == "CASH-1":  #for cash, keep in cash variable
                            self.Cash = p.Units
                        else:
                            self.Positions.append(p) #for security, add to holdings list
                        
                
                
        f.close()
    

    #Update the changes to the csv file (just like saving data in database)

    def CommitChangesHoldings(self):
        f = open(portfolioFile,"w+")
        f.write("Symbol,Units,PurchasedPx,PurchasedDate,CostBasis\n")
        f.write("CASH-1," + str(self.Cash) + ",1,1/1/9999,0\n")
        for pos in self.Positions:
            f.write(pos.Symbol + "," + str(pos.Units) + "," + str(pos.PurchasedPx) + "," + pos.PurchasedDate + "," + str(pos.CostBasis) +  "\n")
        f.close()
        


        
    #read all orders, update holdings, write back to file
    #Assume given "order" is executed with sufficient cash
    def UpdatePosition(self, order):
        
        #order = new trade
        #holdings = existing positions
        
        #full cost basis is the original cost basis
        #cost basis is the cost basis for new order
        self.ReadHoldings()
        
        #general:
        #long buy: unit > 0, amount < 0, cost basis = 0, exec date = now, purchased date = ""
        #long sell: unit < 0, amount > 0, adj cost basis = (sell units/orig units) * orig. cost basis , exec date = now, purchased date = original long exec date
        #   orig units > 0 & orig cost basis < 0 & cost basis >0
        
        #Short sell: unit < 0, amount < 0, cost basis = 0, exec date = now, purchased date = ""
        #Cover buy: unit > 0, amount > 0, adj cost basis = (buy units/orig units) * orig cost basis, exec date = now, purchased date = original short exec date
        #   orig units < 0 & orig cost basis < 0 & cost basis > 0
        
        
        
        
        #how to calculate the amount, cost basis, unit, and cash
        #long buy: cash = cash + (amount), unit > 0, amount = -1 * unit*current_px, amount < 0
        #Long sell:  cash = cash + (amount), unit <0, amount = -1 * unit*current_px, amount > 0
        
        #Short sell: cash = cash + (amount), unit <0, amount = unit * current_px, amount < 0
        #Cover buy: cash = cash + (amount), unit > 0, amount = unit * current_px, amount > 0
        
        
        
        
        #cost basis is used for P/L 
        #if amount from sell > cost basis from buy, it is profit, else it is loss
        #if amount from cover buy < cost basis from short sell, it is profit, else it is loss
        
        #Unrealized P/L
        #for long, (unit * current price) + cost basis
        #for short, (-1 * unit  * current price) + cost basis
        
        
        IsChanged = False 


        #Long action
        if order.Action == "BUY":
            
            
            #append new traded ordered to current holdings
            p = Position()
            p.Symbol = order.Symbol
            p.Units = order.Units
            p.PurchasedPx = order.ExecPx
            p.PurchasedDate = order.ExecDate
            p.CostBasis = order.Amount
            
            self.Cash = self.Cash + order.Amount
            self.Positions.append(p)
            IsChanged = True #flip the sign to the change


        
        #Long action
        if order.Action == "SELL":
            #for long sell, lot is positive and order.Unit is neative 
            for p in self.Positions:
                if p.PurchasedDate == order.PurchasedDate and p.Symbol == order.Symbol:
                    if p.Units == abs(order.Units): #sell the whole lot
                        p.Units = 0
                        p.CostBasis = 0
                    else:
                        #remain cost basis = (1 - (sold pct)) * original cost basis
                        adj_costBasis = (float(order.Units)/float(p.Units))*float(p.CostBasis) #update cost basis due to partail sell
                        p.Units = p.Units + order.Units #p.Unit is +ve and order.Units is -ve
                        p.CostBasis = p.CostBasis + adj_costBasis
                    #after sell, add cash
                    self.Cash = self.Cash + order.Amount
                    
                    IsChanged = True #flip the sign to the change
                    break #stop the loop for updating lots

                        
        #Short action   
        if order.Action == "SELL_TO_OPEN":
            #for sell, order.Unit is neative
            
            if order.PurchasedDate == "": #it is short sell(original purchased date is zero)
                #short sell just like create a buy position
                
                #negative share with cash deduction
                
                #append new traded ordered to current holdings
                p = Position()
                p.Symbol = order.Symbol
                p.Units = float(order.Units)
                p.PurchasedPx = order.ExecPx
                p.PurchasedDate = order.ExecDate
                p.CostBasis = order.Amount #new order amount => lot cost basis
                
                self.Cash = self.Cash + order.Amount
                self.Positions.append(p)
                IsChanged = True #flip the sign to the change
                
          
          


        #Short action
        if order.Action == "BUY_TO_CLOSE":    
            #for short sell, lot is negative and order.Unit is positive 
            for p in self.Positions:
                if p.PurchasedDate == order.PurchasedDate and p.Symbol == order.Symbol:
                    if abs(p.Units) == order.Units: #sell the whole lot
                        p.Units = 0
                        p.CostBasis = 0
                        
                        
                    else:
                        #remain cost basis = (1 - (sold pct)) * original cost basis
                        adj_costBasis = (float(order.Units)/float(p.Units))*float(p.CostBasis) #update cost basis due to partail cover buy
                        p.Units = p.Units + order.Units #p.Units is -ve and order.Units is +ve
                        p.CostBasis = p.CostBasis + abs(adj_costBasis)
                    #after sell, add cash
                    self.Cash = self.Cash + order.Amount
                    
                    IsChanged = True #flip the sign to the change
                    break #stop the loop for updating lots
 
            
            
        #if there is any change, update    
        if IsChanged == True:
            self.CommitChangesHoldings()
            
        
    #check postion before selling
    #shorting create new position with date, it is different than selling 
    def IsPositionExist(self,order): #sum of the order units
        isExist = False
        for p in self.Positions:
            if p.Symbol == order.Symbol and p.Units == order.Units:
                isExist = True
                break
            
        return isExist
    
    
    def GetPositions(self): #memory only
        return self.Positions
    
    def GetPositionsBySym(self,sym):
        sym_pos = []
        for p in self.Positions:
            if p.Symbol == sym:
                sym_pos.append(p)
        
        if not sym_pos: #is empty list
            
            return []
        else:
            return sym_pos
    
    def GetCash(self): #memory only
        return self.Cash

    def GetRows(self):
        
        return len(self.Positions)





