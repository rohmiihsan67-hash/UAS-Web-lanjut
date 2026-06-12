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
