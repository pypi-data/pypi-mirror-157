# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 18:08:08 2022

@author: RobWen
Version: 0.3.2
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from StockHero.Ticker_Sources.gurufocus import Gurufocus

class Morningstar_Quote:
    
    def __init__(self, ticker, headers_standard):
        self.ticker = ticker
        self.headers_standard = headers_standard
        
    def __repr__(self):
        return(self.ticker)
        
    def __str__(self):
        return(self.ticker)
        #return(self.Morningstar_Key_Ratios or '') # by None
        
    #####################
    ###               ###
    ###  Morningstar  ###
    ###               ###
    #####################
    
    ### Morningstar Quote                                       ###
    ### e.g. https://www.morningstar.com/stocks/xnas/nvda/quote ###
    ### Rückgabe None implementiert und getestet                ###
    ### Ungültige Werte = NaN implementiert                     ###
    def morningstar_quote_df(self):
        
        if Gurufocus.stock_exchange(self) != None:
            if Gurufocus.stock_exchange(self).split(':')[0] == 'NAS':
                url = f'https://www.morningstar.com/stocks/xnas/{self.ticker}/quote'
            elif Gurufocus.stock_exchange(self).split(':')[0] == 'NYSE':
                url = f'https://www.morningstar.com/stocks/xnys/{self.ticker}/quote'
        else:
            return None
        
        page = requests.get(url)
        page = BeautifulSoup(page.content, 'html.parser')
        string = page.find_all(text=True)[-4].replace('"','').strip().split(',')
        
        parameter = [s for s in string if "byId" in s]
                
        if not parameter:
            df_morningstar_quote = None
        else:
            morningstar_performance_id = parameter[0].split(':')[1].replace('{','')
            
            url = f'https://api-global.morningstar.com/sal-service/v1/stock/header/v2/data/{morningstar_performance_id}/securityInfo?showStarRating=&languageId=en&locale=en&clientId=MDC&benchmarkId=category&component=sal-components-quote&version=3.69.0'
            
            headers = {
                'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
            }
            
            r = requests.get(url, headers=headers)
            dictionary = r.json()
            
            priceEarnings = dictionary["priceEarnings"]
            priceBook = dictionary["priceBook"]
            priceSale = dictionary["priceSale"]
            forwardPE = dictionary["forwardPE"]
            forwardDivYield = dictionary["forwardDivYield"]
            
            url = f'https://api-global.morningstar.com/sal-service/v1/stock/keyStats/{morningstar_performance_id}?languageId=en&locale=en&clientId=MDC&benchmarkId=category&component=sal-components-quote&version=3.69.0'
            
            headers = {
                'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
            }
            
            r = requests.get(url, headers=headers)
            json = r.json()
            
            revenue3YearGrowth = json['revenue3YearGrowth']['stockValue']
            netIncome3YearGrowth = json['netIncome3YearGrowth']['stockValue']
            operatingMarginTTM = json['operatingMarginTTM']['stockValue']
            netMarginTTM = json['netMarginTTM']['stockValue']
            roaTTM = json['roaTTM']['stockValue']
            roeTTM = json['roeTTM']['stockValue']
            freeCashFlowTTM = json['freeCashFlow']['cashFlowTTM']
            
            try:
                priceEarnings = '{:.2f}'.format(float(priceEarnings))
                priceBook = '{:.2f}'.format(float(priceBook))
                priceSale = '{:.2f}'.format(float(priceSale))
                forwardPE = '{:.2f}'.format(float(forwardPE))
                forwardDivYield = float(forwardDivYield) * 100 # in %
                revenue3YearGrowth = '{:.2f}'.format(float(revenue3YearGrowth))
                netIncome3YearGrowth = '{:.2f}'.format(float(netIncome3YearGrowth))
                operatingMarginTTM = '{:.2f}'.format(float(operatingMarginTTM))
                netMarginTTM = '{:.2f}'.format(float(netMarginTTM))
                roaTTM = '{:.2f}'.format(float(roaTTM))
                roeTTM = '{:.2f}'.format(float(roeTTM))
                freeCashFlowTTM = '{:,.2f}'.format(float(freeCashFlowTTM)) # locale='en_US'
            except(TypeError):
                pass
            
            df_morningstar_quote = pd.DataFrame([priceEarnings, priceBook, priceSale, forwardPE, forwardDivYield
                               , revenue3YearGrowth, netIncome3YearGrowth, operatingMarginTTM, netMarginTTM, roaTTM, roeTTM
                               , freeCashFlowTTM]
                              , index =['Price/Earnings', 'Price/Book', 'Price/Sales', 'Consensus Forward P/E', 'Forward Div Yield %'
                                        , 'Rev 3-Yr Growth', 'Net Income 3-Yr Growth'
                                        , 'Operating Margin % TTM', 'Net Margin % TTM', 'ROA % TTM'
                                        , 'ROE % TTM', 'Current Free Cash Flow']
                              , columns =[self.ticker + ' Ratio'])
            
            df_morningstar_quote = df_morningstar_quote.fillna(value=np.nan) # None mit NaN ersetzen für df
        
        # Rückgabe
        self.__df_morningstar_quote = df_morningstar_quote
        
        return self.__df_morningstar_quote