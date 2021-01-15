# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 17:23:36 2021

@author: Roméo

Title: Connecting to PostgreSQL Server and Importing Ticker History CSV
"""
'''Cell 0: Import Packages'''
import os,sys
import glob
import time
import psycopg2
from configparser import ConfigParser
import numpy as np
import pandas as pd
import math
from bs4 import BeautifulSoup
import requests
import xlsxwriter
import openpyxl
from selenium import webdriver
# from selenium.webdriver.support.select import Select
#pip install chromedriver-binary==87.0.4280.88.0 if Chrome version 87, else conda install chromedriver-binary
import chromedriver_binary

#%%
'Cell 1: Config file for database'

def config(filename='C:\\Users\\Home\\Desktop\\Roméo\\Professional\\Data Science Finance Project\\PostgreSQL\\database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
#%%
'Cell 2: Connect to PostgreSQL server'
def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()
#%%
'Cell 3: Create History Tables'
#Written using SQL, could also read in csv as file and use psycopg2 cursor method copy_from() to avoid needing to put csvs in PostgreSQL accessible folder
def create_tables():
    History_path='C:\\Historical_Data\\'
    Ticker_list=tuple([fname.split('\\')[-1].split('.')[0] for fname in glob.glob(History_path+'*csv')])
    Table_create = [
        f'''CREATE TABLE IF NOT EXISTS {Ticker}_history(
            date date PRIMARY KEY,
            Open real,
            High real,
            Low real,
            Close real,
            Adj_Close real,
            Volume bigint);'''
            for Ticker in Ticker_list]
    
    Empty_check=tuple([f'''SELECT count(*) FROM (SELECT 1 FROM {Ticker}_history LIMIT 1) AS t;''' for Ticker in Ticker_list])
    'Empty table if returns 0, not empty if 1'
    
    Table_copy=tuple([f'''COPY {Ticker}_history(
    date,
    Open,
    High,
    Low,
    Close,
    Adj_Close,
    Volume) 
    FROM '''+"'"+History_path+f"{Ticker}.csv' DELIMITER ',' CSV HEADER NULL 'null';"
    for Ticker in Ticker_list])
    
    Binary_list=[]
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in Table_create:
            cur.execute(command)
        for command_ind in range(0,len(Empty_check)):
            cur.execute(Empty_check[command_ind])
            Binary=cur.fetchone()[0]
            Binary_list.append(Binary)
            if Binary==0:
                cur.execute(Table_copy[command_ind])
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()