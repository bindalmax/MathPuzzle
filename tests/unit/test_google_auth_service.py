import unittest
import os
import sys
import time
from unittest.mock import patch, MagicMock

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from google_auth_service import (
    GoogleAuthService,
    GoogleAuthServiceUnavailableError,
    InvalidTokenError
)


class TestGoogleAuthService(unittest.TestCase):
    def setUp(self):
        GoogleAuthService.reset_cache()

    def tearDown(self):
        GoogleAuthService.reset_cache()

    def test_get_google_certs_caching(self):
        """Verify that Google public certificates are cached and reused within TTL."""
        fake_certs = {'key1': 'cert1', 'key2': 'cert2'}
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = fake_certs
        mock_response.headers = {'Cache-Control': 'public, max-age=3600'}

        with patch.object(GoogleAuthService, '_create_http_session') as mock_session_factory:
            mock_session = MagicMock()
            mock_session.get.return_value = mock_response
            mock_session_factory.return_value = mock_session

            # 1. First call fetches from endpoint
            certs1 = GoogleAuthService.get_google_certs()
            self.assertEqual(certs1, fake_certs)
            self.assertEqual(mock_session.get.call_count, 1)

            # 2. Second call should be served from memory cache (no HTTP call)
            certs2 = GoogleAuthService.get_google_certs()
            self.assertEqual(certs2, fake_certs)
            self.assertIs(certs1, certs2)
            self.assertEqual(mock_session.get.call_count, 1)

    def test_stale_certs_fallback_on_network_error(self):
        """Verify that when network/DNS fails on refresh, stale cached certs are returned."""
        fake_certs = {'key1': 'cert1'}
        GoogleAuthService._certs_cache = fake_certs
        GoogleAuthService._certs_expires_at = time.time() - 100  # Expired

        with patch.object(GoogleAuthService, '_create_http_session') as mock_session_factory:
            mock_session = MagicMock()
            # Simulate DNS failure
            mock_session.get.side_effect = Exception("Temporary failure in name resolution")
            mock_session_factory.return_value = mock_session

            # Should return stale cached certs with a warning rather than crashing
            certs = GoogleAuthService.get_google_certs(force_refresh=True)
            self.assertEqual(certs, fake_certs)

    def test_service_unavailable_when_no_cache_and_network_fails(self):
        """Verify that GoogleAuthServiceUnavailableError is raised if network fails without cache."""
        GoogleAuthService.reset_cache()

        with patch.object(GoogleAuthService, '_create_http_session') as mock_session_factory:
            mock_session = MagicMock()
            mock_session.get.side_effect = Exception("Failed to resolve 'www.googleapis.com'")
            mock_session_factory.return_value = mock_session

            with self.assertRaises(GoogleAuthServiceUnavailableError):
                GoogleAuthService.get_google_certs()

    def test_mock_token_in_dev_mode(self):
        """Verify that mock tokens decode immediately in development mode."""
        res = GoogleAuthService.verify_id_token('mock-supergamer', is_dev_or_test=True)
        self.assertEqual(res['sub'], 'google-mock-supergamer')
        self.assertEqual(res['email'], 'mock-supergamer@example.com')
        self.assertEqual(res['name'], 'Mock mock-supergamer')

    def test_invalid_token_missing_or_bad_type(self):
        """Verify that empty or non-string tokens raise InvalidTokenError."""
        with self.assertRaises(InvalidTokenError):
            GoogleAuthService.verify_id_token('')
        with self.assertRaises(InvalidTokenError):
            GoogleAuthService.verify_id_token(None)

    def test_dev_fallback_on_network_error(self):
        """Verify that in dev/test, if Google certs cannot be fetched, unverified claims are extracted."""
        GoogleAuthService.reset_cache()
        # Simulated valid JWT structure for testing dev fallback
        # Payload: {"sub": "12345", "email": "test@domain.com", "name": "Dev User"}
        # Header: {"alg": "RS256", "kid": "key1"}
        sample_jwt = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImtleTEifQ.eyJzdWIiOiIxMjM0NSIsImVtYWlsIjoidGVzdEBkb21haW4uY29tIiwibmFtZSI6IkRldiBVc2VyIn0.c2lnbmF0dXJl"

        with patch.object(GoogleAuthService, 'get_google_certs', side_effect=GoogleAuthServiceUnavailableError("DNS down")):
            claims = GoogleAuthService.verify_id_token(sample_jwt, is_dev_or_test=True)
            self.assertEqual(claims['sub'], '12345')
            self.assertEqual(claims['email'], 'test@domain.com')
            self.assertEqual(claims['name'], 'Dev User')


if __name__ == '__main__':
    unittest.main()
