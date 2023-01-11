import numpy as np
from flask import Flask, request, jsonify
from openpyxl import load_workbook

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Documentation can be detailed here.'


@app.route('/diagnose', methods=['POST'])
def diagnose():
    likelihood_values = []
    data = request.get_json()
    animal = data['animal']
    # TODO: symptom data should be passed as below but is currently just a list of 1 or 0
    #  which has to be formatted correctly. It is probably best to fix this first so everything else can
    #  conform to this standard going forward..
    # {
    #     "animal": "Cattle",
    #     "symptoms": {
    #         "Anae": 1,
    #         "Anrx": 0,
    #         "Atax": 0,
    #         "Const": 0,
    #         "Diarr": 0,
    #         "Dysnt": 0,
    #         "Dyspn": 0,
    #         "Icter": 0,
    #         "Lymph": 0,
    #         "Pyrx": 0,
    #         "Stare": 0,
    #         "Stunt": 0,
    #         "SV_Oedm": 0,
    #         "Weak": 0,
    #         "Wght_L": 0
    #     }
    # }
    shown_symptoms = data['symptoms']
    # used to store the values of the Bayes calculation before we zip them together in a dictionary with the names of
    # diseases
    results = []
    # Get the correct data from the data Excel sheet
    diseases, likelihoods = get_disease_data(animal)

    for dis in likelihoods:
        # TODO: find a way around this solution
        if dis != 'Disease':
            # TODO: fix this too, I am currently grabbing a list and appending
            #  it to an existing list of lists to populate the matrix, there has to a better way
            likelihood_values.append(likelihoods[dis])
        # TODO: alter this down the line to take data from an API request so we don't always 
        #  have to assume priors are equal
    prior_likelihoods = np.full(shape=len(likelihood_values), fill_value=100 / len(likelihood_values), dtype=float)

    for x in range(len(likelihood_values)):
        # Start probability at 1
        chain_probability = 1.0
        for y in range(len(likelihood_values[0])):
            # likelihood is not impacted if it's not observed but may still be present, hence set to 1 ahead of time
            likelihood = 1
            if shown_symptoms[y] == 1:
                # if the symptom is present then grab the data from the matrix
                likelihood = likelihood_values[x][y]
            elif shown_symptoms[y] == -1:
                # if the symptom is not present, take the complement
                likelihood = 1 - likelihood_values[x][y]
            # multiply to get the chain probability
            chain_probability *= likelihood
            # calculate posterior
            posterior = chain_probability * prior_likelihoods[x]
            # get results in a list
        results.append(posterior * 100.0)
    # Normalise the output
    normalised_results = normalise(results)
    # Zip the outputs with the disease names
    final_results = zip_data(diseases, normalised_results)
    # Finally, fulfil the API request
    return jsonify({'results': final_results})


# A function used to collect the data from the Excel workbook which I manually formatted to ensure the data works.
def get_disease_data(animal):
    # Get the workbook (the file path is currently set to the path used on pythonanywhere but this should be changed as
    # needed).
    wb = load_workbook(filename='/home/Frasercs/mysite/data.xlsx')
    # Animal is the string passed in the function which directs to the correct sheet in the workbook
    ws = wb[animal]
    # This has to be set as 0 for the setting of the likelihood in the dictionary on first pass otherwise we would get
    # an error as it is unassigned
    disease = 0
    diseases = []
    likelihoods = {}
    # Loop through all rows in the workbook
    for row in ws.rows:
        # TODO: this is used to skip the first row, we will still need to cover the first row
        #  as it is what gives the sign data but for now this is necessary.
        if row[0].value != 'Disease':
            disease = row[0].value
            diseases.append(disease)
        symptom_likelihoods = []
        # This is used to skip the disease name
        for cell in row[1:]:
            symptom_likelihoods.append(cell.value)
        # TODO: fix this so that it is not required, change is needed at line 95 however ws.rows isn't iterable so I
        #  can't just slice it, sadly.
        if disease != 0:
            likelihoods[disease] = symptom_likelihoods
    return diseases, likelihoods


# A function used to normalise the outputs of the bayes calculation
def normalise(results):
    normalised_results = []
    summed_results = sum(results)
    for r in results:
        value = r
        norm = value / summed_results
        normalised_results.append(norm * 100)

    return normalised_results


# A function used to zip together the diseases with their likelihoods after all calculations have taken place
# So they can be returned through the API in a useful manner
def zip_data(key, value):
    results = {}
    for k in key:
        for v in value:
            results[k] = v
            value.remove(v)
            break
    return results


if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)
