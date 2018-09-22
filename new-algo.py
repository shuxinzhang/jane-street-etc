#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import datetime
import time
# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="xiaokeai"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"
port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('hostname='+exchange_hostname)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def buy(exchange, symbol, price, size):
    timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
    print("buy order for", symbol, "under price", price, "and size", size)
    write_to_exchange(exchange, {"type":"add","order_id":int(timeid),"symbol":symbol,"dir":"BUY","price":price,"size":size})
    buy_res = read_from_exchange(exchange)
    if buy_res['type']=="ack":
        print("buy order for", symbol, "under price", price, "and size", size, " acknowledged.")
	#bond_amount = bond_amount + size
    time.sleep(1)
    return buy_res

def sell(exchange, symbol, price, size):
    timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
    print("sell order for", symbol, "under price", price, "and size", size)
    write_to_exchange(exchange, {"type":"add","order_id":int(timeid),"symbol":symbol,"dir":"SELL","price":price,"size":size})
    sell_res = read_from_exchange(exchange)
    if sell_res['type']=="ack":
        print("sell order acknowledged.")
	#bond_amount = bond_amount - size
    time.sleep(1)
    return sell_res

# ~~~~~============== MAIN LOOP ==============~~~~~
def get_running_avg(feed,symbol,direction):
    runnig_avg = 0
    if (feed['type']=='book'):
        if (feed['symbol']==symbol):
            amt_sum = 0
            total = 0
            for trade in feed[direction]:
                amt_sum = trade[1] + amt_sum
                total = total + trade[1] * trade[0]
	    if amt_sum == 0:
		  return 0
	    runnig_avg = total * 1.0/amt_sum
    return 

def get_max(feed,symbol,direction):
    maxV = 0
    if (feed['type']=='book'):
#        print(feed)
        if (feed['symbol']==symbol):
            
            for trade in feed[direction]:
                if trade[0] > maxV:
                    maxV = trade[0]
    return maxV

def get_min(feed,symbol,direction):
    minV = 10000000000
    if (feed['type']=='book'):
 #       print(feed)
        if (feed['symbol']==symbol):          
            for trade in feed[direction]:
                if trade[0] < minV:
                    minV = trade[0]
    return minV

def get_lowest_offer_for(feed,symbol,amount,direction):
    dl = []
    if (feed['type']=='book'):
 #       print(feed)
        total_price = 0
        total_amount = 0
        if (feed['symbol']==symbol):          
            all_trades = feed[direction]
            all_trades.sort(key=lambda offer:offer[0])
            i = 0
            remaining_amount = amount
            while remaining_amount > 0 and i < len(all_trades):
                temp = amount - all_trades[i][1]
                if (temp < 0):
                    total_price = total_price + all_trades[i][0] * remaining_amount
                    total_amount = total_amount + remaining_amount
                    dl.append([all_trades[i][0],remaining_amount])
                    remaining_amount = 0
                else:
                    total_price = total_price + all_trades[i][0] * all_trades[i][1]
                    total_amount = total_amount + all_trades[i][1]
                    dl.append(all_trades[i])
                    remaining_amount = remaining_amount - all_trades[i][1]
                i=i+1
            if (remaining_amount > 0):
                return None
            else:
                return (total_price * 1.0/total_amount, dl)

def get_highest_bid_for(feed,symbol,amount,direction):
    dm = []
    if (feed['type']=='book'):
 #       print(feed)
        total_price = 0
        total_amount = 0
        if (feed['symbol']==symbol):  
            if (symbol == "XLK"):
                print("XLK PROCESSING!")        
            all_trades = feed[direction]
            all_trades.sort(reverse=True,key=lambda offer:offer[0])
            i = 0
            remaining_amount = amount
            while remaining_amount > 0 and i < len(all_trades):
                temp = amount - all_trades[i][1]
                print("REMAINING="+str(remaining_amount))
                if (temp < 0):
                    total_price = total_price + all_trades[i][0] * remaining_amount
                    total_amount = total_amount + remaining_amount
                    dm.append([all_trades[i][0],remaining_amount])
                    remaining_amount = 0
                else:
                    total_price = total_price + all_trades[i][0] * all_trades[i][1]
                    total_amount = total_amount + all_trades[i][1]
                    dm.append(all_trades[i])
                    remaining_amount = remaining_amount - all_trades[i][1]
                i=i+1
            if (remaining_amount > 0):
                return None
            else:
                return (total_price * 1.0/total_amount,dm)

def price_for_a_unit_for_4(feed):
    stock_list = {'BOND':3,"AAPL":2,"MSFT":3,"GOOG":2}
    bid_dict = {}
    offer_dict = {}
    for name,amount in stock_list.items():
        if (get_highest_bid_for(feed,name,amount,"buy")!=None):
            bid_dict[name]=get_highest_bid_for(feed,name,amount,"buy")
        if (get_lowest_offer_for(feed,name,amount,"sell")!=None):
            offer_dict[name]=get_lowest_offer_for(feed,name,amount,"sell")


def main():
    current_bond = 0
    buy_price = 1000
    sell_price = 1001
    exchange = connect()
    babz_buy_max = 0
    babz_sell_min = 0
    baba_buy_max = 0
    baba_sell_min = 0
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    bid_dict = {}
    offer_dict = {}
    stock_list = {'BOND':3,"AAPL":2,"MSFT":3,"GOOG":2}
    xlk_dict = {}
    i = 0 
    while(True):
        feed = read_from_exchange(exchange)
        print(feed)
        for name,amount in stock_list.items():
            if (get_highest_bid_for(feed,name,amount,"buy")!=None):
                bid_dict[name]=get_highest_bid_for(feed,name,amount,"buy")
            if (get_lowest_offer_for(feed,name,amount,"sell")!=None):
                offer_dict[name]=get_lowest_offer_for(feed,name,amount,"sell")
        
        if (get_highest_bid_for(feed,"XLK",10,"buy")!=None):
            xlk_dict['bid']=get_highest_bid_for(feed,"XLK",10,"buy")
        if (get_lowest_offer_for(feed,"XLK",10,"sell")!=None):
            xlk_dict['offer']=get_lowest_offer_for(feed,"XLK",10,"sell")
        print("dictionaries = ", str(bid_dict),str(offer_dict),str(xlk_dict))
        i = i + 1;
        if (i > 0):
            dm = bid_dict
            dl = offer_dict
            dm_total = 0
            dl_total = 0
            for name,amount in stock_list.items():
                if dm[name]!=None:
                    dm_total = dm_total + amount * dm[name][0]
                if dl[name]!=None:
                    dl_total = dl_total + amount * dl[name][0]
            if (dm_total > 10*xlk_dict['offer'][0]):
                for offer in xlk_dict['offer'][1]:
                    buy(exchange,"XLK",offer[0],offer[1])

                write_to_exchange(exchange, {"type": "convert", "order_id":int(timeid),"symbol":"XLK","dir":"SELL","size":10})
                print("Conversion:"+str(read_from_exchange(exchange)))
                for name, bids in dm.items:
                    for bid in bids[1]:
                        sell(exchange,name,bid[0],bid[1])
            if (dl_total < 10*xlk_dict['bid'][0]):
                for name, bids in dm.items:
                    for bid in bids[1]:
                        buy(exchange,name,bid[0],bid[1]) 
                write_to_exchange(exchange, {"type": "convert", "order_id":int(timeid),"symbol":"XLK","dir":"BUY","size":10})
                print("Conversion:"+str(read_from_exchange(exchange)))  
                for offer in xlk_dict['offer'][1]:
                    sell(exchange,"XLK",offer[0],offer[1])       


if __name__ == "__main__":
    main()
