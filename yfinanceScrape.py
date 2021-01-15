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

# To do
# Use system time to get the date
# Use regex to extract the time from the scrape


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


def ScrapeLiveQuotes(tickers, interval):

    # Benchmark ticker for handling synchronous timestamps
    benchmark = tickers[0]
    r = requests.get(
        "https://ca.finance.yahoo.com/quote/{}?p={}".format(benchmark, benchmark))
    soup = BeautifulSoup(r.text, "html.parser")
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
            r = requests.get(
                "https://ca.finance.yahoo.com/quote/{}?p={}".format(ticker, ticker))
            soup = BeautifulSoup(r.text, "html.parser")

            price = soup.find(
                "span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text

            quote_dict[ticker].append(price)

    if any(a != [] for a in quote_dict.values()) == False:
        for idx, ticker in enumerate(ticker_list):
            r = requests.get(
                "https://ca.finance.yahoo.com/quote/{}?p={}".format(ticker, ticker))
            soup = BeautifulSoup(r.text, "html.parser")

            price = soup.find(
                "span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text

            quote_dict[ticker].append(price)

    return print(quote_dict), print(datetime_dict)

# Function Calls


# ticker_list = ["FB", "AAPL", "AMZN", "TSLA", "GOOGL"] # Regular Hour Trading Tickers
# Outside of Regular Trading Hour Trading Tickers
ticker_list = ["ES=F", "YM=F", "NQ=F", "GC=F", "SI=F", "CL=F"]
quote_dict = dict()
datetime_dict = dict()
datetime_dict['DateTime'] = list()
for ticker in ticker_list:
    quote_dict[ticker] = list()

scrape_interval = 5  # seconds
schedule.every(scrape_interval).seconds.do(
    ScrapeLiveQuotes, ticker_list, scrape_interval)

while True:
    schedule.run_pending()
    time.sleep(1)
