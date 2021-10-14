import os
from pathlib import Path
import us
import pandas as pd
from census import Census
import json
from datetime import datetime, date


industry_map = {
    'C24050_001': 'Total',
    'C24050_002': 'Agriculture, forestry, fishing and hunting, and mining',
    'C24050_003': 'Construction',
    'C24050_004': 'Manufacturing',
    'C24050_005': 'Wholesale trade',
    'C24050_006': 'Retail trade',
    'C24050_007': 'Transportation and warehousing, and utilities',
    'C24050_008': 'Information',
    'C24050_009': 'Finance and insurance, and real estate, and rental and leasing',
    'C24050_010': 'Professional, scientific, and management, and administrative, and waste '
                  'management services',
    'C24050_011': 'Educational services, and health care and social assistance',
    'C24050_012': 'Arts, entertainment, and recreation, and accommodation and food services',
    'C24050_013': 'Other services, except public administration',
    'C24050_014': 'Public administration',
}

occupation_map = {
    'C24060_001': 'Total',
    'C24060_002': 'Management, business, science, and arts occupations',
    'C24060_003': 'Service occupations',
    'C24060_004': 'Sales and office occupations',
    'C24060_005': 'Natural resources, construction, and maintenance occupations',
    'C24060_006': 'Production, transportation, and material moving occupations',
}
education_map = {
        'B15003_001': 'Total',
        'B15003_002': 'No Schooling Completed',
        'B15003_003': 'Nursery School',
        'B15003_004': 'Kindergarten',
        'B15003_005': '1st grade',
        'B15003_006': '2nd grade',
        'B15003_007': '3rd grade',
        'B15003_008': '4th grade',
        'B15003_009': '5th grade',
        'B15003_010': '6th grade',
        'B15003_011': '7th grade',
        'B15003_012': '8th grade',
        'B15003_013': '9th grade',
        'B15003_014': '10th grade',
        'B15003_015': '11th grade',
        'B15003_016': '12th grade, no diploma',
        'B15003_017': 'Regular high school diploma',
        'B15003_018': 'GED or alternative credential',
        'B15003_019': 'Some college, less than 1 year',
        'B15003_020': 'Some college, 1 or more years, no degree',
        'B15003_021': 'Associate\'s degree',
        'B15003_022': 'Bachelor\'s degree',
        'B15003_023': 'Master\'s degree',
        'B15003_024': 'Professional school degree',
        'B15003_025': 'Doctorate degree',
}


def cache_expiration(state, county, codes, data_name, year=date.today().year):
    if os.path.isdir(Path('../data/')):
        data_path = os.path.join('../data/census_data/', str(year),
                                 state, county, data_name)
    elif os.path.isdir('data/'):
        data_path = os.path.join('data/census_data/', str(year),
                                 state, county, data_name)
    else:
        raise FileNotFoundError("Data path is not found")

    data_path = Path(data_path)

    # Ensure that data path exists, if it doesn't already
    os.makedirs(data_path, exist_ok=True)

    names = ['occupation', 'industry', 'education']

    if data_name in names:
        # Ensures that cached data is not older than 6 months
        # If timestamp is found, it will read in the date listed.
        # If the date was over 24 hours ago, the files are deleted so they can
        # be re-queried in the next step.
        time_file_path = os.path.join(data_path, 'cat_last_modified.txt')
        if os.path.isfile(time_file_path):
            with open(time_file_path) as file:
                time_str = file.read()
                timestamp = datetime.strptime(time_str, '%m/%d/%Y %H:%M:%S')
                time_elapsed = datetime.now() - timestamp
                # Converts seconds to days
                time_elapsed = time_elapsed.total_seconds() / (60 * 60 * 24)
                if time_elapsed > cache_time:
                    os.remove(os.path.join(data_path, 'categories.json'))
                    os.remove(os.path.join(data_path, 'cat_last_modified.txt'))

        # Ensures that cached data is not older than 1 day
        # If timestamp is found, it will read in the date listed.
        # If the date was over 24 hours ago, the files are deleted so they can
        # be re-queried in the next step.
        time_file_path = os.path.join(data_path, 'margin_last_modified.txt')
        if os.path.isfile(time_file_path):
        with open(time_file_path) as file:
        time_str = file.read()
        timestamp = datetime.strptime(time_str, '%m/%d/%Y %H:%M:%S')
        time_elapsed = datetime.now() - timestamp
        time_elapsed = time_elapsed.total_seconds() / (60 * 60 * 24)
        if time_elapsed > cache_time:
            os.remove(os.path.join(data_path, 'margin_of_error.json'))
            os.remove(os.path.join(data_path,
                                   'margin_last_modified.txt'))

    elif data_name == "credentials":
        # Ensures that cached data is not older than 1 day
        # If timestamp is found, it will read in the date listed.
        # If the date was over 24 hours ago, the files are deleted so they can
        # be re-queried in the next step.
        time_file_path = os.path.join(data_path, 'creds_last_modified.txt')
        if os.path.isfile(time_file_path):
            with open(time_file_path) as file:
                time_str = file.read()
                timestamp = datetime.strptime(time_str, '%m/%d/%Y %H:%M:%S')
                time_elapsed = datetime.now() - timestamp
                # Converts seconds to days
                time_elapsed = time_elapsed.total_seconds() / (60 * 60 * 24)
                if time_elapsed > cache_time:
                    os.remove(os.path.join(data_path, 'credentials.json'))
                    os.remove(os.path.join(data_path,
                                           'creds_last_modified.txt'))

    return data_path


def append_in_list(list, suffix):
    return [x + suffix for x in list]


def get_state_data() -> dict:
    """
    This function creates a dictionary of information about
    a state.
    Specifically, this collects a states FIPS code, abbreviation,
    and all its counties.

    Returns: dictionary
    """

    # Will stores information about state
    states = dict()

    # Read in a list of counties for all states
    if os.path.exists(Path('data/counties.txt')):
        counties_df = pd.read_csv(Path('data/counties.txt'), sep='\t')
    elif os.path.exists(Path('../data/counties.txt')):
        counties_df = pd.read_csv(Path('../data/counties.txt'), sep='\t')
    else:
        raise FileNotFoundError("county data file not found")

    # Converts GEOID to string for easier data manipulation
    counties_df['GEOID'] = counties_df['GEOID'].apply(str)

    # Iterates across all the states
    for state in us.states.STATES:
        # Gets the FIPS code and USPS abbreviation
        fips = state.fips
        abbr = state.abbr

        # Creates empty county dictionary for later data storage
        counties = {}

        # Filters list of counties to only those from this state
        df = counties_df[counties_df['USPS'].apply(
            lambda x: x.startswith(abbr))]

        # Removes leading digits from GEOID as this is needed for census query
        for index, row in df.iterrows():
            counties[row['NAME']] = row['GEOID'][-3:]

        # Stores information about a state
        # (which includes nested dictionary of counties)
        states[str(state)] = {
            "abbr": abbr,
            "fips": fips,
            "counties": counties
        }

    return states


def generate_table(census_api, state, county, codes, data_name, year=2019):
    # How long data can remain in cache before refresh
    # stored in days.
    cache_time = 182


    if os.path.isdir(Path('../data/')):
        data_path = os.path.join('../data/census_data/', str(year),
                                 state, county, data_name)
    elif os.path.isdir('data/'):
        data_path = os.path.join('data/census_data/', str(year),
                                 state, county, data_name)
    else:
        raise FileNotFoundError("Data path is not found")

    data_path = Path(data_path)

    # Ensure that data path exists, if it doesn't already
    os.makedirs(data_path, exist_ok=True)

    # Ensures that cached data is not older than 1 day
    # If timestamp is found, it will read in the date listed.
    # If the date was over 24 hours ago, the files are deleted so they can
    # be re-queried in the next step.
    time_file_path = os.path.join(data_path, 'cat_last_modified.txt')
    if os.path.isfile(time_file_path):
        with open(time_file_path) as file:
            time_str = file.read()
            timestamp = datetime.strptime(time_str, '%m/%d/%Y %H:%M:%S')
            time_elapsed = datetime.now() - timestamp
            # Converts seconds to days
            time_elapsed = time_elapsed.total_seconds()/(60 * 60 * 24)
            if time_elapsed > cache_time:
                os.remove(os.path.join(data_path,'categories.json'))
                os.remove(os.path.join(data_path,'cat_last_modified.txt'))


    # Ensures that cached data is not older than 1 day
    # If timestamp is found, it will read in the date listed.
    # If the date was over 24 hours ago, the files are deleted so they can
    # be re-queried in the next step.
    time_file_path = os.path.join(data_path, 'margin_last_modified.txt')
    if os.path.isfile(time_file_path):
        with open(time_file_path) as file:
            time_str = file.read()
            timestamp = datetime.strptime(time_str, '%m/%d/%Y %H:%M:%S')
            time_elapsed = datetime.now() - timestamp
            # Converts seconds to days
            time_elapsed = time_elapsed.total_seconds()/(60 * 60 * 24)
            if time_elapsed > cache_time:
                os.remove(os.path.join(data_path,'margin_of_error.json'))
                os.remove(os.path.join(data_path,'margin_last_modified.txt'))


    # Using the Census wrapper to query the Census API and get occupation data. The state is TN  (states.TN.fips returns
    # 47, the number the census uses to represent the state of TN), and the county is Hamilton County (065).
    # NOTE: The data chosen was just to test the wrapper. These values can/should change. We can also change it to
    # accept a user's selected input such as state, county, region, etc.

    # Creates path for where data should be stored
    cat_file_path = os.path.join(data_path, 'categories.json')

    # Checks if file exists in cache
    if os.path.isfile(cat_file_path):
        # Load data from cache
        categories = [json.load(open(cat_file_path))]
    else:
        # Query data from the census API
        categories = census_api.acs5.state_county(append_in_list(codes, 'E'), state, county)

        # Write data to cache for later usage
        json_obj = json.dumps(categories[0], indent = 2)
        with open(cat_file_path, "w") as outfile:
            outfile.write(json_obj)
        del json_obj

        # Record timestamp of data retrieved for cache expiration
        time_file_path = os.path.join(data_path,
                                      'cat_last_modified.txt')
        with open(time_file_path, "w") as outfile:
            now_str = datetime.strftime(datetime.now(),'%m/%d/%Y %H:%M:%S')
            outfile.write(now_str)

    # Query the margin of error for the above data
    margin_file_path = os.path.join(data_path, 'margin_of_error.json')

    # Checks if file exists in cache
    if os.path.isfile(margin_file_path):
        # Load data from cache
        margin_of_error = [json.load(open(margin_file_path))]
    else:
        # Query data from the census API
        margin_of_error = census_api.acs5.state_county(append_in_list(codes, 'M'), state, county)

        # Write data to cache for later usage
        json_obj = json.dumps(margin_of_error[0], indent = 2)
        with open(margin_file_path, "w") as outfile:
            outfile.write(json_obj)
        del json_obj

        # Record timestamp of data retrieved for cache expiration
        time_file_path = os.path.join(data_path,
                                      'margin_last_modified.txt')
        with open(time_file_path, "w") as outfile:
            now_str = datetime.strftime(datetime.now(),'%m/%d/%Y %H:%M:%S')
            outfile.write(now_str)


def credential_holder(census_api, state, county, codes, data_name):
    current_year = date.today().year
    df_array = []
    years = []

    for year in range(current_year - 4, current_year - 1):
        data_path = cache_expiration(state, county, codes,
                                     data_name, year=year)

        # Query the margin of error for the above data
        credentials_file_path = os.path.join(data_path, 'credentials.json')

        # Checks if file exists in cache
        if os.path.isfile(credentials_file_path):
            # Load data from cache
            credentials = [json.load(open(credentials_file_path))]
        else:
            # Query data from the census API
            credentials = census_api.acs5.state_county(
                append_in_list(codes, 'E'), state, county, year=year)

            # Write data to cache for later usage
            json_obj = json.dumps(credentials[0], indent=2)
            with open(credentials_file_path, "w") as outfile:
                outfile.write(json_obj)
            del json_obj

            # Record timestamp of data retrieved for cache expiration
            time_file_path = os.path.join(data_path,
                                          'creds_last_modified.txt')
            with open(time_file_path, "w") as outfile:
                now_str = datetime.strftime(datetime.now(),
                                            '%m/%d/%Y %H:%M:%S')
                outfile.write(now_str)

        df = pd.DataFrame(credentials)
        df = df.drop(columns=['state', 'county'])
        df = df.rename(columns=lambda code: codes[code[:-1]],
                       # This below line just renames the index header to year
                       index={0: year}
                       )
        df_array.append(df)
        years.append(year)

    pd.set_option('display.max_columns', None)
    df = pd.concat(df_array)

    for year in range(current_year - 1, current_year + 6):
        row = []
        years.append(year)
        for key, value in credential_holder_map.items():
            row.append(df.tail(3)[value].mean())

        row = pd.Series(row, df.columns)
        df = df.append(row, ignore_index=True)

    df.index = pd.Series(years)
    df.rename_axis('Year', axis='columns', inplace=True)

    df = df.tail(7)

    pd.options.display.float_format = '{:,.0f}'.format
    return df


def census_api_request(state, county, year=2019):
    api_key = "e47ca974808081f8978710f433125783362afc45"
    # Supply the Census wrapper with an api key
    c = Census(api_key, year)
    occupation_table = generate_table(c, state, county, occupation_map, "occupation", year)
    industry_table = generate_table(c, state, county, industry_map, "industry", year)
    education_table = generate_table(c, state, county, education_map, "education", year)
    cred_table = credential_holder(c, state, county, credential_holder_map, "credentials")
    # return an array of pandas data frames
    return [occupation_table, industry_table, education_table, cred_table]


if __name__ == "__main__":
    current_year = date.today().year
    states = get_state_data()

    for year in range(current_year-4, current_year-1):
        for state_key, state_value in states.items():
            for county_key, county_value in state_value['counties'].items():
                print(str(year) + " | Caching " + county_key + ", " + state_key)
                try:
                    census_api_request(state_value['fips'], county_value, year)
                except:
                    print("Caching failed for " + county_key + ", " + state_key)

