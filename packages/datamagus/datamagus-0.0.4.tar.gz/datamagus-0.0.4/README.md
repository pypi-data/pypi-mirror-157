# datamagus
[![PyPI](https://img.shields.io/badge/PyPI-0.0.3-green)](https://pypi.org/project/datamagus/)</br>
Packages and API interface for basic data analysis processing, graphing and modeling, and practical use.


## Installation
```
pip install datamagus
```
## Model
The datamagus model module contains several analysis models, including RFM, Pareto, etc.

#### RFM Example

Example 1: In most cases the data we use to study customer value is based on order sales, consisting of user id,transaction time and transaction amount.
```python
# https://www.kaggle.com/datasets/regivm/retailtransactiondata?select=Retail_Data_Transactions.csv
>>> from datamagus.model import RFMModel
>>> rfm=RFMModel()
>>> df=pd.read_csv('https://raw.githubusercontent.com/Alazia/datamagus/main/src/test/Retail_Data_Transactions.csv') 
    customer_id trans_date  tran_amount
0           CS5295  11-Feb-13           35
1           CS4768  15-Mar-15           39
>>> rfm.load_data(df,its=['customer_id','trans_date','tran_amount'],t="2022-06-27")
>>> rfm.rfm
    id     R   F       M
0     CS1112  2721  15  1012.0
1     CS1113  2695  20  1490.0
2     CS1114  2692  19  1432.0
>>> rfm.unleash()
>>> rfm.rfm_score
    R   F       M  R_score  F_score  M_score     RFM
id                                                         
CS1112  2721  15  1012.0        2        1        1  一般发展客户
CS1113  2695  20  1490.0        2        2        2  重要价值客户
CS1114  2692  19  1432.0        2        2        2  重要价值客户
```
Example 2: When we have data in RFM format.
```python
>>> df = pd.DataFrame({
'id': np.arange(1, 10001),
'R': np.random.randint(1, 10, 10000),
'F': np.random.randint(1, 100, 10000),
'M': np.random.randint(1000, 10000, 10000),
})
>>> rfm=RFMModel()
>>> rfm.load_data(df)
>>> rfm.unleash()
>>> rfm.rfm_score
    R   F     M  R_score  F_score  M_score     RFM
id                                                   
1      1  93  3841        2        2        1  一般价值客户
2      6  86  1833        1        2        1  一般保持客户
3      7  31  4474        1        1        1  一般挽留客户
>>> rfm.visualize()
```
**RFM Visualization**

<img src="./data/pic/RFM_bar.png" width="70%">
<img src="./data/pic/RFM_donut.png" width="70%">

#### Pareto 
```python
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
```
**Pareto Visualization**

<img src="./data/pic/Pareto_plot.png" width="70%">

