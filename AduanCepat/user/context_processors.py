from .models import Submission

def notifications(request):
    """
    Returns recent status updates for the user's submissions to be displayed in the notification bell.
    """
    if request.user.is_authenticated:
        # Get the latest 5 submissions that have been updated
        recent_submissions = Submission.objects.filter(user=request.user).order_by('-updated_at')[:5]
        
        # We'll treat the latest 3 submissions that are NOT pending as "notifications"
        # Or just show all recent ones. Let's just show recent ones.
        notifs = []
        for sub in recent_submissions:
            if sub.status == 'resolved':
                title = "Laporan Selesai"
                body = f"Laporan '{sub.title}' telah berhasil diselesaikan."
                icon = "✅"
            elif sub.status == 'in_progress':
                title = "Laporan Diproses"
                body = f"Laporan '{sub.title}' sedang ditindaklanjuti."
                icon = "🔄"
            else:
                title = "Laporan Diterima"
                body = f"Laporan '{sub.title}' sedang dalam antrean."
                icon = "🕐"
            
            notifs.append({
                'title': title,
                'body': body,
                'icon': icon,
                'time': sub.updated_at
            })
            
        return {
            'recent_notifications': notifs,
            'unread_notifs_count': len(notifs) # Simplified unread logic
        }
    return {}
