"""
Views for notifications app.
"""
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """View for listing notifications."""
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(
            user=self.request.user, is_read=False
        ).count()
        return context


class MarkAsReadView(LoginRequiredMixin, View):
    """View for marking a notification as read."""
    
    def post(self, request, pk):
        notification = get_object_or_404(
            Notification, pk=pk, user=request.user
        )
        notification.mark_as_read()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        if notification.action_url:
            return redirect(notification.action_url)
        return redirect('notifications:list')


class MarkAllAsReadView(LoginRequiredMixin, View):
    """View for marking all notifications as read."""
    
    def post(self, request):
        from django.utils import timezone
        Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('notifications:list')


class UnreadCountView(LoginRequiredMixin, View):
    """View for getting unread notification count."""
    
    def get(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return JsonResponse({'unread_count': count})


class NotificationDropdownView(LoginRequiredMixin, View):
    """View for notification dropdown content."""
    
    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        data = [{
            'id': str(n.id),
            'type': n.type,
            'title': n.title,
            'message': n.message[:100],
            'is_read': n.is_read,
            'action_url': n.action_url,
            'created_at': n.created_at.isoformat(),
        } for n in notifications]
        
        return JsonResponse({
            'notifications': data,
            'unread_count': notifications.filter(is_read=False).count()
        })
