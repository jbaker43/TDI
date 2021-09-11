import os

import flask
from flask import render_template, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import SelectField

import us
import pandas

SECRET_KEY = os.urandom(32)

app = flask.Flask(__name__, template_folder="templates")
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = SECRET_KEY


def get_state_data():

    # Will stores information about state
    states = dict()

    # Read in a list of counties for all states
    counties_df = pandas.read_csv('data/counties.txt', sep='\t')

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
            counties[row['NAME']] = row['GEOID'][2:]

        # Stores information about a state
        # (which includes nested dictionary of counties)
        states[str(state)] = {
            "abbr": abbr,
            "fips": fips,
            "counties": counties
        }

    return states


def get_state_choices():
    """
    Get (fips, state) tuple for each state
    This is used in flask form choice parameters
    """
    states = get_state_data()
    choices = []
    for key, value in states.items():
        choices.append((key, key))
    return choices


def get_county_choices(state):
    states = get_state_data()
    choices = []
    for key, value in states[state]['counties'].items():
        choices.append((value, key))
    return choices


class State_Form(FlaskForm):
    state = SelectField('State', choices=get_state_choices())


class County_Form(FlaskForm):
    county = SelectField('County', validate_choice=False)


@app.route("/", methods=["GET", "POST"])
def state_query():
    form = State_Form()

    if flask.request.method == 'POST':
        # replace this with an insert into whatever database you're using
        for item in flask.request.form.items():
            if 'state' in item:
                field, state = item
        return redirect(url_for('county_query', state=state))

    return render_template('state.html', form=form)


@app.route('/query/<state>/', methods=["GET", "POST"])
def county_query(state):
    # replace this with a query from whatever database you're using
    form = County_Form()
    print(get_county_choices(state))
    form.county.choices = get_county_choices(state)

    return render_template('county.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)
