"""
Utility functions for the application.
"""
import os
import uuid
from django.utils.text import slugify
from django.conf import settings


def generate_unique_slug(model_class, title, slug_field='slug'):
    """
    Generate a unique slug for a model instance.
    """
    slug = slugify(title)
    unique_slug = slug
    num = 1
    
    while model_class.objects.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f'{slug}-{num}'
        num += 1
    
    return unique_slug


def get_upload_path(instance, filename, folder):
    """
    Generate a unique upload path for files.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join(folder, filename)


def avatar_upload_path(instance, filename):
    """Upload path for user avatars."""
    return get_upload_path(instance, filename, 'avatars')


def project_attachment_path(instance, filename):
    """Upload path for project attachments."""
    return get_upload_path(instance, filename, 'project_attachments')


def proposal_attachment_path(instance, filename):
    """Upload path for proposal attachments."""
    return get_upload_path(instance, filename, 'proposal_attachments')


def deliverable_upload_path(instance, filename):
    """Upload path for deliverables."""
    return get_upload_path(instance, filename, 'deliverables')


def message_attachment_path(instance, filename):
    """Upload path for message attachments."""
    return get_upload_path(instance, filename, 'message_attachments')


def get_file_size_display(size_bytes):
    """
    Convert file size in bytes to human-readable format.
    """
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    elif size_bytes < 1024 * 1024 * 1024:
        return f'{size_bytes / (1024 * 1024):.1f} MB'
    else:
        return f'{size_bytes / (1024 * 1024 * 1024):.1f} GB'


def validate_file_extension(filename):
    """
    Validate file extension against allowed extensions.
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in settings.ALLOWED_UPLOAD_EXTENSIONS


def validate_file_size(file):
    """
    Validate file size against maximum allowed size.
    """
    return file.size <= settings.MAX_UPLOAD_SIZE


def calculate_platform_fee(amount):
    """
    Calculate platform fee based on amount.
    """
    from decimal import Decimal
    fee_percent = Decimal(str(settings.PLATFORM_FEE_PERCENT))
    return (amount * fee_percent / 100).quantize(Decimal('0.01'))


def calculate_net_amount(amount):
    """
    Calculate net amount after platform fee.
    """
    fee = calculate_platform_fee(amount)
    return amount - fee
