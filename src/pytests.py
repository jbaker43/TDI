import pytest
import os
from tdi import get_county_name, get_county_name_full
from tdi import get_state_data
import censusapi

def test_county_name_resolution():
    """
    Test to ensure that a FIPS code resolves to the proper county
    """
    assert get_county_name("47093").strip() == "Knox County"
    assert get_county_name("47065").strip() == "Hamilton County"
    assert get_county_name("47097").strip() == "Lauderdale County"
    assert get_county_name("47133").strip() == "Overton County"


def test_full_county_name_resolution():
    """
    Test to ensure that county names are properly associated with the correct state
    """
    assert get_county_name_full("47093").strip() == "Knox County, Tennessee"
    assert get_county_name_full("47065").strip() == "Hamilton County, Tennessee"
    assert get_county_name_full("47097").strip() == "Lauderdale County, Tennessee"
    assert get_county_name_full("47133").strip() == "Overton County, Tennessee"


def test_api_query():
    """
    Tests the API functionality as well as cache functionality
    Fails if the process is unable to complete
    """
    os.environ['CENSUS_API_KEY'] = 'e47ca974808081f8978710f433125783362afc45'
    censusapi.census_api_request('47', '065')

