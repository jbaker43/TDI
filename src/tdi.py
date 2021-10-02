import os
from pathlib import Path
import flask
import us
import pandas
import censusapi
from flask import render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import SelectField, FieldList, StringField, HiddenField

SECRET_KEY = os.urandom(32)

app = flask.Flask(__name__, template_folder="templates")
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = SECRET_KEY

states_data = None


def get_state_data(reload=False) -> dict:
    """
    This function creates a dictionary of information about
    a state.
    Specifically, this collects a states FIPS code, abbreviation,
    and all its counties.
    If reload, then data will re-read from system.

    Returns: dictionary
    """

    if states_data and not reload:
        return

    # Will stores information about state
    states = dict()

    # Read in a list of counties for all states
    if os.path.exists(Path('data/counties.txt')):
        counties_df = pandas.read_csv(Path('data/counties.txt'), sep='\t')
    elif os.path.exists(Path('../data/counties.txt')):
        counties_df = pandas.read_csv(Path('../data/counties.txt'), sep='\t')
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

        for index, row in df.iterrows():
            counties[row['GEOID'].zfill(5)] = {
                "state": state,
                "name": row['NAME']
            }


        states[state.fips] = {
            "abbr": abbr,
            "name": state.name,
            "counties": counties,
            "enum": state
        }

    return states

def get_county_name(county):
    state = county[0:2]
    return states_data[state]['counties'][county]['name']

def get_county_name_full(county):
    state = county[0:2]
    return get_county_name(county) + ", " + states_data[state]['name']

def to_fips(state):
    return us.states.lookup(state).fips

def get_state_name(state):
    return us.states.lookup(state).name

def add_code(code_base, new_code):
    if new_code in code_base.split('|'):
        return code_base
    code = code_base
    if code_base:
        code += '|'
    code += new_code
    return code

def get_state_choices() -> tuple:
    """
    Get (fips, state) tuple for each state
    This is used in flask form choice parameters

    Returns: tuple
    """
    global states_data
    if states_data is None:
        states_data = get_state_data()
    choices = []
    for key, value in states_data.items():
        choices.append((key, get_state_name(key)))
    return choices

def get_county_choices(state: str) -> tuple:
    """
    Takes list of counties for a state, and puts them in
    flask-wtf form format.

    Returns: tuple
    """
    choices = []
    for key, value in states_data[state]['counties'].items():
        choices.append((key, value['name'] + ", " + value['state'].name))
    return choices

class State_Form(FlaskForm):
    state_choices = get_state_choices()
    county_choices = [county for state in states_data for county in get_county_choices(state)]
    state = SelectField('State', choices=state_choices, id='state_select')
    county = SelectField('County', choices=county_choices, id='county_select')

    selected_counties = FieldList(StringField('County', render_kw={'readonly': True}), [])
    codes = HiddenField('codes')

class Table_Form(FlaskForm):
    table = SelectField('Table', validate_choice=False)

@app.route("/", methods=["GET", "POST"])
def query():
    if flask.request.args and flask.request.args['fips']:
        form = State_Form(codes=flask.request.args['fips'])
    else:
        form = State_Form()

    if flask.request.method == 'POST':
        county = flask.request.form.get('county')
        state = flask.request.form.get('state')
        fips = flask.request.form.get('codes')
        if not county or not state: return

        if flask.request.form.get('submit'):
            return redirect(url_for('table_query', fips_url=fips))
        elif flask.request.form.get('add_county'):
            fips = add_code(fips, county)
            return redirect(url_for('query', fips=fips))
        else:
            raise Exception('Unsupported form action')

    elif flask.request.method == 'GET':
        if request.args and request.args['fips']:
            fill_selected_counties(form, request.args['fips'])
    else:
        raise Exception('Unsupported HTTP request method: ' + flask.request.method)

    return render_template('state.html', form=form)

def fill_selected_counties(form, fips):
    counties = fips.split('|')
    for county in counties:
        print(county)
        form.selected_counties.append_entry(get_county_name_full(county))

@app.route('/query/<fips_url>', methods=["GET", "POST"])
def table_query(fips_url):
    """
    This route takes a selected state and county
    and allows a user to choose a table to view
    """

    fips = fips_url.split('|')
    table_sums = None
    titles = []
    for code in fips:
        titles.append(get_county_name(code))
    table_title = 'Data for ' + ', '.join(titles)
    total = [] # For recalculating percentage

    for code in fips:
        print(code)

        # Lookup state and get fips code
        state = code[0:2]
        county = code[2:]
        s = us.states.lookup(state)
        state_fip = s.fips
        state_name = s.name
        county_name = get_county_name(code) 

        df = censusapi.census_api_request(state_fip, county)
        if table_sums:
            for i in range(len(table_sums)):
                table_sums[i]['Estimate'] += df[i]['Estimate']
                table_sums[i]['Margin_of_Error'] += df[i]['Margin_of_Error']
                total[i] += df[i]['Estimate'][-1]
        else:
            for i in range(len(df)):
                df[i]['Percent'].multiply(df[i]['Estimate'][-1] / 100)
                total.append(df[i]['Estimate'][-1])
            else:
                table_sums = df

    # Recalculate percentage
    print('total', total)
    for i in range(len(table_sums)):
        table_sums[i]['Percent'].multiply(total[i] / 100)

    # Formatting the columns was moved from censusapi.py to here, because you
    # can't add symbols. This should probably still move further forward
    for table in table_sums:
        table['Estimate'] = table['Estimate'].map(int).map('{:d}'.format)
        table['Margin_of_Error'] = table['Margin_of_Error'].map(int).map('±{:d}'.format)
        table['Percent'] = table['Percent'].map('{:.2f}%'.format)

    # Turning the pandas dataframes to html to display
    for i in range(len(table_sums)):
        table_sums[i] = table_sums[i].to_html(classes='table table-hover table-dark', justify='start')

    return render_template('table.html', tables=table_sums, title=table_title)

@app.route('/county_list/<state>')
def county_list(state):
    if state == "all":
        counties = dict([item for state in states_data for item in states_data[state]['counties'].items()])
    else:
        counties = dict([(key, value['name']) for (key, value) in states_data[state]['counties'].items()])
    return counties

if __name__ == "__main__":
    app.run(debug=True)
