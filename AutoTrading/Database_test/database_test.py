import pandas as pd

# 예제 데이터프레임 생성
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['New York', 'San Francisco', 'Los Angeles']}

df = pd.DataFrame(data)

# 데이터프레임을 itertuples()를 사용하여 반복
for row in df.itertuples():
    print(row.Index, row.Name, row.Age, row.City)
