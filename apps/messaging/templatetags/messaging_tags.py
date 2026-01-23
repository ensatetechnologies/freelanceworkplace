"""
Template tags for messaging app.
"""
from django import template

register = template.Library()


@register.simple_tag
def get_other_participant(conversation, user):
    """Get the other participant in a conversation."""
    return conversation.get_other_participant(user)


@register.simple_tag
def get_unread_count(conversation, user):
    """Get unread message count for a conversation."""
    return conversation.get_unread_count(user)
