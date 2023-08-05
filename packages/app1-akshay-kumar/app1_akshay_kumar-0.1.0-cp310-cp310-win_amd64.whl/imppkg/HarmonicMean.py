import sys
from imppkg.hello import HarmonicMean
from typing import List


def main():
    res = 0.0
    list: List[float] = []
    # arr: List[str] = sys.argv
    try:
        list = [float(i) for i in sys.argv[1:]]
    except ValueError:
        list = []

    try:
        res = HarmonicMean(list)
    except ZeroDivisionError:
        pass
    print(str(res))
