# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.fedb import FEDB
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from hbshare.fe.xwq.analysis.service.industry_analysis_data import get_stock_info
from datetime import datetime
from scipy import stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style('white', {'font.sans-serif': ['simhei', 'Arial']})
line_color_list = ['#F04950', '#6268A2', '#959595', '#333335', '#EE703F', '#7E4A9B', '#8A662C',
                   '#44488E', '#BA67E9', '#3FAEEE']
bar_color_list = ['#C94649', '#EEB2B4', '#E1777A', '#D57C56', '#E39A79', '#DB8A66', '#E5B88C',
                  '#8588B7', '#B4B6D1', '#55598D', '#628497', '#A9C6CB', '#866EA9', '#B79BC7',
                  '#7D7D7E', '#CACACA', '#A7A7A8', '#606063', '#C4C4C4', '#99999B', '#B7B7B7']
industry_theme_dic = {'银行': '大金融', '非银金融': '大金融', '房地产': '大金融',
                      '食品饮料': '消费', '家用电器': '消费', '医药生物': '消费', '社会服务': '消费', '农林牧渔': '消费', '商贸零售': '消费', '美容护理': '消费',
                      '通信': 'TMT', '计算机': 'TMT', '电子': 'TMT', '传媒': 'TMT', '国防军工': 'TMT',
                      '交通运输': '制造', '机械设备': '制造', '汽车': '制造', '纺织服饰': '制造', '轻工制造': '制造', '电力设备': '制造',
                      '钢铁': '周期', '有色金属': '周期', '建筑装饰': '周期', '建筑材料': '周期', '基础化工': '周期', '石油石化': '周期', '煤炭': '周期', '公用事业': '周期', '环保': '周期',
                      '综合': '其他'}

def get_industry_info():
    industry_info = HBDB().read_industry_info()
    industry_info = industry_info.rename(columns={'flmc': 'INDUSTRY_NAME', 'zsdm': 'INDUSTRY_ID', 'hyhfbz': 'INDUSTRY_VERSION', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS'})
    industry_info = industry_info.dropna(subset=['BEGIN_DATE'])
    industry_info['END_DATE'] = industry_info['END_DATE'].replace('', np.nan).fillna('20990101')
    industry_info['BEGIN_DATE'] = industry_info['BEGIN_DATE'].apply(lambda x: datetime.strptime(x, '%Y/%m/%d').strftime('%Y%m%d') if '/' in x else x)
    industry_info['END_DATE'] = industry_info['END_DATE'].apply(lambda x: datetime.strptime(x, '%Y/%m/%d').strftime('%Y%m%d') if '/' in x else x)
    industry_info['BEGIN_DATE'] = industry_info['BEGIN_DATE'].astype(int).astype(str)
    industry_info['END_DATE'] = industry_info['END_DATE'].astype(int).astype(str)
    industry_info['INDUSTRY_VERSION'] = industry_info['INDUSTRY_VERSION'].astype(int)
    industry_info['INDUSTRY_TYPE'] = industry_info['INDUSTRY_TYPE'].astype(int)
    industry_info['IS'] = industry_info['IS'].astype(int)
    industry_info = industry_info[industry_info['INDUSTRY_VERSION'] == 3]
    return industry_info

class IndustryAnalysis:
    def __init__(self, file_path, start_date, end_date, last_report_date, report_date, sw_type, select_industry=[]):
        self.file_path = file_path
        self.start_date = start_date
        self.end_date = end_date
        self.sw_type = sw_type
        self.last_report_date = last_report_date
        self.report_date = report_date

        self.industry_info = get_industry_info()
        self.industry_info = self.industry_info[self.industry_info['INDUSTRY_TYPE'] == self.sw_type]
        self.industry_info = self.industry_info[self.industry_info['IS'] == 1]
        self.industry_info = self.industry_info[['INDUSTRY_NAME', 'INDUSTRY_ID', 'BEGIN_DATE', 'END_DATE']]
        self.industry_id_name_dic = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']].set_index('INDUSTRY_ID')['INDUSTRY_NAME'].to_dict()
        self.industry_name_id_dic = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']].set_index('INDUSTRY_NAME')['INDUSTRY_ID'].to_dict()
        self.select_industry = self.industry_info['INDUSTRY_NAME'].unique().tolist() if len(select_industry) == 0 else select_industry

    def IndustryMarketValue(self):
        ind_mv = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'MARKET_VALUE'], 'industry_technology', self.sw_type)
        ind_mv = ind_mv[ind_mv['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_mv['MARKET_VALUE'] = ind_mv['MARKET_VALUE'].apply(lambda x: round(x / 10000000000.0, 2))
        ind_mv = ind_mv.pivot(index='INDUSTRY_NAME', columns='REPORT_DATE', values='MARKET_VALUE')
        date_list = sorted(list(ind_mv.columns))[-12:]
        rank_list = list(ind_mv[max(date_list)].sort_values(ascending=False).index)
        ind_mv = ind_mv.reset_index()
        ind_mv['INDUSTRY_NAME'] = ind_mv['INDUSTRY_NAME'].astype('category')
        ind_mv['INDUSTRY_NAME'].cat.reorder_categories(rank_list, inplace=True)
        ind_mv = ind_mv.sort_values('INDUSTRY_NAME')
        ind_mv = ind_mv.set_index('INDUSTRY_NAME')[date_list]
        #####画热力图#####
        plt.figure(figsize=(12, 8))
        sns.heatmap(ind_mv, annot=True, fmt='.2f', cmap='OrRd')
        plt.xlabel('')
        plt.ylabel('行业市值（百亿）')
        plt.tight_layout()
        plt.savefig('{0}market_value_heatmap.png'.format(self.file_path))
        return

    def IndustryRet(self):
        ind_ret = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'RET'], 'industry_technology', self.sw_type)
        ind_ret = ind_ret[ind_ret['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_ret['RET'] = ind_ret['RET'].apply(lambda x: round(x * 100.0, 2))
        ind_ret = ind_ret.pivot(index='INDUSTRY_NAME', columns='REPORT_DATE', values='RET')
        date_list = sorted(list(ind_ret.columns))[-12:]
        rank_list = list(ind_ret[max(date_list)].sort_values(ascending=False).index)
        ind_ret = ind_ret.reset_index()
        ind_ret['INDUSTRY_NAME'] = ind_ret['INDUSTRY_NAME'].astype('category')
        ind_ret['INDUSTRY_NAME'].cat.reorder_categories(rank_list, inplace=True)
        ind_ret = ind_ret.sort_values('INDUSTRY_NAME')
        ind_ret = ind_ret.set_index('INDUSTRY_NAME')[date_list]
        #####画热力图#####
        plt.figure(figsize=(12, 8))
        sns.heatmap(ind_ret, annot=True, fmt='.2f', cmap='OrRd')
        plt.xlabel('')
        plt.ylabel('行业季度涨跌幅（%）')
        plt.tight_layout()
        plt.savefig('{0}ret_heatmap.png'.format(self.file_path))
        return

    def IndustryTech(self):
        ind_tech = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'RET', 'VOL', 'BETA', 'ALPHA'], 'industry_technology', self.sw_type)
        ind_tech = ind_tech[ind_tech['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_tech['RET'] = ind_tech['RET'].apply(lambda x: round(x * 100.0, 2))
        ind_tech['VOL'] = ind_tech['VOL'].apply(lambda x: round(x * 100.0, 2))
        ind_tech['BETA'] = ind_tech['BETA'].apply(lambda x: round(x, 2))
        ind_tech['ALPHA'] = ind_tech['ALPHA'].apply(lambda x: round(x * 100.0, 2))
        #####画热力图#####
        fig, ax = plt.subplots(2, 2, figsize=(30, 20))
        tech_list = [['RET', 'VOL'], ['BETA', 'ALPHA']]
        for i in range(2):
            for j in range(2):
                ind_item = ind_tech.pivot(index='INDUSTRY_NAME', columns='REPORT_DATE', values=tech_list[i][j])
                date_list = sorted(list(ind_item.columns))[-12:]
                rank_list = list(ind_item[max(date_list)].sort_values(ascending=False).index)
                ind_item = ind_item.reset_index()
                ind_item['INDUSTRY_NAME'] = ind_item['INDUSTRY_NAME'].astype('category')
                ind_item['INDUSTRY_NAME'].cat.reorder_categories(rank_list, inplace=True)
                ind_item = ind_item.sort_values('INDUSTRY_NAME')
                ind_item = ind_item.set_index('INDUSTRY_NAME')[date_list]
                ylabel = '涨跌幅（%）' if tech_list[i][j] == 'RET' else '波动率（%）' if tech_list[i][j] == 'VOL' else 'BETA' if tech_list[i][j] == 'BETA' else 'ALPHA（%）'
                axij = sns.heatmap(ind_item, ax=ax[i][j], annot=True, fmt='.2f', cmap='OrRd')
                axij.set_xlabel('')
                axij.set_ylabel(ylabel)
        plt.tight_layout()
        plt.savefig('{0}tech_heatmap.png'.format(self.file_path))
        return

    def IndustryNewhigh(self):
        ind_newhigh = pd.read_excel('D:/Git/hbshare/hbshare/fe/xwq/data/new_high/2022年创历史新高个股汇总.xlsx', index_col=0)
        ind_newhigh['股票代码'] = ind_newhigh['股票代码'].apply(lambda x: str(x).zfill(6))
        ind_newhigh['创新高日期'] = ind_newhigh['创新高日期'].apply(lambda x: str(x))
        stock_info = get_stock_info()[['TICKER_SYMBOL', 'SAMPLE_DATE']].rename(columns={'TICKER_SYMBOL': '股票代码', 'SAMPLE_DATE': '入选样本日期'})
        ind_newhigh = ind_newhigh.merge(stock_info, on=['股票代码'], how='inner')
        ind_newhigh = ind_newhigh[ind_newhigh['创新高日期'] >= ind_newhigh['入选样本日期']]
        ind_newhigh = ind_newhigh.reset_index().drop(['index', '入选样本日期'], axis=1)
        ind_newhigh = ind_newhigh[ind_newhigh['创新高日期'] <= '20220331']
        ind_newhigh = ind_newhigh.sort_values(['股票代码', '创新高日期']).drop_duplicates('股票代码', keep='first')
        ind_newhigh = ind_newhigh.sort_values(['申万一级行业', '股票代码'])
        ind_newhigh = ind_newhigh.reset_index().drop(['index', '创新高日期', '区间内首次创新高', '区间内收盘价最高', '收盘价格'], axis=1)
        ind_newhigh = ind_newhigh[['申万一级行业', '股票代码']].groupby('申万一级行业').count().rename(columns={'股票代码': '创新高数量'})
        ind_newhigh = ind_newhigh.reindex(self.select_industry).fillna(0.0)
        ind_newhigh = ind_newhigh.reset_index().sort_values('创新高数量', ascending=False)
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='申万一级行业', y='创新高数量', data=ind_newhigh, palette=[bar_color_list[0]])
        plt.xlabel('')
        plt.ylabel('创新高个股数量')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig('{0}new_high_bar.png'.format(self.file_path))
        return

    def IndustryVal(self):
        # ind_pe_latest['PE_TTM_RANGE'] = ind_pe_latest['PE_TTM'].apply(lambda x: '0<PE_TTM<=10' if (x > 0 and x <= 10) else
        #                                                                         '10<PE_TTM<=20' if (x > 10 and x <= 20) else
        #                                                                         '20<PE_TTM<=30' if (x > 20 and x <= 30) else
        #                                                                         '30<PE_TTM<=40' if (x > 30 and x <= 40) else
        #                                                                         '40<PE_TTM<=50' if (x > 40 and x <= 50) else
        #                                                                         'PE_TTM>50（含负）')
        # pe_list = [['0<PE_TTM<=10', '10<PE_TTM<=20'], ['20<PE_TTM<=30', '30<PE_TTM<=40'], ['40<PE_TTM<=50', 'PE_TTM>50（含负）']]
        # #####画时序图#####
        # fig, ax = plt.subplots(3, 2, figsize=(90, 20))
        # for i in range(3):
        #     for j in range(2):
        #         ind_list = ind_pe_latest[ind_pe_latest['PE_TTM_RANGE'] == pe_list[i][j]]['INDUSTRY_NAME'].unique().tolist()
        #         for ind in ind_list:
        #             ind_pe_ind = ind_pe[ind_pe['INDUSTRY_NAME'] == ind].sort_values('TRADE_DATE')
        #             ax[i][j].plot(ind_pe_ind['TRADE_DATE'], ind_pe_ind['PE_TTM'], label=ind)
        #             ax[i][j].set_xlabel('最新估值区间：{0}'.format(pe_list[i][j]))
        #             ax[i][j].set_ylabel('PE_TTM')
        #             ax[i][j].legend(loc=1)
        # plt.tight_layout()
        # plt.savefig('{0}pe_ts.png'.format(self.file_path))

        ind_pe = FEDB().read_industry_data(['TRADE_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'PE_TTM'], 'industry_daily_valuation', self.sw_type)
        ind_pe = ind_pe[ind_pe['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_pe_latest = ind_pe[ind_pe['TRADE_DATE'] == ind_pe['TRADE_DATE'].max()]
        ind_pe_min = ind_pe[['INDUSTRY_NAME', 'PE_TTM']].groupby('INDUSTRY_NAME').min().reset_index().rename(columns={'PE_TTM': 'PE_TTM_MIN'})
        ind_pe_mean = ind_pe[['INDUSTRY_NAME', 'PE_TTM']].groupby('INDUSTRY_NAME').mean().reset_index().rename(columns={'PE_TTM': 'PE_TTM_MEAN'})
        ind_pe_median = ind_pe[['INDUSTRY_NAME', 'PE_TTM']].groupby('INDUSTRY_NAME').median().reset_index().rename(columns={'PE_TTM': 'PE_TTM_MEDIAN'})
        ind_pe_max = ind_pe[['INDUSTRY_NAME', 'PE_TTM']].groupby('INDUSTRY_NAME').max().reset_index().rename(columns={'PE_TTM': 'PE_TTM_MAX'})
        ind_pe_quantile = ind_pe[['INDUSTRY_NAME', 'TRADE_DATE', 'PE_TTM']].groupby('INDUSTRY_NAME').apply(lambda x: stats.percentileofscore(x['PE_TTM'], x.sort_values('TRADE_DATE')['PE_TTM'].iloc[-1]))
        ind_pe_quantile = pd.DataFrame(ind_pe_quantile).reset_index().rename(columns={0: 'PE_TTM_QUANTILE'})
        ind_pe_disp = ind_pe_latest.merge(ind_pe_min, on=['INDUSTRY_NAME'], how='left') \
                                   .merge(ind_pe_mean, on=['INDUSTRY_NAME'], how='left') \
                                   .merge(ind_pe_median, on=['INDUSTRY_NAME'], how='left') \
                                   .merge(ind_pe_max, on=['INDUSTRY_NAME'], how='left') \
                                   .merge(ind_pe_quantile, on=['INDUSTRY_NAME'], how='left')
        ind_pe_disp = ind_pe_disp.sort_values('PE_TTM_QUANTILE')
        for col in ['PE_TTM', 'PE_TTM_QUANTILE', 'PE_TTM_MIN', 'PE_TTM_MEAN', 'PE_TTM_MEDIAN', 'PE_TTM_MAX']:
            ind_pe_disp[col] = ind_pe_disp[col].apply(lambda x: round(x, 2))
        ind_pe_disp['PE_TTM_QUANTILE'] = ind_pe_disp['PE_TTM_QUANTILE'].apply(lambda x: '{0}%'.format(x))
        ind_pe_disp = ind_pe_disp[['INDUSTRY_NAME', 'PE_TTM', 'PE_TTM_QUANTILE', 'PE_TTM_MIN', 'PE_TTM_MEAN', 'PE_TTM_MEDIAN', 'PE_TTM_MAX']]
        ind_pe_disp.columns = ['行业名称', 'PE_TTM', '分位水平', '最小值', '平均值', '中位数', '最大值']
        ind_pe_disp.to_excel('{0}pe_disp.xlsx'.format(self.file_path))

        ind_pe = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'PE_TTM'], 'industry_valuation', self.sw_type)
        ind_pe = ind_pe[ind_pe['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_pe['PE_TTM'] = ind_pe['PE_TTM'].apply(lambda x: round(x, 2))
        ind_pe = ind_pe[ind_pe['REPORT_DATE'].isin([self.last_report_date, self.report_date])]
        ind_pe = ind_pe.sort_values(['REPORT_DATE', 'PE_TTM'], ascending=[False, True])
        ind_pe = ind_pe[['REPORT_DATE', 'INDUSTRY_NAME', 'PE_TTM']]
        ind_pe.columns = ['报告日期', '行业名称', 'PE_TTM']
        rank_list = [self.last_report_date, self.report_date]
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='PE_TTM', data=ind_pe, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[7], bar_color_list[0]])
        plt.xlabel('')
        plt.ylabel('PE_TTM')
        plt.xticks(rotation=90)
        plt.legend(loc=2)
        plt.tight_layout()
        plt.savefig('{0}pe_ttm_bar.png'.format(self.file_path))

        ind_pb = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'PB_LF'], 'industry_valuation', self.sw_type)
        ind_pb = ind_pb[ind_pb['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_pb['PB_LF'] = ind_pb['PB_LF'].apply(lambda x: round(x, 2))
        ind_pb = ind_pb[ind_pb['REPORT_DATE'].isin([self.last_report_date, self.report_date])]
        ind_pb = ind_pb.sort_values(['REPORT_DATE', 'PB_LF'], ascending=[False, True])
        ind_pb = ind_pb[['REPORT_DATE', 'INDUSTRY_NAME', 'PB_LF']]
        ind_pb.columns = ['报告日期', '行业名称', 'PB_LF']
        rank_list = [self.last_report_date, self.report_date]
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='PB_LF', data=ind_pb, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[7], bar_color_list[0]])
        plt.xlabel('')
        plt.ylabel('PB_LF')
        plt.xticks(rotation=90)
        plt.legend(loc=2)
        plt.tight_layout()
        plt.savefig('{0}pb_lf_bar.png'.format(self.file_path))

        ind_val = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'PE_TTM', 'PB_LF'], 'industry_valuation', self.sw_type)
        ind_val = ind_val[ind_val['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_val['PE_TTM'] = ind_val['PE_TTM'].apply(lambda x: round(x, 2))
        ind_val['PB_LF'] = ind_val['PB_LF'].apply(lambda x: round(x, 2))
        #####画热力图#####
        fig, ax = plt.subplots(1, 2, figsize=(30, 10))
        val_list = ['PE_TTM', 'PB_LF']
        for i in range(2):
            ind_item = ind_val.pivot(index='INDUSTRY_NAME', columns='REPORT_DATE', values=val_list[i])
            date_list = sorted(list(ind_item.columns))[-12:]
            rank_list = list(ind_item[max(date_list)].sort_values(ascending=False).index)
            ind_item = ind_item.reset_index()
            ind_item['INDUSTRY_NAME'] = ind_item['INDUSTRY_NAME'].astype('category')
            ind_item['INDUSTRY_NAME'].cat.reorder_categories(rank_list, inplace=True)
            ind_item = ind_item.sort_values('INDUSTRY_NAME')
            ind_item = ind_item.set_index('INDUSTRY_NAME')[date_list]
            axi = sns.heatmap(ind_item, ax=ax[i], annot=True, fmt='.2f', cmap='OrRd')
            axi.set_xlabel('')
            axi.set_ylabel(val_list[i])
        plt.tight_layout()
        plt.savefig('{0}val_heatmap.png'.format(self.file_path))
        return

    def IndustryFmt(self):
        date_list = ['20191231', '20201231', '20210331', '20210630', '20210930', '20211231', '20220331']
        ind_fmt = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'NET_PROFIT_ACCUM_YOY'], 'industry_fundamental_derive', self.sw_type)
        ind_fmt = ind_fmt[ind_fmt['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_fmt = ind_fmt[ind_fmt['REPORT_DATE'].isin(date_list)]
        ind_fmt = ind_fmt.pivot(index='INDUSTRY_NAME', columns='REPORT_DATE', values='NET_PROFIT_ACCUM_YOY').reset_index()
        ind_fmt['THEME'] = ind_fmt['INDUSTRY_NAME'].apply(lambda x: industry_theme_dic[x])
        ind_fmt['THEME'] = ind_fmt['THEME'].astype('category')
        ind_fmt['THEME'].cat.reorder_categories(['周期', '制造', '消费', '大金融', 'TMT', '其他'], inplace=True)
        ind_fmt = ind_fmt.sort_values(['THEME', self.report_date], ascending=[True, False])
        for date in date_list:
            ind_fmt[date] = ind_fmt[date].apply(lambda x: '{0}%'.format(round(x * 100.0, 2)))
        ind_fmt = ind_fmt[['THEME', 'INDUSTRY_NAME'] + date_list]
        ind_fmt.columns = ['主题', '行业', '2019A', '2020A', '2021Q1', '2021Q2', '2021Q3', '2021A', '2022Q1']
        ind_fmt.to_excel('{0}net_profit_disp.xlsx'.format(self.file_path))

        for index_name in ['ROE_TTM', 'GROSS_INCOME_RATIO_TTM']:
            ind_fmt = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', index_name], 'industry_fundamental', self.sw_type)
            ind_fmt = ind_fmt[ind_fmt['INDUSTRY_NAME'].isin(self.select_industry)][['REPORT_DATE', 'INDUSTRY_NAME', index_name]]
            ind_fmt[index_name] = ind_fmt[index_name].apply(lambda x: round(x, 2))
            ind_fmt = ind_fmt[ind_fmt['REPORT_DATE'].isin([self.last_report_date, self.report_date])]
            ind_fmt = ind_fmt.sort_values(['REPORT_DATE', index_name], ascending=[False, False])
            industry_list = ind_fmt[ind_fmt['REPORT_DATE'] == self.report_date]['INDUSTRY_NAME'].unique().tolist()
            ind_fmt.columns = ['报告日期', '行业名称', index_name]
            rank_list = [self.last_report_date, self.report_date]
            ind_fmt_mom_abs = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', index_name + '_MOM_ABS'], 'industry_fundamental_derive', self.sw_type)
            ind_fmt_mom_abs = ind_fmt_mom_abs[ind_fmt_mom_abs['INDUSTRY_NAME'].isin(self.select_industry)][['REPORT_DATE', 'INDUSTRY_NAME', index_name + '_MOM_ABS']]
            ind_fmt_mom_abs[index_name + '_MOM_ABS'] = ind_fmt_mom_abs[index_name + '_MOM_ABS'].apply(lambda x: round(x, 2))
            ind_fmt_mom_abs = ind_fmt_mom_abs[ind_fmt_mom_abs['REPORT_DATE'].isin([self.report_date])]
            ind_fmt_mom_abs['INDUSTRY_NAME'] = ind_fmt_mom_abs['INDUSTRY_NAME'].astype('category')
            ind_fmt_mom_abs['INDUSTRY_NAME'].cat.reorder_categories(industry_list, inplace=True)
            ind_fmt_mom_abs = ind_fmt_mom_abs.sort_values('INDUSTRY_NAME')
            ind_fmt_mom_abs.columns = ['报告日期', '行业名称', index_name + '_MOM_ABS']
            ind_fmt_mom_abs.columns = ['报告日期', '行业名称', index_name + '_MOM_ABS']
            #####画柱状图#####
            fig, ax = plt.subplots(2, 1, figsize=(12, 12))
            sns.barplot(ax=ax[0], x='行业名称', y=index_name, data=ind_fmt, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[7], bar_color_list[0]])
            ax[0].set_xlabel('')
            ax[0].set_ylabel(index_name + '（%）')
            ax[0].set_xticklabels(labels=industry_list, rotation=90)
            ax[0].legend(loc=1)
            sns.barplot(ax=ax[1], x='行业名称', y=index_name + '_MOM_ABS', data=ind_fmt_mom_abs, palette=[bar_color_list[0]])
            ax[1].set_xlabel('')
            ax[1].set_ylabel(index_name + '环比变化值（%）')
            ax[1].set_xticklabels(labels=industry_list, rotation=90)
            plt.tight_layout()
            plt.savefig('{0}{1}_bar.png'.format(self.file_path, index_name.lower()))

            ind_fmt_yoy_abs = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', index_name + '_YOY_ABS'], 'industry_fundamental_derive', self.sw_type)
            ind_fmt_yoy_abs = ind_fmt_yoy_abs[ind_fmt_yoy_abs['INDUSTRY_NAME'].isin(self.select_industry)][['REPORT_DATE', 'INDUSTRY_NAME', index_name + '_YOY_ABS']]
            ind_fmt_yoy_abs[index_name + '_YOY_ABS'] = ind_fmt_yoy_abs[index_name + '_YOY_ABS'].apply(lambda x: round(x, 2))
            ind_fmt_yoy_abs = ind_fmt_yoy_abs[ind_fmt_yoy_abs['REPORT_DATE'].isin([self.last_report_date, self.report_date])]
            ind_fmt_yoy_abs = ind_fmt_yoy_abs.sort_values(['REPORT_DATE', index_name + '_YOY_ABS'], ascending=[False, False])
            ind_fmt_yoy_abs.columns = ['报告日期', '行业名称', index_name + '_YOY_ABS']
            rank_list = [self.last_report_date, self.report_date]
            #####画柱状图#####
            plt.figure(figsize=(12, 6))
            sns.barplot(x='行业名称', y=index_name + '_YOY_ABS', data=ind_fmt_yoy_abs, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[7], bar_color_list[0]])
            plt.xlabel('')
            plt.ylabel(index_name + '同比变化值（%）')
            plt.xticks(rotation=90)
            plt.legend(loc=1)
            plt.tight_layout()
            plt.savefig('{0}{1}_yoy_bar.png'.format(self.file_path, index_name.lower()))
        return

    def IndustryCon(self):
        date = '20211231'
        ind_con = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'IS_EXCEED_NEW', 'EXCEED_RATIO_NEW'], 'industry_consensus', self.sw_type)
        ind_con = ind_con[ind_con['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_con = ind_con[ind_con['REPORT_DATE'] == date]
        ind_con = ind_con.sort_values('EXCEED_RATIO_NEW', ascending=False)
        ind_con['EXCEED_RATIO_NEW'] = ind_con['EXCEED_RATIO_NEW'].apply(lambda x: round(x * 100.0, 2))
        ind_con = ind_con[['REPORT_DATE', 'INDUSTRY_NAME', 'IS_EXCEED_NEW', 'EXCEED_RATIO_NEW']]
        ind_con.columns = ['报告日期', '行业名称', 'IS_EXCEED_NEW', 'EXCEED_RATIO_NEW']
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='EXCEED_RATIO_NEW', data=ind_con, palette=[bar_color_list[0]])
        plt.xlabel('')
        plt.ylabel('超预期个股占比（%）')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig('{0}exceed_ratio_bar.png'.format(self.file_path))

        index_name = 'EST_NET_PROFIT_YOY'
        ind_con_yoy = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', index_name], 'industry_consensus', self.sw_type)
        ind_con_yoy = ind_con_yoy[ind_con_yoy['INDUSTRY_NAME'].isin(self.select_industry)][['REPORT_DATE', 'INDUSTRY_NAME', index_name]]
        # ind_con_yoy = ind_con_yoy[ind_con_yoy['INDUSTRY_NAME'] != '医药生物']
        ind_con_yoy[index_name] = ind_con_yoy[index_name].apply(lambda x: round(x, 2))
        ind_con_yoy = ind_con_yoy[ind_con_yoy['REPORT_DATE'].isin([self.last_report_date, self.report_date])]
        ind_con_yoy = ind_con_yoy.sort_values(['REPORT_DATE', index_name], ascending=[False, False])
        industry_list = ind_con_yoy[ind_con_yoy['REPORT_DATE'] == self.report_date]['INDUSTRY_NAME'].unique().tolist()
        ind_con_yoy.columns = ['报告日期', '行业名称', index_name]
        rank_list = [self.last_report_date, self.report_date]
        ind_con_yoy_mom_abs = ind_con_yoy[ind_con_yoy['报告日期'] == self.report_date][['行业名称', index_name]].set_index('行业名称') - ind_con_yoy[ind_con_yoy['报告日期'] == self.last_report_date][['行业名称', index_name]].set_index('行业名称')
        ind_con_yoy_mom_abs = pd.DataFrame(ind_con_yoy_mom_abs).rename(columns={index_name: index_name + '_MOM_ABS'}).reset_index()
        ind_con_yoy_mom_abs['行业名称'] = ind_con_yoy_mom_abs['行业名称'].astype('category')
        ind_con_yoy_mom_abs['行业名称'].cat.reorder_categories(industry_list, inplace=True)
        ind_con_yoy_mom_abs = ind_con_yoy_mom_abs.sort_values('行业名称')
        #####画柱状图#####
        fig, ax = plt.subplots(2, 1, figsize=(12, 12))
        sns.barplot(ax=ax[0], x='行业名称', y=index_name, data=ind_con_yoy, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[7], bar_color_list[0]])
        ax[0].set_xlabel('')
        ax[0].set_ylabel(index_name + '（%）')
        ax[0].set_xticklabels(labels=industry_list, rotation=90)
        ax[0].legend(loc=1)
        sns.barplot(ax=ax[1], x='行业名称', y=index_name + '_MOM_ABS', data=ind_con_yoy_mom_abs, palette=[bar_color_list[0]])
        ax[1].set_xlabel('')
        ax[1].set_ylabel(index_name + '环比变化值（%）')
        ax[1].set_xticklabels(labels=industry_list, rotation=90)
        plt.tight_layout()
        plt.savefig('{0}{1}_bar.png'.format(self.file_path, index_name.lower()))
        return

    def IndustryFundHolding(self):
        fund_industry_1st = FEDB().read_data(self.report_date, 'INDUSTRY_SW1')
        fund_industry_1st = fund_industry_1st[fund_industry_1st['LABEL_NAME'].isin(self.select_industry)]
        fund_industry_1st = fund_industry_1st.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
        fund_industry_1st = fund_industry_1st[fund_industry_1st.index.isin([self.last_report_date, self.report_date])]
        fund_industry_1st = fund_industry_1st.unstack().reset_index().rename(columns={0: 'LABEL_VALUE'})
        fund_industry_1st = fund_industry_1st.sort_values(['REPORT_HISTORY_DATE', 'LABEL_VALUE'], ascending=[False, False])
        fund_industry_1st.columns = ['行业名称', '报告日期', '持仓比例']
        rank_list = [self.last_report_date, self.report_date]
        industry_list = fund_industry_1st[fund_industry_1st['报告日期'] == self.report_date]['行业名称'].unique().tolist()
        mom_abs = fund_industry_1st[fund_industry_1st['报告日期'] == self.report_date][['行业名称', '持仓比例']].set_index('行业名称') - fund_industry_1st[fund_industry_1st['报告日期'] == self.last_report_date][['行业名称', '持仓比例']].set_index('行业名称')
        mom_abs = pd.DataFrame(mom_abs).rename(columns={'持仓比例': '持仓比例_MOM_ABS'}).reset_index()
        mom_abs['行业名称'] = mom_abs['行业名称'].astype('category')
        mom_abs['行业名称'].cat.reorder_categories(industry_list, inplace=True)
        mom_abs = mom_abs.sort_values('行业名称')
        #####画柱状图#####
        fig, ax = plt.subplots(2, 1, figsize=(12, 12))
        sns.barplot(ax=ax[0], x='行业名称', y='持仓比例', data=fund_industry_1st, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[7], bar_color_list[0]])
        ax[0].set_xlabel('')
        ax[0].set_ylabel('公募重仓比例（%）')
        ax[0].set_xticklabels(labels=industry_list, rotation=90)
        ax[0].legend(loc=1)
        sns.barplot(ax=ax[1], x='行业名称', y='持仓比例_MOM_ABS', data=mom_abs, palette=[bar_color_list[0]])
        ax[1].set_xlabel('')
        ax[1].set_ylabel('公募重仓比例环比变化值（%）')
        ax[1].set_xticklabels(labels=industry_list, rotation=90)
        plt.tight_layout()
        plt.savefig('{0}fund_holding_bar.png'.format(self.file_path))
        return

    def get_all(self):
        self.IndustryMarketValue()
        self.IndustryRet()
        self.IndustryTech()
        self.IndustryNewhigh()
        self.IndustryVal()
        self.IndustryFmt()
        self.IndustryCon()
        self.IndustryFundHolding()
        return


if __name__ == '__main__':
    file_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/inudstry_analysis/'
    start_date = '20170101'
    end_date = '20220331'
    last_report_date = '20211231'
    report_date = '20220331'
    for sw_type in [1]:
        IndustryAnalysis(file_path, start_date, end_date, last_report_date, report_date, sw_type).get_all()