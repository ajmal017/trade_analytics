# -*- coding: utf-8 -*-
"""
Created on Sat May 20 18:58:59 2017

@author: c0redumb
"""

import yqd

def load_quote(ticker):
	print('===', ticker, '===')
	print(yqd.load_yahoo_quote(ticker, '20160101', '20171201'))
	print(yqd.load_yahoo_quote(ticker, '20170515', '20170517', 'dividend'))
	print(yqd.load_yahoo_quote(ticker, '20170515', '20170517', 'split'))

def test():
	# Download quote for stocks
	load_quote('QCOM')
	load_quote('C')

	# Download quote for index
	load_quote('^DJI')

if __name__ == '__main__':
	test()