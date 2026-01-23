"""
Custom validators for the application.
"""
import os
from django.core.exceptions import ValidationError
from django.conf import settings


def validate_file_extension(value):
    """
    Validate file extension against allowed extensions.
    """
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise ValidationError(
            f'Invalid file extension. Allowed extensions: {", ".join(settings.ALLOWED_UPLOAD_EXTENSIONS)}'
        )


def validate_file_size(value):
    """
    Validate file size against maximum allowed size.
    """
    if value.size > settings.MAX_UPLOAD_SIZE:
        max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise ValidationError(f'File size must be less than {max_size_mb} MB.')


def validate_image_file(value):
    """
    Validate image file extension.
    """
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f'Invalid image format. Allowed formats: {", ".join(allowed_extensions)}'
        )


def validate_positive_decimal(value):
    """
    Validate that a decimal value is positive.
    """
    if value <= 0:
        raise ValidationError('Value must be greater than zero.')


def validate_budget_range(budget_min, budget_max):
    """
    Validate that budget_max is greater than budget_min.
    """
    if budget_max < budget_min:
        raise ValidationError('Maximum budget must be greater than or equal to minimum budget.')
