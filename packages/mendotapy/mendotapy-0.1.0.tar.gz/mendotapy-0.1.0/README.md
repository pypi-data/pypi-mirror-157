# mendotapy

A Python 3.6+ package for analysis-ready [Lake Mendota ice phenology](https://www.aos.wisc.edu/~sco/lakes/Mendota-ice.html) data

Installing
----------

### PyPi
```sh
pip install mendotapy==0.1.0
```

### GitHub
```sh
pip install -e git+https://github.com/lgloege/mendotapy.git#egg=mendotapy
```

Using the Package
----------
**Read data into a dataframe**
```python
import mendotapy
df = mendotapy.load()
```

**Summary plot of the data**
```python
import mendotapy
mendotapy.plot()
```
