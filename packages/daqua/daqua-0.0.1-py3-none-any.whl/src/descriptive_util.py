

from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
import numpy as np
import pandas as pd
import os
import datetime

class MetaInfo:


    def __init__(self, main):        
        self.main = main
        self._dfs = {sheet_name: self.main.excel_reader.parseExcel(sheet_name) for 
                        sheet_name in self.main.excel_reader.getSheetNames()}
        self._meta_data = pd.DataFrame([{
                                sheet_name: dataframe.shape for sheet_name, dataframe in self._dfs.items()
                            }])

        self._detailed_meta = {sheet_name: self.getDetailMeta(sheet_name) for sheet_name in self._dfs.keys()}
        _ = self.createAllMeta()
        self._descriptive_num = {sheet_name: self.getNumericDetails(sheet_name) for sheet_name in self._dfs.keys()}
        self._descriptive_str = {sheet_name: self.getStringDetails(sheet_name) for sheet_name in self._dfs.keys()}
        # self._descriptive_date = {sheet_name: self.detectDate(sheet_name) for sheet_name in self._dfs.keys()}


    def getMetaData(self):
        return self._meta_data.T

    
    def rowWiseFillRate(self, df):
        val_cnt = df.isna().sum(axis=1).value_counts()
        val_cnt = pd.DataFrame(val_cnt)
        val_cnt.columns = ['n_rows']
        val_cnt['n_cols'] = val_cnt.index

    
    def getDetailMeta(self, sheet_name):
        df = self._dfs[sheet_name]
        column_names = df.columns.tolist()
        detailed_meta = [
                        {
                            "column_name": col,
                            "data_type": df[col].dtype,
                            "not_na_val": df[col].notna().sum(),
                            "fill_rate": df[col].notna().sum()*100/len(df),
                            "num_unique": df[col].nunique()
                            # "unique_rate": df[col].nunique()*100/len(df[df[col].notna()]) 
                        }
                        for col in column_names]

        detailed_meta_df = pd.DataFrame(detailed_meta)
        detailed_meta_df.loc[:, 'unique_rate'] = detailed_meta_df.loc[:, 'num_unique'] * 100 / detailed_meta_df.loc[:, 'not_na_val']
        detailed_meta_df.loc[:, 'unique_rate'] = detailed_meta_df.loc[:, 'unique_rate'].fillna(0)
        detailed_meta_df['Table_name'] = sheet_name
        detailed_meta_df['Shape'] = [df.shape]*len(detailed_meta_df)
        return detailed_meta_df


    def createAllMeta(self):
        ls_data = list(self._detailed_meta.values())
        self._all_meta_df = pd.concat(ls_data)


    def getAllMeta(self):
        return self._all_meta_df

    
    def getNumericDetails(self, sheet_name):
        df = self._dfs[sheet_name]
        meta_df = self._detailed_meta[sheet_name]
        num_cols = meta_df.loc[meta_df['data_type']==int, 'column_name'].tolist()
        res = df[num_cols].describe()
        return num_cols


    def getStringDetails(self, sheet_name):
        df = self._dfs[sheet_name]
        meta_df = self._detailed_meta[sheet_name]
        str_cols = meta_df.loc[meta_df['data_type']==str, 'column_name'].tolist()
        return str_cols


    def detectDate(self, sheet_name):
        df = self._dfs[sheet_name]
        mask = df.astype(str).apply(lambda x : x.str.match(r'\d{4}-\d{2}-\d{2} \d{2}\:\d{2}\:\d{2}').all())
        df.loc[:,mask] = df.loc[:,mask].apply(pd.to_datetime)
        date_time_cols = df[df.dtypes == datetime.datetime]
        return date_time_cols

    
    def getAppropriate(self):
        """get the appropriate data type for the column"""
        pass


    def getQuantileStat(self, series_col):

        res_dict = {"minimum": series_col.min(), "maximum": series_col.max(), "range": series_col.max() - series_col.min()}


    def getDfWiseDetails(self, sheet_name):
        df = self._dfs[sheet_name][self._descriptive_num[sheet_name]]
        res_dict1, res_dict2 = [], []
        for item in df:
            res1, res2 = getStatData(df[item])
            res_dict1.append(res1)
            res_dict2.append(res2)
