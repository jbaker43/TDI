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
        choices.append((key, key))
    return choices


def get_county_choices(state: str) -> tuple:
    """
    Takes list of counties for a state, and puts them in
    flask-wtf form format.

    Returns: tuple
    """
    choices = []
    for key, value in states_data[state]['counties'].items():
        choices.append((value, key))
    return choices


class State_Form(FlaskForm):
    state = SelectField('State', choices=get_state_choices())


class County_Form(FlaskForm):
    county = SelectField('County', validate_choice=False)


class Table_Form(FlaskForm):
    table = SelectField('Table', validate_choice=False)


@app.route("/", methods=["GET", "POST"])
def state_query():
    form = State_Form()

    if flask.request.method == 'POST':
        for item in flask.request.form.items():
            if 'state' in item:
                field, state = item
        return redirect(url_for('county_query', state=state))

    return render_template('state.html', form=form)


@app.route('/query/<state>/', methods=["GET", "POST"])
def county_query(state):
    form = County_Form()
    form.county.choices = get_county_choices(state)

    if flask.request.method == 'POST':
        for item in flask.request.form.items():
            if 'county' in item:
                field, code = item
        return redirect(url_for('table_query',
                                state=state,
                                county_code=code))

    return render_template('county.html', form=form)


@app.route('/query/<state>/<county_code>', methods=["GET", "POST"])
def table_query(state, county_code):
    """
    This route takes a selected state and county
    and allows a user to choose a table to view
    """
    # Lookup state and get fips code
    s = us.states.lookup(state)
    state_fip = s.fips
    state_name = s.name
    df = censusapi.census_api_request(state_fip, county_code)
    table_title = "Data for " + state_name
    # Turning the pandas dataframes to html to display
    occupation = df[0].to_html(classes='table table-hover table-dark', justify='start')
    industry = df[1].to_html(classes='table table-hover table-dark', justify='start')
    edu = df[2].to_html(classes='table table-hover table-dark', justify='start')
    return render_template('table.html',  tables=[occupation, industry, edu], title=table_title,)


if __name__ == "__main__":
    app.run(debug=True)
