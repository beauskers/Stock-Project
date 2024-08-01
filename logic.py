import datetime

from PyQt6.QtWidgets import *
from gui import *
import csv
import re
import yfinance as yf
import datetime as d
import time


class Logic(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.stock = None
        self.ticker = None
        self.marketOpen = True
        self.amount = 0
        self.setupUi(self)

        self.today = d.date.today()
        self.checkMarketStatus()

        self.loginBtn.clicked.connect(lambda: self.login())
        self.toCreateBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.createBtn.clicked.connect(lambda: self.createAcc())
        self.checkButton.clicked.connect(lambda: self.priceCheck())
        self.buyButton.clicked.connect(lambda: self.buyStock())
        self.sellButton.clicked.connect(lambda: self.sellStock())
        self.logoutBtn.clicked.connect(lambda: self.logout())
        self.toSettingsBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.buttonEdit.clicked.connect(lambda: self.settings())

        self.passwordEnter.setEchoMode(QLineEdit.EchoMode.Password)
        self.createPassEnter.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirmEnter.setEchoMode(QLineEdit.EchoMode.Password)

        self.email = ''
        self.password = ''
        self.__balance = 0
        self.__stocks = {}

    def check_email(self):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        self.email = self.createUserEnter.text()
        if re.fullmatch(regex, self.email):
            return True
        else:
            return False

    def login(self):
        self.email = self.usernameEnter.text()
        self.password = self.passwordEnter.text()
        with open('accounts.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                if self.email == line[0] and self.password == line[1]:
                    self.__stocks.clear()
                    self.__balance = float(line[2])
                    self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                    stocks_only = line[3::2]
                    amounts_only = line[4::2]
                    print(stocks_only, amounts_only)
                    for i in range(len(stocks_only)):
                        self.__stocks[stocks_only[i]] = int(amounts_only[i])
                    print(self.__stocks)
                    self.update()
                    self.usernameEnter.clear()
                    self.passwordEnter.clear()
                    self.stackedWidget.setCurrentIndex(2)
                else:
                    self.loginStatus.setText('Incorrect email or password')
                    self.passwordEnter.clear()

    def createAcc(self):
        email_check = self.check_email()
        if email_check:
            self.password = self.createPassEnter.text()
            password_check = self.confirmEnter.text()
            if password_check == self.password:
                with open('accounts.csv', 'a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    account_info = [self.email, self.password, 0]
                    csv_writer.writerow(account_info)
                self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                self.createUserEnter.clear()
                self.createPassEnter.clear()
                self.confirmEnter.clear()
                self.createStatus.setText('')
                self.stackedWidget.setCurrentIndex(2)
            else:
                self.createStatus.setText('Passwords do not match')
                self.confirmEnter.clear()
        else:
            self.createStatus.setText('Email is invalid')

    def checkMarketStatus(self):
        holidays = []
        todayHoliday = False
        day_of_week = self.today.weekday()
        # close_time = d.datetime('15:00')
        if day_of_week < 5 and todayHoliday == False:
            marketOpen = True
            # while True:
            # self.marketStatus.setText(f'Market Status: OPEN - Closes in {(close_time - d.datetime.now())}')
            # time.sleep(1)
        else:
            marketOpen = False
            # while True:
            self.marketStatus.setText(f'Market Status: CLOSED - Opens in ')
            # time.sleep(1)

            # get time to work

    def priceCheck(self):
        while True:
            if self.tickerEnter.text() == '':
                self.stockInfo.setText('No ticker entered')
                break
            try:
                self.ticker = self.tickerEnter.text().strip().upper()
                self.stock = yf.Ticker(self.ticker)
                price = self.stock.info['currentPrice']
            except KeyError:
                self.stockInfo.setText('Invalid ticker')
                break
            else:
                yesterday = self.today - d.timedelta(days=1)
                open = self.stock.info['open']
                prev = self.stock.info['previousClose']
                f2wkch = self.stock.info['52WeekChange']
                rec = self.stock.info['recommendationKey']
                self.stockInfo.setText(f'Current price: {round(price, 2)} '
                                       f'\n{self.today} open: {open} '
                                       f'\n{yesterday} close: {prev} '
                                       f'\n52 Week Change: {round(f2wkch, 3)}%'
                                       f'\nAnalyst Recommendation: {rec}')
                break

    def buyStock(self):
        if self.marketOpen:
            if self.stockInfo.text() == "Invalid ticker" or self.stock is None:
                self.orderStatus.setText('Invalid stock')
            elif not self.amountEnter.text().isdigit():
                self.orderStatus.setText('Invalid amount')
                self.amountEnter.clear()
            elif self.stock.info['currentPrice'] * int(self.amountEnter.text()) > self.__balance:
                self.orderStatus.setText('Too poor')
            else:
                if self.ticker in self.__stocks:
                    self.amount += int(self.amountEnter.text())
                    fillPrice = self.stock.info['currentPrice']
                    self.__balance -= fillPrice * int(self.amountEnter.text())
                    self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                    self.__stocks[self.ticker] += self.amount
                    self.orderStatus.setText(f'Success!\n{self.amount} {self.ticker} filled @ {fillPrice}')
                    print(self.__stocks)
                    self.amount = 0
                else:
                    self.amount += int(self.amountEnter.text())
                    fillPrice = self.stock.info['currentPrice']
                    self.__balance -= fillPrice * int(self.amountEnter.text())
                    self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                    self.__stocks[self.ticker] = self.amount
                    self.orderStatus.setText(f'Success!\n{self.amount} {self.ticker} filled @ {fillPrice}')
                    print(self.__stocks)
                    self.amount = 0
                self.update()
        elif not self.marketOpen:
            self.orderStatus.setText('Market closed')

    def sellStock(self):
        pass
        # Create stock sell

    def clear(self):
        self.tickerEnter.clear()
        # self.comboBox.clear()
        self.loginStatus.setText('')
        self.stockInfo.clear()
        self.amountEnter.clear()
        self.orderStatus.clear()
        self.amount = 0
        self.__stocks = {}
        self.stockShow.setText('')

    def update(self):
        text = f''
        total = 0
        for stock, amount in self.__stocks.items():
            price = yf.Ticker(stock).info["currentPrice"]
            text = text + f'{stock}: {amount} - {price:.2f}\n'
            total += price
        self.stockShow.setText(text)
        self.stockBal.setText(f'${total:.2f}')

    def logout(self):
        with open('accounts.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            info = [self.email, self.password, self.__balance]
            print(self.__stocks)
            for stock, amount in self.__stocks.items():
                info.append(stock)
                info.append(amount)
            csv_writer.writerow(info)
        self.stackedWidget.setCurrentIndex(0)
        self.__balance = 0
        self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
        self.clear()

    def settings(self):
        self.__balance = int(self.amountEdit.text())
        self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
        self.stackedWidget.setCurrentIndex(2)

    # Add login on other pages

    # Fix "middeling"

    # Add 4th panel
