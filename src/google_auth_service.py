"""
Google Authentication Service
Provides resilient Google OAuth2 ID Token verification with:
- In-memory certificate caching (TTL based on Google's Cache-Control max-age, ~6 hours)
- HTTP connection retries with exponential backoff for transient network hiccups
- Stale certificate fallback on transient DNS/network drops
- Development / test environment offline fallback
- Clean classification of invalid tokens (401) vs service unreachable (503)
"""

import os
import time
import re
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from google.auth import jwt, exceptions as google_auth_exceptions
from logger import get_logger

logger = get_logger('google_auth_service')

GOOGLE_CERTS_URL = 'https://www.googleapis.com/oauth2/v1/certs'
VALID_ISSUERS = {'accounts.google.com', 'https://accounts.google.com'}
DEFAULT_CACHE_TTL = 21600  # 6 hours in seconds

class GoogleAuthError(Exception):
    """Base exception for Google authentication errors."""
    pass

class InvalidTokenError(GoogleAuthError):
    """Raised when an ID token is cryptographically invalid, expired, or wrong audience."""
    pass

class GoogleAuthServiceUnavailableError(GoogleAuthError):
    """Raised when Google's public certificates cannot be reached due to network/DNS failures."""
    pass


class GoogleAuthService:
    _certs_cache = None
    _certs_expires_at = 0
    _last_fetched_at = 0

    @classmethod
    def _create_http_session(cls):
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        return session

    @classmethod
    def get_google_certs(cls, force_refresh=False):
        """
        Fetch Google's public certificates with in-memory TTL caching.
        Falls back to stale cached certs if network/DNS resolution fails.
        """
        now = time.time()
        if not force_refresh and cls._certs_cache and now < cls._certs_expires_at:
            return cls._certs_cache

        try:
            session = cls._create_http_session()
            response = session.get(GOOGLE_CERTS_URL, timeout=(3.0, 5.0))
            if response.status_code == 200:
                certs = response.json()
                max_age = DEFAULT_CACHE_TTL
                cache_control = response.headers.get('Cache-Control', '')
                match = re.search(r'max-age=(\d+)', cache_control)
                if match:
                    max_age = int(match.group(1))

                cls._certs_cache = certs
                cls._certs_expires_at = now + max_age
                cls._last_fetched_at = now
                logger.debug(f"Google public certificates refreshed successfully (TTL: {max_age}s)")
                return certs
            else:
                logger.warning(f"Google certs endpoint returned unexpected status: {response.status_code}")
        except Exception as e:
            logger.warning(f"Failed to fetch Google public certs from {GOOGLE_CERTS_URL}: {e}")
            # If we have existing cached certs, use them as stale fallback!
            if cls._certs_cache:
                logger.info("Using stale cached Google certs due to network/DNS resolution failure.")
                return cls._certs_cache
            # No cache available
            raise GoogleAuthServiceUnavailableError(
                f"Google certificate endpoint unreachable: {e}"
            ) from e

        if cls._certs_cache:
            return cls._certs_cache
        raise GoogleAuthServiceUnavailableError("Unable to retrieve Google public certificates.")

    @classmethod
    def verify_id_token(cls, token, audience=None, is_dev_or_test=False):
        """
        Verify an ID Token issued by Google.
        Returns the decoded user info dict: {'sub': ..., 'email': ..., 'name': ...}
        """
        if not token or not isinstance(token, str):
            raise InvalidTokenError("ID Token is required and must be a string")

        token = token.strip()

        # 1. Check for mock token in development / test mode
        if token.startswith('mock-') and is_dev_or_test:
            mock_id = f"google-{token}"
            email = f"{token}@example.com"
            name = f"Mock {token}"
            return {
                'sub': mock_id,
                'email': email,
                'name': name
            }

        # 2. Try cryptographic verification with cached Google certificates
        try:
            certs = cls.get_google_certs()
            payload = jwt.decode(token, certs=certs, audience=audience)
            issuer = payload.get('iss')
            if issuer not in VALID_ISSUERS:
                raise InvalidTokenError(f"Invalid token issuer: {issuer}")
            return payload
        except GoogleAuthServiceUnavailableError as err:
            # Network / DNS failure fetching certs with no cache available
            if is_dev_or_test:
                # In development/test mode, fallback to unverified decoding if token has valid JWT structure
                try:
                    payload = jwt.decode(token, verify=False)
                    if payload and 'sub' in payload:
                        logger.warning(
                            f"DNS/network resolution failed for Google certs in dev/test. "
                            f"Proceeding with unverified claims for user: {payload.get('email', payload.get('sub'))}"
                        )
                        return payload
                except Exception:
                    pass
            raise err
        except (ValueError, google_auth_exceptions.InvalidValue, google_auth_exceptions.MalformedError) as err:
            raise InvalidTokenError(f"Token validation failed: {err}") from err
        except Exception as err:
            # Check if this was a transport/connection error wrapped inside
            err_str = str(err).lower()
            if 'resolution' in err_str or 'connection' in err_str or 'timeout' in err_str or 'name' in err_str:
                raise GoogleAuthServiceUnavailableError(f"Network transport error: {err}") from err
            raise InvalidTokenError(f"Token verification error: {err}") from err

    @classmethod
    def reset_cache(cls):
        """Helper for test suites to reset in-memory cache."""
        cls._certs_cache = None
        cls._certs_expires_at = 0
        cls._last_fetched_at = 0
