'''core code for data analysis'''
import pandas as pd
import numpy as np
from datamagus.vis import *
# from .vis import *

class DataMagus(object):
    def __init__(self):
        self._df = None

    @property
    def df(self):
        """ 
        Return a DataFrame.
        Examples
        --------
        >>> df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        >>> dm = DataMagus()
        >>> dm.df = df
        	col1	col2
        0	1	3
        1	2	4
        """
        return self._df

    @df.setter
    def df(self,df:pd.DataFrame):
        if isinstance(df,pd.DataFrame):
            self._df=df.copy()
        else:
            raise TypeError("Object is not pd.DataFrame")

    @df.deleter
    def df(self):
        del self._df

    # magic base on dataframe
    def df_na(self,n=6) -> float:
        """
        Return na ratio of the DataFrame(matrix).
        Examples
        --------
        >>> df = pd.DataFrame({'col1': [1, np.nan], 'col2': [3, 4]})
        >>> dm = DataMagus()
        >>> dm.df = df
        >>> dm.df_na()
        0.25
        """
        return round(self._df.isna().sum().sum()/\
            (self._df.shape[0]*self._df.shape[1]),n)
    
    def df_describe(self) -> pd.core.series.Series:
        """
        Return describe of the DataFrame(matrix).
        Examples
        --------
        >>> df = pd.DataFrame({'col1': [1, 2, 2, 3], 'col2': [3, 3, 4, 5 ]})
        >>> dm = DataMagus()
        >>> dm.df = df
        >>> dm.df_describe()
        """
        return pd.Series.describe(pd.Series(self._df.unstack().tolist()))
    
    def density_df(self,savefig=False):
        plot_setting(title='density')
        plot_density(self._df)
        if savefig:plot_savefig(title='DM_density')
            

        
        




