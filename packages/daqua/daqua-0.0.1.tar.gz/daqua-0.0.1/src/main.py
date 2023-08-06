"""
Created By: Satya Pati
Created on: 17-06-2021 00:36
"""
import numpy as np
import pandas as pd


from config import Config
import read_flat_file
import descriptive_util 

class Main:
    def __init__(self):
        self.config = Config()
        self.excel_reader = read_flat_file.ReadExcel(self)
        self.meta_info = descriptive_util.MetaInfo(self)
        


def main():
    m = Main()
    pd.set_option('display.max_columns', None)
    l = m.excel_reader.getFileDetails()
    print(l)
    l = m.meta_info.getMetaData()
    s = m.meta_info.getAllMeta()
    print(s.data_type.unique())
    print("------------------------------------")
    print(s.groupby('Table_name').size())
    print("-----------------------------------------------")
    print(s[(s['num_unique']==0)|(s['num_unique']==1)].groupby('Table_name').size())



if __name__=="__main__":
    main()