import pytz
from PyQt6.QtWidgets import *
from gui import *
import csv
import re
import yfinance as yf
import datetime as d
import time
from datetime import datetime, time
import os
import sys

class Logic(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.stock = None
        self.ticker = None
        self.amount = 0
        self.setupUi(self)
        self.marketOpen = None

        if getattr(sys, 'frozen', False):
            self.application_path = os.path.join(sys._MEIPASS, 'accounts.csv')
        else:
            self.application_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'accounts.csv')

        self.today = d.date.today()

        self.loginBtn.clicked.connect(lambda: self.login())
        self.toCreateBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.createBtn.clicked.connect(lambda: self.create_acc())
        self.checkButton.clicked.connect(lambda: self.price_check())
        self.buyButton.clicked.connect(lambda: self.buy_stock())
        self.sellButton.clicked.connect(lambda: self.sell_stock())
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

        self.market_timer = QtCore.QTimer(self)
        self.market_timer.timeout.connect(self.check_market_status)

        self.cooldown_timer = QtCore.QTimer(self)

    def check_email(self) -> bool:
        """
        This function checks to see if the email entered is valid.

        :returns:
            bool: True or False.
        """
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        self.email = self.createUserEnter.text()
        if re.fullmatch(regex, self.email):
            return True
        else:
            return False

    def login(self) -> None:
        """
        Logs the user into the app with an existing account.
        """
        empty = True
        self.email = self.usernameEnter.text()
        self.password = self.passwordEnter.text()
        with open(self.application_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                empty = False
                if self.email == line[0] and self.password == line[1]:
                    self.market_timer.start(1000)
                    self.__stocks.clear()
                    self.__balance = float(line[2])
                    self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                    stocks_only = line[3::2]
                    amounts_only = line[4::2]
                    for i in range(len(stocks_only)):
                        self.__stocks[stocks_only[i]] = int(amounts_only[i])
                    self.update()
                    self.usernameEnter.clear()
                    self.passwordEnter.clear()
                    self.stackedWidget.setCurrentIndex(2)
                else:
                    self.loginStatus.setText('Incorrect email or password')
                    self.passwordEnter.clear()
            if empty:
                self.loginStatus.setText('No accounts in database')

    def create_acc(self) -> None:
        """
        Creates a new account for the user and logs them into the app.
        """
        email_check = self.check_email()
        if email_check:
            self.password = self.createPassEnter.text()
            password_check = self.confirmEnter.text()
            if password_check == self.password:
                self.market_timer.start(1000)
                with open(self.application_path, 'a', newline='') as csv_file:
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

    def check_market_status(self) -> None:
        """
        Checks if the Nasdaq stock market is currently open or closed.
        """
        eastern = pytz.timezone('US/Eastern')
        market_open_time = eastern.localize(datetime.combine(datetime.now(eastern).date(), time(9, 30)))
        market_close_time = eastern.localize(datetime.combine(datetime.now(eastern).date(), time(16, 0)))

        utcnow = d.datetime.now(tz=pytz.UTC)
        estnow = utcnow.astimezone(pytz.timezone('US/Eastern'))
        holidays = []
        todayHoliday = False
        day_of_week = self.today.weekday()
        # print(day_of_week)
        # print(datetime.now(eastern))
        # print(market_close_time - datetime.now(eastern)) # Issue happens after market close but on the NEXT DAY before market open, can change market_open_time to market_open_time.time(), but how to do that for current time?
        # print(market_open_time - (datetime.now(eastern) - d.timedelta(days=1)))

        # Friday after close
        if (day_of_week == 4 and datetime.now(eastern) > market_close_time) and todayHoliday == False:
            self.marketOpen = False
            self.marketStatus.setText(f'Market Status: CLOSED - Opens in {str((market_open_time - (datetime.now(eastern) - d.timedelta(days=3)))).split(".")[0]}')
        # Saturday before "open"
        elif (day_of_week == 5 and (datetime.now(eastern) + d.timedelta(days=1)) > market_open_time) and todayHoliday == False:
            self.marketOpen = False
            self.marketStatus.setText(f'Market Status: CLOSED - Opens in {str((market_open_time - (datetime.now(eastern) - d.timedelta(days=2)))).split(".")[0]}')
        # Saturday after "close"
        elif (day_of_week == 5 and datetime.now(eastern) > market_close_time) and todayHoliday == False:
            self.marketOpen = False
            self.marketStatus.setText(
                f'Market Status: CLOSED - Opens in {str((market_open_time - (datetime.now(eastern) - d.timedelta(days=2)))).split(".")[0]}')
        # Sunday before "open"
        elif (day_of_week == 6 and (datetime.now(eastern) + d.timedelta(days=1)) > market_open_time) and todayHoliday == False:
            self.marketOpen = False
            self.marketStatus.setText(f'Market Status: CLOSED - Opens in {str((market_open_time - (datetime.now(eastern) - d.timedelta(days=1)))).split(".")[0]}')
        # Sunday after "close"
        elif (day_of_week == 6 and datetime.now(eastern) > market_close_time) and todayHoliday == False:
            self.marketOpen = False
            self.marketStatus.setText(
                f'Market Status: CLOSED - Opens in {str((market_open_time - (datetime.now(eastern) - d.timedelta(days=1)))).split(".")[0]}')
        # All other weekdays
        elif (day_of_week < 4) or (day_of_week == 4 and datetime.now(eastern) < market_close_time) and todayHoliday == False:
            if market_open_time <= datetime.now(eastern) <= market_close_time:
                self.marketOpen = True
                self.marketStatus.setText(f'Market Status: OPEN - Closes in {str((market_close_time - (datetime.now(eastern)))).split(".")[0]}')
            else:
                self.marketOpen = False
                if datetime.now(eastern).hour >= market_close_time.hour:
                    self.marketStatus.setText(
                        f'Market Status: CLOSED - Opens in {str((market_open_time - (datetime.now(eastern) - d.timedelta(days=1)))).split(".")[0]}')
                else:
                    self.marketStatus.setText(f'Market Status: CLOSED - Opens in {str((market_open_time - (datetime.now(eastern)))).split(".")[0]}')

    def cooldown(self):
        self.checkButton.setEnabled(False)
        self.cooldown_timer.singleShot(1000, lambda: self.checkButton.setDisabled(False))

    def price_check(self) -> None:
        """
        Gets the current details of a stock.
        """
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
                prev = self.stock.info['previousClose']
                open = self.stock.info['open']
                low = self.stock.info['regularMarketDayLow']
                high = self.stock.info['regularMarketDayHigh']
                fiftytwo_week_low = self.stock.info['fiftyTwoWeekLow']
                fiftytwo_week_high = self.stock.info['fiftyTwoWeekHigh']
                # f2wkch = self.stock.info['52WeekChange']
                rec = self.stock.info['recommendationKey']
                self.stockInfo.setText(f'Current price: {round(price, 2)}'
                                       f'\n{yesterday} close: {prev}'
                                       f'\n{self.today} open: {open}'
                                       f'\nToday\'s range: {low} - {high}'
                                       f'\n52 Week Range: {fiftytwo_week_low} - {fiftytwo_week_high}'
                                       # f'\n52 Week Change: {round(f2wkch, 3)}%'
                                       f'\nAnalyst Rec: {rec}')
                break
        self.cooldown()

    def buy_stock(self) -> None:
        """
        Buys stock for the user based on what they entered.
        """
        if self.checkBox.isChecked():
            if self.marketOpen:
                if self.stockInfo.text() == "Invalid ticker" or self.stock is None:
                    self.orderStatus.setText('Invalid stock')
                elif not self.amountEnter.text().isdigit():
                    self.orderStatus.setText('Invalid amount')
                    self.amountEnter.clear()
                elif self.stock.info['currentPrice'] * int(self.amountEnter.text()) > self.__balance:
                    self.orderStatus.setText('Not enough funds')
                else:
                    if self.comboBox.currentIndex() == 0:
                        if self.ticker in self.__stocks:
                            self.amount += int(self.amountEnter.text())
                            fillPrice = self.stock.info['currentPrice']
                            self.__balance -= fillPrice * int(self.amountEnter.text())
                            self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                            self.__stocks[self.ticker] += self.amount
                            self.orderStatus.setText(f'Success!\n{self.amount} {self.ticker} filled @ {fillPrice}')
                            self.amount = 0
                        else:
                            self.amount += int(self.amountEnter.text())
                            fillPrice = self.stock.info['currentPrice']
                            self.__balance -= fillPrice * int(self.amountEnter.text())
                            self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                            self.__stocks[self.ticker] = self.amount
                            self.orderStatus.setText(f'Success!\n{self.amount} {self.ticker} filled @ {fillPrice}')
                            self.amount = 0
                        self.update()
            elif not self.marketOpen:
                self.orderStatus.setText('Market closed')
        else:
            if self.stockInfo.text() == "Invalid ticker" or self.stock is None:
                self.orderStatus.setText('Invalid stock')
            elif not self.amountEnter.text().isdigit():
                self.orderStatus.setText('Invalid amount')
                self.amountEnter.clear()
            elif self.stock.info['currentPrice'] * int(self.amountEnter.text()) > self.__balance:
                self.orderStatus.setText('Too poor')
            else:
                if self.comboBox.currentIndex() == 0:
                    if self.ticker in self.__stocks:
                        self.amount += int(self.amountEnter.text())
                        fillPrice = self.stock.info['currentPrice']
                        self.__balance -= fillPrice * int(self.amountEnter.text())
                        self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                        self.__stocks[self.ticker] += self.amount
                        self.orderStatus.setText(f'Success!\n{self.amount} {self.ticker} filled @ {fillPrice}')
                        self.amount = 0
                    else:
                        self.amount += int(self.amountEnter.text())
                        fillPrice = self.stock.info['currentPrice']
                        self.__balance -= fillPrice * int(self.amountEnter.text())
                        self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                        self.__stocks[self.ticker] = self.amount
                        self.orderStatus.setText(f'Success!\n{self.amount} {self.ticker} filled @ {fillPrice}')
                        self.amount = 0
                    self.update()

    def sell_stock(self) -> None:
        """
        Sells stock for the user based on what they entered.
        """
        if self.checkBox.isChecked():
            if self.marketOpen:
                if self.stockInfo.text() == "Invalid ticker" or self.stock is None:
                    self.orderStatus.setText('Invalid stock')
                elif not self.amountEnter.text().isdigit():
                    self.orderStatus.setText('Invalid amount')
                    self.amountEnter.clear()
                elif int(self.amountEnter.text()) > self.__stocks[self.ticker]:
                    self.orderStatus.setText('Can\'t oversell assets')
                else:
                    if self.comboBox.currentIndex() == 0:
                        if self.ticker in self.__stocks:
                            self.amount += int(self.amountEnter.text())
                            fillPrice = self.stock.info['currentPrice']
                            self.__balance += fillPrice * int(self.amountEnter.text())
                            self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                            self.__stocks[self.ticker] -= self.amount
                            self.orderStatus.setText(f'Success!\n{self.amount} {self.ticker} filled @ {fillPrice}')
                            self.amount = 0
                        else:
                            self.orderStatus.setText('You don\'t own any of that stock')
                        self.update()
            elif not self.marketOpen:
                self.orderStatus.setText('Market closed')
        else:
            if self.stockInfo.text() == "Invalid ticker" or self.stock is None:
                self.orderStatus.setText('Invalid stock')
            elif not self.amountEnter.text().isdigit():
                self.orderStatus.setText('Invalid amount')
                self.amountEnter.clear()
            elif int(self.amountEnter.text()) > self.__stocks[self.ticker]:
                self.orderStatus.setText('Can\'t oversell assets')
            else:
                if self.comboBox.currentIndex() == 0:
                    if self.ticker in self.__stocks:
                        self.amount += int(self.amountEnter.text())
                        fillPrice = self.stock.info['currentPrice']
                        self.__balance += fillPrice * int(self.amountEnter.text())
                        self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                        self.__stocks[self.ticker] -= self.amount
                        self.orderStatus.setText(f'Success!\n{self.amount} {self.ticker} filled @ {fillPrice}')
                        self.amount = 0
                    else:
                        self.orderStatus.setText('You don\'t own any of that stock')
                    self.update()

    def clear(self) -> None:
        """
        Clears multiple objects
        """
        self.tickerEnter.clear()
        # self.comboBox.clear()
        self.loginStatus.setText('')
        self.stockInfo.clear()
        self.amountEnter.clear()
        self.orderStatus.clear()
        self.amount = 0
        self.__stocks = {}
        self.stockShow.setText('')
        self.stockBal.setText('')
        self.checkBox.setChecked(True)
        self.liveTimer.setChecked(True)

    def update(self) -> None:
        """
        Updates the stock portfolio's value after a stock buy or sell.
        """
        text = f''
        total = 0
        for stock, amount in self.__stocks.items():
            price = yf.Ticker(stock).info["currentPrice"]
            text = text + f'{stock}: {amount} - {price * amount:.2f}\n'
            total += (price * amount)
        self.stockShow.setText(text)
        self.stockBal.setText(f'Portfolio Value: ${total:.2f}')

    def logout(self) -> None:
        """
        Logs the user out of their account and saves their data.
        """
        with open(self.application_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            info = [self.email, self.password, self.__balance]
            for stock, amount in self.__stocks.items():
                info.append(stock)
                info.append(amount)
            csv_writer.writerow(info)
        self.stackedWidget.setCurrentIndex(0)
        self.__balance = 0
        self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
        self.clear()
        self.clean_up()
        self.market_timer.stop()

    def settings(self) -> None:
        """
        Deals with all the options in the settings page
        """
        if self.amountEdit.text() == '':
            self.stackedWidget.setCurrentIndex(2)
            self.amountEdit.clear()
        else:
            try:
                self.__balance = int(self.amountEdit.text())
                self.balLabel.setText(f'Account Balance: ${self.__balance:.2f}')
                self.stackedWidget.setCurrentIndex(2)
                self.amountEdit.clear()
                self.settingsLabel.clear()
            except ValueError:
                self.settingsLabel.setText('Invalid Money Amount')
        if not self.checkBox.isChecked():
            self.liveTimer.setChecked(False)
            self.market_timer.stop()
            self.marketStatus.setText('Market Status: N/A')
        else:
            self.check_market_status()
        # if self.liveTimer.isChecked() and not self.checkBox.isChecked():
        #     self.settingsLabel.setText('TruMarket must be enabled')
        if self.liveTimer.isChecked():
            self.market_timer.start(1000)
        if not self.liveTimer.isChecked():
            self.market_timer.stop()

    def clean_up(self) -> None:
        """
        Optimizes the multiple account system save file to keep space and lag to a minimum.
        """
        save_list = []
        with open(self.application_path, 'r') as csv_file:
            csv_reader = list(csv.reader(csv_file))
            if csv_reader:
                test = csv_reader[-1]
                save_list.append(test)
                for row in reversed(csv_reader[:-1]):
                    if row[0] not in [element[0] for element in save_list]:
                        save_list.append(row)
        with open(self.application_path, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            for element in save_list:
                csv_writer.writerow(element)
