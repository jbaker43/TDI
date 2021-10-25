import os
from pathlib import Path
import flask
import us
import pandas
import censusapi
from flask import render_template, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import SelectField

SECRET_KEY = os.urandom(32)

app = flask.Flask(__name__, template_folder="templates")
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = SECRET_KEY

states_data = None


def get_state_data(reload=False) -> dict:
    """
    This function creates a dictionary of information about
    a state.

    A state is represented by a 2-digit FIPS code. This maps to it's name,
    postal abbreviation, list of counties, and the object representing the
    state in the us package.
    Each county is a 5-digit FIPS code which is a combination of it's two-digit
    state FIPS code and it's additional 3 digits. Counties map to it's us
    package object and it's name

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
    """
    Maps a 5-digit FIPS code to the county's name
    """
    state = county[0:2]
    return states_data[state]['counties'][county]['name']


def get_county_name_full(county):
    """
    Maps a 5-digit FIPS code to it's name followed by the state's name
    """
    state = county[0:2]
    return get_county_name(county) + ", " + states_data[state]['name']


def to_fips(state):
    """
    Returns the 2-digit FIPS code for a state
    """
    return us.states.lookup(state).fips


def get_state_name(state):
    """
    Maps a 2-digit FIPS code to the state's name
    """
    return us.states.lookup(state).name


def add_code(code_base, new_code):
    """
    Takes a pipe-delimited string of FIPS codes and appends another to the end
    if it isn't already there
    """
    if new_code in code_base.split('|'):
        return code_base
    code = code_base
    if code_base:
        code += '|'
    code += new_code
    return code


def remove_code(code_base, old_code):
    """
    Take a pipe-delimited string of FIPS codes and removes the given one if
    it's already there
    """
    codes = code_base.split('|')
    if old_code in codes:
        codes.remove(old_code)
    return '|'.join(codes)


def get_remove_action(request):
    """
    Returns the name of the button that was pressed if that button corresponds
    to removal of a county
    """
    for key in request.form:
        if key.startswith('remove_'):
            return key
    return None


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
    county_choices = [county
                      for state in states_data
                      for county in get_county_choices(state)]
    state = SelectField('State', choices=state_choices, id='state_select')
    county = SelectField('County', choices=county_choices, id='county_select')


class Table_Form(FlaskForm):
    table = SelectField('Table', validate_choice=False)


@app.route("/", methods=["GET", "POST"])
def query():
    """
    Displays the state and county select screen.
    FIPS codes can be provided via the URL parameter fips in the form of
    a pipe-delimited string. Ex: '/?fips=10001,10002' selects two counties
    """
    form = State_Form()

    if flask.request.method == 'POST':
        county = flask.request.form.get('county')
        state = flask.request.form.get('state')
        to_remove = get_remove_action(flask.request)
        if not county or not state:
            return
        fips = ''
        if flask.request.args and 'fips' in flask.request.args:
            fips = flask.request.args['fips']
        if flask.request.form.get('submit'):
            return redirect(url_for('table_query', fips_url=fips))
        elif flask.request.form.get('add_county'):
            fips = add_code(fips, county)
            return redirect(url_for('query', fips=fips))
        elif to_remove:
            fips = remove_code(fips, to_remove[-5:])
            if fips:
                return redirect(url_for('query', fips=fips))
            else:
                return redirect(url_for('query'))
        else:
            raise Exception('Unsupported form action')

    elif flask.request.method == 'GET':
        pass
    else:
        raise Exception('Unsupported HTTP request: ' + flask.request.method)

    return render_template('state.html', form=form, states=states_data)


@app.route('/query/<fips_url>', methods=["GET", "POST"])
def table_query(fips_url):
    """
    This route takes a selected state and county
    and allows a user to choose a table to view
    """

    codes = fips_url.split('|')
    table_sums = None
    titles = []
    for code in codes:
        titles.append(get_county_name(code))
    table_title = 'Data for ' + ', '.join(titles)
    totals = []  # For recalculating percentages

    for code in codes:
        # Lookup state and get fips code
        state_code = code[0:2]
        county_code = code[2:]
        skip_adding = ['Year']

        df = censusapi.census_api_request(state_code, county_code)
        if not totals:
            totals = [0] * len(df)  # Up to one total for each table

        # We are assuming that any table with 'Percent' also has 'Estimate'
        for i in range(len(df)):
            if 'Percent' in df[i].columns:
                df[i]['Percent'] *= df[i]['Estimate'][-1]
                totals[i] += df[i]['Estimate'][-1]

        if table_sums:
            for i in range(len(table_sums)):
                for column in table_sums[i]:
                    if column not in skip_adding:
                        table_sums[i][column] += df[i][column]
        else:
            for i in range(len(df)):
                table_sums = df

    # Recalculate percentage
    for i in range(len(table_sums)):
        if 'Percent' in table_sums[i].columns:
            norm_factor = totals[i]
            table_sums[i]['Percent'] = table_sums[i]['Percent'] \
                .divide(norm_factor)

    # Formatting the columns was moved from censusapi.py to here, because you
    # can't add symbols. This should probably still move further forward
    format_margin = lambda x: '±{:d}'.format(int(x))
    format_percent = lambda x: '{:.2f}%'.format(x)
    for table in table_sums:
        if 'Margin_of_Error' in table:
            table['Margin_of_Error'] = table['Margin_of_Error'] \
                .map(format_margin)
        if 'Percent' in table:
            table['Percent'] = table['Percent'].map(format_percent)

    # Turning the pandas dataframes to html to display
    classes = 'table table-hover table-dark'
    for i in range(len(table_sums)):
        table_sums[i] = table_sums[i].to_html(classes=classes, justify='start')

    return render_template('table.html', tables=table_sums, title=table_title)


@app.route('/county_list/<state>')
def county_list(state):
    """
    Returns a list of counties given a state.
    This is used for generating the county dropdown on the state,county
    selection screen.
    """
    # There _must_ be a better way of doing this
    items = states_data[state]['counties'].items()
    if state == "all":
        counties = dict([county for state in states_data for county in items])
    else:
        counties = dict([(key, value['name']) for (key, value) in items])
    return counties


if __name__ == "__main__":
    app.run(debug=True)
