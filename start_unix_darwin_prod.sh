#!/bin/bash
export CENSUS_API_KEY="d19843a72adf95bac43d31835bbd3af890e80a86"
export FLASK_APP=src/tdi
flask run --host=0.0.0.0 --port=80
