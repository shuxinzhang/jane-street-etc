import sys
import socket
import json
import time
import util

# returns the exchange instance of trading
def main():
	print("bot started")
	exchange = util.connect()
	hello_response = util.hello(exchange)
	print('hello from exchange ' + hello_response)
	while(True):
		""" Customized strategy here
		buy = util.buy(...)
		sell = util.sell(...)
		Customed strategy ends"""
if __name__ == "__main__":
	main()
