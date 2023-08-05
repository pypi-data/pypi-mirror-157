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
>>> rfm.get_rfm(df,its=['customer_id','trans_date','tran_amount'],t="2022-06-27")
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
>>> rfm.get_rfm(df)
>>> rfm.fit()
>>> rfm.rfm_score
    R   F     M  R_score  F_score  M_score     RFM
id                                                   
1      1  93  3841        2        2        1  一般价值客户
2      6  86  1833        1        2        1  一般保持客户
3      7  31  4474        1        1        1  一般挽留客户
>>> rfm.show()
```
**RFM Visualization**

<img src="./data/pic/RFM_bar.png" width="70%">
<img src="./data/pic/RFM_donut.png" width="70%">