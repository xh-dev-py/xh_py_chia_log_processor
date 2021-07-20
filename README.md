# Chia Log Processor

A library provide functionality process chia plot log.

# Installation

```
pip install pyChiaLogProcessor
```

# Demo

```python
import pyChiaLogProcessor 
```

```python
from pyChiaLogProcessor import ChiaLog

log = ChiaLog("plot.log")
print(log.find_start())
print(log.find_id())
print(log.find_phrase(1))
print(log.find_phrase(2))
print(log.find_phrase(3))
print(log.find_phrase(4))
print(log.find_plot_name())
print(log.find_complete())

```