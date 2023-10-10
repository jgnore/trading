import pandas as pd

def setrealreg():
    data = {'item_code':[]}
    data = pd.DataFrame(data, columns=['item_code'])
    return data

def algo1_df():
    data = {'item_code':[], 'first_buy_price':[], 'second_buy_price':[]}
    data = pd.DataFrame(data, columns = ['item_code', 'first_buy_price','second_buy_price'])
    return data