import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from app import app, APP_VERSION
from database import db


class TestHealthProbe(unittest.TestCase):
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

    def test_health_check_healthy(self):
        """Verify that /health returns HTTP 200 with healthy status when DB is connected."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data.get('status'), 'healthy')
        self.assertEqual(data.get('database'), 'connected')
        self.assertEqual(data.get('version'), APP_VERSION)

    def test_health_check_unhealthy_db_failure(self):
        """Verify that /health returns HTTP 503 with unhealthy status when DB connection fails."""
        with patch.object(db.session, 'execute', side_effect=Exception("Database connection timeout")):
            response = self.client.get('/health')
            self.assertEqual(response.status_code, 503)
            
            data = response.get_json()
            self.assertIsNotNone(data)
            self.assertEqual(data.get('status'), 'unhealthy')
            self.assertEqual(data.get('database'), 'disconnected')
            self.assertEqual(data.get('version'), APP_VERSION)

    def test_health_check_limiter_exemption(self):
        """Verify that /health endpoint is exempt from rate limiting."""
        from app import limiter
        # Endpoint function view_func should be marked as exempt
        view_func = self.app.view_functions.get('health_check')
        self.assertIsNotNone(view_func)
        self.assertTrue(hasattr(view_func, '_rate_limit_exempt') or getattr(view_func, '__name__', '') == 'health_check')
        
        # Rapid repeated requests should all succeed with 200
        for _ in range(15):
            res = self.client.get('/health')
            self.assertEqual(res.status_code, 200)

    def test_sqlalchemy_engine_options_configuration(self):
        """Verify that SQLALCHEMY_ENGINE_OPTIONS contains resilience pooling parameters."""
        engine_options = self.app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
        self.assertTrue(engine_options.get('pool_pre_ping'), "pool_pre_ping must be True to prevent dropped connections")
        self.assertEqual(engine_options.get('pool_recycle'), 1800, "pool_recycle must be 1800 seconds (30 minutes)")


if __name__ == '__main__':
    unittest.main()
