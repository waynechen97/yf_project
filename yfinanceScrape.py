# IMPORTS
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import datetime
from datetime import time
import sys
import os
import schedule
import time

path = r'C:\Python\Web Scrapping\yfinanceScrape.py'
scrapeInterval = 5  # seconds
fileIdentifier = 'Bitcoin'
ScrapeCount = 0


def defineTickers(DelayedTickers=False, LiveTickers=False, BitcoinScrape=False):
    if DelayedTickers:
        ticker_list = ["ES=F", "YM=F", "NQ=F", "GC=F", "SI=F", "CL=F"]
    elif LiveTickers:
        ticker_list = ["FB", "AAPL", "AMZN", "TSLA", "GOOGL"]
    elif BitcoinScrape:
        ticker_list = ["BTC-USD"]

    return ticker_list


def defineEmptyDataStructure(ticker_list):
    # Define quote_dict to store scrapped pries
    # Define datetime_dict to store scrapped timestamps
    quote_dict = dict()
    datetime_dict = dict()

    datetime_dict['DateTime'] = list()

    for ticker in ticker_list:
        quote_dict[ticker] = list()

    return quote_dict, datetime_dict


def convert24(str1):

    # Checking if last two elements of time
    # is AM and first two elements are 12
    if len(str1) == 6 and str1[-2:] == 'AM':
        hour = int(str1[0])
        minutes = int(str1[2:4])
        time = datetime.time(hour, minutes)
        return time

    if len(str1) == 7 and str1[-2:] == 'AM':
        # if str1[:2] == "00":
        #     hour = 0
        #     minutes = int(str[3:5])
        #     time = datetime.time(hour, minutes)
        #     return time
        hour = int(str1[:2])
        minutes = int(str1[3:5])
        time = datetime.time(hour, minutes)
        return time

    if len(str1) == 6 and str1[-2:] == 'PM':
        hour = int(str1[0])
        minutes = int(str1[2:4])
        time = datetime.time(hour+12, minutes)
        return time

    if len(str1) == 7 and str1[-2:] == 'PM':
        # if str1[:2] == "12":
        #     hour = 0
        #     minutes = int(str[3:5])
        #     time = datetime.time(hour, minutes)
        #     return time
        hour = int(str1[:2])
        minutes = int(str1[3:5])
        time = datetime.time(hour+12, minutes)

        return time


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def timeStampAdjustment(date_time, LiveTickersOnly=False, DelayedTickersOnly=False, DelayLength=10):

    if LiveTickersOnly:  # Equities have live quotes
        now = datetime.datetime.now()
        dtwithoutseconds = now.replace(second=0, microsecond=0)
        return dtwithoutseconds

    elif DelayedTickersOnly:  # Only select delayed quotes of the same delay duration

        timeBfConv = re.findall(
            r'\b((0?[1-9]|1[012])([:.][0-5][0-9])?(\s?[AP]M)|([01]?[0-9]|2[0-3])([:.][0-5][0-9]))\b', date_time)

        timeProper = str(convert24(timeBfConv[0][0]))
        timeProper = datetime.datetime.strptime(timeProper, '%H:%M:%S').time()
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        start = datetime.time(23, 59-DelayLength, 0)
        end = datetime.time(23, 59, 0)
        while time_in_range(start, end, timeProper):
            date = datetime.datetime.today() - timedelta(days=1)
            return str(date) + ' ' + str(timeProper)

        return str(date) + ' ' + str(timeProper)


def ScrapeLiveQuotes(tickers, scrapeInterval):

    # Benchmark ticker for handling synchronous timestamps
    benchmark = tickers[0]

    if 'BTC-USD' in tickers:
        r = requests.get(
            "https://ca.finance.yahoo.com/quote/{}".format(benchmark))
    else:
        r = requests.get(
            "https://ca.finance.yahoo.com/quote/{}?p={}".format(benchmark, benchmark))

    soup = BeautifulSoup(r.text, "html.parser")

    try:
        date_base = soup.find(
            "div", {"id": "quote-market-notice"}).find("span").text

        date_base = timeStampAdjustment(
            date_time=date_base, DelayedTickersOnly=True)

        # False means the dictionary is empty
        if any(a != [] for a in datetime_dict.values()) == False:
            datetime_dict['DateTime'].append(date_base)
        elif date_base != datetime_dict['DateTime'][len(datetime_dict['DateTime']) - 1]:
            datetime_dict['DateTime'].append(date_base)

            for idx, ticker in enumerate(ticker_list):
                if 'BTC-USD' in tickers:
                    r = requests.get(
                        "https://ca.finance.yahoo.com/quote/{}".format(benchmark))
                else:
                    r = requests.get(
                        "https://ca.finance.yahoo.com/quote/{}?p={}".format(benchmark, benchmark))
                soup = BeautifulSoup(r.text, "html.parser")

                price = soup.find(
                    "span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text

                quote_dict[ticker].append(price)

        if any(a != [] for a in quote_dict.values()) == False:
            for idx, ticker in enumerate(ticker_list):
                if 'BTC-USD' in tickers:
                    r = requests.get(
                        "https://ca.finance.yahoo.com/quote/{}".format(benchmark))
                else:
                    r = requests.get(
                        "https://ca.finance.yahoo.com/quote/{}?p={}".format(benchmark, benchmark))
                soup = BeautifulSoup(r.text, "html.parser")

                price = soup.find(
                    "span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text

                quote_dict[ticker].append(price)

        df = {**datetime_dict, **quote_dict}

        df = pd.DataFrame(df)
        # df.to_csv(path = path,'file_{}_test_save_5m_interval'.format(count))
        pathname = 'file_' + fileIdentifier + '.csv'
        df.to_csv(pathname, index=False)

        min_scrapped = len(datetime_dict['DateTime'])
        total_tickers = len(quote_dict.keys())

        global ScrapeCount
        ScrapeCount += 1

        return print(f'Scrape Complete, Frequency: {scrapeInterval} s | Minutes Scrapped: {min_scrapped} | Total Tickers: {total_tickers} | Successful Scrapes: {ScrapeCount}')

    except Exception:
        print('Scrapped Failed, Recovering and Trying Again...')

# Function Calls to Initiate Scrape


ticker_list = defineTickers(BitcoinScrape=True)
quote_dict, datetime_dict = defineEmptyDataStructure(ticker_list)

schedule.every(scrapeInterval).seconds.do(
    ScrapeLiveQuotes, ticker_list, scrapeInterval)

while True:
    schedule.run_pending()
    time.sleep(1)
