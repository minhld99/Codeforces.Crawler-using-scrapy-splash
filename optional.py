import pandas as pd
from pandas.tests.tseries.frequencies.test_inference import count

f = pd.read_csv('cf_testcase.csv')
i = 00
for input in f.inputs:
    if count(input.split(',')[0]('...')) == 1:
        print("1")