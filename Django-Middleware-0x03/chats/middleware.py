import os
import threading
from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from collections import defaultdict, deque

class RequestLoggingMiddleware:
    """Logs each request with timestamp, user (or anonymous), and path to a file."""
    def __init__(self, get_response):
        self.get_response = get_response
        self.log_file = getattr(settings, 'REQUEST_LOG_FILE', os.path.join(settings.BASE_DIR, 'requests.log'))
        self._lock = threading.Lock()
    def __call__(self, request):
        user = getattr(request, 'user', None)
        user_repr = getattr(user, 'username', 'anonymous') if user and user.is_authenticated else 'anonymous'
        # Match required format: f"{datetime.now()} - User: {user} - Path: {request.path}"
        line = f"{datetime.now()} - User: {user_repr} - Path: {request.path}\n"
        try:
            with self._lock:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(line)
        except Exception:
            # Fail silently; logging must not break the app
            pass
        return self.get_response(request)

class RestrictAccessByTimeMiddleware:
    """Restricts access to chat endpoints outside allowed hours."""
    def __init__(self, get_response):
        self.get_response = get_response
        # Expect a tuple (start_hour, end_hour) in 24h format
        self.allowed_hours = getattr(settings, 'ALLOWED_CHAT_HOURS', (18, 21))
    def __call__(self, request):
        # Only restrict API chat paths
        if request.path.startswith('/api/'):
            now_hour = datetime.utcnow().hour  # Use UTC to align with TIME_ZONE = UTC
            start_hour, end_hour = self.allowed_hours
            # Allowed window: start <= hour < end
            allowed = start_hour <= now_hour < end_hour
            if not allowed:
                return HttpResponseForbidden('Chat access is restricted during this time.')
        return self.get_response(request)

class OffensiveLanguageMiddleware:
    """Rate limits number of POST chat messages per IP within a rolling time window."""
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'CHAT_MESSAGE_RATE_LIMIT', 5)
        self.window_seconds = getattr(settings, 'CHAT_MESSAGE_RATE_WINDOW_SECONDS', 60)
        # Map ip -> deque of timestamps
        self.ip_timestamps: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()
    def __call__(self, request):
        if request.method == 'POST' and request.path.startswith('/api/messages'):
            ip = self._get_ip(request)
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=self.window_seconds)
            with self._lock:
                dq = self.ip_timestamps[ip]
                # Purge old entries
                while dq and dq[0] < window_start:
                    dq.popleft()
                if len(dq) >= self.rate_limit:
                    return JsonResponse({'error': 'Rate limit exceeded. Try again later.'}, status=429)
                dq.append(now)
        return self.get_response(request)
    def _get_ip(self, request):
        # Basic extraction; can be extended for X-Forwarded-For
        return request.META.get('REMOTE_ADDR', '0.0.0.0')

class RolePermissionMiddleware:
    """Enforces that only users with specific roles can access protected chat endpoints."""
    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_prefixes = getattr(settings, 'ROLE_PROTECTED_PATH_PREFIXES', ['/api/messages', '/api/conversations'])
        self.allowed_roles = getattr(settings, 'ROLE_ALLOWED_ROLES', {'admin', 'host'})
    def __call__(self, request):
        path = request.path
        if any(path.startswith(prefix) for prefix in self.protected_prefixes):
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                return HttpResponseForbidden('Authentication required.')
            # Accept staff/superuser automatically
            if user.is_staff or user.is_superuser:
                return self.get_response(request)
            role = getattr(user, 'role', None)
            if role not in self.allowed_roles:
                return HttpResponseForbidden('You do not have permission to access this resource.')
        return self.get_response(request)
