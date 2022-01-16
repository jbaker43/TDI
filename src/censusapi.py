from census import Census
import pandas as pd
import os
import json
from datetime import datetime, date
from pathlib import Path
import pathlib
import csv

def load_map(filename):
    map = dict()
    with open(filename) as file:
        scanner = csv.DictReader(file)
        for row in scanner:
            map[row['key']] = row['value']
    return map

table_path = os.path.join(pathlib.Path(__file__).parent.resolve(), 'static/tables')
industry_map = load_map(os.path.join(table_path, 'industry.csv'))
occupation_map = load_map(os.path.join(table_path, 'occupation.csv'))
education_map = load_map(os.path.join(table_path, 'education.csv'))
credential_holder_map = load_map(os.path.join(table_path, 'credential_holder.csv'))

# How long data can remain in cache before refresh
# stored in days.
cache_time = 182


def cache_expiration(state, county, codes,
                     data_name, year=date.today().year):
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


def census_api_request(state, county):
    # Supply the Census wrapper with an api key
    c = Census(os.getenv('CENSUS_API_KEY'))
    occ_table = generate_table(c, state, county, occupation_map, "occupation")
    ind_table = generate_table(c, state, county, industry_map, "industry")
    edu_table = generate_table(c, state, county, education_map, "education")
    cred_table = credential_holder(c, state, county, credential_holder_map,
                                   "credentials")
    # return an array of pandas data frames
    return [occ_table, ind_table, edu_table, cred_table]


def generate_table(census_api, state, county, codes, data_name, year=2019):
    data_path = cache_expiration(state, county, codes, data_name, year)

    # Using the Census wrapper to query the Census API and get occupation data.
    # The state is TN  (states.TN.fips returns 47, the number the census uses
    # to represent the state of TN), and the county is Hamilton County (065).
    # NOTE: The data chosen was just to test the wrapper. These values
    # can/should change. We can also change it to accept a user's selected
    # input such as state, county, region, etc.

    # Creates path for where data should be stored
    cat_file_path = os.path.join(data_path, 'categories.json')

    # Checks if file exists in cache
    if os.path.isfile(cat_file_path):
        # Load data from cache
        categories = [json.load(open(cat_file_path))]
    else:
        # Query data from the census API
        categories = census_api.acs5.state_county(
            append_in_list(codes, 'E'), state, county)

        # Write data to cache for later usage
        json_obj = json.dumps(categories[0], indent=2)
        with open(cat_file_path, "w") as outfile:
            outfile.write(json_obj)
        del json_obj

        # Record timestamp of data retrieved for cache expiration
        time_file_path = os.path.join(data_path,
                                      'cat_last_modified.txt')
        with open(time_file_path, "w") as outfile:
            now_str = datetime.strftime(datetime.now(), '%m/%d/%Y %H:%M:%S')
            outfile.write(now_str)

    # Query the margin of error for the above data
    margin_file_path = os.path.join(data_path, 'margin_of_error.json')

    # Checks if file exists in cache
    if os.path.isfile(margin_file_path):
        # Load data from cache
        margin_of_error = [json.load(open(margin_file_path))]
    else:
        # Query data from the census API
        margin_of_error = census_api.acs5.state_county(
            append_in_list(codes, 'M'), state, county)

        # Write data to cache for later usage
        json_obj = json.dumps(margin_of_error[0], indent=2)
        with open(margin_file_path, "w") as outfile:
            outfile.write(json_obj)
        del json_obj

        # Record timestamp of data retrieved for cache expiration
        time_file_path = os.path.join(data_path,
                                      'margin_last_modified.txt')
        with open(time_file_path, "w") as outfile:
            now_str = datetime.strftime(datetime.now(), '%m/%d/%Y %H:%M:%S')
            outfile.write(now_str)

    # Using the occupational data obtained from the Census wrapper,
    # we create a pandas data frame to display the info
    # and then transpose the data frame (DF) to have the occupations be the
    # index of the DF.
    df = pd.DataFrame(categories).transpose()
    # Create a DF for the margin of error
    dm = pd.DataFrame(margin_of_error).transpose()
    # Merging the values from the margin of error DF and creating a new column
    # in our original DF
    df = df.assign(Margin_of_Error=dm.values)
    # Cleaning up the data frame by removing values not useful to the table
    df = df.drop(['state', 'county'])
    df = df.rename(index=lambda code: codes[code[:-1]],
                   # This below line just renames the column header to estimate
                   columns={0: 'Estimate'}
                   )
    # Add column for labor percentages
    df = df.assign(Percent=df['Estimate'] * 100 / df['Estimate'][1:].sum())
    pd.set_option('display.max_columns', None)
    # Sort the values by their estimate
    df = df.sort_values(by='Estimate')
    df.rename_axis('Category', axis='columns', inplace=True)
    return df


def append_in_list(list, suffix):
    return [x + suffix for x in list]


def credential_holder(census_api, state, county, codes, data_name):
    current_year = date.today().year
    df_array = []
    years = []
#Range of 4 years to query- threw exception since 2021 was not available yet. (was current year -4 and -1) We might decide on better implementation.
    for year in range(current_year - 5, current_year - 2):
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
#No comment but this looks like it is for future predictions.
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


if __name__ == '__main__':
    # Supply the Census wrapper with an api key
    c = Census(os.getenv('CENSUS_API_KEY'))
    credential_holder(c, '47', '065', credential_holder_map)
    census_api_request('01', '001')
