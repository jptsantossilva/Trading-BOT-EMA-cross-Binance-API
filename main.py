import  requests 
import numpy as np 
import talib #talib library for various calculation related to financial and technical indicators
from binance.client  import Client  #importing client 
import os

# get binance api key and secret from os environment variables
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']

client = Client(api_key, api_secret)


SYMBOL = "BTCUSDT"  
TIME_PERIOD= "15m" #taking 15 minute time period 
LIMIT = "200" # taking 200 candles as limit 
QNTY = 0.006 # we will define quantity over here 

def place_order(order_type):
    # buy or sell order type 
    if(order_type == "buy"):
        # we will place buy order
        order = client.create_order(symbol=SYMBOL, side="buy",quantity=QNTY,type="MARKET") # market order buy type 
    else:
        order = client.create_order(symbol=SYMBOL, side="sell", quantity=QNTY,type="MARKET") # market order sell type 

    print("order placed successfully!") 
    print(order)
    return

#function to get data from binance 
def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol={}&interval={}&limit={}".format(SYMBOL, TIME_PERIOD, LIMIT)
    res = requests.get(url) 
    #now we can either save the response or convert it to numpy array , converting is more reasonable 
    return_data = []
    for each in res.json():
        return_data.append(float(each[4]))
    return np.array(return_data)

#define main entry point for the script 
def main():
    buy = False #it means we are yet to buy and have not bought
    sell = True #we have not sold , but if you want to buy first then set it to True
    ema_fast = None #starting with None 
    ema_slow = None #starting with None 

    #we also need to store the last variables that was the value for the ema_8 and ema_21, so we can compare
    last_ema_fast = None 
    last_ema_slow = None 

    print("started..")
    #the script will run continously and fetch latest data from binance 
    while True:
        
        closing_data = get_data() #get latest closing data for the candles 
        
        #now feed the data to the Ema function of talib
        # i am using ema crossover strategy, in which i am using timeframe 8 AND 34
        # 8 for FAST ema line and 34 for SLOWER 
        ema_fast = talib.EMA(closing_data,8)[-1] #data and timeperiod are the two parameters that the function takes 
        ema_slow = talib.EMA(closing_data, 34)[-1] #same as the last one 
     
        #print("ema_8", ema_8[-1])
        #print("ema_34",ema_21[-1])

        #now , the last thing we need to do is get the order going. we will create function to place 
        #order

        #logic for buy and sell 
        # also one thing
        if(ema_fast > ema_slow and last_ema_fast): #we have to check if the value of ema_8 crossed ema_21 or not 
            if(last_ema_fast < last_ema_slow and not buy): # to check if previously, it was below of ema_21 and we haven't already bought it 
                print("buy logic goes here")
                buy = True 
                sell = False #switch the values for next order

        if(ema_slow > ema_fast and last_ema_slow):  #to check if ema_8 got down from top to bottom 
            if(last_ema_slow < last_ema_fast and not sell): # to check if previously it was above ema_21
                print("sell logic goes here")
                sell = True 
                buy = False #switching values for next order 

        #at last we are setting the current values as last one 
        last_ema_8 = ema_fast
        last_ema_21 = ema_slow
        #return
        
if __name__ == "__main__":
    main()

