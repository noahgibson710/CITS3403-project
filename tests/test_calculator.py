import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash
import pytest

class CalculatorPageTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_calculator_get_route(self):
        response = self.app.get('/calculator')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Calculator Form', response.data)

    def test_calculator_form_fields_present(self):
        response = self.app.get('/calculator')
        html = response.get_data(as_text=True)
        self.assertIn('<select id="gender"', html)
        self.assertIn('<input type="number" id="age"', html)
        self.assertIn('<input type="number" id="weight"', html)
        self.assertIn('<input type="number" id="height"', html)
        self.assertIn('<select id="activity"', html)
        self.assertIn('<select id="calorie"', html)

    def test_calc_js_included(self):
        response = self.app.get('/calculator')
        html = response.get_data(as_text=True)
        self.assertIn('<script src="./static/js/calc.js"></script>', html)



    def test_invalid_age(self):
        response = self.app.post('/calculator', json={
            'gender': 'male',
            'age': 15,  # Invalid age
            'weight': 60.0,
            'height': 160,
            'activity': '1.2',
            'calorie': 'surplus'
        })
        self.assertEqual(response.status_code, 200)



if __name__ == '__main__':
    unittest.main()
