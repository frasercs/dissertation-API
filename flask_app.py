import os
import sys

from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from openpyxl import load_workbook

app = Flask(__name__)
api = Api(app, version='1.0', title='Diagnosis API', description='A simple API to diagnose animals using Bayes Theorem', default= 'Diagnosis API', default_label='Diagnosis API')


diagnosis_model = api.model('Diagnose', {
    'animal': fields.String(required=True, description='The type of animal'),
    'symptoms': fields.List(fields.String, required=True, description='The symptoms shown by the animal')
})


@api.route('/api/diagnose/', methods=['POST'])

@api.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
         params={'animal': 'The type of animal to be diagnosed', 'symptoms': 'The symptoms shown by the animal'})
@api.expect(diagnosis_model)
class diagnose(Resource):
    def post(self):
        # Get the data from the API request
        data = request.get_json()

        # Grab the type of animal it is from the API request data
        animal = data['animal']

        # Grab the list of symptoms from the API request data
        shown_symptoms = data['symptoms']

        # used to store the values of the Bayes calculation before we zip them together in a dictionary with the names of
        # diseases
        results = {}

        # Get the correct data from the data Excel sheet
        likelihoods = get_likelihood_data(animal)

        # Get the list of diseases
        diseases = get_diseases(animal)

        # TODO: alter this down the line to take data from an API request so we don't always
        #  have to assume priors are equal
        # The likelihoods are being populated using equal priors
        prior_likelihoods = {}

        for disease in diseases:
            prior_likelihoods[disease] = 100 / len(diseases)

        for disease in diseases:
            results[disease] = 0.0
            chain_probability = 1.0
            current_likelihoods = likelihoods[disease
            ]
            for s in shown_symptoms:
                presence = shown_symptoms[s]
                if presence == 1:
                    chain_probability *= current_likelihoods[s]
                elif presence == -1:
                    chain_probability *= (1 - current_likelihoods[s])
                posterior = chain_probability * prior_likelihoods[disease]
                results[disease] = (posterior * 100)

        # Normalise the results
        normalised_results = normalise(results)

        return jsonify({'results': normalised_results})

@api.route('/api/data/<string:animal>')

@api.doc(responses={200: 'OK', 400: 'Invalid Argument'})
class diagnosis_data(Resource):
    def get(self, animal):
        # Load the correct Excel sheet
        ws = load_spreadsheet(animal)

        # Get the correct data from the data Excel sheet
        likelihoods = get_likelihood_data(animal)

        # Get the list of diseases
        diseases = get_diseases(animal)

        # Get the list of symptoms
        symptoms = get_symptoms(animal)

        return jsonify({'possible diseases': diseases, 'required symptoms': symptoms, 'likelihoods': likelihoods})

@api.route('/api/matrix/<string:animal>')

@api.doc(responses={200: 'OK', 400: 'Invalid Argument'})
class disease_symptom_matrix(Resource):
    def get(self, animal):
        # Load the correct Excel sheet
        data = get_likelihood_data(animal)
        return jsonify(data)


# A function used to collect the data from the Excel workbook which I manually formatted to ensure the data works.
def get_likelihood_data(animal):
    # Load the correct Excel sheet
    ws = load_spreadsheet(animal)

    # Get the list of symptoms and diseases
    symptoms = get_symptoms(animal)
    diseases = get_diseases(animal)

    # Dictionary which stores the likelihoods of each disease
    likelihoods = {}

    # Counter used to keep track of the current disease
    disease_counter = 0

    # Loop through all rows in the workbook
    for row in ws.rows:
        # Skip the first row as it is just the headers
        if row[0].value == 'Disease':
            disease_counter = 0
            continue

        # Counter used to keep track of the current symptom
        symptom_counter = 0
        # Dictionary which stores the likelihoods of each symptom for the current disease
        current_disease_likelihoods = {}

        # Loop through all cells in each row except the first one as it is the disease name
        for cell in row[1:]:
            chance = cell.value
            current_disease_likelihoods[symptoms[symptom_counter]] = chance
            symptom_counter += 1
        likelihoods[diseases[disease_counter]] = current_disease_likelihoods
        disease_counter += 1

    return likelihoods


def get_diseases(animal):
    # List which stores every given disease
    diseases = []
    ws = load_spreadsheet(animal)
    # Populate the list of diseases
    for row in ws.iter_rows(min_row=2, max_col=1, max_row=ws.max_row):
        for cell in row:
            diseases.append(cell.value)
    return diseases


def get_symptoms(animal):
    # List which stores every given symptom
    symptoms = []
    ws = load_spreadsheet(animal)
    # Populate the list of symptoms
    for col in ws.iter_cols(min_col=2, max_row=1):
        for cell in col:
            symptoms.append(cell.value)
    return symptoms


def load_spreadsheet(animal):
    workbook = load_workbook(filename=os.path.join(sys.path[0], "data.xlsx"))
    return workbook[animal]


# A function used to normalise the outputs of the bayes calculation
def normalise(results):
    normalised_results = {}
    summed_results = sum(results.values())
    for r in results:
        value = results[r]
        norm = value / summed_results
        normalised_results[r] = norm * 100
    return normalised_results


if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)
