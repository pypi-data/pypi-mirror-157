# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 18:08:08 2022

@author: RobWen
Version: 0.3.2
"""
# Packages
from StockHero.Ticker_Sources.gurufocus import Gurufocus
#from StockHero.Ticker_Sources.morningstar_key_ratios import Morningstar_Key_Ratios
from StockHero.Ticker_Sources.morningstar_quote import Morningstar_Quote
from StockHero.Ticker_Sources.nasdaq import Nasdaq
from StockHero.Ticker_Sources.yahoo import Yahoo

    ##############
    ###        ###
    ###  Data  ###
    ###        ###
    ##############

class Ticker:
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.headers_standard = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"}
    
    def __repr__(self):
        return(self.ticker)
        
    def __str__(self):
        return(self.ticker)
        #return(self.ticker or '') # by None
       
    #####################
    ###               ###
    ###  Morningstar  ###
    ###               ###
    #####################
    
    ''' Down since 23.06.2022
    
    @property
    def morningstar_financials(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_financials_df()
    
    @property
    def morningstar_marginofsales(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_margins_of_sales_df()
    
    @property
    def morningstar_profitability(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_profitability_df()
    
    @property
    def morningstar_growth_rev(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_growth_revenue_df()
    
    @property
    def morningstar_growth_op_inc(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_growth_operating_income_df()
    
    @property
    def morningstar_growth_net_inc(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_growth_net_income_df()
    
    @property
    def morningstar_growth_eps(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_growth_eps_df()
    
    @property
    def morningstar_cf_ratios(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_cashflow_ratios_df()
    
    @property
    def morningstar_bs(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_finhealth_bs_df()
    
    @property
    def morningstar_li_fin(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_finhealth_health_df()
    
    @property
    def morningstar_efficiency(self):
        self.morningstar_data = Morningstar_Key_Ratios(self.ticker, self.headers_standard)
        return self.morningstar_data.morningstar_effiency_ratios_df()
    '''
    
    @property
    def morningstar_quote(self):
        self.morningstar_quote_data = Morningstar_Quote(self.ticker, self.headers_standard)
        return self.morningstar_quote_data.morningstar_quote_df()
    
    ################
    ###          ###
    ###  NASDAQ  ###
    ###          ###
    ################
    
    @property
    def nasdaq_summ(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_summary_df()
    
    @property
    def nasdaq_div_hist(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_dividend_history_df()
    
    @property
    def nasdaq_hist_quotes_stock(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_historical_data_stock_df()
    
    @property
    def nasdaq_hist_quotes_etf(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_historical_data_etf_df()
    
    @property
    def nasdaq_hist_nocp(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_historical_nocp_df()
    
    @property
    def nasdaq_fin_income_statement_y(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_financials_income_statement_y_df()
    
    @property
    def nasdaq_fin_balance_sheet_y(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_financials_balance_sheet_y_df()
    
    @property
    def nasdaq_fin_cash_flow_y(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_financials_cash_flow_y_df()
    
    @property
    def nasdaq_fin_fin_ratios_y(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_financials_financials_ratios_y_df()
    
    @property
    def nasdaq_fin_income_statement_q(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_financials_income_statement_q_df()
    
    @property
    def nasdaq_fin_balance_sheet_q(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_financials_balance_sheet_q_df()
    
    @property
    def nasdaq_fin_cash_flow_q(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_financials_cash_flow_q_df()
    
    @property
    def nasdaq_fin_fin_ratios_q(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_financials_financials_ratios_q_df()
    
    @property
    def nasdaq_earn_date_eps(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_earnings_date_eps_df()
    
    @property
    def nasdaq_earn_date_surprise(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_earnings_date_surprise_df()
    
    @property
    def nasdaq_yearly_earn_forecast(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_earnings_date_yearly_earnings_forecast_df()
    
    @property
    def nasdaq_quarterly_earn_forecast(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.nasdaq_earnings_date_quarterly_earnings_forecast_df()
    
    @property
    def nasdaq_pe_peg_forecast(self):
        self.nasdaq_data = Nasdaq(self.ticker, self.headers_standard)
        return self.nasdaq_data.forecast_pe_peg_df()
    
    #######################
    ###                 ###
    ###  Yahoo Finance  ###
    ###                 ###
    #######################

    @property
    def yahoo_statistics(self):
        self.yahoo_data = Yahoo(self.ticker, self.headers_standard)
        return self.yahoo_data.yahoo_statistics_abfrage()
    
    @property
    def yahoo_statistics_p(self):
        self.yahoo_data = Yahoo(self.ticker, self.headers_standard)
        return self.yahoo_data.yahoo_statistics_df_p()
    '''
    @property
    def yahoo_query(self):
        self.yahoo_data = Yahoo(self.ticker, self.headers_standard)
        return self.yahoo_data.yahoo_query_df()
    '''
    #####################
    ###               ###
    ###  Gurufocus    ###
    ###               ###
    #####################
    
    @property
    def gurufocus_pe_ratio_av(self):
        self.gurufocus_data = Gurufocus(self.ticker, self.headers_standard)
        #self.gurufocus_data = Ticker_Sources.gurufocus.Gurufocus(self.ticker, self.headers_standard) lokal
        return self.gurufocus_data.gurufocus_pe_ratio_av_v()
    
    @property
    def gurufocus_debt_to_ebitda(self):
        self.gurufocus_data = Gurufocus(self.ticker, self.headers_standard)
        return self.gurufocus_data.gurufocus_debt_to_ebitda()


###############################################################################
###############################################################################
