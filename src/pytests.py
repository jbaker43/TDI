import pytest
from tdi import get_county_name, get_county_name_full
from tdi import get_state_data

def test_county_name_resolution():
    assert get_county_name("47093").strip() == "Knox County"
    assert get_county_name("47065").strip() == "Hamilton County"
    assert get_county_name("47097").strip() == "Lauderdale County"
    assert get_county_name("47133").strip() == "Overton County"


def test_full_county_name_resolution():
    assert get_county_name_full("47093").strip() == "Knox County, Tennessee"
    assert get_county_name_full("47065").strip() == "Hamilton County, Tennessee"
    assert get_county_name_full("47097").strip() == "Lauderdale County, Tennessee"
    assert get_county_name_full("47133").strip() == "Overton County, Tennessee"
