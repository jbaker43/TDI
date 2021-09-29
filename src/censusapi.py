import pandas
import us.states
from census import Census
from us import states
import pandas as pd
import os
import json
from datetime import datetime
from datetime import date
from pathlib import Path

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
credential_holder_map = {
    'B23006_001': 'Total',
    'B23006_002': 'Less than high school graduate',
    'B23006_003': 'Less than high school graduate in labor force',
    'B23006_009': 'High school graduate',
    'B23006_010': 'High school graduate in labor force',
    'B23006_016': 'Some college or associate\'s degree',
    'B23006_017': 'Some college or associate\'s degree in labor force',
    'B23006_023': 'Bachelor\'s degree or higher',
    'B23006_024': 'Bachelor\'s degree or higher in labor force',
}

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

    return data_path


def census_api_request(state, county):
    api_key = "e47ca974808081f8978710f433125783362afc45"
    # Supply the Census wrapper with an api key
    c = Census(api_key)
    occupation_table = generate_table(c, state, county, occupation_map, "occupation")
    industry_table = generate_table(c, state, county, industry_map, "industry")
    education_table = generate_table(c, state, county, education_map, "education")
    credential_holder_table = credential_holder(c, state, county, credential_holder_map, "credentials")
    # return an array of pandas data frames
    return [occupation_table, industry_table, education_table, credential_holder_table]


def generate_table(census_api, state, county, codes, data_name, year=2019):
    data_path = cache_expiration(state, county, codes, data_name, year)

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
        margin_of_error = census_api.acs5.state_county(append_in_list(codes, 'M'), state, county)

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

    # Using the occupational data obtained from the Census wrapper, we create a pandas data frame to display the info
    # and then transpose the data frame (DF) to have the occupations be the index of the DF.
    df = pd.DataFrame(categories).transpose()
    # Create a DF for the margin of error
    dm = pd.DataFrame(margin_of_error).transpose()
    # Merging the values from the margin of error DF and creating a new column in our original DF
    df = df.assign(Margin_of_Error=dm.values)
    # Cleaning up the data frame by removing values not useful to the table
    df = df.drop(['state', 'county'])
    df = df.rename(index=lambda code: codes[code[:-1]],
                   # This below line just renames the column header to estimate
                   columns={0: 'Estimate'}
                   )
    # Add column for labor percentages
    df = df.assign(Percent=df['Estimate'] * 100 / df['Estimate'][1:].sum())
    # Rounding the percent column to the hundredths place
    df['Percent'] = df['Percent'].astype(float).round(2)
    # This adds the percent sign but be careful because it casts as a string type
    df['Percent'] = df['Percent'].astype(str) + '%'
    # This adds +/- sign but same as above, be careful as it casts as a string type
    df['Margin_of_Error'] = '+/- ' + df['Margin_of_Error'].astype(str)
    pd.set_option('display.max_columns', None)
    # Sort the values by their estimate
    df = df.sort_values(by='Estimate')
    return df


def append_in_list(list, suffix):
    return [x + suffix for x in list]


def credential_holder(census_api, state, county, codes, data_name):
    current_year = date.today().year
    df_array = []

    for year in range(current_year-4, current_year-1):
        data_path = cache_expiration(state, county, codes, data_name, year=year)

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
                time_elapsed = time_elapsed.total_seconds()/(60 * 60 * 24)
                if time_elapsed > cache_time:
                    os.remove(os.path.join(data_path,'credentials.json'))
                    os.remove(os.path.join(data_path,'creds_last_modified.txt'))

        # Query the margin of error for the above data
        credentials_file_path = os.path.join(data_path, 'credentials.json')

        # Checks if file exists in cache
        if os.path.isfile(credentials_file_path):
            # Load data from cache
            credentials = [json.load(open(credentials_file_path))]
        else:
            # Query data from the census API
            credentials = census_api.acs5.state_county(append_in_list(codes, 'E'), state, county, year=year)

            # Write data to cache for later usage
            json_obj = json.dumps(credentials[0], indent=2)
            with open(credentials_file_path, "w") as outfile:
                outfile.write(json_obj)
            del json_obj

            # Record timestamp of data retrieved for cache expiration
            time_file_path = os.path.join(data_path,
                                          'creds_last_modified.txt')
            with open(time_file_path, "w") as outfile:
                now_str = datetime.strftime(datetime.now(), '%m/%d/%Y %H:%M:%S')
                outfile.write(now_str)

        df = pandas.DataFrame(credentials)
        df = df.drop(columns=['state', 'county'])
        df = df.rename(columns=lambda code: codes[code[:-1]],
                       # This below line just renames the index header to year
                       index={0: year}
                       )
        df_array.append(df)

    pd.set_option('display.max_columns', None)
    df = pd.concat(df_array)

    years = []
    for year in range(current_year-1, current_year+6):
        row = []
        years.append(year)
        for key, value in credential_holder_map.items():
            row.append(df.tail(3)[value].mean())

        row = pd.Series(row, df.columns)
        df = df.append(row, ignore_index=True)


    df = df.tail(7)
    df.index = pd.Series(years)
    df.rename_axis('Year', axis='columns', inplace=True)

    pd.options.display.float_format = '{:,.0f}'.format
    return df


if __name__ == '__main__':
    api_key = "e47ca974808081f8978710f433125783362afc45"
    # Supply the Census wrapper with an api key
    c = Census(api_key)
    credential_holder(c, '47', '065', credential_holder_map)
    census_api_request('01', '001')
