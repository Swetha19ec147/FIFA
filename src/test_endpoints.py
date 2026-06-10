import os
import sys
import unittest
import json

# Setup sys path to import app correctly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

from app import app

class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_homepage(self):
        print("Testing GET /")
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)

    def test_api_teams(self):
        print("Testing GET /api/teams")
        response = self.client.get('/api/teams')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('teams', data)
        self.assertGreater(len(data['teams']), 0)
        
        # Test team structure
        first_team = data['teams'][0]
        self.assertIn('name', first_team)
        self.assertIn('elo', first_team)
        self.assertIn('avg_shots', first_team)
        self.assertIn('avg_corners', first_team)
        self.assertIn('elo_history', first_team)

    def test_api_standings(self):
        print("Testing GET /api/standings")
        response = self.client.get('/api/standings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('standings', data)
        self.assertGreater(len(data['standings']), 0)
        
        # Test standing row structure
        first_row = data['standings'][0]
        self.assertIn('team', first_row)
        self.assertIn('played', first_row)
        self.assertIn('won', first_row)
        self.assertIn('gf', first_row)
        self.assertIn('gd', first_row)
        self.assertIn('points', first_row)
        self.assertIn('rank', first_row)

    def test_api_matches(self):
        print("Testing GET /api/matches")
        response = self.client.get('/api/matches')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('completed', data)
        self.assertIn('upcoming', data)

    def test_api_predict(self):
        print("Testing POST /api/predict")
        payload = {
            'home_team': 'Man City',
            'away_team': 'Arsenal'
        }
        response = self.client.post(
            '/api/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('prediction', data)
        pred = data['prediction']
        self.assertIn('home_win_prob', pred)
        self.assertIn('draw_prob', pred)
        self.assertIn('away_win_prob', pred)
        self.assertIn('predicted_score', pred)
        self.assertIn('expected_goals_home', pred)
        self.assertIn('expected_goals_away', pred)

    def test_api_simulate_step(self):
        print("Testing POST /api/simulate-step")
        payload = {
            'home_team': 'Man City',
            'away_team': 'Arsenal',
            'minute': 10,
            'home_goals': 0,
            'away_goals': 0,
            'home_red_cards': 0,
            'away_red_cards': 0,
            'home_shots': 1,
            'away_shots': 0,
            'home_sot': 0,
            'away_sot': 0,
            'home_corners': 0,
            'away_corners': 0,
            'home_fouls': 1,
            'away_fouls': 2
        }
        response = self.client.post(
            '/api/simulate-step',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('minute', data)
        self.assertIn('stats', data)
        self.assertIn('events', data)
        self.assertIn('prediction', data)
        
        # Verify prediction keys
        pred = data['prediction']
        self.assertIn('home_win_prob', pred)
        self.assertIn('draw_prob', pred)
        self.assertIn('away_win_prob', pred)
        
        # Verify stats keys
        stats = data['stats']
        self.assertIn('home_goals', stats)
        self.assertIn('away_goals', stats)
        self.assertIn('possession_home', stats)
        self.assertIn('possession_away', stats)

    def test_api_manual(self):
        print("Testing GET /api/manual")
        response = self.client.get('/api/manual')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('manual', data)
        self.assertIn('sections', data['manual'])
        self.assertIn('faqs', data['manual'])

    def test_api_refresh_data(self):
        print("Testing POST /api/refresh-data")
        response = self.client.post('/api/refresh-data')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('message', data)

if __name__ == "__main__":
    unittest.main()
