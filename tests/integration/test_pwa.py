import unittest
import os
import sys

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from app import app
from database import db

class TestPWAIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_manifest_route(self):
        response = self.client.get('/manifest.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/manifest+json')
        self.assertIn(b'"short_name": "MathPuzzle"', response.data)
        self.assertIn(b'"id": "/"', response.data)
        self.assertIn(b'"screenshots"', response.data)
        self.assertIn(b'"form_factor": "narrow"', response.data)
        self.assertIn(b'"form_factor": "wide"', response.data)

    def test_sw_route(self):
        response = self.client.get('/sw.js')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/javascript')
        self.assertIn(b'CACHE_NAME', response.data)

    def test_homepage_pwa_tags(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Check for manifest link
        self.assertIn(b'<link rel="manifest" href="/manifest.json">', response.data)
        # Check for theme-color
        self.assertIn(b'<meta name="theme-color" content="#4f46e5">', response.data)
        # Check for SW registration script
        self.assertIn(b'navigator.serviceWorker.register("/sw.js")', response.data)

    def test_icons_accessibility(self):
        response_192 = self.client.get('/static/icons/icon-192.png')
        self.assertEqual(response_192.status_code, 200)
        
        response_512 = self.client.get('/static/icons/icon-512.png')
        self.assertEqual(response_512.status_code, 200)

if __name__ == '__main__':
    unittest.main()
