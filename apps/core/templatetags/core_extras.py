"""
Custom template filters shared across the project.

Usage in templates:
    {% load core_extras %}
    {{ value|replace:"_,  " }}         # replaces '_' with '  '
    {{ value|replace:"_: " }}          # replaces '_' with ' '  (colon separator)
"""
from django import template

register = template.Library()


@register.filter(name="replace")
def replace(value, arg):
    """
    Replace occurrences of a substring with another.

    The `arg` is a two-part string separated by either a colon (``:``) or a
    comma (``,``). This keeps the filter usable from templates where colons
    have special meaning in some contexts.

    Examples:
        {{ "hello_world"|replace:"_: " }}   -> "hello world"
        {{ "a-b-c"|replace:"-,+" }}         -> "a+b+c"
    """
    if value is None:
        return ""
    text = str(value)
    if not arg:
        return text

    separator = ":" if ":" in arg else ("," if "," in arg else None)
    if separator is None:
        return text

    old, _, new = arg.partition(separator)
    return text.replace(old, new)


@register.filter(name="humanize_underscores")
def humanize_underscores(value):
    """Convert ``some_type_name`` -> ``some type name``."""
    if value is None:
        return ""
    return str(value).replace("_", " ")
