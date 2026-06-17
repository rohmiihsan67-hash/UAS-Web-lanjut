from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    full_name = models.CharField('Nama Lengkap', max_length=150, blank=True, default='')
    phone = models.CharField('Nomor Telepon', max_length=20, blank=True, default='')
    occupation = models.CharField('Pekerjaan', max_length=100, blank=True, default='')
    home_address = models.TextField('Alamat Rumah', blank=True, default='')
    avatar = models.ImageField('Foto Profil', upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField('Terverifikasi', default=False)
    trust_score = models.PositiveIntegerField('Community Trust Score', default=85)
    language = models.CharField('Language', max_length=10, default='id')
    timezone = models.CharField('Timezone', max_length=50, default='Asia/Jakarta')
    # Notifikasi
    notif_email = models.BooleanField('Notifikasi Email', default=True)
    notif_push  = models.BooleanField('Notifikasi Push', default=True)
    notif_sms   = models.BooleanField('Notifikasi SMS', default=False)
    # Privasi
    privacy_mode = models.CharField('Mode Privasi', max_length=20, default='transparent',
                                    choices=[('transparent', 'Transparansi Penuh'), ('anonymous', 'Pelaporan Rahasia')])
    # Keamanan
    mfa_enabled = models.BooleanField('Autentikasi Dua Faktor', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'UserProfile: {self.user.username}'


class Submission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('pending_publication', 'Pending Publication'),
    ]
    CATEGORY_CHOICES = [
        ('infrastructure', 'Infrastructure'),
        ('environment', 'Environment'),
        ('public_safety', 'Public Safety'),
        ('other', 'Other'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    title = models.CharField('Judul Laporan', max_length=200)
    category = models.CharField('Kategori', max_length=50, choices=CATEGORY_CHOICES, default='infrastructure')
    priority = models.CharField('Prioritas', max_length=10, choices=PRIORITY_CHOICES, default='medium')
    description = models.TextField('Deskripsi', blank=True)
    location_address = models.CharField('Alamat Lokasi', max_length=255, blank=True)
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    photo = models.ImageField('Foto Bukti', upload_to='incident_photos/', null=True, blank=True)
    status = models.CharField('Status', max_length=30, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        ordering = ['-created_at']

    @property
    def status_color(self):
        if self.status == 'pending': return 'emergency'
        if self.status == 'in_progress': return 'maintenance'
        if self.status == 'resolved': return 'verified'
        return 'emergency'

    def __str__(self):
        return f'#{self.pk} - {self.title}'

    def get_status_display_class(self):
        mapping = {
            'pending': 'status-pending',
            'in_progress': 'status-inprogress',
            'resolved': 'status-resolved',
            'pending_publication': 'status-pendpub',
        }
        return mapping.get(self.status, '')
