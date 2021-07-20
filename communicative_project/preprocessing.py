import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import sys
import codecs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

# Data Processing
## dataset_1
## https://www.kaggle.com/the-guardian/olympic-games?select=summer.csv
dictionary = pd.read_csv("archive/dictionary.csv")
summer = pd.read_csv("archive/summer.csv")
winter = pd.read_csv("archive/winter.csv")
countries = dictionary.dropna()
country_code = countries.Code.to_list()
## winter_countries
winter_countries = winter.loc[winter['Country'].isin(country_code)]
winter_countries['Season'] = ['winter'] * winter_countries.shape[0]
## summer_countries
summer_countries = summer.loc[summer['Country'].isin(country_code)]
summer_countries['Season'] = ['summer'] * summer_countries.shape[0]
## df
df = pd.concat([summer_countries,winter_countries],axis=0).reset_index().iloc[:,1:]
df_50_60 = df[df.Year.isin(range(1950,1970))]
df_70_80 = df[df.Year.isin(range(1970,1990))]
df_90 = df[df.Year.isin(range(1990,1999))]
df_00 = df[df.Year.isin(range(2000,2006))]
df_06 = df[df.Year>2006]
df_NOR = df[df.Country=='NOR']

df.to_csv('data/summer_winter.csv')
countries.to_csv('data/countries.csv')


## dataset_2
URL = "https://www.nytimes.com/interactive/2018/sports/olympics/medal-count-results-schedule.html"

result = requests.get(URL,'html.parser')
soup = BeautifulSoup(result.content, 'html.parser')
table_soup = soup.find(class_="int-table oly-table int-table-medal-standings")

table = table_soup.find('table')
rows_soup = table.find_all('tr')
heads = rows_soup[0]
data = rows_soup[1:]

columns = []
heads_item = heads.find_all('td')
for item in heads_item:
    columns.append(item.text)
rows = []
for row in data:
    rows.append([item.text for item in row])

medal_2018 = pd.DataFrame(rows,columns=columns)
medal_2018['Country'] = medal_2018.apply(lambda X: X['Medal Count'][:-3],axis=1)
medal_2018['Code'] = medal_2018.apply(lambda row: row['Medal Count'][-3:], axis=1)

medal_2018.to_csv('data/medal_2018.csv')


## dataset-3
# https://data.world/makeovermonday/2018w7-the-winter-olympics 
# Winner of Winter Olympics 1924-2014
winner_medals = pd.read_excel('archive/Winer Olympic Medals.xlsx')
# print(winner_medals.loc[8])
winner_medals.to_csv('data/winner_medals.csv',encoding='utf-8')



