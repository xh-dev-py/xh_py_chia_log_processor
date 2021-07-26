import re
from datetime import datetime
from typing import Optional


def __parse_to_datetime(d_str: str) -> datetime:
    return datetime.strptime(d_str[0:19], "%Y-%m-%dT%H:%M:%S")


def find_start(lines) -> Optional[datetime]:
    try:
        pattern = '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.\\d{3}'
        return next(
            __parse_to_datetime(re.search(pattern, line)[0]) for line in lines if re.search(pattern, line) is not None)
    except:
        return None


def find_id(lines) -> str or None:
    try:
        pattern = '^ID: (\\w+)$'
        return next(re.search(pattern, line)[1] for line in lines if re.search(pattern, line) != None)
    except:
        return None


def find_phrase_start(lines, phrase: int) -> Optional[datetime]:
    def to_datetime(line):
        try:
            timeformat = "%b %d %H:%M:%S %Y"
            return datetime.strptime(line, timeformat)
        except:
            return None

    pattern = "Starting phase 1/4: .* \\w{3} (\\w{3} \\d{2} \\d{2}:\\d{2}:\\d{2} \\d{4})".replace('1', str(phrase))
    try:
        return next(to_datetime(re.search(pattern, line)[1]) for line in lines if re.search(pattern, line) is not None)
    except StopIteration:
        return None


def find_phrase_end(lines, phrase: int) -> Optional[datetime]:
    def to_datetime(line):
        try:
            timeformat = "%b %d %H:%M:%S %Y"
            return datetime.strptime(line, timeformat)
        except:
            return None

    pattern = "Time for phase 1 = \\d+\\.\\d+ seconds\\..* \\w{3} (\\w{3} \\d{2} \\d{2}:\\d{2}:\\d{2} \\d{4})".replace(
        '1', str(phrase))
    try:
        return next(to_datetime(re.search(pattern, line)[1]) for line in lines if re.search(pattern, line) is not None)
    except StopIteration:
        return None


def find_complete(lines, plot_name: str) -> Optional[datetime]:
    try:
        pattern = "^(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.\\d{3})[ ]+chia.plotting.create_plots[ ]+.*(<plotName>).*".replace(
            '<plotName>', plot_name)
        return next(
            __parse_to_datetime(re.search(pattern, line)[1]) for line in lines if re.search(pattern, line) is not None)
    except:
        return None


def find_plot_name(lines) -> Optional[str]:
    id = find_id(lines)
    start = find_start(lines)
    if id is None or start is None:
        return None
    else:
        return "plot-k32-%04d-%02d-%02d-%02d-%02d-%s.plot" % (
            start.year, start.month, start.day, start.hour, start.minute, id)


def summary(lines) -> dict:
    res = {
        'whole': {'start': None, 'end': None},
        'phrase1': {'start': None, 'end': None},
        'phrase2': {'start': None, 'end': None},
        'phrase3': {'start': None, 'end': None},
        'phrase4': {'start': None, 'end': None},
    }
    has_start = find_start(lines)
    if has_start is None:
        return res
    else:
        res['whole']['start'] = has_start

    phrase1 = find_phrase_start(lines, 1)
    if phrase1 is None:
        return res
    else:
        res['phrase1']['start'] = phrase1

    phrase1_done = find_phrase_end(lines, 1)
    if phrase1_done is None:
        return res
    else:
        res['phrase1']['end'] = phrase1_done

    phrase2 = find_phrase_start(lines, 2)
    if phrase2 is None:
        return res
    else:
        res['phrase2']['start'] = phrase2

    phrase2_done = find_phrase_end(lines, 2)
    if phrase2_done is None:
        return res
    else:
        res['phrase2']['end'] = phrase2_done

    phrase3 = find_phrase_start(lines, 3)
    if phrase3 is None:
        return res
    else:
        res['phrase3']['start'] = phrase3

    phrase3_done = find_phrase_end(lines, 3)
    if phrase3_done is None:
        return res
    else:
        res['phrase3']['end'] = phrase3_done

    phrase4 = find_phrase_start(lines, 4)
    if phrase4 is None:
        return res
    else:
        res['phrase4']['start'] = phrase4

    phrase4_done = find_phrase_end(lines, 4)
    if phrase4_done is None:
        return res
    else:
        res['phrase4']['end'] = phrase4_done

    completed = find_complete(lines, find_plot_name(lines))
    if completed is None:
        return res
    else:
        res['whole']['end'] = completed

    return res


class ChiaLog:

    def __init__(self, path):
        with open(path, "r") as file:
            self.lines = file.readlines()

    def find_start(slef) -> Optional[datetime]:
        return find_start(slef.lines)

    def find_id(self) -> Optional[str]:
        return find_id(self.lines)

    def find_phrase(self, phrase: int) -> Optional[datetime]:
        return find_phrase_start(self.lines, phrase)

    def find_plot_name(self) -> Optional[str]:
        return find_plot_name(self.lines)

    def find_complete(self) -> Optional[datetime]:
        plot_name = self.find_plot_name()
        if plot_name is None:
            return None
        else:
            return find_complete(self.lines, plot_name)

    def summary(self) -> dict:
        return summary(self.lines)


class ChiaLogSummary:

    def __init__(self, log):
        self.summary = log.summary()

    def _testDone(self, tag: str) -> bool:
        tag = self.summary[tag]
        if tag['start'] is not None and tag['end'] is not None:
            return True
        else:
            return False

    def _duration(self, tag: str) -> Optional[datetime]:
        tag = self.summary[tag]
        if tag['start'] is not None and tag['end'] is not None:
            return tag['end'] - tag['start']
        else:
            return None

    def isCompleted(self) -> bool:
        return self._testDone('whole')

    def completeDuration(self):
        return self._duration('whole')

    def isPhrase1Done(self) -> bool:
        return self._testDone('phrase1')

    def phrase1Duration(self) -> Optional[datetime]:
        return self._duration('phrase1')

    def isPhrase2Done(self) -> bool:
        return self._testDone('phrase2')

    def phrase2Duration(self) -> Optional[datetime]:
        return self._duration('phrase2')

    def isPhrase3Done(self) -> bool:
        return self._testDone('phrase3')

    def phrase3Duration(self) -> Optional[datetime]:
        return self._duration('phrase3')

    def isPhrase4Done(self) -> bool:
        return self._testDone('phrase4')

    def phrase4Duration(self) -> Optional[datetime]:
        return self._duration('phrase4')


if __name__ == '__main__':
    log = ChiaLog(r"Y:\plot109.log")
    print(log.find_start())
    print(log.find_id())
    print(log.find_phrase(1))
    print(log.find_phrase(2))
    print(log.find_phrase(3))
    print(log.find_phrase(4))
    print(log.find_plot_name())
    print(log.find_complete())
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
