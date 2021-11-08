import streamlit as st

import plotly.express as px

import numpy as np
import pandas as pd
import datetime as dt
import time
import calendar
from datetime import date, timedelta,time
import xlrd
import openpyxl

# import dask
# import dask.dataframe as dd
#
# import config
# import simplejson
# import os
#
# from bs4 import BeautifulSoup
# import requests
# import re
#
# from zipfile import ZipFile, BadZipfile, is_zipfile
# from io import BytesIO

from streamlit import caching

from datetime import datetime


st.set_page_config('FCAS Pricing data',layout='wide')


st.title('Australia FCAS price analysis')

url = 'https://nemweb.com.au/Reports/Current/Vwa_Fcas_Prices/'

path = 'C:/Users/matth/Documents/pythonprograms/FCAS/prices/'

# r = requests.get(url)
# data = BeautifulSoup(r.text,'html.parser')

## List all the files in the url

# mylist = []
# for link in data.find_all('a'):
#     if '.zip' in link.get('href'):
#         mylist.append(link.get('href'))
#
# mylist = [item.split('/')[-1] for item in mylist]
#
# errors = []
#
# for file in mylist:
#     with open(path+file,'wb') as zip:
#         myurl = url+file
#         try:
#             r= requests.get(myurl)
#             zip.write(r.content)
#         except:
#             errors.append(filename)
#
# st.write(errors)
#
# downloadlist = os.listdir(path)
# badlist = []
# for f in downloadlist:
#     if is_zipfile(path+f) == False:
#         badlist.append(f)
#
# computelist = list(set(downloadlist)-set(badlist))
#
# parts = [dask.delayed(pd.read_csv)(path+f,skiprows=1,header=0,parse_dates=['SETTLEMENTDATE']) for f in computelist]
# df = dd.from_delayed(parts)
#
# st.write(df)
#
# df.compute().to_csv('FCAS_prices_data.csv',mode='a')
#




df = pd.read_csv('FCAS_prices_data.csv')

def convert_df(df):
    return df.to_csv().encode('utf-8')

csv = convert_df(df)


collist = df.columns.tolist()
pricecol = [col for col in collist if 'PRICE' in col]

pricecol.insert(0,'SETTLEMENTDATE')

df = df[[col for col in pricecol]]

df['SETTLEMENTDATE'] = pd.to_datetime(df['SETTLEMENTDATE'],errors='coerce')

df['Time of Day'] = df['SETTLEMENTDATE'].dt.strftime('%H:%M')

min = datetime(2020,9,9)
max = datetime(2021,11,8)

with st.form(key='my_form'):
    period = st.slider('Select period',min,max,(min,max))
    EoD = st.checkbox('End of Day 5pm to 8pm')
    # timeinterval = st.slider('Select time interval',time(0,0),time(23,59),value=(time(8,0),time(18,00)),step=timedelta(minutes=30))
    st.form_submit_button('Submit')

# timeinterval = st.slider('Select time interval',time(0,0),time(23,59),value=(time(8,0),time(18,00)),step=timedelta(minutes=30))

if EoD:
    df = df.set_index(pd.DatetimeIndex(df['Time of Day']))
    df = df.between_time(time(17,0),time(20,0))

df = df[(df['SETTLEMENTDATE']>=period[0])&(df['SETTLEMENTDATE']<=period[1])]

distrib = df.describe([0.01,0.025,0.05,0.1,0.25,0.3,0.4,0.5,0.6,0.75,0.9,0.95,0.975,0.99])

st.header('Price distribution')

df = df[df.columns[2:10]]

newdf = pd.DataFrame(df.stack())
newdf.reset_index(inplace=True)
newdf=newdf.iloc[:,1:]
newdf.columns = ['Item','Price']


fig = px.ecdf(newdf,x='Price',color='Item')
fig.update_xaxes(range=(0,100))
st.plotly_chart(fig)

st.write(distrib)


st.download_button(label = 'Download data file',data=csv,file_name='FCAS_price_distribution.csv',mime='text/csv')
