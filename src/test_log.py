from pyChiaLogProcessor import ChiaLog
from datetime import datetime

def test_log():
    log = ChiaLog(r"./src/plot109.log")
    assert log is not None
    assert log.find_start() is not None
    assert log.find_start() == datetime(2021,6,18,8,16,23) #2021-06-18T08:16:23.104
    assert log.find_id() == "8ab403dbc4faf4f9e9981f478533c4c4aaa31c13242aa631f6dcfadae50f2c35"
    assert log.find_phrase(1) == datetime(2021,6,18,8,16,23) #Jun 18 08:16:23 2021
    assert log.find_phrase(2) == datetime(2021,6,19,6,46,19) #Sat Jun 19 06:46:19 2021
    assert log.find_phrase(3) == datetime(2021,6,19,13,33,19) #Jun 19 13:33:19 2021
    assert log.find_phrase(4) == datetime(2021,6,20,5,5,52) #Sun Jun 20 05:05:52 2021

    assert log.find_plot_name() == "plot-k32-2021-06-18-08-16-8ab403dbc4faf4f9e9981f478533c4c4aaa31c13242aa631f6dcfadae50f2c35.plot"
    assert log.find_complete() == datetime(2021,6,20,6,40,13) #2021-06-20T06:40:13.273

    res = log.summary()
    assert res is not None
    assert res['whole']['progress'] == round(100, 2)
    assert res['phrase1']['progress'] == round(100, 2)
    assert res['phrase2']['progress'] == round(100, 2)
    assert res['phrase3']['progress'] == round(100, 2)
    assert res['phrase4']['progress'] == round(100, 2)
