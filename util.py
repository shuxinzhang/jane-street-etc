import sys
import socket
import json
import time

# returns the exchange instance of trading
def connect(socket_name = "production", socket_port = 25000):
	so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s = so.connect((socket_name,socket_port))
	return s.makefile('rw',1)

def write(exchange, obj_to_write):
	json.dump(obj,exchange)
	exchange.write("\n")

def read(exchange):
	return json.loads(exchange.readline())

def hello(exchange):
	write(exchange,{"type":"hello","team":"XiaoKeAi"})
	res = read(exchange)
	print('hello from exchange replied', res)
	return res

def buy(exchange, symbol, price, size):
	timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
	write(exchange, {"type":"add","order_id":int(timeid),"symbol":symbol,"dir":"BUY","price":price,"size":size})
	sleep(1)
	return read(exchange)

def sell(exchange, symbol, price, size):
	timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
	write(exchange, {"type":"add","order_id":int(timeid),"symbol":symbol,"dir":"SELL","price":price,"size":size})
	sleep(1)
	return read(exchange)


