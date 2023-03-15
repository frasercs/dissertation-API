import os
import sys
from typing import Dict, List, Union

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from openpyxl import load_workbook
from werkzeug.exceptions import BadRequest

# load the Excel file
wb = load_workbook(filename=os.path.join(sys.path[0], "data.xlsx"))

# init the api
api = Api(version='1.0', title='Diagnosis API', description='A simple API to diagnose animals using Bayes Theorem.',
          default='Diagnosis API', default_label='Diagnosis API')
# init the flask app
app = Flask(__name__)
# fix the cors issue
CORS(app)
# init the api using factory pattern
api.init_app(app)

diagnosis_payload_model = api.model('Diagnose',
                                    {'animal': fields.String(required=True, description='The species of animal. As of '
                                                                                        'version 1.0 this can be '
                                                                                        '\'Cattle\', \'Sheep\','
                                                                                        '\'Goat\', \'Camel\', \'Horse\''
                                                                                        'or \'Donkey\'.',
                                                             example='Cattle'),
                                     'signs': fields.Raw(required=True, description='The signs shown by the animal. For'
                                                                                    'example: {\"Anae\": 0, \"Anrx\":'
                                                                                    '1,'
                                                                                    '\"Atax\": 0, \"Const\": 0,'
                                                                                    '\"Diarr\": 0, \"Dysnt\": 1, '
                                                                                    '\"Dyspn\": 0,'
                                                                                    '\"Icter\": 0, \"Lymph\": -1,'
                                                                                    '\"Pyrx\": 0, \"Stare\": 0, '
                                                                                    '\"Stunt\": 0,'
                                                                                    '\"SV_Oedm\": 1, \"Weak\": 0,'
                                                                                    '\"Wght_L\": 0}',
                                                         example={"Anae": 0, "Anrx": 1, "Atax": 0, "Const": 0,
                                                                  "Diarr": 0, "Dysnt": 1, "Dyspn": 0, "Icter": 0,
                                                                  "Lymph": -1, "Pyrx": 0, "Stare": 0, "Stunt": 0,
                                                                  "SV_Oedm": 1, "Weak": 0, "Wght_L": 0}),
                                     'priors': fields.Raw(required=False,
                                                          description='This field can be used if you wish'
                                                                      'to specify which diseases are more '
                                                                      'likely'
                                                                      'than others. If left blank, the '
                                                                      'algorithm will assume all diseases '
                                                                      'have an'
                                                                      'equal chance of occurring. The'
                                                                      'values given MUST add up to 100. '
                                                                      'The values'
                                                                      'given are the percentage '
                                                                      'likelihood of each disease '
                                                                      'occurring. \n \n You must'
                                                                      'provide data for every disease. This is the '
                                                                      'case as without every disease'
                                                                      'being considered, the algorithm\'s output will'
                                                                      'be far less accurate',
                                                          example={"Anthrax": 5, "Babesiosis": 5, "Blackleg": 5,
                                                                   "CBPP": 5, "Colibacillosis": 5, "Cowdriosis": 5,
                                                                   "FMD": 5, "Fasciolosis": 5, "LSD": 5, "Lungworm": 25,
                                                                   "Pasteurollosis": 5, "PGE / GIT parasite": 5,
                                                                   "Rabies": 5, "Trypanosomosis": 5, "Tuberculosis": 5,
                                                                   "ZZ_Other": 5}),
                                     'likelihoods': fields.Raw(required=False, description='This field can be used to '
                                                                                           'define your own'
                                                                                           'likelihood data'
                                                                                           'for each disease being'
                                                                                           'the cause of each sign.'
                                                                                           'If left blank, '
                                                                                           'the algorithm will use '
                                                                                           'the default'
                                                                                           'likelihood data. The'
                                                                                           'values given MUST add up '
                                                                                           'to be greater than 0 and '
                                                                                           'less than 1'
                                                                                           '. The values given are '
                                                                                           'the percentage likelihood '
                                                                                           'of each sign being '
                                                                                           'present when the'
                                                                                           'animal has the disease. '
                                                                                           '\n \n You must provide '
                                                                                           'data for every disease '
                                                                                           'and every sign. This'
                                                                                           'is the case as without '
                                                                                           'every disease and sign '
                                                                                           'being considered, '
                                                                                           'the algorithm\'s will'
                                                                                           'not work correctly.',
                                                               example={"Anthrax": {"Anae": 0.025, "Anrx": 0.8813,
                                                                                    "Atax": 0.025, "Const": 0.0563,
                                                                                    "Diarr": 0.025, "Dysnt": 0.025,
                                                                                    "Dyspn": 0.1188, "Icter": 0.025,
                                                                                    "Lymph": 0.0875, "Pyrx": 0.9438,
                                                                                    "SV_Oedm": 0.0563, "Stare": 0.7625,
                                                                                    "Stunt": 0.025, "Weak": 0.175,
                                                                                    "Wght_L": 0.0563},
                                                                        "Babesiosis": {"Anae": 0.9438, "Anrx": 0.7938,
                                                                                       "Atax": 0.0563, "Const": 0.0563,
                                                                                       "Diarr": 0.025, "Dysnt": 0.025,
                                                                                       "Dyspn": 0.5, "Icter": 0.8813,
                                                                                       "Lymph": 0.325, "Pyrx": 0.9125,
                                                                                       "SV_Oedm": 0.025,
                                                                                       "Stare": 0.7625, "Stunt": 0.0875,
                                                                                       "Weak": 0.8813,
                                                                                       "Wght_L": 0.5875},
                                                                        "Blackleg": {"Anae": 0.0563, "Anrx": 0.9438,
                                                                                     "Atax": 0.025, "Const": 0.15,
                                                                                     "Diarr": 0.025, "Dysnt": 0.025,
                                                                                     "Dyspn": 0.0563, "Icter": 0.025,
                                                                                     "Lymph": 0.4125, "Pyrx": 0.9125,
                                                                                     "SV_Oedm": 0.025, "Stare": 0.825,
                                                                                     "Stunt": 0.0563, "Weak": 0.7938,
                                                                                     "Wght_L": 0.0875},
                                                                        "CBPP": {"Anae": 0.0875, "Anrx": 0.9125,
                                                                                 "Atax": 0.025, "Const": 0.025,
                                                                                 "Diarr": 0.025, "Dysnt": 0.025,
                                                                                 "Dyspn": 0.975, "Icter": 0.0563,
                                                                                 "Lymph": 0.5, "Pyrx": 0.9125,
                                                                                 "SV_Oedm": 0.0563, "Stare": 0.8813,
                                                                                 "Stunt": 0.675, "Weak": 0.9125,
                                                                                 "Wght_L": 0.9125},
                                                                        "Colibacillosis": {"Anae": 0.1188,
                                                                                           "Anrx": 0.9438,
                                                                                           "Atax": 0.0563,
                                                                                           "Const": 0.025,
                                                                                           "Diarr": 0.975,
                                                                                           "Dysnt": 0.825,
                                                                                           "Dyspn": 0.025,
                                                                                           "Icter": 0.0563,
                                                                                           "Lymph": 0.175,
                                                                                           "Pyrx": 0.9125,
                                                                                           "SV_Oedm": 0.025,
                                                                                           "Stare": 0.7938,
                                                                                           "Stunt": 0.6188,
                                                                                           "Weak": 0.9438,
                                                                                           "Wght_L": 0.9125},
                                                                        "Cowdriosis": {"Anae": 0.325, "Anrx": 0.7938,
                                                                                       "Atax": 0.975, "Const": 0.0875,
                                                                                       "Diarr": 0.175, "Dysnt": 0.025,
                                                                                       "Dyspn": 0.675, "Icter": 0.0563,
                                                                                       "Lymph": 0.5875, "Pyrx": 0.9125,
                                                                                       "SV_Oedm": 0.025,
                                                                                       "Stare": 0.7625, "Stunt": 0.2938,
                                                                                       "Weak": 0.8813, "Wght_L": 0.5},
                                                                        "FMD": {"Anae": 0.7938, "Anrx": 0.325,
                                                                                "Atax": 0.025, "Const": 0.2938,
                                                                                "Diarr": 0.5, "Dysnt": 0.025,
                                                                                "Dyspn": 0.025, "Icter": 0.675,
                                                                                "Lymph": 0.025, "Pyrx": 0.025,
                                                                                "SV_Oedm": 0.9438, "Stare": 0.8813,
                                                                                "Stunt": 0.7063, "Weak": 0.9125,
                                                                                "Wght_L": 0.9438},
                                                                        "Fasciolosis": {"Anae": 0.2639, "Anrx": 0.9056,
                                                                                        "Atax": 0.3694, "Const": 0.05,
                                                                                        "Diarr": 0.1722,
                                                                                        "Dysnt": 0.0778,
                                                                                        "Dyspn": 0.2111,
                                                                                        "Icter": 0.1444,
                                                                                        "Lymph": 0.5667, "Pyrx": 0.9333,
                                                                                        "SV_Oedm": 0.05,
                                                                                        "Stare": 0.8917,
                                                                                        "Stunt": 0.3278, "Weak": 0.8667,
                                                                                        "Wght_L": 0.775},
                                                                        "LSD": {"Anae": 0.1861, "Anrx": 0.8917,
                                                                                "Atax": 0.025, "Const": 0.025,
                                                                                "Diarr": 0.1194, "Dysnt": 0.2528,
                                                                                "Dyspn": 0.3306, "Icter": 0.1056,
                                                                                "Lymph": 0.825, "Pyrx": 0.8667,
                                                                                "SV_Oedm": 0.01, "Stare": 0.8917,
                                                                                "Stunt": 0.025, "Weak": 0.8389,
                                                                                "Wght_L": 0.55},
                                                                        "Lungworm": {"Anae": 0.3556, "Anrx": 0.3694,
                                                                                     "Atax": 0.0917, "Const": 0.0917,
                                                                                     "Diarr": 0.2111, "Dysnt": 0.1306,
                                                                                     "Dyspn": 0.8667, "Icter": 0.0528,
                                                                                     "Lymph": 0.1861, "Pyrx": 0.225,
                                                                                     "SV_Oedm": 0.275, "Stare": 0.5667,
                                                                                     "Stunt": 0.1, "Weak": 0.5139,
                                                                                     "Wght_L": 0.7083},
                                                                        "PGE / GIT parasite": {"Anae": 0.7063,
                                                                                               "Anrx": 0.5,
                                                                                               "Atax": 0.025,
                                                                                               "Const": 0.2063,
                                                                                               "Diarr": 0.7938,
                                                                                               "Dysnt": 0.325,
                                                                                               "Dyspn": 0.175,
                                                                                               "Icter": 0.025,
                                                                                               "Lymph": 0.025,
                                                                                               "Pyrx": 0.0563,
                                                                                               "SV_Oedm": 0.675,
                                                                                               "Stare": 0.9438,
                                                                                               "Stunt": 0.9438,
                                                                                               "Weak": 0.9125,
                                                                                               "Wght_L": 0.9438},
                                                                        "Pasteurollosis": {"Anae": 0.0563,
                                                                                           "Anrx": 0.9125,
                                                                                           "Atax": 0.025,
                                                                                           "Const": 0.025,
                                                                                           "Diarr": 0.025,
                                                                                           "Dysnt": 0.025,
                                                                                           "Dyspn": 0.975,
                                                                                           "Icter": 0.025,
                                                                                           "Lymph": 0.4125,
                                                                                           "Pyrx": 0.9438,
                                                                                           "SV_Oedm": 0.85,
                                                                                           "Stare": 0.7063,
                                                                                           "Stunt": 0.5, "Weak": 0.9125,
                                                                                           "Wght_L": 0.9125},
                                                                        "Rabies": {"Anae": 0.025, "Anrx": 0.9125,
                                                                                   "Atax": 0.325, "Const": 0.175,
                                                                                   "Diarr": 0.025, "Dysnt": 0.025,
                                                                                   "Dyspn": 0.2938, "Icter": 0.025,
                                                                                   "Lymph": 0.025, "Pyrx": 0.4125,
                                                                                   "SV_Oedm": 0.025, "Stare": 0.175,
                                                                                   "Stunt": 0.025, "Weak": 0.0563,
                                                                                   "Wght_L": 0.0563},
                                                                        "Trypanosomosis": {"Anae": 0.9125,
                                                                                           "Anrx": 0.7938,
                                                                                           "Atax": 0.025,
                                                                                           "Const": 0.0875,
                                                                                           "Diarr": 0.2063,
                                                                                           "Dysnt": 0.025,
                                                                                           "Dyspn": 0.4125,
                                                                                           "Icter": 0.0875,
                                                                                           "Lymph": 0.975,
                                                                                           "Pyrx": 0.5875,
                                                                                           "SV_Oedm": 0.025,
                                                                                           "Stare": 0.9125,
                                                                                           "Stunt": 0.9125,
                                                                                           "Weak": 0.9125,
                                                                                           "Wght_L": 0.975},
                                                                        "Tuberculosis": {"Anae": 0.2063, "Anrx": 0.325,
                                                                                         "Atax": 0.025, "Const": 0.0563,
                                                                                         "Diarr": 0.025, "Dysnt": 0.025,
                                                                                         "Dyspn": 0.9438,
                                                                                         "Icter": 0.025,
                                                                                         "Lymph": 0.9438, "Pyrx": 0.5,
                                                                                         "SV_Oedm": 0.025,
                                                                                         "Stare": 0.8813,
                                                                                         "Stunt": 0.8813,
                                                                                         "Weak": 0.9125,
                                                                                         "Wght_L": 0.9438},
                                                                        "ZZ_Other": {"Anae": 0.7938, "Anrx": 0.1188,
                                                                                     "Atax": 0.975, "Const": 0.9438,
                                                                                     "Diarr": 0.8806, "Dysnt": 0.975,
                                                                                     "Dyspn": 0.6694, "Icter": 0.9438,
                                                                                     "Lymph": 0.5875, "Pyrx": 0.0875,
                                                                                     "SV_Oedm": 0.95, "Stare": 0.175,
                                                                                     "Stunt": 0.6722, "Weak": 0.1188,
                                                                                     "Wght_L": 0.225}})})


class getHelper:

    def __init__(self, *args, **kwargs):
        super(getHelper, self).__init__(*args, **kwargs)

    # A function used to collect the data from the Excel workbook which I manually formatted to ensure the data works.
    def get_disease_wiki_ids(self, animal):
        # Empty dictionary to store the WikiData IDs
        wiki_ids = {}
        # Get the list of diseases
        for disease in self.get_diseases(animal):
            # Loop through the diseases in the Excel sheet
            for row in wb['Disease_Codes'].rows:
                # If the disease is found, add it to the dictionary
                if row[0].value == disease:
                    wiki_ids[disease] = row[1].value
        # Return the dictionary
        return wiki_ids

    # A function used to collect the data from the Excel workbook which I manually formatted to ensure the data works.
    def get_likelihood_data(self, animal):
        # Load the correct Excel sheet
        ws = wb[animal]
        # Check if the animal exists
        if ws == -1:
            return -1

        # Get the list of signs and diseases
        signs = self.get_signs(animal)
        diseases = self.get_diseases(animal)
        if signs == -1 or diseases == -1:
            return -1

        # Dictionary which stores the likelihoods of each disease
        likelihoods = {}

        # Loop through all rows in the workbook
        for i, row in enumerate(ws.rows):
            # Skip the first row as it is just the headers
            if i == 0:
                continue

            # Counter used to keep track of the current sign

            # Dictionary which stores the likelihoods of each sign for the current disease
            current_disease_likelihoods = {}

            # Loop through all cells in each row except the first one as it is the disease name
            for j, cell in enumerate(row[1:]):
                chance = cell.value
                current_disease_likelihoods[signs[j]] = chance
            likelihoods[diseases[i - 1]] = current_disease_likelihoods

        return likelihoods

    @staticmethod
    def get_diseases(animal):
        # List which stores every given disease
        diseases = []
        ws = wb[animal]
        if ws == -1:
            return -1
        # Populate the list of diseases
        for row in ws.iter_rows(min_row=2, max_col=1, max_row=ws.max_row):
            for cell in row:
                diseases.append(cell.value)
        return diseases

    @staticmethod
    def get_signs(animal):
        # List which stores every given sign
        signs = []
        ws_signs = wb[animal]
        if ws_signs == -1:
            return -1
        # Populate the list of signs
        for col in ws_signs.iter_cols(min_col=2, max_row=1):
            for cell in col:
                signs.append(cell.value)
        return signs

    @staticmethod
    def get_sign_names_and_codes(animal):
        ws = wb[animal + '_Abbr']
        full_sign_data = {}
        medical_name = {}
        wikidata_code = {}
        for row in ws.rows:
            medical_name["name"] = row[1].value
            wikidata_code["code"] = row[2].value
            full_sign_data[row[0].value] = {**medical_name, **wikidata_code}
        return full_sign_data


class diagnosisHelper:

    @staticmethod
    def validate_priors(priors, diseases):
        provided_keys = []
        for key in priors.keys():
            if key not in diseases:
                raise BadRequest(f"Disease '{key}' is not a valid disease. Please use a valid disease from {diseases}.")
            provided_keys.append(key)

        for disease in diseases:
            if disease not in provided_keys:
                raise BadRequest(
                    f"Missing '{disease}' in priors. Please provide a prior likelihood value for all diseases.")

        total_value = sum(priors.values())
        if total_value != 100:
            raise BadRequest(f"Priors must add up to 100. Currently they add up to {total_value}.")

        return priors

    @staticmethod
    # function which checks the data provided is valid and checks that the values of the likelihoods are always
    # greater than 0 and less than 1
    def validate_likelihoods(likelihoods, diseases, signs):
        provided_keys = []
        likelihoods = likelihoods
        for key in likelihoods.keys():
            if key not in diseases:
                raise BadRequest(f"Disease '{key}' is not a valid disease.")
            provided_keys.append(key)

        for disease in diseases:
            if disease not in provided_keys:
                raise BadRequest(
                    f"Missing '{disease}' in likelihoods. Please provide a likelihood value for all diseases.")

        for disease in likelihoods:
            current_likelihoods = likelihoods[disease]
            provided_keys = []
            for key in current_likelihoods.keys():
                if key not in signs:
                    raise BadRequest(f"Sign '{key}' is not a valid sign. Please use a valid sign from {signs}.")
                provided_keys.append(key)

            for sign in signs:
                if sign not in provided_keys:
                    raise BadRequest(
                        f"Missing '{sign}' in likelihoods for disease '{disease}'. Please provide a likelihood value"
                        f"for all signs.")

            for sign in current_likelihoods:
                if (not current_likelihoods[sign] > 0) or (current_likelihoods[sign] >= 1):
                    raise BadRequest(f"Likelihood for sign '{sign}' in disease '{disease}' is not a valid value. "
                                     f"Please use a value greater than 0 and less than 1.")

        return likelihoods

    @staticmethod
    def calculate_results(diseases, likelihoods, shown_signs, priors):
        results = {}
        for disease in diseases:
            chain_probability = 1.0
            current_likelihoods = likelihoods[disease]
            for s in shown_signs:
                presence = shown_signs[s]
                if presence == 1:
                    chain_probability *= current_likelihoods[s]
                elif presence == -1:
                    chain_probability *= (1 - current_likelihoods[s])
            posterior = chain_probability * priors[disease]
            results[disease] = posterior * 100
        return results

    @staticmethod
    # A function used to normalise the outputs of the bayes calculation
    def normalise(results):
        normalised_results = {}
        summed_results = sum(results.values())
        for r in results:
            value = results[r]
            norm = value / summed_results
            normalised_results[r] = norm * 100
        return normalised_results

    @staticmethod
    def get_default_priors(diseases):
        priors = {}
        for disease in diseases:
            priors[disease] = 100 / len(diseases)
        return priors


@api.route('/api/diagnose/', methods=['POST'])
@api.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'}, description='<h1>Description</h1>'
                                                                                               '<p>This endpoint '
                                                                                               'takes a <a '
                                                                                               'href="https'
                                                                                               '://developer.mozilla'
                                                                                               '.org/en-US/docs/Learn'
                                                                                               '/JavaScript'
                                                                                               '/Objects/JSON">JSON'
                                                                                               '</a> object '
                                                                                               'containing the '
                                                                                               'species of animal and '
                                                                                               'a list of signs,'
                                                                                               'and optionally a list '
                                                                                               'of prior likelihood '
                                                                                               'values. It'
                                                                                               'then returns a list '
                                                                                               'of diseases and their '
                                                                                               'likelihood of being '
                                                                                               'the cause of the '
                                                                                               'signs.</p> \n \n'
                                                                                               '<p>The <a '
                                                                                               'href="https'
                                                                                               '://developer.mozilla'
                                                                                               '.org/en-US/docs/Learn'
                                                                                               '/JavaScript/Objects'
                                                                                               '/JSON">JSON</a'
                                                                                               '> object must contain '
                                                                                               'both "animal" and '
                                                                                               '"signs" and can '
                                                                                               'optionally contain '
                                                                                               '"priors"</p> \n \n'
                                                                                               '<h1> Parameters</h1>'
                                                                                               '<p>animal:  You can '
                                                                                               'use the'
                                                                                               '/api/data'
                                                                                               '/valid_animals GET '
                                                                                               'method to find out '
                                                                                               'which animals are '
                                                                                               'available for '
                                                                                               'diagnosis.</p>'
                                                                                               '\n \n'
                                                                                               '<p>signs\': \'All '
                                                                                               'signs detailed in the '
                                                                                               'GET method'
                                                                                               '/api/data'
                                                                                               '/full_sign_data'
                                                                                               '/\'animal\''
                                                                                               'must be included. The '
                                                                                               'data must be '
                                                                                               'formatted as a <a '
                                                                                               'href="https'
                                                                                               '://developer.mozilla'
                                                                                               '.org/en-US/docs/Learn'
                                                                                               '/JavaScript/Objects'
                                                                                               '/JSON">JSON</a> object,'
                                                                                               'the key must be a '
                                                                                               'string and the value'
                                                                                               'of each'
                                                                                               'sign must be 1 0, or '
                                                                                               '-1. 1 means the sign '
                                                                                               'is present, '
                                                                                               '0 means the sign is not'
                                                                                               'observed, but may '
                                                                                               'still be present, '
                                                                                               'and -1 means the sign '
                                                                                               'is not present.</p> '
                                                                                               '\n \n'
                                                                                               '<p>priors: This is an '
                                                                                               'optional parameter '
                                                                                               'which does not need '
                                                                                               'to be passed in the '
                                                                                               'payload.'
                                                                                               'It is used to alter '
                                                                                               'the prior likelihoods '
                                                                                               'of diseases occurring '
                                                                                               'which'
                                                                                               'influences the '
                                                                                               'outcome of the Bayes '
                                                                                               'algorithm. If this is '
                                                                                               'not included, '
                                                                                               'the algorithm assumes'
                                                                                               'equal prior '
                                                                                               'likelihoods. The list '
                                                                                               'of diseases and their '
                                                                                               'prior likelihoods '
                                                                                               'must add up to 100.'
                                                                                               'Data for the required '
                                                                                               'parameters can be '
                                                                                               'returned by the GET '
                                                                                               'Method at'
                                                                                               '/api/data'
                                                                                               '/full_disease_data'
                                                                                               '/\'animal\''
                                                                                               'which returns each '
                                                                                               'disease as the key '
                                                                                               'and the corresponding '
                                                                                               '<a '
                                                                                               'href="https://www'
                                                                                               '.wikidata.org'
                                                                                               '/">WikiData ID</a> as '
                                                                                               'the value. </p>\n \n'
                                                                                               'likelihoods: '
                                                                                               'This is an optional '
                                                                                               'parameter which does '
                                                                                               'not need to be passed '
                                                                                               'in the payload. It is '
                                                                                               'used to alter the '
                                                                                               'likelihoods of '
                                                                                               'signs being present '
                                                                                               'for each disease. If '
                                                                                               'this is not included, '
                                                                                               'the algorithm assumes '
                                                                                               'equal likelihoods. The '
                                                                                               'list of diseases and '
                                                                                               'their likelihoods must '
                                                                                               'only contain values '
                                                                                               'between 0 and 1, '
                                                                                               'non-inclusive. Data '
                                                                                               'for the required '
                                                                                               'parameters can be '
                                                                                               'returned by the GET '
                                                                                               'Method at'
                                                                                               '/api/data'
                                                                                               '/matrix/\'animal\''
                                                                                               'which returns the '
                                                                                               'default matrix the '
                                                                                               'Bayesian algorithm '
                                                                                               'uses.</p> \n \n'
                                                                                               'WARNING: Providing '
                                                                                               'your own likelihoods '
                                                                                               'and priors can '
                                                                                               'result in the '
                                                                                               'algorithm returning '
                                                                                               'incorrect results. '
                                                                                               'Use this feature with '
                                                                                               'caution if the values '
                                                                                               'you provide are '
                                                                                               'not provided'
                                                                                               'from research. </p> '
                                                                                               '\n \n'
                                                                                               '\n \n <h1> Example <a '
                                                                                               'href="https'
                                                                                               '://developer.mozilla'
                                                                                               '.org/en-US/docs/Learn'
                                                                                               '/JavaScript/Objects'
                                                                                               '/JSON">JSON</a>'
                                                                                               ' object:</h1> \n \n  {'
                                                                                               '\n"animal": "Cattle", '
                                                                                               '\n\"signs\": {'
                                                                                               '"Anae": 0, '
                                                                                               '\"Anrx\": 1, '
                                                                                               '\"Atax\": 0,'
                                                                                               '\"Const\": 0, '
                                                                                               '\"Diarr\": 0, '
                                                                                               '\"Dysnt\": 1, '
                                                                                               '\"Dyspn\": 0, '
                                                                                               '\"Icter\": 0, '
                                                                                               '\"Lymph\": -1,'
                                                                                               '\"Pyrx\": 0, '
                                                                                               '\"Stare\": 0, '
                                                                                               '\"Stunt\": 0, '
                                                                                               '\"SV_Oedm\": 1, '
                                                                                               '\"Weak\": 0, '
                                                                                               '\"Wght_L\": 0},'
                                                                                               '\n \"priors\": { '
                                                                                               '\"Anthrax\": 5, '
                                                                                               '\"Babesiosis\": 5, '
                                                                                               '\"Blackleg\": 5, '
                                                                                               '\"CBPP\": 5,'
                                                                                               '\"Colibacillosis\": '
                                                                                               '5, \"Cowdriosis\": 5,'
                                                                                               '\"FMD\": 5,'
                                                                                               '\"Fasciolosis\": 5,'
                                                                                               '\"LSD\": 5,'
                                                                                               '\"Lungworm\":'
                                                                                               '25,\"Pasteurollosis'
                                                                                               '\": 5,\"PGE / GIT '
                                                                                               'parasite\": 5,'
                                                                                               '\"Rabies\": 5,'
                                                                                               '\"Trypanosomosis\": 5,'
                                                                                               '\"Tuberculosis\": 5,'
                                                                                               '\"ZZ_Other\": 5},\n'
                                                                                               '"likelihoods" : {"Anthrax": {"Anae": 0.025, "Anrx": 0.8813, "Atax": 0.025, "Const": 0.0563, "Diarr": 0.025, "Dysnt": 0.025, '
                                                                                               '"Dyspn": 0.1188, "Icter": 0.025, "Lymph": 0.0875, "Pyrx": 0.9438, "SV_Oedm": 0.0563, "Stare": 0.7625, '
                                                                                               '"Stunt": 0.025, "Weak": 0.175, "Wght_L": 0.0563},'
                                                                                               '"Babesiosis": {"Anae": 0.9438, "Anrx": 0.7938, "Atax": 0.0563, "Const": 0.0563, "Diarr": 0.025, "Dysnt": 0.025, '
                                                                                               '"Dyspn": 0.5, "Icter": 0.8813, "Lymph": 0.325, "Pyrx": 0.9125, "SV_Oedm": 0.025, "Stare": 0.7625, '
                                                                                               '"Stunt": 0.0875, "Weak": 0.8813, "Wght_L": 0.5875}, '
                                                                                               '"Blackleg": {"Anae": 0.0563, "Anrx": 0.9438, "Atax": 0.025, "Const": 0.15, "Diarr": 0.025, "Dysnt": 0.025, '
                                                                                               '"Dyspn": 0.0563, "Icter": 0.025, "Lymph": 0.4125, "Pyrx": 0.9125, "SV_Oedm": 0.025, "Stare": 0.825,    '
                                                                                               '"Stunt": 0.0563, "Weak": 0.7938, "Wght_L": 0.0875},    '
                                                                                               '"CBPP": {"Anae": 0.0875, "Anrx": 0.9125, "Atax": 0.025, "Const": 0.025, "Diarr": 0.025, "Dysnt": 0.025,    '
                                                                                               '"Dyspn": 0.975, "Icter": 0.0563, "Lymph": 0.5, "Pyrx": 0.9125, "SV_Oedm": 0.0563, "Stare": 0.8813,   '
                                                                                               '"Stunt": 0.675, "Weak": 0.9125, "Wght_L": 0.9125},   '
                                                                                               '"Colibacillosis": {"Anae": 0.1188, "Anrx": 0.9438, "Atax": 0.0563, "Const": 0.025, "Diarr": 0.975, "Dysnt": 0.825, '
                                                                                               '"Dyspn": 0.025, "Icter": 0.0563, "Lymph": 0.175, "Pyrx": 0.9125, "SV_Oedm": 0.025, "Stare": 0.7938,'
                                                                                               '"Stunt": 0.6188, "Weak": 0.9438, "Wght_L": 0.9125}, '
                                                                                               '"Cowdriosis": {"Anae": 0.325, "Anrx": 0.7938, "Atax": 0.975, "Const": 0.0875, "Diarr": 0.175, "Dysnt": 0.025, '
                                                                                               '"Dyspn": 0.675, "Icter": 0.0563, "Lymph": 0.5875, "Pyrx": 0.9125, "SV_Oedm": 0.025, "Stare": 0.7625,'
                                                                                               '"Stunt": 0.2938, "Weak": 0.8813, "Wght_L": 0.5},'
                                                                                               '"FMD": {"Anae": 0.7938, "Anrx": 0.325, "Atax": 0.025, "Const": 0.2938, "Diarr": 0.5, "Dysnt": 0.025, "Dyspn": 0.025,'
                                                                                               '"Icter": 0.675, "Lymph": 0.025, "Pyrx": 0.025, "SV_Oedm": 0.9438, "Stare": 0.8813, "Stunt": 0.7063,'
                                                                                               '"Weak": 0.9125, "Wght_L": 0.9438},'
                                                                                               '"Fasciolosis": {"Anae": 0.2639, "Anrx": 0.9056, "Atax": 0.3694, "Const": 0.05, "Diarr": 0.1722, "Dysnt": 0.0778,'
                                                                                               '"Dyspn": 0.2111, "Icter": 0.1444, "Lymph": 0.5667, "Pyrx": 0.9333, "SV_Oedm": 0.05, "Stare": 0.8917,'
                                                                                               '"Stunt": 0.3278, "Weak": 0.8667, "Wght_L": 0.775},'
                                                                                               '"LSD": {"Anae": 0.1861, "Anrx": 0.8917, "Atax": 0.025, "Const": 0.025, "Diarr": 0.1194, "Dysnt": 0.2528,'
                                                                                               '"Dyspn": 0.3306, "Icter": 0.1056, "Lymph": 0.825, "Pyrx": 0.8667, "SV_Oedm": 0.01, "Stare": 0.8917, '
                                                                                               '"Stunt": 0.025, "Weak": 0.8389, "Wght_L": 0.55}, '
                                                                                               '"Lungworm": {"Anae": 0.3556, "Anrx": 0.3694, "Atax": 0.0917, "Const": 0.0917, "Diarr": 0.2111, "Dysnt": 0.1306, '
                                                                                               '"Dyspn": 0.8667, "Icter": 0.0528, "Lymph": 0.1861, "Pyrx": 0.225, "SV_Oedm": 0.275, "Stare": 0.5667, '
                                                                                               '"Stunt": 0.1, "Weak": 0.5139, "Wght_L": 0.7083}, '
                                                                                               '"PGE / GIT parasite": {"Anae": 0.7063, "Anrx": 0.5, "Atax": 0.025, "Const": 0.2063, "Diarr": 0.7938, "Dysnt": 0.325, '
                                                                                               '"Dyspn": 0.175, "Icter": 0.025, "Lymph": 0.025, "Pyrx": 0.0563, "SV_Oedm": 0.675, "Stare": 0.9438, '
                                                                                               '"Stunt": 0.9438, "Weak": 0.9125, "Wght_L": 0.9438}, '
                                                                                               '"Pasteurollosis": {"Anae": 0.0563, "Anrx": 0.9125, "Atax": 0.025, "Const": 0.025, "Diarr": 0.025, "Dysnt": 0.025, '
                                                                                               '"Dyspn": 0.975, "Icter": 0.025, "Lymph": 0.4125, "Pyrx": 0.9438, "SV_Oedm": 0.85, "Stare": 0.7063, "Stunt": 0.5,  '
                                                                                               '"Weak": 0.9125, "Wght_L": 0.9125}, '
                                                                                               '"Rabies": {"Anae": 0.025, "Anrx": 0.9125, "Atax": 0.325, "Const": 0.175, "Diarr": 0.025, "Dysnt": 0.025, '
                                                                                               '"Dyspn": 0.2938, "Icter": 0.025, "Lymph": 0.025, "Pyrx": 0.4125, "SV_Oedm": 0.025, "Stare": 0.175, '
                                                                                               '"Stunt": 0.025, "Weak": 0.0563, "Wght_L": 0.0563}, '
                                                                                               '"Trypanosomosis": {"Anae": 0.9125, "Anrx": 0.7938, "Atax": 0.025, "Const": 0.0875, "Diarr": 0.2063, "Dysnt": 0.025, '
                                                                                               '"Dyspn": 0.4125, "Icter": 0.0875, "Lymph": 0.975, "Pyrx": 0.5875, "SV_Oedm": 0.025, "Stare": 0.9125, '
                                                                                               '"Stunt": 0.9125, "Weak": 0.9125, "Wght_L": 0.975}, '
                                                                                               '"Tuberculosis": {"Anae": 0.2063, "Anrx": 0.325, "Atax": 0.025, "Const": 0.0563, "Diarr": 0.025, "Dysnt": 0.025, '
                                                                                               '"Dyspn": 0.9438, "Icter": 0.025, "Lymph": 0.9438, "Pyrx": 0.5, "SV_Oedm": 0.025, "Stare": 0.8813, '
                                                                                               '"Stunt": 0.8813, "Weak": 0.9125, "Wght_L": 0.9438}, '
                                                                                               '"ZZ_Other": {"Anae": 0.7938, "Anrx": 0.1188, "Atax": 0.975, "Const": 0.9438, "Diarr": 0.8806, "Dysnt": 0.975, '
                                                                                               '"Dyspn": 0.6694, "Icter": 0.9438, "Lymph": 0.5875, "Pyrx": 0.0875, "SV_Oedm": 0.95, "Stare": 0.175, '
                                                                                               '"Stunt": 0.6722, "Weak": 0.1188, "Wght_L": 0.225}\n \t }\n } ')
class diagnose(Resource):
    def __init__(self, *args, **kwargs):
        self.gh = getHelper()
        self.dh = diagnosisHelper()
        super(diagnose, self).__init__(*args, **kwargs)

    @staticmethod
    def options() -> Response:
        return jsonify({'status': 'ok'})

    @api.expect(diagnosis_payload_model, validate=True)
    def post(self) -> Response:

        # Get the data from the API request
        data: [str, Union[str, Dict[str, int], None]] = request.get_json()
        # Grab the species of animal it is from the API request data
        animal: str = data['animal'].capitalize()

        # Capitalise the first letter of the animal to ensure input matches syntax used in sheets

        valid_animals: List[str] = getAnimals().get().get_json()
        # Check if the animal is valid
        if animal not in valid_animals:
            # If the animal is invalid, raise an error
            raise BadRequest(f'Invalid animal: {animal}. Please use a valid animal from /api/data/valid_animals.')

        # Get the list of diseases
        diseases: List[str] = self.gh.get_diseases(animal)
        # Get the list of wiki ids
        wiki_ids: Dict[str, str] = self.gh.get_disease_wiki_ids(animal)

        if data.get('likelihoods') is not None:
            # Check if the likelihoods are valid
            if not self.dh.validate_likelihoods(data['likelihoods'], diseases, self.gh.get_signs(animal)):
                # If the likelihoods are invalid, raise an error
                raise BadRequest(f'Invalid likelihoods: {data["likelihoods"]}. Please use valid likelihoods from '
                                 f'/api/data/valid_likelihoods/{animal}.')

        # Get the prior likelihoods from the API request data
        likelihoods: Dict[str, Dict[str, float]] = data.get('likelihoods')

        # If the likelihoods are not included in the request, get them from the data Excel sheet
        if likelihoods is None:
            likelihoods: Dict[str, Dict[str, float]] = self.gh.get_likelihood_data(animal)

        # Grab the list of signs from the API request data
        shown_signs: Dict[str, int] = data['signs']

        valid_sign_values = [0, 1, -1]
        # Check if the signs values are all valid
        for x, value in enumerate(shown_signs.values()):
            if value not in valid_sign_values:
                sign = list(shown_signs.keys())[x]
                raise BadRequest(f'Error with value of {sign}: {value}. Sign values must be either -1, 0 or 1')

        # Grab the priors from the API request data (if they exist)
        priors: Dict[str, float] = data.get('priors')
        if priors is not None:
            priors = self.dh.validate_priors(priors, diseases)
        else:
            priors = self.dh.get_default_priors(diseases)

        results: Dict[str, float] = self.dh.calculate_results(diseases, likelihoods, shown_signs, priors)
        normalised_results: Dict[str, float] = self.dh.normalise(results)

        return jsonify({'results': normalised_results, 'wiki_ids': wiki_ids})


@api.route('/api/data/full_animal_data/<string:animal>')
@api.doc(example='Goat', required=True, responses={200: 'OK', 400: 'Invalid Argument'},
         params={'animal': 'The species of animal you wish to retrieve signs and diseases for. This must be a valid '
                           'animal as returned by /api/data/valid_animals. \n \n'}, description='<h1>Description</h1>'
                                                                                                '<p>This endpoint returns a '
                                                                                                '<a href="https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON">JSON</a> object '
                                                                                                'containing diagnosable diseases with their corresponding '
                                                                                                '<a href="https://www.wikidata.org/">WikiData IDs</a> as well as the valid signs '
                                                                                                'associated with the animal, their full medical terminology in English, and their'
                                                                                                'corresponding <a href="https://www.wikidata.org/">WikiData IDs</a> (if they exist).</p>'
                                                                                                '<h1>URL Parameters</h1>'
                                                                                                '<ul>'
                                                                                                '<li><p>animal: The species of animal you wish to retrieve signs and diseases for. This must be'
                                                                                                'a valid animal as returned by /api/data/valid_animals. </p></li>'
                                                                                                '</ul>\n \n ')
class getRequiredInputData(Resource):
    def __init__(self, *args, **kwargs):
        self.gh = getHelper()
        super(getRequiredInputData, self).__init__(*args, **kwargs)

    def get(self, animal):
        animal = animal.capitalize()
        # Load the correct Excel sheet
        if animal not in getAnimals().get().get_json():
            # If the animal is invalid, raise an error
            raise BadRequest('Invalid animal: %s. Please use a valid animal from /api/data/valid_animals.' % animal)
        return jsonify(
            {'diseases': self.gh.get_disease_wiki_ids(animal), 'signs': self.gh.get_sign_names_and_codes(animal)})


@api.route('/api/data/matrix/<string:animal>')
class getDiseaseSignMatrix(Resource):
    def __init__(self, *args, **kwargs):
        self.gh = getHelper()
        super(getDiseaseSignMatrix, self).__init__(*args, **kwargs)

    def get(self, animal):
        # Handle capitalisation
        animal = animal.capitalize()
        # Check if the animal is valid
        if animal not in getAnimals().get().get_json():
            # If the animal is invalid, raise an error
            raise BadRequest(f'Invalid animal: {animal}. Please use a valid animal from /api/data/valid_animals.')
        # Get the correct data from the data Excel sheet
        data = self.gh.get_likelihood_data(animal)
        # Return the data
        return jsonify(data)


@api.route('/api/data/valid_animals')
@api.doc(responses={200: 'OK', 400: 'Invalid Argument'}, description='<h1>Description</h1>'
                                                                     '<p>This endpoint returns a <a '
                                                                     'href="https://developer.mozilla.org/en-US/docs'
                                                                     '/Learn/JavaScript'
                                                                     '/Objects/JSON">JSON</a> object containing the '
                                                                     'names of animal species which are available for'
                                                                     'diagnosis in the /api/diagnose POST method '
                                                                     'below. </p>\n')
class getAnimals(Resource):
    @staticmethod
    def get():
        # Get the Excel sheets which don't contain _Abbr or _Codes
        names = [name for name in wb.sheetnames if "_Abbr" not in name and "_Codes" not in name]
        # Return the names
        return jsonify(names)


@api.route('/api/data/full_sign_data/<string:animal>')
@api.doc(required=True, responses={200: 'OK', 400: 'Invalid Argument'}, description='<h1>Description</h1>'
                                                                                    '<p>This endpoint returns a <a '
                                                                                    'href="https://developer.mozilla'
                                                                                    '.org/en-US/docs/Learn/JavaScript'
                                                                                    '/Objects/JSON">JSON</a> object '
                                                                                    'which contains the full medical '
                                                                                    'terminology for each sign'
                                                                                    ' in English as '
                                                                                    'well as the corresponding <a '
                                                                                    'href="https://www.wikidata.org'
                                                                                    '/">WikiData IDs</a> for the '
                                                                                    'signs ('
                                                                                    'if they exist).</p>'
                                                                                    '<h1>URL Parameters</h1>'
                                                                                    '<ul>'
                                                                                    '<li><p>animal: The species of '
                                                                                    'animal you wish to retrieve '
                                                                                    'signs and diseases for. This '
                                                                                    'must be'
                                                                                    'a valid'
                                                                                    'animal as returned by '
                                                                                    '/api/data/valid_animals.</p></li>'
                                                                                    '</ul>',
         params={'animal': 'The species of animal you wish to retrieve the data for. This must be a valid animal as '
                           'returned by /api/data/valid_animals. \n \n '})
class getSignCodesAndTerminology(Resource):
    def __init__(self, *args, **kwargs):
        self.gh = getHelper()
        super(getSignCodesAndTerminology, self).__init__(*args, **kwargs)

    def get(self, animal):
        # Handle capitalisation
        animal = animal.capitalize()
        # Check if the animal is valid
        if animal not in getAnimals().get().get_json():
            # If the animal is invalid, raise an error
            raise BadRequest('Invalid animal: %s. Please use a valid animal from /api/data/valid_animals.' % animal)
        # Return the data
        return jsonify({'full_sign_data': self.gh.get_sign_names_and_codes(animal)})


@api.route('/api/data/full_disease_data/<string:animal>')
@api.doc(required=True, responses={200: 'OK', 400: 'Invalid Argument'}, description='<h1>Description</h1>'
                                                                                    '<p>This endpoint returns a <a '
                                                                                    'href="https://developer.mozilla'
                                                                                    '.org/en-US/docs/Learn/JavaScript'
                                                                                    '/Objects/JSON">JSON</a> object '
                                                                                    'which contains the possible '
                                                                                    'diseases for the given animal as'
                                                                                    'well as the corresponding <a '
                                                                                    'href="https://www.wikidata.org'
                                                                                    '/">WikiData IDs</a> (if they'
                                                                                    'exist).</p>'
                                                                                    '<h1>URL Parameters</h1>'
                                                                                    '<ul>'
                                                                                    '<li><p>animal: The species of '
                                                                                    'animal you wish to retrieve '
                                                                                    'signs and diseases for. This '
                                                                                    'must be'
                                                                                    'a valid'
                                                                                    'animal as returned by '
                                                                                    '/api/data/valid_animals.</p></li>'
                                                                                    '</ul>',
         params={'animal': 'The species of animal you wish to retrieve the data for. This must be a valid animal as '
                           'returned by'
                           '/api/data/valid_animals. \n \n'})
class getDiseaseCodes(Resource):

    def __init__(self, *args, **kwargs):
        self.gh = getHelper()
        super(getDiseaseCodes, self).__init__(*args, **kwargs)

    def get(self, animal):
        # Handle capitalisation to allow for case insensitivity
        animal = animal.capitalize()
        # Check if the animal is valid
        if animal not in getAnimals().get().get_json():
            # If the animal is invalid, raise an error
            raise BadRequest('Invalid animal: %s. Please use a valid animal from /api/data/valid_animals.' % animal)
        # Return the data
        return jsonify({'disease_codes': self.gh.get_disease_wiki_ids(animal)})


if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run(port=5000)
