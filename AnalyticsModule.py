# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 15:55:09 2021

@author: Roméo

Title: Analytics and Forecasting Module For Ticker Stock Price

"""

'''Cell 0: Import Packages'''
import os,sys
import glob
import psycopg2
from configparser import ConfigParser
import time
import pandas as pd
import numpy as np
import math
import seaborn
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as data_utils
import sklearn as sk
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.datasets import make_regression
from sklearn.metrics import silhouette_score
from sklearn.metrics import mean_absolute_error
#%%
'''Cell 1: Pulling Ticker data from PostgreSQL server'''

#%%
'''Cell 2: Defining X Variable'''

#%%
################################################################
## Cells 3a-3e define, train, and evaluate regression methods ##
################################################################
'''Cell 3a: Linear Regression'''

#%%
'''Cell 3b: Single-hidden layer Feed-Forward Neural Network Regression'''

#%%
'''Cell 3c: Gradient Boost Regression'''

#%%
###############################################################
## Cells 4a-4e predict on trained models, producing forecast ##
###############################################################
'''Cell 4a: Linear Regression'''
#%%
'''Cell 5: Statistical Analysis of Forecasts'''