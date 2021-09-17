import us.states
from census import Census
from us import states
import pandas as pd

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


def census_api_request(state, county):
    api_key = "e47ca974808081f8978710f433125783362afc45"
    # Supply the Census wrapper with an api key
    c = Census(api_key)
    occupation_table = generate_table(c, state, county, occupation_map)
    industry_table = generate_table(c, state, county, industry_map)

    return occupation_table

def generate_table(census_api, state, county, codes):
    # Using the Census wrapper to query the Census API and get occupation data. The state is TN  (states.TN.fips returns
    # 47, the number the census uses to represent the state of TN), and the county is Hamilton County (065).
    # NOTE: The data chosen was just to test the wrapper. These values can/should change. We can also change it to
    # accept a user's selected input such as state, county, region, etc.
    categories = census_api.acs5.state_county(append_in_list(codes, 'E'), state, county)
    # Query the margin of error for the above data
    margin_of_error = census_api.acs5.state_county(append_in_list(codes, 'M'), state, county)
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
    df = df.assign(Percent=df['Estimate']*100/df['Estimate'][1:].sum())
    pd.set_option('display.max_columns', None)
    # Sort the values by their estimate
    df = df.sort_values(by='Estimate')
    print(df)
    return df


def append_in_list(list, suffix):
    return [x + suffix for x in list]


if __name__ == '__main__':
    census_api_request('01', '001')
