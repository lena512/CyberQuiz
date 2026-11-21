from .models import Event


def notifications(request):
    """Количество новых уведомлений для значка в навигации."""
    return {
        "unread_events": Event.objects.filter(status=Event.STATUS_NEW).count(),
    }
