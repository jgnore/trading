"""algorithm_1.py"""
import pandas as pd
import manage_db
class algo1:
    def __init__(self, min5_data, start_date):
        self.min5_data = min5_data
        self.start_date = start_date
        self.min5_data['date'] = self.min5_data['time'].str.slice(start=0, stop=8)
        print(self.min5_data)

        data_of_start_date = self.min5_data[self.min5_data['date'] == self.start_date]
        print(data_of_start_date)

        self.start_price = int(data_of_start_date.loc[0,'open'])
        print(self.start_price)

    # def run(self):
    #     self.highest_price = self.start_price
    #
    #     for data in self.min5_data.itertuples():
    #         high = int(data.high)
    #
    #         if high > self.highest_price:
    #             print("고가가 갱신되었습니다.")
    #             self.highest_price = high
    #             self.buy_price = (self.start_price + self.highest_price)/2
    #
    #     print(self.buy_price)


if __name__ == "__main__":
    item_code = "005930"
    start_date = "20221017"
    min5_data = pd.read_sql(f"SELECT*FROM s{item_code}",manage_db.engine_5min).sort_values(by='time').reset_index(drop=True)
    algo1(min5_data, start_date).run()