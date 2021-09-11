import us.states
from census import Census
from us import states
import pandas as pd

data_tables = {
    'C24050_001E': 'Total',
    'C24050_002E': 'Agriculture, forestry, fishing and hunting, and mining',
    'C24050_003E': 'Construction',
    'C24050_004E': 'Manufacturing',
    'C24050_005E': 'Wholesale trade',
    'C24050_006E': 'Retail trade',
    'C24050_007E': 'Transportation and warehousing, and utilities',
    'C24050_008E': 'Information',
    'C24050_009E': 'Finance and insurance, and real estate, and rental and leasing',
    'C24050_010E': 'Professional, scientific, and management, and administrative, and waste '
                   'management services',
    'C24050_011E': 'Educational services, and health care and social assistance',
    'C24050_012E': 'Arts, entertainment, and recreation, and accommodation and food services',
    'C24050_013E': 'Other services, except public administration',
    'C24050_014E': 'Public administration',
}


def census_api_request(state, county):
    api_key = "e47ca974808081f8978710f433125783362afc45"
    # Supply the Census wrapper with an api key
    c = Census(api_key)

    # Using the Census wrapper to query the Census API and get occupation data. The state is TN  (states.TN.fips returns
    # 47, the number the census uses to represent the state of TN), and the county is Hamilton County (065).
    # NOTE: The data chosen was just to test the wrapper. These values can/should change. We can also change it to
    # accept a user's selected input such as state, county, region, etc.
    occupation = c.acs5.state_county(
        ('NAME', 'C24050_001E', 'C24050_002E', 'C24050_003E', 'C24050_004E', 'C24050_005E', 'C24050_006E',
         'C24050_007E', 'C24050_008E', 'C24050_009E', 'C24050_010E', 'C24050_011E',
         'C24050_012E', 'C24050_013E', 'C24050_014E'), state, county)

    # Query the margin of error for the above data
    margin_of_error = c.acs5.state_county(
        ('NAME', 'C24050_001M', 'C24050_002M', 'C24050_003M', 'C24050_004M', 'C24050_005M',
         'C24050_006M', 'C24050_007M', 'C24050_008M', 'C24050_009M', 'C24050_010M',
         'C24050_011M', 'C24050_012M', 'C24050_013M', 'C24050_014M'),
        state, county)
    # Using the occupational data obtained from the Census wrapper, we create a pandas data frame to display the info
    # and then transpose the data frame (DF) to have the occupations be the index of the DF.
    df = pd.DataFrame(occupation).transpose()
    df = df.rename(index={'C24050_001E': 'Total',
                          'C24050_002E': 'Agriculture, forestry, fishing and hunting, and mining',
                          'C24050_003E': 'Construction',
                          'C24050_004E': 'Manufacturing',
                          'C24050_005E': 'Wholesale trade',
                          'C24050_006E': 'Retail trade',
                          'C24050_007E': 'Transportation and warehousing, and utilities',
                          'C24050_008E': 'Information',
                          'C24050_009E': 'Finance and insurance, and real estate, and rental and leasing',
                          'C24050_010E': 'Professional, scientific, and management, and administrative, and waste '
                                         'management services',
                          'C24050_011E': 'Educational services, and health care and social assistance',
                          'C24050_012E': 'Arts, entertainment, and recreation, and accommodation and food services',
                          'C24050_013E': 'Other services, except public administration',
                          'C24050_014E': 'Public administration'
                          },
                   # This below line just renames the column header to estimate
                   columns={0: 'Estimate'}
                   )
    # Create a DF for the margin of error
    dm = pd.DataFrame(margin_of_error).transpose()
    # Merging the values from the margin of error DF and creating a new column in our original DF
    df = df.assign(Margin_of_Error=dm.values)
    # Cleaning up the data frame by removing values not useful to the table
    df = df.drop(['NAME', 'state', 'county'])
    pd.set_option('display.max_columns', None)
    # Sort the values by their estimate
    df = df.sort_values(by='Estimate')
    print(df)


if __name__ == '__main__':
    census_api_request('01', '001')
