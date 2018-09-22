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
test_exchange_index=1
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
                dl.add([all_trades[i][0],remaining_amount])
                remaining_amount = 0
            else:
                total_price = total_price + all_trades[i][0] * all_trades[i][1]
                total_amount = total_amount + all_trades[i][1]
                dl.add(all_trades[i])
                remaining_amount = remaining_amount - all_trades[i][1]
            i=i+1
        if (remaining_amount > 0):
            return (0, None)
        else:
            return (total_price * 1.0/total_amount, dl)

def get_highest_bid_for(feed,symbol,amount,direction):
    dm = []
    if (feed['type']=='book'):
 #       print(feed)
        total_price = 0
        total_amount = 0
        if (feed['symbol']==symbol):          
            all_trades = feed[direction]
            all_trades.sort(reverse=True,key=lambda offer:offer[0])
        i = 0
        remaining_amount = amount
        while remaining_amount > 0 and i < len(all_trades):
            temp = amount - all_trades[i][1]
            if (temp < 0):
                total_price = total_price + all_trades[i][0] * remaining_amount
                total_amount = total_amount + remaining_amount
                dm.add([all_trades[i][0],remaining_amount])
                remaining_amount = 0
            else:
                total_price = total_price + all_trades[i][0] * all_trades[i][1]
                total_amount = total_amount + all_trades[i][1]
                dm.add(all_trades[i])
                remaining_amount = remaining_amount - all_trades[i][1]
            i=i+1
        if (remaining_amount > 0):
            return (0,None)
        else:
            return (total_price * 1.0/total_amount,dm)

def price_for_a_unit_for_4(feed):
    stock_list = {'BOND':3,"AAPL":2,"MSFT":3,"GOOG":2}
    for name,amount in stock_list.items():
        if (get_highest_bid_for(feed,name,amount,"BUY")!=None):
            stock_amt[name]['bid']=get_highest_bid_for(feed,name,amount,"BUY")
        if (get_lowest_offer_for(feed,name,amount,"SELL")!=None):
            stock_amt[name]['offer']=get_lowest_offer_for(feed,name,amount,"SELL")


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
    while(True):
        feed = read_from_exchange(exchange)
        print(feed)
        print(str(price_for_a_unit_for_4(feed)))
#        feed = json.loads(feed)
     #    bz_buy_max = get_max(feed,'BABZ',"buy")
     #    bz_sell_min = get_min(feed,'BABZ',"sell")
     #    ba_buy_max = get_max(feed,'BABA',"buy")
     #    ba_sell_min = get_min(feed,'BABA',"sell")
     #    if (bz_buy_max != 0):
     #        babz_buy_max = bz_buy_max
     #    if (bz_sell_min != 10000000000):
     #        babz_sell_min = bz_sell_min
     #    if (ba_buy_max != 0):
     #        baba_buy_max = ba_buy_max
     #    if (ba_sell_min != 10000000000):
     #        baba_sell_min = ba_sell_min
	    # print('zb,zs,ab,as',babz_buy_max,babz_sell_min,baba_buy_max,baba_sell_min)
     #    if (babz_buy_max > baba_sell_min + 12):
     #        buy(exchange,"BABA",baba_sell_min+1,1)
     #        timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
     #        write_to_exchange(exchange, {"type": "convert", "order_id":int(timeid),"symbol":"BABA","dir":"SELL","size":1})
     #        print("Conversion:"+str(read_from_exchange(exchange)))
     #        sell(exchange,"BABZ",babz_buy_max-1,1)
     #    if (baba_buy_max > babz_sell_min + 12):
     #        buy(exchange,"BABZ",babz_sell_min+1,1)
     #        timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
     #        write_to_exchange(exchange, {"type": "convert", "order_id":int(timeid),"symbol":"BABA","dir":"BUY","size":1})
     #        print("Conversion:"+str(read_from_exchange(exchange)))
     #        sell(exchange,"BABA",baba_buy_max-1,1)

if __name__ == "__main__":
    main()
