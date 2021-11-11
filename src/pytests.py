import pytest
from tdi import get_county_name
from tdi import get_state_data
import censusapi


def test():
    def get_county_name1():
        return get_county_name()

def test2():
    TN = "Tennessee"
    return get_county_name(TN,47093)

def test3():
    def get_state_data1(states):
        return get_state_data(fips)
        return get_state_data(abbr)
        return get_state_data(counties)
        return get_state_data("Tennessee")