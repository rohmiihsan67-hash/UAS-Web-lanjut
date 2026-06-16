from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Submission


def get_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


@login_required(login_url='/akun/login/')
def overview_view(request):
    profile = get_user_profile(request.user)
    submissions = Submission.objects.filter(user=request.user)
    total = submissions.count()
    resolved = submissions.filter(status='resolved').count()
    in_progress = submissions.filter(status='in_progress').count()
    pending = submissions.filter(status='pending').count()
    recent = submissions[:5]
    context = {
        'profile': profile,
        'total': total,
        'resolved': resolved,
        'in_progress': in_progress,
        'pending': pending,
        'recent_submissions': recent,
        'active_page': 'overview',
    }
    return render(request, 'user/overview.html', context)


@login_required(login_url='/akun/login/')
def incident_map_view(request):
    import json
    profile = get_user_profile(request.user)
    submissions = Submission.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).order_by('-created_at')[:50]
    
    pins = []
    for sub in submissions:
        pins.append({
            'id': sub.id,
            'title': sub.title,
            'category': sub.get_category_display(),
            'status': sub.status,
            'status_display': sub.get_status_display(),
            'lat': sub.latitude,
            'lng': sub.longitude,
            'address': sub.location_address,
            'time': sub.created_at.strftime("%d %b %Y %H:%M"),
            'color': sub.status_color
        })

    context = {
        'profile': profile,
        'submissions': submissions,
        'pins_json': json.dumps(pins),
        'active_page': 'incident_map',
    }
    return render(request, 'user/incident_map.html', context)


@login_required(login_url='/akun/login/')
def public_feed_view(request):
    profile = get_user_profile(request.user)
    submissions = Submission.objects.all().order_by('-created_at')
    resolved_count = Submission.objects.filter(status='resolved').count()
    in_progress_count = Submission.objects.filter(status='in_progress').count()
    context = {
        'profile': profile,
        'submissions': submissions,
        'resolved_count': resolved_count,
        'in_progress_count': in_progress_count,
        'active_page': 'public_feed',
    }
    return render(request, 'user/public_feed.html', context)


@login_required(login_url='/akun/login/')
def my_submissions_view(request):
    profile = get_user_profile(request.user)
    submissions = Submission.objects.filter(user=request.user)
    total = submissions.count()
    resolved = submissions.filter(status='resolved').count()
    in_progress = submissions.filter(status='in_progress').count()
    pending = submissions.filter(status='pending').count()
    context = {
        'profile': profile,
        'submissions': submissions,
        'total': total,
        'resolved': resolved,
        'in_progress': in_progress,
        'pending': pending,
        'active_page': 'my_submissions',
    }
    return render(request, 'user/my_submissions.html', context)


@login_required(login_url='/akun/login/')
def profile_view(request):
    profile = get_user_profile(request.user)
    submissions = Submission.objects.filter(user=request.user)
    total = submissions.count()
    resolved = submissions.filter(status='resolved').count()
    pending_action = submissions.filter(status='in_progress').count()
    recent_activity = submissions[:3]

    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name', profile.full_name)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.occupation = request.POST.get('occupation', profile.occupation)
        profile.home_address = request.POST.get('home_address', profile.home_address)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()
        profile.save()
        messages.success(request, 'Profil berhasil diperbarui!')
        return redirect('user_profile')

    context = {
        'profile': profile,
        'total': total,
        'resolved': resolved,
        'pending_action': pending_action,
        'recent_activity': recent_activity,
        'active_page': 'profile',
    }
    return render(request, 'user/profile.html', context)


@login_required(login_url='/akun/login/')
def settings_view(request):
    profile = get_user_profile(request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'change_password':
            from django.contrib.auth import update_session_auth_hash
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password berhasil diubah!')
            else:
                messages.error(request, 'Password lama salah.')
        elif action == 'update_regional':
            language = request.POST.get('language')
            timezone = request.POST.get('timezone')
            profile.language = language
            profile.timezone = timezone
            profile.save()
            messages.success(request, 'Regional preferences saved successfully!')
        return redirect('user_settings')
    context = {
        'profile': profile,
        'active_page': 'settings',
    }
    return render(request, 'user/settings.html', context)


@login_required(login_url='/akun/login/')
def new_report_view(request):
    profile = get_user_profile(request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'infrastructure')
        priority = request.POST.get('priority', 'medium')
        description = request.POST.get('description', '')
        location_address = request.POST.get('location_address', '')
        
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        photo = request.FILES.get('photo')

        if title:
            Submission.objects.create(
                user=request.user,
                title=title,
                category=category,
                priority=priority,
                description=description,
                location_address=location_address,
                latitude=float(lat) if lat else None,
                longitude=float(lng) if lng else None,
                photo=photo,
                status='pending',
            )
            messages.success(request, 'Laporan berhasil dikirim!')
            return redirect('user_my_submissions')
        else:
            messages.error(request, 'Judul laporan tidak boleh kosong.')
    context = {
        'profile': profile,
        'active_page': 'new_report',
    }
    return render(request, 'user/new_report.html', context)
