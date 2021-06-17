CHANNEL_DATA = [
    ( 1,  1, 0,  47,  50), # VHF channel 1
    ( 4,  2, 6,  57,  72), # VHF channel range  2~4
    ( 6,  5, 6,  79,  88), # VHF channel range  5~6
    (13,  7, 6, 177, 216), # VHF channel range  7~13
    (99, 14, 6, 473, 999), # UHF channel range 14~xx
]

RANGE_MIN = 2
RANGE_MAX = 51

MHz_to_Hz = 1000000


def min(a, b):
    return a if a < b else b


def max(a, b):
    return a if a > b else a


def coherce_in_range(number):
    return max(min(number, RANGE_MAX), RANGE_MIN)


def channel_to_frequency(number):
    for threshold, base, mul, offset, _ in CHANNEL_DATA:
        if number <= threshold:
            return (number - base) * mul + offset


def frequency_to_channel(frequency):
    frequency_mhz = frequency / 1000000
    for _, base, mul, offset, threshold in CHANNEL_DATA:
        if frequency_mhz <= threshold:
            return (frequency_mhz - offset) / mul + base


class RFChannel(object):
    def __init__(self, number=None, frequencyHz=None):
        if number is not None:
            self.number = coherce_in_range(number)
            self.frequency = channel_to_frequency(self.number)
        elif frequencyHz is not None:
            self.number = frequency_to_channel(frequencyHz)
            self.frequency = frequencyHz / MHz_to_Hz

    def frequencyHz(self):
        return self.frequency * MHz_to_Hz
