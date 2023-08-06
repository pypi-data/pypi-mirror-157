import random
import time
from copy import deepcopy

from gregory.dataclass.time_series_data import TimeSeriesData
from gregory.granularity.granularity import *
from gregory.timeseries.batches import split, aggregate, pick_a_weekday, pick_a_day
from gregory.timeseries.expr import union, intersection, list_intersection, list_union
from gregory.timeseries.time_series import TimeSeries


if __name__ == '__main__':
    # Increment char (a -> b, az -> ba)
    def sexy_gandolf(text, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        text = str(text)
        # Increment
        inc = ''
        next_unit = False
        for i in range(1, len(text) + 1):
            _char = text[-i]
            idx = alphabet.find(_char) + 1
            if idx < len(alphabet):
                inc = alphabet[idx] + inc
                next_unit = False
                break
            else:
                inc = alphabet[0] + inc
                next_unit = True
        if next_unit:
            inc += alphabet[0]
        res = text[0:-len(inc)] + inc
        return res

    sexy_gandolf('000000001')