import unittest
from werkzeug.exceptions import BadRequest

from diagnosis_helper import validate_priors, validate_likelihoods, calculate_results, normalise, validate_animal


class TestValidatePriors(unittest.TestCase):

    def test_valid_priors(self):
        priors = {'disease1': 30, 'disease2': 40, 'disease3': 30}
        diseases = ['disease1', 'disease2', 'disease3']
        self.assertEqual(validate_priors(priors, diseases), priors)

    def test_invalid_disease(self):
        priors = {'disease1': 30, 'disease2': 40, 'disease4': 30}
        diseases = ['disease1', 'disease2', 'disease3']
        with self.assertRaises(BadRequest) as cm:
            validate_priors(priors, diseases)
        self.assertEqual(str(cm.exception),
                         "400 Bad Request: Disease 'disease4' is not a valid disease. Please use a valid disease from "
                         "['disease1', 'disease2', 'disease3'].")

    def test_missing_disease(self):
        priors = {'disease1': 30, 'disease2': 40}
        diseases = ['disease1', 'disease2', 'disease3']
        with self.assertRaises(BadRequest) as cm:
            validate_priors(priors, diseases)
        self.assertEqual(str(cm.exception),
                         "400 Bad Request: Missing 'disease3' in priors. Please provide a prior likelihood value "
                         "for all diseases.")

    def test_priors_not_add_up_to_100(self):
        priors = {'disease1': 30, 'disease2': 40, 'disease3': 35}
        diseases = ['disease1', 'disease2', 'disease3']
        with self.assertRaises(BadRequest) as cm:
            validate_priors(priors, diseases)
        self.assertEqual(str(cm.exception), "400 Bad Request: Priors must add up to 100. Currently they add up to 105.")


class TestValidateLikelihoods(unittest.TestCase):
    def test_valid_likelihoods(self):
        likelihoods = {'disease1': {'sign1': 0.3, 'sign2': 0.4, 'sign3': 0.2, 'sign4': 0.1},
            'disease2': {'sign1': 0.1, 'sign2': 0.2, 'sign3': 0.3, 'sign4': 0.4},
            'disease3': {'sign1': 0.2, 'sign2': 0.3, 'sign3': 0.2, 'sign4': 0.3}}
        diseases = ['disease1', 'disease2', 'disease3']
        signs = ['sign1', 'sign2', 'sign3', 'sign4']
        self.assertEqual(validate_likelihoods(likelihoods, diseases, signs), likelihoods)

    def test_invalid_disease(self):
        likelihoods = {'disease1': {'sign1': 0.3, 'sign2': 0.4, 'sign3': 0.2, 'sign4': 0.1},
            'disease2': {'sign1': 0.1, 'sign2': 0.2, 'sign3': 0.3, 'sign4': 0.4},
            'disease4': {'sign1': 0.2, 'sign2': 0.3, 'sign3': 0.2, 'sign4': 0.3}}
        diseases = ['disease1', 'disease2', 'disease3']
        signs = ['sign1', 'sign2', 'sign3', 'sign4']
        with self.assertRaises(BadRequest) as cm:
            validate_likelihoods(likelihoods, diseases, signs)
        self.assertEqual(str(cm.exception),
                         "400 Bad Request: Disease 'disease4' in 'likelihoods' is not a valid disease.")

    def test_missing_disease(self):
        likelihoods = {'disease1': {'sign1': 0.3, 'sign2': 0.4, 'sign3': 0.2, 'sign4': 0.1},
            'disease2': {'sign1': 0.1, 'sign2': 0.2, 'sign3': 0.3, 'sign4': 0.4}}
        diseases = ['disease1', 'disease2', 'disease3']
        signs = ['sign1', 'sign2', 'sign3', 'sign4']
        with self.assertRaises(BadRequest) as cm:
            validate_likelihoods(likelihoods, diseases, signs)
        self.assertEqual(str(cm.exception),
                         "400 Bad Request: Missing 'disease3' in likelihoods. Please provide a "
                         "likelihood value for all diseases.")

    def test_invalid_sign(self):
        likelihoods = {'disease1': {'sign1': 0.3, 'sign2': 0.4, 'sign3': 0.2, 'sign4': 0.1},
            'disease2': {'sign1': 0.1, 'sign2': 0.2, 'sign3': 1.3, 'sign4': 0.4},
                       'disease3': {'sign1': 0.2, 'sign2': 0.3, 'sign3': 0.2, 'sign5': 0.3}}
        diseases = ['disease1', 'disease2', 'disease3']
        signs = ['sign1', 'sign2', 'sign3', 'sign4']
        with self.assertRaises(BadRequest) as cm:
            validate_likelihoods(likelihoods, diseases, signs)
        self.assertEqual(str(cm.exception),
                         "400 Bad Request: Sign 'sign3' in 'likelihoods' for disease 'disease2' is not a valid sign.")

    def test_invalid_sign(self):
        likelihoods = {'disease1': {'sign1': 0.3, 'sign2': 0.4, 'sign3': 0.2, 'sign4': 0.1},
            'disease2': {'sign1': 0.1, 'sign2': 0.2, 'sign3': 1.3, 'sign4': 0.4},
            'disease3': {'sign1': 0.2, 'sign2': 0.3, 'sign3': 0.2, 'sign4': 0.3}}
        diseases = ['disease1', 'disease2', 'disease3']
        signs = ['sign1', 'sign2', 'sign3', 'sign4']
        with self.assertRaises(BadRequest) as cm:
            validate_likelihoods(likelihoods, diseases, signs)
        self.assertEqual(str(cm.exception),
                         "400 Bad Request: Likelihood for sign 'sign3' in disease 'disease2' is not a valid value. "
                         "Please use a value greater than 0 and less than 1.")

    def test_missing_sign(self):
        likelihoods = {'disease1': {'sign1': 0.3, 'sign2': 0.4, 'sign3': 0.2, 'sign4': 0.1},
            'disease2': {'sign1': 0.1, 'sign2': 0.2, 'sign4': 0.4},
            'disease3': {'sign1': 0.2, 'sign2': 0.3, 'sign3': 0.2, 'sign4': 0.3}}
        diseases = ['disease1', 'disease2', 'disease3']
        signs = ['sign1', 'sign2', 'sign3', 'sign4']
        with self.assertRaises(BadRequest) as cm:
            validate_likelihoods(likelihoods, diseases, signs)
        self.assertEqual(str(cm.exception),
                         "400 Bad Request: Missing 'sign3' in likelihoods for disease 'disease2'. Please provide a "
                         "likelihood value for all signs.")

    def test_invalid_likelihood_value(self):
        likelihoods = {'disease1': {'sign1': 0.3, 'sign2': 0.4, 'sign3': 0.2, 'sign4': 0},
            'disease2': {'sign1': 0.1, 'sign2': 0.2, 'sign3': 0.3, 'sign4': 1},
            'disease3': {'sign1': 0.2, 'sign2': 0.3, 'sign3': 0.2, 'sign4': 0.3}}
        diseases = ['disease1', 'disease2', 'disease3']
        signs = ['sign1', 'sign2', 'sign3', 'sign4']
        with self.assertRaises(BadRequest) as cm:
            validate_likelihoods(likelihoods, diseases, signs)
        self.assertEqual(str(cm.exception),
                         "400 Bad Request: Likelihood for sign 'sign4' in disease 'disease1' is not a valid value. "
                         "Please use a value greater than 0 and less than 1.")

class TestCalculateResults(unittest.TestCase):
    def test_calculate_results(self):
        likelihoods = {'disease1': {'sign1': 0.3, 'sign2': 0.4, 'sign3': 0.2, 'sign4': 0.1},
            'disease2': {'sign1': 0.1, 'sign2': 0.2, 'sign3': 0.3, 'sign4': 0.4},
            'disease3': {'sign1': 0.2, 'sign2': 0.3, 'sign3': 0.2, 'sign4': 0.3}}
        diseases = ['disease1', 'disease2', 'disease3']
        shown_signs = {'sign1': 1, 'sign2': 1, 'sign3': -1, 'sign4': -1}
        priors = {'disease1': 30, 'disease2': 50, 'disease3': 20}
        expected_results = {'disease1': 259.2, 'disease2': 42.00000000000001, 'disease3': 67.19999999999999}
        self.assertDictEqual(calculate_results(diseases, likelihoods, shown_signs, priors), expected_results)

class TestNormalise(unittest.TestCase):
    def test_normalise(self):
        results = {'disease1': 259.2, 'disease2': 42.00000000000001, 'disease3': 67.19999999999999}
        expected_results = {'disease1': 70.35830618892508, 'disease2': 11.400651465798047,
                            'disease3': 18.24104234527687}
        self.assertDictEqual(normalise(results), expected_results)


class TestValidateAnimal(unittest.TestCase):
    def test_valid_animal(self):
        animal = 'Cattle'
        self.assertEqual(validate_animal(animal), animal)

    def test_invalid_animal(self):
        animal = 'Dog'
        self.assertEqual(validate_animal(animal), False)


if __name__ == '__main__':
    unittest.main()
