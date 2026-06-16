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

    from .models import AdminProfile
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


