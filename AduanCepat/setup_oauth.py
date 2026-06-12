import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'masyarakat_project.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def setup_google_oauth():
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("[-] Gagal: GOOGLE_CLIENT_ID atau GOOGLE_CLIENT_SECRET tidak ditemukan di file .env")
        return

    # Ambil atau buat site default, lalu pastikan domainnya 127.0.0.1:8000
    site, created = Site.objects.get_or_create(id=1)
    site.domain = '127.0.0.1:8000'
    site.name = 'Localhost'
    site.save()

    # Buat atau update aplikasi social account
    app, created = SocialApp.objects.update_or_create(
        provider='google',
        defaults={
            'name': 'Google OAuth',
            'client_id': client_id,
            'secret': client_secret,
        }
    )
    
    app.sites.add(site)
    print(f"[+] Berhasil: Google OAuth telah dikonfigurasi di database.")

if __name__ == '__main__':
    setup_google_oauth()
