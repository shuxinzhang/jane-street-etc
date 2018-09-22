        print(read_from_exchange)
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
    print("Buying an order")
    write_to_exchange(exchange, {"type":"add","order_id":int(timeid),"symbol":symbol,"dir":"BUY","price":price,"size":size})
    buy_res = read_from_exchange(exchange)
    if buy_res['type']=="ack":
        print("buy order acknowledged.")
    #bond_amount = bond_amount + size
    time.sleep(1)
    return buy_res

def sell(exchange, symbol, price, size):
    timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
    print("Selling")
    write_to_exchange(exchange, {"type":"add","order_id":int(timeid),"symbol":symbol,"dir":"SELL","price":price,"size":size})
    sell_res = read_from_exchange(exchange)
    if sell_res['type']=="ack":
        print("sell order acknowledged.")
    #bond_amount = bond_amount - size
    time.sleep(1)
    return sell_res

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    current_bond = 0
    buy_price = 1000
    sell_price = 1001
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    while(True):
        buy_reply = buy(exchange,"BOND",buy_price,10)
    if (buy_reply['type']=='ack'):
        current_bond = current_bond+10
        sell_reply = sell(exchange,"BOND",sell_price,10)
        if (sell_reply['type']=='ack'):
                current_bond = current_bond-10
    print('current bond=' + str(current_bond))
    if current_bond <= -50:
        buy_price = buy_price + 2
        sell_price = sell_price + 2
    if current_bond >= 50:
        buy_price =  buy_price - 2
        sell_price = sell_price - 2 
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    

if __name__ == "__main__":
    main()
