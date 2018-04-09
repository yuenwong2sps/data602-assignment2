# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 23:12:33 2018

@author: johnw
"""
from pymongo import MongoClient


class DB:
    def __init__(self,dbName):
        self._dbName = dbName
        self._client = MongoClient('localhost', 27017)
        self._db = self._client[self._dbName]
        
    def insert(self,dbTableName,postData):
        dbTable = self._db[dbTableName]    
        result = dbTable.insert_one(postData)
        return result

    def read(self,dbTableName,criteria = None):
        dbTable = self._db[dbTableName]        
        if criteria is None:
            _items = dbTable.find({})
            items = [item for item in _items]
            return items
        else:
            _items = dbTable.find(criteria)
            items = [item for item in _items]
            return items

        
    def delete(self,dbTableName,criteria = None):
        dbTable = self._db[dbTableName]
        if criteria is None:
            dbTable.delete_many({})
        else:
            dbTable.delete_many(criteria)

    #if return True, some kind of insert statement occurred
    #if return False, no insert statement occurred or table is created
    def isDBInit(self):
        client = MongoClient('localhost', 27017)
        if( self._dbName in client.database_names()):
            return True
        else:
            return False
    

#def testDB():
    #databaseName = "CyptoTrading"

    #db =  DB(databaseName)
    
    
    #if not db.isDBInit(databaseName):
    #    print("should init db")
        
    #else:
    #    print("ok to read")
    
    #post_data = {
    #        "Symbol":	"AAPL",
    #        "Units":	400,
    #        "PurchasedPx":  155,
    #        "PurchasedDate":	"1/1/2018",
    #        "CostBasis":	21000
                                                                        
    #        }
    
    
    #result = db.delete('portfolio')
    #print(result)
    
    #result = db.insert('portfolio',post_data)
    #print(result)
    
    #criteria = {"Units":400}

   
#testDB()    