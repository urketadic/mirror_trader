
from binance.client import Client
from binance.enums import *
from datetime import date, datetime
import json
import time
#import ccxt # for the OCO orders
from modules.helper import *

# global variables (seen by the binance.py too)
clientOrders = {}
ocoOrders = { }
copy_clients = []
lvrgPrcnt = 1
mainBalance = 1.0

__DIR__ = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, __DIR__)
sys.path.insert(0, __DIR__ + '/../')


# ------ HELPER FUNCTIONS --------------
def get_clients():
    return copy_clients
    
'''
	This function initializes the 'copy-clients' according to their
	balance-ratio to the main-account. That's the only argument for this function
'''
def init_copy_clients( MainBalance ):
	global copy_clients
     
	f = open(__DIR__ + '/copy_clients.txt', 'r')
	creds = f.read().split('\n')
	f.close()
	#registerTelegramCommands()
	for cr in creds:
		if len(cr)<2 or cr.startswith('#'):
			continue
		key_secret = cr.split('   ')
		print("Client Initiliazed: " +str(key_secret) )
		binance_api_key = key_secret[0]
		binance_api_secret = key_secret[1]
		accName = key_secret[2]
		try:
			newClient = Client(binance_api_key, binance_api_secret)
			#newClient.ccxtClient = ccxt.binance({ 'apiKey': binance_api_key, 'secret': binance_api_secret,'enableRateLimit': True})
					
			thisBalance = float(newClient.get_asset_balance(asset='BTC')['free'])
			copy_clients.append( newClient )
			copy_clients[-1]._id = key_secret[0]
			
			thisBalance = 0.2 # thisBalance['free']
			copy_clients[-1].BlncRate = float(thisBalance)/MainBalance
			copy_clients[-1].accName = accName
			copy_clients[-1].active = True
			print('Client-to-main ratio balance: '+ str(copy_clients[-1].BlncRate))
			clientOrders[key_secret[0]] = {}
			ocoOrders[key_secret[0]] = {}
		except Exception as ex:
			print('Client Initialization failed: '+ str(ex) )
     


def copy_order( client, message, count):
	
	orderData = message
	notUpd = True
	try:
		if (orderData['o']=='TAKE_PROFIT_LIMIT' or orderData['o']=='STOP_LOSS_LIMIT') and orderData['X']=='NEW' and orderData['g']!=-1:
			ocoOrders[client._id][orderData['g']] = orderData
			notUpd = False

		if orderData['o']=='MARKET' and orderData['X']=='NEW':
			symb = orderData['s']
			ordSide = orderData['S']
			
			if ordSide=='BUY':  
			 mainusdt = float(orderData['Q'])
			 f = open(__DIR__ + '/copy_clients.txt', 'r')
			 CREDENTIALS = f.read().split('\n')
			 CREDENTIALS = CREDENTIALS[0].split('   ')
			 uno = Client(CREDENTIALS[0], CREDENTIALS[1])
			 clientusdt = float(uno.get_asset_balance(asset='USDT')['free'])
			 
			 client.BlncRate=float((clientusdt)/(mainusdt))
			 print('newblncrate'+ str(client.BlncRate))
			else:
			 mainlink = float(orderData['q'])
			 f = open(__DIR__ + '/copy_clients.txt', 'r')
			 CREDENTIALS = f.read().split('\n')
			 CREDENTIALS = CREDENTIALS[0].split('   ')
			 uno = Client(CREDENTIALS[0], CREDENTIALS[1])
			 clientlink = float(uno.get_asset_balance(asset='LINK')['free'])
			 
			 client.BlncRate=float((clientlink)/(mainlink))
			 print('newblncrate'+ str(client.BlncRate))			 
			tIFrc = orderData['f']
			def truncate(n, decimals=0):
			 multiplier = 10 ** decimals
			 return int(n * multiplier) / multiplier
			ordQty = truncate(float(orderData['q'])*client.BlncRate,1)
			print('ordqty'+ str(ordQty))
			upd = client.create_order( symbol=symb , side=ordSide, type=ORDER_TYPE_MARKET, quantity=ordQty)
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT:: Placed a New MARKET-Order, Price: ' + str(orderData['p']) + \
									' Quantity: ' + str(orderData['q']) + ' for the '+ orderData['s'] + ' pair\n\n'			
			clientMsg = client.accName+':: Placed a New MARKET-Order'  + \
							' Quantity: ' + str(upd['origQty']) + ' for the '+ upd['symbol'] + ' pair'
			console_message(clientMsg, "binance")
			bMessage = bMessage + clientMsg

	except Exception as ex:
			console_message(client.accName+' ' +str(ex), "binance")



def cancel_order( client, message):

	orderData = message
	try:	
		if client._id in clientOrders.keys():
			console_message(client.accName+":: Cancelling OrderID: " + str(clientOrders[client._id][orderData['i']]), "binance")
	except Exception as ex:
			console_message(client.accName+' ' +str(ex), "binance")
	try:
		ordId = clientOrders[client._id][orderData['i']]
		client.cancel_order( symbol=orderData['s'], orderId=ordId)
	except Exception as ex:
			console_message(client.accName+' ' +str(ex), "binance")
