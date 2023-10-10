"""algorithm_1.py"""
import pandas as pd
import manage_db
import os
import sys
from AutoTrading.valuable import _df
class algo1:

    def __init__(self, min5_data, start_date, item_code):
        self.df = _df.algo1_df()
        self.min5_data = min5_data
        self.start_date = start_date
        self.item_code = item_code

        # self.min5_data['date'] = pd.to_datetime(self.min5_data['time'].str.slice(start=0, stop=8), format='%Y%m%d')
        self.min5_data = self.min5_data.sort_values(by='time', ascending=True).reset_index(drop=True)
        self.min5_data['date'] = self.min5_data['time'].str.slice(start=0, stop=8)
        data_of_start_date = self.min5_data[self.min5_data['date'] == self.start_date].reset_index(drop=True)
        self.start_price = int(data_of_start_date.loc[0,'open'])
        self.temp_min5_data = self.min5_data[self.min5_data['date']>=self.start_date]
        start_date_data = self.min5_data[self.min5_data['date'] == self.start_date]
        self.standard_high = max(start_date_data['high'])

    def run(self):
        self.highest_price = self.start_price
        self.lowest_price = 0
        self.pos_buy = False
        idx_of_df = len(self.df['item_code'])

        for data in self.temp_min5_data.itertuples():
            high = int(data.high)
            low = int(data.low)
            self.pos_buy = False

            if high > self.highest_price:
                print(f"고가가 갱신되었습니다.{data.date},{data.time}")
                self.highest_price = high ## 고가 데이터 재입력
                self.buy_price = (self.start_price + self.highest_price)/2
                self.df.loc[idx_of_df, 'first_buy_price'] = self.buy_price
                self.df.loc[idx_of_df, 'item_code'] = self.item_code
                self.lowest_price = high

                if high == self.standard_high:
                    self.pos_buy = True

            if low <= self.lowest_price:
                print(f"저가가 갱신되었습니다... {data.date}, {data.time}")
                self.lowest_price = low

                if self.pos_buy:
                    print(f"매수 예정 가격에 닿았습니다... [{data.time}] {low}/{self.buy_price}")
                    return False, '0'

        return True, self.df


        """20230704까지밖에 안나옴;;"""
if __name__ == "__main__":
    item_code = "005930"
    start_date = "20221004"
    min5_data = pd.read_sql(f"SELECT * FROM s{item_code}", manage_db.engine_5min)
    result = algo1(min5_data, start_date, item_code).run()
    print(result[0])
    print(result[1])