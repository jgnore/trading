from sqlalchemy import create_engine
import mysql.connector


engine_3min = create_engine('mysql+pymysql://root:whdrud12@127.0.0.1:3306/3min_data', encoding='utf-8')
connection_3min = engine_3min.connect()

engine_5min = create_engine('mysql+pymysql://root:whdrud12@127.0.0.1:3306/5min_data', encoding='utf-8')
connection_5min = engine_5min.connect()

connection = mysql.connector.connect(user="root", password="whdrud12", host="127.0.0.1", charset="utf8mb4")
cur = connection.cursor()

cur.execute("SHOW DATABASES LIKE'all_data'")
result = cur.fetchall()

"""CREATE 또는 DROP 등을 사용할 때에는 백틱(`) SHOW~의 경우는 작은따옴표(')"""
def check_db(db_name):
    cur.execute("SHOW DATABASES LIKE '"+ db_name + "'")
    result = cur.fetchall()
    print("done")
    if len(result)== 0:
        cur.execute("CREATE DATABASE `"+ db_name + "`")
        print("[DB 관리]", db_name, "DB를 생성합니다.")
    else:
        print("[DB 관리]", db_name, "DB가 이미 존재합니다.")

def check_table(db_name, table_name):
    check_db(db_name)

    connect = mysql.connector.connect(user='root', password="whdrud12", host="127.0.0.1", db=db_name, charset="utf8mb4")
    cur = connect.cursor()

    cur.execute("SHOW TABLES LIKE '" + table_name + "'")
    result = cur.fetchall()

    if len(result) == 0:
        print("[DB 관리] ", table_name, "table을 생성합니다.")
        cur.execute("CREATE TABLE `" + db_name + "`.`" + table_name + "` (`code` VARCHAR (100), `sv_day` VARCHAR(100))")
        print("[DB 관리] ", table_name, "table이 생성되었습니다.")
    else:
        print("[DB 관리] ", table_name, "table이 이미 존재합니다.")

    connect.commit()
    cur.close()

def insert_into(db_name, table_name, columns_name, data):
    connect = mysql.connector.connect(user='root', password="whdrud12", host="127.0.0.1", charset="utf8mb4")
    cur = connect.cursor()

    send_message = "INSERT INTO `" + db_name + "`.`" + table_name + "` (" + columns_name + ") VALUES ('" + data + "');"
    cur.execute(send_message)
    connect.commit()
if __name__ == "__main__":
    check_db('item_savepoint')
