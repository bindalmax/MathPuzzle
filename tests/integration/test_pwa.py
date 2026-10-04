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
        # Check for dynamic version in CACHE_NAME
        from app import APP_VERSION
        self.assertIn(f"mathpuzzle-v{APP_VERSION}".encode(), response.data)
        
        # Check for headers
        self.assertEqual(response.headers.get('Cache-Control'), 'no-cache, no-store, must-revalidate')
        self.assertEqual(response.headers.get('Service-Worker-Allowed'), '/')
        # Ensure root path '/' is NOT in STATIC_ASSETS to prevent stale CSRF caching
        self.assertNotIn(b"'/'", response.data)
        self.assertNotIn(b'"/"', response.data)

    def test_homepage_pwa_tags(self):
        from app import APP_VERSION
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Check for manifest link with cache buster
        self.assertIn(f'<link rel="manifest" href="/manifest.json?v={APP_VERSION}">'.encode(), response.data)
        # Check for CSS link with cache buster
        self.assertIn(f'responsive.css?v={APP_VERSION}">'.encode(), response.data)
        # Check for theme-color
        self.assertIn(b'<meta name="theme-color" content="#4f46e5">', response.data)
        # Check for SW registration script
        self.assertIn(b'navigator.serviceWorker.register("/sw.js")', response.data)

    def test_icons_accessibility(self):
        response_192 = self.client.get('/static/icons/icon-192.png')
        self.assertEqual(response_192.status_code, 200)
        
        response_512 = self.client.get('/static/icons/icon-512.png')
        self.assertEqual(response_512.status_code, 200)

    def test_ads_txt(self):
        response = self.client.get('/ads.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/plain')
        self.assertIn(b'google.com, pub-4860872913350465, DIRECT, f08c47fec0942fa0', response.data)

    def test_robots_txt(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/plain')
        self.assertIn(b'User-agent: Mediapartners-Google', response.data)
        self.assertIn(b'Allow: /', response.data)

    def test_adsense_tags_consistency(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<meta name="google-adsense-account" content="ca-pub-4860872913350465">', response.data)
        self.assertIn(b'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4860872913350465', response.data)
        self.assertNotIn(b'ca-pub-8821650129943864', response.data)

if __name__ == '__main__':
    unittest.main()
