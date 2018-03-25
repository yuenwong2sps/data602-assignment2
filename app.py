# Assignment 2 template code
# Jamiel Sheikh

# Resources:
# https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
# https://www.w3schools.com/bootstrap/default.asp
# https://www.w3schools.com/bootstrap/bootstrap_buttons.asp


from flask import Flask, render_template, request, url_for
import urllib.request as req
import numpy as np
import pandas as pd
import matplotlib as mp

import clsTrade

from pymongo import MongoClient



app = Flask(__name__)

@app.route("/")
def show_main_page():
    with app.test_request_context():
        print( url_for('show_trade_screen'))
        print( url_for('show_blotter'))
        print( url_for('show_pl'))
        print( url_for('execute_trade'))
        print( url_for('show_testDB_screen'))
        print( url_for('execute_testDB'))

        
        return render_template('main.html')

@app.route("/trade")
def show_trade_screen():
    return render_template('trade.html')

@app.route("/testDB")
def show_testDB_screen():
    return render_template('testDB.html')

@app.route("/blotter")
def show_blotter():
    return render_template('blotter.html')

@app.route("/pl")
def show_pl():
    return render_template('pl.html')

@app.route("/submitTrade",methods=['POST'])
def execute_trade():
    obj_trade = clsTrade.Trade()
    symbol = request.form['symbol']
    quantity = request.form['quantity']
    
    quote = obj_trade.GetQuote(symbol)

    price = quote.Ask * float(quantity)
    
    # pull quote
    # calculate trade value
    # insert into blotter
    # calculate impact to p/l and cash
    return "You traded at " + str(price)

@app.route("/submitEntryToDB",methods=['POST'])
def execute_testDB():
    
    side = request.form['side']
    symbol = request.form['symbol']
    quantity = request.form['quantity']
        
    
    client = MongoClient('localhost', 27017)
    
    db = client['pymongo_test']
    
    posts = db.posts
    post_data = {
        'Action': side,
        'Symbol': symbol,
        'Quantity': quantity
    }
    result = posts.insert_one(post_data)

    return 'One post: {0}'.format(result.inserted_id)
   
    
@app.route("/sample")
def show_sample():
    return render_template('sample.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0') # host='0.0.0.0' needed for docker
