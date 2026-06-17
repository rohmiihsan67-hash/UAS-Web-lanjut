from django.db import models
from django.contrib.auth.models import User


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')

    # Data Diri
    full_name = models.CharField('Nama Lengkap', max_length=150, blank=True, default='')
    email = models.EmailField('Email', blank=True, default='')
    phone = models.CharField('Nomor Telepon', max_length=20, blank=True, default='')
    birth_date = models.DateField('Tanggal Lahir', null=True, blank=True)
    birth_place = models.CharField('Tempat Lahir', max_length=100, blank=True, default='')
    age = models.PositiveIntegerField('Umur', null=True, blank=True)
    gender = models.CharField('Jenis Kelamin', max_length=20, blank=True, default='', choices=[
        ('', '-'),
        ('Laki-laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan'),
    ])

    # Data Pekerjaan
    department = models.CharField('Departemen', max_length=150, blank=True, default='')
    position = models.CharField('Jabatan', max_length=150, blank=True, default='')
    supervisor = models.CharField('Supervisor', max_length=150, blank=True, default='')
    duty_start = models.TimeField('Jam Masuk', null=True, blank=True)
    duty_end = models.TimeField('Jam Selesai', null=True, blank=True)

    # Internal Memo
    memo_text = models.TextField('Internal Memo', blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'

    def __str__(self):
        return f'AdminProfile: {self.user.username}'

    @property
    def is_profile_complete(self):
        """Cek apakah profil sudah diisi minimal nama dan email."""
        return bool(self.full_name and self.email)


class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True, verbose_name="Alamat IP")
    reason = models.CharField(max_length=255, blank=True, verbose_name="Alasan Pemblokiran")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'

    def __str__(self):
        return self.ip_address


class SecurityLog(models.Model):
    STATUS_CHOICES = [
        ('allowed', 'Diizinkan'),
        ('blocked', 'Diblokir'),
        ('login_failed', 'Login Gagal'),
        ('login_success', 'Login Berhasil'),
    ]

    ip_address = models.GenericIPAddressField(verbose_name="Alamat IP")
    path       = models.CharField(max_length=500, verbose_name="Halaman Diakses")
    method     = models.CharField(max_length=10, default='GET')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='allowed')
    user       = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Pengguna")
    user_agent = models.TextField(blank=True, verbose_name="Browser/Device")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Security Log'
        verbose_name_plural = 'Security Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.status}] {self.ip_address} → {self.path}"


class SiteSetting(models.Model):
    org_name = models.CharField(max_length=255, default="AduanCepat Institutional", verbose_name="Nama Organisasi")
    domain = models.CharField(max_length=255, default="portal.aduancepat.gov", verbose_name="Domain Utama")
    language = models.CharField(max_length=50, default="id", choices=[('en', 'English (US)'), ('id', 'Bahasa Indonesia')], verbose_name="Bahasa Sistem")
    timezone = models.CharField(max_length=50, default="Asia/Jakarta", choices=[('Asia/Jakarta', 'UTC +7:00 (Jakarta)'), ('Asia/Makassar', 'UTC +8:00 (Makassar)')], verbose_name="Zona Waktu")

    # Preferences
    mod_auto = models.BooleanField(default=True, verbose_name="Moderasi Otomatis")
    notif_email = models.BooleanField(default=True, verbose_name="Notifikasi Email")
    public_analytic = models.BooleanField(default=False, verbose_name="Analitik Publik")
    mfa_required = models.BooleanField(default=True, verbose_name="Autentikasi Multi-Faktor")

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return "Pengaturan Sistem"
