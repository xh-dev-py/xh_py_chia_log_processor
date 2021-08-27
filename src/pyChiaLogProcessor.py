import re
from datetime import datetime, timedelta
from typing import Optional


# PROCESS_WHOLE = "whole"
# PROCESS_PHASE_1 = 'phrase1'
# PROCESS_PHASE_2 = 'phrase2'
# PROCESS_PHASE_3 = 'phrase3'
# PROCESS_PHASE_4 = 'phrase4'


def __parse_to_datetime(d_str: str) -> datetime:
    return datetime.strptime(d_str[0:19], "%Y-%m-%dT%H:%M:%S")


def formatDuration(dt: Optional[timedelta]) -> str:
    if dt is None:
        return ""
    else:
        return dt.__str__()


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
        return next(re.search(pattern, line)[1] for line in lines if re.search(pattern, line) is not None)
    except:
        return None


def _to_datetime(line):
    try:
        timeformat = "%b %d %H:%M:%S %Y"
        return datetime.strptime(line, timeformat)
    except:
        return None


def find_phrase_start(lines, phrase: int) -> Optional[datetime]:
    pattern = "Starting phase %d/4: .* \\w{3} (\\w{3} +\\d{1,2} \\d{2}:\\d{2}:\\d{2} \\d{4})" % phrase
    try:
        return next(_to_datetime(re.search(pattern, line)[1]) for line in lines if re.search(pattern, line) is not None)
    except StopIteration:
        return None


def find_phrase_end(lines, phrase: int) -> Optional[datetime]:
    pattern = "Time for phase %d = \\d+\\.\\d+ seconds\\..* \\w{3} (\\w{3} +\\d{1,2} \\d{2}:\\d{2}:\\d{2} \\d{4})" % phrase
    try:
        return next(_to_datetime(re.search(pattern, line)[1]) for line in lines if re.search(pattern, line) is not None)
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


class LogSummaryRecord:
    start: Optional[datetime]
    end: Optional[datetime]
    progress: float

    def __init__(self):
        self.start = None
        self.end = None
        self.progress = round(0, 2)

    def setStart(self, start: Optional[datetime]):
        self.start = start

    def setEnd(self, end: Optional[datetime]):
        self.end = end

    def setProgress(self, progress: float):
        self.progress = progress

    def isCompleted(self) -> bool:
        if self.start is not None and self.end is not None:
            return True
        else:
            return False

    def diff(self) -> Optional[timedelta]:
        if self.start is not None and self.end is not None:
            return self.end - self.start
        else:
            return None

    def testPhraseDone(self) -> bool:
        if self.start is not None and self.end is not None:
            return True
        else:
            return False

    def duration(self) -> Optional[timedelta]:
        if self.start is not None and self.end is not None:
            return self.end - self.start
        else:
            return None


class SummaryContainer:
    whole: LogSummaryRecord = LogSummaryRecord()
    phase1: LogSummaryRecord = LogSummaryRecord()
    phase2: LogSummaryRecord = LogSummaryRecord()
    phase3: LogSummaryRecord = LogSummaryRecord()
    phase4: LogSummaryRecord = LogSummaryRecord()


def summary(lines) -> SummaryContainer:
    res = SummaryContainer()
    has_start = find_start(lines)
    if has_start is None:
        return res
    else:
        res.whole.start = has_start

    phrase1 = find_phrase_start(lines, 1)
    if phrase1 is None:
        return res
    else:
        res.phase1.start = phrase1

    phrase1_done = find_phrase_end(lines, 1)
    if phrase1_done is None:
        return res
    else:
        res.phase1.end = phrase1_done
        res.whole.progress = round(25, 2)
        res.phase1.progress = round(100, 2)

    phrase2 = find_phrase_start(lines, 2)
    if phrase2 is None:
        return res
    else:
        res.phase2.start = phrase2

    phrase2_done = find_phrase_end(lines, 2)
    if phrase2_done is None:
        return res
    else:
        res.phase2.end = phrase2_done
        res.whole.progress = round(50, 2)
        res.phase2.progress = round(100, 2)

    phrase3 = find_phrase_start(lines, 3)
    if phrase3 is None:
        return res
    else:
        res.phase3.start = phrase3

    phrase3_done = find_phrase_end(lines, 3)
    if phrase3_done is None:
        return res
    else:
        res.phase3.end = phrase3_done
        res.whole.progress = round(75, 2)
        res.phase3.progress = round(100, 2)

    phrase4 = find_phrase_start(lines, 4)
    if phrase4 is None:
        return res
    else:
        res.phase4.start = phrase4

    phrase4_done = find_phrase_end(lines, 4)
    if phrase4_done is None:
        return res
    else:
        res.phase4.end = phrase4_done
        res.whole.progress = round(98, 2)
        res.phase4.progress = round(100, 2)

    completed = find_complete(lines, find_plot_name(lines))
    if completed is None:
        return res
    else:
        res.whole.end = completed
        res.whole.progress = round(100, 2)

    return res


class ChiaLog:

    def __init__(self, path):
        with open(path, "r") as file:
            self.lines = file.readlines()

    def find_start(self) -> Optional[datetime]:
        return find_start(self.lines)

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

    def summary(self) -> SummaryContainer:
        return summary(self.lines)


class ChiaLogSummary:

    def __init__(self, log):
        self.summary: SummaryContainer = log.summary()

    def isCompleted(self) -> bool:
        return self.summary.whole.testPhraseDone()

    def completeDuration(self):
        return self.summary.whole.duration()

    def isPhrase1Done(self) -> bool:
        return self.summary.phase1.testPhraseDone()

    def wholeProgress(self) -> float:
        return self.summary.whole.progress

    def phrase1Duration(self) -> Optional[datetime]:
        return self.summary.phase1.duration()

    def phrase1Progress(self) -> float:
        return self.summary.phase1.progress

    def isPhrase2Done(self) -> bool:
        return self.summary.phase2.testPhraseDone()

    def phrase2Duration(self) -> Optional[datetime]:
        return self.summary.phase2.duration()

    def phrase2Progress(self) -> float:
        return self.summary.phase2.progress

    def isPhrase3Done(self) -> bool:
        return self.summary.phase3.testPhraseDone()

    def phrase3Duration(self) -> Optional[datetime]:
        return self.summary.phase3.duration()

    def phrase3Progress(self) -> float:
        return self.summary.phase3.progress

    def isPhrase4Done(self) -> bool:
        return self.summary.phase4.testPhraseDone()

    def phrase4Duration(self) -> Optional[datetime]:
        return self.summary.phase4.duration()

    def phrase4Progress(self) -> float:
        return self.summary.phase4.progress


if __name__ == '__main__':
    log = ChiaLog(r"c:\users\xeth0\plot125.log")
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
