import unittest
import os
import sys
import logging
from unittest.mock import patch, MagicMock

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from logger import setup_root_logger, get_logger, setup_app_logging, get_log_level
from flask import Flask

class TestLogger(unittest.TestCase):
    def test_get_log_level_default(self):
        with patch.dict(os.environ, {}, clear=False):
            if 'LOG_LEVEL' in os.environ:
                del os.environ['LOG_LEVEL']
            level = get_log_level()
            self.assertEqual(level, logging.INFO)

    def test_get_log_level_override(self):
        with patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG'}):
            level = get_log_level()
            self.assertEqual(level, logging.DEBUG)

    def test_setup_root_logger(self):
        root = setup_root_logger()
        self.assertIsNotNone(root)
        self.assertTrue(len(root.handlers) >= 1)

    def test_get_logger_named(self):
        log = get_logger('test_component')
        self.assertEqual(log.name, 'test_component')
        self.assertIsInstance(log, logging.Logger)

    def test_setup_app_logging(self):
        test_app = Flask('test_logger_app')
        setup_app_logging(test_app)
        self.assertTrue(len(test_app.logger.handlers) >= 1)

        # Test request lifecycle timing with test client
        @test_app.route('/ping')
        def ping():
            return 'pong'

        client = test_app.test_client()
        resp = client.get('/ping')
        self.assertEqual(resp.status_code, 200)

if __name__ == '__main__':
    unittest.main()
