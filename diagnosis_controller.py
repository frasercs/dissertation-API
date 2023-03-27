import os
import sys
from typing import Dict, List, Union, Tuple

from flask import request, jsonify, Response
from flask_restx import Namespace, Resource, fields
from openpyxl import load_workbook
from werkzeug.exceptions import BadRequest

import diagnosis_helper as dh

# load the Excel file
wb = load_workbook(filename=os.path.join(sys.path[0], "data.xlsx"))

api = Namespace('diagnosis', description='Diagnosis related operations')

diagnosis_payload_model = api.model('Diagnose', {
    'animal': fields.String(required=True, description='The species of animal. As of version 1.0 this can be'
                                                       ' \'Cattle\', \'Sheep\',\'Goat\', \'Camel\', \'Horse\'or '
                                                       '\'Donkey\'.', example='Cattle'),
    'signs': fields.Raw(required=True,
                        description='The signs shown by the animal. For example: {\"Anae\": 0, \"Anrx\":1,'
                                    '\"Atax\": 0, \"Const\": 0,\"Diarr\": 0, \"Dysnt\": 1, \"Dyspn\": 0,'
                                    '\"Icter\": 0, \"Lymph\": -1,\"Pyrx\": 0, \"Stare\": 0, \"Stunt\": 0,'
                                    '\"SV_Oedm\": 1, \"Weak\": 0,\"Wght_L\": 0}',
                        example={"Anae": 0, "Anrx": 1, "Atax": 0, "Const": 0, "Diarr": 0, "Dysnt": 1, "Dyspn": 0,
                                 "Icter": 0, "Lymph": -1, "Pyrx": 0, "Stare": 0, "Stunt": 0, "SV_Oedm": 1, "Weak": 0,
                                 "Wght_L": 0}), 'priors': fields.Raw(required=False,
                                                                     description='This field can be used if you wish '
                                                                                 'to specify which diseases are more '
                                                                                 'likely than others. If left blank, '
                                                                                 'the algorithm will assume all '
                                                                                 'diseases have an equal chance of '
                                                                                 'occurring. The values given MUST '
                                                                                 'add up to 100. The values given are '
                                                                                 'the percentage likelihood of each '
                                                                                 'disease occurring. \n \n '
                                                                                 'You must provide data for every '
                                                                                 'disease. This is the case as '
                                                                                 'without every disease being '
                                                                                 'considered, the algorithm\'s output '
                                                                                 'will be far less accurate',
                                                                     example={"Anthrax": 5, "Babesiosis": 5,
                                                                              "Blackleg": 5, "CBPP": 5,
                                                                              "Colibacillosis": 5, "Cowdriosis": 5,
                                                                              "FMD": 5, "Fasciolosis": 5, "LSD": 5,
                                                                              "Lungworm": 25, "Pasteurollosis": 5,
                                                                              "PGE / GIT parasite": 5, "Rabies": 5,
                                                                              "Trypanosomosis": 5, "Tuberculosis": 5,
                                                                              "ZZ_Other": 5}),
    'likelihoods': fields.Raw(required=False,
                              description='This field can be used to define your own likelihood data for each disease '
                                          'being the cause of each sign.If left blank, the algorithm will use the '
                                          'default likelihood data. The values given MUST add up to be greater than '
                                          '0 and less than 1. The values given are the percentage likelihood of each '
                                          'sign being present when the animal has the disease. \n \n You must provide '
                                          'data for every disease and every sign. This is the case as without '
                                          'every disease and sign being considered, the algorithm\'s '
                                          'will not work correctly.', example={
            "Anthrax": {"Anae": 0.2668, "Anrx": 0.4023, "Atax": 0.0085, "Const": 0.185, "Diarr": 0.7954,
                "Dysnt": 0.0888, "Dyspn": 0.7864, "Icter": 0.2016, "Lymph": 0.6453, "Pyrx": 0.8447, "SV_Oedm": 0.0814,
                "Stare": 0.5038, "Stunt": 0.7275, "Weak": 0.0771, "Wght_L": 0.6383},
            "Babesiosis": {"Anae": 0.9315, "Anrx": 0.1084, "Atax": 0.5898, "Const": 0.7412, "Diarr": 0.2778,
                "Dysnt": 0.5351, "Dyspn": 0.2371, "Icter": 0.1604, "Lymph": 0.5144, "Pyrx": 0.8542, "SV_Oedm": 0.8295,
                "Stare": 0.8088, "Stunt": 0.9521, "Weak": 0.1691, "Wght_L": 0.6912},
            "Blackleg": {"Anae": 0.2589, "Anrx": 0.1933, "Atax": 0.503, "Const": 0.3529, "Diarr": 0.5158,
                "Dysnt": 0.9027, "Dyspn": 0.3662, "Icter": 0.6998, "Lymph": 0.3139, "Pyrx": 0.2509, "SV_Oedm": 0.735,
                "Stare": 0.1036, "Stunt": 0.5706, "Weak": 0.2188, "Wght_L": 0.0016},
            "CBPP": {"Anae": 0.4047, "Anrx": 0.9005, "Atax": 0.7564, "Const": 0.9049, "Diarr": 0.0014, "Dysnt": 0.0739,
                "Dyspn": 0.9572, "Icter": 0.2247, "Lymph": 0.0228, "Pyrx": 0.8588, "SV_Oedm": 0.2807, "Stare": 0.6536,
                "Stunt": 0.1723, "Weak": 0.0436, "Wght_L": 0.7293},
            "Colibacillosis": {"Anae": 0.5151, "Anrx": 0.6292, "Atax": 0.1373, "Const": 0.4801, "Diarr": 0.5341,
                "Dysnt": 0.8744, "Dyspn": 0.5039, "Icter": 0.7543, "Lymph": 0.4948, "Pyrx": 0.404, "SV_Oedm": 0.5243,
                "Stare": 0.1538, "Stunt": 0.6301, "Weak": 0.8463, "Wght_L": 0.1069},
            "Cowdriosis": {"Anae": 0.1476, "Anrx": 0.7902, "Atax": 0.7319, "Const": 0.7912, "Diarr": 0.7395,
                "Dysnt": 0.6757, "Dyspn": 0.1096, "Icter": 0.3056, "Lymph": 0.185, "Pyrx": 0.3019, "SV_Oedm": 0.4824,
                "Stare": 0.0284, "Stunt": 0.5792, "Weak": 0.1685, "Wght_L": 0.2448},
            "FMD": {"Anae": 0.2977, "Anrx": 0.871, "Atax": 0.963, "Const": 0.1151, "Diarr": 0.9518, "Dysnt": 0.6154,
                "Dyspn": 0.6984, "Icter": 0.4119, "Lymph": 0.3372, "Pyrx": 0.6846, "SV_Oedm": 0.0385, "Stare": 0.6973,
                "Stunt": 0.4824, "Weak": 0.6523, "Wght_L": 0.614},
            "Fasciolosis": {"Anae": 0.0095, "Anrx": 0.977, "Atax": 0.1164, "Const": 0.1311, "Diarr": 0.0569,
                "Dysnt": 0.1604, "Dyspn": 0.0823, "Icter": 0.4349, "Lymph": 0.6208, "Pyrx": 0.9651, "SV_Oedm": 0.1108,
                "Stare": 0.8521, "Stunt": 0.5637, "Weak": 0.1865, "Wght_L": 0.7242},
            "LSD": {"Anae": 0.0883, "Anrx": 0.3197, "Atax": 0.9291, "Const": 0.6622, "Diarr": 0.631, "Dysnt": 0.6657,
                "Dyspn": 0.974, "Icter": 0.153, "Lymph": 0.8023, "Pyrx": 0.2831, "SV_Oedm": 0.4065, "Stare": 0.2959,
                "Stunt": 0.3347, "Weak": 0.5577, "Wght_L": 0.9966},
            "Lungworm": {"Anae": 0.4765, "Anrx": 0.7152, "Atax": 0.6797, "Const": 0.938, "Diarr": 0.6535,
                "Dysnt": 0.9752, "Dyspn": 0.6245, "Icter": 0.4954, "Lymph": 0.4811, "Pyrx": 0.3523, "SV_Oedm": 0.2446,
                "Stare": 0.6479, "Stunt": 0.7919, "Weak": 0.7959, "Wght_L": 0.0079},
            "PGE / GIT parasite": {"Anae": 0.2108, "Anrx": 0.078, "Atax": 0.6913, "Const": 0.664, "Diarr": 0.5129,
                "Dysnt": 0.1369, "Dyspn": 0.27, "Icter": 0.9672, "Lymph": 0.8923, "Pyrx": 0.1874, "SV_Oedm": 0.7678,
                "Stare": 0.4827, "Stunt": 0.6827, "Weak": 0.8251, "Wght_L": 0.4358},
            "Pasteurollosis": {"Anae": 0.5699, "Anrx": 0.8898, "Atax": 0.7183, "Const": 0.9549, "Diarr": 0.4316,
                "Dysnt": 0.5618, "Dyspn": 0.4728, "Icter": 0.5825, "Lymph": 0.2789, "Pyrx": 0.6803, "SV_Oedm": 0.1556,
                "Stare": 0.1606, "Stunt": 0.5968, "Weak": 0.4604, "Wght_L": 0.1261},
            "Rabies": {"Anae": 0.021, "Anrx": 0.1521, "Atax": 0.99, "Const": 0.553, "Diarr": 0.6056, "Dysnt": 0.123,
                "Dyspn": 0.5579, "Icter": 0.8676, "Lymph": 0.4572, "Pyrx": 0.4503, "SV_Oedm": 0.8823, "Stare": 0.6489,
                "Stunt": 0.0886, "Weak": 0.5222, "Wght_L": 0.4999},
            "Trypanosomosis": {"Anae": 0.3602, "Anrx": 0.6961, "Atax": 0.898, "Const": 0.6043, "Diarr": 0.5259,
                "Dysnt": 0.3489, "Dyspn": 0.6187, "Icter": 0.3156, "Lymph": 0.0677, "Pyrx": 0.0405, "SV_Oedm": 0.0257,
                "Stare": 0.5779, "Stunt": 0.9064, "Weak": 0.0779, "Wght_L": 0.9971},
            "Tuberculosis": {"Anae": 0.2207, "Anrx": 0.7513, "Atax": 0.9402, "Const": 0.5418, "Diarr": 0.9419,
                "Dysnt": 0.0402, "Dyspn": 0.6023, "Icter": 0.399, "Lymph": 0.6675, "Pyrx": 0.5587, "SV_Oedm": 0.4947,
                "Stare": 0.59, "Stunt": 0.1479, "Weak": 0.8633, "Wght_L": 0.085},
            "ZZ_Other": {"Anae": 0.6361, "Anrx": 0.1729, "Atax": 0.3008, "Const": 0.6395, "Diarr": 0.3737,
                "Dysnt": 0.858, "Dyspn": 0.9196, "Icter": 0.3255, "Lymph": 0.4681, "Pyrx": 0.7769, "SV_Oedm": 0.0234,
                "Stare": 0.9337, "Stunt": 0.3675, "Weak": 0.1286, "Wght_L": 0.0943}})})

custom_diagnosis_payload_model = api.model('Custom Diagnosis Payload', {

    'diseases': fields.List(fields.String, required=True, description='The diseases to be diagnosed',
                            example=['Rabies', 'Cold']),
    'signs': fields.List(fields.String, required=True, description='The symptoms to be diagnosed',
                         example=['Fever', 'Cough', 'Diarrhoea']),
    'shown_signs': fields.Raw(required=True, description='The symptoms that are shown',
                              example={"Fever": 1, "Cough": 0, "Diarrhoea": -1}),
    'likelihoods': fields.Raw(required=True, description='The likelihoods to be diagnosed',
                              example={"Rabies": {"Fever": 0.6, "Cough": 0.1, "Diarrhoea": 0.1},
                                       "Cold": {"Fever": 0.9, "Cough": 0.9, "Diarrhoea": 0.1}}),
    'priors': fields.Raw(required=False, description='The priors to be diagnosed', example={"Rabies": 20, "Cold": 80}),
    'animal': fields.String(required=False, description='The animal to be diagnosed', example='Dog')})


@api.route('/diagnose/', methods=['POST'])
@api.doc(responses={200: 'OK', 400: 'Bad Request', 500: 'Internal Server Error'},
         description='<h1>Description</h1><p>This endpoint takes a <a href="https://developer.mozilla.org/'
                     'en-US/docs/Learn/JavaScript/Objects/JSON">JSON</a> object containing the species of animal and '
                     'a list of signs,and optionally a list of prior likelihood values. It then returns a list '
                     'of diseases and their likelihood of being the cause of the signs.</p> \n \n'
                     '<p>The <a href="https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON">JSON</a'
                     '> object must contain both "animal" and "signs" and can optionally contain '
                     '"priors" and "likelihoods"</p> \n \n<h1> Parameters</h1><p>animal:  You can use the'
                     '/data/valid_animals GET method to find out which animals are available for '
                     'diagnosis.</p>\n \n<p>signs: \'All signs detailed in the GET method '
                     '/data/full_sign_data/\'animal\' must be included. The data must be formatted as a '
                     '<a href="https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON">JSON</a> '
                     'object,the key must be a string and the value of each sign must be 1 0, or -1. '
                     '1 means the sign is '
                     'present, 0 means the sign is not observed, but may still be present, and -1 means the sign is '
                     'not present.</p> \n \n<p>priors: This is an optional parameter which does not need to be passed '
                     'in the payload.It is used to alter the prior likelihoods of diseases occurring which influences '
                     'the outcome of the Bayes algorithm. If this is not included, the algorithm assumes equal prior '
                     'likelihoods. The list of diseases and their prior likelihoods must add up to 100.Data for the '
                     'required parameters can be returned by the GET Method at /data/full_disease_data/\'animal\' '
                     'which returns each disease as the key and the corresponding <a href="https://www.wikidata.org/">'
                     'WikiData ID</a> as the value. </p>\n \nlikelihoods: This is an optional parameter which does not '
                     'need to be passed in the payload. It is used to alter the likelihoods of signs being present for '
                     'each disease. If this is not included, the algorithm assumes equal likelihoods. The list of '
                     'diseases and their likelihoods must only contain values between 0 and 1, non-inclusive. Data '
                     'for the required parameters can be returned by the GET Method at /data/matrix/\'animal\' '
                     'which returns the default matrix the Bayesian algorithm uses. Alternatively the required signs '
                     'and diseases can be obtained via the /data/full_animal_data/\'animal\' endpoint.</p> \n \n'
                     '<p>WARNING: Providing your own likelihoods and priors can result in the algorithm returning '
                     'incorrect results. Use these features with caution if the values you provide are not based on '
                     'research. </p> <p>NOTE: likelihood values in the example payload are randomly generated '
                     'and as such should not be used to provide accurate results\n \n <h1> Example <a '
                     'href="https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON">JSON</a> '
                     'object:</h1> \n \n  {\n"animal": "Cattle", \n\"signs\": {"Anae": 0, \"Anrx\": 1, \"Atax\": 0, '
                     '\"Const\": 0, \"Diarr\": 0, \"Dysnt\": 1, \"Dyspn\": 0, \"Icter\": 0, \"Lymph\": -1,\"Pyrx\": 0, '
                     '\"Stare\": 0, \"Stunt\": 0, \"SV_Oedm\": 1, \"Weak\": 0, \"Wght_L\": 0},\n '
                     '\"priors\": { \"Anthrax\": 5, \"Babesiosis\": 5, \"Blackleg\": 5, \"CBPP\": 5, '
                     '\"Colibacillosis\": 5, \"Cowdriosis\": 5,\"FMD\": 5,\"Fasciolosis\": 5,\"LSD\": 5, '
                     '\"Lungworm\":25,\"Pasteurollosis\": 5,\"PGE / GIT parasite\": 5,\"Rabies\": 5, '
                     '\"Trypanosomosis\": 5,\"Tuberculosis\": 5,\"ZZ_Other\": 5},\n'
                     '"likelihoods": { '
                     '    "Anthrax": {'
                     '      "Anae": 0.2668,'
                     '      "Anrx": 0.4023,'
                     '      "Atax": 0.0085,'
                     '      "Const": 0.185,'
                     '      "Diarr": 0.7954,'
                     '      "Dysnt": 0.0888,'
                     '      "Dyspn": 0.7864,'
                     '      "Icter": 0.2016,'
                     '      "Lymph": 0.6453,'
                     '      "Pyrx": 0.8447,'
                     '      "SV_Oedm": 0.0814,'
                     '      "Stare": 0.5038,'
                     '      "Stunt": 0.7275,'
                     '      "Weak": 0.0771,'
                     '      "Wght_L": 0.6383'
                     '    },'
                     '    "Babesiosis": {'
                     '      "Anae": 0.9315,'
                     '      "Anrx": 0.1084,'
                     '      "Atax": 0.5898,'
                     '      "Const": 0.7412,'
                     '      "Diarr": 0.2778,'
                     '      "Dysnt": 0.5351,'
                     '      "Dyspn": 0.2371,'
                     '      "Icter": 0.1604,'
                     '      "Lymph": 0.5144,'
                     '      "Pyrx": 0.8542,'
                     '      "SV_Oedm": 0.8295,'
                     '      "Stare": 0.8088,'
                     '      "Stunt": 0.9521,'
                     '      "Weak": 0.1691,'
                     '      "Wght_L": 0.6912'
                     '    },'
                     '    "Blackleg": {'
                     '      "Anae": 0.2589,'
                     '      "Anrx": 0.1933,'
                     '      "Atax": 0.503,'
                     '      "Const": 0.3529,'
                     '      "Diarr": 0.5158,'
                     '      "Dysnt": 0.9027,'
                     '      "Dyspn": 0.3662,'
                     '      "Icter": 0.6998,'
                     '      "Lymph": 0.3139,'
                     '      "Pyrx": 0.2509,'
                     '      "SV_Oedm": 0.735,'
                     '      "Stare": 0.1036,'
                     '      "Stunt": 0.5706,'
                     '      "Weak": 0.2188,'
                     '      "Wght_L": 0.0016'
                     '    },'
                     '    "CBPP": {'
                     '      "Anae": 0.4047,'
                     '      "Anrx": 0.9005,'
                     '      "Atax": 0.7564,'
                     '      "Const": 0.9049,'
                     '      "Diarr": 0.0014,'
                     '      "Dysnt": 0.0739,'
                     '      "Dyspn": 0.9572,'
                     '      "Icter": 0.2247,'
                     '      "Lymph": 0.0228,'
                     '      "Pyrx": 0.8588,'
                     '      "SV_Oedm": 0.2807,'
                     '      "Stare": 0.6536,'
                     '      "Stunt": 0.1723,'
                     '      "Weak": 0.0436,'
                     '      "Wght_L": 0.7293'
                     '    },'
                     '    "Colibacillosis": {'
                     '      "Anae": 0.5151,'
                     '      "Anrx": 0.6292,'
                     '      "Atax": 0.1373,'
                     '      "Const": 0.4801,'
                     '      "Diarr": 0.5341,'
                     '      "Dysnt": 0.8744,'
                     '      "Dyspn": 0.5039,'
                     '      "Icter": 0.7543,'
                     '      "Lymph": 0.4948,'
                     '      "Pyrx": 0.404,'
                     '      "SV_Oedm": 0.5243,'
                     '      "Stare": 0.1538,'
                     '      "Stunt": 0.6301,'
                     '      "Weak": 0.8463,'
                     '      "Wght_L": 0.1069'
                     '    },'
                     '    "Cowdriosis": {'
                     '      "Anae": 0.1476,'
                     '      "Anrx": 0.7902,'
                     '      "Atax": 0.7319,'
                     '      "Const": 0.7912,'
                     '      "Diarr": 0.7395,'
                     '      "Dysnt": 0.6757,'
                     '      "Dyspn": 0.1096,'
                     '      "Icter": 0.3056,'
                     '      "Lymph": 0.185,'
                     '      "Pyrx": 0.3019,'
                     '      "SV_Oedm": 0.4824,'
                     '      "Stare": 0.0284,'
                     '      "Stunt": 0.5792,'
                     '      "Weak": 0.1685,'
                     '      "Wght_L": 0.2448'
                     '    },'
                     '    "FMD": {'
                     '      "Anae": 0.2977,'
                     '      "Anrx": 0.871,'
                     '      "Atax": 0.963,'
                     '      "Const": 0.1151,'
                     '      "Diarr": 0.9518,'
                     '      "Dysnt": 0.6154,'
                     '      "Dyspn": 0.6984,'
                     '      "Icter": 0.4119,'
                     '      "Lymph": 0.3372,'
                     '      "Pyrx": 0.6846,'
                     '      "SV_Oedm": 0.0385,'
                     '      "Stare": 0.6973,'
                     '      "Stunt": 0.4824,'
                     '      "Weak": 0.6523,'
                     '      "Wght_L": 0.614'
                     '    },'
                     '    "Fasciolosis": {'
                     '      "Anae": 0.0095,'
                     '      "Anrx": 0.977,'
                     '      "Atax": 0.1164,'
                     '      "Const": 0.1311,'
                     '      "Diarr": 0.0569,'
                     '      "Dysnt": 0.1604,'
                     '      "Dyspn": 0.0823,'
                     '      "Icter": 0.4349,'
                     '      "Lymph": 0.6208,'
                     '      "Pyrx": 0.9651,'
                     '      "SV_Oedm": 0.1108,'
                     '      "Stare": 0.8521,'
                     '      "Stunt": 0.5637,'
                     '      "Weak": 0.1865,'
                     '      "Wght_L": 0.7242'
                     '    },'
                     '    "LSD": {'
                     '      "Anae": 0.0883,'
                     '      "Anrx": 0.3197,'
                     '      "Atax": 0.9291,'
                     '      "Const": 0.6622,'
                     '      "Diarr": 0.631,'
                     '      "Dysnt": 0.6657,'
                     '      "Dyspn": 0.974,'
                     '      "Icter": 0.153,'
                     '      "Lymph": 0.8023,'
                     '      "Pyrx": 0.2831,'
                     '      "SV_Oedm": 0.4065,'
                     '      "Stare": 0.2959,'
                     '      "Stunt": 0.3347,'
                     '      "Weak": 0.5577,'
                     '      "Wght_L": 0.9966'
                     '    },'
                     '    "Lungworm": {'
                     '      "Anae": 0.4765,'
                     '      "Anrx": 0.7152,'
                     '      "Atax": 0.6797,'
                     '      "Const": 0.938,'
                     '      "Diarr": 0.6535,'
                     '      "Dysnt": 0.9752,'
                     '      "Dyspn": 0.6245,'
                     '      "Icter": 0.4954,'
                     '      "Lymph": 0.4811,'
                     '      "Pyrx": 0.3523,'
                     '      "SV_Oedm": 0.2446,'
                     '      "Stare": 0.6479,'
                     '      "Stunt": 0.7919,'
                     '      "Weak": 0.7959,'
                     '      "Wght_L": 0.0079'
                     '    },'
                     '    "PGE / GIT parasite": {'
                     '      "Anae": 0.2108,'
                     '      "Anrx": 0.078,'
                     '      "Atax": 0.6913,'
                     '      "Const": 0.664,'
                     '      "Diarr": 0.5129,'
                     '      "Dysnt": 0.1369,'
                     '      "Dyspn": 0.27,'
                     '      "Icter": 0.9672,'
                     '      "Lymph": 0.8923,'
                     '      "Pyrx": 0.1874,'
                     '      "SV_Oedm": 0.7678,'
                     '      "Stare": 0.4827,'
                     '      "Stunt": 0.6827,'
                     '      "Weak": 0.8251,'
                     '      "Wght_L": 0.4358'
                     '    },'
                     '    "Pasteurollosis": {'
                     '      "Anae": 0.5699,'
                     '      "Anrx": 0.8898,'
                     '      "Atax": 0.7183,'
                     '      "Const": 0.9549,'
                     '      "Diarr": 0.4316,'
                     '      "Dysnt": 0.5618,'
                     '      "Dyspn": 0.4728,'
                     '      "Icter": 0.5825,'
                     '      "Lymph": 0.2789,'
                     '      "Pyrx": 0.6803,'
                     '      "SV_Oedm": 0.1556,'
                     '      "Stare": 0.1606,'
                     '      "Stunt": 0.5968,'
                     '      "Weak": 0.4604,'
                     '      "Wght_L": 0.1261'
                     '    },'
                     '    "Rabies": {'
                     '      "Anae": 0.021,'
                     '      "Anrx": 0.1521,'
                     '      "Atax": 0.99,'
                     '      "Const": 0.553,'
                     '      "Diarr": 0.6056,'
                     '      "Dysnt": 0.123,'
                     '      "Dyspn": 0.5579,'
                     '      "Icter": 0.8676,'
                     '      "Lymph": 0.4572,'
                     '      "Pyrx": 0.4503,'
                     '      "SV_Oedm": 0.8823,'
                     '      "Stare": 0.6489,'
                     '      "Stunt": 0.0886,'
                     '      "Weak": 0.5222,'
                     '      "Wght_L": 0.4999'
                     '    },'
                     '    "Trypanosomosis": {'
                     '      "Anae": 0.3602,'
                     '      "Anrx": 0.6961,'
                     '      "Atax": 0.898,'
                     '      "Const": 0.6043,'
                     '      "Diarr": 0.5259,'
                     '      "Dysnt": 0.3489,'
                     '      "Dyspn": 0.6187,'
                     '      "Icter": 0.3156,'
                     '      "Lymph": 0.0677,'
                     '      "Pyrx": 0.0405,'
                     '      "SV_Oedm": 0.0257,'
                     '      "Stare": 0.5779,'
                     '      "Stunt": 0.9064,'
                     '      "Weak": 0.0779,'
                     '      "Wght_L": 0.9971'
                     '    },'
                     '    "Tuberculosis": {'
                     '      "Anae": 0.2207,'
                     '      "Anrx": 0.7513,'
                     '      "Atax": 0.9402,'
                     '      "Const": 0.5418,'
                     '      "Diarr": 0.9419,'
                     '      "Dysnt": 0.0402,'
                     '      "Dyspn": 0.6023,'
                     '      "Icter": 0.399,'
                     '      "Lymph": 0.6675,'
                     '      "Pyrx": 0.5587,'
                     '      "SV_Oedm": 0.4947,'
                     '      "Stare": 0.59,'
                     '      "Stunt": 0.1479,'
                     '      "Weak": 0.8633,'
                     '      "Wght_L": 0.085'
                     '    },'
                     '    "ZZ_Other": {'
                     '      "Anae": 0.6361,'
                     '      "Anrx": 0.1729,'
                     '      "Atax": 0.3008,'
                     '      "Const": 0.6395,'
                     '      "Diarr": 0.3737,'
                     '      "Dysnt": 0.858,'
                     '      "Dyspn": 0.9196,'
                     '      "Icter": 0.3255,'
                     '      "Lymph": 0.4681,'
                     '      "Pyrx": 0.7769,'
                     '      "SV_Oedm": 0.0234,'
                     '      "Stare": 0.9337,'
                     '      "Stunt": 0.3675,'
                     '      "Weak": 0.1286,'
                     '      "Wght_L": 0.0943'
                     '    }'
                     ' }\n \t }\n } ')
class diagnose(Resource):

    @staticmethod
    def options() -> Response:
        # This is required to allow the OPTIONS method to be used for CORS
        return jsonify({'status': 'ok'})

    @staticmethod
    @api.expect(diagnosis_payload_model, validate=True)
    def post() -> tuple[dict[str, str | int], int] | Response:

        data: [str, Union[str, Dict[str, int], None]] = request.get_json()
        animal: str = data['animal']

        animal = dh.validate_animal(animal)
        if animal is False:
            return {'error': 'Invalid animal. Please use a valid animal '
                             'from /data/valid_animals.', 'status': 404}, 404

        valid_signs: List[str] = dh.get_signs(animal)
        diseases: List[str] = dh.get_diseases(animal)
        wiki_ids: Dict[str, str] = dh.get_disease_wiki_ids(animal)

        # Check if the likelihoods are included in the API request data
        if data.get('likelihoods') is not None:
            likelihoods = dh.validate_likelihoods(data['likelihoods'], diseases, valid_signs)
        else:
            likelihoods: Dict[str, Dict[str, float]] = dh.get_likelihood_data(animal)

        # Get the signs from the API request data
        shown_signs: Dict[str, int] = data['signs']
        if set(shown_signs.keys()) != set(valid_signs):
            raise BadRequest(f'Invalid signs: {list(set(shown_signs.keys()) - set(valid_signs))}. '
                             f'Please use valid sign from /data/valid_signs/{animal}.')

        valid_sign_values = [0, 1, -1]
        for x, value in enumerate(shown_signs.values()):
            if value not in valid_sign_values:
                sign = list(shown_signs.keys())[x]
                raise BadRequest(f'Error with value of {sign}: {value}. Sign values must be either -1, 0 or 1')

        # Check if the priors are included in the API request data
        if data.get('priors') is not None:
            priors = dh.validate_priors(data.get('priors'), diseases)
        else:
            priors = dh.get_default_priors(diseases)

        # Perform calculations and normalisation
        results: Dict[str, float] = dh.calculate_results(diseases, likelihoods, shown_signs, priors)
        normalised_results: Dict[str, float] = dh.normalise(results)

        return jsonify({'results': normalised_results, 'wiki_ids': wiki_ids})


@api.route('/custom_diagnose', methods=['POST'])
@api.doc(responses={200: 'OK', 400: 'Bad Request', 500: 'Internal Server Error'},
         description='<h1>Description</h1><p>This endpoint takes a <a '
                     'href="https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON">JSON</a> '
                     'object containing the list of possible diseases for the animal you wish to diagnose,'
                     'the list of signs you intend to input,'
                     'the signs paired with the the value relating to the presence of the sign '
                     'and optionally a list of prior likelihood values for the disease to occur in the animal and the '
                     'type of animal it is. It then returns a list of diseases and their likelihood of being the cause '
                     'of the signs.</p> \n \n<p>The '
                     '<a href="https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON">JSON</a> object '
                     'must contain both "diseases", "signs" and "shown_signs" and can optionally contain "priors" and '
                     '"likelihoods"</p> \n \n<h1>'
                     'Parameters</h1><p>animal:  You can input any string, this is currently arbitrary and unused, '
                     'but may in future be used to store data to gather information.</p>\n \n<p>signs: This is a list '
                     'of signs that will be used to diagnose the animal. The list of signs must be the same as the '
                     'list of shown_signs for the animal you are diagnosing. </p>\n \n<p>shown_signs: This is a list '
                     'of signs that are present in the animal. The list of signs must be the same as the list of '
                     'signs for the animal you are diagnosing. The value of each sign must be either -1, 0 or 1. '
                     '-1 means the sign is not present, 0 means the sign is not observed  and 1 means the '
                     'sign is present in the animal.</p> \n \n'
                     '<p>likelihoods: This is the data which will be provided to the algorithm to calculate the '
                     'likelihood of each disease being the cause of the signs. The likelihoods must be formatted '
                     'as a dictionary with the disease as the key and a dictionary of signs and their likelihoods '
                     'as the value. The signs must be formatted as a dictionary with the sign as the key and the '
                     'likelihood of the sign being present for the disease as the value. The likelihoods must '
                     'be a float between 0 and 1. </p>\n \n'
                     '<p>priors: This is an optional parameter which does not need to be passed in '
                     'the payload.It is used to alter the prior likelihoods of diseases occurring which influences the '
                     'outcome of the Bayes algorithm. If this is not included, the algorithm assumes equal prior '
                     'likelihoods. The list of diseases and their prior likelihoods must add up to 100.'
                     'The priors must be formatted as a dictionary with the disease as the key and the prior '
                     'likelihood of the disease as the value. The prior likelihoods must be a float between 0 and 100'
                     '. You must include every disease in the list of diseases for the animal you are diagnosing. '
                     ' </p>\n \n <h1> '
                     'Example <a href="https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON">JSON'
                     '</a> '
                     'object:</h1> \n \n  {\n \"diseases\": [\"Rabies\",\"Cold\"], \n'
                     '\"signs\": [\"Fever\", \"Cough\", \"Diarrhoea\"],\n '
                     '\"shown_signs\": {\"Fever\": 1, \"Cough\": 0 \"Diarrhoea\": -1},\n '
                     '"likelihoods": {"Rabies": {"Fever": 0.6, "Cough": 0.1, "Diarrhoea": 0.1},"Cold": '
                     '{"Fever": 0.9,"Cough": 0.9,"Diarrhoea": 0.1}},\n '
                     '"priors": {"Rabies": 20,"Cold": 80 },\n "animal": "Dog" \n}')
class custom_diagnose(Resource):
    """
    This class is used to create the custom_diagnose endpoint.
    """

    @staticmethod
    def options() -> Response:
        # This is required to allow the OPTIONS method to be used for CORS
        return jsonify({'status': 'ok'})

    @staticmethod
    @api.expect(custom_diagnosis_payload_model, validate=True)
    def post():
        # This is the POST method for the custom_diagnose endpoint which allows the user to input their own data,
        # meaning the API can be used in a larger number of contexts.

        data: [str, Union[str, Dict[str, int], None]] = request.get_json()
        shown_signs: Dict[str, int] = data.get('shown_signs')
        likelihoods: Dict[str, Dict[str, float]] = data.get('likelihoods')
        diseases: List[str] = data.get('diseases')
        priors: Dict[str, float] = data.get('priors')
        sign_list: List[str] = data.get('signs')

        valid_sign_values = [0, 1, -1]
        # Check if the signs values are all valid
        for x, value in enumerate(shown_signs.values()):
            if value not in valid_sign_values:
                sign = list(shown_signs.keys())[x]
                raise BadRequest(f'Error with value of {sign}: {value}. Sign values must be either -1, 0 or 1')

        # Check to make sure the likelihoods are valid
        dh.validate_likelihoods(likelihoods, diseases, sign_list)

        # Check to make sure the priors are valid
        if priors is not None:
            dh.validate_priors(priors, diseases)
        else:
            priors = dh.get_default_priors(diseases)

        results: Dict[str, float] = dh.calculate_results(diseases, likelihoods, shown_signs, priors)
        normalised_results: Dict[str, float] = dh.normalise(results)

        return jsonify({'results': normalised_results})
