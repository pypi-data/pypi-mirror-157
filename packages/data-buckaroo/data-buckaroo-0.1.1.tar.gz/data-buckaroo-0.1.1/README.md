# Data Buckaroo

Lightweight AWS Data Wrangler, for Athena queries only. Also has a lightweight "DataFrame" implementation if you prefer not to use Pandas.

### Install

```bash
pip install data-buckaroo
# Optional if you would like to use Pandas
pip install data-buckaroo[pandas]
```

### Usage

```python
from data_buckaroo import AthenaQuery
from lightframe import LightFrame
aq = AthenaQuery(workgroup="ATHENA_WORKGROUP", database="ATHENA_DATABASE")
lf: LightFrame = aq.read_sql_query("SELECT * FROM TABLE_NAME")
print(lf)
```
```
   id  string_object  string  float  int        date            timestamp   bool  par0  par1
0   1            foo     foo    1.0    1  2020-01-01  2020-01-01 00:00:00   True     1     a
1   2                                                                                1     b
2   3            boo     boo    2.0    2  2020-01-02  2020-01-02 00:00:01  False     2     b
```
