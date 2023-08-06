# -*- coding: utf-8 -*-

from hbshare.fe.asset_allocation.data_loader import Loader
from hbshare.fe.common.util.exception import InputParameterError
from hbshare.fe.common.util.logger import logger
from hbshare.fe.common.util.verifier import verify_type
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


class RiskParity:
    def __init__(self, asset_type, asset_list, start_date, end_date, window, is_reblance, reblance_type, n, frequency, lb_list=None, ub_list=None, total_weight=1.0):
        self.asset_type = asset_type
        self.asset_list = asset_list
        self.start_date = start_date
        self.end_date = end_date
        self.window = window
        self.start_date_backup = (datetime.strptime(start_date, '%Y%m%d') - timedelta(self.window * 2)).strftime('%Y%m%d')
        self.is_reblance = is_reblance
        self.reblance_type = reblance_type
        self.n = n
        self.frequency = frequency
        self.lb_list = lb_list if lb_list is not None else [0.0] * len(self.asset_list)
        self.ub_list = ub_list if ub_list is not None else [1.0] * len(self.asset_list)
        self.total_weight = total_weight
        self._verify_input_param()
        self._load()

    def _verify_input_param(self):
        verify_type(self.asset_type, 'asset_type', str)
        verify_type(self.asset_list, 'asset_list', list)
        verify_type(self.start_date, 'start_date', str)
        verify_type(self.end_date, 'end_date', str)
        verify_type(self.window, 'window', int)
        verify_type(self.is_reblance, 'is_reblance', bool)
        verify_type(self.reblance_type, 'reblance_type', str)
        verify_type(self.n, 'n', int)
        verify_type(self.frequency, 'frequency', str)
        verify_type(self.lb_list, 'lb_list', list)
        verify_type(self.ub_list, 'ub_list', list)
        verify_type(self.total_weight, 'total_weight', float)
        if self.asset_type not in ['mutual_index', 'private_index', 'market_index', 'mutual_fund', 'private_fund']:
            msg = "asset_type not supported, check your input"
            logger.error(msg)
            raise InputParameterError(message=msg)
        if len(self.asset_list) == 0:
            msg = "asset_list is empty, check your input"
            logger.error(msg)
            raise InputParameterError(message=msg)
        if self.window <= 0:
            msg = "window must be larger than 0, check your input"
            logger.error(msg)
            raise InputParameterError(message=msg)
        if self.reblance_type not in ['初始权重', '初始投资目标']:
            msg = "reblance_type not supported, check your input"
            logger.error(msg)
            raise InputParameterError(message=msg)
        if self.n <= 0:
            msg = "n must be larger than 0, check your input"
            logger.error(msg)
        if self.frequency not in ['day', 'week', 'month', 'quarter', 'year']:
            msg = "frequency not supported, check your input"
            logger.error(msg)
            raise InputParameterError(message=msg)
        if len(self.lb_list) != len(self.asset_list) or len(self.ub_list) != len(self.asset_list):
            msg = "lb_list or ub_list are not the same length with asset_list, check your input"
            logger.error(msg)
            raise InputParameterError(message=msg)
        if not (self.total_weight >= 0.0 and self.total_weight <= 1.0):
            msg = "total_weight must be between 0 and 1, check your input"
            logger.error(msg)
            raise InputParameterError(message=msg)
        if len([i for i in self.lb_list if (i >= 0.0 and i <= 1.0)]) != len(self.asset_list):
            msg = "lb must be between 0 and 1, check your input"
            logger.error(msg)
            raise InputParameterError(message=msg)
        if len([i for i in self.ub_list if (i >= 0.0 and i <= 1.0)]) != len(self.asset_list):
            msg = "ub must be between 0 and 1, check your input"
            logger.error(msg)
            raise InputParameterError(message=msg)

    def _load(self):
        self.calendar_df = Loader().read_cal(self.start_date_backup, self.end_date)
        self.calendar_df = self.calendar_df.rename(columns={'JYRQ': 'CALENDAR_DATE', 'SFJJ': 'IS_OPEN', 'SFZM': 'IS_WEEK_END', 'SFYM': 'IS_MONTH_END'})
        self.calendar_df['CALENDAR_DATE'] = self.calendar_df['CALENDAR_DATE'].astype(str)
        self.calendar_df = self.calendar_df.sort_values('CALENDAR_DATE')
        self.calendar_df['IS_OPEN'] = self.calendar_df['IS_OPEN'].astype(int).replace({0: 1, 1: 0})
        self.calendar_df['IS_WEEK_END'] = self.calendar_df['IS_WEEK_END'].fillna(0).astype(int)
        self.calendar_df['IS_MONTH_END'] = self.calendar_df['IS_MONTH_END'].fillna(0).astype(int)
        self.calendar_df['YEAR_MONTH'] = self.calendar_df['CALENDAR_DATE'].apply(lambda x: x[:6])
        self.calendar_df['MONTH'] = self.calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:6])
        self.calendar_df['MONTH_DAY'] = self.calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:])
        self.calendar_df['IS_QUARTER_END'] = np.where((self.calendar_df['IS_MONTH_END'] == 1) & (self.calendar_df['MONTH'].isin(['03', '06', '09', '12'])), 1, 0)
        self.calendar_df['IS_QUARTER_END'] = self.calendar_df['IS_QUARTER_END'].astype(int)
        self.calendar_df['IS_SEASON_END'] = np.where(self.calendar_df['MONTH_DAY'].isin(['0331', '0630', '0930', '1231']), 1, 0)
        self.calendar_df['IS_SEASON_END'] = self.calendar_df['IS_SEASON_END'].astype(int)
        trade_cal = self.calendar_df[self.calendar_df['IS_OPEN'] == 1]
        trade_cal['TRADE_DATE'] = trade_cal['CALENDAR_DATE']
        self.calendar_df = self.calendar_df.merge(trade_cal[['CALENDAR_DATE', 'TRADE_DATE']], on=['CALENDAR_DATE'], how='left')
        self.calendar_df['TRADE_DATE'] = self.calendar_df['TRADE_DATE'].fillna(method='ffill')
        self.calendar_df = self.calendar_df[['CALENDAR_DATE', 'IS_OPEN', 'IS_WEEK_END', 'IS_MONTH_END', 'IS_QUARTER_END', 'IS_SEASON_END', 'TRADE_DATE', 'YEAR_MONTH', 'MONTH', 'MONTH_DAY']]

        if self.asset_type == 'mutual_index':
            self.nav_df = Loader().read_mutual_index_daily_k_given_indexs(self.asset_list, self.start_date_backup, self.end_date)
            self.nav_df = self.nav_df[['INDEX_CODE', 'TRADE_DATE', 'CLOSE_INDEX']] if len(self.nav_df) != 0 else pd.DataFrame(columns=['INDEX_CODE', 'TRADE_DATE', 'CLOSE_INDEX'])
            self.nav_df = self.nav_df.drop_duplicates()
            self.nav_df['TRADE_DATE'] = self.nav_df['TRADE_DATE'].astype(str)
            self.nav_df = self.nav_df.pivot(index='TRADE_DATE', columns='INDEX_CODE', values='CLOSE_INDEX')
            self.nav_df = self.nav_df.sort_index()
        if self.asset_type == 'private_index':
            self.nav_df = Loader().read_private_index_daily_k_given_indexs(self.asset_list, self.start_date_backup[:6], self.end_date[:6])
            self.nav_df = self.nav_df[['INDEX_CODE', 'TRADE_MONTH', 'CLOSE_INDEX']] if len(self.nav_df) != 0 else pd.DataFrame(columns=['INDEX_CODE', 'TRADE_MONTH', 'CLOSE_INDEX'])
            self.nav_df = self.nav_df.drop_duplicates()
            self.nav_df['TRADE_MONTH'] = self.nav_df['TRADE_MONTH'].astype(str)
            self.nav_df = self.nav_df.merge(self.calendar_df[self.calendar_df['IS_MONTH_END'] == 1][['YEAR_MONTH', 'TRADE_DATE']].rename(columns={'YEAR_MONTH': 'TRADE_MONTH'}), on=['TRADE_MONTH'], how='left')
            self.nav_df = self.nav_df.pivot(index='TRADE_DATE', columns='INDEX_CODE', values='CLOSE_INDEX')
            self.nav_df = self.nav_df.sort_index()
        if self.asset_type == 'market_index':
            self.nav_df = Loader().read_market_index_daily_k_given_indexs(self.asset_list, self.start_date_backup, self.end_date)
            self.nav_df = self.nav_df[['INDEX_CODE', 'TRADE_DATE', 'CLOSE_INDEX']] if len(self.nav_df) != 0 else pd.DataFrame(columns=['INDEX_CODE', 'TRADE_DATE', 'CLOSE_INDEX'])
            self.nav_df = self.nav_df.drop_duplicates()
            self.nav_df['TRADE_DATE'] = self.nav_df['TRADE_DATE'].astype(str)
            self.nav_df = self.nav_df.pivot(index='TRADE_DATE', columns='INDEX_CODE', values='CLOSE_INDEX')
            self.nav_df = self.nav_df.sort_index()
        if self.asset_type == 'mutual_fund':
            self.nav_df = Loader().read_mutual_fund_cumret_given_codes(self.asset_list, self.start_date_backup, self.end_date)
            self.nav_df = self.nav_df[['FUND_CODE', 'TRADE_DATE', 'CUM_RET']] if len(self.nav_df) != 0 else pd.DataFrame(columns=['FUND_CODE', 'TRADE_DATE', 'CUM_RET'])
            self.nav_df = self.nav_df.drop_duplicates()
            self.nav_df['TRADE_DATE'] = self.nav_df['TRADE_DATE'].astype(str)
            self.nav_df = self.nav_df.pivot(index='TRADE_DATE', columns='FUND_CODE', values='CUM_RET')
            self.nav_df = self.nav_df.sort_index()
            self.nav_df = 0.01 * self.nav_df + 1
        if self.asset_type == 'private_fund':
            self.nav_df = Loader().read_private_fund_adj_nav_given_codes(self.asset_list, self.start_date_backup, self.end_date)
            self.nav_df = self.nav_df[['FUND_CODE', 'TRADE_DATE', 'ADJ_NAV']] if len(self.nav_df) != 0 else pd.DataFrame(columns=['FUND_CODE', 'TRADE_DATE', 'ADJ_NAV'])
            self.nav_df = self.nav_df.drop_duplicates()
            self.nav_df['TRADE_DATE'] = self.nav_df['TRADE_DATE'].astype(str)
            self.nav_df = self.nav_df.pivot(index='TRADE_DATE', columns='FUND_CODE', values='ADJ_NAV')
            self.nav_df = self.nav_df.sort_index()
        return

    def get_all(self):
        return




if __name__ == '__main__':
    # mutual_index: ['HM0001', 'HM0024', 'HM0095']
    # private_index: ['HB0000', 'HB0016', 'HB1001']
    # market_index: ['000300', '000906', 'CBA00301']
    # mutual_fund: ['002943', '688888', '000729']
    # private_fund: ['SGK768', 'SX8958', 'SR4480']

    RiskParity(asset_type='market_index',
               asset_list=['000300', '000906', 'CBA00301'],
               start_date='20211231',
               end_date='20220704',
               window=60,
               is_reblance=True,
               reblance_type='初始投资目标',
               n=3,
               frequency='month').get_all()