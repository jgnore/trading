import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pandas as pd
import time
import manage_db
from threading import Thread
import valuable._df as _df
import valuable.dummy_variable as dv
import datetime

from Algorithm import algorithm_2



form_class = uic.loadUiType("main.ui")[0]

temp_date = datetime.datetime.now()
latest_date = temp_date

while latest_date.weekday() > 4:
    latest_date = latest_date - datetime.timedelta(days=1)

now_time = time.strftime("%H%M")
print(now_time)
if now_time <= "1530":
    latest_date = latest_date - datetime.timedelta(days=1)
else:
    pass


latest_date = latest_date.strftime("%Y%m%d")
date = temp_date.strftime("%Y%m%d")

print(f"오늘 날짜는 {date}입니다.. 최신 거래일은 {latest_date}입니다.")
class tradesystem(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  ## GUI 켜기
        self.setWindowTitle("주식 프로그램")  ## 프로그램 화면 이름 설정
        self.condition_list = {'index':[], 'name':[]}

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")  ## OpenAPI 시작
        self.kiwoom.dynamicCall("CommConnect()")  ## 로그인 요청

        self.setrealreg = _df.setrealreg()
        print(self.setrealreg)

        """데이터 요청 구간"""
        self.pushButton.clicked.connect(self.request_opt10016)
        self.pushButton_2.clicked.connect(self.request_opt10080)
        self.pushButton_3.clicked.connect(self._pushbtn_3)
        self.pushButton_4.clicked.connect(self._pushbtn_4)
        self.pushButton_5.clicked.connect(self.__getconditionload)
        self.pushButton_6.clicked.connect(self._pushbtn_6)
        self.pushButton_7.clicked.connect(self._pushbtn_7)


        """이벤트 처리 구간"""
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)  ## 데이터 조회 요청 처리 함수
        self.kiwoom.OnEventConnect.connect(self.process_login)  ## 로그인 반환값 처리 함수
        self.kiwoom.OnReceiveRealData.connect(self.receive_realdata)    ##실시간 데이터 수신 처리 함수
        self.kiwoom.OnReceiveConditionVer.connect(self.OnReceiveConditionVer)
        self.kiwoom.OnReceiveTrCondition.connect(self.OnReceiveTrCondition)
        #self.kiwoom.OnReceiveRealCondition.connect(self.OnReceiveRealCondition)
        self.kiwoom.OnReceiveChejanData.connect(self.receive_chejandata)


    """자동 매매 구간"""

    def _auto_trade(self):
        while 1:
            now_time = QTime.currentTime().toString('hh:mm:ss')
            print(f"[{now_time}] 정상 동작 중입니다.")
            time.sleep(60)

    """로그인 처리 구간"""

    def process_login(self):
        account_cnt = self.__getlogininfo("ACCOUNT_CNT")
        accno = self.__getlogininfo("ACCNO")
        key_b = self.__getlogininfo("KEY_BSECGB")
        firew = self.__getlogininfo("FIREW_SECGB")

        if account_cnt != "0" and key_b == "1":
            auto_trade = Thread(target=self._auto_trade)
            auto_trade.start()

    """실시간 데이터 수신 구간"""
    def receive_realdata(self, jongmokcode, realtype, realdata):
        if realtype == "주식체결":
            now = self.__getcommrealdata(jongmokcode, 10)
            acc_vol = self.__getcommrealdata(jongmokcode, 13)
            acc_tvol = self.__getcommrealdata(jongmokcode, 14)
            open = self.__getcommrealdata(jongmokcode, 16)
            high = self.__getcommrealdata(jongmokcode, 17)
            low = self.__getcommrealdata(jongmokcode, 18)
            turnover = self.__getcommrealdata(jongmokcode, 31)
            strength = self.__getcommrealdata(jongmokcode, 228)
            gubun = self.__getcommrealdata(jongmokcode, 290)

            print(f"[{jongmokcode}] NOW:{now}, HIGH:{high}, LOW:{low},OPEN:{open}, ACC VOL:{acc_vol}, ACC TVOL:{acc_tvol}, TURNOVER:{turnover}, STRENGTH:{strength}, GUBUN:{gubun}")
            try:
                row_num = self.setrealreg.index[self.setrealreg['item_code'] == jongmokcode].item()

                self.tableWidget.setItem(row_num, dv.tableWidget_now, QTableWidgetItem(str(now)))
                self.tableWidget.setItem(row_num, dv.tableWidget_now, QTableWidgetItem(str(gubun)))
                self.tableWidget.setItem(row_num, dv.tableWidget_now, QTableWidgetItem(str(strength)))
                self.tableWidget.setItem(row_num, dv.tableWidget_now, QTableWidgetItem(str(open)))
                self.tableWidget.setItem(row_num, dv.tableWidget_now, QTableWidgetItem(str(high)))
                self.tableWidget.setItem(row_num, dv.tableWidget_now, QTableWidgetItem(str(low)))
                self.tableWidget.setItem(row_num, dv.tableWidget_now, QTableWidgetItem(str(turnover)))

            except UnboundLocalError:
                pass
            except ValueError:
                pass



    """데이터 수신 구간"""

    def receive_trdata(self, ScrNo, RqName, TrCode, RecordName, PreNext):
        print(f"RQNAME:{RqName}, TRCODE:{TrCode}, RECORDNAME:{RecordName}, PRENEXT:{PreNext}")

        if PreNext == "2":
            self.remained_data = True
        elif PreNext != "2":
            self.remained_data = False

        if RqName == "신고저가요청":
            self.OPT10016(TrCode, RecordName)
        if RqName == "분봉차트조회요청":
            self.opt10080(TrCode, RecordName)

        try:
            self.event_loop.exit()
        except AttributeError:
            pass

    """데이터 처리 구간"""

    def OPT10016(self, TrCode, RecordName):
        """
        data_len : 데이터의 개수를 구함
        for문 : 데이터의 개수를 하나씩 돌면서 index의 인자로 전달
        """
        data_len = self.__getrepeatcnt(TrCode, RecordName)

        for index in range(data_len):
            item_code = self.__getcommdata(TrCode, RecordName, index, "종목코드").strip(" ")
            item_name = self.__getcommdata(TrCode, RecordName, index, "종목명").strip(" ")
            now = self.__getcommdata(TrCode, RecordName, index, "현재가").strip(" ")

            print(f"[{item_code}]:{item_name}. 현재가:{now}")

    """데이터 처리 구간"""

    def opt10080(self, TrCode, RecordName):
        data_len = self.__getrepeatcnt(TrCode, RecordName)

        for index in range(data_len):
            time = self.__getcommdata(TrCode, RecordName, index, "체결시간").strip(" ")
            now = self.__getcommdata(TrCode, RecordName, index, "현재가").strip("+- ")
            open = self.__getcommdata(TrCode, RecordName, index, "시가").strip("+- ")
            high = self.__getcommdata(TrCode, RecordName, index, "고가").strip("+- ")
            low = self.__getcommdata(TrCode, RecordName, index, "저가").strip("+- ")
            #yclose = self.__getcommdata(TrCode, RecordName, index, "전일종가").strip("+- ")
            # print(f"[{time}] NOW:{now}, OPEN:{open}, HIGH:{high}, LOW:{low}, YCLOSE:{yclose}")

            self.chart_data['time'].append(time)
            self.chart_data['now'].append(now)
            self.chart_data['open'].append(open)
            self.chart_data['high'].append(high)
            self.chart_data['low'].append(low)

    """opt10080 : 분봉차트조회요청"""

    def request_opt10080(self, item_code, tick):
        self.chart_data = {'time': [], 'now': [], 'open': [], 'high': [], 'low': []}
        self.__setinputvalue("종목코드", item_code)
        self.__setinputvalue("틱범위", tick)
        self.__setinputvalue("수정주가구분", "1")
        self.__commrqdata("분봉차트조회요청", "opt10080", 0, "0600")
        self.event_loop = QEventLoop()
        self.event_loop.exec_()
        time.sleep(0.5)

        while self.remained_data == True:
            self.__setinputvalue("종목코드", item_code)
            self.__setinputvalue("틱범위", tick)
            self.__setinputvalue("수정주가구분", "1")
            self.__commrqdata("분봉차트조회요청", "opt10080", 2, "0600")
            self.event_loop = QEventLoop()
            self.event_loop.exec_()
            time.sleep(0.5)

        chart_data = pd.DataFrame(self.chart_data, columns=['time', 'now', 'open', 'high', 'low'])
        print(chart_data)
        chart_data.to_sql(name="s"+item_code, con=manage_db.engine_5min, index=False, if_exists='replace')
        print("차트데이터 저장이 완료되었습니다.")
        return chart_data


    """OPT10016 : 신고저가요청"""

    def request_opt10016(self):
        self.__setinputvalue("시장구분", "000")
        self.__setinputvalue("신고저구분", "1")
        self.__setinputvalue("고저종구분", "1")
        self.__setinputvalue("종목조건", "0")
        self.__setinputvalue("거래량구분", "00000")
        self.__setinputvalue("신용조건", "0")
        self.__setinputvalue("상하한포함", "1")
        self.__setinputvalue("기간", "60")
        self.__commrqdata("신고저가요청", "OPT10016", 0, "0161")

    """데이터 입력 구간"""

    def __setinputvalue(self, item, value):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", [item, value])

    """데이터 요청 구간"""

    def __commrqdata(self, rqname, trcode, pre, scrno):
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", [rqname, trcode, pre, scrno])

    """데이터 수신 구간"""

    def __getcommdata(self, trcode, recordname, index, itemname):
        return self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                       [trcode, recordname, index, itemname])

    """실시간 데이터 수신 구간"""

    def __getcommrealdata(self, jongmokcode, fid):
        return self.kiwoom.dynamicCall("GetCommRealData(QString, int)",[jongmokcode, fid])

    """데이터 개수 반환"""

    def __getrepeatcnt(self, trcode, recordname):
        return self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", [trcode, recordname])

    """로그인 정보 표시"""

    def __getlogininfo(self, tag):
        """
        ① "ACCOUNT_CNT" : 전체 계좌 개수
        ② "ACCNO" : 전체 계좌 리스트 반환(구분자는 ;)
        ③ "USER_ID" : 사용자의 ID 반환
        ④ "USER_NAME" : 사용자명 반환
        ⑤ "KEY_BSECGB" : 키보드 보안 해지 여부 (0:정상, 1:해지)
        ⑥ "FIREW_SECGB" : 방화벽 설정 여부 (0:미설정, 1:설정, 2:해지)
        """
        return self.kiwoom.dynamicCall("GetLoginInfo(QString)", [tag])

    """조건검색식 저장"""
    def __getconditionload(self):
        self.kiwoom.dynamicCall("GetConditionLoad()")


    """OnReceiveConditionVer 이벤트 처리"""
    def OnReceiveConditionVer(self):
        condition_list = self.kiwoom.dynamicCall("GetConditionNameList()").split(";")

        for data in condition_list:
            try:
                a = data.split("^")
                self.comboBox.addItem(a[1])
                self.condition_list['index'].append(str(a[0]))
                self.condition_list['name'].append(str(a[1]))
            except IndexError:
                pass

    """SendCondition 함수 실행"""
    def __sendcondition(self,con_name, con_index, int):
        result = self.kiwoom.dynamicCall("SendCondition(QString, QString, int, int)", ["0156", con_name, con_index, int])
        ## 요청 이후의 결과 데이터는 OnReceiveTrCondition 또는 OnReceiveRealCondition으로 반환받음

        if result == 1:
            print("[조건검색] 조회요청 성공")
        if result != 1:
            print("[조건검색] 조회요청 실패")

    """OnReceiveTrCondition 이벤트 처리"""
    def OnReceiveTrCondition(self, scrno, codelist, con_name, con_index, next):
        ## codelist 안에 해당 조건검색식이 찾아낸 종목코드가 담겨 있다.
        self.code_list = [code for code in codelist.split(";") if code.strip()]



    def _pushbtn_3(self):
        item_code = self.lineEdit.text()
        self.__setrealreg(item_code)
        print(self.setrealreg)

    def _pushbtn_4(self):
        item_code = self.lineEdit_2.text()
        if item_code in self.setrealreg['item_code']:
            self.__setrealremove("ALL", item_code)
            print(self.setrealreg)

    def _pushbtn_6(self):
        condition_name = self.comboBox.currentText()

        saved_idx = self.condition_list['name'].index(condition_name)
        condition_idx = self.condition_list['index'][saved_idx]

        self.__sendcondition(condition_name, condition_idx, 0)

    def _pushbtn_7(self):
        total_df = _df.algo1_df()
        print(self.code_list)
        for item_code in self.code_list:
            if item_code !="":
                min5_chart_data = self.request_opt10080(item_code,5)
                print(min5_chart_data)

                result = algorithm_2.algo1(min5_chart_data, "20221004",item_code).run()

                if result[0]:
                    total_df = pd.concat([total_df, result[1]], ignore_index = True).reset_index(drop=True)

        print("total_df")
        print(total_df)
        total_df.to_sql(name =f"s{latest_date}", con=manage_db.engine_condition, index=False, if_exists = 'replace')




    """실시간 등록 함수"""

    def __setrealreg(self,item_code):
        if len(self.setrealreg['item_code']) == 0:
            self.add_to_setrealreg(item_code)
            self.tableWidget.setRowCount(len(self.setrealreg['item_code']))
            row_num = self.setrealreg.index[self.setrealreg['item_code'] == item_code].item()
            self.tableWidget.setItem(row_num, dv.tableWidget_itemcode,QTableWidgetItem(item_code))
            return self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                                           ["0101", item_code, '10', '0'])
        else:
            self.add_to_setrealreg(item_code)
            self.tableWidget.setRowCount(len(self.setrealreg['item_code']))
            row_num = self.setrealreg.index[self.setrealreg['item_code'] == item_code].item()
            self.tableWidget.setItem(row_num, dv.tableWidget_itemcode, QTableWidgetItem(item_code))
            return self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                                           ["0101", item_code, '10', '1'])

    """실시간 해제 함수"""
    def __setrealremove(self, scrno, item_code):
        idx = self.setrealreg.index[self.setrealreg['item_code'] == item_code].item()
        self.setrealreg = self.setrealreg.drop(index=idx).reset_index(drop=True)
        self.tableWidget.removeRow(idx)

        return self.kiwoom.dynamicCall("SetRealRemove(QString, QString"), [scrno, item_code]

    """실시간 등록 종목 데이터 동기화 함수"""
    def add_to_setrealreg(self, item_code):
        if  item_code not in self.setrealreg['item_code']:
            idx = len(self.setrealreg)
            self.setrealreg.loc[idx, 'item_code'] = item_code

    """SendOrder 함수 실행"""
    def __sendorder(self, rqname, scrno, accno, ordertype, code, qty, price, hogagb, orgorderno):
        self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                [rqname, scrno, accno, ordertype, code, qty, price, hogagb, orgorderno])

    def receive_chejandata(self, Gubun, ItemCnt, FidList):
        """
        Gubun(string) - 0:주문체결통보, 1:국내주식잔고통보, 4:파생상품잔고통보
        FidList(string) - 데이터 구분은 ;이다.
        """
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = tradesystem()
    myWindow.show()
    app.exec_()