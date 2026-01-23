"""
Views for messaging app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from apps.accounts.models import User
from .models import Conversation, Message, MessageAttachment


class ConversationListView(LoginRequiredMixin, ListView):
    """View for listing user's conversations."""
    model = Conversation
    template_name = 'messaging/inbox.html'
    context_object_name = 'conversations'
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants').order_by('-last_message_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add other_user and unread_count for each conversation
        conversations_with_data = []
        for conv in context['conversations']:
            conv.other_user = conv.get_other_participant(self.request.user)
            conv.unread = conv.get_unread_count(self.request.user)
            conversations_with_data.append(conv)
        context['conversations'] = conversations_with_data
        return context


class ConversationDetailView(LoginRequiredMixin, DetailView):
    """View for conversation/chat interface."""
    model = Conversation
    template_name = 'messaging/conversation.html'
    context_object_name = 'conversation'
    
    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Mark messages as read
        self.object.mark_as_read(request.user)
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages_list'] = self.object.messages.select_related('sender').order_by('created_at')[:50]
        context['other_user'] = self.object.get_other_participant(self.request.user)
        
        # Add all conversations for sidebar with other_user data
        all_conversations = Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants').order_by('-last_message_at')
        
        for conv in all_conversations:
            conv.other_user = conv.get_other_participant(self.request.user)
        
        context['all_conversations'] = all_conversations
        return context


class StartConversationView(LoginRequiredMixin, View):
    """View for starting a new conversation."""
    
    def post(self, request):
        recipient_id = request.POST.get('recipient_id')
        initial_message = request.POST.get('message', '')
        
        recipient = get_object_or_404(User, pk=recipient_id)
        
        # Check if conversation already exists
        existing = Conversation.objects.filter(
            participants=request.user
        ).filter(participants=recipient).first()
        
        if existing:
            if initial_message:
                Message.objects.create(
                    conversation=existing,
                    sender=request.user,
                    content=initial_message
                )
            return redirect('messaging:conversation', pk=existing.pk)
        
        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)
        
        if initial_message:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=initial_message
            )
        
        return redirect('messaging:conversation', pk=conversation.pk)
    
    def get(self, request):
        recipient_id = request.GET.get('recipient')
        context = {}
        
        if recipient_id:
            context['recipient'] = get_object_or_404(User, pk=recipient_id)
        
        return render(request, 'messaging/start_conversation.html', context)


class SendMessageView(LoginRequiredMixin, View):
    """View for sending a message."""
    
    def post(self, request, conversation_pk):
        conversation = get_object_or_404(
            Conversation,
            pk=conversation_pk,
            participants=request.user
        )
        
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'error': 'Message cannot be empty.'}, status=400)
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Handle file attachment
        if 'file' in request.FILES:
            MessageAttachment.objects.create(
                message=message,
                file=request.FILES['file']
            )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': str(message.id),
                'content': message.content,
                'sender_id': str(message.sender.id),
                'sender_name': message.sender.get_full_name(),
                'created_at': message.created_at.isoformat(),
            })
        
        return redirect('messaging:conversation', pk=conversation.pk)


class FetchMessagesView(LoginRequiredMixin, View):
    """View for fetching new messages (polling)."""
    
    def get(self, request, conversation_pk):
        conversation = get_object_or_404(
            Conversation,
            pk=conversation_pk,
            participants=request.user
        )
        
        last_id = request.GET.get('last_id')
        
        messages_qs = conversation.messages.select_related('sender')
        if last_id:
            messages_qs = messages_qs.filter(id__gt=last_id)
        
        # Mark as read
        conversation.mark_as_read(request.user)
        
        messages_data = [{
            'id': str(m.id),
            'content': m.content,
            'sender_id': str(m.sender.id),
            'sender_name': m.sender.get_full_name(),
            'sender_avatar': m.sender.get_avatar_url(),
            'is_mine': m.sender == request.user,
            'created_at': m.created_at.isoformat(),
        } for m in messages_qs[:50]]
        
        return JsonResponse({'messages': messages_data})


class UnreadCountView(LoginRequiredMixin, View):
    """View for getting unread message count."""
    
    def get(self, request):
        count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        
        return JsonResponse({'unread_count': count})
