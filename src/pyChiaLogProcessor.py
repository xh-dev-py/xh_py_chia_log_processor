import re
from datetime import datetime


def __parse_to_datetime(str):
    return datetime.strptime(str[0:19], "%Y-%m-%dT%H:%M:%S")


def find_start(lines):
    try:
        pattern = '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.\\d{3}'
        return next(__parse_to_datetime(re.search(pattern, line)[0]) for line in lines if re.search(pattern, line) is not None)
    except:
        return None


def find_id(lines) -> str:
    try:
        pattern = '^ID: (\\w+)$'
        return next(re.search(pattern, line)[1] for line in lines if re.search(pattern, line) != None)
    except:
        return None


def find_phrase_start(lines, phrase: int) -> datetime:
    def to_datetime(line):
        try:
            print(line)
            timeformat = "%b %d %H:%M:%S %Y"
            return datetime.strptime(line, timeformat)
        except:
            return None

    pattern = "Starting phase 1/4: .* \\w{3} (\\w{3} \\d{2} \\d{2}:\\d{2}:\\d{2} \\d{4})".replace('1', str(phrase))
    return next(to_datetime(re.search(pattern, line)[1]) for line in lines if re.search(pattern, line) is not None)


def find_complete(lines, plot_name: str) -> datetime:
    try:
        pattern = "^(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.\\d{3})[ ]+chia.plotting.create_plots[ ]+.*(<plotName>).*".replace(
            '<plotName>', plot_name)
        return next(__parse_to_datetime(re.search(pattern, line)[1]) for line in lines if re.search(pattern, line) is not None)
    except:
        return None

def find_plot_name(lines):
    id = find_id(lines)
    start = find_start(lines)
    if id is None or start is None:
        return None
    else:
        return "plot-k32-%04d-%02d-%02d-%02d-%02d-%s.plot"%(start.year,start.month,start.day,start.hour,start.minute,id)

class ChiaLog:

    def __init__(self, path):
        with open(path, "r") as file:
            self.lines = file.readlines()

    def find_start(slef):
        return find_start(slef.lines)

    def find_id(self):
        return find_id(self.lines)

    def find_phrase(self, phrase: int):
        return find_phrase_start(self.lines, phrase)

    def find_plot_name(self):
        return find_plot_name(self.lines)

    def find_complete(self):
        plot_name = self.find_plot_name()
        if plot_name is None:
            return None
        else:
            return find_complete(self.lines,plot_name)

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
