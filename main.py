import yfinance as yf
import datetime as d

while True:
    try:
        ticker = input('Enter a ticker symbol: ').strip().upper()
        stock = yf.Ticker(ticker)
        price = stock.info['currentPrice']
    except KeyError:
        print('Invalid ticker')
    else:
        today = d.date.today()
        yesterday = today - d.timedelta(days = 1)
        open = stock.info['open']
        prev = stock.info['previousClose']
        f2wkch = stock.info['52WeekChange']
        rec = stock.info['recommendationKey']
        print(f'Current price: {round(price, 2)} '
              f'\n{today} open: {open} '
              f'\n{yesterday} close: {prev} '
              f'\n52 Week Change: {round(f2wkch, 3)}%'
              f'\nAnalyst Recommendation: {rec}')
        break
