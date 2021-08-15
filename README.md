# Chia Log Processor

A library provide functionality process chia plot log.

# Installation

```shell script
pip install pyChiaLogProcessor
```

or

```shell script
pip3 install pyChiaLogProcessor
```


# Demo

```python
from pyChiaLogProcessor import ChiaLog, ChiaLogSummary

# ChiaLog
log = ChiaLog("plot.log")
print(log.find_start())
print(log.find_id())
print(log.find_phrase(1))
print(log.find_phrase(2))
print(log.find_phrase(3))
print(log.find_phrase(4))
print(log.find_plot_name())
print(log.find_complete())

#ChiaLogSummary
summary = ChiaLogSummary(log)
print(summary.isCompleted())
if summary.isCompleted():
    print(summary.completeDuration())
print(summary.isPhrase1Done())
if summary.isPhrase1Done():
    print(summary.phrase1Duration())
print(summary.isPhrase2Done())
if summary.isPhrase2Done():
    print(summary.phrase2Duration())
print(summary.isPhrase3Done())
if summary.isPhrase3Done():
    print(summary.phrase3Duration())
print(summary.isPhrase4Done())
if summary.isPhrase4Done():
    print(summary.phrase4Duration())

```