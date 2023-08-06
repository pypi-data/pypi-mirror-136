# CSV ElasticDictWriter


DictWriter, built on top of csv.DictWriter, that supports automatic extension of headers according to what data it receives.
The result file always has a complete header (as defined by fieldnames) or it is extended if some new columns
 are introduced in the data. It always produces a valid CSV (missing columns are filled with blanks).
 It uses a series of cached writers / files that are merged into a single one with final set of columns on close()


## Installation 
 
The package may be installed via PIP:
 
```
pip install keboola.csvwriter
```



**NOTE:** If not using "with" statement, close() method must be called at the end of processing to get the result.

**NOTE:** Does not keep the order of rows added - the rows containing additional headers always come first:

### Example:

```python
from keboola.csvwriter import ElasticDictWriter
file = '/test/test.csv'
wr = ElasticDictWriter(file, ["a", "b" , "c"])
wr.writeheader()
wr.writerow({"a":1,"b":2})
wr.writerow({"b":2, "d":4})
wr.close()

```

leads to CSV with following content:
   
|a  |b  |c  |d  |
|---|---|---|---|
|   |2  |   |4  |
|1  | 2 |   |   |

May be also used with `with` statement to automatically close once finished:

```python
from keboola.csvwriter import ElasticDictWriter
file = '/test/test.csv'
with ElasticDictWriter(file, ["a", "b" , "c"]) as wr:
    wr.writeheader()
    wr.writerow({"a":1,"b":2})
    wr.writerow({"b":2, "d":4})

# get final headers
final_header = wr.fieldnames
```

**NOTE:** The final column list is stored in `fieldnames` property:

```python
columns = writer.fieldnames
```