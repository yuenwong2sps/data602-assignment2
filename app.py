# Assignment 2 template code
# Jamiel Sheikh

# Resources:
# https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
# https://www.w3schools.com/bootstrap/default.asp
# https://www.w3schools.com/bootstrap/bootstrap_buttons.asp


from flask import Flask, render_template, request, url_for

from flask_socketio import SocketIO, emit, send
import datetime


#import time
#import json
#import threading
#import urllib.request as req
#import numpy as np
#import pandas as pd
#import matplotlib as mp
#from pymongo import MongoClient


#unofficial gdax websocket package, it could be found in folder gdax
import gdax.websocket_client2

#models code that support the views and controls
import clsModels


#flask and socket init code
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

update_time = datetime.datetime.now

#web socket client for gdax price
wsClient = gdax.websocket_client2.MyWebsocketClient() 

#start wsClient and get feed
def init_feed():
    print("Start websocket feed")
    wsClient.start()
 

@app.route("/")
def show_main_page():
    init_feed()
    with app.test_request_context():
        
        
        
        #show main page at the beginning
        return render_template('main.html')



####Trade Controllers ####
@app.route("/trade")
def show_trade_screen():
    tradeModel = clsModels.TradeModel()
    
    CashEntry = tradeModel.CashEntry
    AggEntries = tradeModel.AggEntries
    
    
          
    return render_template('trade.html', Entries = AggEntries, CashEntry = CashEntry)

@app.route("/submitTrade",methods=['POST'])
def execute_trade():
   
    tradeModel = clsModels.TradeModel()
    
    symbol = request.form['symbol']
    quantity = request.form['quantity']
    side = request.form['side']
    
   
    
    trade_message_to_user = ""
    
    if quantity.isdigit():
    
        #get price at server session instead of model to ensure it keeps running instead of be killed after each request
        sym_price = wsClient.GetQuote(symbol)
        print(symbol + " " + str(quantity) + " " + str(sym_price)) 
        if side == 'b':
            trade_message_to_user = tradeModel.TradeBuy(symbol, float(quantity), float(sym_price))
        else:
            trade_message_to_user = tradeModel.TradeSell(symbol, float(quantity), float(sym_price ))

    else:
        #not trade and show warning message
        trade_message_to_user = "Quantity has to be digit"
    
    CashEntry = tradeModel.CashEntry
    AggEntries = tradeModel.AggEntries
    
    
          
    return render_template('trade.html', Entries = AggEntries, CashEntry = CashEntry, MessageToUser = trade_message_to_user)


    



#####Blotter Controllers ####
@app.route("/blotter")
def show_blotter():
    blotterModel = clsModels.BlotterModel()
    blotterEntries = blotterModel.Entries
    
    return render_template('blotter.html', Entries = blotterEntries)



#####P/L Controllers ####
@app.route("/pl")
def show_pl():
    
    #generate px list with websocket for PL calculation
    symbolList = ["ETH-USD","BTC-USD","LTC-USD","BCH-USD"]
    dictPx = {}
    
    
    for s in symbolList:
        dictPx[s] = wsClient.GetQuote(s)
    
    dictPx["CASH-1"] = 1
    
    
    
    plmodel = clsModels.PLModel(dictPx)
    plEntries = plmodel.Entries
    return render_template('pl.html', Entries = plEntries)


#hidden control to kill the websocket client
@app.route("/killFeed")
def show_killFeed():
    wsClient.close()
    return render_template('main.html')



   
#socket message will show up when it is connected with client
    
@socketio.on('client_connected')                          # Decorator to catch an event called "my event":
def test_message(message):                        # test_message() is the event callback function.
    hit_time = str(datetime.datetime.now())
    print(message)
    emit('my_response', {'data': hit_time })      # Trigger a new event called "my response" 
                                                  # that can be caught by another callback later in the program.
           
     



if __name__ == "__main__":
    #app.run(host='0.0.0.0') # host='0.0.0.0' needed for docker
    socketio.run(app, host='0.0.0.0') 

    