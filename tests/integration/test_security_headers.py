import unittest
import os
import sys

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from app import app
from database import db

class TestSecurityHeaders(unittest.TestCase):
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

    def test_security_headers_baseline(self):
        """Verify presence and strict values of mandatory HTTP security headers."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # 1. MIME type sniffing prevention
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')

        # 2. Clickjacking prevention
        self.assertEqual(response.headers.get('X-Frame-Options'), 'SAMEORIGIN')

        # 3. Referrer Policy
        self.assertEqual(response.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')

        # 4. Permissions Policy
        perm_policy = response.headers.get('Permissions-Policy')
        self.assertIsNotNone(perm_policy)
        self.assertIn('camera=()', perm_policy)
        self.assertIn('microphone=()', perm_policy)

        # 5. Content Security Policy (CSP)
        csp = response.headers.get('Content-Security-Policy')
        self.assertIsNotNone(csp, "Content-Security-Policy header must be present")
        self.assertIn("default-src 'self'", csp)
        self.assertIn("https://accounts.google.com", csp)
        self.assertIn("googlesyndication.com", csp)
        self.assertIn("adtrafficquality.google", csp)
        self.assertIn("doubleclick.net", csp)
        self.assertIn("https://cdn.jsdelivr.net", csp)
        self.assertIn("https://fonts.googleapis.com", csp)
        self.assertIn("https://fonts.gstatic.com", csp)
        self.assertIn("ws:", csp)
        self.assertIn("wss:", csp)
        self.assertIn("object-src 'none'", csp)
        self.assertIn("base-uri 'self'", csp)

    def test_security_headers_across_routes(self):
        """Verify that security headers are uniformly enforced across all routes."""
        routes = ['/', '/leaderboard', '/how-to-play', '/about', '/faq', '/privacy', '/terms']
        for route in routes:
            with self.subTest(route=route):
                resp = self.client.get(route)
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.headers.get('X-Content-Type-Options'), 'nosniff')
                self.assertEqual(resp.headers.get('X-Frame-Options'), 'SAMEORIGIN')
                self.assertEqual(resp.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
                self.assertIsNotNone(resp.headers.get('Content-Security-Policy'))

    def test_hsts_when_forwarded_https(self):
        """Verify Strict-Transport-Security is attached when request is secure (HTTPS)."""
        response = self.client.get('/', headers={'X-Forwarded-Proto': 'https'})
        self.assertEqual(response.status_code, 200)
        hsts = response.headers.get('Strict-Transport-Security')
        self.assertIsNotNone(hsts)
        self.assertIn('max-age=31536000', hsts)
        self.assertIn('includeSubDomains', hsts)

    def test_session_cookie_security_configuration(self):
        """Verify session cookie configuration flags."""
        self.assertTrue(self.app.config.get('SESSION_COOKIE_HTTPONLY'))
        self.assertEqual(self.app.config.get('SESSION_COOKIE_SAMESITE'), 'Lax')
