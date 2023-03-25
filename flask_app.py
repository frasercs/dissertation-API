"""

This file contains the code for the Flask API. It is used to diagnose animals using Bayes Theorem.

"""

from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from data_controller import api as data_ns
from diagnosis_controller import api as diagnosis_ns

# init the api
api = Api(version='1.0', title='Diagnosis API', description='A simple API to diagnose animals using Bayes Theorem.',
          default='Diagnosis API', default_label='Diagnosis API')
# init the flask app
app = Flask(__name__)
# fix the cors issue
CORS(app)
# init the api using factory pattern
api.init_app(app)

api.add_namespace(diagnosis_ns)
api.add_namespace(data_ns)

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run(port=5000)
