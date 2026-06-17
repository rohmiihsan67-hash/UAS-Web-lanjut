from django.http import HttpResponseForbidden
from .models import BlockedIP


class IPBlockingMiddleware:
    """
    Middleware utama:
    1. Memblokir IP yang ada di daftar BlockedIP.
    2. Mencatat setiap request ke SecurityLog (kecuali static/media files).
    """
    SKIP_PATHS = ('/static/', '/media/', '/favicon.ico')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        # 1. Cek apakah IP diblokir
        if BlockedIP.objects.filter(ip_address=ip).exists():
            self._log(request, ip, 'blocked')
            return HttpResponseForbidden(
                "<h1 style='font-family:sans-serif;text-align:center;margin-top:80px;color:#b91c1c;'>"
                "🚫 Akses Ditolak</h1>"
                "<p style='text-align:center;font-family:sans-serif;color:#555;'>"
                "IP Anda telah diblokir oleh administrator sistem.</p>"
            )

        response = self.get_response(request)

        # 2. Catat log (skip file statis)
        if not any(request.path.startswith(p) for p in self.SKIP_PATHS):
            self._log(request, ip, 'allowed')

        return response

    def _log(self, request, ip, status):
        """Simpan log ke database secara aman (tidak crash jika ada error)."""
        try:
            from .models import SecurityLog
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            SecurityLog.objects.create(
                ip_address=ip,
                path=request.path[:500],
                method=request.method,
                status=status,
                user=user,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )
        except Exception:
            pass  # Jangan crash server karena logging error

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
