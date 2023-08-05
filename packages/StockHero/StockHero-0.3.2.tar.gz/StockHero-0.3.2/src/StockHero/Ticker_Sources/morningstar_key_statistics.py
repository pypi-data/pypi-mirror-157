# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 18:08:08 2022

@author: RobWen
Version: 0.3.2
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.morningstar.com/stocks/xnas/nvda/quote'

page = requests.get(url)
page = BeautifulSoup(page.content, 'html.parser')

# https://api-global.morningstar.com/sal-service/v1/stock/keyStats/growthTable/0P000003RE?languageId=en&locale=en&clientId=undefined&component=sal-components-key-stats-growth-table&version=3.71.0

morningstar_performance_id = '0P000003RE'

url = f'https://api-global.morningstar.com/sal-service/v1/stock/keyStats/growthTable/{morningstar_performance_id}?languageId=en&locale=en&clientId=undefined&component=sal-components-key-stats-growth-table&version=3.71.0'

headers = {
    'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
}

r = requests.get(url, headers=headers)
json = r.json()

print(json)
print(json['dataList'][0])

len(json['dataList'])
columns_ = []

for i in range(len(json['dataList'])):
    columns_.append(json['dataList'][i]['fiscalPeriodYearMonth'])
    
liste_values = []

for i in range(len(json['dataList'])):
    liste_values.append(list(json['dataList'][i]['epsPer'].values()))

epsPer_0 = json['dataList'][0]['epsPer']
list(epsPer_0.values())

morningstar_growth_eps_df = pd.DataFrame(liste_values
                   , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                   , columns = columns_
                   )

print(morningstar_growth_eps_df)