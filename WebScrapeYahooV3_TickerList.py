# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 17:25:54 2021

@author: Roméo

Title: Webscraping Functions For Yahoo Finance Tickers
"""
'''Cell 0: Import Packages'''
import os,sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
'''Cell 1: Define Breakdown Function For All Information On Yahoo Finance Ticker Site'''
def Company_Information():
    
    Information_Type=0
    while Information_Type==0:
        Information_Type=input('Select the kind of information you want from the following:'
                               ' \n 1. Financial Statements \n 2. Analysis \n 3. Historical Data \n 4. Statistics \n Input:')
        
        if Information_Type==str(1) or Information_Type=='Financial Statements':
            Information=Financial_Statements()
        elif Information_Type==str(2) or Information_Type=='Analysis':
            Information=Analysis()
        elif Information_Type==str(3) or Information_Type=='Historical Data':
            Information=Historical_Data()
        elif Information_Type==str(4) or Information_Type=='Statistics':
            Information=Statistics()
        else:
            Reprompt=input('Please enter one of the 4 options given')
            Information_Type=0
    return Information   
    
#%%
'''Cell 2: Define Webscraping Function For Financial Statements: Income Statement, Balance Sheet, Cash Flow'''
#Loop through the three subtabs (Income Statement, Balance Sheet, and Cash Flow) within the Financials tab. We do use the requests package and pass through the 3 hyperlinks to do so.
#Subsequently, loop through the rows and columns of the table under each subtab to reconstitute them into a dataframe, obtaining the text/data from the html filters applied using BeautifulSoup.
#Each dataframe is added to the final dictionary.

def Financial_Statements():
    Ticker_list=[ticker for ticker in input('Input company tickers separated by commas:').split(',')]
    Company_finance={}
    for Ticker in Ticker_list:
        is_link = f'https://finance.yahoo.com/quote/{Ticker}/financials?p={Ticker}'
        bs_link = f'https://finance.yahoo.com/quote/{Ticker}/balance-sheet?p={Ticker}'
        cf_link = f'https://finance.yahoo.com/quote/{Ticker}/cash-flow?p={Ticker}'
        
        Statements_list=[is_link,bs_link,cf_link]
        Names=['Income Statement','Balance Sheet', 'Cash Flow']
        Table_headers = []
        Rows_list = []
        Table_clean = []
        index = 0
        
        #function to make all values numerical
        def Convert_to_numeric(column):
        
            first_col = [i.replace(',','') for i in column]
            second_col = [i.replace('-','') for i in first_col]
            final_col = pd.to_numeric(second_col)
        
            return final_col
        
        Finance_tables = {}
        
        for link in Statements_list:
            Table_headers = []
            page=requests.get(link)
            soup = BeautifulSoup(page.content,'lxml')
            
            Table_rows=soup.find_all('div', class_='D(tbr)')
            
            #create headers, Table_rows[0] is the 0th row, the headers
            for item in Table_rows[0].find_all('div', class_='D(ib)'):
                Table_headers.append(item.text)
                
           
            #Reconstitute table of statement contents
            while index <= len(Table_rows)-1:
                #Filter for each row of the table
                Table_columns = Table_rows[index].find_all('div', class_='D(tbc)')
                for item in Table_columns:
                    #Each item added to a list to properly format row with each element distinctly
                    Rows_list.append(item.text)
                #Rows_list added to Table_clean, values now separated by commas rather than jumbled together
                Table_clean.append(Rows_list)
                #Clear Rows_list for next link in loop
                Rows_list = []
                index+=1
                
            Table_df = pd.DataFrame(Table_clean[1:])
            Table_df.columns = Table_headers
            
            
            for column in Table_headers[1:]:
                    Table_df[column] = Convert_to_numeric(Table_df[column])
                
            #Remove nan and None values, replace with dash
            Table_df = Table_df.fillna('-')
            #Add table to output dictionary
            Finance_tables[Names[Statements_list.index(link)]]=Table_df
            
            #Reset all lists for next link in loop
            Table_headers = []
            Rows_list = []
            Table_clean = []
            index = 0
        Company_finance[Ticker]=Finance_tables
    return Company_finance

#%%
'''Cell 3: Define Webscarping Function For Analysis'''
#Access the html code on the Analysis tab and find all elements in the 'tables' class.
#Loop through these tables, get all the rows, set up the headers. Loop through the rows and extract each value separately, to avoid jumbling.
#Reconstitute the tables with its extracted values and add them to a dictionary.
def Analysis():
    #Function to make all values numerical, as the numbers are strings
    def Convert_to_numeric(column):
        
        first_col = [i.replace(',','') for i in column]
        second_col = [i.replace('-','') for i in first_col]
        final_col = pd.to_numeric(second_col)
    
        return final_col
    
    Ticker_list=[ticker for ticker in input('Input company tickers separated by commas:').split(',')]
    Company_Analysis={}
    for Ticker in Ticker_list:
        
        analysis_link = f'https://finance.yahoo.com/quote/{Ticker}/analysis?p={Ticker}'
        Table_Names=[]
        Table_headers = []
        Rows_list = []
        Table_clean = []
        index = 0
        Analysis_tables = {}
        
        
        
        page=requests.get(analysis_link)
        soup = BeautifulSoup(page.content,'lxml')
        
        Tables=soup.find_all('table')
        for table in Tables:
            
        
            #create headers, Table_rows[0] is the 0th row, the headers
            Table_rows=table.find_all('th')
            Table_Names.append(Table_rows[0].text)
            for item in Table_rows:
                Table_headers.append(item.text)
                
           
            #Reconstitute table of statement contents
            # while index <= len(Table_rows)-1:
            #     #Filter for each row of the table
            for Row in table.find_all('tr'):
                Row_vals=Row.find_all('td')
                Row_clean=[]
                for Value in Row_vals:
                    Row_clean.append(Value.text)
                #each item added to a temp list
                Rows_list.append(Row_clean)
            #temp_list added to final list
            Table_clean.append(Rows_list)
            #clear temp_list
            Rows_list = []
            index+=1
                
            Table_df = pd.DataFrame(Table_clean[0][1:])
            Table_df.columns = Table_headers
            
            
            # for column in Table_headers[1:]:
            #         Table_df[column] = Convert_to_numeric(Table_df[column])
                
            #Remove nan and None values, replace with dash
            Table_df = Table_df.fillna('-')
            #Add table to output dictionary
            Analysis_tables[Table_Names[Tables.index(table)]]=Table_df
            
            #Reset all lists for next link in loop
            Table_headers = []
            Rows_list = []
            Table_clean = []
            index = 0
        Company_Analysis[Ticker]=Analysis_tables
    return Company_Analysis

#%%
'''Cell 4: Define Webscraping Function For Historical Data'''
#Use Selenium webdriver to select the max data range for historical data and press the apply button, then download the table to csv.
# Then, load in this csv file to a dataframe.

def Historical_Data():
    Ticker_list=[ticker for ticker in input('Input company tickers separated by commas:').split(',')]
    Historical_dict={}
    for Ticker in Ticker_list:
        history_link = f'https://finance.yahoo.com/quote/{Ticker}/history?p={Ticker}'
        
        
        # Use Selenium to find start date of data for specific ticker
        # Replace path with location where you want historical data csv files saved
        History_path='C:\\Historical_Data\\'
        if not os.path.exists(History_path):
            os.makedirs(History_path)
        ChromeOptions=webdriver.ChromeOptions()
        Preferences={"download.default_directory" : History_path}
        ChromeOptions.add_argument('--start-maximized')
        ChromeOptions.add_experimental_option('prefs',Preferences)
        driver=webdriver.Chrome(options=ChromeOptions)
        driver.get(history_link)
        datebutton=driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div/div/div/span')
        datebutton.click()
        maxrange=driver.find_element_by_xpath('//*[@id="dropdown-menu"]/div/ul[2]/li[4]/button')
        maxrange.click()
        applybutton=driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button')
        applybutton.click()
        downloadlink=driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a')
        downloadlink.click()
        while not os.path.exists(History_path+'\\'+Ticker+'.csv'):
            time.sleep(1)
            if os.path.exists(History_path+'\\'+Ticker+'.csv'):
                History_df=pd.read_csv(History_path+'\\'+Ticker+'.csv')
        
        Historical_dict[Ticker]=History_df
        driver.close()
    
    return Historical_dict

#%%
'''Cell 5: Define Webscraping Function For Statistics'''
def Statistics():
    Ticker_list=[ticker for ticker in input('Input company tickers separated by commas:').split(',')]
    Company_Statistics={}
    for Ticker in Ticker_list:
        statistics_link = f'https://finance.yahoo.com/quote/{Ticker}/key-statistics?p={Ticker}'
        Table_Names=[]
        Table_headers = []
        Rows_list = []
        Table_clean = []
        index = 0
        
        
        Statistics_tables = {}
        
        
        
        page=requests.get(statistics_link)
        soup = BeautifulSoup(page.content,'lxml')
        Main=soup.find('div',id='Main')
        Tables=Main.find_all('table')
        
        def Table_Title():
            Embedded_table_name=[Main.find_all('h2')[0].text]
            Regular_table_names=Main.find_all('h3')
            Regular_table_names_clean=[]
            Combined=[]
            for i in range(0,len(Regular_table_names)):
                Regular_table_names_clean.append(Regular_table_names[i].text)
            Combined=Embedded_table_name+Regular_table_names_clean
            return Combined
        Table_Names=Table_Title()    
           
        for table in Tables:
            
            
            #create headers, Table_rows[0] is the 0th row, the headers
            
            Table_rows=table.find_all('th')
            if Tables.index(table)==0:
                for item in Table_rows:
                    Table_headers.append(item.text)
                Table_headers[0]=0
                
               
            #Reconstitute table of statement contents
            # while index <= len(Table_rows)-1:
            #     #Filter for each row of the table
            for Row in table.find_all('tr'):
                Row_vals=Row.find_all('td')
                Row_clean=[]
                for Value in Row_vals:
                    Row_clean.append(Value.text)
                #each item added to a temp list
                Rows_list.append(Row_clean)
            #temp_list added to final list
            Table_clean.append(Rows_list)
            #clear temp_list
            Rows_list = []
            index+=1
            
            if Tables.index(table)==0:
                Table_df = pd.DataFrame(Table_clean[0][1:])
                Table_df.columns = Table_headers
            else:
                Table_df = pd.DataFrame(Table_clean[0])
            
            
            
                
            #Remove nan and None values, replace with dash
            Table_df = Table_df.fillna('-')
            #Add table to output dictionary
            Statistics_tables[Table_Names[Tables.index(table)]]=Table_df
            
            #Reset all lists for next link in loop
            Table_headers = []
            Rows_list = []
            Table_clean = []
            index = 0
        Company_Statistics[Ticker]=Statistics_tables
    return Company_Statistics