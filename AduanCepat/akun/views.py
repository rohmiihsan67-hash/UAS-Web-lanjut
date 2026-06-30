from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CitizenRegistrationForm


@login_required(login_url='/akun/login/')
def home_view(request):
    from user.models import Submission
    total_reports  = Submission.objects.count()
    resolved       = Submission.objects.filter(status='resolved').count()
    in_progress    = Submission.objects.filter(status='in_progress').count()
    success_rate   = round((resolved / total_reports * 100), 1) if total_reports > 0 else 0
    recent_reports = Submission.objects.all().order_by('-created_at')[:4]

    context = {
        'total_reports':  total_reports,
        'resolved_count': resolved,
        'in_progress_count': in_progress,
        'success_rate':   success_rate,
        'recent_reports': recent_reports,
    }
    return render(request, 'akun/home.html', context)


@login_required(login_url='/akun/login/')
def admin_dashboard_view(request):
    if not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki akses ke halaman admin.')
        return redirect('/')

    from .models import AdminProfile, BlockedIP, SiteSetting, SecurityLog
    from .forms import AdminProfileForm

    # Get or create profile for this admin
    profile, created = AdminProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil disimpan!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Mohon periksa kembali data yang diisi.')
    else:
        form = AdminProfileForm(instance=profile)

    from django.contrib.auth.models import User
    from user.models import Submission

    user_count = User.objects.count()
    total_reports = Submission.objects.count()
    pending_actions = Submission.objects.filter(status__in=['pending', 'in_progress']).count()
    resolved_reports = Submission.objects.filter(status='resolved').count()
    
    if total_reports > 0:
        success_rate = int((resolved_reports / total_reports) * 100)
    else:
        success_rate = 0

    recent_reports = Submission.objects.all().order_by('-created_at')[:5]
    all_reports    = Submission.objects.all().order_by('-created_at')

    # Category breakdown for hotspot chart
    infra_count   = Submission.objects.filter(category='infrastructure').count()
    env_count     = Submission.objects.filter(category='environment').count()
    safety_count  = Submission.objects.filter(category='public_safety').count()
    other_count   = Submission.objects.filter(category='other').count()

    def pct(n):
        return round((n / total_reports) * 100) if total_reports > 0 else 0

    staff_members = User.objects.filter(is_staff=True).order_by('-date_joined')

    # Calculate real 7-day chart data
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.localdate()
    
    # --- 7 Days Data ---
    last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    ind_days = {'Mon': 'Sen', 'Tue': 'Sel', 'Wed': 'Rab', 'Thu': 'Kam', 'Fri': 'Jum', 'Sat': 'Sab', 'Sun': 'Min'}
    chart_7_labels = [ind_days.get(d.strftime('%a'), d.strftime('%a')) for d in last_7_days]
    
    chart_7_data = [Submission.objects.filter(created_at__date=d).count() for d in last_7_days]
    x_coords_7 = [40, 130, 220, 310, 400, 490, 580]
    max_val_7 = max(chart_7_data) if chart_7_data and max(chart_7_data) > 0 else 1
    
    points_7 = []
    nodes_7 = []
    for idx, val in enumerate(chart_7_data):
        x = x_coords_7[idx]
        y = 170 - (val / max_val_7 * 130)
        points_7.append(f"{x} {y}")
        nodes_7.append({'x': x, 'y': y, 'label': chart_7_labels[idx], 'val': val})
        
    chart_7_path_str = " L ".join(points_7)
    chart_7_path = f"M {chart_7_path_str}" if points_7 else ""
    chart_7_area = f"{chart_7_path} L 580 170 L 40 170 Z" if points_7 else ""

    # --- 30 Days Data ---
    last_30_days = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
    chart_30_labels = [d.strftime('%d/%m') for d in last_30_days]
    chart_30_data = [Submission.objects.filter(created_at__date=d).count() for d in last_30_days]
    
    # 30 points mapped from x=40 to x=580.
    # Total width = 540, split into 29 intervals.
    x_step = 540 / 29.0
    x_coords_30 = [40 + (i * x_step) for i in range(30)]
    max_val_30 = max(chart_30_data) if chart_30_data and max(chart_30_data) > 0 else 1
    
    points_30 = []
    nodes_30 = []
    for idx, val in enumerate(chart_30_data):
        x = x_coords_30[idx]
        y = 170 - (val / max_val_30 * 130)
        points_30.append(f"{x} {y}")
        show_label = (idx % 6 == 0) or (idx == 29) # Show label every ~6 days
        nodes_30.append({'x': x, 'y': y, 'label': chart_30_labels[idx] if show_label else '', 'val': val})
        
    chart_30_path_str = " L ".join(points_30)
    chart_30_path = f"M {chart_30_path_str}" if points_30 else ""
    chart_30_area = f"{chart_30_path} L 580 170 L 40 170 Z" if points_30 else ""

    import json
    incidents_list = []
    for r in all_reports:
        lat = r.latitude if r.latitude else -6.2088 # Default Jakarta
        lng = r.longitude if r.longitude else 106.8456
        incidents_list.append({
            'id': r.id,
            'lat': float(lat),
            'lng': float(lng),
            'status': r.status,
            'title': r.title,
            'loc': r.location_address or f"Lokasi: {lat}, {lng}",
            'desc': r.description or '',
            'active': False
        })
    incidents_json = json.dumps(incidents_list)

    # For matching user incident map
    map_submissions = Submission.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).order_by('-created_at')[:100]
    pins = []
    for sub in map_submissions:
        pins.append({
            'id': sub.id,
            'title': sub.title,
            'category': sub.get_category_display(),
            'category_raw': sub.category,
            'status': sub.status,
            'status_display': sub.get_status_display(),
            'priority': sub.priority,
            'lat': sub.latitude,
            'lng': sub.longitude,
            'address': sub.location_address,
            'time': sub.created_at.strftime("%d %b %Y %H:%M"),
            'color': sub.status_color,
            'description': (sub.description[:80] + '...') if sub.description and len(sub.description) > 80 else (sub.description or ''),
        })
    pins_json = json.dumps(pins)

    context = {
        'profile': profile,
        'form': form,
        'is_editing': request.GET.get('edit') == '1' or not profile.is_profile_complete,
        'actions': [],
        'user_count': user_count,
        'total_reports': total_reports,
        'pending_actions': pending_actions,
        'resolved_reports': resolved_reports,
        'success_rate': success_rate,
        'recent_reports': recent_reports,
        'all_reports': all_reports,
        'infra_count':   infra_count,   'infra_pct':   pct(infra_count),
        'env_count':     env_count,     'env_pct':     pct(env_count),
        'safety_count':  safety_count,  'safety_pct':  pct(safety_count),
        'other_count':   other_count,   'other_pct':   pct(other_count),
        'staff_members': staff_members,
        'blocked_ips':   BlockedIP.objects.all().order_by('-created_at'),
        'site_settings': SiteSetting.objects.first(),
        'security_logs': SecurityLog.objects.all()[:100],
        'chart_7_path': chart_7_path,
        'chart_7_area': chart_7_area,
        'chart_7_nodes': nodes_7,
        'chart_30_path': chart_30_path,
        'chart_30_area': chart_30_area,
        'chart_30_nodes': nodes_30,
        'incidents_json': incidents_json,
        'map_submissions': map_submissions,
        'pins_json': pins_json,
    }
    return render(request, 'admin/admin_dashboard.html', context)


@login_required(login_url='/akun/login/')
def admin_update_status(request, report_id):
    """Admin: update status of a submission from the Reports tab."""
    if not request.user.is_staff:
        messages.error(request, 'Akses ditolak.')
        return redirect('/')
    if request.method == 'POST':
        from user.models import Submission
        from django.shortcuts import get_object_or_404
        report = get_object_or_404(Submission, pk=report_id)
        new_status = request.POST.get('status')
        valid_statuses = ['pending', 'in_progress', 'resolved']
        if new_status in valid_statuses:
            report.status = new_status
            report.save()
            messages.success(request, f'Status laporan #{report_id} diubah ke "{new_status}".')
    return redirect('/akun/admin-dashboard/?tab=reports')


def register_view(request):
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Akun berhasil dibuat untuk {username}! Silakan login.')
            return redirect('login')
    else:
        form = CitizenRegistrationForm()
    return render(request, 'akun/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('/')
    if request.method == 'POST':
        login_role = request.POST.get('login_role', 'user')
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if login_role == 'admin' and not user.is_staff:
                    messages.error(request, 'Akun ini tidak memiliki hak akses admin.')
                    return render(request, 'akun/login.html', {'form': form})
                login(request, user)
                if login_role == 'admin' and user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('/')
        else:
            messages.error(request, 'Username atau password salah.')
    else:
        form = AuthenticationForm()
    return render(request, 'akun/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


import random
import time
from django.core.mail import send_mail
from django.contrib.auth.models import User

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Silakan masukkan email Anda.')
            return render(request, 'akun/forgot_password.html')
            
        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, 'Email tidak terdaftar.')
            return render(request, 'akun/forgot_password.html')
            
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Save to session
        request.session['reset_email'] = email
        request.session['reset_otp'] = otp
        request.session['reset_otp_expiry'] = time.time() + 300 # 5 minutes
        
        # Send Email
        subject = 'AduanCepat - Kode Verifikasi Reset Password'
        body = f"""Halo,

Anda menerima email ini karena ada permintaan untuk mereset kata sandi akun Anda di AduanCepat.

Kode verifikasi Anda adalah: {otp}

Kode ini hanya berlaku selama 5 menit. Jika Anda tidak merasa melakukan permintaan ini, silakan abaikan email ini.

Salam,
Tim AduanCepat"""
        try:
            send_mail(
                subject,
                body,
                'noreply@aduancepat.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Kode verifikasi telah dikirim ke email Anda.')
            return redirect('reset_password')
        except Exception as e:
            messages.error(request, f'Gagal mengirim email: {str(e)}')
            
    return render(request, 'akun/forgot_password.html')


def reset_password_view(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Silakan masukkan email Anda terlebih dahulu.')
        return redirect('forgot_password')
        
    if request.method == 'POST':
        # Combine 6 OTP boxes
        code_1 = request.POST.get('code_1', '')
        code_2 = request.POST.get('code_2', '')
        code_3 = request.POST.get('code_3', '')
        code_4 = request.POST.get('code_4', '')
        code_5 = request.POST.get('code_5', '')
        code_6 = request.POST.get('code_6', '')
        input_otp = f"{code_1}{code_2}{code_3}{code_4}{code_5}{code_6}"
        
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        session_otp = request.session.get('reset_otp')
        expiry = request.session.get('reset_otp_expiry', 0)
        
        if not input_otp or len(input_otp) < 6:
            messages.error(request, 'Kode verifikasi tidak lengkap.')
            return render(request, 'akun/reset_password.html')
            
        if not session_otp or time.time() > expiry:
            messages.error(request, 'Kode verifikasi telah kedaluwarsa atau tidak valid. Silakan kirim ulang.')
            return render(request, 'akun/reset_password.html')
            
        if input_otp != session_otp:
            messages.error(request, 'Kode verifikasi yang Anda masukkan salah.')
            return render(request, 'akun/reset_password.html')
            
        if not new_password or len(new_password) < 8:
            messages.error(request, 'Password baru minimal harus 8 karakter.')
            return render(request, 'akun/reset_password.html')
            
        if new_password != confirm_password:
            messages.error(request, 'Konfirmasi password baru tidak cocok.')
            return render(request, 'akun/reset_password.html')
            
        # Change password
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()
            
            # Clear session
            if 'reset_email' in request.session: del request.session['reset_email']
            if 'reset_otp' in request.session: del request.session['reset_otp']
            if 'reset_otp_expiry' in request.session: del request.session['reset_otp_expiry']
            
            return redirect('reset_success')
        else:
            messages.error(request, 'Pengguna tidak ditemukan.')
            
    return render(request, 'akun/reset_password.html')


def resend_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Silakan masukkan email Anda terlebih dahulu.')
        return redirect('forgot_password')
        
    otp = str(random.randint(100000, 999999))
    request.session['reset_otp'] = otp
    request.session['reset_otp_expiry'] = time.time() + 300
    
    subject = 'AduanCepat - Kode Verifikasi Reset Password'
    body = f"""Halo,

Berikut adalah kode verifikasi baru Anda untuk mereset kata sandi:

Kode verifikasi Anda adalah: {otp}

Kode ini berlaku selama 5 menit.

Salam,
Tim AduanCepat"""
    try:
        send_mail(
            subject,
            body,
            'noreply@aduancepat.com',
            [email],
            fail_silently=False,
        )
        messages.success(request, 'Kode verifikasi baru telah dikirim.')
    except Exception as e:
        messages.error(request, f'Gagal mengirim email: {str(e)}')
        
    return redirect('reset_password')


def reset_success_view(request):
    return render(request, 'akun/reset_success.html')

@login_required(login_url='/akun/login/')
def block_ip(request):
    if not request.user.is_staff:
        messages.error(request, 'Akses ditolak.')
        return redirect('/')
    
    if request.method == 'POST':
        ip = request.POST.get('ip_address')
        reason = request.POST.get('reason', '')
        if ip:
            from .models import BlockedIP
            BlockedIP.objects.get_or_create(ip_address=ip, defaults={'reason': reason})
            messages.success(request, f'IP {ip} berhasil diblokir.')
        else:
            messages.error(request, 'Alamat IP tidak valid.')
    return redirect('/akun/admin-dashboard/?tab=security')

@login_required(login_url='/akun/login/')
def unblock_ip(request, ip_id):
    if not request.user.is_staff:
        messages.error(request, 'Akses ditolak.')
        return redirect('/')
        
    from .models import BlockedIP
    try:
        blocked_ip = BlockedIP.objects.get(id=ip_id)
        ip_addr = blocked_ip.ip_address
        blocked_ip.delete()
        messages.success(request, f'Blokir untuk IP {ip_addr} berhasil dibuka.')
    except BlockedIP.DoesNotExist:
        messages.error(request, 'Data IP tidak ditemukan.')
        
    return redirect('/akun/admin-dashboard/?tab=security')

@login_required(login_url='/akun/login/')
def save_settings(request):
    if not request.user.is_staff:
        messages.error(request, 'Akses ditolak.')
        return redirect('/')
        
    if request.method == 'POST':
        from .models import SiteSetting
        setting, created = SiteSetting.objects.get_or_create(id=1)
        
        setting.org_name = request.POST.get('org_name', setting.org_name)
        setting.domain = request.POST.get('domain', setting.domain)
        setting.language = request.POST.get('language', setting.language)
        setting.timezone = request.POST.get('timezone', setting.timezone)
        
        setting.mod_auto = request.POST.get('mod_auto') == 'on'
        setting.notif_email = request.POST.get('notif_email') == 'on'
        setting.public_analytic = request.POST.get('public_analytic') == 'on'
        setting.mfa_required = request.POST.get('mfa_required') == 'on'
        
        setting.save()
        messages.success(request, 'Pengaturan berhasil disimpan.')
        
    return redirect('/akun/admin-dashboard/?tab=settings')

@login_required(login_url='/akun/login/')
def clear_cache(request):
    if not request.user.is_staff:
        messages.error(request, 'Akses ditolak.')
        return redirect('/')
        
    if request.method == 'POST':
        from django.core.cache import cache
        cache.clear()
        messages.success(request, 'Cache sistem berhasil dibersihkan.')
        
    return redirect('/akun/admin-dashboard/?tab=settings')


@login_required(login_url='/akun/login/')
def admin_security_logs_partial(request):
    """Endpoint AJAX untuk polling log keamanan secara real-time."""
    from django.http import HttpResponseForbidden
    if not request.user.is_staff:
        return HttpResponseForbidden()
    from .models import SecurityLog
    security_logs = SecurityLog.objects.all().order_by('-created_at')[:100]
    return render(request, 'admin/dashboard_tabs/security_logs_body.html', {
        'security_logs': security_logs
    })
