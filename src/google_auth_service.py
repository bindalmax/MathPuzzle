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

from pathlib import Path
import json

PRIMARY_CERTS_URL = 'https://www.googleapis.com/oauth2/v1/certs'
SECONDARY_CERTS_URL = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'
GOOGLE_CERTS_URL = PRIMARY_CERTS_URL  # Backward compatibility
VALID_ISSUERS = {'accounts.google.com', 'https://accounts.google.com'}
DEFAULT_CACHE_TTL = 21600  # 6 hours in seconds

BUNDLED_CERTS_PATHS = [
    Path(__file__).resolve().parent.parent / 'data' / 'google_certs_bundled.json',
    Path(__file__).resolve().parent / 'data' / 'google_certs_bundled.json',
    Path('/app/data/google_certs_bundled.json')
]

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
        # Force IPv4 resolution for Google endpoints to prevent connection hangs
        # on dual-stack Ubuntu hosts where containers lack outbound IPv6 routing.
        try:
            import urllib3.util.connection as urllib3_conn
            import socket
            urllib3_conn.allowed_gai_family = lambda: socket.AF_INET
        except Exception as e:
            logger.debug(f"Could not enforce IPv4 gai family: {e}")

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
    def _load_bundled_certs(cls):
        """Load bundled fallback certificates if network/DNS resolution fails on cold start."""
        for p in BUNDLED_CERTS_PATHS:
            try:
                if p.exists():
                    with open(p, 'r', encoding='utf-8') as f:
                        certs = json.load(f)
                        if isinstance(certs, dict) and len(certs) > 0:
                            logger.info(f"Loaded {len(certs)} bundled Google certificates from {p}")
                            return certs
            except Exception as err:
                logger.warning(f"Failed to read bundled certs from {p}: {err}")
        return None

    @classmethod
    def get_google_certs(cls, force_refresh=False):
        """
        Fetch Google's public certificates with in-memory TTL caching.
        Falls back to secondary endpoints, stale cache, and bundled certs if network/DNS fails.
        """
        now = time.time()
        if not force_refresh and cls._certs_cache and now < cls._certs_expires_at:
            return cls._certs_cache

        session = cls._create_http_session()
        last_error = None

        # 1. Try primary and secondary Google cert endpoints
        for certs_url in [PRIMARY_CERTS_URL, SECONDARY_CERTS_URL]:
            try:
                response = session.get(certs_url, timeout=(3.0, 5.0))
                if response.status_code == 200:
                    certs = response.json()
                    if isinstance(certs, dict) and len(certs) > 0:
                        max_age = DEFAULT_CACHE_TTL
                        cache_control = response.headers.get('Cache-Control', '')
                        match = re.search(r'max-age=(\d+)', cache_control)
                        if match:
                            max_age = int(match.group(1))

                        cls._certs_cache = certs
                        cls._certs_expires_at = now + max_age
                        cls._last_fetched_at = now
                        logger.debug(f"Google public certificates refreshed successfully from {certs_url} (TTL: {max_age}s)")
                        return certs
                else:
                    logger.warning(f"Google certs endpoint {certs_url} returned status: {response.status_code}")
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to fetch Google public certs from {certs_url}: {e}")

        # 2. If we have existing cached certs, use them as stale fallback!
        if cls._certs_cache:
            logger.info("Using stale cached Google certs due to network/DNS resolution failure.")
            return cls._certs_cache

        # 3. Fallback to bundled certificates on disk (protects against cold-start container DNS drops)
        bundled = cls._load_bundled_certs()
        if bundled:
            cls._certs_cache = bundled
            cls._certs_expires_at = now + DEFAULT_CACHE_TTL
            cls._last_fetched_at = now
            logger.info("Using bundled fallback Google certificates.")
            return bundled

        raise GoogleAuthServiceUnavailableError(
            f"Google certificate endpoint unreachable and no fallback available: {last_error}"
        )

    @classmethod
    def prewarm_cache(cls):
        """Asynchronously or synchronously populate certificates cache on server boot."""
        try:
            return cls.get_google_certs()
        except Exception as e:
            logger.warning(f"Pre-warm of Google certificates failed: {e}")
            return None

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
