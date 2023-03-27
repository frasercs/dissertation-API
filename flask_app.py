"""

This file contains the code for the Flask API. It is used to diagnose animals using Bayes' Theorem.

"""

from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from data_controller import api as data_ns
from diagnosis_controller import api as diagnosis_ns

# set up the api's documentation
api = Api(version='1.0', title='Diagnosis API', description='A simple API to diagnose animals using Bayes\' Theorem. '
                                                            'To view the endpoints, use the drop downs below. <br> The '
                                                            'section titled "Diagnosis" contains the endpoints for '
                                                            'diagnosing an animal. <br>'
                                                            'The section titled "Data" contains the endpoints for '
                                                            'accessing relevant data and obtaining examples of input.'
                                                            '<br> \'Models\' contains information about the formatting '
                                                            'of data required in the payloads for the POST requests.',
          default='Diagnosis API', default_label='Diagnosis API')
# init the flask app
app = Flask(__name__)
# fix the cors issue
CORS(app)
# init the api using factory pattern
api.init_app(app)

# add the namespaces to the api
api.add_namespace(diagnosis_ns)
api.add_namespace(data_ns)

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run(port=5000)
