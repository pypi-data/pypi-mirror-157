import numpy as np
import pandas as pd
import datetime as dt
from datamagus.core import DataMagus
from datamagus.vis import *
import warnings
warnings.filterwarnings("ignore")


class BaseModel(DataMagus):
    def __init__(self):
        super().__init__()

    def fit(self):
        pass

    def show(self):
        pass


class RFMModel(BaseModel):
    """
    Example 1:   
    >>> rfm=RFMModel()
    >>> df=pd.read_csv('https://raw.githubusercontent.com\
        /Alazia/datamagus/main/src/test/Retail_Data_Transactions.csv')
     customer_id trans_date  tran_amount
    0           CS5295  11-Feb-13           35
    1           CS4768  15-Mar-15           39
    >>> rfm.get_rfm(df,its=['customer_id','trans_date','tran_amount'],\
        t="2022-06-27")
    >>> rfm.rfm
        id     R   F       M
    0     CS1112  2721  15  1012.0
    1     CS1113  2695  20  1490.0
    2     CS1114  2692  19  1432.0
    >>> rfm.fit()
    >>> rfm.rfm_score
        R   F       M  R_score  F_score  M_score     RFM
    id                                                         
    CS1112  2721  15  1012.0        2        1        1  一般发展客户
    CS1113  2695  20  1490.0        2        2        2  重要价值客户
    CS1114  2692  19  1432.0        2        2        2  重要价值客户
    Example 2:
    >>> df = pd.DataFrame({
    'id': np.arange(1, 10001),
    'R': np.random.randint(1, 10, 10000),
    'F': np.random.randint(1, 100, 10000),
    'M': np.random.randint(1000, 10000, 10000),
    })
    >>> rfm=RFMModel()
    >>> rfm.get_rfm(df)
    >>> rfm.fit()
    >>> rfm.rfm_score
        R   F     M  R_score  F_score  M_score     RFM
    id                                                   
    1      3  62  2029        2        2        1  一般价值客户
    2      9  77  5028        1        2        1  一般保持客户
    3      8  86  4399        1        2        1  一般保持客户
    >>> rfm.show()
    """

    def __init__(self,its=None,metrics=None):
        super().__init__()
        self._metrics=metrics
        if its is not None:self.getrfm(its)

    @property
    def metrics(self):
        return self._metrics

    @metrics.setter
    def metrics(self,mlist:list):
        """
        Example:
        R<90,5
        90<=R<180,4
        ...
        R>=720,
        R(reverse)
        ----
        F<2,1
        2<=F<4,2
        ...
        F>=5,5
        >>>  mlist=[[90,180,360,720],[2,3,4,5],[100,200,500,1000]]
        """
        if isinstance(mlist,mlist) and len(mlist)==3:
            self._metrics=mlist
        else:
            raise TypeError("Object is not mlist")

    @metrics.deleter
    def metrics(self):
        del self._metrics

    def get_rfm(self,df,its:list=None,t:str=None,s:str=None):
        if isinstance(df,pd.DataFrame):
            self.df=df.copy()
        if its is None:
            self.rfm=self.df
            self.rfm.columns=['id','R','F','M']
        elif isinstance(its,list) and len(its)==3:
            _tmp=self.df.loc[:,its]
            _tmp.columns=['id','time','cost']
            _tmp['time']=pd.to_datetime(_tmp['time'])
            _tmp['cost']=_tmp['cost'].astype(float)
            _tmp.dropna(inplace=True)
            if t is None:
                t=dt.datetime.now()
            else:
                t=dt.datetime.strptime(t,'%Y-%m-%d')
            if s is not None:
                s=dt.datetime.strptime(s,'%Y-%m-%d')
                _tmp=_tmp.loc[_tmp['time']>=s,:]
            _tmp['R']=(t-_tmp['time']).dt.days
            R =_tmp.groupby(by=['id'])['R'].agg([('R','min')])
            F =_tmp.groupby(by=['id'])['id'].agg([('F','count')])
            M =_tmp.groupby(by=['id'])['cost'].agg([('M',sum)])
            self.rfm= R.join(F).join(M).reset_index()
              
    @staticmethod
    def between_score(x,ref:list,reverse=False):
        if not reverse:
            if len(ref)==1:
                return 1 if x<ref[0] else 2
            else:
                for i,in range(len(ref)):
                    if i==0:
                        if x<ref[i]:
                            return 1
                    elif i==len(ref)-1:
                        if x>=ref[i]:
                            return 1+len(ref)
                    else:
                        if ref[i-1]<=x<ref[i]:
                            return 1+i
        else:
            if len(ref)==1:
                return 2 if x<ref[0] else 1
            else:
                for i,in range(len(ref)):
                    if i==0:
                        if x<ref[i]:
                            return len(ref)+1
                    elif i==len(ref)-1:
                        if x>=ref[i]:
                            return 1
                    else:
                        if ref[i-1]<=x<ref[i]:
                            return len(ref)+1-i

    def fit(self):
        self.rfm.set_index(self.rfm.columns[0],inplace=True)
        if self._metrics is None:
            self._metrics=[[elem] for elem in self.rfm.mean()]
            _tmp_flag=True
        self.rfm_score=self.rfm.copy()
        self.rfm_score['R_score']=self.rfm_score['R'].apply(lambda x:\
            self.between_score(x,ref=self._metrics[0],reverse=True))
        self.rfm_score['F_score']=self.rfm_score['F'].apply(lambda x:\
            self.between_score(x,ref=self._metrics[1]))
        self.rfm_score['M_score']=self.rfm_score['M'].apply(lambda x:\
            self.between_score(x,ref=self._metrics[2]))
        self.rfm_score['RFM']=self.rfm_score['R_score'].astype(str)+\
            self.rfm_score['F_score'].astype(str)+\
                self.rfm_score['M_score'].astype(str)
        if _tmp_flag:
            self.rfm_score['RFM']=self.rfm_score['RFM'].map({
                "222":"重要价值客户",
                "122":"重要保持客户",
                "212":"重要发展客户",
                "112":"重要挽留客户",
                "221":"一般价值客户",
                "121":"一般保持客户",
                "211":"一般发展客户",
                "111":"一般挽留客户"
            })
    
    def show(self,method='all',savefig=False,colors=None,**kwargs):
        #TODO:donut,bar
        _rfm=self.rfm_score['RFM'].value_counts().\
            sort_values(ascending=False).reset_index()
        if method=='donut':
            plot_setting()
            plot_donut(_rfm,label='index',value='RFM',colors=colors)
            if savefig:plot_savefig(title='RFM_donut',**kwargs)
        elif method=='bar':
            plot_setting(fig1=10,fig2=6)
            plot_bar(_rfm,x='index',height='RFM')
            if savefig:plot_savefig(title='RFM_bar',**kwargs)
        else:
            plot_setting()
            plot_donut(_rfm,label='index',value='RFM',colors=colors)
            if savefig:plot_savefig(title='RFM_donut',**kwargs)
            plot_setting(fig1=10,fig2=6)
            plot_bar(_rfm,x='index',height='RFM')
            if savefig:plot_savefig(title='RFM_bar',**kwargs)
      
