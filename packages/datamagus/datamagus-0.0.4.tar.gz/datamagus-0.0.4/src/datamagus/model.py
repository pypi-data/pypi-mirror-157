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

    def load_data(self,df:pd.DataFrame):
        if isinstance(df,pd.DataFrame):
            self.df=df.copy()
        else:
            TypeError("Incorrect input")

    def unleash(self):
        pass

    def visualize(self):
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
    >>> rfm.load_data(df,its=['customer_id','trans_date','tran_amount'],\
        t="2022-06-27")
    >>> rfm.rfm
        id     R   F       M
    0     CS1112  2721  15  1012.0
    1     CS1113  2695  20  1490.0
    2     CS1114  2692  19  1432.0
    >>> rfm.unleash()
    >>> rfm.res
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
    >>> rfm.load_data(df)
    >>> rfm.unleash()
    >>> rfm.res
        R   F     M  R_score  F_score  M_score     RFM
    id                                                   
    1      3  62  2029        2        2        1  一般价值客户
    2      9  77  5028        1        2        1  一般保持客户
    3      8  86  4399        1        2        1  一般保持客户
    >>> rfm.visualize()
    """

    def __init__(self,metrics=None):
        super().__init__()
        self._metrics=metrics

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
        if isinstance(mlist,list) and len(mlist)==3:
            self._metrics=mlist
        else:
            raise TypeError("Object is not mlist")

    @metrics.deleter
    def metrics(self):
        del self._metrics

    def load_data(self,df,its:list=None,t:str=None,s:str=None):
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
        else:
            TypeError("Incorrect input")
              
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

    def unleash(self):
        self.rfm.set_index(self.rfm.columns[0],inplace=True)
        if self._metrics is None:
            self._metrics=[[elem] for elem in self.rfm.mean()]
            _tmp_flag=True
        self.res=self.rfm.copy()
        self.res['R_score']=self.res['R'].apply(lambda x:\
            self.between_score(x,ref=self._metrics[0],reverse=True))
        self.res['F_score']=self.res['F'].apply(lambda x:\
            self.between_score(x,ref=self._metrics[1]))
        self.res['M_score']=self.res['M'].apply(lambda x:\
            self.between_score(x,ref=self._metrics[2]))
        self.res['RFM']=self.res['R_score'].astype(str)+\
            self.res['F_score'].astype(str)+\
                self.res['M_score'].astype(str)
        if _tmp_flag:
            self.res['RFM']=self.res['RFM'].map({
                "222":"重要价值客户",
                "122":"重要保持客户",
                "212":"重要发展客户",
                "112":"重要挽留客户",
                "221":"一般价值客户",
                "121":"一般保持客户",
                "211":"一般发展客户",
                "111":"一般挽留客户"
            })
    
    def visualize(self,method='all',savefig=False,colors=None,**kwargs):
        plt.rcParams['font.family'] = ['sans-serif']
        plt.rcParams['font.sans-serif'] = ['SimHei']
        _rfm=self.res['RFM'].value_counts().\
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


class ParetoModel(BaseModel):
    """
    Example:
    >>> np.random.seed(1)
    >>> a = np.random.randint(110000,120000,2)
    >>> b = np.random.randint(20000, 80000, 3)
    >>> c = np.random.randint(2000, 8000, 5)
    >>> df = pd.DataFrame({
    'id': np.arange(1, 11),
    'M':np.append(np.append(a,b),c)
    })
    >>> pm=ParetoModel()
    >>> pm.load_data(df)
    >>> pm.unleash()
    >>> pm.res
        id         M  Accumulate  Percent Class
    0   2  115192.0    115192.0   26.37%     A
    1   1  110235.0    225427.0   51.60%     A
    2   4   70057.0    295484.0   67.64%     A
    3   5   63723.0    359207.0   82.23%     B
    4   3   52511.0    411718.0   94.25%     C
    5   7    7056.0    418774.0   95.87%     C
    6   9    6225.0    424999.0   97.29%     C
    7   6    4895.0    429894.0   98.41%     C
    8  10    4797.0    434691.0   99.51%     C
    9   8    2144.0    436835.0  100.00%     C
    >>> pm.results[1]
                                    ID Count_Percent Money_Percent
    Class                                                           
    A                      '2', '1', '4'        30.00%        67.64%
    B                                '5'        10.00%        14.59%
    C      '3', '7', '9', '6', '10', '8'        60.00%        17.77%
    >>> pm.visualize()
    """
    def __init__(self,metrics='ABC'):
        super().__init__()
        self.metrics = metrics

    def load_data(self, df: pd.DataFrame):
        return super().load_data(df)

    @staticmethod
    def between_score(x,ref):
        if ref=='ABC':
            if x<0.8:
                return 'A'
            elif 0.8<=x<0.9:
                return 'B'
            else:
                return 'C'
        else:
            if x<0.8:
                return '1'
            else:
                return '2'

    def unleash(self,percent=True):
        self.df.columns=['id','M']
        self.df['id']=self.df['id'].astype(str)
        self.df['M']=self.df['M'].astype(float)
        self.res=self.df.sort_values('M',ascending=False).reset_index(drop=True)
        self.res['Accumulate']=self.res['M'].cumsum() 
        # Arithmetic is modular when using integer types, and no error is raised on overflow.
        self.res['Percent']= self.res['Accumulate']/self.res['M'].sum()
        self.res['Class']=self.res['Percent'].\
            apply(lambda x:self.between_score(x,ref=self.metrics))
        '''result2'''
        I=self.res.groupby('Class')['id'].agg([lambda x:list(x),'count'])
        S=self.res.groupby('Class')['M'].agg(['sum'])
        _tmp=I.join(S)
        _tmp.columns=['ID','Count_Percent','Money_Percent']
        _tmp['ID']=_tmp['ID'].apply(lambda x:str(x)[1:-1])
        _tmp['Count_Percent']=_tmp['Count_Percent']/_tmp['Count_Percent'].sum()
        _tmp['Money_Percent']=_tmp['Money_Percent']/_tmp['Money_Percent'].sum()
        if percent:
            self.res['Percent']= self.res['Percent'].\
                apply(lambda x: format(x, '.2%'))
            _tmp['Count_Percent']= _tmp['Count_Percent'].\
                apply(lambda x: format(x, '.2%'))
            _tmp['Money_Percent']= _tmp['Money_Percent'].\
                apply(lambda x: format(x, '.2%'))
        self.results=(self.res,_tmp)

    def visualize(self,savefig=False,**kwargs):
        ax=plot_setting()
        plot_bar(df=self.res,x='id',height='M')
        ax2=ax.twinx()
        ax2.plot(self.res['Percent'].str[:-1].astype(float)*0.01,color='orange',marker='o')
        plt.axhline(y=0.8,ls='--',color='green')
        if self.metrics=='ABC':plt.axhline(y=0.9,ls='--',color='blue')
        if savefig:plot_savefig(title='Pareto_plot',**kwargs)
        
  
        
