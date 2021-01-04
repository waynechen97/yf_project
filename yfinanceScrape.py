# IMPORTS
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import datetime
import sys
import os
import sched
import time

s = sched.scheduler(time.time, time.sleep)

ticker_list = ["FB", "AAPL", "AMZN", "TSLA", "GOOGL"]


def ScrapeLiveQuotes(tickers=ticker_list, interval=5, scrape=True):

    quote_dict = [{} for sub in range(len(ticker_list))]

    counter = 0
    for ticker in ticker_list:
        r = requests.get(
            "https://ca.finance.yahoo.com/quote/{}?p={}".format(ticker, ticker))
        soup = BeautifulSoup(r.text, "html.parser")

        price = soup.find(
            "span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
        datetime = soup.find(
            "div", {"id": "quote-market-notice"}).find("span").text

        dict_key = ticker + ", " + datetime

        if quote_dict[counter] == {}:
            quote_dict[counter][dict_key] = price

        if (quote_dict[counter] is not {} and dict_key != list(quote_dict[counter])[len(quote_dict[counter]) - 2]):
            quote_dict[counter][dict_key] = price

        counter += 1
    return quote_dict
    s.enter(5, 1, ScrapeLiveQuotes)


quotes = ScrapeLiveQuotes()
print(quotes)
