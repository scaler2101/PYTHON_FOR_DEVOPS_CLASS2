"""Boundary for HTTP I/O: timeout, auth, limited retry, pagination."""
import logging
import time
import requests

LOG = logging.getLogger(__name__)
RETRYABLE_STATUS = {429, 500, 502, 503, 504}

class PlatformError(RuntimeError):
    pass

class PlatformClient:
    def __init__(self, base_url, token, timeout=2, attempts=3, session=None):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.attempts = attempts
        self.session = session if session is not None else requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {token}'})

    def get(self, path, params=None):
        for attempt in range(1, self.attempts + 1):
            try:
                response = self.session.get(self.base_url + path, params=params, timeout=self.timeout)
                if response.status_code in RETRYABLE_STATUS and attempt < self.attempts:
                    LOG.warning('HTTP %d on %s; retry %d/%d', response.status_code, path, attempt, self.attempts)
                    time.sleep(0.2 * attempt)
                    continue
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise PlatformError(f'Invalid response shape from {path}')
                return payload
            except (requests.Timeout, requests.ConnectionError) as exc:
                if attempt == self.attempts:
                    raise PlatformError(f'Network failure at {path}: {exc}') from exc
                LOG.warning('Network failure on %s; retry %d/%d', path, attempt, self.attempts)
                time.sleep(0.2 * attempt)
            except (requests.HTTPError, requests.exceptions.JSONDecodeError) as exc:
                raise PlatformError(f'HTTP or JSON failure at {path}: {exc}') from exc
        raise PlatformError(f'Retry exhausted for {path}')

    def inventory(self):
        page, result, max_pages = 1, [], 100
        while page <= max_pages:
            payload = self.get('/api/v1/services', params={'page': page, 'limit': 2})
            items = payload.get('items')
            if not isinstance(items, list): raise PlatformError('Missing services list')
            result.extend(items)
            next_page = payload.get('next_page')
            if next_page is None: return result
            if not isinstance(next_page, int) or next_page <= page:
                raise PlatformError('Pagination failed to advance')
            page = next_page
        raise PlatformError('Pagination exceeded safety limit')

    def incidents(self):
        payload = self.get('/api/v1/incidents')
        incidents = payload.get('items')
        if not isinstance(incidents, list): raise PlatformError('Invalid incidents list')
        return incidents

    def close(self):
        self.session.close()
