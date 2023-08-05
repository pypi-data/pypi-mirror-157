# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 18:08:08 2022

@author: RobWen
Version: 0.3.2
"""

import requests
from bs4 import BeautifulSoup

class Gurufocus:
    
    def __init__(self, ticker, headers_standard):
        self.ticker = ticker
        self.headers_standard = headers_standard
        
    def __repr__(self):
        return(self.ticker)
        
    def __str__(self):
        return(self.ticker)
        #return(self.ticker or '') # by None

    #####################
    ###               ###
    ###  Gurufocus    ###
    ###               ###
    #####################
    
    def stock_exchange(self):
        r = requests.get(f'https://www.gurufocus.com/stock/{self.ticker}/summary')
        stock_exchange = BeautifulSoup(r.content, 'html.parser')
        
        try:
            stock_exchange = stock_exchange.find('span', {'class':'t-label'}).text.split()[0]
        except:
            return None
        
        return stock_exchange
    
    def gurufocus_pe_ratio_av_v(self):
        if Gurufocus.stock_exchange(self) != None:
            r = requests.get(f'https://www.gurufocus.com/term/pettm/{Gurufocus.stock_exchange(self)}/PE-Ratio-TTM/')
            page = BeautifulSoup(r.content, 'html.parser')
        
            table = page.find('div', {'class':'history_bar value'})
            try:
                table = table.find('strong').text.split()
                self.__PE_Ratio_Average = float(table[3])
                return self.__PE_Ratio_Average
            except:
                return None
        else:
            return None
        
    def gurufocus_debt_to_ebitda(self):
        
        if Gurufocus.stock_exchange(self) != None:
          
            url = f'https://www.gurufocus.com/term/debt2ebitda/{Gurufocus.stock_exchange(self)}/Debt-to-EBITDA'
            page = requests.get(url)
            page = BeautifulSoup(page.content, 'html.parser')

            table = page.find('div', {'class':'history_bar value'})

            try:
                table = table.find('strong')
                table = table.text.split()
                debt_to_EBITDA = table[7]
                try:
                    self.__debt_to_EBITDA = float(debt_to_EBITDA)
                except:
                    return '#'
                return self.__debt_to_EBITDA
            except (AttributeError):
                return '#'