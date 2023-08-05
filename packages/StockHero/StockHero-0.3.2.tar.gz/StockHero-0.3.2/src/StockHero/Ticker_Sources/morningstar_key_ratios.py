# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 18:08:08 2022

@author: RobWen
Version: 0.3.2
"""

import pandas as pd
import requests
import numpy as np

class Morningstar_Key_Ratios:
    
    def __init__(self, ticker, headers_standard):
        self.ticker = ticker
        self.headers_standard = headers_standard
        self.data = self.__get_data()
        self.__laenge()
        
    def __repr__(self):
        return(self.ticker)
        
    def __str__(self):
        return(self.ticker)
        #return(self.Morningstar_Key_Ratios or '') # by None
        
    #####################
    ###               ###
    ###  Morningstar  ###
    ###  Key Ratios   ###
    ###               ###
    ##################### 
    
    def __get_data(self):
        
        headers = {'Referer': f'http://financials.morningstar.com/ratios/r.html?t={self.ticker}'}
        r = requests.get(f"http://financials.morningstar.com/finan/ajax/exportKR2CSV.html?&t={self.ticker}", headers=headers)
        csvdatei = r.content
        
        my_decoded_str = csvdatei.decode()
        my_decoded_str = my_decoded_str.split()
        
        return my_decoded_str
    
    def __laenge(self):
        if len(self.data) == 304:
            self.length = 0
        elif len(self.data) == 305:
            self.length = 1
        elif len(self.data) == 306:
            self.length = 2
        elif len(self.data) == 307:
            self.length = 3
        elif len(self.data) == 308:
            self.length = 4
        else:
            self.length = 5
            
    ### Morningstar Financials                                      ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet                    ###
    ### Ungültige Werte = NaN implementiert                         ###
    def morningstar_financials_df(self):
                
        data = self.data
        length = self.length
            
        if len(data) == 0:
            self.df_morningstar_financials = None
        else:
            self.df_morningstar_financials = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[12+length]), Morningstar_Key_Ratios.__data_list(data[15+length])
                                            , Morningstar_Key_Ratios.__data_list(data[19+length]), Morningstar_Key_Ratios.__data_list(data[22+length])
                                            , Morningstar_Key_Ratios.__data_list(data[26+length]), Morningstar_Key_Ratios.__data_list(data[30+length])
                                            , Morningstar_Key_Ratios.__data_list(data[32+length]), Morningstar_Key_Ratios.__data_list(data[36+length])
                                            , Morningstar_Key_Ratios.__data_list(data[38+length]), Morningstar_Key_Ratios.__data_list(data[44+length])
                                            , Morningstar_Key_Ratios.__data_list(data[49+length]), Morningstar_Key_Ratios.__data_list(data[53+length])
                                            , Morningstar_Key_Ratios.__data_list(data[58+length]), Morningstar_Key_Ratios.__data_list(data[65+length])
                                            , Morningstar_Key_Ratios.__data_list(data[69+length])]
                          , index =[Morningstar_Key_Ratios.__index(data[10+length] + ' ' + data[11+length] + ' ' + data[12+length])
                                    , Morningstar_Key_Ratios.__index(data[13+length] + ' ' + data[14+length] + ' ' + data[15+length])
                                    , Morningstar_Key_Ratios.__index(data[16+length] + ' ' + data[17+length] + ' ' + data[18+length]+ ' ' + data[19+length])
                                    , Morningstar_Key_Ratios.__index(data[20+length] + ' ' + data[21+length] + ' ' + data[22+length])
                                    , Morningstar_Key_Ratios.__index(data[23+length] + ' ' + data[24+length] + ' ' + data[25+length]+ ' ' + data[26+length])
                                    , Morningstar_Key_Ratios.__index(data[27+length] + ' ' + data[28+length] + ' ' + data[29+length]+ ' ' + data[30+length])
                                    , Morningstar_Key_Ratios.__index(data[31+length] + ' ' + data[32+length])
                                    , Morningstar_Key_Ratios.__index(data[33+length] + ' ' + data[34+length] + ' ' + data[35+length]+ ' ' + data[36+length])
                                    , Morningstar_Key_Ratios.__index(data[37+length] + ' ' + data[38+length])
                                    , Morningstar_Key_Ratios.__index(data[39+length] + ' ' + data[40+length] + ' ' + data[41+length]+ ' ' + data[42+length]+ ' ' + data[43+length]+ ' ' + data[44+length])
                                    , Morningstar_Key_Ratios.__index(data[45+length] + ' ' + data[46+length] + ' ' + data[47+length]+ ' ' + data[48+length]+ ' ' + data[49+length])
                                    , Morningstar_Key_Ratios.__index(data[50+length] + ' ' + data[51+length] + ' ' + data[52+length]+ ' ' + data[53+length])
                                    , Morningstar_Key_Ratios.__index(data[54+length] + ' ' + data[55+length] + ' ' + data[56+length]+ ' ' + data[57+length]+ ' ' + data[58+length])
                                    , Morningstar_Key_Ratios.__index(data[59+length] + ' ' + data[60+length] + ' ' + data[61+length]+ ' ' + data[62+length]+ ' ' + data[53+length]+ ' ' + data[64+length]+ ' ' + data[65+length])
                                    , Morningstar_Key_Ratios.__index(data[66+length] + ' ' + data[67+length] + ' ' + data[68+length]+ ' ' + data[69+length])]
                          , columns = Morningstar_Key_Ratios.__data_list(data[8+length] + data[9+length]))
        
        # There is a bug somewhere =D
        if self.df_morningstar_financials.iloc[-1,-1] == None:
            self.df_morningstar_financials.iloc[-1,-1] = np.nan
    
        return self.df_morningstar_financials
    
    ### Morningstar Margins % of Sales ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet ###
    ### Ungültige Werte = NaN implementiert ###
    def morningstar_margins_of_sales_df(self):
        
        data = self.data
        length = self.length
        
        if len(data) == 0:
            self.df_morningstar_margins_of_sales = None
        else:
            self.df_morningstar_margins_of_sales = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[78+length]), Morningstar_Key_Ratios.__data_list(data[79+length])
                                                  , Morningstar_Key_Ratios.__data_list(data[81+length]), Morningstar_Key_Ratios.__data_list(data[82+length])
                                                  , Morningstar_Key_Ratios.__data_list(data[83+length]), Morningstar_Key_Ratios.__data_list(data[84+length])
                                                  , Morningstar_Key_Ratios.__data_list(data[86+length]), Morningstar_Key_Ratios.__data_list(data[91+length])
                                                  , Morningstar_Key_Ratios.__data_list(data[93+length])]
                              , index =['Revenue', 'COGS', 'Gross Margin', 'SG&A'
                                        , 'R&D', 'Other', 'Operating Margin', 'Net Int Inc & Other', 'EBT Margin']
                              , columns = Morningstar_Key_Ratios.__data_list(data[77+length]))
        
        return self.df_morningstar_margins_of_sales
    
    ### Morningstar Profitability                                   ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet                    ###
    ### Ungültige Werte = NaN implementiert                         ###
    def morningstar_profitability_df(self):
        
        data = self.data
        length = self.length
    
        if len(data) == 0:
            self.df_morningstar_profitability = None
        else:
            self.df_morningstar_profitability = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[97+length]), Morningstar_Key_Ratios.__data_list(data[100+length])
                                               , Morningstar_Key_Ratios.__data_list(data[103+length]), Morningstar_Key_Ratios.__data_list(data[107+length])
                                               , Morningstar_Key_Ratios.__data_list(data[110+length]), Morningstar_Key_Ratios.__data_list(data[114+length])
                                               , Morningstar_Key_Ratios.__data_list(data[119+length]), Morningstar_Key_Ratios.__data_list(data[121+length])]
                          , index =['Tax Rate %', 'Net Margin %', 'Asset Turnover (Average)', 'Return on Assets %'
                                    , 'Financial Leverage (Average)', 'Return on Equity %', 'Return on Invested Capital %'
                                    ,'Interest Coverage']
                          , columns = Morningstar_Key_Ratios.__data_list(data[94+length]))
    
        return self.df_morningstar_profitability
    
    ### Morningstar Growth - Revenue %                              ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet                    ###
    ### Ungültige Werte = NaN implementiert                         ###
    def morningstar_growth_revenue_df(self):
        
        data = self.data
        length = self.length
        
        if len(data) == 0:
            self.df_morningstar_growth_revenue = None
        else:
            self.df_morningstar_growth_revenue = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[132+length]), Morningstar_Key_Ratios.__data_list(data[134+length])
                                                , Morningstar_Key_Ratios.__data_list(data[136+length]), Morningstar_Key_Ratios.__data_list(data[138+length])]
                          , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                          , columns = Morningstar_Key_Ratios.__data_list(data[125+length] + data[126+length] + ' ' + data[127+length]))
    
        return self.df_morningstar_growth_revenue
    
    ### Morningstar Growth - Operating Income %                     ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet                    ###
    ### Ungültige Werte = NaN implementiert                         ###
    def morningstar_growth_operating_income_df(self):
        
        data = self.data
        length = self.length
        
        if len(data) == 0:
            self.df_morningstar_growth_operating_income = None
        else:
            self.df_morningstar_growth_operating_income = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[144+length]), Morningstar_Key_Ratios.__data_list(data[146+length])
                                                         , Morningstar_Key_Ratios.__data_list(data[148+length]), Morningstar_Key_Ratios.__data_list(data[150+length])]
                            , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                            , columns = Morningstar_Key_Ratios.__data_list(data[125+length] + data[126+length] + ' ' + data[127+length]))
    
        return self.df_morningstar_growth_operating_income
    
    ### Morningstar Growth - Net Income %                           ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet                    ###
    ### Ungültige Werte = NaN implementiert                         ###
    def morningstar_growth_net_income_df(self):
        
        data = self.data
        length = self.length
        
        if len(data) == 0:
            self.df_morningstar_growth_net_income = None
        else:
            try: 
                self.df_morningstar_growth_net_income = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[156+length]), Morningstar_Key_Ratios.__data_list(data[158+length])
                                                       , Morningstar_Key_Ratios.__data_list(data[160+length]), Morningstar_Key_Ratios.__data_list(data[162+length])]
                              , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                              , columns = Morningstar_Key_Ratios.__data_list(data[125+length] + data[126+length] + ' ' + data[127+length]))
            except(ValueError):
                Morningstar_Key_Ratios.__data_list(data[156+length]).append(None)
                self.df_morningstar_growth_net_income = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[156+length]), Morningstar_Key_Ratios.__data_list(data[158+length])
                                                       , Morningstar_Key_Ratios.__data_list(data[160+length]), Morningstar_Key_Ratios.__data_list(data[162+length])]
                              , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                              , columns = Morningstar_Key_Ratios.__data_list(data[125+length] + data[126+length] + ' ' + data[127+length]))
    
        return self.df_morningstar_growth_net_income
    
    ### Morningstar Growth - EPS %                                  ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet                    ###
    ### Ungültige Werte = NaN implementiert                         ###
    def morningstar_growth_eps_df(self):
        
        data = self.data
        length = self.length
       
        if len(data) == 0:
            self.df_morningstar_growth_eps = None
        else:
            self.df_morningstar_growth_eps = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[167+length]), Morningstar_Key_Ratios.__data_list(data[169+length])
                                            , Morningstar_Key_Ratios.__data_list(data[171+length]), Morningstar_Key_Ratios.__data_list(data[173+length])]
                          , index =['Year over Year', '3-Year Average', '5-Year Average', '10-Year Average']
                          , columns = Morningstar_Key_Ratios.__data_list(data[125+length] + data[126+length] + ' ' + data[127+length]))
    
        return self.df_morningstar_growth_eps
        
    ### Morningstar Cash Flow - Cash Flow Ratios                    ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet                    ###
    ### Ungültige Werte = NaN implementiert                         ###
    def morningstar_cashflow_ratios_df(self):
        
        data = self.data
        length = self.length
        
        if len(data) == 0:
            self.df_morningstar_cashflow_ratios = None
        else:
            self.df_morningstar_cashflow_ratios = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[187+length]), Morningstar_Key_Ratios.__data_list(data[193+length])
                                                 , Morningstar_Key_Ratios.__data_list(data[204+length]), Morningstar_Key_Ratios.__data_list(data[204+length])
                                                 , Morningstar_Key_Ratios.__data_list(data[208+length])]
                          , index =['Operating Cash Flow Growth % YOY', 'Free Cash Flow Growth % YOY', 'Cap Ex as a % of Sales'
                                    , 'Free Cash Flow/Sales %', 'Free Cash Flow/Net Income']
                          , columns =Morningstar_Key_Ratios.__data_list(data[181+length]))
    
        return self.df_morningstar_cashflow_ratios
    
    ### Morningstar Cash Flow - Balance Sheet Items (in %)          ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet                    ###
    ### Ungültige Werte = NaN implementiert                         ###
    def morningstar_finhealth_bs_df(self):
        
        data = self.data
        length = self.length
        
        if len(data) == 0:
            self.df_morningstar_finhealth_bs = None
        else:
            self.df_morningstar_finhealth_bs = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[223+length]), Morningstar_Key_Ratios.__data_list(data[225+length])
                                              , Morningstar_Key_Ratios.__data_list(data[226+length]), Morningstar_Key_Ratios.__data_list(data[229+length])
                                              , Morningstar_Key_Ratios.__data_list(data[232+length]), Morningstar_Key_Ratios.__data_list(data[234+length])
                                              , Morningstar_Key_Ratios.__data_list(data[235+length]), Morningstar_Key_Ratios.__data_list(data[238+length])
                                              , Morningstar_Key_Ratios.__data_list(data[240+length]), Morningstar_Key_Ratios.__data_list(data[242+length])
                                              , Morningstar_Key_Ratios.__data_list(data[244+length]), Morningstar_Key_Ratios.__data_list(data[246+length])
                                              , Morningstar_Key_Ratios.__data_list(data[248+length]), Morningstar_Key_Ratios.__data_list(data[251+length])
                                              , Morningstar_Key_Ratios.__data_list(data[254+length]), Morningstar_Key_Ratios.__data_list(data[256+length])
                                              , Morningstar_Key_Ratios.__data_list(data[259+length]), Morningstar_Key_Ratios.__data_list(data[261+length])
                                              , Morningstar_Key_Ratios.__data_list(data[264+length]), Morningstar_Key_Ratios.__data_list(data[268+length])]
                              , index =['Cash & Short-Term Investments', 'Accounts Receivable', 'Inventory', 'Other Current Assets'
                                        , 'Total Current Assets', 'Net PP&E', 'Intangibles', 'Other Long-Term Assets', 'Total Assets'
                                        , 'Accounts Payable', 'Short-Term Debt', 'Taxes Payable', 'Accrued Liabilities'
                                        , 'Other Short-Term Liabilities', 'Total Current Liabilities', 'Long-Term Debt', 'Other Long-Term Liabilities'
                                        ,'Total Liabilities', "Total Stockholder's Equity", 'Total Liabilities & Equity']
                              , columns = Morningstar_Key_Ratios.__data_list(data[218+length] + ' ' + data[219+length]))
    
        return self.df_morningstar_finhealth_bs
        
    ### Morningstar Cash Flow - Liquidity/Financial Health          ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet                    ###
    ### Ungültige Werte = NaN implementiert                         ###
    def morningstar_finhealth_health_df(self):
        
        data = self.data
        length = self.length
        
        if len(data) == 0:
            self.df_morningstar_finhealth_health = None
        else:
            self.df_morningstar_finhealth_health = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[273+length]), Morningstar_Key_Ratios.__data_list(data[275+length])
                                                  , Morningstar_Key_Ratios.__data_list(data[277+length]), Morningstar_Key_Ratios.__data_list(data[278+length])]
                              , index =['Current Ratio', 'Quick Ratio', 'Financial Leverage', 'Debt/Equity']
                              , columns = Morningstar_Key_Ratios.__data_list(data[270+length] + ' ' + data[271+length]))
        
        return self.df_morningstar_finhealth_health
    
    ### Morningstar Cash Flow - Efficiency                          ###
    ### e.g. http://financials.morningstar.com/ratios/r.html?t=NVDA ###
    ### Rückgabe None implementiert und getestet                    ###
    ### Ungültige Werte = NaN implementiert                         ###
    def morningstar_effiency_ratios_df(self):
        
        data = self.data
        length = self.length
        
        if len(data) == 0:
            self.df_morningstar_effiency_ratios = None
        else:
            self.df_morningstar_effiency_ratios = pd.DataFrame([Morningstar_Key_Ratios.__data_list(data[287+length]), Morningstar_Key_Ratios.__data_list(data[289+length])
                                                 , Morningstar_Key_Ratios.__data_list(data[291+length]), Morningstar_Key_Ratios.__data_list(data[294+length])
                                                 , Morningstar_Key_Ratios.__data_list(data[296+length]), Morningstar_Key_Ratios.__data_list(data[298+length])
                                                 , Morningstar_Key_Ratios.__data_list(data[301+length]), Morningstar_Key_Ratios.__data_list(data[303+length])]
                          , index =['Days Sales Outstanding', 'Days Inventory', 'Payables Period', 'Cash Conversion Cycle'
                                    , 'Receivables Turnover', 'Inventory Turnover', 'Fixed Assets Turnover', 'Asset Turnover']
                          , columns = Morningstar_Key_Ratios.__data_list(data[284+length]))
    
        return self.df_morningstar_effiency_ratios
    
    def __data_list(string):
        if '"' in string:
            substrings = []
            for s_quote_mark in string.split('"'):
                if len(s_quote_mark)>0: 
                    if s_quote_mark[0]=="," or s_quote_mark[-1]=="," or s_quote_mark==string:
                        for s_comma in s_quote_mark.split(','):
                            if len(s_comma)>0:
                                substrings.append(s_comma)
                            #else:
                            #    substrings.append(None)
                    else:
                        substrings.append(s_quote_mark)
        else: 
            substrings = string.split(',')
    
            for n, i in enumerate(substrings):
	            if len(substrings[n]) == 0:
		            substrings[n] = np.nan
        
        del substrings[0]
    
        return substrings
    
    def __index(string):
        string = string.split(',')
        return string[0]